# -*- coding: utf-8 -*-
"""Ai2d3dhautangleichendpunkte — „Haut angleichen“ auf der Testseite von 2d-3d-AI (05.11.2026), Ablage und Lauf in `Ai2d3dhautangleich`.

    GET  /api/2d3dai/<job>/hautangleich/                  → Stand {bereit, laeuft, kopf, bilder, regler, felder, netz, original, fehler}
    POST /api/2d3dai/<job>/hautangleich/vorbereiten/      → Stand (Original sichern, Tonfelder rechnen lassen)
    GET  /api/2d3dai/<job>/hautangleich/daten/<name>/     → felder.bin | netz.bin
    GET  /api/2d3dai/<job>/hautangleich/original/<kachel>/→ Kachel, von der die Regler ausgehen
    GET  /api/2d3dai/<job>/hautangleich/zeichnung/<kachel>/→ dieselbe Kachel mit der Zeichnung gesehener Haut (`Hautzeichnung`)
    POST /api/2d3dai/<job>/hautangleich/speichern/        Formular: k1001 … (JPEG), regler (JSON) → Stand
    POST /api/2d3dai/<job>/hautangleich/zuruecksetzen/    → Stand

Dieselben Endpunkte für die Testseite unter /api/mesh3dai/test/<kennung>/hautangleich/ (06.11.2026, Edgar: „mach den besten code den wir haben in beiden pipelines“): `core/urls_mesh3dai.py` setzt `aus_test`.
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
    def _angleich(job, aus_test):
        return Ai2d3dhautangleich.fuer_test(job) if aus_test else Ai2d3dhautangleich.fuer(Ai2d3djobs.job(job))

    @staticmethod
    def _adresse(job, aus_test):
        return ('/api/mesh3dai/test/%s/hautangleich/' if aus_test else '/api/2d3dai/%s/hautangleich/') % job

    @staticmethod
    def _keine():
        return JsonResponse({'error': 'Noch keine fertige Haut'}, status=404)

    @staticmethod
    @require_GET
    def stand(request, job, aus_test=False):
        a = Ai2d3dhautangleichendpunkte._angleich(job, aus_test)
        return JsonResponse(a.stand(Ai2d3dhautangleichendpunkte._adresse(job, aus_test))) if a else Ai2d3dhautangleichendpunkte._keine()

    @staticmethod
    @require_POST
    def vorbereiten(request, job, aus_test=False):
        a = Ai2d3dhautangleichendpunkte._angleich(job, aus_test)
        if a is None:
            return Ai2d3dhautangleichendpunkte._keine()
        a.vorbereiten()
        return JsonResponse(a.stand(Ai2d3dhautangleichendpunkte._adresse(job, aus_test)))

    @staticmethod
    @require_GET
    def daten(request, job, name, aus_test=False):
        a = Ai2d3dhautangleichendpunkte._angleich(job, aus_test)
        pfad = a.datei(name) if a else None
        return Auftragsdatei.antwort(request, pfad) if pfad else JsonResponse({'error': 'Noch nicht vorbereitet'}, status=404)

    @staticmethod
    @require_GET
    def original(request, job, kachel, aus_test=False):
        a = Ai2d3dhautangleichendpunkte._angleich(job, aus_test)
        pfad = a.originalbild(kachel) if a else None
        return Auftragsdatei.antwort(request, pfad) if pfad else JsonResponse({'error': 'Kein Original'}, status=404)

    @staticmethod
    @require_GET
    def zeichnung(request, job, kachel, aus_test=False):
        a = Ai2d3dhautangleichendpunkte._angleich(job, aus_test)
        pfad = a.zeichnungsbild(kachel) if a else None
        return Auftragsdatei.antwort(request, pfad) if pfad else JsonResponse({'error': 'Keine Zeichnung'}, status=404)

    @staticmethod
    @require_POST
    def speichern(request, job, aus_test=False):
        a = Ai2d3dhautangleichendpunkte._angleich(job, aus_test)
        if a is None:
            return Ai2d3dhautangleichendpunkte._keine()
        try:
            regler = json.loads(request.POST.get('regler') or '{}')
            dateien = {name[1:]: d.read() for name, d in request.FILES.items() if name.startswith('k')}
            a.speichern(dateien, regler)
        except (ValueError, KeyError, TypeError, OSError) as fehler:
            logger.warning('Haut angleichen: %s nicht gespeichert: %s', job, fehler)
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse(a.stand(Ai2d3dhautangleichendpunkte._adresse(job, aus_test)))

    @staticmethod
    @require_POST
    def zuruecksetzen(request, job, aus_test=False):
        a = Ai2d3dhautangleichendpunkte._angleich(job, aus_test)
        if a is None:
            return Ai2d3dhautangleichendpunkte._keine()
        try:
            a.zuruecksetzen()
        except (ValueError, OSError) as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse(a.stand(Ai2d3dhautangleichendpunkte._adresse(job, aus_test)))
