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
    #: Wie weit die Umriss-Hülle (`Kostuemhuelle`) die Ringe des Huts bewegen darf (Vielfaches der Weite aus dem Wertesatz).
    HUELLE_HUT = (0.85, 1.35)

    def __init__(self, masse, p, vorn_grad, huelle=None):
        self.m = masse
        self.p = p
        self.huelle = huelle
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
            kx,
            ky,
            kb * p['kapuze.kopf_weite'],
            kt * p['kapuze.kopf_weite'] * 0.96,
            kz + 0.01 * h,
        )
        mx, my, hb, ht = self.m.ring(self.m.z('hals'))
        rohr.ring_waagerecht(
            mx,
            my,
            hb * p['kapuze.hals_weite'],
            ht * p['kapuze.hals_weite'] * 0.95,
            self.m.z('hals'),
        )
        # Die Kapuze liegt auf den Schultern und fällt über den Rücken: erst ein Ring auf Schulterhöhe, dann
        # einer auf Brusthöhe — bis Version 1 endete sie als flache Scheibe auf den Schultern (wie eine zweite
        # Hutkrempe).
        mx, my, hb, ht = self.m.ring(self.m.z('schulter'))
        w = p['kapuze.schulter_weite']
        rohr.ring_waagerecht(
            mx,
            my - self.vorn * 0.01 * h,
            hb * w,
            ht * w * 1.1,
            self.m.z('schulter') + 0.005 * h,
            welle=0.03,
            wellen=6,
        )
        mx, my, hb, ht = self.m.ring(self.m.z('brust'))
        rohr.ring_waagerecht(
            mx,
            my - self.vorn * 0.015 * h,
            hb * w * 0.95,
            ht * w * 1.05,
            self.m.z('brust'),
            welle=0.04,
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
        # Der Bart der Vorlage ist breit und läuft rund aus (bis 30.09.2026 verjüngte er sich zu einer
        # Spitze).
        for t, r, welle in (
            (0.0, 1.0, 0.06),
            (0.15, 1.02, 0.10),
            (0.4, 0.95, 0.14),
            (0.7, 0.78, 0.16),
            (0.9, 0.45, 0.10),
            (1.0, 0.1, 0.0),
        ):
            rohr.ring_waagerecht(
                kx,
                y_vorn - self.vorn * t * kt * 0.5,
                kb * p['bart.breite'] * r,
                kt * 0.42 * r + 0.006,
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
        # (Höhe, Breite ×, Tiefe ×, Versatz nach hinten in Kopftiefen): oben am Schädel, dann nach unten
        # weiter und flacher — das Haar liegt auf Schultern und Rücken, es steht nicht als Zylinder um den
        # Kopf (Version 1).
        for z, fb, ft, zurueck in (
            (kz + 0.09 * h, 1.0, 1.0, 0.0),
            (kz + 0.03 * h, 1.08, 1.04, 0.05),
            (kz - p['haar.laenge'] * h * 0.4, 1.2, 0.95, 0.15),
            (kz - p['haar.laenge'] * h, 1.4, 0.8, 0.3),
        ):
            rohr.ring_waagerecht(
                kx, hinten - self.vorn * kt * zurueck, kb * w * fb, kt * w * ft * 0.9, z, welle=0.06, wellen=9
            )
        return rohr.bauen(dicke=0.006)

    def hut(self):
        p = self.p
        kx, ky, kb, kt, kz = self.m.kopf()
        h = self.m.hoehe
        auf = self.m.scheitel - 0.02
        krone, krempe = p['hut.krone_weite'], p['hut.krempe_weite']
        rand = Rohr('Krempe', self.farbe('hut'), huelle=self.huelle)
        rand.ring_waagerecht(kx, ky, kb * krone, kt * krone * 0.96, auf + 0.005)
        # `hut.kipp`: Die Krempe der Vorlage sitzt schräg — vorn angehoben (die Stirn und die Augen sind
        # frei), hinten gesenkt. Ohne Neigung deckte die hängende Krempe (`krempe_haengen`, für die
        # Seitenumrisse gebraucht) das Gesicht zu (Detailbild vom 30.09.2026).
        kipp = p['hut.kipp']
        neigung = self.vorn * kipp
        rand.ring_waagerecht(
            kx,
            ky,
            kb * (krone + krempe) * 0.55,
            kt * (krone + krempe) * 0.53,
            auf - 0.005,
            dz=lambda w: 0.5 * neigung * np.sin(w),
            anpassen=self.HUELLE_HUT,
        )
        rand.ring_waagerecht(
            kx,
            ky,
            kb * krempe,
            kt * krempe * 0.935,
            auf - 0.005 - p['hut.krempe_haengen'],
            welle=0.04,
            wellen=7,
            dz=lambda w: neigung * np.sin(w),
            anpassen=self.HUELLE_HUT,
        )
        spitze = Rohr('Hutspitze', self.farbe('hut'), huelle=self.huelle)
        hoehe = p['hut.hoehe'] * h
        for t in np.linspace(0, 1, 11):
            r = (1 - t) ** 1.3
            biegung = p['hut.biegung'] * h * t**2.4
            # nach HINTEN gebogen (gegen die Blickrichtung) — bis Runde 9 fest nach −y, bei dieser Figur das
            # Gesicht `hut.seite`: die Spitze der Vorlage neigt sich auch zur Seite (von vorn gesehen nach
            # links im Bild)
            spitze.ring_waagerecht(
                kx + p['hut.seite'] * h * t**2.4,
                ky - self.vorn * biegung * 0.7,
                kb * krone * r + 0.004,
                kt * krone * 0.96 * r + 0.004,
                auf + hoehe * t - biegung * 0.3,
                anpassen=self.HUELLE_HUT if t < 0.75 else None,
            )
        teile = [rand.bauen(dicke=0.008, glaetten=1), spitze.bauen(dicke=0.006, deckel_oben=True)]
        if p['borte.an'] >= 0.5:
            # Hutband: zwei Ringe kurz über der Krempe, ein wenig weiter als die Spitze an dieser Stelle.
            band = Rohr('Hutband', self.farbe('borte'))
            for dz in (0.006, 0.006 + p['borte.breite'] * 0.5):
                r = (1 - dz / max(hoehe, 0.05)) ** 1.3
                band.ring_waagerecht(kx, ky, kb * krone * r + 0.011, kt * krone * 0.96 * r + 0.011, auf + dz)
            teile.append(band.bauen(dicke=0.004, glaetten=0))
        return teile

    def bauen(self):
        teile = []
        schalter = (('kapuze', self.kapuze), ('haar', self.haar), ('bart', self.bart))
        for name, bau in schalter:
            if self.p['%s.an' % name] >= 0.5:
                teile.append(bau())
        if self.p['hut.an'] >= 0.5:
            teile += self.hut()
        return teile
