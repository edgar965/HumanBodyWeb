# -*- coding: utf-8 -*-
"""Bildmodellgvhmrendpunkte — das GVHMR-Netz eines Bildes für die 3D-Ansicht.

GET /api/bildmodell/<id>/gvhmr3d/<datei>/   `{ok, datei, anzahl, punkte (base64 float32
                                            N×3, Meter, y oben), dreiecke (base64 uint32),
                                            hoehe_cm, betas, frames, stand}`
GET /api/bildmodell/<id>/flame3d/<datei>/   dasselbe für den FLAME-Kopf eines Kopfbilds
                                            (`Bildmodellflame`, Knopf „Kopf (FLAME)", 20.09.2026)
GET /api/bildmodell/<id>/kopf3d/            dasselbe für das Ergebnis der Kopf-Pipeline
                                            (`Bildmodellkopf`, Knopf „Kopf berechnen", 22.09.2026 —
                                            job-weit, nicht an ein Bild gebunden)

Gerechnet wird nicht hier: der Knopf „SMPL (GVHMR)" je Kachel startet den
Arbeitsprozess mit `schritte: ['gvhmr'], bild: <datei>` über `starten/`
(`Bildmodellstart`), weil ein Lauf 30–60 s dauert und der Autoreload des
Servers ihn nicht mitreißen soll. Ohne Ergebnis: 404 mit dem Grund.
"""

import logging

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from ..daten.bildmodellablage import Bildmodellablage
from ..dienste.bildmodellflame import Bildmodellflame
from ..dienste.bildmodellgvhmr import Bildmodellgvhmr
from ..dienste.bildmodellkopf import Bildmodellkopf
from ..models import Bildmodellauftrag

logger = logging.getLogger('core')

__all__ = ['Bildmodellgvhmrendpunkte']


class Bildmodellgvhmrendpunkte:
    @staticmethod
    @require_GET
    def netz3d(request, job_id, datei):
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        eintrag = job.bild(datei)
        if eintrag is None:
            raise Http404('Kein Bild %s' % datei)
        try:
            return JsonResponse(Bildmodellgvhmr(job, Bildmodellablage(job.kennung)).netz3d(eintrag))
        except FileNotFoundError as fehler:
            return JsonResponse({'error': str(fehler)}, status=404)
        except (OSError, ValueError) as fehler:
            logger.warning('Bildmodell %s: GVHMR-Netz %s nicht lesbar: %s', job.kennung, datei, fehler)
            return JsonResponse({'error': 'GVHMR-Netz nicht lesbar: %s' % fehler}, status=500)

    @staticmethod
    @require_GET
    def flame3d(request, job_id, datei):
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        eintrag = job.bild(datei)
        if eintrag is None:
            raise Http404('Kein Bild %s' % datei)
        try:
            return JsonResponse(Bildmodellflame(job, Bildmodellablage(job.kennung)).netz3d(eintrag))
        except FileNotFoundError as fehler:
            return JsonResponse({'error': str(fehler)}, status=404)
        except (OSError, ValueError) as fehler:
            logger.warning('Bildmodell %s: FLAME-Netz %s nicht lesbar: %s', job.kennung, datei, fehler)
            return JsonResponse({'error': 'FLAME-Netz nicht lesbar: %s' % fehler}, status=500)

    @staticmethod
    @require_GET
    def kopf3d(request, job_id):
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        try:
            dienst = Bildmodellkopf(job, Bildmodellablage(job.kennung), job.optionen or {})
            return JsonResponse(dienst.netz3d())
        except FileNotFoundError as fehler:
            return JsonResponse({'error': str(fehler)}, status=404)
        except (OSError, ValueError) as fehler:
            logger.warning('Bildmodell %s: Kopf-Netz nicht lesbar: %s', job.kennung, fehler)
            return JsonResponse({'error': 'Kopf-Netz nicht lesbar: %s' % fehler}, status=500)
