# -*- coding: utf-8 -*-
"""Blendermodelliterationenendpunkte — die Runden der Tabelle „Iterationen" löschen (30.09.2026).

    POST /api/blendermodell/<id>/runden/loeschen/   {runden: [12, 13, …]}
    → {ok, geloescht: [...], vorgemerkt: [...]}

Ohne Lauf werden die Runden sofort gelöscht (`geloescht`). Rechnet gerade ein Lauf, schreibt nur er in
`ergebnis` — die Runden werden vorgemerkt (`vorgemerkt`) und der Lauf löscht sie zu Beginn der nächsten Runde
(`Kostuemloeschung`). Gesperrt ist dabei nichts: Edgar (30.09.2026): Löschen soll auch im laufenden Lauf gehen.
"""

from django.views.decorators.http import require_POST

from ..dienste.kostuemloeschung import Kostuemloeschung
from ..models import Blendermodellauftrag
from .blendermodell import Blendermodellendpunkte
from .auftragsfamilie import Auftragsfamilie

__all__ = ['Blendermodelliterationenendpunkte']


class Blendermodelliterationenendpunkte:
    @staticmethod
    @require_POST
    def loeschen(request, job_id):
        return Auftragsfamilie.iterationen_loeschen(Blendermodellauftrag, Blendermodellendpunkte.rumpf, Kostuemloeschung, request, job_id)
