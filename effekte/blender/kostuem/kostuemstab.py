# -*- coding: utf-8 -*-
"""Kostuemstab — der Zauberstab in der RECHTEN Hand der Figur: knorriger Schaft vom Boden bis über die Schulter, oben
eine Fassung um eine blaue Kristallkugel.

Rechts heißt: rechts der Figur, nicht des Bildes. Blickt sie nach −y, liegt ihre rechte Seite bei −x
(Blickrichtung × oben); blickt sie nach +y, bei +x — die Seite ist also das Vorzeichen der Blickrichtung
(`seite = vorn`). In der Vorlage steht der Stab in der Vorderansicht links im Bild: das ist die rechte Hand der
Figur. Er steht VOR dem Körper (in den Seitenansichten weit vor der Brust): Der rechte Unterarm ist gebeugt
(`pose.ellbogen_stab`), der Schaft geht senkrecht durch die Faust — bis Version 1 stand er neben der Hüfte und war
in den Seitenansichten hinter dem Körper versteckt (Bild vom 30.09.2026: in ±90° kein Stab zu sehen).

Bauteile: Schaft (`Stab`, Ringe mit seitlicher Schlängelung und Knoten, `stab.knorrig`), Fassung (`Stabfassung`,
ein Becher, der sich zur Kugel weitet, `stab.kopf`) und Kugel (`Stabkugel`, Farbe `kristall`).
"""

import numpy as np

from effekte.blender.kostuem.rohr import Rohr

__all__ = ['Kostuemstab']


class Kostuemstab:
    RINGE = 34

    def __init__(self, masse, p, vorn_grad):
        self.m = masse
        self.p = p
        self.vorn_grad = vorn_grad
        self.vorn = 1 if vorn_grad == 90 else -1

    def farbe(self, name='stab'):
        return tuple(float(self.p['farbe.%s.%s' % (name, k)]) for k in 'rgb')

    def _faust(self):
        """Mitte der Faust: hinter dem Handgelenk in Richtung Unterarm."""
        seite = self.vorn
        _, hand, _ = self.m.arm(seite)
        ellbogen = self.m.ellbogen.get(seite)
        if ellbogen is not None:
            richtung = np.asarray(hand, float) - np.asarray(ellbogen, float)
            hand = np.asarray(hand, float) + richtung / max(float(np.linalg.norm(richtung)), 1e-6) * 0.04
        # `stab.vorn`: In den Seitenansichten der Vorlage steht der Stab weiter vor dem Körper, als der Arm reicht.
        return float(hand[0]) + seite * self.p['stab.abstand'], float(hand[1]) + seite * self.p['stab.vorn']

    def bauen(self):
        p = self.p
        if p['stab.an'] < 0.5:
            return []
        x, y = self._faust()
        boden = self.m.boden
        oben = boden + p['stab.hoehe'] * self.m.hoehe
        r = p['stab.dicke']
        kugel = p['stab.kristall']
        fassung = kugel * p['stab.kopf']
        # Der Schaft endet unter der Fassung; die Kugel sitzt zu gut einem Drittel in ihr und ragt oben heraus.
        z_schaft = oben - kugel * 2.1 - 0.03
        schaft = Rohr('Stab', self.farbe())
        knorrig = p['stab.knorrig']
        for i, z in enumerate(np.linspace(boden, z_schaft, self.RINGE)):
            t = i / (self.RINGE - 1)
            schlaenge = knorrig * r * 1.4 * np.sin(t * 17.0)
            knoten = 1.0 + knorrig * (0.5 * max(0.0, np.sin(t * 23.0 + 1.0)) ** 3 + 0.9 * max(0.0, t - 0.86) * 6)
            schaft.ring_waagerecht(x + float(schlaenge), y + 0.4 * float(schlaenge), r * knoten, r * knoten, float(z))
        teile = [schaft.bauen(dicke=0.0, glaetten=1)]
        if kugel > 0.005:
            cup = Rohr('Stabfassung', self.farbe())
            hoehe_cup = 0.03 + kugel * 0.8
            for t in np.linspace(0.0, 1.0, 7):
                weite = r * 1.6 + (fassung - r * 1.6) * float(np.sin(t * np.pi / 2)) ** 1.2
                cup.ring_waagerecht(x, y, weite, weite, z_schaft + t * hoehe_cup)
            teile.append(cup.bauen(dicke=0.004, glaetten=1))
            ball = Rohr('Stabkugel', self.farbe('kristall'))
            mitte = z_schaft + hoehe_cup + kugel * 0.35
            for w in np.linspace(-0.95, 0.95, 13):
                rk = kugel * float(np.sqrt(1 - w * w))
                ball.ring_waagerecht(x, y, rk, rk, mitte + kugel * float(w))
            teile.append(ball.bauen(dicke=0.0, glaetten=1, deckel_oben=True))
            if p['stab.krone'] > 0.005:
                teile.append(self._krone(x, y, z_schaft + hoehe_cup, mitte, kugel, r))
        return teile

    def _krone(self, x, y, z_cup, z_kugel, kugel, r):
        """Die Holzkrone der Vorlage: verschlungene Äste, die die Kugel umgreifen und darüber zusammenlaufen. Als Käfig
        gebaut (Ringe mit fünf Ausbuchtungen, vorn offen — die Kugel bleibt von vorn zu sehen), nicht als Deckel."""
        krone = self.p['stab.krone']
        rohr = Rohr('Stabkrone', self.farbe(), offen_grad=120.0, offen_richtung=self.vorn_grad)
        hoch = z_kugel + kugel + krone * 2.2
        for t in np.linspace(0.0, 1.0, 9):
            z = z_cup + (hoch - z_cup) * t
            # unten schmal, auf Höhe der Kugel am weitesten, oben wieder eng (die Äste laufen zusammen)
            weite = r * 1.3 + (kugel + krone * 0.6 - r * 1.3) * float(np.sin(min(t * 1.25, 1.0) * np.pi / 2)) ** 1.1
            weite *= 1.0 - 0.75 * max(0.0, t - 0.6) / 0.4
            rohr.ring_waagerecht(x, y, weite + 0.004, weite + 0.004, z, welle=0.3, wellen=5)
        return rohr.bauen(dicke=0.007, glaetten=1)
