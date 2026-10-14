# -*- coding: utf-8 -*-
"""Mesh3dreiterendpunkte — Aufträge der Seite „Mesh-3D“ von einem Reiter in den anderen verschieben (13.10.2026), siehe `Mesh3dreiter`.

    POST /api/mesh3d/reiter/verschieben/   {ids: [kennung, …], reiter: "test"}  → {ok, verschoben, reiter}

Verschoben wird nur die Zuordnung; der Auftrag, sein Ordner und ein laufender Lauf bleiben unberührt (auch ein rechnender Auftrag darf den Reiter wechseln).
"""

import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..dienste.mesh3dreiter import Mesh3dreiter

__all__ = ['Mesh3dreiterendpunkte']


class Mesh3dreiterendpunkte:
    #: Wie beim Kopieren: mehr in einem Zug nur auf ausdrücklichen Wunsch.
    HOECHSTENS = 200

    @staticmethod
    def _rumpf(request):
        try:
            daten = json.loads(request.body or b'{}')
        except ValueError:
            return {}
        return daten if isinstance(daten, dict) else {}

    @staticmethod
    @require_POST
    def verschieben(request):
        rumpf = Mesh3dreiterendpunkte._rumpf(request)
        ids = [str(k) for k in (rumpf.get('ids') or []) if k][:Mesh3dreiterendpunkte.HOECHSTENS]
        if not ids:
            return JsonResponse({'error': 'Kein Auftrag gewählt'}, status=400)
        try:
            verschoben = Mesh3dreiter.setzen(ids, rumpf.get('reiter'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'verschoben': verschoben, 'reiter': rumpf.get('reiter')})
