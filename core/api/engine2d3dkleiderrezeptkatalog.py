# -*- coding: utf-8 -*-
"""Engine2d3dKleiderrezeptkatalogendpunkt — der Katalog dessen, was ein Rezept benennen darf (05.10.2026).

    GET /api/engine2d3dkleider/<id>/rezeptkatalog/   {auftrag, garderobe, regler, koerper, schnitt, fehler} — Aufbau und Herkunft: `Engine2d3dKleiderrezeptkatalog`

Nur lesen. Gebraucht vom Lauf der Nachbesserung (`Edgar.auftragsklient`), der daraus den Abschnitt „Was es gibt" des Prompts macht.
"""

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from ..dienste.engine2d3dkleiderrezeptkatalog import Engine2d3dKleiderrezeptkatalog
from ..models import Engine2d3dKleiderauftrag

__all__ = ['Engine2d3dKleiderrezeptkatalogendpunkt']


class Engine2d3dKleiderrezeptkatalogendpunkt:
    @staticmethod
    @require_GET
    def lesen(request, job_id):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        return JsonResponse(Engine2d3dKleiderrezeptkatalog(job).daten(), json_dumps_params={'ensure_ascii': False})
