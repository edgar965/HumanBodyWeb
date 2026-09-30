# -*- coding: utf-8 -*-
"""Koerpermasse — was das Kostüm vom Körper wissen muss, gemessen am importierten Netz (Blender, z oben).

Alle Maße in Metern, aus den Punkten des Körpernetzes: Höhe, Höhen von
Hals/Schulter/Brust/Taille/Hüfte/Knie/Wade/ Knöchel als Anteile der Körperhöhe (Genesis-9-Grundfigur,
A-Haltung), je Höhe Halbbreite und Halbtiefe des Rumpfes (Arme ausgeschlossen), die Achse jedes Arms (Schulter
→ Handgelenk), der Kopf — und die Blickrichtung.
"""

import numpy as np

__all__ = ['Koerpermasse']


class Koerpermasse:
    #: Höhen als Anteil der Körperhöhe (gemessen an der A-Haltung der Grundfigur, Kostüm-Runde 1).
    HOEHEN = {
        'hals': 0.86,
        'schulter': 0.815,
        'brust': 0.73,
        'taille': 0.62,
        'huefte': 0.53,
        'knie': 0.29,
        'wade': 0.18,
        'knoechel': 0.06,
    }
    #: Rumpfkern: Punkte mit |x| unter diesem Anteil der Körperhöhe zählen als Rumpf, nicht als Arm.
    RUMPF_X = 0.11
    #: Kopf: die obersten so viel der Körperhöhe.
    KOPF = 0.13
    #: Mit Knochen (`arme`): Punkte näher als so viel an der Achse Schulter → Hand gehören zum Arm, nicht zum
    # Rumpf.
    ARM_NAEHE = 0.075

    def __init__(self, punkte, arme=None, ellbogen=None):
        p = np.asarray(punkte, dtype=float)
        self.punkte = p
        #: {seite: (schulter, handgelenk)} aus dem Rig (`Koerperpose.arme`) — ohne Rig misst `arm` an den
        # Punkten.
        self.arme = arme or {}
        #: {seite: Ellbogen} (`Koerperpose.ellbogen`): Ein gebeugter Arm liegt nicht auf der Strecke
        # Schulter → Handgelenk; ohne diese Angabe würde sein Unterarm zum Rumpf gezählt.
        self.ellbogen = ellbogen or {}
        self.boden = float(p[:, 2].min())
        self.scheitel = float(p[:, 2].max())
        self.hoehe = self.scheitel - self.boden
        self.mitte_y = float(np.median(p[:, 1]))
        self._rumpf = self._rumpfmaske()

    def z(self, name):
        return self.boden + self.HOEHEN[name] * self.hoehe

    @staticmethod
    def _abstand_zur_strecke(p, a, b):
        ab = b - a
        t = np.clip(((p - a) @ ab) / max(float(ab @ ab), 1e-9), 0.0, 1.0)
        return np.linalg.norm(p - (a + np.outer(t, ab)), axis=1), t

    def _rumpfmaske(self):
        """Welche Punkte zum Rumpf zählen. Ohne Rig: |x| klein (A-Haltung, die Arme stehen weit ab). Mit Rig:
        alles, was nicht nahe an einer Armachse liegt — hängende Arme liegen dicht am Rumpf, |x| trennt sie
        nicht mehr."""
        p = self.punkte
        if not self.arme:
            return np.abs(p[:, 0]) < self.RUMPF_X * self.hoehe
        maske = np.ones(len(p), dtype=bool)
        for seite, (schulter, hand) in self.arme.items():
            e = self.ellbogen.get(seite)
            if e is None:
                segmente = [(schulter, hand + (hand - schulter) * 0.35, 0.08)]
            else:
                segmente = [(schulter, e, 0.08), (e, hand + (hand - e) * 0.5, 0.0)]
            for a, b, ab_t in segmente:
                abstand, t = self._abstand_zur_strecke(p, a, b)
                maske &= ~((abstand < self.ARM_NAEHE) & (t > ab_t))
        return maske

    def ring(self, z, band=0.015, nur_rumpf=True):
        """(mitte_x, mitte_y, halbbreite, halbtiefe) des Querschnitts auf Höhe z."""
        p = self.punkte
        sel = np.abs(p[:, 2] - z) < band
        if nur_rumpf:
            sel &= self._rumpf
        q = p[sel]
        if len(q) < 8:
            return 0.0, self.mitte_y, 0.08, 0.06
        x0, x1 = np.percentile(q[:, 0], [1, 99])
        y0, y1 = np.percentile(q[:, 1], [1, 99])
        return float((x0 + x1) / 2), float((y0 + y1) / 2), float((x1 - x0) / 2), float((y1 - y0) / 2)

    def arm(self, seite):
        """(schulter, handgelenk, radius) — mit Rig aus den Knochen, sonst per Hauptachse der Armpunkte; seite
        ±1 (Vorzeichen von x). Der Radius: 80. Perzentil der Abstände der Armpunkte zur Achse."""
        p = self.punkte
        if seite in self.arme:
            schulter, hand = (np.asarray(v, dtype=float) for v in self.arme[seite])
            # Gebeugt: der Radius wird am Oberarm gemessen (Schulter → Ellbogen), sonst an der ganzen Strecke.
            ende = np.asarray(self.ellbogen[seite], dtype=float) if seite in self.ellbogen else hand
            abstand, t = self._abstand_zur_strecke(p, schulter, ende)
            nah = abstand[(abstand < self.ARM_NAEHE) & (t > 0.1) & (t < 0.95)]
            return schulter, hand, float(np.percentile(nah, 80)) if len(nah) > 20 else 0.045
        sel = (np.sign(p[:, 0]) == seite) & (np.abs(p[:, 0]) > self.RUMPF_X * self.hoehe * 1.3)
        sel &= p[:, 2] > self.z('huefte') * 0.9
        q = p[sel]
        if len(q) < 50:
            s = np.array([seite * 0.2, self.mitte_y, self.z('schulter')])
            return s, s + np.array([seite * 0.45, 0, -0.45]), 0.045
        mitte = q.mean(axis=0)
        achse = np.linalg.svd(q - mitte)[2][0]
        if achse[0] * seite < 0:
            achse = -achse
        t = (q - mitte) @ achse
        schulter = mitte + achse * np.percentile(t, 2)
        hand = mitte + achse * np.percentile(t, 97)
        senk = q - mitte - np.outer(t, achse)
        radius = float(np.percentile(np.linalg.norm(senk, axis=1), 80))
        return schulter, hand, radius

    def fuss(self, seite):
        """(mitte_x, y_min, y_max, halbbreite, hoehe) des Fußes auf `seite` (Vorzeichen von x): die Punkte in den
        untersten 7,5 % der Körperhöhe. Für die Schuhe (`Kostuemschuhe`)."""
        p = self.punkte
        sel = (p[:, 2] < self.boden + 0.075 * self.hoehe) & (np.sign(p[:, 0]) == seite) & (np.abs(p[:, 0]) > 0.02)
        q = p[sel]
        if len(q) < 30:
            return seite * 0.09, self.mitte_y - 0.10, self.mitte_y + 0.16, 0.045, 0.09
        x0, x1 = np.percentile(q[:, 0], [2, 98])
        y0, y1 = np.percentile(q[:, 1], [1, 99])
        return (
            float((x0 + x1) / 2),
            float(y0),
            float(y1),
            float((x1 - x0) / 2),
            float(np.percentile(q[:, 2], 98) - self.boden),
        )

    def kopf(self):
        """(mitte_x, mitte_y, halbbreite, halbtiefe, z_unten) des Kopfes."""
        p = self.punkte
        # Nur Punkte nahe der Mittellinie: Ein nach vorn geschwungener Arm (`pose.arm_vor`) hebt die Hand bis in
        # Kopfhöhe — ohne den Filter verschöbe sie Mitte und Breite des Kopfes und mit ihnen Hut, Haar und Bart.
        q = p[(p[:, 2] > self.scheitel - self.KOPF * self.hoehe) & (np.abs(p[:, 0]) < 0.1 * self.hoehe)]
        x0, x1 = np.percentile(q[:, 0], [1, 99])
        y0, y1 = np.percentile(q[:, 1], [1, 99])
        return (
            float((x0 + x1) / 2),
            float((y0 + y1) / 2),
            float((x1 - x0) / 2),
            float((y1 - y0) / 2),
            float(self.scheitel - self.KOPF * self.hoehe),
        )

    def vorn_grad(self):
        """Blickrichtung als Winkel in der xy-Ebene: +90 (Gesicht nach +y) oder −90 (nach −y), dazu die
        Zählung.

        NICHT über die Ausdehnung (Kostüm-Runden 6/7: Rückseite und Gesicht ragen bei dieser Grundfigur
        ähnlich weit heraus, die Differenz war zu knapp und zeigte auf die falsche Seite — kein Bart, keine
        Kapuze zu sehen). Stattdessen die PUNKTDICHTE auf Augenhöhe: ein modelliertes Gesicht hat um ein
        Vielfaches mehr Eckpunkte als der glatte Hinterkopf — gemessen an der maskulinen Grundfigur 2084 zu
        420 Punkten.
        """
        _, ky, _, _, _ = self.kopf()
        von, bis = self.scheitel - 0.09 * self.hoehe, self.scheitel - 0.03 * self.hoehe
        band = self.punkte[(self.punkte[:, 2] > von) & (self.punkte[:, 2] < bis)]
        plus = int(np.count_nonzero(band[:, 1] - ky > 0.02 * self.hoehe))
        minus = int(np.count_nonzero(band[:, 1] - ky < -0.02 * self.hoehe))
        return (90 if plus > minus else -90), {'plus': plus, 'minus': minus}

    def bericht(self):
        aus = {'hoehe_m': round(self.hoehe, 3)}
        for name in self.HOEHEN:
            _, _, hb, ht = self.ring(self.z(name))
            aus[name] = {'z': round(self.z(name), 3), 'halbbreite': round(hb, 3), 'halbtiefe': round(ht, 3)}
        aus['fuss'] = {
            str(s): [round(v, 3) for v in self.fuss(s)] for s in (1, -1)
        }  # (mitte_x, y_min, y_max, halbbreite, hoehe)
        kx, ky, kb, kt, kz = self.kopf()
        aus['kopf'] = {
            'mitte': [round(kx, 3), round(ky, 3)],
            'halbbreite': round(kb, 3),
            'halbtiefe': round(kt, 3),
            'unten': round(kz, 3),
            'scheitel': round(self.scheitel, 3),
        }
        return aus
