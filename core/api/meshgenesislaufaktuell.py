# -*- coding: utf-8 -*-
"""Meshgenesislaufaktuellendpunkt — Stand des Reiters „Lauf Aktuell“ auf /mesh-genesis/ (18.10.2026).

GET /api/meshgenesis/lauf-aktuell/   was gerade rechnet: Jobs mit CPU, GPU, Arbeitsspeicher und Fortschritt, GPU-Sperre, Ketten, andere Programme auf der GPU, Rechner gesamt (`Meshgenesislaufaktuell`).
Die Seite fragt alle `takt_s` Sekunden, nur solange der Reiter offen und der Tab sichtbar ist; die Antwort kommt aus dem Hintergrund-Zwischenspeicher (höchstens einen Takt alt).
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.meshgenesislaufaktuell import Meshgenesislaufaktuell

__all__ = ['Meshgenesislaufaktuellendpunkt']


class Meshgenesislaufaktuellendpunkt:
    @staticmethod
    @require_GET
    def stand(request):
        return JsonResponse(Meshgenesislaufaktuell.lesen())
