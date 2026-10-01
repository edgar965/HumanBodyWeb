# -*- coding: utf-8 -*-
"""Haarengineanimexportendpunkte — das Modell der besten Runde mit der Bewegung als GLB und Blender-Datei (01.10.2026).

    POST /api/haarengine/<id>/animexport/   {blend?: true}
        → {kanaele, fehlend, bilder, sekunden, runde, glb: {datei, bytes, adresse},
           blend: {datei, bytes, adresse} | {fehler}}

Rechnet im Anfrageprozess (`Haarengineanimexport`: umpacken in Sekundenbruchteilen, Blender ~10 s). Während der Auftrag
rechnet: 409 — die Runden-GLB und die Bewegung könnten gerade neu geschrieben werden.
"""

import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..dienste.haarengineanimexport import Haarengineanimexport
from ..dienste.haarenginearbeiter import Haarenginearbeiter
from ..models import Haarengineauftrag
from .haarengine import Haarengineendpunkte

logger = logging.getLogger('core')

__all__ = ['Haarengineanimexportendpunkte']


class Haarengineanimexportendpunkte:
    @staticmethod
    @require_POST
    def exportieren(request, job_id):
        job = get_object_or_404(Haarengineauftrag, pk=job_id)
        if job.laeuft and Haarenginearbeiter.lebt(job):
            return JsonResponse({'error': 'Auftrag läuft — exportieren, wenn er fertig ist'}, status=409)
        rumpf = Haarengineendpunkte.rumpf(request)
        try:
            bericht = Haarengineanimexport(job).ausfuehren(blend=rumpf.get('blend', True) is not False)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=409)
        except Exception as fehler:  # noqa: BLE001 — sichtbar im Log, die Seite bekommt die Meldung
            logger.exception('2D3D Kleider %s: Export mit Animation gescheitert', job.kennung)
            return JsonResponse({'error': 'Export gescheitert: %s' % fehler}, status=500)
        for teil in ('glb', 'blend'):
            if isinstance(bericht.get(teil), dict) and bericht[teil].get('datei'):
                bericht[teil]['adresse'] = '/api/haarengine/%s/datei/ergebnis/%s' % (job.id, bericht[teil]['datei'])
        return JsonResponse(bericht)
