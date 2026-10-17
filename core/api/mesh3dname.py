# -*- coding: utf-8 -*-
"""Mesh3dnameendpunkte — den Namen eines Mesh-3D-Auftrags ändern (12.10.2026), siehe `Mesh3dname`.

    POST /api/mesh3d/<kennung>/name/   {name}  → {ok, name}

Dieselbe Antwortform wie `Auftragsnameendpunkte` bei den anderen Bereichen, damit `gemeinsam/auftragname.js` ohne Änderung bedient wird. Der Name wird gesäubert (`Blendimportquelle.eigener`) und
kommt gesäubert zurück; auch ein Auftrag, der rechnet, lässt sich umbenennen (der Lauf übernimmt den Namen).
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..dienste.mesh3dname import Mesh3dname

logger = logging.getLogger('core')

__all__ = ['Mesh3dnameendpunkte']


class Mesh3dnameendpunkte:
    @staticmethod
    @require_POST
    def setzen(request, kennung):
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Rumpf ist kein JSON mit name'}, status=400)
        rumpf = rumpf if isinstance(rumpf, dict) else {}
        try:
            auftrag = Mesh3dname(kennung)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=404)
        alt = (auftrag.stand.get('quelle') or {}).get('name')
        try:
            name = auftrag.setzen(rumpf.get('name'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        mit = getattr(auftrag, 'angeglichen', {})
        logger.info('mesh3d %s umbenannt: „%s" → „%s" (Auftrag Mesh to 3D: %s, Modell: %s)', kennung, alt, name, mit.get('figur'), mit.get('modell'))
        return JsonResponse({'ok': True, 'name': name, 'figur': mit.get('figur'), 'modell': mit.get('modell')})
