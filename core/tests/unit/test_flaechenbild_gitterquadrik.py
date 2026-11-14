# -*- coding: utf-8 -*-
"""Segmentierung auf der Karte (12.11.2026): `Flaechenbild` (VideoToBVH/wrappers) zeichnet das Flächennummern-Bild Pixel für Pixel wie `ImageDraw.polygon` im Malerverfahren, `Gitterquadrik`
(KoerperKI_alle) vereinfacht ein Netz für das Abstimm-Netz. Gegenproben am Zauberer: `ProjektTemp/_wegwerf/genesis_zuerst/umbau/flaechenbild_probe.py` (0 Pixel anders, Sabotage rot),
`abstimmnetz_vergleich.py`, `abstimmnetz_referenz.py`.

Hier Kunstfiguren: zufällige Dreiecke mit vielen Sonderfällen (ganzzahlige Ecken, waagrechte Kanten, zusammenfallende Punkte, Ränder außerhalb des Bilds) gegen PIL im selben Prozess, und eine
Kugel aus Breiten- und Längenkreisen für die Vereinfachung. Braucht die Grafikkarte (sonst übersprungen). Nicht gelaufen — läuft nur auf Ansage.
Sabotage: in `Flaechenbild._round_up` `+ h` → `+ 2 * h` → `test_1` rot; in `Gitterquadrik.vereinfachen` `TOLERANZ = 0.5` → `test_3` rot.
"""
import math
import sys
import unittest

import torch
from KoerperKI_alle.gitterquadrik import Gitterquadrik
from PIL import Image, ImageDraw

sys.path.insert(0, r'A:\3DTools\VideoToBVH\wrappers')
from flaechenbild import Flaechenbild  # noqa: E402


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class FlaechenbildGitterquadrikTest(unittest.TestCase):
    G = torch.device('cuda')

    def _pil(self, px, py, tiefe, flaechen, breite, hoehe):
        bild = Image.new('I', (breite, hoehe), 0)
        zeichner = ImageDraw.Draw(bild)
        t = tiefe[flaechen]
        mitte = ((t[:, 0] + t[:, 1]) + t[:, 2]) / 3.0
        for i in torch.argsort(mitte, stable=True).tolist():
            zeichner.polygon([(float(px[j]), float(py[j])) for j in flaechen[i].tolist()], fill=i + 1)
        roh = torch.frombuffer(bytearray(bild.tobytes()), dtype=torch.int32)                  # cpu gewollt: Bildbytes von PIL
        return roh.view(hoehe, breite).to(self.G)

    def _fall(self, n, breite, hoehe, saat, raster=False):
        gen = torch.Generator(device=self.G).manual_seed(saat)
        groesse = torch.tensor([breite * 1.2, hoehe * 1.2], device=self.G, dtype=torch.float64)
        mitte = torch.rand(n, 1, 2, device=self.G, generator=gen, dtype=torch.float64) * groesse - 0.1 * breite
        ecken = mitte + (torch.rand(n, 3, 2, device=self.G, generator=gen, dtype=torch.float64) - 0.5) * 30
        if raster:
            ecken = torch.round(ecken)                                                         # ganze Zahlen: waagrechte Kanten, gleiche Punkte
            ecken[::7, 2] = ecken[::7, 0]
            ecken[::11, 1, 1] = ecken[::11, 0, 1]
        px, py = ecken[..., 0].reshape(-1), ecken[..., 1].reshape(-1)
        tiefe = torch.rand(3 * n, device=self.G, generator=gen, dtype=torch.float64)
        flaechen = torch.arange(3 * n, device=self.G).view(n, 3)
        return px, py, tiefe, flaechen

    def test_1_zufall_wie_pil(self):
        for saat in (1, 2, 3):
            px, py, tiefe, flaechen = self._fall(800, 200, 160, saat)
            ist = Flaechenbild.zeichnen(px, py, tiefe, flaechen, 200, 160)
            soll = self._pil(px.cpu(), py.cpu(), tiefe.cpu(), flaechen.cpu(), 200, 160)
            self.assertEqual(int((ist != soll).sum()), 0, 'Saat %d' % saat)

    def test_2_ganzzahlige_ecken_wie_pil(self):
        for saat in (4, 5):
            px, py, tiefe, flaechen = self._fall(800, 150, 150, saat, raster=True)
            ist = Flaechenbild.zeichnen(px, py, tiefe, flaechen, 150, 150)
            soll = self._pil(px.cpu(), py.cpu(), tiefe.cpu(), flaechen.cpu(), 150, 150)
            self.assertEqual(int((ist != soll).sum()), 0, 'Saat %d' % saat)

    def test_3_kugel_vereinfacht(self):
        breiten, laengen = 300, 600
        th = torch.linspace(0.01, math.pi - 0.01, breiten, device=self.G, dtype=torch.float64)
        ph = torch.linspace(0, 2 * math.pi, laengen + 1, device=self.G, dtype=torch.float64)[:-1]
        T, P = torch.meshgrid(th, ph, indexing='ij')
        punkte = torch.stack([T.sin() * P.cos(), T.cos(), T.sin() * P.sin()], -1).reshape(-1, 3)
        i = torch.arange(breiten - 1, device=self.G).view(-1, 1) * laengen
        j = torch.arange(laengen, device=self.G).view(1, -1)
        a, b, c, d = i + j, i + (j + 1) % laengen, i + laengen + j, i + laengen + (j + 1) % laengen
        flaechen = torch.cat([torch.stack([a, c, b], -1).reshape(-1, 3), torch.stack([b, c, d], -1).reshape(-1, 3)])
        ziel = 20_000
        lage, neu = Gitterquadrik.vereinfachen(punkte, flaechen, ziel)
        self.assertLessEqual(abs(len(neu) - ziel), Gitterquadrik.TOLERANZ * ziel)

        def inhalt(p, f):
            return float(torch.linalg.cross(p[f[:, 1]] - p[f[:, 0]], p[f[:, 2]] - p[f[:, 0]]).norm(dim=1).sum() / 2)
        self.assertAlmostEqual(inhalt(lage, neu) / inhalt(punkte, flaechen), 1.0, delta=0.03)
        self.assertLess(float((lage.norm(dim=1) - 1).abs().max()), 0.02)                    # Punkte bleiben auf der Kugel


if __name__ == '__main__':
    unittest.main()
