# -*- coding: utf-8 -*-
"""Hosenfalten — Stoffdrapierung auf eine Hose des Stand-Modells, die als glatte Röhre aus der Stoffsimulation kommt (04.10.2026).

Anlass (Edgar, 04.10.2026): Die Hose „ist nun ganz eng anliegend, ohne Falten wie im Original", „um den Penis herum völlig falsch — das Original hat Stoffdrapierungen".
Die Hose aus GarmentCode legt sich nach dem Anliegen (`bau.anliegen_mm`) wie ein Strumpf auf die Haut; die Vorlage (`Model_Jobs/Frank/Randy/vorlage.jpeg`, vergrößert) zeigt
eine schlanke weiße Hose mit Schrittnaht und Reißverschlusswulst, feinen Falten, die vom Schritt fächerförmig nach außen laufen, Querfalten am Knie und Stauchfalten am Saum.

Hier entstehen diese Falten rein als Verschiebung der Punkte entlang der Oberflächennormalen (keine Simulation, keine Physik — siehe unten). Maße in Metern, Y oben, Z nach vorn;
der Schritt ist der tiefste Punkt dicht an der Mittelebene (|x| < 1,2 cm; gemessen am Stand von Runde 55: 0,70 m, mit |x| < 2 cm stand dort 0,64 m, die Stelle, an der die Beine auseinandergehen), das Knie liegt bei 58 % der Beinlänge (Schritt bis Saum) — beides Annahmen aus dem Körperbau, an der Hose
des Randy nicht nachgemessen. Die Höhen der Falten (Millimeter) sind Geschmack, an der Vorlage nach Augenmaß gewählt, nicht gemessen.

    punkte = Hosenfalten.anwenden(punkte, dreiecke)        # (N, 3) in denselben Einheiten wie die Eingabe (Meter oder Zentimeter)

Eine echte Faltenbildung kommt aus der Stoffsimulation im Film (Hose und Hemd in `film_video.py --stoff hybrid|sim`); die Hose ist dort bisher gehäutet (starr am Körper).
"""

import numpy as np

__all__ = ['Hosenfalten']


class Hosenfalten:
    #: Größte Verschiebung nach außen / nach innen (m): nach innen höchstens ein Millimeter, sonst durchstößt der Stoff die Haut (Abstand zur Haut siehe `bau.anliegen_mm`).
    AUSSEN, INNEN = 0.010, 0.003
    FAECHER = 0.30            # Radius um den Schritt (m), in dem die Falten fächerförmig nach außen laufen
    KNIE = 0.58               # Anteil der Beinlänge (Schritt → Saum), bei dem das Knie liegt

    @staticmethod
    def _normalen(p, d):
        n = np.zeros_like(p)
        f = np.cross(p[d[:, 1]] - p[d[:, 0]], p[d[:, 2]] - p[d[:, 0]])
        for k in range(3):
            np.add.at(n, d[:, k], f)
        return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)

    @classmethod
    def _nach_aussen(cls, p, n):
        """Normalen nach außen drehen: weg von den beiden Beinachsen (Schwerpunkt der Punkte je Seite)."""
        weg = np.zeros_like(p)
        for seite in (p[:, 0] > 0.0, p[:, 0] <= 0.0):
            if seite.sum() > 10:
                mitte = p[seite].mean(axis=0)
                weg[seite] = p[seite] - np.array([mitte[0], p[seite][:, 1].mean(), mitte[2]])
        weg[:, 1] = 0.0
        return n if (n * weg).sum() >= 0.0 else -n

    @staticmethod
    def _weich(x):
        x = np.clip(x, 0.0, 1.0)
        return x * x * (3.0 - 2.0 * x)

    @classmethod
    def innen(cls, punkte, dreiecke):
        """Boolesche Reihe (je Dreieck): zeigt das Dreieck zum anderen Bein hin (Innenseite von Oberschenkel und Wade) oder liegt es im Schritt? Dort gehört nie ein Seitenstreifen hin
        (`Stoffweissung`, Regel 2). Kriterium: Normale (nach außen) mal Vorzeichen von x < −0,25, oder dicht an der Mittelebene (|x| < 3 cm) mit nach unten zeigender Normale."""
        roh = np.asarray(punkte, dtype=np.float64)
        p = roh * (1.0 if np.ptp(roh[:, 1]) < 5.0 else 0.01)
        d = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        n = cls._nach_aussen(p, cls._normalen(p, d))
        mitte = p[d].mean(axis=1)
        nz = n[d].mean(axis=1)
        zum_bein = nz[:, 0] * np.sign(mitte[:, 0]) < -0.25
        schritt = (np.abs(mitte[:, 0]) < 0.03) & (nz[:, 1] < -0.3)
        return zum_bein | schritt

    @classmethod
    def anwenden(cls, punkte, dreiecke):
        roh = np.asarray(punkte, dtype=np.float64)
        skala = 1.0 if np.ptp(roh[:, 1]) < 5.0 else 0.01          # Meter oder Zentimeter
        p = roh * skala
        d = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        n = cls._nach_aussen(p, cls._normalen(p, d))
        ymin, ymax = p[:, 1].min(), p[:, 1].max()
        mitte = p[np.abs(p[:, 0]) < 0.012]
        yc = float(mitte[:, 1].min()) if len(mitte) else ymin + 0.8 * (ymax - ymin)
        bein = max(yc - ymin, 0.3)
        x, y, z = p[:, 0], p[:, 1], p[:, 2]
        vorn = cls._weich((n[:, 2] + 0.2) / 0.6)                   # 1 auf der Vorderseite
        hinten = cls._weich((-n[:, 2] + 0.2) / 0.6)
        # Winkel um die Beinachse: die Faltenlinien schlängeln sich (kein gerader Ring)
        theta = np.arctan2(z - np.where(x > 0, p[x > 0, 2].mean(), p[x <= 0, 2].mean()), np.abs(x) - np.where(x > 0, np.abs(p[x > 0, 0]).mean(), np.abs(p[x <= 0, 0]).mean()))
        # 1. Fächer vom Schritt: Falten laufen strahlenförmig vom Schritt nach oben/außen
        r = np.hypot(x, y - yc)
        alpha = np.arctan2(y - yc, x)
        faecher = np.sin(9.0 * alpha + 0.6 * np.sin(3.0 * alpha + 1.0)) * (1.0 - cls._weich(r / cls.FAECHER)) ** 1.2 * (0.55 + 0.45 * np.sin(23.0 * r))
        feld = 0.0060 * faecher * (0.6 * vorn + 0.4 * hinten)
        # 2. Reißverschlusswulst vorn: schmale Rinne an der Mittelnaht vom Schritt aufwärts
        rinne = np.exp(-(x / 0.006) ** 2) * cls._weich((y - yc + 0.01) / 0.03) * (1.0 - cls._weich((y - yc - 0.16) / 0.04)) * vorn
        feld -= 0.0040 * rinne
        # 3. Knie: Querfalten, hinten kräftiger (Kniekehle), vorn leichter
        yk = ymin + cls.KNIE * bein
        knie = np.sin(2.0 * np.pi * (y - yk) / 0.034 + 2.2 * np.sin(2.0 * theta)) * np.exp(-((y - yk) / 0.07) ** 2)
        feld += 0.0050 * knie * (0.5 * vorn + 1.0 * hinten)
        # 4. Saum: Stauchfalten über dem Knöchel
        s = y - ymin
        saum = np.sin(2.0 * np.pi * s / 0.042 + 1.7 * np.sin(3.0 * theta)) * np.exp(-s / 0.11) * cls._weich(s / 0.012)
        feld += 0.0040 * saum
        # 5. Weiche Unruhe über Oberschenkel und Gesäß (kein Muster erkennbar)
        feld += 0.0015 * (np.sin(26.0 * x + 9.0 * y + 3.0 * z) + np.sin(17.0 * y - 11.0 * z + 1.3)) * cls._weich((y - ymin - 0.2) / 0.3)
        feld = np.clip(feld, -cls.INNEN, cls.AUSSEN)
        return (p + n * feld[:, None]) / skala
