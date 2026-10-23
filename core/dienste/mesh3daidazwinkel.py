# -*- coding: utf-8 -*-
"""Mesh3daidazwinkel — Daz-Gelenkwinkel aus den Knochendrehungen eines Wegs (19.10.2026 spätabends).

Edgar zu MannLaufen: „pose kaputt (Beine)“. Die Ergebnis-Figur der Jobseite (`Mesh3daigenesis`, Genesis-Figur mit dem Code von Charakter) stand in den Winkeln des Netzes DIREKT
(`<gruppe>_winkel` des Laufs, MannLaufen Probe 1 Ø 126 mm daneben), wurde aber starr auf das Rig des gewählten Wegs gelegt (Vorgabe: die Vorstufe, 6,7 mm) — Pose und Rig aus zwei Wegen,
die Beine standen falsch. Die Wege (`Mesh3daiwege`) tragen je Knochen die Drehung gegen die Ruhelage (`<weg>_dreh`), keine Winkel; hier werden sie zu Winkeln wie in
`ProjektTemp/_wegwerf/mesh3dai_kinematik.py` (`winkel_waehlen`): E = Oᵀ · D_elternᵀ · D · O, Euler in der Reihenfolge des Knochens, von den zwei Lösungen die in den Grenzen.

    Mesh3daidazwinkel.aus_drehungen(dreh (N, 3, 3), knochen aus kinematik.json) -> (N, 3) Grad (Wurzel 0)
"""
import numpy as np
from Figurfilm.dazwinkel import Dazwinkel

__all__ = ['Mesh3daidazwinkel']


class Mesh3daidazwinkel:

    @staticmethod
    def _verletzung(w, lo, hi):
        return float((np.maximum(0, lo - w) + np.maximum(0, w - hi)).sum())

    @classmethod
    def _waehlen(cls, e, reihenfolge, lo, hi):
        a = Dazwinkel.euler_winkel(e[None], reihenfolge)[0]
        o = [Dazwinkel.ACHSE[c] for c in reihenfolge.upper()]
        b = a.copy()
        b[o[0]] += 180
        b[o[1]] = 180 - b[o[1]]
        b[o[2]] += 180
        b = (b + 180) % 360 - 180
        kandidaten = []
        for w in (a, b):
            if np.abs(Dazwinkel.euler_matrix(w[None], reihenfolge)[0] - e).max() > 1e-5:
                continue
            w = w.copy()
            for i in range(3):
                if w[i] < lo[i] and w[i] + 360 <= hi[i]:
                    w[i] += 360
                elif w[i] > hi[i] and w[i] - 360 >= lo[i]:
                    w[i] -= 360
            kandidaten.append((cls._verletzung(w, lo, hi), float(np.abs(w).sum()), w))
        return min(kandidaten, key=lambda t: (t[0], t[1]))[2] if kandidaten else a

    @classmethod
    def aus_drehungen(cls, dreh, knochen):
        d = np.asarray(dreh, dtype=np.float64)
        o = Dazwinkel.euler_matrix(np.array([k['o'] for k in knochen], dtype=np.float64), 'XYZ')
        aus = np.zeros((len(knochen), 3))
        for j, k in enumerate(knochen):
            e = int(k['eltern'])
            if e < 0:
                continue
            lokal = d[e].T @ d[j]
            aus[j] = cls._waehlen(o[j].T @ lokal @ o[j], k['reihenfolge'], np.asarray(k['min'], dtype=float), np.asarray(k['max'], dtype=float))
        return aus
