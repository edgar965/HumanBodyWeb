# -*- coding: utf-8 -*-
"""Engine2d3dKleideranimexportendpunkte — das Modell der besten Runde mit der Bewegung als GLB und Blender-Datei (01.10.2026).

    POST /api/engine2d3dkleider/<id>/animexport/   {glb?: true, blend?: true, bvh?: true, bvh_pfad?: '', audio?: true, audio_pfad?: '', name?: ''}
        → {kanaele, fehlend, bilder, sekunden, runde, bvh, audio, glb: {datei, bytes, adresse},
           blend: {datei, bytes, adresse} | {fehler}, ablage: {ordner, dateien}}

Rechnet im Anfrageprozess (`Engine2d3dKleideranimexport`: umpacken in Sekundenbruchteilen, Blender ~10 s). Während der Auftrag
rechnet: 409 — die Runden-GLB und die Bewegung könnten gerade neu geschrieben werden.
"""

import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..dienste.engine2d3dkleideranimexport import Engine2d3dKleideranimexport
from ..dienste.engine2d3dkleiderarbeiter import Engine2d3dKleiderarbeiter
from ..models import Engine2d3dKleiderauftrag
from .engine2d3dkleider import Engine2d3dKleiderendpunkte

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleideranimexportendpunkte']


class Engine2d3dKleideranimexportendpunkte:
    @staticmethod
    @require_POST
    def exportieren(request, job_id):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        if job.laeuft and Engine2d3dKleiderarbeiter.lebt(job):
            return JsonResponse({'error': 'Auftrag läuft — exportieren, wenn er fertig ist'}, status=409)
        rumpf = Engine2d3dKleiderendpunkte.rumpf(request)
        try:
            bericht = Engine2d3dKleideranimexport(job).ausfuehren(
                glb=rumpf.get('glb', True) is not False, blend=rumpf.get('blend', True) is not False,
                bvh=rumpf.get('bvh', True) is not False, bvh_pfad=str(rumpf.get('bvh_pfad') or ''),
                audio=rumpf.get('audio', True) is not False and bool(str(rumpf.get('audio_pfad') or '').strip()),
                audio_pfad=str(rumpf.get('audio_pfad') or ''), name=str(rumpf.get('name') or '')[:120])
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=409)
        except Exception as fehler:  # noqa: BLE001 — sichtbar im Log, die Seite bekommt die Meldung
            logger.exception('2D3D Kleider %s: Export mit Animation gescheitert', job.kennung)
            return JsonResponse({'error': 'Export gescheitert: %s' % fehler}, status=500)
        for teil in ('glb', 'blend'):
            if isinstance(bericht.get(teil), dict) and bericht[teil].get('datei'):
                bericht[teil]['adresse'] = '/api/engine2d3dkleider/%s/datei/ergebnis/%s' % (job.id, bericht[teil]['datei'])
        return JsonResponse(bericht)
