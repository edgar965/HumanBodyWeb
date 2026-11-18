"""Haarstummel (18.11.2026, aus `Haarstraehnen` herausgelöst) — ein Kunstfall auf der Karte, keine echten
Netze. Nur auf Ansage laufen lassen (`testsuite-nur-auf-ansage`).

  test_01 `Haarstummel.weg`: kürzer als Anteil × Median der sichtbaren Längen fällt weg; Unsichtbare zählen
          weder mit noch fallen sie weg
"""
import sys
import unittest

import torch

for _pfad in (r'A:\3DTools', r'A:\3DTools\meshgenesis'):
    if _pfad not in sys.path:
        sys.path.append(_pfad)

KARTE = torch.cuda.is_available()
f64 = torch.float64


@unittest.skipUnless(KARTE, 'braucht CUDA')
class HaarstummelTest(unittest.TestCase):
    databases = []

    def test_01_median(self):
        """Längen 50, 50, 50, 12, 5 cm sichtbar, dazu 0 cm unsichtbar (zwei) → Median 50 cm, Grenze 15 cm:
        12 und 5 cm fallen weg, die Unsichtbaren nicht. Sabotage: Unsichtbare im Median mitzählen (Median
        12 cm, Grenze 3,6 cm) → 12 cm bleibt → rot."""
        from haar_Bart.haarstummel import Haarstummel
        laenge = torch.tensor([0.5, 0.5, 0.5, 0.12, 0.05, 0.0, 0.0], dtype=f64, device='cuda')
        sichtbar = torch.tensor([True] * 5 + [False] * 2, device='cuda')
        soll = [False] * 3 + [True] * 2 + [False] * 2
        self.assertEqual(Haarstummel.weg(laenge, sichtbar, 0.3).tolist(), soll)


if __name__ == '__main__':
    unittest.main()
