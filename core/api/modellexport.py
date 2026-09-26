# -*- coding: utf-8 -*-
"""Modellexport — Endpunkt für „Exportieren …" im Kontextmenü der Modellzeile.

Der Browser hat die Formate schon geschrieben (GLB/OBJ/PLY/STL/DAE, siehe
`static/viewer/scene/modellexport.js`); hier werden sie nur noch abgelegt.
Nur `.blend` läuft noch durch Blender (`core/dienste/modellexportlauf.py`).
"""

import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..dienste.modellexportlauf import Modellexportlauf, ZielAbgelehnt

logger = logging.getLogger('core')


class Modellexportanfrage:
    """`vorgabe` liefert den Startordner, `ablegen` nimmt den Export an."""

    @staticmethod
    @require_GET
    def vorgabe(request):
        return JsonResponse({'ordner': str(settings.HUMANBODY_MODELLEXPORT_VORGABE_DIR)})

    @staticmethod
    @csrf_exempt
    @require_POST
    def ablegen(request):
        dateien = request.FILES.getlist('dateien')
        if not dateien and 'blend_quelle' not in request.FILES:
            return JsonResponse({'error': 'Keine Datei zum Ablegen'}, status=400)
        lauf = Modellexportlauf(
            ordner_roh=request.POST.get('ordner'),
            name_roh=request.POST.get('name'),
            dateien=dateien,
            blend_quelle=request.FILES.get('blend_quelle'),
        )
        try:
            ergebnis = lauf.ausfuehren()
        except ZielAbgelehnt as e:
            return JsonResponse({'error': str(e)}, status=400)
        warnungen = _liste(request.POST.get('warnungen'))
        if warnungen:
            logger.info('Modellexport: %s — Warnungen: %s', ergebnis['ordner'], '; '.join(warnungen))
        ergebnis['warnungen'] = warnungen
        return JsonResponse(ergebnis)


def _liste(roh):
    try:
        werte = json.loads(roh or '[]')
    except (json.JSONDecodeError, ValueError):
        return []
    return [str(w) for w in werte] if isinstance(werte, list) else []
