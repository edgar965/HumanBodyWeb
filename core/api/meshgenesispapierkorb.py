# -*- coding: utf-8 -*-
"""Meshgenesispapierkorbendpunkt — gewählte Jobs oder Tests von `/mesh-genesis/` beiseitelegen (23.10.2026), siehe `Meshgenesispapierkorb`.

    POST /api/meshgenesis/loeschen/   {art: 'jobs'|'tests', ids: [...]}  → {ok, ziel, ergebnis: [{kennung, ok, fehler?}]}
"""

import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..dienste.meshgenesispapierkorb import Meshgenesispapierkorb

__all__ = ['Meshgenesispapierkorbendpunkt']


class Meshgenesispapierkorbendpunkt:
    @staticmethod
    @require_POST
    def loeschen(request):
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Rumpf ist kein JSON'}, status=400)
        art, ids = (rumpf.get('art'), rumpf.get('ids')) if isinstance(rumpf, dict) else (None, None)
        if art not in Meshgenesispapierkorb.ARTEN or not isinstance(ids, list) or not ids:
            return JsonResponse({'error': 'Erwartet {art: jobs|tests, ids: [...]}'}, status=400)
        aus = Meshgenesispapierkorb.loeschen(art, ids)
        return JsonResponse(dict(aus, ok=all(e['ok'] for e in aus['ergebnis'])))
