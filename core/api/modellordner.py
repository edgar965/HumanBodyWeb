# -*- coding: utf-8 -*-
"""Modellordnerendpunkte — Ordner der gespeicherten Modelle im Dialog „Charakter hinzufügen“ (15.10.2026), siehe `Modellordner`.

    GET  /api/character/modellordner/                 → {quelle: {ordner: [...], modelle: {name: ordner}}}
    POST /api/character/modellordner/anlegen/         {quelle, name}            → {ok, name}
    POST /api/character/modellordner/verschieben/     {quelle, namen, ordner}   → {ok, anzahl}     ordner leer = ohne Ordner
    POST /api/character/modellordner/umbenennen/      {quelle, ordner, name}    → {ok, name}
    POST /api/character/modellordner/loeschen/        {quelle, ordner}          → {ok, anzahl}     anzahl = Modelle, die jetzt ohne Ordner stehen
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.modellordner import Modellordner

logger = logging.getLogger('core')

__all__ = ['Modellordnerendpunkte']


class Modellordnerendpunkte:
    @staticmethod
    @require_GET
    def liste(request):
        try:
            return JsonResponse(Modellordner.lesen())
        except (OSError, ValueError) as fehler:
            return JsonResponse({'error': 'Ordnerliste nicht lesbar: %s' % fehler}, status=500)

    @staticmethod
    @require_POST
    def anlegen(request):
        rumpf = Modellordnerendpunkte._rumpf(request)
        try:
            name = Modellordner.anlegen(str(rumpf.get('quelle') or ''), rumpf.get('name'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'name': name})

    @staticmethod
    @require_POST
    def verschieben(request):
        rumpf = Modellordnerendpunkte._rumpf(request)
        namen = rumpf.get('namen') if isinstance(rumpf.get('namen'), list) else []
        try:
            anzahl = Modellordner.verschieben(str(rumpf.get('quelle') or ''), namen, str(rumpf.get('ordner') or ''))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'anzahl': anzahl})

    @staticmethod
    @require_POST
    def umbenennen(request):
        rumpf = Modellordnerendpunkte._rumpf(request)
        try:
            name = Modellordner.ordner_umbenennen(str(rumpf.get('quelle') or ''), str(rumpf.get('ordner') or ''), rumpf.get('name'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'name': name})

    @staticmethod
    @require_POST
    def loeschen(request):
        rumpf = Modellordnerendpunkte._rumpf(request)
        try:
            anzahl = Modellordner.ordner_loeschen(str(rumpf.get('quelle') or ''), str(rumpf.get('ordner') or ''))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'anzahl': anzahl})

    @staticmethod
    def _rumpf(request):
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return {}
        return rumpf if isinstance(rumpf, dict) else {}
