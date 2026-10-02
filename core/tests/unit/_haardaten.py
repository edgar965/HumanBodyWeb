# -*- coding: utf-8 -*-
"""Haardaten — die Kunstdaten der Tests der Haar-Dynamik (`test_haardynamik.py`, `test_haarstraehnen.py`, 02.10.2026): eine
Kopfhaut als Gitter, zehn Käfigpunkte mit zwei Ketten, ein Körper — klein, ohne Bibliothek und ohne Datei."""

import numpy as np

__all__ = ['Haardaten']

#: Kette A = 4 → 1 → 7 → 2 und Kette B = 9 → 0 → 5 (Wurzeln 4 und 9); die Punkte 3, 6, 8 gehören keiner Kette an.
_SEGMENTE = np.array([(4, 1), (1, 7), (7, 2), (9, 0), (0, 5)])


class Haardaten:
    class Strang:
        """Ein Strang-Teil des Käfigs: nur das, was `Haardynamik` und `G9haarzusatz.ketten` lesen."""
        ART = 'strang'
        kennung = 'geometry'
        segmente = _SEGMENTE

    class Karte:
        """Ein Teil ohne Strang (Haarkappe, Kartenhaar)."""
        ART = 'flaeche'
        kennung = 'kappe'

    SEGMENTE = _SEGMENTE
    #: Der Körper: zwei Dreiecke unter der Haut (die Attrappe des Solvers rechnet nichts damit).
    KOERPER = (np.array([(0.0, -0.5, 0.0), (1.0, -0.5, 0.0), (0.0, -0.5, 1.0), (0.0, -1.0, 0.0)]),
               np.array([(0, 1, 2), (0, 2, 3)]))

    @staticmethod
    def haut(n=21):
        """Die Kopfhaut: ein Gitter bei y = 0 (Abstand 0,1 m, Eckpunkte auch bei (0, 0) und (0,5, 0,5)), nach +y gewandt; die
        Strähnen wachsen nach oben (+y, „nach außen“). Der Abstand der Wurzel zur Haut ist der zum nächsten EckPUNKT — das Gitter
        muss dicht genug sein."""
        achse = np.linspace(-1.0, 1.0, n)
        punkte = np.array([(x, 0.0, z) for z in achse for x in achse])
        dreiecke = []
        for j in range(n - 1):
            for i in range(n - 1):
                a = j * n + i
                dreiecke += [(a, a + n + 1, a + 1), (a, a + n, a + n + 1)]
        return {'punkte': punkte, 'dreiecke': np.array(dreiecke), 'uv': None, 'quelle': 'kappe:Attrappe', 'flaeche_m2': 4.0}

    @staticmethod
    def punkte():
        """Die zehn Käfigpunkte (10, 3); Wurzel A auf 3 mm, Wurzel B auf 4 mm über der Haut."""
        p = np.zeros((10, 3))
        p[[4, 1, 7, 2]] = [(0.0, 0.003, 0.0), (0.0, 0.05, 0.0), (0.01, 0.1, 0.0), (0.02, 0.15, 0.0)]
        p[[9, 0, 5]] = [(0.5, 0.004, 0.5), (0.5, 0.05, 0.5), (0.51, 0.1, 0.5)]
        p[[3, 6, 8]] = [(0.9, 0.5, 0.9), (0.8, 0.5, 0.8), (0.7, 0.5, 0.7)]
        return p
