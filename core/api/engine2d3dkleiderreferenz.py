# -*- coding: utf-8 -*-
"""Endpunkt „Referenzvideo" von „2D3D Kleider" (04.10.2026).

    POST /api/engine2d3dkleider/<id>/referenz/   {pfad}   → {ok, referenz: {video, quelle, bytes}}

Kopiert die genannte Videodatei (Franks Ergebnis, `Model_Jobs/Frank/Randy/vid2.mp4`) nach `referenz/` des Auftrags; die Seite spielt sie neben den Vorlagebildern ab. Den Stand
trägt der Zustand des Auftrags (`referenz`). Geliefert wird die Datei vom Datei-Endpunkt (`…/datei/referenz/<name>`, mit Bereichsanfragen, damit das Springen im Video geht).
"""

import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..dienste.engine2d3dkleiderreferenz import Engine2d3dKleiderreferenz
from ..models import Engine2d3dKleiderauftrag
from .engine2d3dkleider import Engine2d3dKleiderendpunkte

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderreferenzendpunkte']


class Engine2d3dKleiderreferenzendpunkte:
    @staticmethod
    @require_POST
    def uebernehmen(request, job_id):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        rumpf = Engine2d3dKleiderendpunkte.rumpf(request)
        try:
            bericht = Engine2d3dKleiderreferenz(job).uebernehmen(rumpf.get('pfad'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        except OSError as fehler:
            logger.warning('2D3D Kleider %s: Referenzvideo nicht kopiert (%s)', job.kennung, fehler)
            return JsonResponse({'error': 'Das Video ließ sich nicht kopieren: %s' % fehler}, status=500)
        logger.info('2D3D Kleider %s: Referenzvideo %s (%d Bytes)', job.kennung, bericht['video'], bericht['bytes'])
        return JsonResponse({'ok': True, 'referenz': bericht})
