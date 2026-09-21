# -*- coding: utf-8 -*-
"""Hautverschiebung für das Bildmodell: Metawerte wie HumanBody, nächster Punkt auf Dreiecken,
UV an Nähten je Ecke (21.09.2026). Kunstfiguren, kein Netz, keine Datenbank."""
import unittest

import numpy as np

from core.dienste.bildmodellhautverschiebung import Bildmodellhautverschiebung
from core.dienste.hbdreiecksuche import Hbdreiecksuche


class MetawerteTest(unittest.TestCase):
    databases = []

    def test_mitte_und_raender(self):
        w = Bildmodellhautverschiebung.metawerte({'alter': 59, 'gewicht_kg': 122.5, 'tonus': 50})
        self.assertEqual(w, {'age': 0.0, 'mass': 0.0, 'tone': 0.0})
        w = Bildmodellhautverschiebung.metawerte({'alter': 100, 'gewicht_kg': 45, 'tonus': 100})
        self.assertEqual(w, {'age': 1.0, 'mass': -1.0, 'tone': 1.0})

    def test_fehlend_und_geklemmt(self):
        w = Bildmodellhautverschiebung.metawerte({'alter': 5, 'gewicht_kg': None})
        self.assertEqual(w, {'age': -1.0, 'mass': 0.0, 'tone': 0.0})
        self.assertEqual(Bildmodellhautverschiebung.metawerte(None), {'age': 0.0, 'mass': 0.0, 'tone': 0.0})

    def test_gleich(self):
        person = {'alter': 28, 'gewicht_kg': 58, 'tonus': 70}
        bericht = dict(Bildmodellhautverschiebung.metawerte(person), dauer_s=3)
        self.assertTrue(Bildmodellhautverschiebung.gleich(person, bericht))
        self.assertFalse(Bildmodellhautverschiebung.gleich(dict(person, tonus=71), bericht))
        self.assertFalse(Bildmodellhautverschiebung.gleich(person, None))


class DreiecksucheTest(unittest.TestCase):
    databases = []

    def setUp(self):
        # Zwei Dreiecke in der Ebene z = 0, UV je Ecke — das zweite mit eigener Insel (v + 10).
        self.punkte = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]], dtype=float)
        self.ecken = np.array([[0, 1, 2], [1, 3, 2]])
        self.uvs = np.array([[[0, 0], [1, 0], [0, 1]], [[1, 10], [1, 11], [0, 11]]], dtype=float)

    def test_naechster_innen_kante_ecke(self):
        d = self.punkte[self.ecken[[0, 0, 0]]]
        p = np.array([[0.25, 0.25, 0.7], [0.5, -1.0, 0.0], [-1.0, -1.0, 0.0]])
        b, d2 = Hbdreiecksuche.naechster(p, d)
        np.testing.assert_allclose(b[0], [0.5, 0.25, 0.25], atol=1e-9)
        self.assertAlmostEqual(d2[0], 0.49)
        np.testing.assert_allclose(b[1], [0.5, 0.5, 0.0], atol=1e-9)   # Fußpunkt auf Kante AB
        self.assertAlmostEqual(d2[1], 1.0)
        np.testing.assert_allclose(b[2], [1.0, 0.0, 0.0], atol=1e-9)   # Ecke A
        self.assertAlmostEqual(d2[2], 2.0)

    def test_uv_je_insel(self):
        suche = Hbdreiecksuche(self.punkte, self.ecken, self.uvs)
        uv, abstand = suche.uv(np.array([[0.2, 0.2, 0.1], [0.8, 0.8, -0.1]]))
        np.testing.assert_allclose(uv[0], [0.2, 0.2], atol=1e-9)
        np.testing.assert_allclose(uv[1], [0.8, 10.8], atol=1e-9)   # zweite Insel, nicht gemittelt
        np.testing.assert_allclose(abstand, [0.1, 0.1], atol=1e-9)


if __name__ == '__main__':
    unittest.main()
