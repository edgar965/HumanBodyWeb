"""Saummaß mit ausgeglichenem Kern (`Kostuemsaumausgleich`, `Kostuemsaumkurve`) und Sicht-Hautmaske der Eigen-Stücke (`Eigensichtmaske`) — 16.11.2026, Edgar zur Goldprinzessin:
„mach weiter“ (Zacken am Rand, Verdecktes Stück ergänzt).

Kunstdaten auf der Karte (ohne Karte übersprungen), keine echten Netze. Schreibt nichts.

Sabotage, je Fall rot:
  - in `Kostuemsaumausgleich.kurve` `(1 - (1 - k) ** 2)` durch `k` → test_1 (glatter Kreis misst wieder ~0,9 mm).
  - in `Kostuemsaumausgleich.kurve` den Kern durch 1 ersetzen → test_2 (Sägezahn verschwindet aus dem Maß).
  - in `Kostuemsaumkurve._breite` `math.sqrt(schwund)` durch `schwund` → test_3 (Breite wie beim alten Kern).
  - in `Eigensichtmaske.verborgen` `self.ohne & ~self._ringe(mit)` durch `self.ohne & ~mit` → test_5 (Rand der offenen Schale verborgen).

Geschrieben am 16.11.2026, nicht gelaufen (Tests nur auf Ansage).
"""
import math
import sys
from pathlib import Path
from unittest import skipUnless

import torch
from django.conf import settings
from django.test import SimpleTestCase

for _pfad in (str(Path(settings.TOOLS_ROOT) / 'meshgenesis'), str(Path(settings.TOOLS_ROOT))):
    if _pfad not in sys.path:
        sys.path.insert(0, _pfad)

KARTE = torch.cuda.is_available()


def _schleife(a_mm, b_mm, n, zahn_mm=0.0):
    t = torch.linspace(0, 2 * math.pi, n + 1, dtype=torch.float64, device='cuda')[:-1]
    p = torch.stack([a_mm * torch.cos(t), b_mm * torch.sin(t), torch.zeros_like(t)], 1)
    r = torch.nn.functional.normalize(torch.stack([b_mm * torch.cos(t), a_mm * torch.sin(t), torch.zeros_like(t)], 1), dim=1)
    return (p + r * zahn_mm * (torch.arange(n, device='cuda') % 2)[:, None].double()) / 1000


def _zacken(cls, p):
    an, _laenge, _glatt = cls.glaetten(p)
    return float(torch.quantile((p - an).norm(dim=1) * 1000, 0.95))


def _kugel(r, n=24, m=48, mitte=(0.0, 0.0, 0.0), bis=math.pi):
    """UV-Kugel (Radius r, n Ringe bis Polwinkel `bis`, m Segmente) → Punkte, Dreiecke; bis < π: offene Schale."""
    th = torch.linspace(0, bis, n + 1, dtype=torch.float64, device='cuda')
    ph = torch.linspace(0, 2 * math.pi, m + 1, dtype=torch.float64, device='cuda')[:-1]
    tt, pp = torch.meshgrid(th, ph, indexing='ij')
    p = torch.stack([r * torch.sin(tt) * torch.cos(pp), r * torch.cos(tt), r * torch.sin(tt) * torch.sin(pp)], -1).reshape(-1, 3) + torch.tensor(mitte, dtype=torch.float64, device='cuda')
    i = torch.arange(n, device='cuda')[:, None] * m
    j = torch.arange(m, device='cuda')[None]
    a, b, c, d = i + j, i + (j + 1) % m, i + m + j, i + m + (j + 1) % m
    dr = torch.cat([torch.stack([a, c, b], -1).reshape(-1, 3), torch.stack([b, c, d], -1).reshape(-1, 3)])
    return p, dr


@skipUnless(KARTE, 'ohne Karte')
class SaumausgleichTest(SimpleTestCase):
    def test_1_glatter_kreis_hat_keine_zacken(self):
        from KoerperKI_Fotos.saummass import Saummass
        from meshgenesis_kostuem_saumausgleich import Kostuemsaumausgleich
        kreis = _schleife(35.3, 35.3, 90)
        self.assertGreater(_zacken(Saummass, kreis), 0.7)                    # der alte Kern zählt die Krümmung (gemessen 0,91 mm)
        self.assertLess(_zacken(Kostuemsaumausgleich, kreis), 0.2)
        self.assertLess(_zacken(Kostuemsaumausgleich, _schleife(40.0, 30.0, 100)), 0.4)

    def test_2_saegezahn_bleibt_sichtbar(self):
        from meshgenesis_kostuem_saumausgleich import Kostuemsaumausgleich
        self.assertGreater(_zacken(Kostuemsaumausgleich, _schleife(35.3, 35.3, 90, zahn_mm=1.0)), 0.4)
        self.assertGreater(_zacken(Kostuemsaumausgleich, _schleife(135.0, 135.0, 225, zahn_mm=3.0)), 1.2)

    def test_3_breite_aus_dem_schwund(self):
        from meshgenesis_kostuem_saumkurve import Kostuemsaumkurve
        b = Kostuemsaumkurve._breite(0.15, 0.02)
        k = math.exp(-2 * math.pi ** 2 * b ** 2 / 0.15 ** 2)
        self.assertAlmostEqual((1 - k) ** 2, 0.02, places=6)                # der Kreis schwindet genau um den erlaubten Anteil
        self.assertEqual(Kostuemsaumkurve._breite(1.0, 0.02), Kostuemsaumkurve.GLAETTE_M)


@skipUnless(KARTE, 'ohne Karte')
class SichtmaskeTest(SimpleTestCase):
    def test_4_geschlossene_huelle_verbirgt_alles(self):
        from meshgenesis_eigensichtmaske import Eigensichtmaske
        fp, fd = _kugel(0.10)
        hp, hd = _kugel(0.15, mitte=(0.0, 0.0, 0.0))
        maske, bericht = Eigensichtmaske(fp, fd).verborgen(hp, hd)
        self.assertEqual(bericht['mit_sichtbar'], 0)
        self.assertGreater(int(maske.sum()), 0.9 * bericht['ohne_sichtbar'])

    def test_5_offene_schale_laesst_den_rand_sehen(self):
        from meshgenesis_eigensichtmaske import Eigensichtmaske
        fp, fd = _kugel(0.10)
        hp, hd = _kugel(0.15, bis=0.5 * math.pi)                             # obere Halbschale: von unten sieht man die Figur
        maske, _bericht = Eigensichtmaske(fp, fd).verborgen(hp, hd)
        mitte_y = fp[fd].mean(1)[:, 1]
        self.assertFalse(bool(maske[mitte_y < -0.01].any()))                 # untere Hälfte nie verborgen
        self.assertTrue(bool(maske[mitte_y > 0.09].all()))                   # Kappe oben verborgen
