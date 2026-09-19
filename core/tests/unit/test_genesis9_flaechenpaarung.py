# -*- coding: utf-8 -*-
"""G9flaechenpaarung ohne Bibliothek: nächster Punkt auf dem Dreieck, Zuordnung (19.09.2026).

Die Fototextur braucht je Käfigpunkt einen Punkt AUF dem SMPL-X-Netz — mit
dem nächsten Punkt allein fielen 74 % der Käfigdreiecke auf Doppelpartner
(Mosaik). Kunstdaten:

1. `naechster_punkt` (Ericson): innen → die Anteile des Punkts selbst; über
   einer Ecke → (1, 0, 0); neben einer Kante → auf der Kante (ein Anteil 0);
   die Summe ist immer 1.
2. `zuordnen`: ein Quadrat aus zwei Dreiecken, drei Käfigpunkte mit demselben
   Partner (Ecke 0) bekommen drei VERSCHIEDENE Lagen — und `lagen` gibt sie
   zurück; ohne Partner Dreieck −1 und Lage 0.
3. Sabotage: dieselbe Zuordnung als reines Punktschnappen (Partnerlage für
   alle) fiele auf eine einzige Lage — der Test misst, dass die Flächenpaarung
   die drei trennt.
"""

import unittest

import numpy as np
from Genesis9.flaechenpaarung import G9flaechenpaarung


class FlaechenpaarungTest(unittest.TestCase):
    def setUp(self):
        self.ecken = np.array([[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]])   # (1, 3, 3)

    def test_1_naechster_punkt(self):
        innen = G9flaechenpaarung.naechster_punkt(np.array([[0.25, 0.25, 0.5]]), self.ecken)
        self.assertTrue(np.allclose(innen, [[0.5, 0.25, 0.25]]), innen)
        ecke = G9flaechenpaarung.naechster_punkt(np.array([[-1.0, -1.0, 0.0]]), self.ecken)
        self.assertTrue(np.allclose(ecke, [[1.0, 0.0, 0.0]]), ecke)
        kante = G9flaechenpaarung.naechster_punkt(np.array([[0.5, -1.0, 0.3]]), self.ecken)
        self.assertTrue(np.allclose(kante, [[0.5, 0.5, 0.0]]), kante)
        viele = G9flaechenpaarung.naechster_punkt(np.random.default_rng(1).normal(size=(20, 1, 3)),
                                                  np.repeat(self.ecken, 20, axis=0)[:, None])
        self.assertTrue(np.allclose(viele.sum(-1), 1.0))
        self.assertGreaterEqual(float(viele.min()), 0.0)

    def test_2_zuordnen_und_lagen(self):
        b = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]])
        flaechen = np.array([[0, 1, 2], [0, 2, 3]])
        a = np.array([[0.05, 0.05, 0.1], [0.3, 0.1, -0.1], [0.1, 0.3, 0.05], [5.0, 5.0, 5.0]])
        zuordnung = np.array([0, 0, 0, -1])
        dreieck, anteile = G9flaechenpaarung.zuordnen(a, zuordnung, b, flaechen)
        self.assertEqual(int(dreieck[3]), -1)
        self.assertTrue((dreieck[:3] >= 0).all())
        self.assertTrue(np.allclose(anteile[:3].sum(1), 1.0))
        f = G9flaechenpaarung(dreieck, anteile, flaechen)
        lagen = f.lagen(b)
        self.assertTrue(np.allclose(lagen[:3, :2], a[:3, :2], atol=1e-9), lagen)   # senkrecht projiziert
        self.assertTrue(np.allclose(lagen[3], 0.0))
        # Sabotage: reines Punktschnappen gäbe dreimal Ecke 0 — hier drei verschiedene Lagen.
        paarweise = [np.linalg.norm(lagen[i] - lagen[j]) for i in range(3) for j in range(i + 1, 3)]
        self.assertGreater(min(paarweise), 0.1, paarweise)
