# -*- coding: utf-8 -*-
"""Meshgenesisnameendpunkte — den Namen eines Jobs oder Tests von Mesh-Genesis ändern (19.10.2026), siehe `Meshgenesisname`.

    POST /api/meshgenesis/<job>/name/             {name}  → {ok, name}
    POST /api/meshgenesis/test/<kennung>/name/    {name}  → {ok, name}

Dieselbe Antwortform wie `Auftragsnameendpunkte` und `Mesh3dnameendpunkte`, damit `gemeinsam/auftragname.js` ohne Änderung bedient wird. Kennung und Adresse bleiben.
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..dienste.meshgenesisattrappe import Meshgenesisattrappe
from ..dienste.meshgenesisname import Meshgenesisname
from ..dienste.meshgenesistest import Meshgenesistest

logger = logging.getLogger('core')

__all__ = ['Meshgenesisnameendpunkte']


class Meshgenesisnameendpunkte:
    @staticmethod
    @require_POST
    def job(request, job):
        gefunden = Meshgenesisattrappe.job(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Job %s' % job}, status=404)
        return Meshgenesisnameendpunkte._setzen(request, 'Job %s' % gefunden['id'], Meshgenesisname.wurzel() / gefunden['ordner'], gefunden['name'], gefunden['name_vorgabe'])

    @staticmethod
    @require_POST
    def test(request, kennung):
        ordner = Meshgenesistest.pfad(kennung)
        if ordner is None:
            return JsonResponse({'error': 'Kein Test %s' % kennung}, status=404)
        try:
            vorgabe = str(json.loads((ordner / 'test.json').read_text(encoding='utf-8')).get('name') or kennung)
        except (OSError, ValueError, AttributeError):
            vorgabe = kennung
        return Meshgenesisnameendpunkte._setzen(request, 'Test %s' % kennung, ordner, Meshgenesisname.lesen(ordner) or vorgabe, vorgabe)

    @staticmethod
    def _setzen(request, wer, ordner, alt, vorgabe):
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Rumpf ist kein JSON mit name'}, status=400)
        try:
            name = Meshgenesisname.setzen(ordner, rumpf.get('name') if isinstance(rumpf, dict) else None, vorgabe)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        logger.info('Mesh-Genesis %s umbenannt: „%s“ → „%s“ (ursprünglich „%s“)', wer, alt, name, vorgabe)
        return JsonResponse({'ok': True, 'name': name})
