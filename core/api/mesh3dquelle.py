# -*- coding: utf-8 -*-
"""Mesh3dquelleendpunkte — Datei und Name eines Mesh-3D-Auftrags ändern (11.10.2026), siehe `Mesh3dquellwechsel`.

    POST /api/mesh3d/<kennung>/quelle/   {pfad, eigener_name?}  → {ok, quelle, weg, weg_grund, neues_netz, verworfen}

Ein anderes Netz verwirft die Ergebnisse des Auftrags (`neues_netz`, `verworfen` = der entfernte Auftrag „Mesh to 3D“); nur ein anderer Name lässt sie stehen. Ein Auftrag, der rechnet, ist 409.
"""

import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..dienste.mesh3dquellwechsel import Mesh3dquellwechsel

__all__ = ['Mesh3dquelleendpunkte']


class Mesh3dquelleendpunkte:
    @staticmethod
    @require_POST
    def aendern(request, kennung):
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            rumpf = {}
        rumpf = rumpf if isinstance(rumpf, dict) else {}
        try:
            wechsel = Mesh3dquellwechsel(kennung)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=404)
        try:
            return JsonResponse({'ok': True, **wechsel.wechseln(rumpf.get('pfad'), rumpf.get('eigener_name'))})
        except Mesh3dquellwechsel.Laeuft as fehler:
            return JsonResponse({'error': str(fehler)}, status=409)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
