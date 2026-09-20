# -*- coding: utf-8 -*-
"""Garmentabbruch — der Abbrechen-Knopf beim Bauen.

    POST /api/garmentcode/abbrechen/  Feld `anfrage=<Kennung>`
      -> {'ergebnis': 'beendet' | 'kein_lauf' | 'fremd'}

WARUM (20.09.2026, Edgar: „2D+3D bauen — es soll einen Abbrechen-Button
geben"): Der Browser kann seine Anfrage abbrechen, aber die Simulation
laeuft als eigener Prozess 25 bis 65 s weiter und belegt den Rechner.
`GarmentCode.laufregister.Laufregister` kennt den Prozess zur Kennung
(`Drapierung` meldet ihn an) und beendet ihn. Was danach im Browser
passiert, steht in `scene/garmentcode_abbruch.js`.
"""

import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST

logger = logging.getLogger('core')

__all__ = ['Garmentabbruch']


class Garmentabbruch:
    """Der Endpunkt hinter dem Abbrechen-Knopf."""

    @staticmethod
    @require_POST
    def abbrechen(request):
        """Den Simulationsprozess zur Anfrage-Kennung beenden."""
        from GarmentCode.laufregister import Laufregister

        kennung = request.POST.get('anfrage') or ''
        if not Laufregister.KENNUNG.match(kennung):
            return JsonResponse({'fehler': 'Keine gültige Kennung'}, status=400)
        ergebnis = Laufregister.abbrechen(kennung)
        return JsonResponse({'ergebnis': ergebnis, 'anfrage': kennung})
