# -*- coding: utf-8 -*-
"""Engine2d3dKleiderbewegung — die BVH-Datei auf Genesis 9 rechnen, bevor die Engine den Film rechnet.

Nutzt denselben Retarget-Kern wie die Studio-Vorschau im Browser (`/Charakter/`,
`core.dienste.retargetdaten.Retargetdaten`, Ziel `genesis9`). Das Ergebnis (Knochendrehungen je Bild,
`humanbody_core.skeleton.bewegungsspuren.Bewegungsspuren`) liegt als JSON im Arbeitsordner; die Bühne spielt
es live auf der Figur ab (`Engine2d3dKleideranimation`), und der Film der Engine bekommt es als Eingabe.
Gerechnet wird nur einmal, im Django-Prozess.
"""

from .blendermodellbewegung import Blendermodellbewegung

__all__ = ['Engine2d3dKleiderbewegung']


class Engine2d3dKleiderbewegung:
    DATEI = 'bewegung.json'

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job

    rechnen = Blendermodellbewegung.rechnen          # dieselbe Rechnung wie `Blendermodellbewegung.rechnen` (bis 08.11.2026 eine Kopie hier)
