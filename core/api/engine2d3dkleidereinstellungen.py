# -*- coding: utf-8 -*-
"""Engine2d3dKleidereinstellungen — die Auftragsseite „2D3D Kleider" speichert jede Eingabe sofort.

    POST /api/engine2d3dkleider/<id>/einstellungen/   {optionen: {figur?: {…}, iterationen?: {…}, film?: {…}}}
         → {ok, optionen}   (409 während eines Laufs — der Arbeitsprozess hat seine Optionen schon gelesen)

Eine Seite schickt nur, was sie kennt; `Engine2d3dKleideroptionen.mischen` legt es Gruppe für Gruppe über den
gespeicherten Stand und prüft das Ergebnis gegen die Kataloge. Wer die Seite verlässt, verliert damit
nichts.
"""

from django.views.decorators.http import require_POST

from ..dienste.engine2d3dkleiderarbeiter import Engine2d3dKleiderarbeiter
from ..dienste.engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from ..models import Engine2d3dKleiderauftrag
from .engine2d3dkleider import Engine2d3dKleiderendpunkte
from .auftragsfamilie import Auftragsfamilie

__all__ = ['Engine2d3dKleidereinstellungen']


class Engine2d3dKleidereinstellungen:
    @staticmethod
    @require_POST
    def speichern(request, job_id):
        return Auftragsfamilie.einstellungen_speichern(Engine2d3dKleiderauftrag, Engine2d3dKleiderarbeiter, Engine2d3dKleiderendpunkte.rumpf, Engine2d3dKleideroptionen, request, job_id)
