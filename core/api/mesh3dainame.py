# -*- coding: utf-8 -*-
"""Mesh3dainameendpunkte — den Namen eines Jobs oder Tests von Mesh3D-AI ändern (19.10.2026), siehe `Mesh3dainame`.

    POST /api/mesh3dai/<job>/name/             {name}  → {ok, name}
    POST /api/mesh3dai/test/<kennung>/name/    {name}  → {ok, name}

Dieselbe Antwortform wie `Auftragsnameendpunkte` und `Mesh3dnameendpunkte`, damit `gemeinsam/auftragname.js` ohne Änderung bedient wird. Kennung und Adresse bleiben.
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..dienste.mesh3daiattrappe import Mesh3daiattrappe
from ..dienste.mesh3dainame import Mesh3dainame
from ..dienste.mesh3daitest import Mesh3daitest

logger = logging.getLogger('core')

__all__ = ['Mesh3dainameendpunkte']


class Mesh3dainameendpunkte:
    @staticmethod
    @require_POST
    def job(request, job):
        gefunden = Mesh3daiattrappe.job(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Job %s' % job}, status=404)
        return Mesh3dainameendpunkte._setzen(request, 'Job %s' % gefunden['id'], Mesh3dainame.wurzel() / gefunden['ordner'], gefunden['name'], gefunden['name_vorgabe'])

    @staticmethod
    @require_POST
    def test(request, kennung):
        ordner = Mesh3daitest.pfad(kennung)
        if ordner is None:
            return JsonResponse({'error': 'Kein Test %s' % kennung}, status=404)
        try:
            vorgabe = str(json.loads((ordner / 'test.json').read_text(encoding='utf-8')).get('name') or kennung)
        except (OSError, ValueError, AttributeError):
            vorgabe = kennung
        return Mesh3dainameendpunkte._setzen(request, 'Test %s' % kennung, ordner, Mesh3dainame.lesen(ordner) or vorgabe, vorgabe)

    @staticmethod
    def _setzen(request, wer, ordner, alt, vorgabe):
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Rumpf ist kein JSON mit name'}, status=400)
        try:
            name = Mesh3dainame.setzen(ordner, rumpf.get('name') if isinstance(rumpf, dict) else None, vorgabe)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        logger.info('Mesh3D-AI %s umbenannt: „%s“ → „%s“ (ursprünglich „%s“)', wer, alt, name, vorgabe)
        return JsonResponse({'ok': True, 'name': name})
