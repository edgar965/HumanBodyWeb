# -*- coding: utf-8 -*-
"""Bausteine der Haut-Maske auf der Karte (18.11.2026, `core/dienste/hautkarte*.py`, Edgar: „Hautverdeckung auf GPU, alles auf GPU!“).

Gegen den Worker im Browser verglichen: `_wegwerf/hautkarte_vergleich.js` (seratin + GC FemSuit Double Breasted, deckend, durchsichtig und als Ersatzstück:
alle Felder bitgleich). Hier ohne Browser: das Feldpaket hin und zurück, `Hautkartewege` an einem Streifen mit bekannten Wegen (Naht mit doppelten Punkten
verbunden, Reichweite), `hypot` wie `Math.hypot`. Braucht die Grafikkarte (sonst übersprungen). Nicht gelaufen — läuft nur auf Ansage.
Sabotage: in `Hautkartewege.kanten` die Nähte weglassen → `test_2` rot; in `Feldpaket._rund` auf 4 statt 8 Bytes runden → `test_1` rot.
"""
import unittest

import torch


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class HautkarteTest(unittest.TestCase):

    def test_1_feldpaket_hin_und_zurueck(self):
        from core.daten.feldpaket import Feldpaket
        g = torch.device('cuda')
        objekt = {'maske': torch.tensor([0, 1, 1], dtype=torch.uint8, device=g), 'werte': torch.tensor([1.5, -2.25], dtype=torch.float32, device=g),
                  'liste': [torch.tensor([3.0], dtype=torch.float64, device=g), None], 'zahl': 7, 'text': 'ä'}
        zurueck = Feldpaket.entpacken(Feldpaket.packen(objekt))
        self.assertTrue(torch.equal(zurueck['maske'], objekt['maske']))
        self.assertTrue(torch.equal(zurueck['werte'], objekt['werte']))
        self.assertTrue(torch.equal(zurueck['liste'][0], objekt['liste'][0]))
        self.assertIsNone(zurueck['liste'][1])
        self.assertEqual((zurueck['zahl'], zurueck['text']), (7, 'ä'))

    def test_2_wege_ueber_naht_und_reichweite(self):
        u"""Zwei Dreiecksstreifen, an x = 1 mit doppelten Punkten (Naht) aneinander: von Punkt 0 aus über die Naht weiter, jenseits der Reichweite inf."""
        from core.dienste.hautkartewege import Hautkartewege
        g = torch.device('cuda')
        P = torch.tensor([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0],          # linker Streifen
                          [1, 0, 0], [2, 0, 0], [1, 1, 0], [2, 1, 0]],         # rechter, Punkte 4 und 6 doppelt zu 1 und 3
                         dtype=torch.float64, device=g)
        T = torch.tensor([[0, 1, 2], [1, 3, 2], [4, 5, 6], [5, 7, 6]], dtype=torch.int64, device=g)
        quelle = torch.zeros(8, dtype=torch.bool, device=g)
        quelle[0] = True
        weg = Hautkartewege.wege(P, T, quelle, 1.5)
        self.assertEqual(weg[1].item(), 1.0)
        self.assertEqual(weg[4].item(), 1.0)                                   # über die Naht (Länge 0)
        self.assertEqual(weg[5].item(), 2.0 if 2.0 <= 1.5 else float('inf'))   # jenseits der Reichweite
        self.assertAlmostEqual(weg[3].item(), 2 ** 0.5, places=15)

    def test_3_hypot_wie_math_hypot(self):
        from core.dienste.hautkartewege import Hautkartewege
        g = torch.device('cuda')
        x = torch.tensor([3.0, 0.0, -1e-200, 1e200], dtype=torch.float64, device=g)
        y = torch.tensor([4.0, 0.0, 1e-200, 1e200], dtype=torch.float64, device=g)
        z = torch.tensor([0.0, 0.0, 0.0, 0.0], dtype=torch.float64, device=g)
        h = Hautkartewege.hypot(x, y, z).tolist()
        self.assertEqual(h[0], 5.0)
        self.assertEqual(h[1], 0.0)
        self.assertGreater(h[2], 0.0)                                          # kein Unterlauf
        self.assertTrue(h[3] < float('inf'))                                   # kein Überlauf


if __name__ == '__main__':
    unittest.main()
