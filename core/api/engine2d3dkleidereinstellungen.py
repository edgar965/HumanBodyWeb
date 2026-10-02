# -*- coding: utf-8 -*-
"""Engine2d3dKleidereinstellungen — die Auftragsseite „Haar Engine" speichert jede Eingabe sofort.

    POST /api/engine2d3dkleider/<id>/einstellungen/   {optionen: {figur?: {…}, iterationen?: {…}, film?: {…}}}
         → {ok, optionen}   (409 während eines Laufs — der Arbeitsprozess hat seine Optionen schon gelesen)

Eine Seite schickt nur, was sie kennt; `Engine2d3dKleideroptionen.mischen` legt es Gruppe für Gruppe über den
gespeicherten Stand und prüft das Ergebnis gegen die Kataloge. Wer die Seite verlässt, verliert damit
nichts.
"""

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..dienste.engine2d3dkleiderarbeiter import Engine2d3dKleiderarbeiter
from ..dienste.engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from ..models import Engine2d3dKleiderauftrag
from .engine2d3dkleider import Engine2d3dKleiderendpunkte

__all__ = ['Engine2d3dKleidereinstellungen']


class Engine2d3dKleidereinstellungen:
    @staticmethod
    @require_POST
    def speichern(request, job_id):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        if job.laeuft and Engine2d3dKleiderarbeiter.lebt(job):
            return JsonResponse({'error': 'Der Auftrag läuft — Änderungen erst nach dem Lauf'}, status=409)
        neu = Engine2d3dKleiderendpunkte.rumpf(request).get('optionen')
        if isinstance(neu, dict):
            job.optionen = Engine2d3dKleideroptionen.mischen(job.optionen, neu)
            job.save(update_fields=['optionen', 'updated_at'])
        return JsonResponse({'ok': True, 'optionen': Engine2d3dKleideroptionen.pruefen(job.optionen)})
