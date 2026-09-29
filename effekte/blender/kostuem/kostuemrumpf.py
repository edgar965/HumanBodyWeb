# -*- coding: utf-8 -*-
"""Kostuemrumpf — was am Rumpf hängt: Unterkleid, Mantel, Ärmel, Gürtel, Gürteltaschen.

Jedes Maß ist ein Vielfaches eines Körpermaßes (`Koerpermasse`) mal einem Wert aus dem Wertesatz `p`
(Schlüssel `teil.name`, Schema und Startwerte: `core/dienste/kostuemparameter.py`). Die Startwerte sind die
von Hand gefundenen Faktoren der Kostüm-Runde 9 — ohne Wertesatz sieht das Kostüm aus wie damals.
"""

from effekte.blender.kostuem.rohr import Rohr

__all__ = ['Kostuemrumpf']


class Kostuemrumpf:
    def __init__(self, masse, p, vorn_grad):
        self.m = masse
        self.p = p
        self.vorn_grad = vorn_grad
        self.vorn = 1 if vorn_grad == 90 else -1

    def farbe(self, name):
        return tuple(float(self.p['farbe.%s.%s' % (name, k)]) for k in 'rgb')

    def _rumpfringe(self, rohr, namen, luft):
        for name in namen:
            mx, my, hb, ht = self.m.ring(self.m.z(name))
            rohr.ring_waagerecht(mx, my, hb * luft, ht * luft, self.m.z(name))

    def _rockringe(self, rohr, mitte_weite, saum_hoehe, saum_weite, welle, wellen):
        """Zwei Ringe unter der Hüfte: Kniehöhe (0,29 × Höhe) und Saum — der Saum liegt laut Schema immer
        tiefer."""
        mx, my, hb, ht = self.m.ring(self.m.z('huefte'))
        for anteil, f in ((0.29, mitte_weite), (saum_hoehe, saum_weite)):
            rohr.ring_waagerecht(
                mx, my, hb * f, ht * f, self.m.boden + anteil * self.m.hoehe, welle=welle, wellen=wellen
            )

    def unterkleid(self):
        p = self.p
        rohr = Rohr('Unterkleid', self.farbe('unterkleid'))
        self._rumpfringe(rohr, ('hals', 'schulter', 'brust', 'taille', 'huefte'), p['unterkleid.luft'])
        self._rockringe(
            rohr,
            p['unterkleid.mitte_weite'],
            p['unterkleid.saum_hoehe'],
            p['unterkleid.saum_weite'],
            p['unterkleid.welle'],
            12,
        )
        return rohr.bauen(dicke=0.004, deckel_oben=True)

    def mantel(self):
        p = self.p
        rohr = Rohr(
            'Mantel', self.farbe('mantel'), offen_grad=p['mantel.offen_grad'], offen_richtung=self.vorn_grad
        )
        mx, my, hb, ht = self.m.ring(self.m.z('hals'))
        rohr.ring_waagerecht(
            mx, my, hb * p['mantel.hals_weite'], ht * p['mantel.hals_weite'] * 0.9, self.m.z('hals') + 0.01
        )
        mx, my, hb, ht = self.m.ring(self.m.z('schulter'))
        rohr.ring_waagerecht(
            mx,
            my,
            hb * p['mantel.schulter_weite'],
            ht * p['mantel.schulter_tiefe'],
            self.m.z('schulter') - 0.02,
        )
        self._rumpfringe(rohr, ('brust', 'taille', 'huefte'), p['mantel.luft'])
        self._rockringe(
            rohr,
            p['mantel.mitte_weite'],
            p['mantel.saum_hoehe'],
            p['mantel.saum_weite'],
            p['mantel.welle'],
            9,
        )
        return rohr.bauen(dicke=0.008)

    def aermel(self, seite):
        p = self.p
        schulter, hand, radius = self.m.arm(seite)
        achse = hand - schulter
        rohr = Rohr('Aermel_%s' % ('R' if seite > 0 else 'L'), self.farbe('mantel'))
        laenge = p['aermel.laenge']
        oben, mitte, saum = p['aermel.weite_oben'], p['aermel.weite_mitte'], p['aermel.weite_saum']
        for t, f in (
            (-0.05, oben),
            (0.4, mitte),
            (0.75, mitte * 0.97),
            (0.95, (mitte + saum) / 2),
            (1.05, saum),
        ):
            t = t if t < 0 else t * laenge / 1.05
            rohr.ring_auf_achse(
                schulter + achse * t, achse, radius * f, radius * f * (1.0 if t < 0.9 else 1.1)
            )
        return rohr.bauen(dicke=0.008)

    def guertel(self):
        p = self.p
        mx, my, hb, ht = self.m.ring(self.m.z('taille'))
        rohr = Rohr('Guertel', self.farbe('leder'))
        weite = p['mantel.luft'] * p['guertel.weite']
        for dz in (-p['guertel.breite'] / 2, p['guertel.breite'] / 2):
            rohr.ring_waagerecht(mx, my, hb * weite, ht * weite, self.m.z('taille') + dz)
        return rohr.bauen(dicke=0.01, glaetten=0)

    def tasche(self, seite):
        """Lederbeutel am Gürtel, vorn seitlich (Vorlage: Beutel und Fläschchen an der Hüfte)."""
        g = self.p['taschen.groesse']
        mx, my, hb, ht = self.m.ring(self.m.z('taille'))
        z0 = self.m.z('taille')
        rohr = Rohr('Guerteltasche_%s' % ('R' if seite > 0 else 'L'), self.farbe('leder'))
        cx, cy = mx + seite * hb * 0.75, my + self.vorn * ht * 1.05
        for r, dz in ((0.55, 0.0), (1.0, -0.03), (0.85, -0.09), (0.1, -0.115)):
            rohr.ring_waagerecht(cx, cy, 0.045 * r * g, 0.035 * r * g, z0 + dz * g)
        return rohr.bauen(dicke=0.004, deckel_oben=True)

    def bauen(self):
        teile = [self.unterkleid(), self.mantel(), self.aermel(1), self.aermel(-1), self.guertel()]
        if self.p['taschen.an'] >= 0.5:
            teile += [self.tasche(1), self.tasche(-1)]
        return teile
