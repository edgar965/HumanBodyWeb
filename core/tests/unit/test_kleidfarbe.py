# -*- coding: utf-8 -*-
u"""Die Farbe je Punkt eines Kleidungsteils (`Genesis9/kleidfarbe.py`, 30.09.2026) — Bild × Farbe, wie der Browser sie
zeigt.

Ohne Daz-Bibliothek: Das Bild kommt als Kunstbild (`_bild` ersetzt), die Punkte aus einem erfundenen Netz.
"""
import unittest
from unittest import mock

import numpy as np
from Genesis9.kleidfarbe import G9kleidfarbe

#: 2 × 2 Pixel: oben Rot, Grün — unten Blau, Weiß. Die Mitten der Pixel liegen bei u, v = 0,25 / 0,75.
BILD = np.array([[[1, 0, 0], [0, 1, 0]], [[0, 0, 1], [1, 1, 1]]], dtype=np.float32)


def netz(gruppen):
    u"""Zwei Dreiecke mit sechs Punkten; `gruppen` je (ab, anzahl) in Indizes, wie `G9netzteilung` sie zählt."""
    return {'punkte': np.zeros((6, 3)),
            'dreiecke': np.array([[0, 1, 2], [3, 4, 5]]),
            'uv': np.array([[0.25, 0.75], [0.75, 0.75], [0.25, 0.25], [0.75, 0.25], [0.5, 0.5], [1.25, 0.75]]),
            'gruppen': gruppen}


class ProbeTest(unittest.TestCase):

    def test_1_die_mitte_eines_pixels_ist_seine_farbe(self):
        farbe = G9kleidfarbe._probe(BILD, np.array([[0.25, 0.75], [0.75, 0.75], [0.25, 0.25], [0.75, 0.25]]))
        np.testing.assert_allclose(farbe, [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 1]], atol=1e-6)

    def test_2_dazwischen_wird_bilinear_gemischt(self):
        farbe = G9kleidfarbe._probe(BILD, np.array([[0.5, 0.5], [0.5, 0.75]]))
        np.testing.assert_allclose(farbe, [[0.5, 0.5, 0.5], [0.5, 0.5, 0.0]], atol=1e-6)

    def test_3_die_kachel_wiederholt_sich(self):
        farbe = G9kleidfarbe._probe(BILD, np.array([[1.25, 0.75], [-0.75, 0.75], [0.25, 1.75]]))
        np.testing.assert_allclose(farbe, [[1, 0, 0], [1, 0, 0], [1, 0, 0]], atol=1e-6)

    def test_4_v_zaehlt_von_unten_wie_in_daz(self):
        oben = G9kleidfarbe._probe(BILD, np.array([[0.25, 0.75]]))
        unten = G9kleidfarbe._probe(BILD, np.array([[0.25, 0.25]]))
        self.assertGreater(float(oben[0, 0]), float(unten[0, 0]))             # Rot liegt oben


class FarbenTest(unittest.TestCase):

    def setUp(self):
        bild = mock.patch.object(G9kleidfarbe, '_bild',
                                 classmethod(lambda cls, pfad: BILD if pfad == 'a.png' else None))
        bild.start()
        self.addCleanup(bild.stop)

    def test_1_bild_mal_farbe(self):
        bilder = {'albedo': 'a.png', 'farbe': [0.5, 0.5, 0.5]}
        n = netz([{'name': 'M', 'index_ab': 0, 'index_anzahl': 3, 'bilder': bilder},
                  {'name': 'N', 'index_ab': 3, 'index_anzahl': 3, 'bilder': {}}])
        farbe = G9kleidfarbe.farben(n)
        np.testing.assert_allclose(farbe[:3], [[0.5, 0, 0], [0, 0.5, 0], [0, 0, 0.5]], atol=1e-6)

    def test_2_ohne_bild_gilt_die_farbe_und_ohne_beides_der_hautton(self):
        n = netz([{'name': 'M', 'index_ab': 0, 'index_anzahl': 3, 'bilder': {'farbe': [0.2, 0.4, 0.6]}},
                  {'name': 'N', 'index_ab': 3, 'index_anzahl': 3, 'bilder': {}}])
        farbe = G9kleidfarbe.farben(n)
        np.testing.assert_allclose(farbe[:3], [[0.2, 0.4, 0.6]] * 3, atol=1e-6)
        np.testing.assert_allclose(farbe[3:], [G9kleidfarbe.HAUT] * 3, atol=1e-6)

    def test_3_ein_bild_das_fehlt_faellt_auf_die_farbe_zurueck(self):
        bilder = {'albedo': 'gibtsnicht.png', 'farbe': [1, 0, 1]}
        n = netz([{'name': 'M', 'index_ab': 0, 'index_anzahl': 6, 'bilder': bilder}])
        np.testing.assert_allclose(G9kleidfarbe.farben(n), [[1, 0, 1]] * 6, atol=1e-6)

    def test_4_jede_gruppe_faerbt_nur_ihre_punkte(self):
        n = netz([{'name': 'M', 'index_ab': 3, 'index_anzahl': 3, 'bilder': {'albedo': 'a.png'}}])
        farbe = G9kleidfarbe.farben(n)
        np.testing.assert_allclose(farbe[:3], [G9kleidfarbe.HAUT] * 3, atol=1e-6)     # nicht in der Gruppe: Hautton
        np.testing.assert_allclose(farbe[3], [1, 1, 1], atol=1e-6)

    def test_5_form_und_typ(self):
        gruppe = {'name': 'M', 'index_ab': 0, 'index_anzahl': 6, 'bilder': {'albedo': 'a.png'}}
        farbe = G9kleidfarbe.farben(netz([gruppe]))
        self.assertEqual(farbe.shape, (6, 3))
        self.assertEqual(farbe.dtype, np.float32)
        self.assertGreaterEqual(float(farbe.min()), 0.0)
        self.assertLessEqual(float(farbe.max()), 1.0)

    def test_6_ohne_gruppen_alles_hautton(self):
        farbe = G9kleidfarbe.farben({'punkte': np.zeros((2, 3)), 'dreiecke': np.array([[0, 1, 1]]), 'uv': None})
        np.testing.assert_allclose(farbe, [G9kleidfarbe.HAUT] * 2, atol=1e-6)


class BildTest(unittest.TestCase):

    def setUp(self):
        G9kleidfarbe._bilder.clear()
        self.addCleanup(G9kleidfarbe._bilder.clear)

    def test_1_ein_unbekannter_pfad_gibt_none_mit_warnung(self):
        with mock.patch('Genesis9.material.G9material.datei', return_value=None):
            with self.assertLogs('core', level='WARNING') as log:
                self.assertIsNone(G9kleidfarbe._bild('gibtsnicht.png'))
        self.assertIn('gibtsnicht.png', log.output[0])


if __name__ == '__main__':
    unittest.main()
