# -*- coding: utf-8 -*-
"""`KoerperKI_alle.Ergaenzung` (31.10.2026; Edgar: „wo Hände was verdecken … extrapoliert — von der symmetrischen Seite, oder von der Umgebung, oder von bekannten Formen“) — an
Kunstflächen auf der CPU, ohne Figur und ohne Fotos.

1. Spiegel: die rechte Seite hat ein Loch, die linke ist gesehen → das Loch trägt die Werte der linken Stelle am gespiegelten Ort, der Partner ist genau dieser Punkt.
2. Umgebung über die Fläche: ein linearer Verlauf mit Loch kommt im Loch wieder heraus (Mittel der Nachbarn), der Partner ist ein gesehener Punkt desselben Teils.
3. Gefaltetes Band: Vorder- und Rückseite 5 mm auseinander, auf der Fläche weit — die Füllung nimmt nur die eigene Lage (die Zellenpyramide ohne Graph mischt beide).
4. Ein Teil ganz ohne Beobachtung bekommt die Vorlage.
5. Farbe: der Spiegel bringt die Zeichnung, der Ton bleibt der eigenen Seite (links doppelt so hell beleuchtet).
6. Texel mit Raster: die Füllung trägt die Zeichnung der gesehenen Haut (Streuung), nicht nur den glatten Ton.
"""
import sys
import unittest

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_alle.ergaenzung import Ergaenzung  # noqa: E402


def blatt(nx, ny, h, versatz=(0.0, 0.0, 0.0)):
    """Ebenes Gitter in x/y (nx × ny Punkte, Abstand h) → Punkte (N, 3), Dreiecke."""
    ii, jj = torch.meshgrid(torch.arange(nx), torch.arange(ny), indexing='ij')
    p = torch.stack([ii.flatten() * h, jj.flatten() * h, torch.zeros(nx * ny)], 1) + torch.tensor(versatz)
    d = []
    for i in range(nx - 1):
        for j in range(ny - 1):
            a, b, c, e = i * ny + j, (i + 1) * ny + j, i * ny + j + 1, (i + 1) * ny + j + 1
            d += [[a, b, c], [b, e, c]]
    return p, torch.tensor(d)


class Ergaenzungtest(unittest.TestCase):

    def test_1_spiegel_fuellt_das_loch_mit_der_anderen_seite(self):
        rechts, d = blatt(10, 10, 0.01, (0.05, 0.0, 0.0))
        links = rechts * torch.tensor([-1.0, 1.0, 1.0])
        p = torch.cat([links, rechts])
        dd = torch.cat([d, d + len(links)])
        teil = torch.cat([torch.zeros(len(links)), torch.ones(len(rechts))]).long()
        werte = torch.cat([p[:len(links), 1:2] * 10 + 1, torch.zeros(len(rechts), 1)])            # links: Verlauf in y
        sicher = torch.ones(len(p))
        loch = torch.zeros(len(p), dtype=torch.bool)
        loch[len(links):] = (rechts[:, 1] > 0.025) & (rechts[:, 1] < 0.065)
        sicher[loch] = 0
        werte[len(links):] = torch.where(loch[len(links):, None], torch.zeros(len(rechts), 1), rechts[:, 1:2] * 10 + 1)
        aus, herkunft, partner, _b = Ergaenzung(p, teil, torch.tensor([1, 0]), dreiecke=dd).fuellen(werte, sicher, farbe=False)
        self.assertTrue(bool((herkunft[loch] == 1).all()))
        self.assertLess(float((aus[loch, 0] - (p[loch, 1] * 10 + 1)).abs().max()), 1e-4)
        gespiegelt = p[partner[loch]] * torch.tensor([-1.0, 1.0, 1.0])
        self.assertLess(float((gespiegelt - p[loch]).norm(dim=1).max()), 1e-5)

    def test_2_umgebung_ueber_die_flaeche_gibt_den_verlauf_zurueck(self):
        p, d = blatt(30, 30, 0.005)
        werte = (p[:, 0:1] * 4 + p[:, 1:2] * 2)
        mitte = ((p[:, :2] - 0.0725).norm(dim=1) < 0.03)
        sicher = (~mitte).float()
        aus, herkunft, partner, _b = Ergaenzung(p, dreiecke=d).fuellen(torch.where(mitte[:, None], torch.zeros_like(werte), werte), sicher, farbe=False)
        self.assertTrue(bool((herkunft[mitte] == 2).all()))
        self.assertLess(float((aus[mitte] - werte[mitte]).abs().max()), 0.01)
        self.assertTrue(bool((sicher[partner[mitte]] == 1).all()))

    def test_3_gefaltetes_band_mischt_die_lagen_nicht(self):
        vorn, d = blatt(60, 6, 0.005)
        hinten = vorn + torch.tensor([0.0, 0.0, 0.005])
        p = torch.cat([vorn, hinten])
        n = len(vorn)
        falz = [[i * 6 + j, n + i * 6 + j, i * 6 + j + 1] for i in (59,) for j in range(5)] + [[n + i * 6 + j, n + i * 6 + j + 1, i * 6 + j + 1] for i in (59,) for j in range(5)]
        dd = torch.cat([d, d + n, torch.tensor(falz)])
        werte = torch.cat([torch.ones(n, 1), torch.zeros(n, 1)])
        loch = torch.zeros(2 * n, dtype=torch.bool)
        loch[:n] = (vorn[:, 0] > 0.05) & (vorn[:, 0] < 0.08)
        sicher = (~loch).float()
        aus, _h, _p, _b = Ergaenzung(p, dreiecke=dd).fuellen(werte, sicher, farbe=False)
        self.assertGreater(float(aus[loch, 0].min()), 0.99, 'die Rückseite ist in die Vorderseite geflossen')
        ohne, _h, _p, _b = Ergaenzung(p).fuellen(werte, sicher, farbe=False)
        self.assertLess(float(ohne[loch, 0].mean()), 0.9, 'Gegenprobe: ohne Graph mischen die Lagen')

    def test_4_teil_ohne_beobachtung_nimmt_die_vorlage(self):
        a, d = blatt(8, 8, 0.01)
        b = a + torch.tensor([0.5, 0.0, 0.0])
        p = torch.cat([a, b])
        teil = torch.cat([torch.zeros(len(a)), torch.ones(len(b))]).long()
        werte = torch.full((len(p), 1), 3.0)
        sicher = torch.cat([torch.ones(len(a)), torch.zeros(len(b))])
        vorlage = torch.full((len(p), 1), 7.0)
        aus, herkunft, partner, _b = Ergaenzung(p, teil, dreiecke=torch.cat([d, d + len(a)])).fuellen(werte, sicher, vorlage=vorlage, farbe=False)
        self.assertTrue(bool((herkunft[len(a):] == 3).all()))
        self.assertLess(float((aus[len(a):] - 7.0).abs().max()), 1e-4)
        self.assertTrue(bool((partner[len(a):] == -1).all()))

    def test_5_farbe_spiegel_bringt_zeichnung_mit_eigenem_ton(self):
        rechts, d = blatt(40, 40, 0.004, (0.05, 0.0, 0.0))
        links = rechts * torch.tensor([-1.0, 1.0, 1.0])
        p = torch.cat([links, rechts])
        n = len(links)
        muster = 1 + 0.3 * torch.sign(torch.sin(rechts[:, 1] * 400))                  # Streifen 8 mm
        werte = torch.cat([0.4 * muster, 0.2 * muster])[:, None].expand(-1, 3).clone()  # links doppelt so hell
        loch = torch.zeros(2 * n, dtype=torch.bool)
        loch[n:] = ((rechts[:, :2] - torch.tensor([0.128, 0.078])).norm(dim=1) < 0.03)
        sicher = (~loch).float()
        teil = torch.cat([torch.zeros(n), torch.ones(n)]).long()
        aus, herkunft, _p, befund = Ergaenzung(p, teil, torch.tensor([1, 0]), dreiecke=torch.cat([d, d + n])).fuellen(werte, sicher)
        self.assertTrue(bool((herkunft[loch] == 1).all()))
        verhaeltnis = aus[loch, 0] / (0.2 * muster[loch[n:]])
        self.assertLess(float((verhaeltnis - 1).abs().max()), 0.1, 'Ton der Spiegelseite statt der eigenen')
        self.assertAlmostEqual(befund['spiegel_angleich_median'][0], 0.5, places=2)

    def test_6_texel_mit_raster_tragen_zeichnung(self):
        seite = 128
        yy, xx = torch.meshgrid(torch.arange(seite), torch.arange(seite), indexing='ij')
        y, x = yy.flatten(), xx.flatten()
        p = torch.stack([x * 0.002, y * 0.002, torch.zeros_like(x, dtype=torch.float)], 1).float()
        torch.manual_seed(3)
        zeichnung = torch.exp(0.3 * torch.randn(len(p)))
        werte = (0.3 * zeichnung)[:, None].expand(-1, 3).clone()
        loch = ((x - 64) ** 2 + (y - 64) ** 2) < 20 ** 2
        sicher = (~loch).float()
        raster = (torch.zeros_like(x), y, x, seite)
        aus, herkunft, _p, befund = Ergaenzung(p).fuellen(werte, sicher, raster=raster)
        self.assertTrue(bool((herkunft[loch] == 2).all()))
        gesehen_streu = float(torch.log(werte[~loch, 0]).std())
        loch_streu = float(torch.log(aus[loch, 0]).std())
        self.assertGreater(loch_streu, 0.5 * gesehen_streu, 'die Füllung ist glatt, die Zeichnung fehlt')
        self.assertLess(abs(float(torch.log(aus[loch, 0]).mean()) - float(torch.log(werte[~loch, 0]).mean())), 0.1)
        self.assertGreater(befund['zeichnung']['quellbloecke'], 0)


if __name__ == '__main__':
    unittest.main()
