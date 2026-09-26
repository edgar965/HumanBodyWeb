# -*- coding: utf-8 -*-
"""GC-Stücke zwischen GarmentCode-Reiter und Genesis-Garderobe (`G9gceigenes`).

    GET  /api/garmentcode/genesis/<stueck>/   Herkunft eines gebackenen GC-Stücks
                                              {vorlage, quelle, werte, farbe, stoff, name}
    POST /api/garmentcode/genesis/speichern/  vorlage, regler (JSON), bau (JSON), titel,
                                              material (JSON), quelle
                                              → {stueck, kennung, name, sekunden, stoff}

Das Speichern drapiert neu auf der Genesis-Figur des Reiters (`regler_figur`, sonst der
Grundfigur; ~25–60 s, wie „Bauen 2D + 3D"),
schreibt das Stück in die eigene Bibliothek und lässt die Garderobe neu lesen.
Beide Views `@staticmethod` — `require_*` liest `args[0].method` (`garmentcode.py`).
"""
import json
import logging
import re
import time

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger(__name__)


class Gcgenesisapi:
    u"""Herkunft lesen, Stück aus dem Reiter speichern."""

    STUECK = re.compile(r'^gc_[a-z0-9_]{1,120}$')

    @staticmethod
    @require_GET
    def herkunft(request, stueck):
        from Genesis9.gceigenes import G9gceigenes
        if not Gcgenesisapi.STUECK.match(stueck):
            return JsonResponse({'fehler': 'Kein GC-Stück'}, status=400)
        daten = G9gceigenes.herkunft(stueck)
        if not daten:
            return JsonResponse({'fehler': 'Herkunft unbekannt'}, status=404)
        return JsonResponse(daten)

    @staticmethod
    def _json(roh, vorgabe):
        try:
            wert = json.loads(roh or '')
        except ValueError:
            return vorgabe
        return wert if isinstance(wert, type(vorgabe)) else vorgabe

    @staticmethod
    @require_POST
    def speichern(request):
        from GarmentCode.drapierung import DrapierFehler
        from GarmentCode.entwurf import EntwurfFehler
        from GarmentCode.katalog import Katalog
        from Genesis9.gceigenes import G9gceigenes
        vorlage = request.POST.get('vorlage') or ''
        if not Katalog.kennt(vorlage):
            return JsonResponse({'fehler': 'Unbekannte Vorlage %r' % vorlage}, status=400)
        werte = Gcgenesisapi._json(request.POST.get('regler'), {})
        for pfad, wert in Gcgenesisapi._json(request.POST.get('bau'), {}).items():
            # Die Bauwerte des Reiters als Pseudo-Pfade, wie die Vorbilder sie tragen.
            if pfad == 'anliegen_mm' and wert:
                werte['bau.anliegen_mm'] = float(wert)
        material = Gcgenesisapi._json(request.POST.get('material'), {})
        titel = (request.POST.get('titel') or '').strip() or vorlage
        start = time.time()
        try:
            # Die Figur des Reiters (25.09.2026, `G9gcfigurbau`) — leer = Grundfigur.
            bilanz = G9gceigenes.bauen(vorlage, werte, titel, material,
                                       request.POST.get('quelle') or 'reiter',
                                       Gcgenesisapi._json(request.POST.get('regler_figur'), {}))
        except (DrapierFehler, EntwurfFehler, ValueError) as fehler:
            logger.warning('GC → Genesis gescheitert: %s', fehler)
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except Exception as fehler:                      # noqa: BLE001
            logger.exception('GC → Genesis: unerwarteter Fehler')
            return JsonResponse({'fehler': '%s: %s' % (type(fehler).__name__, fehler)}, status=500)
        return JsonResponse({'stueck': bilanz['stueck'], 'kennung': bilanz['kennung'],
                             'name': bilanz['name'], 'stoff': bilanz.get('stoff') or {},
                             'sekunden': round(time.time() - start, 1),
                             'haut_median_mm': bilanz['haut_median_mm'],
                             'figurbau': bilanz.get('figurbau'),
                             'angepasst': bilanz.get('angepasst') or {}})
