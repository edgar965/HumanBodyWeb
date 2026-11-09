"""`Fotosegmentablage._ausgabe`: Häkchen „Keine Kleider“ macht die Kleidung der Fotos zu Haut, Haar und Bart bleiben. Ohne Karte, ohne Modelle."""
import unittest

import torch

from KopfKI.fotosegmentablage import Fotosegmentablage


class OhneKleiderTest(unittest.TestCase):
    databases = []

    def setUp(self):
        self.addCleanup(setattr, Fotosegmentablage, 'ohne_kleider', False)
        self.ablage = Fotosegmentablage.__new__(Fotosegmentablage)
        leer = torch.zeros((1, 5), dtype=torch.bool)
        self.e = {'person': leer.clone(), 'haar': leer.clone(), 'bart': leer.clone(), 'haut': leer.clone()}
        self.e['person'][0, :4] = True          # Spalten: Haar, Bart, Haut, Kleidung, außerhalb
        self.e['haar'][0, 0] = True
        self.e['bart'][0, 1] = True
        self.e['haut'][0, 2] = True

    def test_ohne_wahl_bleibt_das_ergebnis(self):
        self.assertIs(self.ablage._ausgabe(self.e), self.e)

    def test_kleidung_wird_haut(self):
        Fotosegmentablage.ohne_kleider = True
        haut = self.ablage._ausgabe(self.e)['haut'][0].tolist()
        self.assertEqual(haut, [False, False, True, True, False])

    def test_ablage_bleibt_unberuehrt(self):
        Fotosegmentablage.ohne_kleider = True
        self.ablage._ausgabe(self.e)
        self.assertEqual(self.e['haut'][0].tolist(), [False, False, True, False, False])
