# -*- coding: utf-8 -*-
"""Kostuemkopf — was am Kopf sitzt: Kapuze, Bart, langes Haar, Spitzhut. Werte aus `p` wie `Kostuemrumpf`.

Zwei Lehren der Handrunden stecken in den Formeln: Die Kapuzenringe fallen streng in z (Kopf → Hals →
Schulter, sonst faltet sich das Rohr), und der Bart sitzt deutlich VOR der Gesichtsfläche (`kt·abstand`,
Startwert 1,3 — bei 0,85 lag er hinter der Nasenspitze, die bei ~1,05·kt liegt, und steckte unsichtbar im
Kopf).
"""

import numpy as np

from effekte.blender.kostuem.rohr import Rohr

__all__ = ['Kostuemkopf']


class Kostuemkopf:
    def __init__(self, masse, p, vorn_grad):
        self.m = masse
        self.p = p
        self.vorn_grad = vorn_grad
        self.vorn = 1 if vorn_grad == 90 else -1

    def farbe(self, name):
        return tuple(float(self.p['farbe.%s.%s' % (name, k)]) for k in 'rgb')

    def kapuze(self):
        p = self.p
        kx, ky, kb, kt, kz = self.m.kopf()
        h = self.m.hoehe
        rohr = Rohr(
            'Kapuze', self.farbe('mantel'), offen_grad=p['kapuze.offen_grad'], offen_richtung=self.vorn_grad
        )
        rohr.ring_waagerecht(
            kx, ky, kb * p['kapuze.kopf_weite'], kt * p['kapuze.kopf_weite'] * 0.96, kz + 0.01 * h
        )
        mx, my, hb, ht = self.m.ring(self.m.z('hals'))
        rohr.ring_waagerecht(
            mx, my, hb * p['kapuze.hals_weite'], ht * p['kapuze.hals_weite'] * 0.95, self.m.z('hals')
        )
        mx, my, hb, ht = self.m.ring(self.m.z('schulter'))
        w = p['kapuze.schulter_weite']
        rohr.ring_waagerecht(
            mx,
            my - self.vorn * 0.02 * h,
            hb * w,
            ht * w * 1.2,
            self.m.z('schulter') + 0.02 * h,
            welle=0.03,
            wellen=6,
        )
        return rohr.bauen(dicke=0.006)

    def bart(self):
        p = self.p
        kx, ky, kb, kt, kz = self.m.kopf()
        h = self.m.hoehe
        y_vorn = ky + self.vorn * kt * p['bart.abstand']
        rohr = Rohr('Bart', self.farbe('bart'))
        laenge = p['bart.laenge'] * h
        for t, r, welle in (
            (0.0, 1.0, 0.06),
            (0.15, 0.92, 0.10),
            (0.4, 0.65, 0.14),
            (0.7, 0.35, 0.16),
            (0.92, 0.12, 0.10),
            (1.0, 0.02, 0.0),
        ):
            rohr.ring_waagerecht(
                kx,
                y_vorn - self.vorn * t * kt * 0.5,
                kb * p['bart.breite'] * r,
                kt * 0.4 * r + 0.006,
                kz + 0.01 * h - laenge * t,
                welle=welle,
                wellen=5,
            )
        return rohr.bauen(dicke=0.005, deckel_oben=True)

    def haar(self):
        """Langes Haar hinter dem Kopf bis auf die Schultern, vorn offen (das Gesicht bleibt frei)."""
        p = self.p
        kx, ky, kb, kt, kz = self.m.kopf()
        h = self.m.hoehe
        w = p['haar.weite']
        rohr = Rohr('Haar', self.farbe('bart'), offen_grad=150.0, offen_richtung=self.vorn_grad)
        hinten = ky - self.vorn * kt * 0.15
        for z, f in (
            (kz + 0.08 * h, 1.0),
            (kz + 0.02 * h, 1.02),
            (kz - p['haar.laenge'] * h * 0.5, 0.95),
            (kz - p['haar.laenge'] * h, 0.8),
        ):
            rohr.ring_waagerecht(kx, hinten, kb * w * f, kt * w * f * 0.9, z, welle=0.05, wellen=9)
        return rohr.bauen(dicke=0.006)

    def hut(self):
        p = self.p
        kx, ky, kb, kt, kz = self.m.kopf()
        h = self.m.hoehe
        auf = self.m.scheitel - 0.02
        krone, krempe = p['hut.krone_weite'], p['hut.krempe_weite']
        rand = Rohr('Krempe', self.farbe('mantel'))
        rand.ring_waagerecht(kx, ky, kb * krone, kt * krone * 0.96, auf + 0.005)
        rand.ring_waagerecht(kx, ky, kb * (krone + krempe) * 0.55, kt * (krone + krempe) * 0.53, auf - 0.005)
        rand.ring_waagerecht(
            kx,
            ky,
            kb * krempe,
            kt * krempe * 0.935,
            auf - 0.005 - p['hut.krempe_haengen'],
            welle=0.04,
            wellen=7,
        )
        spitze = Rohr('Hutspitze', self.farbe('mantel'))
        hoehe = p['hut.hoehe'] * h
        for t in np.linspace(0, 1, 11):
            r = (1 - t) ** 1.3
            biegung = p['hut.biegung'] * h * t**2.4
            # nach HINTEN gebogen (gegen die Blickrichtung) — bis Runde 9 fest nach −y, bei dieser Figur das
            # Gesicht
            spitze.ring_waagerecht(
                kx,
                ky - self.vorn * biegung * 0.7,
                kb * krone * r + 0.004,
                kt * krone * 0.96 * r + 0.004,
                auf + hoehe * t - biegung * 0.3,
            )
        return [rand.bauen(dicke=0.008, glaetten=1), spitze.bauen(dicke=0.006, deckel_oben=True)]

    def bauen(self):
        teile = []
        schalter = (('kapuze', self.kapuze), ('haar', self.haar), ('bart', self.bart))
        for name, bau in schalter:
            if self.p['%s.an' % name] >= 0.5:
                teile.append(bau())
        if self.p['hut.an'] >= 0.5:
            teile += self.hut()
        return teile
