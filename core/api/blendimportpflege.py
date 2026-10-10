# -*- coding: utf-8 -*-
"""Blendimportpflegeendpunkte — Importe löschen, abbrechen und die verwaisten aufräumen (10.10.2026).

GET  /api/character/blendimport/verwaist/                  {importe: [Plan]} — Importe, die niemandem mehr dienen (`Blendimportloeschen.verwaiste`)
POST /api/character/blendimport/verwaist/loeschen/         {kennungen?} → {geloescht, fehler}; ohne Liste alle verwaisten
GET  /api/character/blendimport/<kennung>/loeschplan/      Plan: Name, Größe, Auftrag, Stücke, Modelle — für die Rückfrage
POST /api/character/blendimport/<kennung>/loeschen/        {mit_modell?, anhalten?, stuecke_trotzdem?} → Ergebnis; 409, wenn er rechnet und `anhalten` fehlt;
                                                           `stuecke_trotzdem` entfernt auch Stücke, die ein Modell oder ein anderer Import noch braucht

„Abbrechen" in der Leiste oben ist `loeschen` mit `anhalten: true` (Edgar, 10.10.2026: „der Abbrechen löscht auch alle Importdaten").
Der Dienst: `core/dienste/blendimportloeschen.py`.
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.blendimportloeschen import Blendimportloeschen, ImportLaeuft, ImportNichtGeloescht

logger = logging.getLogger('core')

__all__ = ['Blendimportpflegeendpunkte']


class Blendimportpflegeendpunkte:

    @staticmethod
    def _rumpf(request):
        try:
            daten = json.loads(request.body or b'{}')
        except ValueError:
            return {}
        return daten if isinstance(daten, dict) else {}

    @staticmethod
    def _import(kennung):
        """Der Dienst für diese Kennung — oder `None`, wenn es den Import nicht gibt."""
        try:
            dienst = Blendimportloeschen(kennung)
        except ValueError:
            return None
        return dienst if dienst.vorhanden() else None

    @staticmethod
    @require_GET
    def verwaist(request):
        return JsonResponse({'importe': Blendimportloeschen.verwaiste()})

    @staticmethod
    @require_GET
    def loeschplan(request, kennung):
        dienst = Blendimportpflegeendpunkte._import(kennung)
        if dienst is None:
            return JsonResponse({'error': 'Kein Import %s' % kennung}, status=404)
        return JsonResponse(dienst.plan())

    @staticmethod
    @require_POST
    def loeschen(request, kennung):
        dienst = Blendimportpflegeendpunkte._import(kennung)
        if dienst is None:
            return JsonResponse({'error': 'Kein Import %s' % kennung}, status=404)
        rumpf = Blendimportpflegeendpunkte._rumpf(request)
        try:
            ergebnis = dienst.loeschen(mit_modell=rumpf.get('mit_modell', True) is not False, anhalten=rumpf.get('anhalten') is True,
                                       stuecke_trotzdem=rumpf.get('stuecke_trotzdem') is True)
        except ImportLaeuft as grund:
            return JsonResponse({'error': str(grund)}, status=409)
        except (ImportNichtGeloescht, OSError) as grund:
            logger.warning('Blender-Import %s nicht gelöscht: %s', kennung, grund)
            return JsonResponse({'error': str(grund)}, status=500)
        return JsonResponse({'ok': True, **ergebnis})

    @staticmethod
    @require_POST
    def verwaiste_loeschen(request):
        kennungen = Blendimportpflegeendpunkte._rumpf(request).get('kennungen')
        if kennungen is not None and not isinstance(kennungen, list):
            return JsonResponse({'error': 'kennungen muss eine Liste sein'}, status=400)
        ergebnis = Blendimportloeschen.verwaiste_loeschen(None if kennungen is None else {str(k) for k in kennungen})
        return JsonResponse({'ok': not ergebnis['fehler'], **ergebnis})
