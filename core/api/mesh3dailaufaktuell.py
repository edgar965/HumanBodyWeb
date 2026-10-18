# -*- coding: utf-8 -*-
"""Mesh3dailaufaktuellendpunkt — Stand des Reiters „Lauf Aktuell“ auf /mesh-3D-AI/ (18.10.2026).

GET /api/mesh3dai/lauf-aktuell/   was gerade rechnet: Jobs mit CPU, GPU, Arbeitsspeicher und Fortschritt, GPU-Sperre, Ketten, andere Programme auf der GPU, Rechner gesamt (`Mesh3dailaufaktuell`).
Die Seite fragt alle `takt_s` Sekunden, nur solange der Reiter offen und der Tab sichtbar ist; die Antwort kommt aus dem Hintergrund-Zwischenspeicher (höchstens einen Takt alt).
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.mesh3dailaufaktuell import Mesh3dailaufaktuell

__all__ = ['Mesh3dailaufaktuellendpunkt']


class Mesh3dailaufaktuellendpunkt:
    @staticmethod
    @require_GET
    def stand(request):
        return JsonResponse(Mesh3dailaufaktuell.lesen())
