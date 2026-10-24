# -*- coding: utf-8 -*-
"""Mesh3daipapierkorbendpunkt — gewählte Jobs oder Tests von `/mesh-3D-AI/` beiseitelegen (23.10.2026), siehe `Mesh3daipapierkorb`.

    POST /api/mesh3dai/loeschen/   {art: 'jobs'|'tests', ids: [...]}  → {ok, ziel, ergebnis: [{kennung, ok, fehler?}]}
"""

import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..dienste.mesh3daipapierkorb import Mesh3daipapierkorb

__all__ = ['Mesh3daipapierkorbendpunkt']


class Mesh3daipapierkorbendpunkt:
    @staticmethod
    @require_POST
    def loeschen(request):
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Rumpf ist kein JSON'}, status=400)
        art, ids = (rumpf.get('art'), rumpf.get('ids')) if isinstance(rumpf, dict) else (None, None)
        if art not in Mesh3daipapierkorb.ARTEN or not isinstance(ids, list) or not ids:
            return JsonResponse({'error': 'Erwartet {art: jobs|tests, ids: [...]}'}, status=400)
        aus = Mesh3daipapierkorb.loeschen(art, ids)
        return JsonResponse(dict(aus, ok=all(e['ok'] for e in aus['ergebnis'])))
