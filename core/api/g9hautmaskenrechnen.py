# -*- coding: utf-8 -*-
"""Die Haut-Maske auf der Grafikkarte rechnen (18.11.2026, Edgar: „Hautverdeckung auf GPU, alles auf GPU!“, `core/dienste/hautkarterechnung.py`).

    POST /api/character/genesis9-figur/hautmasken/<fassung>/<schluessel>/rechnen/?stufe=fein    Rumpf: die Eingabe als Feldpaket (gzip)
         → das Ergebnis als Feldpaket (gzip), wie `Hautrechnung.rechnen` im Worker; legt es wie `G9hautmaskenapi` ab, wenn die Stufe dazugehört.

Asynchron, die Rechnung in einem eigenen Faden (`asyncio.to_thread`). Ohne Grafikkarte 503 — der Browser rechnet dann im Worker wie bisher.
"""
import asyncio
import logging

import torch
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..dienste.g9hautmasken import G9hautmasken
from ..dienste.netzvorratwahl import Netzvorratwahl

__all__ = ['G9hautmaskenrechnen']

logger = logging.getLogger('core')


class G9hautmaskenrechnen:
    #: Größte Eingabe (gzip): die Filmstufe mit Kleidung liegt deutlich darunter.
    GROESSTE_MB = 256

    @staticmethod
    @csrf_exempt
    async def rechnen(request, fassung, schluessel):
        if request.method != 'POST':
            return JsonResponse({'fehler': 'nur POST'}, status=405)
        if G9hautmasken.datei(fassung, schluessel) is None:
            return JsonResponse({'fehler': 'Fassung oder Schlüssel ungültig'}, status=400)
        if not torch.cuda.is_available():
            return JsonResponse({'fehler': 'keine Grafikkarte'}, status=503)
        roh = request.body
        if not roh or len(roh) > G9hautmaskenrechnen.GROESSTE_MB * 1024 * 1024:
            return JsonResponse({'fehler': 'Eingabe fehlt oder zu groß'}, status=400)
        from ..dienste.hautkarterechnung import Hautkarterechnung
        try:
            antwort = await asyncio.to_thread(Hautkarterechnung.aus_bytes, roh)
        except (ValueError, KeyError, RuntimeError) as fehler:
            logger.warning('Haut-Maske auf der Karte: %s', fehler)
            return JsonResponse({'fehler': str(fehler)}, status=400)
        stufe = request.GET.get('stufe', '')
        wahl = await asyncio.to_thread(Netzvorratwahl.gewaehlt)
        if stufe in Netzvorratwahl.STUFEN and Netzvorratwahl.behalten(Netzvorratwahl.STUFEN.index(stufe), wahl):
            await asyncio.to_thread(G9hautmasken.ablegen, fassung, schluessel, antwort)
        return HttpResponse(antwort, content_type='application/octet-stream')
