# -*- coding: utf-8 -*-
"""Kunstflächen für die Tests des Daz-Bakes (11.10.2026): ein `Dazgeograftziel` ohne Daz-Bibliothek, gebaut aus Platten."""
import numpy as np

from core.dienste.dazgeograftziel import Dazgeograftziel


class Dazkunstziel:
    HALB = 0.020

    @classmethod
    def _leer(cls, punkte, dreiecke, uv_ecken, farbe=None):
        """Das Ziel mit diesen Daten — die Dateien der Bibliothek werden nicht gelesen. `farbe`: `(H, W, 3)` uint8 oder None."""
        ziel = Dazgeograftziel.__new__(Dazgeograftziel)
        ziel.punkte, ziel.dreiecke, ziel.uv_ecken = np.asarray(punkte, dtype=np.float64), np.asarray(dreiecke, dtype=np.int64), np.asarray(uv_ecken, dtype=np.float64)
        ziel.name, ziel._netz, ziel._farbe, ziel._proben, ziel._rand = 'Kunst', None, None, None, None
        ziel.bild = lambda kanal: farbe if kanal == 'farbe' else None
        return ziel

    @classmethod
    def zwei_platten(cls):
        """Zwei Platten 40 × 40 mm im Abstand 2 mm: die untere (z = 0, Normale +z) mit der UV links im Farbbild (rot), die obere (z = 2 mm, Normale −z) rechts (blau)."""
        a = cls.HALB
        unten = [[-a, -a, 0.0], [a, -a, 0.0], [a, a, 0.0], [-a, a, 0.0]]
        oben = [[-a, -a, 0.002], [a, -a, 0.002], [a, a, 0.002], [-a, a, 0.002]]
        links, rechts = [[0.05, 0.4], [0.45, 0.4], [0.45, 0.6], [0.05, 0.6]], [[0.55, 0.4], [0.95, 0.4], [0.95, 0.6], [0.55, 0.6]]
        uv = [[links[0], links[1], links[2]], [links[0], links[2], links[3]], [rechts[0], rechts[2], rechts[1]], [rechts[0], rechts[3], rechts[2]]]
        farbe = np.zeros((1, 2, 3), dtype=np.uint8)
        farbe[0, 0], farbe[0, 1] = (255, 0, 0), (0, 0, 255)
        return cls._leer(unten + oben, [[0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6]], uv, farbe)

    @classmethod
    def geneigte_platte(cls, grad, halb=0.060):
        """Eine Platte `2·halb` im Quadrat, um die x-Achse um `grad` geneigt (Normale +z gekippt), UV (x, y)/(2·halb) + 0,5; Farbbild: linke Hälfte rot, rechte blau (Auflösung 64 × 64)."""
        w = np.radians(grad)
        ecken = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]], dtype=np.float64) * halb
        punkte = np.column_stack([ecken[:, 0], ecken[:, 1] * np.cos(w), ecken[:, 1] * np.sin(w)])
        dreiecke = [[0, 1, 2], [0, 2, 3]]
        uv = ecken / (2 * halb) + 0.5
        farbe = np.zeros((64, 64, 3), dtype=np.uint8)
        farbe[:, :32], farbe[:, 32:] = (255, 0, 0), (0, 0, 255)
        return cls._leer(punkte, dreiecke, [uv[d] for d in dreiecke], farbe)
