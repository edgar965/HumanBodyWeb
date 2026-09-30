# -*- coding: utf-8 -*-
"""Blendermodelliterationenendpunkte — die Runden der Tabelle „Iterationen" löschen (30.09.2026).

    POST /api/blendermodell/<id>/runden/loeschen/   {runden: [12, 13, …]}
    → {ok, geloescht: [...], vorgemerkt: [...]}

Ohne Lauf werden die Runden sofort gelöscht (`geloescht`). Rechnet gerade ein Lauf, schreibt nur er in
`ergebnis` — die Runden werden vorgemerkt (`vorgemerkt`) und der Lauf löscht sie zu Beginn der nächsten Runde
(`Kostuemloeschung`). Gesperrt ist dabei nichts: Edgar (30.09.2026): Löschen soll auch im laufenden Lauf gehen.
"""

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..dienste.kostuemloeschung import Kostuemloeschung
from ..models import Blendermodellauftrag
from .blendermodell import Blendermodellendpunkte

__all__ = ['Blendermodelliterationenendpunkte']


class Blendermodelliterationenendpunkte:
    @staticmethod
    @require_POST
    def loeschen(request, job_id):
        job = get_object_or_404(Blendermodellauftrag, id=job_id)
        try:
            runden = sorted({int(n) for n in Blendermodellendpunkte.rumpf(request).get('runden') or []})
        except (TypeError, ValueError):
            return JsonResponse({'error': '„runden“: eine Liste von Rundennummern'}, status=400)
        if not runden:
            return JsonResponse({'error': 'Keine Runde gewählt'}, status=400)
        loeschung = Kostuemloeschung(job)
        loeschung.vormerken(runden)
        if job.laeuft:
            return JsonResponse({'ok': True, 'geloescht': [], 'vorgemerkt': loeschung.vorgemerkt()})
        geloescht = loeschung.abarbeiten()
        job.save(update_fields=['ergebnis', 'updated_at'])
        return JsonResponse({'ok': True, 'geloescht': geloescht, 'vorgemerkt': []})
