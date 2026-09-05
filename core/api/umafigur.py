# -*- coding: utf-8 -*-
u"""UMA-Figur aus dem Figurkatalog: Dateien, Beipackzettel, Form-Regler.

WARUM (05.09.2026): Die Szene-Seite (`/humanbody/scene/`) lädt neben den
HumanBody-Modellen eine UMA-Figur aus `Figuren/uma/` — dieselbe GLB, die
Unity für Roomguest ablegt. Nichts hier schreibt; der Katalog bleibt, wie
der Vertrag (`Figuren/VERTRAG.md`) ihn beschreibt.

    GET /api/character/uma-figur/                 {figuren: [{name, bytes, stand,
                                                   geschlecht, zettel}], aktuell}
    GET /api/character/uma-figur/<name>/          die GLB (mit Last-Modified;
                                                   304 bei If-Modified-Since)
    GET /api/character/uma-figur/<name>/zettel/   der Beipackzettel
    GET /api/character/uma-regler/?figur=<name>   Regler-Gruppen fürs Geschlecht
                                                   der Figur (oder ?geschlecht=)
    GET  /api/character/uma-rassen/               {rassen, ermittelt, figuren:[{name, rasse}]}
    POST /api/character/uma-rassen/ermitteln/     Unity schreibt die Rassenliste (202)
    POST /api/character/uma-figur/bauen/          {rasse, name?, zeiger?} → Unity baut (202)
    GET  /api/character/uma-figur/bauen/<name>/stand/   {laeuft, exit, sekunden, datei, meldung}

Bauen auf Zuruf (06.09.2026): `core/dienste/umabauer.py` startet Unity ohne
Fenster; die Seite fragt den Stand ab, bis die Datei im Katalog liegt.
"""
import json
import logging
import os
import re
import time

from django.conf import settings
from django.http import FileResponse, HttpResponseNotModified, JsonResponse
from django.utils.http import http_date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.views.static import was_modified_since

from ..dienste.umabauer import Umabauer, UmabauerBelegt, UmabauerFehlt
from ..dienste.umaformregler import Umaformregler, UmaformreglerFehlt
from ..dienste.umaskelett import Umaskelett, UmaskelettFehlt

logger = logging.getLogger('core')

__all__ = ['Umafigur']


class Umafigur:
    u"""Lesende Endpunkte auf `Figuren/uma/`."""

    TYP = 'model/gltf-binary'
    #: Ein Dateiname, kein Pfad: Buchstaben, Ziffern, Leerzeichen, Punkt, Strich.
    NAME = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_ .\-]*\.glb$')
    ZEITFORMAT = '%Y-%m-%d %H:%M:%S'
    #: Der Zettel nennt die Rasse im Satz „Rasse Human Male 3.0, 12 Kleidungsstücke: …".
    RASSE = re.compile(r'Rasse ([^,]+),')

    # ------------------------------------------------------------ Helfer

    @staticmethod
    def _ordner():
        return os.path.join(str(settings.FIGUREN_KATALOG), Umaskelett.QUELLE)

    @classmethod
    def _pfad(cls, name):
        if not cls.NAME.match(name or '') or '..' in name:
            raise ValueError('Ungültiger Figurname: %r' % (name,))
        pfad = os.path.join(cls._ordner(), name)
        if not os.path.isfile(pfad):
            raise FileNotFoundError(name)
        return pfad

    @classmethod
    def _pfad_oder_antwort(cls, name):
        u"""`(pfad, None)` — oder `(None, JsonResponse)` mit 400/404."""
        try:
            return cls._pfad(name), None
        except ValueError as fehler:
            return None, JsonResponse({'error': str(fehler)}, status=400)
        except FileNotFoundError:
            return None, JsonResponse({'error': 'Keine UMA-Figur %s' % name}, status=404)

    @staticmethod
    def _zettel(glb_pfad):
        u"""Der Beipackzettel neben der GLB; `None`, wenn er fehlt oder unlesbar ist."""
        pfad = glb_pfad[:-4] + '.json'
        if not os.path.isfile(pfad):
            return None
        try:
            with open(pfad, encoding='utf-8') as datei:
                return json.load(datei)
        except (OSError, ValueError):
            logger.warning('Umafigur: Zettel %s unlesbar', pfad, exc_info=True)
            return None

    @classmethod
    def _rasse(cls, zettel):
        treffer = cls.RASSE.search((zettel or {}).get('hinweis') or '')
        return treffer.group(1).strip() if treffer else None

    @classmethod
    def _rasse_der_datei(cls, pfad):
        u"""Rasse aus dem Zettel — eine bewegte Fassung (`…_bewegt.glb`) erbt sie von ihrer Vorlage."""
        rasse = cls._rasse(cls._zettel(pfad))
        if rasse is None and pfad.lower().endswith('_bewegt.glb'):
            rasse = cls._rasse(cls._zettel(pfad[:-len('_bewegt.glb')] + '.glb'))
        return rasse

    @classmethod
    def _eintrag(cls, pfad):
        zettel = cls._zettel(pfad)
        stat = os.stat(pfad)
        return {
            'name': os.path.basename(pfad),
            'bytes': stat.st_size,
            'stand': time.strftime(cls.ZEITFORMAT, time.localtime(stat.st_mtime)),
            'geschlecht': Umaformregler.geschlecht_aus_zettel(zettel),
            'rasse': cls._rasse_der_datei(pfad),
            'zettel': zettel,
        }

    @classmethod
    def _pfade(cls):
        ordner = cls._ordner()
        if not os.path.isdir(ordner):
            return []
        pfade = [os.path.join(ordner, n) for n in os.listdir(ordner) if n.lower().endswith('.glb')]
        pfade.sort(key=os.path.getmtime, reverse=True)
        return pfade

    # ---------------------------------------------------------- Endpunkte

    @staticmethod
    @require_GET
    def liste(request):
        pfade = Umafigur._pfade()
        try:
            aktuell = os.path.basename(Umaskelett.glb_pfad())
        except UmaskelettFehlt as fehler:
            logger.info('Umafigur: keine gültige Figur im Katalog — %s', fehler)
            aktuell = None
        return JsonResponse({
            'figuren': [Umafigur._eintrag(p) for p in pfade],
            'aktuell': aktuell,
            'ordner': Umafigur._ordner(),
        })

    @staticmethod
    @require_GET
    def datei(request, name):
        pfad, antwort = Umafigur._pfad_oder_antwort(name)
        if antwort:
            return antwort
        stat = os.stat(pfad)
        if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'), stat.st_mtime):
            return HttpResponseNotModified()
        antwort = FileResponse(open(pfad, 'rb'), content_type=Umafigur.TYP)
        antwort['Last-Modified'] = http_date(stat.st_mtime)
        antwort['Content-Length'] = str(stat.st_size)
        return antwort

    @staticmethod
    @require_GET
    def zettel(request, name):
        pfad, antwort = Umafigur._pfad_oder_antwort(name)
        if antwort:
            return antwort
        zettel = Umafigur._zettel(pfad)
        if zettel is None:
            return JsonResponse({'error': 'Kein Beipackzettel zu %s' % name}, status=404)
        return JsonResponse(zettel)

    @staticmethod
    @require_GET
    def regler(request):
        geschlecht = request.GET.get('geschlecht')
        figur = request.GET.get('figur')
        if figur and not geschlecht:
            pfad, antwort = Umafigur._pfad_oder_antwort(figur)
            if antwort:
                return antwort
            geschlecht = Umaformregler.geschlecht_aus_zettel(Umafigur._zettel(pfad))
        if not geschlecht:
            try:
                geschlecht = Umaformregler.geschlecht_aus_zettel(
                    Umafigur._zettel(Umaskelett.glb_pfad()))
            except UmaskelettFehlt as fehler:
                return JsonResponse({'error': str(fehler)}, status=404)
        try:
            return JsonResponse(Umaformregler.holen(geschlecht))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        except UmaformreglerFehlt as fehler:
            return JsonResponse({'error': str(fehler)}, status=404)
        except (OSError, KeyError) as fehler:
            logger.error('Umafigur: Regler unlesbar', exc_info=True)
            return JsonResponse({'error': 'Regler unlesbar: %s' % fehler}, status=500)

    # ------------------------------------------------- Bauen auf Zuruf (Unity)

    @staticmethod
    @require_GET
    def rassen(request):
        u"""Rassen aus Unitys Liste und die Figuren im Katalog mit ihrer Rasse."""
        rassen = Umabauer.rassen()
        figuren = [{'name': os.path.basename(pfad), 'rasse': Umafigur._rasse_der_datei(pfad)}
                   for pfad in Umafigur._pfade()]
        return JsonResponse({'rassen': rassen or [], 'ermittelt': rassen is not None, 'figuren': figuren})

    @staticmethod
    @csrf_exempt
    @require_POST
    def rassen_ermitteln(request):
        return Umafigur._lauf(Umabauer.rassen_ermitteln)

    @staticmethod
    @csrf_exempt
    @require_POST
    def bauen(request):
        try:
            daten = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Kein JSON'}, status=400)
        kleidung = daten.get('kleidung')
        if kleidung is not None and not isinstance(kleidung, list):
            return JsonResponse({'error': 'kleidung muss eine Liste von Rezeptnamen sein'}, status=400)
        return Umafigur._lauf(Umabauer.bauen, daten.get('rasse'), daten.get('name'),
                              bool(daten.get('zeiger')), kleidung)

    @staticmethod
    def _lauf(start, *args):
        u"""Einen Unity-Lauf starten; 202 mit dem Stand, sonst 400/409/503."""
        try:
            return JsonResponse(start(*args), status=202)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        except UmabauerBelegt as fehler:
            return JsonResponse({'error': str(fehler)}, status=409)
        except UmabauerFehlt as fehler:
            return JsonResponse({'error': str(fehler)}, status=503)

    @staticmethod
    @require_GET
    def bau_stand(request, name):
        stand = Umabauer.stand(name)
        if stand is None:
            return JsonResponse({'error': 'Kein Lauf %s' % name}, status=404)
        return JsonResponse(stand)
