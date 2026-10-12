# -*- coding: utf-8 -*-
"""Mesh3dendpunkte — die Seite „Mesh-3D“ unter Dashboard (11.10.2026): ein Netz (Blender, OBJ, FBX, GLB) → Genesis-Modell.

Kein neuer Auftrag, keine neue Kette: ein Auftrag hier IST ein Modell-Import (`Blendimportlauf`, `3DObjects/blendimport/<kennung>/stand.json`),
dieselbe Kette wie „Datei → Modell importieren…“ auf der Charakter-Seite. Diese Klasse liefert nur die Seiten und das, was der Import
bisher nicht hatte — eine Liste, eine Jobseite, das Anlegen ohne Start und das Ändern der Einstellungen. Start, Anhalten, „ab Schritt neu“
und Löschen laufen über die vorhandenen Endpunkte (`core/api/blendimport.py`, `blendimportpflege.py`).

GET  /mesh-3D/                                   die Liste (Neuer Auftrag, Tabelle)
GET  /mesh-3D/<kennung>/                         die Jobseite
GET  /api/mesh3d/laufende/                       Kurzstand aller Aufträge (Liste im Takt)
GET  /api/mesh3d/<kennung>/zustand/              der ganze Stand für die Jobseite (`Mesh3dzustand`)
GET  /api/mesh3d/<kennung>/datei/<ordner>/<name> ein Bild des Imports (`ergebnis`, `arbeit`, `figur`)
POST /api/mesh3d/anlegen/                        {format, werte} → Auftrag anlegen, NICHT starten
POST /api/mesh3d/<kennung>/einstellungen/        {werte} → Einstellungen des Auftrags ändern (nicht während eines Laufs)
"""

import json
import logging
import re

from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from ..daten.auftragskennung import Auftragskennung
from ..daten.blendimportablage import Blendimportablage
from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.blendimportarbeiter import Blendimportarbeiter
from ..dienste.blendimportformate import Blendimportformate
from ..dienste.blendimportquelle import Blendimportquelle
from ..dienste.blendimportweg import Blendimportweg
from ..dienste.mesh3dbewegung import Mesh3dbewegung
from ..dienste.mesh3dergebnisse import Mesh3dergebnisse
from ..dienste.mesh3dtabelle import Mesh3dtabelle
from ..dienste.mesh3dzustand import Mesh3dzustand

logger = logging.getLogger('core')

__all__ = ['Mesh3dendpunkte']


class Mesh3dendpunkte:
    #: Bilddateien, die `datei` ausliefert — nur Name und Endung, nie ein Pfad.
    BILDNAME = re.compile(r'^[\w .\-]+\.(png|jpg|jpeg|webp)$', re.IGNORECASE)
    ORDNER = ('ergebnis', 'arbeit', 'figur', 'pose', 'segmentierung')
    #: Diese Felder gehören zur Quelle, nicht zu den Einstellungen, die man auf der Jobseite ändert.
    QUELLFELDER = ('pfad', 'name', 'eigener_name')

    @staticmethod
    def _rumpf(request):
        try:
            daten = json.loads(request.body or b'{}')
        except ValueError:
            return {}
        return daten if isinstance(daten, dict) else {}

    # ---------------------------------------------------------------- Seiten

    @staticmethod
    @require_GET
    def liste(request):
        return render(request, 'mesh3d.html', {'tabelle': Mesh3dtabelle().tabelle()})

    @staticmethod
    @require_GET
    def seite(request, kennung):
        zustand = Mesh3dzustand.von(kennung)
        if zustand is None:
            raise Http404('Kein Auftrag %s' % kennung)
        return render(request, 'mesh3d_auftrag.html', {'job': {'kennung': kennung, 'name': zustand['name']}, 'format': zustand['format']})

    # ---------------------------------------------------------------- Daten

    @staticmethod
    @require_GET
    def laufende(request):
        """Kurzstand je Auftrag — die Liste zieht damit Balken und Status im Takt nach, ohne die Seite neu zu laden."""
        aus = []
        for kennung in Blendimportablage.alle():
            stand = Mesh3dzustand.stand(kennung)
            if stand:
                aus.append({'kennung': kennung, 'status': stand.get('status'), 'fortschritt': stand.get('fortschritt') or 0,
                            'detail': stand.get('detail') or '', 'schritt': stand.get('schritt')})
        return JsonResponse({'auftraege': aus})

    @staticmethod
    @require_GET
    def zustand(request, kennung):
        daten = Mesh3dzustand.von(kennung)
        if daten is None:
            return JsonResponse({'error': 'Kein Auftrag %s' % kennung}, status=404)
        return JsonResponse(daten, json_dumps_params={'default': str})

    @staticmethod
    @require_GET
    def datei(request, kennung, ordner, name):
        stand = Mesh3dzustand.stand(kennung)
        if stand is None or ordner not in Mesh3dendpunkte.ORDNER or not Mesh3dendpunkte.BILDNAME.match(name):
            raise Http404()
        pfad = Mesh3dergebnisse(stand).pfad(ordner, name)
        if pfad is None or not pfad.is_file():
            raise Http404()
        return Auftragsdatei.antwort(request, pfad, kennung=request.GET.get('v'))

    @staticmethod
    @require_GET
    def bewegungsdatei(request, kennung):
        """`bewegung.json` (Spuren je Bild) für die Animationsleiste der 3D-Ansicht — 404, solange sie nicht gerechnet ist."""
        if Mesh3dzustand.stand(kennung) is None:
            raise Http404()
        pfad = Mesh3dbewegung(kennung).pfad()
        if not pfad.is_file():
            raise Http404()
        return Auftragsdatei.antwort(request, pfad, kennung=request.GET.get('v'))

    # ---------------------------------------------------------------- Schreiben

    @staticmethod
    @require_POST
    def bewegung(request, kennung):
        """Die BVH-Bewegung (Vorgabe: der Tanz) auf der Figur dieses Auftrags rechnen — `{bvh?}`; derselbe Retarget-Weg wie bei „2D3D Kleider“ (`Mesh3dbewegung`)."""
        if Mesh3dzustand.stand(kennung) is None:
            return JsonResponse({'error': 'Kein Auftrag %s' % kennung}, status=404)
        try:
            antwort = Mesh3dbewegung(kennung).rechnen(Mesh3dendpunkte._rumpf(request).get('bvh'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, **antwort, 'adresse': '%s?v=%s' % (reverse('mesh3d_bewegungsdatei', args=[kennung]), antwort['stand'])})

    @staticmethod
    @require_POST
    def anlegen(request):
        """Einen Auftrag anlegen, ohne ihn zu starten — die Einstellungen stehen danach auf der Jobseite, „Neu berechnen“ startet."""
        rumpf = Mesh3dendpunkte._rumpf(request)
        format = Blendimportformate.pruefen(rumpf.get('format'))
        klasse = Blendimportformate.einstellungen(format)
        werte = klasse.pruefen(rumpf.get('werte'))
        try:
            quelle = Blendimportquelle(werte['pfad'], werte['name'], werte['eigener_name'], Blendimportformate.endung(format)).steckbrief()
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        try:
            weg, weg_grund = Blendimportweg.erkennen(format, quelle['datei'])
        except (OSError, ValueError) as fehler:
            return JsonResponse({'error': 'Die Datei lässt sich nicht lesen: %s' % fehler}, status=400)
        werte = klasse.speichern(werte)
        kennung = Auftragskennung.frei(timezone.now(), lambda k: Blendimportablage(k).ordner().exists())
        ablage = Blendimportablage(kennung)
        ablage.anlegen()
        ablage.stand_schreiben({'kennung': kennung, 'status': 'neu', 'bereich': 'mesh3d', 'quelle': quelle, 'einstellungen': werte,
                                'weg': weg, 'weg_grund': weg_grund, 'angelegt': timezone.now().isoformat()})
        logger.info('Mesh-3D %s angelegt: %s (%s, Weg %s: %s)', kennung, quelle['name'], format, weg, weg_grund)
        return JsonResponse({'ok': True, 'kennung': kennung, 'quelle': quelle, 'weg': weg, 'weg_grund': weg_grund})

    @staticmethod
    @require_POST
    def einstellungen(request, kennung):
        """Einstellungen ändern (die Quelle bleibt): geprüft gegen den Katalog des Formats, sofort gespeichert, gilt ab „Neu berechnen“."""
        stand = Mesh3dzustand.stand(kennung)
        if stand is None:
            return JsonResponse({'error': 'Kein Auftrag %s' % kennung}, status=404)
        if Blendimportarbeiter.lebt(Blendimportablage(kennung)):
            return JsonResponse({'error': 'Der Auftrag rechnet — die Einstellungen gelten ab dem nächsten Start'}, status=409)
        format = Blendimportformate.pruefen((stand.get('quelle') or {}).get('format'))
        neu = {k: v for k, v in (Mesh3dendpunkte._rumpf(request).get('werte') or {}).items() if k not in Mesh3dendpunkte.QUELLFELDER}
        geprueft = Blendimportformate.einstellungen(format).pruefen({**(stand.get('einstellungen') or {}), **neu})
        geprueft.update({k: v for k, v in (stand.get('einstellungen') or {}).items() if k in Mesh3dendpunkte.QUELLFELDER})
        ablage = Blendimportablage(kennung)
        stand = ablage.stand()
        stand['einstellungen'] = geprueft
        ablage.stand_schreiben(stand)
        return JsonResponse({'ok': True, 'einstellungen': geprueft})
