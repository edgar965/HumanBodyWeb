"""`G9meshnormalversatz.deckelfaktor`: Deckel des ganzen Versatzes je Punkt. Ohne Datenbank, ohne Karte."""
import unittest

import torch

from Genesis9.meshnormalversatz import G9meshnormalversatz


class VersatzdeckelTest(unittest.TestCase):
    databases = []

    @staticmethod
    def _neu(weg, deckel=15.0):
        w = torch.tensor(weg, dtype=torch.float64)
        return (w * G9meshnormalversatz.deckelfaktor(w, deckel)).tolist()

    def test_kleiner_weg_bleibt(self):
        self.assertEqual(self._neu([0.0, 3.0, 7.5]), [0.0, 3.0, 7.5])

    def test_grosser_weg_bleibt_unter_dem_deckel(self):
        neu = self._neu([20.0, 60.0, 500.0])
        self.assertTrue(all(w < 15.0 for w in neu))
        self.assertGreater(neu[2], 14.9)

    def test_groesserer_weg_bleibt_groesser(self):
        neu = self._neu([8.0, 12.0, 20.0, 40.0])
        self.assertEqual(neu, sorted(neu))

    def test_keine_stufe_am_knie(self):
        unten, oben = self._neu([7.4999, 7.5001])
        self.assertLess(oben - unten, 0.001)
