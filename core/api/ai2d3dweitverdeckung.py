# -*- coding: utf-8 -*-
"""Ai2d3dweitverdeckungendpunkte — „Haut unter weiten Stücken“ unter dem Feld Genesis-Ergebnis der Jobseite von 2d-3d-AI (08.11.2026), Lauf und Stand in `Ai2d3dweitverdeckung`.

    GET  /api/2d3dai/<job>/weitverdeckung/                → Stand {laeuft, zeile, angewandt, befund, sekunden, veraltet, zustand, rechenlauf}
    POST /api/2d3dai/<job>/weitverdeckung/rechnen/        → Stand (Lauf gestartet)
    POST /api/2d3dai/<job>/weitverdeckung/zuruecksetzen/  → Stand (Masken des Kostümlaufs zurück, im eigenen Prozess)
"""

import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.ai2d3djobs import Ai2d3djobs
from ..dienste.ai2d3dweitverdeckung import Ai2d3dweitverdeckung

logger = logging.getLogger('core')

__all__ = ['Ai2d3dweitverdeckungendpunkte']


class Ai2d3dweitverdeckungendpunkte:
    @staticmethod
    def _schritt(job):
        return Ai2d3dweitverdeckung.fuer(Ai2d3djobs.job(job))

    @staticmethod
    def _keiner():
        return JsonResponse({'error': 'Kein Kostüm zu diesem Job'}, status=404)

    @staticmethod
    @require_GET
    def stand(request, job):
        s = Ai2d3dweitverdeckungendpunkte._schritt(job)
        return JsonResponse(s.stand()) if s else Ai2d3dweitverdeckungendpunkte._keiner()

    @staticmethod
    def _starten(job, zuruecksetzen):
        s = Ai2d3dweitverdeckungendpunkte._schritt(job)
        if s is None:
            return Ai2d3dweitverdeckungendpunkte._keiner()
        try:
            s.starten(zuruecksetzen=zuruecksetzen)
        except (ValueError, OSError) as fehler:
            logger.warning('Haut unter weiten Stücken: %s nicht gestartet: %s', job, fehler)
            return JsonResponse({'error': str(fehler)}, status=409)
        return JsonResponse(s.stand())

    @staticmethod
    @require_POST
    def rechnen(request, job):
        return Ai2d3dweitverdeckungendpunkte._starten(job, False)

    @staticmethod
    @require_POST
    def zuruecksetzen(request, job):
        return Ai2d3dweitverdeckungendpunkte._starten(job, True)
