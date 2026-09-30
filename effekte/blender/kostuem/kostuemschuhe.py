# -*- coding: utf-8 -*-
"""Kostuemschuhe — zwei Stiefelschuhe über den nackten Füßen der Grundfigur.

Bis Version 1 des Kostümmodells standen die Füße nackt unter dem Saum, der Kreislauf zog den Mantel deshalb bis zum
Boden (Saum 0,02 der Körperhöhe — an der Grenze). Die Vorlage trägt braune Schuhe und einen Saum gut eine Handbreit
über dem Boden. Jeder Schuh ist ein Rohr aus elliptischen Querschnitten längs des Fußes (Ferse → Spitze), gemessen
am Fuß der Grundfigur (`Koerpermasse.fuss`), mal `schuhe.groesse`.
"""

from effekte.blender.kostuem.rohr import Rohr

__all__ = ['Kostuemschuhe']


class Kostuemschuhe:
    #: (t längs des Fußes, Breite ×, Höhe ×) — Ferse hoch und schmal, Ballen breit, Spitze flach und rund.
    PROFIL = (
        (0.00, 0.30, 0.55),
        (0.05, 0.85, 1.05),
        (0.22, 0.95, 1.00),
        (0.50, 1.00, 0.80),
        (0.78, 0.92, 0.66),
        (0.95, 0.70, 0.52),
        (1.00, 0.30, 0.30),
    )

    def __init__(self, masse, p, vorn_grad):
        self.m = masse
        self.p = p
        self.vorn = 1 if vorn_grad == 90 else -1

    def farbe(self):
        return tuple(float(self.p['farbe.schuhe.%s' % k]) for k in 'rgb')

    def schuh(self, seite):
        x, y_min, y_max, breite, hoehe = self.m.fuss(seite)
        g = self.p['schuhe.groesse']
        hinten, spitze = (y_min, y_max) if self.vorn > 0 else (y_max, y_min)
        laenge = (spitze - hinten) * g
        hinten = hinten - (g - 1.0) * (spitze - hinten) * 0.25
        rohr = Rohr('Schuh_%s' % ('R' if seite > 0 else 'L'), self.farbe())
        for t, fb, fh in self.PROFIL:
            halbhoehe = max(0.012, hoehe * g * fh * 0.5)
            rohr.ring_auf_achse(
                (x, hinten + self.vorn * abs(laenge) * t, self.m.boden + halbhoehe),
                (0.0, self.vorn, 0.0),
                max(0.01, breite * g * fb + 0.008),
                halbhoehe + 0.004,
            )
        return rohr.bauen(dicke=0.004, glaetten=1)

    def bauen(self):
        if self.p['schuhe.an'] < 0.5:
            return []
        return [self.schuh(1), self.schuh(-1)]
