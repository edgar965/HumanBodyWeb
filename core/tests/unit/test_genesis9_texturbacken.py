# -*- coding: utf-8 -*-
"""G9texturbacken ohne Bibliothek: Dreieck rastern, Rand ziehen, Tönung (19.09.2026).

1. `_dreieck`: ein Dreieck mit drei Eckfarben füllt seine Pixel, Gouraud in der
   Mitte, außerhalb bleibt 0; Deckung ebenso.
2. `rand_ziehen`: ungemalte Pixel bis `RAND_PX` bekommen die nächste gemalte Farbe,
   weiter entfernte nicht.
3. `getoent`: eine graue Albedo wird auf den Fototon gezogen (Mittel = Fototon),
   Faktor auf `TON_GRENZEN` begrenzt.
"""

import unittest

import numpy as np
from Genesis9.texturbacken import G9texturbacken


class TexturbackenTest(unittest.TestCase):
    def test_1_dreieck_gouraud(self):
        rgb = np.zeros((64, 64, 3))
        alpha = np.zeros((64, 64))
        ecken = np.array([[8.0, 8.0], [56.0, 8.0], [8.0, 56.0]])   # v nach oben: Zeile = 64 - v
        farbe = np.array([[1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0]])
        G9texturbacken._dreieck(rgb, alpha, ecken, farbe, np.array([1.0, 1.0, 0.0]))
        # Ecke 0 liegt bei Pixel (x 8, Zeile 56): rot, Deckung 1
        self.assertGreater(rgb[55, 9, 0], 0.8)
        self.assertGreater(alpha[55, 9], 0.9)
        # Schwerpunkt: Mischung aller drei
        s = rgb[64 - 24, 24]
        self.assertTrue((s > 0.15).all(), s)
        self.assertAlmostEqual(float(alpha[64 - 24, 24]), 2 / 3, delta=0.05)
        # Außerhalb (rechts oben) nichts
        self.assertEqual(float(rgb[5, 60].sum()), 0.0)
        self.assertEqual(float(alpha[5, 60]), 0.0)

    def test_2_rand_ziehen(self):
        b = G9texturbacken()
        rgb = np.zeros((40, 40, 3))
        alpha = np.zeros((40, 40))
        rgb[10:20, 10:20] = [0.2, 0.5, 0.9]
        alpha[10:20, 10:20] = 1.0
        rgb, alpha = b.rand_ziehen(rgb, alpha, alpha > 0)
        self.assertTrue(np.allclose(rgb[20 + b.RAND_PX - 1, 15], [0.2, 0.5, 0.9]))
        self.assertEqual(float(alpha[20 + b.RAND_PX - 1, 15]), 1.0)
        self.assertEqual(float(rgb[20 + b.RAND_PX + 2, 15].sum()), 0.0)

    def test_3_toenung(self):
        b = G9texturbacken()
        albedo = np.full((8, 8, 3), 0.5)
        aus = b.getoent(albedo, [187, 132, 103])
        self.assertTrue(np.allclose(aus.reshape(-1, 3).mean(0) * 255, [187, 132, 103], atol=1.0), aus[0, 0] * 255)
        # Grenze: Schwarz kann nicht auf Hautton gehoben werden (Faktor ≤ 2,5).
        dunkel = b.getoent(np.full((4, 4, 3), 0.02), [187, 132, 103])
        self.assertLess(float(dunkel.max()), 0.2)
        self.assertIs(b.getoent(albedo, None), albedo)
