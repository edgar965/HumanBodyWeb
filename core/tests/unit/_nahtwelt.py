# -*- coding: utf-8 -*-
"""Die Kunstwelt der Naht-Tests (11.10.2026): eine flache Haut mit quadratischem Loch und ein Stück, das es füllt.

Haut: Gitter 11 × 11 Punkte, Zelle 10 mm, in der Ebene z = 0 (Normale +z), zwei Dreiecke je Zelle; das Loch sind die 4 × 4 Zellen in der Mitte (Seite 40 mm), sein Ring die 16 Randpunkte
des Lochs gegen den Uhrzeigersinn. Stück: dieselben 16 Punkte als Rand, ein zweiter Ring `abstand_mm` weiter innen (negativ: außen, also auf der Haut), ein Mittelpunkt;
Dreiecke gegen den Uhrzeigersinn (Normale +z), `hub_mm` hebt den inneren Ring und die Mitte über die Ebene.
"""
import numpy as np


class Nahtwelt:
    N, ZELLE = 10, 0.010
    #: Zellen des Lochs: Spalten und Zeilen 3 … 6 (x, y von −20 bis +20 mm).
    LOCH = range(3, 7)

    @classmethod
    def _punkt(cls, i, j):
        return np.array([(i - cls.N // 2) * cls.ZELLE, (j - cls.N // 2) * cls.ZELLE, 0.0])

    @classmethod
    def haut(cls):
        """`(figur, loch)`: `figur = {punkte, dreiecke}` (alle Dreiecke, auch die im Loch), `loch = {dreiecke, ring, ring_punkte, verschiebung}`."""
        n = cls.N + 1
        punkte = np.array([cls._punkt(i, j) for j in range(n) for i in range(n)])
        dreiecke, im_loch = [], []
        for j in range(cls.N):
            for i in range(cls.N):
                a = j * n + i
                paar = [[a, a + 1, a + n + 1], [a, a + n + 1, a + n]]
                if i in cls.LOCH and j in cls.LOCH:
                    im_loch += [len(dreiecke), len(dreiecke) + 1]
                dreiecke += paar
        ring_punkte = cls._ring_nummern()
        figur = {'punkte': punkte, 'dreiecke': np.array(dreiecke, dtype=np.int64)}
        loch = {'dreiecke': np.array(im_loch, dtype=np.int64), 'ring': punkte[ring_punkte].copy(), 'ring_punkte': np.array(ring_punkte, dtype=np.int64), 'verschiebung': None}
        return figur, loch

    @classmethod
    def _ring_nummern(cls):
        """Nummern der 16 Randpunkte des Lochs, gegen den Uhrzeigersinn ab der Ecke unten links."""
        n = cls.N + 1
        a, b = cls.LOCH.start, cls.LOCH.stop            # 3 und 7: Punktspalten des Lochrands
        pfad = [(i, a) for i in range(a, b)] + [(b, j) for j in range(a, b)] + [(i, b) for i in range(b, a, -1)] + [(a, j) for j in range(b, a, -1)]
        return [j * n + i for i, j in pfad]

    @classmethod
    def stueck(cls, abstand_mm=5.0, hub_mm=0.0):
        """`(punkte, dreiecke)`: 16 Randpunkte (gleiche Lage wie der Ring), 16 Punkte des inneren Rings, Mitte — Dreiecke gegen den Uhrzeigersinn."""
        figur, loch = cls.haut()
        ring = loch['ring']
        halb = 0.020
        innen = ring[:, :2] * ((halb - abstand_mm / 1000.0) / halb)
        punkte = np.vstack([ring, np.column_stack([innen, np.full(len(ring), hub_mm / 1000.0)]), [[0.0, 0.0, hub_mm / 1000.0]]])
        k = len(ring)
        dreiecke = []
        for m in range(k):
            r0, r1, s0, s1 = m, (m + 1) % k, k + m, k + (m + 1) % k
            dreiecke += [[r0, r1, s1], [r0, s1, s0], [s0, s1, 2 * k]]
        return punkte, np.array(dreiecke, dtype=np.int64)
