# -*- coding: utf-8 -*-
"""Modelle und UMA-Figuren aus dem Dialog heraus umbenennen und löschen.

    POST /api/character/katalog/uma/umbenennen/     {alt, neu}
    POST /api/character/katalog/uma/loeschen/       {name}
    POST /api/character/katalog/modell/umbenennen/  {alt, neu}
    POST /api/character/katalog/modell/loeschen/    {name}
    POST /api/character/katalog/loeschen-mehrere/   {art, namen}   (15.10.2026, Mehrfachauswahl im Dialog)

Beides sind Vorgänge, die Dateien verändern, deshalb ausschließlich POST und
mit einer Rückfrage davor im Browser. Die eigentliche Arbeit machen
`Umaablage` (GLB plus Beipackzettel plus Zeiger `aktuell.json`) und
`Modellablage` (eine .json); hier stehen nur Eingabeprüfung und Antwort.

Edgar, 06.09.2026: „Mach auch Möglichkeiten zum Umbenennen und Löschen der
Modelle aus dem Dialog."
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..dienste.modellablage import Modellablage
from ..dienste.umaablage import Ablagefehler, Umaablage

logger = logging.getLogger(__name__)

__all__ = ['Katalogverwaltung']


class Katalogverwaltung:
    #: Ein Name aus dem Browser darf nicht leer und nicht endlos sein.
    HOECHSTENS = 120

    # -- UMA-Figuren ----------------------------------------------------------

    @staticmethod
    @csrf_exempt
    @require_POST
    def uma_umbenennen(request):
        return Katalogverwaltung._umbenennen(request, Umaablage)

    @staticmethod
    @csrf_exempt
    @require_POST
    def uma_loeschen(request):
        return Katalogverwaltung._loeschen(request, Umaablage)

    # -- HumanBody-Modelle ----------------------------------------------------

    @staticmethod
    @csrf_exempt
    @require_POST
    def modell_umbenennen(request):
        return Katalogverwaltung._umbenennen(request, Modellablage)

    @staticmethod
    @csrf_exempt
    @require_POST
    def modell_loeschen(request):
        return Katalogverwaltung._loeschen(request, Modellablage)

    # -- mehrere auf einmal (15.10.2026) ---------------------------------------

    #: Reiter → Ablage; ein gespeichertes Genesis-9-Modell ist eine Modelldatei wie ein HumanBody-Modell.
    ABLAGEN = {'modell': Modellablage, 'genesis9': Modellablage, 'uma': Umaablage}
    HOECHSTENS_MEHRERE = 500

    @staticmethod
    @csrf_exempt
    @require_POST
    def mehrere_loeschen(request):
        """POST /api/character/katalog/loeschen-mehrere/ {art, namen} → {geloescht: [...], fehler: {name: grund}} (Edgar: „ich möchte Modelle batch löschen
        können (Mehrfachauswahl und löschen)“). Die Rückfrage stellt der Dialog EINMAL für alle; gelöscht wird je Modell genau wie beim einzelnen Löschen."""
        cls = Katalogverwaltung
        daten, fehler = cls._daten(request)
        if fehler:
            return fehler
        ablage = cls.ABLAGEN.get(str(daten.get('art') or ''))
        namen = [str(n).strip()[: cls.HOECHSTENS] for n in (daten.get('namen') or []) if str(n).strip()]
        if ablage is None or not namen or len(namen) > cls.HOECHSTENS_MEHRERE:
            return JsonResponse({'error': 'art (modell, genesis9, uma) und 1 bis %d namen angeben' % cls.HOECHSTENS_MEHRERE}, status=400)
        geloescht, gescheitert = [], {}
        for name in namen:
            try:
                ablage.loeschen(name)
                geloescht.append(name)
            except (Ablagefehler, OSError) as f:
                logger.exception('Löschen fehlgeschlagen: %s', name)
                gescheitert[name] = str(f)
        logger.info('Mehrere gelöscht (%s): %d, gescheitert %d', daten.get('art'), len(geloescht), len(gescheitert))
        return JsonResponse({'geloescht': geloescht, 'fehler': gescheitert})

    # -- gemeinsam ------------------------------------------------------------

    @classmethod
    def _umbenennen(cls, request, ablage):
        daten, fehler = cls._daten(request)
        if fehler:
            return fehler
        alt, neu = cls._text(daten, 'alt'), cls._text(daten, 'neu')
        if not alt or not neu:
            return JsonResponse({'error': 'alt und neu angeben'}, status=400)
        if alt == neu:
            return JsonResponse({'name': neu, 'unveraendert': True})
        try:
            return JsonResponse({'name': ablage.umbenennen(alt, neu)})
        except Ablagefehler as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        except OSError as fehler:
            logger.exception('Umbenennen fehlgeschlagen: %s -> %s', alt, neu)
            return JsonResponse({'error': str(fehler)}, status=500)

    @classmethod
    def _loeschen(cls, request, ablage):
        daten, fehler = cls._daten(request)
        if fehler:
            return fehler
        name = cls._text(daten, 'name')
        if not name:
            return JsonResponse({'error': 'name angeben'}, status=400)
        try:
            ablage.loeschen(name)
            return JsonResponse({'geloescht': name})
        except Ablagefehler as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        except OSError as fehler:
            logger.exception('Löschen fehlgeschlagen: %s', name)
            return JsonResponse({'error': str(fehler)}, status=500)

    @staticmethod
    def _daten(request):
        try:
            return json.loads(request.body or b'{}'), None
        except ValueError:
            return None, JsonResponse({'error': 'Kein gültiges JSON'}, status=400)

    @classmethod
    def _text(cls, daten, feld):
        wert = (daten.get(feld) or '').strip()
        return wert[: cls.HOECHSTENS]
