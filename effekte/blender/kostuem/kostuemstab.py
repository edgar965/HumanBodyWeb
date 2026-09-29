# -*- coding: utf-8 -*-
"""Kostuemstab — der Wanderstab in der RECHTEN Hand der Figur, vom Boden bis über die Schulter, oben ein
Knauf.

Rechts heißt: rechts der Figur, nicht des Bildes. Blickt sie nach −y, liegt ihre rechte Seite bei −x
(Blickrichtung × oben); blickt sie nach +y, bei +x — die Seite ist also das Vorzeichen der Blickrichtung
(`seite = vorn`). In der Vorlage steht der Stab in der Vorderansicht links im Bild: das ist die rechte Hand
der Figur.
"""

import numpy as np

from effekte.blender.kostuem.rohr import Rohr

__all__ = ['Kostuemstab']


class Kostuemstab:
    RINGE = 9

    def __init__(self, masse, p, vorn_grad):
        self.m = masse
        self.p = p
        self.vorn = 1 if vorn_grad == 90 else -1

    def farbe(self):
        return tuple(float(self.p['farbe.stab.%s' % k]) for k in 'rgb')

    def bauen(self):
        p = self.p
        if p['stab.an'] < 0.5:
            return []
        seite = self.vorn
        _, hand, _ = self.m.arm(seite)
        x = float(hand[0]) + seite * p['stab.abstand']
        y = float(hand[1]) + self.vorn * 0.03
        oben = self.m.boden + p['stab.hoehe'] * self.m.hoehe
        r = p['stab.dicke']
        stab = Rohr('Stab', self.farbe())
        for z in np.linspace(self.m.boden, oben, self.RINGE):
            stab.ring_waagerecht(x, y, r, r, float(z), welle=0.08, wellen=5)
        teile = [stab.bauen(dicke=0.0, glaetten=1)]
        knauf = p['stab.knauf']
        if knauf > 0.005:
            kugel = Rohr('Stabknauf', self.farbe())
            for w in np.linspace(-0.95, 0.95, 9):
                rk = knauf * float(np.sqrt(1 - w * w))
                kugel.ring_waagerecht(x, y, rk, rk, oben + knauf * (1 + float(w)))
            teile.append(kugel.bauen(dicke=0.0, glaetten=1, deckel_oben=True))
        return teile
