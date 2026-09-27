# -*- coding: utf-8 -*-
"""Meshfiguraugenhoehle — Augenpartie aus dem Eigenmorph von „Mesh to 3D" herausnehmen.

Edgar, 27.09.2026: „vergleiche doch Kopfform, Augenform, ist doch total unterschiedlich!"
Gemessen (Auftrag 2026.09.27.15.52.13, Vorderansicht, Tiefenbild Augapfel gegen Körper): der
sichtbare Augapfel der Figur war 20,4 × 26,5 mm groß (419 mm²), die gemalte Lidspalte des Kopfnetzes
10,1 × 28,5 mm (195 mm²). Ohne Eigenmorph: 12,2 × 24,4 mm (230 mm²).

Ursache: Hunyuan formt das Auge nicht, es legt eine Mulde mit aufgemaltem Auge an. Der Rest je
Käfigpunkt zog die Punkte der Augenhöhle (hinter dem Augapfel, bis 17,6 mm Rest) auf diese Fläche.
Der Augapfel ist starr (`G9folger.starr`) und rückt um das MITTEL seiner Körpernachbarn — hier 3,4 mm
nach vorn —, die Lidhaut blieb stehen: der Augapfel stach auf der doppelten Fläche durch die Lider.

Deshalb werden die Körpernachbarn des Augapfels und die Lider (`G9augenpartie`) im Rest zu Lücken:
`G9restmorph` füllt sie aus der umgebenden Haut. Augapfel und Lider rücken dann mit Brauen und Wangen,
und ihre Form geben die Regler (Lidlandmarken) — nicht die Mulde. Gegengerechnet mit `rest.npz`
desselben Auftrags: sichtbar 12,2 × 24,3 mm (229 mm²), Schnitt auf Augenhöhe max. 6,1 statt 10,1 mm.
"""

import numpy as np

__all__ = ['Meshfiguraugenhoehle']


class Meshfiguraugenhoehle:
    _maske = None

    @classmethod
    def maske(cls):
        """(N,) bool je Käfigpunkt — Körpernachbarn des Augapfels und Lider (`G9augenpartie`)."""
        if cls._maske is None:
            from Genesis9.augenpartie import G9augenpartie

            cls._maske = G9augenpartie.maske()
        return cls._maske

    @classmethod
    def luecke(cls, rest, gewicht):
        """`(rest, gewicht, anzahl)` — die Augenpartie als Lücke (Rest 0, Gewicht 0)."""
        maske = cls.maske()
        if len(maske) != len(gewicht):
            return rest, gewicht, 0
        rest, gewicht = np.array(rest, dtype=float), np.array(gewicht, dtype=float)
        rest[maske] = 0.0
        gewicht[maske] = 0.0
        return rest, gewicht, int(maske.sum())
