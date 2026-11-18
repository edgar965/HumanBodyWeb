"""Haarrezept Fassung 11: vielfach genommene Vorlagelinien (18.11.2026) — kleine Kunstfälle auf der Karte,
keine echten Netze. Nur auf Ansage laufen lassen (`testsuite-nur-auf-ansage`). Fortsetzung von
`test_haarrezept_kurven.py` (test_18–30).

  test_31 `Haarwurzeldichte.vielfach`: vielfach genommene Linie dünner, übrige und Kurven ohne Linie
          unverändert
  test_32 `Haarrezeptkappe.wahl`: über `K` × Median behält eine Linie die stärksten Punkte, die übrigen
          nehmen eine andere Linie, wenn sie eine haben
"""
import sys
import unittest

import torch

for _pfad in (r'A:\3DTools', r'A:\3DTools\meshgenesis'):
    if _pfad not in sys.path:
        sys.path.append(_pfad)

KARTE = torch.cuda.is_available()
f64 = torch.float64


def _voll(n, wert):
    return torch.full((n,), wert, dtype=f64, device='cuda')


@unittest.skipUnless(KARTE, 'braucht CUDA')
class HaarrezeptVielfachTest(unittest.TestCase):
    databases = []

    def test_31_vielfach(self):
        """`Haarwurzeldichte.vielfach` mit `VIELFACH_K` 1: 6 Linien; 10 Kurven nehmen Linie 0, je 2 die
        Linien 1–5, eine Kurve keine (Spitze daneben) → Median 2, die zehn tragen Dichte × 0,2, die
        übrigen unverändert; `anwenden` nur für die ersten fünf → nur diese dünner; `VIELFACH_K` 2 →
        × 0,4; `VIELFACH` aus → unverändert. Sabotage: `m / v` → `v / m` → rot."""
        from haar_Bart.haarwurzeldichte import Haarwurzeldichte as W
        t = torch.linspace(0.0, 1.0, 17, dtype=f64, device='cuda')
        li = torch.stack([torch.stack([0.05 * i + 0.0 * t, -0.2 * t, torch.zeros_like(t)], 1)
                          for i in range(6)])
        welche = torch.tensor([0] * 10 + [1, 1, 2, 2, 3, 3, 4, 4, 5, 5], device='cuda')
        spitzen = torch.cat([li[welche, -1], torch.tensor([[0.5, 0.5, 0.5]], dtype=f64, device='cuda')])
        dichte = _voll(21, 0.8)
        alt = (W.VIELFACH, W.VIELFACH_K)
        try:
            W.VIELFACH_K = 1.0
            d = W.vielfach(dichte, spitzen, li)
            self.assertTrue(torch.allclose(d[:10], _voll(10, 0.16)))
            self.assertTrue(torch.equal(d[10:], dichte[10:]))
            an = torch.arange(21, device='cuda') < 5
            d = W.vielfach(dichte, spitzen, li, an)
            self.assertTrue(torch.allclose(d[:5], _voll(5, 0.16)) and torch.equal(d[5:], dichte[5:]))
            W.VIELFACH_K = 2.0
            self.assertTrue(torch.allclose(W.vielfach(dichte, spitzen, li)[:10], _voll(10, 0.32)))
            W.VIELFACH = False
            self.assertTrue(torch.equal(W.vielfach(dichte, spitzen, li), dichte))
        finally:
            W.VIELFACH, W.VIELFACH_K = alt

    def test_32_kappe(self):
        """`Haarrezeptkappe.wahl` mit `K` 2: Punkte 0–9 haben ihren stärksten Kandidaten auf Linie 0
        (Gewicht fallend), den zweiten auf Linie 11 (Punkt 9 keinen); Punkte 10–29 je zu zweit auf den
        Linien 1–10; Punkt 30 ohne Kandidaten → Median 2, Grenze 4: Punkte 0–3 behalten Linie 0, 4–8
        nehmen Linie 11, 9 bleibt (keine andere), alle übrigen den stärksten; `K` None → überall der
        stärkste. Sabotage: `rang >= cls.K * m` → `rang < cls.K * m` → rot."""
        from haar_Bart.haarrezeptkappe import Haarrezeptkappe as K
        i = torch.arange(31, device='cuda')
        w = torch.zeros((31, 2), dtype=f64, device='cuda')
        w[:10, 0] = 1.0 - 0.05 * i[:10].double()
        w[:9, 1] = 0.3
        w[10:30, 0] = 1.0
        linie = torch.zeros((31, 2), dtype=torch.long, device='cuda')
        linie[:10, 1] = 11
        linie[10:30, 0] = 1 + (i[10:30] - 10) // 2
        alt = K.K
        try:
            K.K = 2.0
            self.assertEqual(K.wahl(w, linie, 12).tolist(), [0] * 4 + [1] * 5 + [0] * 22)
            K.K = None
            self.assertEqual(K.wahl(w, linie, 12).tolist(), [0] * 31)
        finally:
            K.K = alt


if __name__ == '__main__':
    unittest.main()
