"""Haarfeldgang: Haut-Abstoßung an einer offenen Anlage (18.11.2026) — ein Kunstfall auf der Karte mit
echtem `Flaechenabstand`, keine echten Netze. Nur auf Ansage laufen lassen (`testsuite-nur-auf-ansage`).

  test_01 `Haarfeldgang._aus_der_haut`: ein Quadrat in y = 0 (Normale +y) als Anlage. Nah darüber und
          darunter → auf `LIFT_M`; weit darüber bleibt; 16 mm neben der Randkante bei 1 mm Höhe bleibt
          (vorher sprang der Punkt auf die Kante, Wildmane S4 `ohr.log`); neben der Kante, aber klar
          darunter → auf die Kante + `LIFT_M`
"""
import sys
import types
import unittest

import torch

for _pfad in (r'A:\3DTools', r'A:\3DTools\meshgenesis'):
    if _pfad not in sys.path:
        sys.path.append(_pfad)

KARTE = torch.cuda.is_available()
f64 = torch.float64


def _t(werte):
    return torch.tensor(werte, dtype=f64, device='cuda')


@unittest.skipUnless(KARTE, 'braucht CUDA')
class HaarfeldgangHautTest(unittest.TestCase):
    databases = []

    def test_01_neben_dem_rand(self):
        """Quadrat 10 × 10 cm, Rand bei x = 0,05. Punkte (Abstand, Höhe in mm): innen 2 über → 4; innen
        10 unter → 4 über; innen 10 über → bleibt; 16 neben dem Rand, 1 über → bleibt; 5 neben dem Rand,
        20 unter (Höhe ÷ Abstand −0,97) → Randkante + 4 mm längs der Normale. Sabotage: Bedingung der
        alten Fassung (`Höhe < lift`) → der vierte Punkt springt auf die Kante → rot."""
        from Genesis9.rechenkarte import G9rechenkarte
        from haar_Bart.haarfeldgang import Haarfeldgang
        from KoerperKI_Fotos.flaechenabstand import Flaechenabstand
        p = _t([[-0.05, 0.0, -0.05], [0.05, 0.0, -0.05], [0.05, 0.0, 0.05], [-0.05, 0.0, 0.05]])
        d = torch.tensor([[0, 2, 1], [0, 3, 2]], device='cuda')
        g = Haarfeldgang.__new__(Haarfeldgang)
        g.m = types.SimpleNamespace(LIFT_M=0.004)
        g.haut = types.SimpleNamespace(flaeche=Flaechenabstand(G9rechenkarte.an(), p, d),
                                       fn=_t([[0.0, 1.0, 0.0]] * 2))
        x = _t([[0.0, 0.002, 0.0], [0.0, -0.010, 0.0], [0.0, 0.010, 0.0], [0.066, 0.001, 0.0],
                [0.055, -0.020, 0.0]])
        soll = _t([[0.0, 0.004, 0.0], [0.0, 0.004, 0.0], [0.0, 0.010, 0.0], [0.066, 0.001, 0.0],
                   [0.05, 0.004, 0.0]])
        aus = g._aus_der_haut(x)
        self.assertTrue(torch.allclose(aus, soll, atol=1e-9), aus.tolist())


if __name__ == '__main__':
    unittest.main()
