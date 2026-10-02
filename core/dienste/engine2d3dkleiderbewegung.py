# -*- coding: utf-8 -*-
"""Engine2d3dKleiderbewegung — die BVH-Datei auf Genesis 9 rechnen, bevor die Engine den Film rechnet.

Nutzt denselben Retarget-Kern wie die Studio-Vorschau im Browser (`/Charakter/`,
`core.dienste.retargetdaten.Retargetdaten`, Ziel `genesis9`). Das Ergebnis (Knochendrehungen je Bild,
`humanbody_core.skeleton.bewegungsspuren.Bewegungsspuren`) liegt als JSON im Arbeitsordner; die Bühne spielt
es live auf der Figur ab (`Engine2d3dKleideranimation`), und der Film der Engine bekommt es als Eingabe.
Gerechnet wird nur einmal, im Django-Prozess.
"""

import json

__all__ = ['Engine2d3dKleiderbewegung']


class Engine2d3dKleiderbewegung:
    DATEI = 'bewegung.json'

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job

    def rechnen(self, bvh_pfad, aus_ordner):
        """Schreibt `bewegung.json` in `aus_ordner`, gibt `(pfad, Bewegungsspuren)` zurück."""
        from Genesis9.formung import G9formung

        from .retargetdaten import Retargetdaten

        formung = G9formung(self.job.stellung())
        hoehe_cm = float((self.job.optionen.get('figur') or {}).get('hoehe_cm') or 0)
        koerpergroesse = hoehe_cm / 100.0 if hoehe_cm > 0 else Retargetdaten.ERSATZHOEHE
        ergebnis = Retargetdaten(
            bvh_pfad, body_height=koerpergroesse, ziel=Retargetdaten.ZIEL_G9, formung=formung
        ).holen()
        ziel = aus_ordner / self.DATEI
        with open(ziel, 'w', encoding='utf-8') as f:
            json.dump(ergebnis.als_dict(), f)
        return ziel, ergebnis
