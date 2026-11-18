"""Gemeinsame Bausteine `KoerperKI_alle.Cpugleich`, `Festsumme`, `Vektorlaenge` (17.11.2026): auf der
Karte Wert für Wert wie dieselbe Rechnung auf der CPU — an gewürfelten Kunstwerten, ohne Figur; ohne
Karte übersprungen. Vorlage: `_wegwerf/cpugleich_probe.py` (dort auch die Zeiten).

1. `Cpugleich.summe`/`punkt`/`mittel` über Breite 1–4 bitgleich zu `sum`/`mean` der CPU (float32,
   float64); Breite 5 wirft.
2. `Cpugleich.teilen` bitgleich zu `x / zahl` der CPU (255 und das nicht darstellbare 1,055).
3. `Cpugleich.exp`/`log` (float32 über float64) bitgleich zur CPU im Bereich der Probe (0,05–0,95).
4. `Festsumme` bitgleich zu `index_add_` der CPU: Tafel und verdichtete Schritte, mit und ohne
   Anfangswert; zweimal gerechnet gleich; Ableitung wie über `index_add`.
5. `Vektorlaenge.normiert` bitgleich zu `F.normalize` der CPU; Ableitung bei Länge 0 endlich.
"""
import sys
import unittest

import torch
import torch.nn.functional as F
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_alle.cpugleich import Cpugleich  # noqa: E402
from KoerperKI_alle.festsumme import Festsumme  # noqa: E402
from KoerperKI_alle.vektorlaenge import Vektorlaenge  # noqa: E402


def gleich(karte, cpu):
    return torch.equal(karte.cpu(), cpu)


@unittest.skipUnless(torch.cuda.is_available(), 'ohne Karte nichts zu vergleichen')
class Cpugleichprobe(unittest.TestCase):

    def setUp(self):
        self.g = torch.Generator(device='cuda').manual_seed(21)

    def _r(self, *form, dtype=torch.float32):
        return torch.randn(*form, device='cuda', generator=self.g, dtype=dtype)

    def test_1_kurze_summen(self):
        for dtype in (torch.float32, torch.float64):
            for breite in (1, 2, 3, 4):
                x = self._r(20_000, breite, dtype=dtype)
                xc = x.cpu()
                self.assertTrue(gleich(Cpugleich.summe(x), xc.sum(-1)), (dtype, breite))
                lang = Cpugleich.summe(x, keepdim=True)
                self.assertTrue(gleich(lang, xc.sum(-1, keepdim=True)), (dtype, breite))
            v, w = self._r(20_000, 3, dtype=dtype), self._r(20_000, 3, dtype=dtype)
            m = self._r(20_000, 3, 3, dtype=dtype)
            self.assertTrue(gleich(Cpugleich.punkt(v, w), (v.cpu() * w.cpu()).sum(-1)), dtype)
            self.assertTrue(gleich(Cpugleich.mittel(m, 1), m.cpu().mean(1)), dtype)
        with self.assertRaises(ValueError):
            Cpugleich.summe(self._r(10, 5))

    def test_2_teilen(self):
        for dtype in (torch.float32, torch.float64):
            x = self._r(50_000, dtype=dtype)
            for zahl in (255.0, 1.055):
                self.assertTrue(gleich(Cpugleich.teilen(x, zahl), x.cpu() / zahl), (dtype, zahl))

    def test_3_exp_log(self):
        x = torch.rand(200_000, device='cuda', generator=self.g) * 0.9 + 0.05
        self.assertTrue(gleich(Cpugleich.exp(x), Cpugleich.exp(x.cpu())))
        self.assertTrue(gleich(Cpugleich.log(x), Cpugleich.log(x.cpu())))

    def test_4_festsumme(self):
        for n, m, verdichtet in ((500, 20_000, False), (2_000, 20_000, True)):
            ziel = torch.randint(0, n, (m,), device='cuda', generator=self.g)
            if verdichtet:
                ziel[::10] = 7                                                       # sehr ungleicher Grad
            werte, basis = self._r(m, 3, dtype=torch.float64), self._r(n, 3, dtype=torch.float64)
            alt = Festsumme.TAFEL_MIN
            Festsumme.TAFEL_MIN = 0 if verdichtet else alt
            try:
                fs = Festsumme(ziel, n)
            finally:
                Festsumme.TAFEL_MIN = alt
            self.assertEqual(fs.tafel is None, verdichtet)
            zc, wc = ziel.cpu(), werte.cpu()
            null = torch.zeros(n, 3, dtype=torch.float64)
            self.assertTrue(gleich(fs.summe(werte), null.index_add_(0, zc, wc)), n)
            self.assertTrue(gleich(fs.summe(werte, basis), basis.cpu().index_add_(0, zc, wc)), n)
            self.assertTrue(torch.equal(fs.summe(werte), fs.summe(werte)), n)
        werte = self._r(1000, 3, dtype=torch.float64).requires_grad_(True)
        ziel = torch.randint(0, 50, (1000,), device='cuda', generator=self.g)
        Festsumme(ziel, 50).summe(werte).pow(2).sum().backward()
        ref = werte.detach().clone().requires_grad_(True)
        torch.zeros(50, 3, dtype=torch.float64, device='cuda').index_add(0, ziel, ref).pow(2).sum().backward()
        self.assertLess(float((werte.grad - ref.grad).abs().max()), 1e-12)

    def test_5_vektorlaenge(self):
        for dtype in (torch.float32, torch.float64):
            v = self._r(20_000, 3, dtype=dtype)
            self.assertTrue(gleich(Vektorlaenge.normiert(v), F.normalize(v.cpu(), dim=-1)), dtype)
        null = torch.zeros(4, 3, device='cuda', dtype=torch.float64, requires_grad=True)
        Vektorlaenge.normiert(null).sum().backward()
        self.assertTrue(bool(torch.isfinite(null.grad).all()))


if __name__ == '__main__':
    unittest.main()
