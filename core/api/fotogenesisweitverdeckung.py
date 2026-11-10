# -*- coding: utf-8 -*-
"""Fotogenesisweitverdeckungendpunkte — „Haut unter weiten Stücken“ unter dem Feld Genesis-Ergebnis der Jobseite von Foto-Genesis (08.11.2026), Lauf und Stand in `Fotogenesisweitverdeckung`.

    GET  /api/fotogenesis/<job>/weitverdeckung/                → Stand {laeuft, zeile, angewandt, befund, sekunden, veraltet, zustand, rechenlauf}
    POST /api/fotogenesis/<job>/weitverdeckung/rechnen/        → Stand (Lauf gestartet)
    POST /api/fotogenesis/<job>/weitverdeckung/zuruecksetzen/  → Stand (Masken des Kostümlaufs zurück, im eigenen Prozess)
"""

import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.fotogenesisjobs import Fotogenesisjobs
from ..dienste.fotogenesisweitverdeckung import Fotogenesisweitverdeckung

logger = logging.getLogger('core')

__all__ = ['Fotogenesisweitverdeckungendpunkte']


class Fotogenesisweitverdeckungendpunkte:
    @staticmethod
    def _schritt(job):
        return Fotogenesisweitverdeckung.fuer(Fotogenesisjobs.job(job))

    @staticmethod
    def _keiner():
        return JsonResponse({'error': 'Kein Kostüm zu diesem Job'}, status=404)

    @staticmethod
    @require_GET
    def stand(request, job):
        s = Fotogenesisweitverdeckungendpunkte._schritt(job)
        return JsonResponse(s.stand()) if s else Fotogenesisweitverdeckungendpunkte._keiner()

    @staticmethod
    def _starten(job, zuruecksetzen):
        s = Fotogenesisweitverdeckungendpunkte._schritt(job)
        if s is None:
            return Fotogenesisweitverdeckungendpunkte._keiner()
        try:
            s.starten(zuruecksetzen=zuruecksetzen)
        except (ValueError, OSError) as fehler:
            logger.warning('Haut unter weiten Stücken: %s nicht gestartet: %s', job, fehler)
            return JsonResponse({'error': str(fehler)}, status=409)
        return JsonResponse(s.stand())

    @staticmethod
    @require_POST
    def rechnen(request, job):
        return Fotogenesisweitverdeckungendpunkte._starten(job, False)

    @staticmethod
    @require_POST
    def zuruecksetzen(request, job):
        return Fotogenesisweitverdeckungendpunkte._starten(job, True)
