# -*- coding: utf-8 -*-
"""Blendermodelleinstellungen — die Auftragsseite „BlenderModel" speichert jede Eingabe sofort (29.09.2026).

Wie bei „Mesh to 3D" (Edgar, 29.09.2026: „bei eingabe in irgend ein feld soll das automatisch gespeichert
werden"): Wer die Seite verlässt, verliert sonst, was er eingestellt hat, weil die Optionen erst mit „Neu
berechnen" an den Server gingen.

    POST /api/blendermodell/<id>/einstellungen/   {optionen: {figur?: {…}, kostuem?: {…}, blender?: {…}}}
         → {ok, optionen}   (409 während eines Laufs — der Arbeitsprozess hat seine Optionen schon gelesen)

Eine Seite schickt nur, was sie kennt; `Blendermodelloptionen.mischen` legt es Gruppe für Gruppe über den
gespeicherten Stand und prüft das Ergebnis gegen die Kataloge.
"""

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..dienste.blendermodellarbeiter import Blendermodellarbeiter
from ..dienste.blendermodelloptionen import Blendermodelloptionen
from ..models import Blendermodellauftrag
from .blendermodell import Blendermodellendpunkte

__all__ = ['Blendermodelleinstellungen']


class Blendermodelleinstellungen:
    @staticmethod
    @require_POST
    def speichern(request, job_id):
        job = get_object_or_404(Blendermodellauftrag, pk=job_id)
        if job.laeuft and Blendermodellarbeiter.lebt(job):
            return JsonResponse({'error': 'Der Auftrag läuft — Änderungen erst nach dem Lauf'}, status=409)
        neu = Blendermodellendpunkte.rumpf(request).get('optionen')
        if isinstance(neu, dict):
            job.optionen = Blendermodelloptionen.mischen(job.optionen, neu)
            job.save(update_fields=['optionen', 'updated_at'])
        return JsonResponse({'ok': True, 'optionen': Blendermodelloptionen.pruefen(job.optionen)})
