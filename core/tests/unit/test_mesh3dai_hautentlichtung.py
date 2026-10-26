# -*- coding: utf-8 -*-
"""Entlichtung der Haut (25.10.2026, Edgar: „in % die Entlichtung … Default voll entlichtete haut“), ohne Karte, an Kunstdaten:

    1  Einstellung `Hautentlichtung`: Vorgabe 100, Zahlen 0–100 als Text, alles andere die Vorgabe
    2  `Hautnetz.forward(x, entlichtung)`: 1 ist bitgleich zum Aufruf ohne Wert; bei p gilt linear aus(p) = aus(1) · g^(p−1) (je Texel, bis auf die Klemme von sRGB)
    3  Prüfung „Entlichtung wie die Wahrheit“: innerhalb des Bereichs der sechs Tripo-Jobs ± Rand grün, Faktor 2 (Kunstwert) rot
    4  „Hautton der Figur“ belichtet die Figur zurück: eine Figur, die genau um g heller ist als der Eingang, hat zurückbelichtet den Ton des Eingangs; ohne Rückbelichtung
       wäre sie rot (g 2,5/2,2/2,0 an sRGB 90/70/60: ΔE76 17,1, unabhängig nachgerechnet 25.10.2026 `_wegwerf/haut_ki/delta_e_gegenprobe.py`; g 1,5/1,4/1,3 gäbe nur 7,1)
    5  Mit Ton-KI prüft „Entlichtung wie die Wahrheit“ nur g der Haut-KI (`licht_hautki_median`), nicht g · Faktor; ohne getrenntes g: nicht geprüft (Prüfung Fassung 22)
    6  „Ton links wie rechts“ (`Kostuemhautseiten.paare`): gleiche Töne → 0, ein abweichendes Ohr → nur das Paar Ohr über 0
Sabotage (von Hand): in `Hautnetz.forward` `g ** (entlichtung - 1)` → `g ** entlichtung` → Fall 2 rot; `LICHT_RAND` auf 10 → Fall 3 rot; in `figur` die Rückbelichtung streichen → Fall 4 rot;
in `licht_der_haut_ki` immer `licht_median` → Fall 5 rot; in `paare` `_rechts` durch `_links` ersetzen → Fall 6 rot.
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
        g = torch.tensor([2.5, 2.2, 2.0], dtype=torch.float64)
        figur = 255.0 * Hautnetz.srgb(Hautnetz.linear(eingang / 255.0) * g)          # die KI hat um g entlichtet
        h = P.__new__(P)
        h.k = SimpleNamespace(t=torch)
        h.ton = Kostuemhautfarbe.lab_aus_rgb(eingang)[0]
        f = torch.tensor([[0, 1, 2]])
        h.s = SimpleNamespace(koerper_alle=(None, f, torch.tensor([0])), koerper=(None, None, figur.expand(3, 3)))
        licht = {'licht_median': g.tolist(), 'entlichtung': 1.0}
        self.assertLess(h.figur(licht)['abstand'], 0.5)
        self.assertGreater(h.figur(None)['abstand'], P.HAUTTON_MAX)

    def test_5_licht_der_haut_ki(self):
        from mesh3dai_kostuem_hautpruefung import Kostuemhautpruefung as P
        gesamt, g = [2.4, 2.9, 3.1], [1.05, 0.88, 0.83]
        self.assertEqual(P.licht_der_haut_ki({'licht': {'licht_median': g}}), g)
        self.assertEqual(P.licht_der_haut_ki({'licht': {'licht_median': gesamt, 'licht_hautki_median': g}, 'hautton': {'lauf': 'x'}}), g)
        self.assertIsNone(P.licht_der_haut_ki({'licht': {'licht_median': gesamt}, 'hautton': {'lauf': 'x'}}))
        self.assertIsNone(P.licht_der_haut_ki({}))

    def test_6_ton_links_wie_rechts(self):
        import torch
        from mesh3dai_kostuem_hautseiten import Kostuemhautseiten as S

        from KoerperKI_alle.hautteilkarte import Hautteilkarte
        teile = Hautteilkarte.TEILE
        toene = torch.full((len(teile), 3), 0.3, dtype=torch.float64)
        self.assertEqual(set(S.paare(toene, teile).values()), {0.0})
        toene[teile.index('ohr_rechts')] = torch.tensor([0.05, 0.04, 0.03], dtype=torch.float64)
        p = S.paare(toene, teile)
        self.assertGreater(p['ohr'], 10.0)
        self.assertEqual({k for k, v in p.items() if v > 0}, {'ohr'})


if __name__ == '__main__':
    unittest.main()
