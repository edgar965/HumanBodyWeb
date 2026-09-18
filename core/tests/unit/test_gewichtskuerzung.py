# -*- coding: utf-8 -*-
"""`CatmullClarkSubdivider.propagate_skin_weights` — nach der Vektorisierung
(17.09.2026): je Vertex hoechstens vier Knochen, die staerksten zuerst,
Winzgewichte fallen weg, die Summe ist wieder 1, leere Zeilen bleiben leer.

An einem Viereck (vier Basispunkte) mit einer Stufe: Der Flaechenpunkt
mischt alle vier Ecken zu je 1/4 — mit sechs Knochen an den Ecken bleiben
ihm nur die vier staerksten.
"""

from unittest import TestCase

import numpy as np
from humanbody_core.catmull_clark import CatmullClarkSubdivider


class Kuerzung(TestCase):
    def setUp(self):
        self.cc = CatmullClarkSubdivider(np.array([[0, 1, 2, 3]]), levels=1)
        self.namen = ['a', 'b', 'c', 'd', 'e', 'f']

    def test_hoechstens_vier_die_staerksten_zuerst_und_summe_eins(self):
        basis = [[[0, 0.5], [1, 0.5]], [[2, 0.7], [3, 0.3]], [[4, 1.0]], [[5, 0.9], [0, 0.1]]]
        aus = self.cc.propagate_skin_weights(basis, self.namen)
        self.assertEqual(aus['vertex_count'], self.cc.sub_vertex_count)
        flaeche = aus['weights'][4]  # Zeile N_v = Flaechenpunkt
        self.assertEqual(len(flaeche), 4)
        for zeile in aus['weights']:
            werte = [w for _k, w in zeile]
            self.assertLessEqual(len(zeile), 4)
            self.assertEqual(werte, sorted(werte, reverse=True))
            self.assertAlmostEqual(sum(werte), 1.0, places=5)
        # Die Ecke ist ein Randpunkt: (b1 + b2 + 6P)/8 — Knochen 0 fuehrt.
        self.assertEqual(aus['weights'][0][0][0], 0)

    def test_winzgewichte_fallen_weg_und_leere_zeilen_bleiben_leer(self):
        # Ecke 0 bekommt 1/8 von Ecke 1: 0,0004/8 liegt unter MINDESTGEWICHT.
        basis = [[[0, 1.0]], [[1, 1.0 - 0.0004], [5, 0.0004]], [[2, 1.0]], [[3, 1.0]]]
        aus = self.cc.propagate_skin_weights(basis, self.namen)
        self.assertNotIn(5, [k for k, _w in aus['weights'][0]])
        self.assertIn(5, [k for k, _w in aus['weights'][1]])
        leer = self.cc.propagate_skin_weights([[], [], [], []], self.namen)
        self.assertEqual(leer['weights'], [[] for _ in range(self.cc.sub_vertex_count)])
