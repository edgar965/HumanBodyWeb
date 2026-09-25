# -*- coding: utf-8 -*-
u"""Eigenes Stück: ein OBJ hochladen, als Genesis-9-Stück ablegen, auf Genesis 9
und HumanBody prüfen.

    POST /api/character/eigenstueck/bauen/                 multipart, -> Bilanz + Proben
    GET  /api/character/eigenstueck/<kennung>/<bild>/      ein Probebild (PNG)

Edgar (25.09.2026): „mach mir ein UI für ein neues garment laut Punkt 2,
erstmal in dieser Hilfeseite. Browser zur Angabe des obj, Ausgabe in einem
Verzeichnis, Test der Ausgabe auf Genesis und HumanBody Modell (Screenshot)".
Die Rechnung steht in `Genesis9/eigenstueck.py` (`G9eigenstueck`), die Probe
in `core/dienste/eigenstueckprobe.py`; hier nur Annahme, Ablage, Antwort.

DIE DATEIEN KOMMEN IN DEN ARBEITSORDNER DES STÜCKS (`…/eigene_stuecke/<Kennung>/
quelle/`), unter ihrem eigenen Namen — eine `.mtl` nennt ihre Textur beim
Namen, umbenannt fände sie sie nicht. Jeder Name geht durch
`SafePath.dateiname` (kein Pfadanteil, keine verbotenen Zeichen). Ein
Probebild wird nur aus einer festen Liste ausgeliefert, die Kennung nur nach
Muster — die Anfrage baut keinen Pfad.
"""
import logging
import re

from django.http import FileResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger('core')

__all__ = ['Eigenstueckapi']


class Eigenstueckapi:
    u"""`bauen` (POST) und `bild` (GET)."""

    BILDER = ('probe_genesis9.png', 'probe_humanbody.png')
    KENNUNG = re.compile(r'^EIGEN_[A-Za-z0-9_]{1,80}$')
    #: Was hochgeladen werden darf: das Netz, seine `.mtl`, Bilder dazu.
    ENDUNGEN = {'obj': ('.obj',), 'mtl': ('.mtl',),
                'textur': ('.png', '.jpg', '.jpeg', '.tga', '.bmp', '.webp')}
    HOECHSTENS_MB = 200
    EINHEITEN = ('auto', 'm', 'dm', 'cm', 'mm')

    @classmethod
    def _zahl(cls, text, vorgabe, kleinst, groesst):
        try:
            wert = float(text)
        except (TypeError, ValueError):
            return vorgabe
        return min(max(wert, kleinst), groesst)

    @staticmethod
    def _farbe(text):
        u"""`#rrggbb` → (r, g, b) 0–1, sonst None (dann gilt die `.mtl` oder Grau)."""
        treffer = re.fullmatch(r'#?([0-9a-fA-F]{6})', str(text or '').strip())
        if not treffer:
            return None
        wert = treffer.group(1)
        return tuple(int(wert[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

    @classmethod
    def _ablegen(cls, request, ordner):
        u"""Die hochgeladenen Dateien nach `ordner`; gibt den Pfad des OBJ zurück."""
        from core.safe_paths import PfadAbgelehnt, SafePath
        obj = None
        ordner.mkdir(parents=True, exist_ok=True)
        for feld, endungen in cls.ENDUNGEN.items():
            for datei in request.FILES.getlist(feld):
                name = SafePath.dateiname(datei.name)
                if not name.lower().endswith(endungen):
                    raise PfadAbgelehnt(u'%s: erwartet %s' % (name, ', '.join(endungen)))
                if datei.size > cls.HOECHSTENS_MB * 1024 * 1024:
                    raise PfadAbgelehnt(u'%s: größer als %d MB' % (name, cls.HOECHSTENS_MB))
                with open(ordner / name, 'wb') as ziel:
                    for block in datei.chunks():
                        ziel.write(block)
                if feld == 'obj':
                    obj = ordner / name
        if obj is None:
            raise PfadAbgelehnt(u'Kein OBJ hochgeladen')
        return obj

    # `@staticmethod`, nicht `@classmethod`: `require_POST` sieht das erste
    # Argument als Anfrage — mit `cls` davor prüfte es die Klasse.
    @staticmethod
    @require_POST
    def bauen(request):
        cls = Eigenstueckapi
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.mbkategorien import G9mbkategorien

        from core.safe_paths import PfadAbgelehnt
        daten = request.POST
        name = (daten.get('name') or '').strip()[:80]
        if not name:
            return JsonResponse({'fehler': u'Bitte einen Namen angeben'}, status=400)
        kennung, _anzeige = G9eigenstueck.kennung_und_name(name)
        ordner = daten.get('kategorie') if daten.get('kategorie') in G9mbkategorien.ORDNER else 'tops'
        einheit = daten.get('einheit') if daten.get('einheit') in cls.EINHEITEN else 'auto'
        try:
            obj = cls._ablegen(request, G9eigenstueck.arbeitsordner(kennung) / 'quelle')
            bilanz = G9eigenstueck.bauen(
                obj, name, ordner=ordner, farbe=cls._farbe(daten.get('farbe')), einheit=einheit,
                oben='z' if daten.get('oben') == 'z' else 'y',
                zentrieren=daten.get('zentrieren', '1') == '1',
                massstab=cls._zahl(daten.get('massstab'), 1.0, 0.01, 100.0),
                versatz_cm=cls._zahl(daten.get('versatz_cm'), 0.0, -200.0, 200.0))
        except PfadAbgelehnt as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except (ValueError, OSError) as fehler:
            logger.warning('Eigenes Stück %s: %s', name, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=400)
        proben = cls._proben(bilanz) if daten.get('probe', '1') == '1' else {}
        return JsonResponse({'bilanz': bilanz, 'proben': proben})

    @classmethod
    def _proben(cls, bilanz):
        u"""Je Figur `{bild (Adresse), pixel, teile}` oder `{fehler}` — eine Figur,
        die scheitert, nimmt der anderen ihr Bild nicht."""
        from Genesis9.eigenstueck import G9eigenstueck

        from core.dienste.eigenstueckprobe import Eigenstueckprobe
        probe = Eigenstueckprobe()
        ordner = G9eigenstueck.arbeitsordner(bilanz['kennung'])
        aus = {}
        for figur in ('genesis', 'humanbody'):
            try:
                ergebnis = getattr(probe, figur)(bilanz['stueck'], ordner)
                ergebnis['bild'] = '/api/character/eigenstueck/%s/%s/' % (
                    bilanz['kennung'], ergebnis['bild'])
                aus[figur] = ergebnis
            except Exception as fehler:  # noqa: BLE001 — je Figur melden, nicht abbrechen
                logger.exception('Eigenes Stück %s: Probe %s', bilanz['kennung'], figur)
                aus[figur] = {'fehler': '%s: %s' % (type(fehler).__name__, fehler)}
        return aus

    @staticmethod
    @require_GET
    def bild(request, kennung, datei):
        cls = Eigenstueckapi
        from Genesis9.eigenstueck import G9eigenstueck
        if not cls.KENNUNG.match(kennung) or datei not in cls.BILDER:
            return JsonResponse({'fehler': 'Unbekanntes Bild'}, status=404)
        pfad = G9eigenstueck.arbeitsordner(kennung) / datei
        if not pfad.is_file():
            return JsonResponse({'fehler': 'Bild fehlt'}, status=404)
        # Ein neuer Bau überschreibt das Bild unter derselben Adresse — nie aus
        # dem Zwischenspeicher (die Seite hängt ohnehin `?t=` an).
        antwort = FileResponse(open(pfad, 'rb'), content_type='image/png')
        antwort['Cache-Control'] = 'no-store'
        return antwort
