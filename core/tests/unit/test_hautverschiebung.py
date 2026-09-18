# -*- coding: utf-8 -*-
"""Hautverschiebung: MB-Labs Displacement-Formel und der Displace-Modifier.

Die Formel steht in `tools/MB-Lab/materialengine.py` (`calculate_disp_pixels`):
    wert = R + alter·(G − 0,5) + tonus⁺·(B − 0,5) + (1 − tonus⁺)·masse·(A − 0,5)
Geprueft an einem 2×2-Bild von Hand, dazu Abtastung und Verschiebung.
"""

from unittest import TestCase

import numpy as np
from humanbody_core.hautverschiebung import Hautverschiebung


class Formel(TestCase):
    BILD = np.array(
        [[[0.5, 1.0, 0.0, 0.5], [0.2, 0.5, 1.0, 0.0]], [[0.9, 0.0, 0.5, 1.0], [0.5, 0.5, 0.5, 0.5]]],
        dtype=np.float32,
    )

    def test_ohne_faktoren_bleibt_die_grundhaut(self):
        t = Hautverschiebung.textur(self.BILD)
        np.testing.assert_allclose(t, [[0.5, 0.2], [0.9, 0.5]])

    def test_alter_addiert_die_falten(self):
        t = Hautverschiebung.textur(self.BILD, alter=1.0)
        # R + (G − 0,5): 0,5+0,5 = 1,0; 0,2+0 = 0,2; 0,9−0,5 = 0,4; 0,5+0 = 0,5
        np.testing.assert_allclose(t, [[1.0, 0.2], [0.4, 0.5]])

    def test_tonus_und_masse_teilen_sich_den_rest(self):
        t = Hautverschiebung.textur(self.BILD, tonus=0.5, masse=1.0)
        # tonus⁺ 0,5: + 0,5·(B − 0,5) + 0,5·1·(A − 0,5)
        erwartet = self.BILD[..., 0] + 0.5 * (self.BILD[..., 2] - 0.5) + 0.5 * (self.BILD[..., 3] - 0.5)
        # Pixel (1, 0): 0,9 + 0,25 = 1,15 → auf 1 gekappt (wie MB-Lab `fmin`).
        np.testing.assert_allclose(t, np.fmin(erwartet, 1.0))

    def test_negativer_tonus_zaehlt_nicht_und_wert_bleibt_unter_eins(self):
        t = Hautverschiebung.textur(self.BILD, alter=1.0, tonus=-1.0, masse=1.0)
        self.assertLessEqual(t.max(), 1.0)
        ohne = Hautverschiebung.textur(self.BILD, alter=1.0, tonus=0.0, masse=1.0)
        np.testing.assert_allclose(t, ohne)


class Modifier(TestCase):
    def test_abtastung_liest_unten_links_bei_uv_null(self):
        textur = np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32)
        werte = Hautverschiebung.abtasten(textur, [[0.0, 0.0], [0.0, 1.0], [0.5, 0.5]])
        np.testing.assert_allclose(werte, [1.0, 0.0, 0.5])

    def test_verschiebung_entlang_der_normale_mit_mitte(self):
        textur = np.array([[1.0, 1.0], [0.0, 0.0]], dtype=np.float32)
        punkte = np.zeros((2, 3))
        normalen = np.array([[0, 0, 1.0], [0, 0, 1.0]])
        uvs = [[0.0, 1.0], [0.0, 0.0]]  # oben = 1,0 · unten = 0,0
        aus = Hautverschiebung.anwenden(punkte, normalen, uvs, textur, staerke=0.01)
        np.testing.assert_allclose(aus[:, 2], [0.005, -0.005], atol=1e-7)

    def test_nahtkopien_bekommen_den_wert_ihres_geometriepunkts(self):
        textur = np.array([[1.0, 0.0], [1.0, 0.0]], dtype=np.float32)
        punkte = np.zeros((3, 3))
        normalen = np.tile([0, 0, 1.0], (3, 1))
        uvs = [[0.0, 0.5], [0.5, 0.5], [1.0, 0.5]]  # Kopie (Index 2) liest 0,0
        aus = Hautverschiebung.anwenden(
            punkte, normalen, uvs, textur, staerke=0.01, kopien_eltern=[0], geo_punkte=2
        )
        self.assertAlmostEqual(float(aus[2, 2]), float(aus[0, 2]), places=7)
