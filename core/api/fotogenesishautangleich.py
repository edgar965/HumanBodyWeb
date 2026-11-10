# -*- coding: utf-8 -*-
"""Fotogenesishautangleichendpunkte — „Haut angleichen“ auf der Testseite von Foto-Genesis (05.11.2026), Ablage und Lauf in `Fotogenesishautangleich`.

    GET  /api/fotogenesis/<job>/hautangleich/                  → Stand {bereit, laeuft, kopf, bilder, regler, felder, netz, original, fehler}
    POST /api/fotogenesis/<job>/hautangleich/vorbereiten/      → Stand (Original sichern, Tonfelder rechnen lassen)
    GET  /api/fotogenesis/<job>/hautangleich/daten/<name>/     → felder.bin | netz.bin
    GET  /api/fotogenesis/<job>/hautangleich/original/<kachel>/→ Kachel, von der die Regler ausgehen
    GET  /api/fotogenesis/<job>/hautangleich/zeichnung/<kachel>/→ dieselbe Kachel mit der Zeichnung gesehener Haut (`Hautzeichnung`)
    POST /api/fotogenesis/<job>/hautangleich/speichern/        Formular: k1001 … (JPEG), regler (JSON) → Stand
    POST /api/fotogenesis/<job>/hautangleich/zuruecksetzen/    → Stand

Dieselben Endpunkte für die Testseite unter /api/meshgenesis/test/<kennung>/hautangleich/ (06.11.2026, Edgar: „mach den besten code den wir haben in beiden pipelines“): `core/urls_meshgenesis.py` setzt `aus_test`.
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.fotogenesishautangleich import Fotogenesishautangleich
from ..dienste.fotogenesisjobs import Fotogenesisjobs
from ..dienste.auftragsdatei import Auftragsdatei

logger = logging.getLogger('core')

__all__ = ['Fotogenesishautangleichendpunkte']


class Fotogenesishautangleichendpunkte:
    @staticmethod
    def _angleich(job, aus_test):
        return Fotogenesishautangleich.fuer_test(job) if aus_test else Fotogenesishautangleich.fuer(Fotogenesisjobs.job(job))

    @staticmethod
    def _adresse(job, aus_test):
        return ('/api/meshgenesis/test/%s/hautangleich/' if aus_test else '/api/fotogenesis/%s/hautangleich/') % job

    @staticmethod
    def _keine():
        return JsonResponse({'error': 'Noch keine fertige Haut'}, status=404)

    @staticmethod
    @require_GET
    def stand(request, job, aus_test=False):
        a = Fotogenesishautangleichendpunkte._angleich(job, aus_test)
        return JsonResponse(a.stand(Fotogenesishautangleichendpunkte._adresse(job, aus_test))) if a else Fotogenesishautangleichendpunkte._keine()

    @staticmethod
    @require_POST
    def vorbereiten(request, job, aus_test=False):
        a = Fotogenesishautangleichendpunkte._angleich(job, aus_test)
        if a is None:
            return Fotogenesishautangleichendpunkte._keine()
        a.vorbereiten()
        return JsonResponse(a.stand(Fotogenesishautangleichendpunkte._adresse(job, aus_test)))

    @staticmethod
    @require_GET
    def daten(request, job, name, aus_test=False):
        a = Fotogenesishautangleichendpunkte._angleich(job, aus_test)
        pfad = a.datei(name) if a else None
        return Auftragsdatei.antwort(request, pfad) if pfad else JsonResponse({'error': 'Noch nicht vorbereitet'}, status=404)

    @staticmethod
    @require_GET
    def original(request, job, kachel, aus_test=False):
        a = Fotogenesishautangleichendpunkte._angleich(job, aus_test)
        pfad = a.originalbild(kachel) if a else None
        return Auftragsdatei.antwort(request, pfad) if pfad else JsonResponse({'error': 'Kein Original'}, status=404)

    @staticmethod
    @require_GET
    def zeichnung(request, job, kachel, aus_test=False):
        a = Fotogenesishautangleichendpunkte._angleich(job, aus_test)
        pfad = a.zeichnungsbild(kachel) if a else None
        return Auftragsdatei.antwort(request, pfad) if pfad else JsonResponse({'error': 'Keine Zeichnung'}, status=404)

    @staticmethod
    @require_POST
    def speichern(request, job, aus_test=False):
        a = Fotogenesishautangleichendpunkte._angleich(job, aus_test)
        if a is None:
            return Fotogenesishautangleichendpunkte._keine()
        try:
            regler = json.loads(request.POST.get('regler') or '{}')
            dateien = {name[1:]: d.read() for name, d in request.FILES.items() if name.startswith('k')}
            a.speichern(dateien, regler)
        except (ValueError, KeyError, TypeError, OSError) as fehler:
            logger.warning('Haut angleichen: %s nicht gespeichert: %s', job, fehler)
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse(a.stand(Fotogenesishautangleichendpunkte._adresse(job, aus_test)))

    @staticmethod
    @require_POST
    def zuruecksetzen(request, job, aus_test=False):
        a = Fotogenesishautangleichendpunkte._angleich(job, aus_test)
        if a is None:
            return Fotogenesishautangleichendpunkte._keine()
        try:
            a.zuruecksetzen()
        except (ValueError, OSError) as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse(a.stand(Fotogenesishautangleichendpunkte._adresse(job, aus_test)))
