# -*- coding: utf-8 -*-
"""Ai2d3dhautangleichendpunkte — „Haut angleichen“ auf der Testseite von 2d-3d-AI (05.11.2026), Ablage und Lauf in `Ai2d3dhautangleich`.

    GET  /api/2d3dai/<job>/hautangleich/                  → Stand {bereit, laeuft, kopf, bilder, regler, felder, netz, original, fehler}
    POST /api/2d3dai/<job>/hautangleich/vorbereiten/      → Stand (Original sichern, Tonfelder rechnen lassen)
    GET  /api/2d3dai/<job>/hautangleich/daten/<name>/     → felder.bin | netz.bin
    GET  /api/2d3dai/<job>/hautangleich/original/<kachel>/→ Kachel, von der die Regler ausgehen
    GET  /api/2d3dai/<job>/hautangleich/zeichnung/<kachel>/→ dieselbe Kachel mit der Zeichnung gesehener Haut (`Hautzeichnung`)
    POST /api/2d3dai/<job>/hautangleich/speichern/        Formular: k1001 … (JPEG), regler (JSON) → Stand
    POST /api/2d3dai/<job>/hautangleich/zuruecksetzen/    → Stand
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.ai2d3dhautangleich import Ai2d3dhautangleich
from ..dienste.ai2d3djobs import Ai2d3djobs
from ..dienste.auftragsdatei import Auftragsdatei

logger = logging.getLogger('core')

__all__ = ['Ai2d3dhautangleichendpunkte']


class Ai2d3dhautangleichendpunkte:
    @staticmethod
    def _angleich(job):
        return Ai2d3dhautangleich.fuer(Ai2d3djobs.job(job))

    @staticmethod
    def _keine():
        return JsonResponse({'error': 'Dieser Job hat noch keine fertige Haut'}, status=404)

    @staticmethod
    @require_GET
    def stand(request, job):
        a = Ai2d3dhautangleichendpunkte._angleich(job)
        return JsonResponse(a.stand(job)) if a else Ai2d3dhautangleichendpunkte._keine()

    @staticmethod
    @require_POST
    def vorbereiten(request, job):
        a = Ai2d3dhautangleichendpunkte._angleich(job)
        if a is None:
            return Ai2d3dhautangleichendpunkte._keine()
        a.vorbereiten()
        return JsonResponse(a.stand(job))

    @staticmethod
    @require_GET
    def daten(request, job, name):
        a = Ai2d3dhautangleichendpunkte._angleich(job)
        pfad = a.datei(name) if a else None
        return Auftragsdatei.antwort(request, pfad) if pfad else JsonResponse({'error': 'Noch nicht vorbereitet'}, status=404)

    @staticmethod
    @require_GET
    def original(request, job, kachel):
        a = Ai2d3dhautangleichendpunkte._angleich(job)
        pfad = a.originalbild(kachel) if a else None
        return Auftragsdatei.antwort(request, pfad) if pfad else JsonResponse({'error': 'Kein Original'}, status=404)

    @staticmethod
    @require_GET
    def zeichnung(request, job, kachel):
        a = Ai2d3dhautangleichendpunkte._angleich(job)
        pfad = a.zeichnungsbild(kachel) if a else None
        return Auftragsdatei.antwort(request, pfad) if pfad else JsonResponse({'error': 'Keine Zeichnung'}, status=404)

    @staticmethod
    @require_POST
    def speichern(request, job):
        a = Ai2d3dhautangleichendpunkte._angleich(job)
        if a is None:
            return Ai2d3dhautangleichendpunkte._keine()
        try:
            regler = json.loads(request.POST.get('regler') or '{}')
            dateien = {name[1:]: d.read() for name, d in request.FILES.items() if name.startswith('k')}
            a.speichern(dateien, regler)
        except (ValueError, KeyError, TypeError, OSError) as fehler:
            logger.warning('Haut angleichen: %s nicht gespeichert: %s', job, fehler)
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse(a.stand(job))

    @staticmethod
    @require_POST
    def zuruecksetzen(request, job):
        a = Ai2d3dhautangleichendpunkte._angleich(job)
        if a is None:
            return Ai2d3dhautangleichendpunkte._keine()
        try:
            a.zuruecksetzen()
        except (ValueError, OSError) as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse(a.stand(job))
