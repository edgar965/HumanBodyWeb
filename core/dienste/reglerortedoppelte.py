# -*- coding: utf-8 -*-
"""Reglerortedoppelte — welche Regler dieselbe Wirkung haben, streng gemessen (18.10.2026, für `Reglerortebau`).

WARUM STRENG: Die erste Inventur verglich Felder per Kosinus nach Abzug von Verschiebung und Skalierung und meldete 83 Überzählige. Die
Stichprobe widerlegte das (`ProjektTemp/_wegwerf/regler_inventur/stichprobe.py`): MB Allyne und MB Olesia haben cos 0,993, liegen aber bis 19,6 mm
auseinander; eine Gruppe entstand nur über eine Kette (roher cos −0,42). Hier zählen die ROHEN Felder (4.000 Punkte, je Regler am Anschlag mit der
größten Wirkung), und eine Zusammenlegung braucht die Lage in Millimetern, nicht nur die Richtung:

    Alias     |cos| ≥ 0,98, Feld x ≈ c · Feld y mit max|x − c·y| < 0,5 mm am Anschlag, UND an den Stützstellen 25/50/75 % gilt x(w) ≈ y(w × faktor)
              bis auf 0,5 mm → faktor = c · ende_y / ende_x (c > 0; c < 0 wird ein Paar). Paarweise statt „jeder für sich linear“: eine Drehung
              (Arms Up-Down, Hip Bend) verschiebt nicht linear, zwei Kanäle derselben Drehung sind trotzdem an jeder Stelle gleich (erster Lauf
              18.10.2026: 6 von 96 fielen an der Einzelprüfung, darunter „Hip Bend“ = „Hip Bend Forward“).
    Paar      cos ≤ −0,98 und Stärke 0,8 … 1,25 — Gegenstücke wie „Ears Move Backward/Forward“: ein zweiseitiger Regler, jede Seite ihr eigener Morph
              (dafür braucht es keine Linearität)

„Ähnlich“ (|cos| ≥ 0,98, aber Millimeter auseinander) wird NICHT zusammengelegt — das wäre verlorene Wirkung.
"""

import numpy as np

__all__ = ['Reglerortedoppelte']


class Reglerortedoppelte:
    COS = 0.98
    GLEICH_MM = 0.5
    MIN_MM = 0.5
    STAERKE = (0.8, 1.25)
    STUETZEN = (0.25, 0.5, 0.75)

    def __init__(self, messung, melden=None):
        self.messung = messung
        self.melden = melden

    def bauen(self, kandidaten):
        """`kandidaten`: `[{name, ende, feld, mm}]` → (aliase, paare, linear) für `G9reglerorte`."""
        # Ein Feld, das auf den 4.000 Stichprobenpunkten 0 ist (Wirkung nur zwischen ihnen), hat keine Richtung — sonst 0/0 im Kosinus.
        wahl = [k for k in kandidaten if k['mm'] >= self.MIN_MM and k.get('feld') is not None and np.any(k['feld'])]
        if len(wahl) < 2:
            return [], [], {}
        f = np.stack([np.asarray(k['feld'], dtype=np.float64).ravel() for k in wahl])
        norm = np.linalg.norm(f, axis=1)
        g = (f / norm[:, None]) @ (f / norm[:, None]).T
        oben = np.triu(np.abs(g) >= self.COS, 1)
        aliasse, paare, linear = [], [], {}
        for i, j in np.argwhere(oben):
            a, b = wahl[i], wahl[j]
            if g[i, j] <= -self.COS:
                if self.STAERKE[0] <= norm[i] / norm[j] <= self.STAERKE[1]:
                    paare.append([a['name'], b['name'], round(float(g[i, j]), 4)])
                continue
            c = float(f[i] @ f[j] / (f[j] @ f[j]))           # Feld a ≈ c · Feld b
            rest = float(np.linalg.norm((f[i] - c * f[j]).reshape(-1, 3), axis=1).max()) * 1000.0
            if rest >= self.GLEICH_MM:
                continue
            faktor = c * float(b['ende']) / float(a['ende'])
            abweichung = self.abweichung(a, b, faktor)
            linear['%s|%s' % (a['name'], b['name'])] = round(abweichung, 3)
            if abweichung >= self.GLEICH_MM:
                continue
            aliasse.append([a['name'], b['name'], faktor, round(rest, 3)])
        if self.melden:
            self.melden('Doppelte: %d Alias-Paare, %d Gegenstücke, %d Paare an Stützstellen geprüft' % (len(aliasse), len(paare), len(linear)))
        return aliasse, paare, linear

    def abweichung(self, a, b, faktor):
        """Größte Abweichung (mm) zwischen a(w) und b(w × faktor) an den Stützstellen w = 25/50/75 % von a's Anschlag."""
        schlechteste = 0.0
        for t in self.STUETZEN:
            w = float(a['ende']) * t
            fa = self.messung.messen({a['name']: w})['feld'].astype(np.float64)
            fb = self.messung.messen({b['name']: w * faktor})['feld'].astype(np.float64)
            schlechteste = max(schlechteste, float(np.linalg.norm(fa - fb, axis=1).max()) * 1000.0)
        return schlechteste
