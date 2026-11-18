# -*- coding: utf-8 -*-
"""Standardmodellpflegeendpunkte — Standard-Modelle im Dialog „Charakter hinzufügen“ umbenennen und ausblenden (16.11.2026), siehe `Standardmodellpflege`.

    GET  /api/character/katalog/standard/              → {quelle: {namen: {name: anzeige}, ausgeblendet: [name]}}
    POST /api/character/katalog/standard/umbenennen/   {quelle, name, neu}   → {ok, anzeige}     neu leer = zurück zur Vorgabe
    POST /api/character/katalog/standard/loeschen/     {quelle, name}        → {ok}              blendet aus; die Daten bleiben
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.standardmodellpflege import Standardmodellpflege

logger = logging.getLogger('core')

__all__ = ['Standardmodellpflegeendpunkte']


class Standardmodellpflegeendpunkte:
    @staticmethod
    @require_GET
    def liste(request):
        try:
            return JsonResponse(Standardmodellpflege.lesen())
        except (OSError, ValueError) as fehler:
            return JsonResponse({'error': 'Pflege der Standard-Modelle nicht lesbar: %s' % fehler}, status=500)

    @staticmethod
    @require_POST
    def umbenennen(request):
        rumpf = Standardmodellpflegeendpunkte._rumpf(request)
        try:
            anzeige = Standardmodellpflege.umbenennen(str(rumpf.get('quelle') or ''), rumpf.get('name'), rumpf.get('neu'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'anzeige': anzeige})

    @staticmethod
    @require_POST
    def loeschen(request):
        rumpf = Standardmodellpflegeendpunkte._rumpf(request)
        try:
            Standardmodellpflege.ausblenden(str(rumpf.get('quelle') or ''), rumpf.get('name'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True})

    @staticmethod
    def _rumpf(request):
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return {}
        return rumpf if isinstance(rumpf, dict) else {}
