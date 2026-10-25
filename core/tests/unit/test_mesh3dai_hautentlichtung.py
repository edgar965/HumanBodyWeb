# -*- coding: utf-8 -*-
"""Entlichtung der Haut (25.10.2026, Edgar: „in % die Entlichtung … Default voll entlichtete haut“), ohne Karte, an Kunstdaten:

    1  Einstellung `Hautentlichtung`: Vorgabe 100, Zahlen 0–100 als Text, alles andere die Vorgabe
    2  `Hautnetz.forward(x, entlichtung)`: 1 ist bitgleich zum Aufruf ohne Wert; bei p gilt linear aus(p) = aus(1) · g^(p−1) (je Texel, bis auf die Klemme von sRGB)
    3  Prüfung „Entlichtung wie die Wahrheit“: innerhalb des Bereichs der sechs Tripo-Jobs ± Rand grün, Faktor 2 (Kunstwert) rot
    4  „Hautton der Figur“ belichtet die Figur zurück: eine Figur, die genau um g heller ist als der Eingang, hat zurückbelichtet den Ton des Eingangs
Sabotage (von Hand): in `Hautnetz.forward` `g ** (entlichtung - 1)` → `g ** entlichtung` → Fall 2 rot; `LICHT_RAND` auf 10 → Fall 3 rot; in `figur` die Rückbelichtung streichen → Fall 4 rot.
"""
import sys
import unittest
from types import SimpleNamespace

from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))
sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


def _torch():
    try:
        import torch  # noqa: F401
        return True
    except ImportError:
        return False


class HautentlichtungEinstellungTest(unittest.TestCase):
    def test_1_einstellung(self):
        from core.dienste.hautentlichtung import Hautentlichtung as H
        self.assertEqual(H.VORGABE, 100)
        self.assertEqual(H.aus({}), 100)
        self.assertEqual(H.aus({H.SCHLUESSEL: '50'}), 50)
        self.assertEqual(H.aus({H.SCHLUESSEL: 0}), 0)
        for falsch in ('-1', '101', 'abc', '2.5', None):
            self.assertEqual(H.aus({H.SCHLUESSEL: falsch}), 100, falsch)


@unittest.skipUnless(_torch(), 'kein torch')
class HautentlichtungNetzTest(unittest.TestCase):
    def test_2_netz(self):
        import torch

        from KoerperKI_alle.hautnetz import Hautnetz
        torch.manual_seed(3)
        netz = Hautnetz(8, relativ=2).eval()
        x = torch.rand((1, 15, 32, 32))
        with torch.no_grad():
            a0, t0 = netz(x)
            a1, _t = netz(x, 1.0)
            a5, _t = netz(x, 0.5)
        self.assertTrue(torch.equal(a0, a1))
        erwartet = Hautnetz.srgb(Hautnetz.linear(a0) * t0['g'] ** -0.5)
        innen = (a0 > 0.01) & (a0 < 0.99)
        self.assertLess(float((a5 - erwartet)[innen].abs().max()), 1e-4)

    def test_3_wahrheit(self):
        from mesh3dai_kostuem_hautpruefung import Kostuemhautpruefung as P
        lo, hi = P.LICHT_WAHRHEIT
        self.assertEqual(P.licht_ausserhalb({'licht_median': [1.0, 1.0, 1.0], 'entlichtung': 1.0}), [])
        self.assertEqual(P.licht_ausserhalb({'licht_median': [hi[0] * 1.05, lo[1] * 0.95, 1.0], 'entlichtung': 1.0}), [])
        self.assertEqual(P.licht_ausserhalb({'licht_median': [2.0, 2.0, 2.0], 'entlichtung': 1.0}), ['R', 'G', 'B'])

    def test_4_zurueckbelichtet(self):
        import torch
        from mesh3dai_kostuem_hautfarbe import Kostuemhautfarbe
        from mesh3dai_kostuem_hautpruefung import Kostuemhautpruefung as P

        from KoerperKI_alle.hautnetz import Hautnetz
        eingang = torch.tensor([[90.0, 70.0, 60.0]], dtype=torch.float64)
        g = torch.tensor([1.5, 1.4, 1.3], dtype=torch.float64)
        figur = 255.0 * Hautnetz.srgb(Hautnetz.linear(eingang / 255.0) * g)          # die KI hat um g entlichtet
        h = P.__new__(P)
        h.k = SimpleNamespace(t=torch)
        h.ton = Kostuemhautfarbe.lab_aus_rgb(eingang)[0]
        f = torch.tensor([[0, 1, 2]])
        h.s = SimpleNamespace(koerper_alle=(None, f, torch.tensor([0])), koerper=(None, None, figur.expand(3, 3)))
        licht = {'licht_median': g.tolist(), 'entlichtung': 1.0}
        self.assertLess(h.figur(licht)['abstand'], 0.5)
        self.assertGreater(h.figur(None)['abstand'], 10.0)


if __name__ == '__main__':
    unittest.main()
