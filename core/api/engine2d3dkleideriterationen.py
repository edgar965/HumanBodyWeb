# -*- coding: utf-8 -*-
"""Engine2d3dKleideriterationenendpunkte — die Runden der Tabelle „Iterationen" löschen.

    POST /api/engine2d3dkleider/<id>/runden/loeschen/   {runden: [12, 13, …]}
    → {ok, geloescht: [...], vorgemerkt: [...]}

Ohne Lauf werden die Runden sofort gelöscht (`geloescht`). Rechnet gerade ein Lauf, schreibt nur er in
`ergebnis` — die Runden werden vorgemerkt (`vorgemerkt`) und der Lauf löscht sie zu Beginn der nächsten
Runde (`Iterationsloeschung`). Gesperrt ist dabei nichts: Löschen geht auch im laufenden Lauf.
"""

from django.views.decorators.http import require_POST

from ..dienste.iterationsloeschung import Iterationsloeschung
from ..models import Engine2d3dKleiderauftrag
from .engine2d3dkleider import Engine2d3dKleiderendpunkte
from .auftragsfamilie import Auftragsfamilie

__all__ = ['Engine2d3dKleideriterationenendpunkte']


class Engine2d3dKleideriterationenendpunkte:
    @staticmethod
    @require_POST
    def loeschen(request, job_id):
        return Auftragsfamilie.iterationen_loeschen(Engine2d3dKleiderauftrag, Engine2d3dKleiderendpunkte.rumpf, Iterationsloeschung, request, job_id)
