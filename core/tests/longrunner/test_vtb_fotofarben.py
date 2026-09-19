# -*- coding: utf-8 -*-
"""Fotofarben (Textur Stufe 2, 19.09.2026) an einem Kunstkörper — ohne Bilder, ohne GPU.

1. `Fotofarben.farben`: ein Würfel vor einer Lochkamera, das Bild links heller,
   rechts dunkler Hautton, Maske überall — die Vorderseite bekommt ihre Bildfarbe, die
   Rückseite (Tiefentest) und die Seitenflächen (streifende Sicht) nichts;
   Sabotage (Tiefentoleranz 10 m) → Rückseite bekommt Farbe → rot.
2. `Fotofarben.haut`: Hautfarbe 1, Grau/Blau/Schwarz 0.
3. `Fotofarben.mischen`: zwei Bilder, eines doppelt so hell, werden aneinander
   angeglichen (Median), das Ergebnis ist das gewichtete Mittel.
"""

import unittest

import numpy as np

from core.tests.unit._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from fotofarben import Fotofarben  # noqa: E402


def wuerfel(z=2.0, halb=0.3):
    """8 Ecken, 12 Dreiecke; Mittelpunkt bei (0, 0, z), Kamera schaut entlang +z."""
    e = np.array([[x, y, w] for x in (-halb, halb) for y in (-halb, halb) for w in (-halb, halb)], float)
    e[:, 2] += z
    f = np.array([
        [0, 1, 3], [0, 3, 2],   # x = -halb (links)
        [4, 6, 7], [4, 7, 5],   # x = +halb (rechts)
        [0, 4, 5], [0, 5, 1],   # y = -halb
        [2, 3, 7], [2, 7, 6],   # y = +halb
        [0, 2, 6], [0, 6, 4],   # z = -halb (vorn, zur Kamera)
        [1, 5, 7], [1, 7, 3],   # z = +halb (hinten)
    ])
    return e, f


class FotofarbenTest(unittest.TestCase):
    def test_1_vorderseite_sichtbar_rueckseite_nicht(self):
        try:
            import pyrender  # noqa: F401
        except ImportError:
            self.skipTest('pyrender fehlt')
        p, f = wuerfel()
        breite, hoehe = 200, 200
        rgb = np.zeros((hoehe, breite, 3), np.uint8)
        # Zwei Hauttöne (der Hautfilter lässt nur Haut durch): links hell, rechts dunkel.
        rgb[:, :100] = (210, 150, 120)
        rgb[:, 100:] = (140, 95, 75)
        maske = np.ones((hoehe, breite), bool)
        kamera = (300.0, 300.0, 100.0, 100.0)
        ff = Fotofarben(f)
        farbe, w = ff.farben(rgb, maske, p, kamera)
        vorn = p[:, 2] < 2.0
        # Ecke 0 (links vorn, Normale (−1,−1,−1)/√3: cos 0,36) und Ecke 6 (rechts vorn,
        # cos 0,65) sehen die Kamera; die Ecken 2 und 4 liegen durch die Dreiecksteilung
        # flacher (cos 0,19 < COS_AB) und zählen nicht — die Rückseite nie.
        self.assertGreater(w[0], 0)
        self.assertGreater(w[6], 0)
        self.assertTrue((w[~vorn] == 0).all(), w)
        self.assertAlmostEqual(farbe[0][0], 210 / 255, places=2)   # links: hell
        self.assertAlmostEqual(farbe[6][0], 140 / 255, places=2)   # rechts: dunkel
        # Sabotage: ohne Tiefentest bekämen auch die hinteren Ecken Farbe.
        alt = Fotofarben.TIEFE_TOLERANZ
        try:
            Fotofarben.TIEFE_TOLERANZ = 10.0
            Fotofarben.COS_AB = -1.0
            _, w2 = Fotofarben(f).farben(rgb, maske, p, kamera)
            self.assertTrue((w2[~vorn] > 0).any())
        finally:
            Fotofarben.TIEFE_TOLERANZ = alt
            Fotofarben.COS_AB = 0.35

    def test_2_hautfilter(self):
        farben = np.array([[187, 132, 103], [121, 93, 74], [128, 128, 128], [40, 60, 220], [0, 0, 0]]) / 255.0
        self.assertEqual(Fotofarben.haut(farben).tolist(), [1.0, 1.0, 0.0, 0.0, 0.0])

    def test_3_angleich_und_mittel(self):
        n = 40
        w = np.ones(n)
        a = np.tile([0.6, 0.4, 0.3], (n, 1))
        b = np.tile([0.3, 0.2, 0.15], (n, 1))   # dasselbe, halb so hell
        farbe, gewicht = Fotofarben.mischen([(a, w), (b, w)])
        self.assertTrue(np.allclose(gewicht, 2.0))
        # Nach dem Angleich liegen beide auf dem gemeinsamen Median (0,45/0,3/0,225).
        self.assertTrue(np.allclose(farbe[0], [0.45, 0.3, 0.225], atol=1e-6), farbe[0])
        leer = Fotofarben.mischen([])
        self.assertEqual(leer[0].shape, (0, 3))
