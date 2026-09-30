# -*- coding: utf-8 -*-
"""Haarengineiterationenendpunkte — die Runden der Tabelle „Iterationen" löschen.

    POST /api/haarengine/<id>/runden/loeschen/   {runden: [12, 13, …]}
    → {ok, geloescht: [...], vorgemerkt: [...]}

Ohne Lauf werden die Runden sofort gelöscht (`geloescht`). Rechnet gerade ein Lauf, schreibt nur er in
`ergebnis` — die Runden werden vorgemerkt (`vorgemerkt`) und der Lauf löscht sie zu Beginn der nächsten
Runde (`Iterationsloeschung`). Gesperrt ist dabei nichts: Löschen geht auch im laufenden Lauf.
"""

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..dienste.iterationsloeschung import Iterationsloeschung
from ..models import Haarengineauftrag
from .haarengine import Haarengineendpunkte

__all__ = ['Haarengineiterationenendpunkte']


class Haarengineiterationenendpunkte:
    @staticmethod
    @require_POST
    def loeschen(request, job_id):
        job = get_object_or_404(Haarengineauftrag, id=job_id)
        try:
            runden = sorted({int(n) for n in Haarengineendpunkte.rumpf(request).get('runden') or []})
        except TypeError, ValueError:
            return JsonResponse({'error': '„runden“: eine Liste von Rundennummern'}, status=400)
        if not runden:
            return JsonResponse({'error': 'Keine Runde gewählt'}, status=400)
        loeschung = Iterationsloeschung(job)
        loeschung.vormerken(runden)
        if job.laeuft:
            return JsonResponse({'ok': True, 'geloescht': [], 'vorgemerkt': loeschung.vorgemerkt()})
        geloescht = loeschung.abarbeiten()
        job.save(update_fields=['ergebnis', 'updated_at'])
        return JsonResponse({'ok': True, 'geloescht': geloescht, 'vorgemerkt': []})
