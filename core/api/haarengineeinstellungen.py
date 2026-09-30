# -*- coding: utf-8 -*-
"""Haarengineeinstellungen — die Auftragsseite „Haar Engine" speichert jede Eingabe sofort.

    POST /api/haarengine/<id>/einstellungen/   {optionen: {figur?: {…}, iterationen?: {…}, film?: {…}}}
         → {ok, optionen}   (409 während eines Laufs — der Arbeitsprozess hat seine Optionen schon gelesen)

Eine Seite schickt nur, was sie kennt; `Haarengineoptionen.mischen` legt es Gruppe für Gruppe über den
gespeicherten Stand und prüft das Ergebnis gegen die Kataloge. Wer die Seite verlässt, verliert damit
nichts.
"""

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..dienste.haarenginearbeiter import Haarenginearbeiter
from ..dienste.haarengineoptionen import Haarengineoptionen
from ..models import Haarengineauftrag
from .haarengine import Haarengineendpunkte

__all__ = ['Haarengineeinstellungen']


class Haarengineeinstellungen:
    @staticmethod
    @require_POST
    def speichern(request, job_id):
        job = get_object_or_404(Haarengineauftrag, pk=job_id)
        if job.laeuft and Haarenginearbeiter.lebt(job):
            return JsonResponse({'error': 'Der Auftrag läuft — Änderungen erst nach dem Lauf'}, status=409)
        neu = Haarengineendpunkte.rumpf(request).get('optionen')
        if isinstance(neu, dict):
            job.optionen = Haarengineoptionen.mischen(job.optionen, neu)
            job.save(update_fields=['optionen', 'updated_at'])
        return JsonResponse({'ok': True, 'optionen': Haarengineoptionen.pruefen(job.optionen)})
