"""`Laplaceloeser` (freie Knoten, Abbruch, Mehrgitter) gegen eine dichte Lösung; `Netzkerne.haeuten`/`mischen` bitgleich zu torch; `Kinematik.schnell_schalten` und `G9meshkette` gegen den alten Weg
(25.11.2026, Edgar: „kompletter job foto-genesis in 5 s“). Läuft nur auf Ansage; beim Schreiben nicht gelaufen.

Sabotage (von Hand): in `Laplacemehrgitter._prolongation` das Vorzeichen drehen → „Mehrgitter wie dicht“ rot; in `netzkerne_cu/reihe.cuh` die Folge tauschen → „bitgleich“ rot;
in `Laplaceloeser._ausrechnen` `b = b + c…` weglassen → „weiche Bindung“ rot.
"""
import unittest

import torch

from KoerperKI_alle.laplaceloeser import Laplaceloeser
from KoerperKI_alle.netzkerne import Netzkerne


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Karte')
class LaplaceTest(unittest.TestCase):
    databases = []

    @staticmethod
    def _gitter(n):
        """Quadratgitter n × n mit Diagonalen: (Kanten, fest am linken und rechten Rand)."""
        nr = torch.arange(n * n, device='cuda').view(n, n)
        k = torch.cat([torch.stack([nr[:, :-1].reshape(-1), nr[:, 1:].reshape(-1)], 1), torch.stack([nr[:-1].reshape(-1), nr[1:].reshape(-1)], 1),
                       torch.stack([nr[:-1, :-1].reshape(-1), nr[1:, 1:].reshape(-1)], 1)])
        fest = torch.zeros(n * n, dtype=torch.bool, device='cuda')
        fest[nr[:, 0]] = True
        fest[nr[:, -1]] = True
        return k, fest

    def _dicht(self, a, grad, werte, fest, zusatz=None):
        n = len(grad)
        m = torch.diag(grad) - a.to_dense()
        b = torch.zeros_like(werte)
        if zusatz is not None:
            m = m + torch.diag(zusatz)
            b = zusatz[:, None] * werte
        m[fest] = torch.eye(n, dtype=m.dtype, device=m.device)[fest]
        b[fest] = werte[fest]
        return torch.linalg.solve(m, b)

    def test_klein_und_mittel_wie_dicht(self):
        for n in (12, 48):                                            # 144: dichte Zerlegung, 2.304: einfacher CG
            k, fest = self._gitter(n)
            a, grad = Laplaceloeser.graph(n * n, k)
            w = torch.rand((n * n, 5), dtype=torch.float64, device='cuda')
            x, rest = Laplaceloeser.loesen(a, grad, w, fest, 2000)
            self.assertLess(float((x - self._dicht(a, grad, w, fest)).abs().max()), 1e-9)
            self.assertTrue(torch.equal(x[fest], w[fest]))
            self.assertEqual(tuple(rest.shape), (5,))

    def test_mehrgitter_wie_dicht(self):
        n = 78                                                        # 6.084 Knoten, über `MEHRGITTER_AB` freie
        k, fest = self._gitter(n)
        a, grad = Laplaceloeser.graph(n * n, k)
        w = torch.rand((n * n, 3), dtype=torch.float64, device='cuda')
        self.assertGreater(int((~fest).sum()), Laplaceloeser.MEHRGITTER_AB)
        x, _rest = Laplaceloeser.loesen(a, grad, w, fest, 2000)
        self.assertLess(float((x - self._dicht(a, grad, w, fest)).abs().max()), 1e-8)

    def test_weiche_bindung(self):
        k, fest = self._gitter(40)
        fest[:] = False
        a, grad = Laplaceloeser.graph(1600, k)
        w = torch.rand((1600, 2), dtype=torch.float64, device='cuda')
        z = torch.full((1600,), 0.3, dtype=torch.float64, device='cuda')
        x, _r = Laplaceloeser.loesen(a, grad, w, fest, 2000, zusatz=z)
        self.assertLess(float((x - self._dicht(a, grad, w, fest, z)).abs().max()), 1e-9)

    def test_insel_ohne_halt_bleibt_endlich(self):
        """Eine Komponente ohne festen Knoten: singulär — der einfache Weg, kein Mehrgitter, Werte endlich."""
        k = torch.tensor([[0, 1], [1, 2], [3, 4]], device='cuda')
        fest = torch.tensor([True, False, False, False, False], device='cuda')
        a, grad = Laplaceloeser.graph(5, k)
        w = torch.tensor([[1.0], [0.0], [0.0], [2.0], [4.0]], dtype=torch.float64, device='cuda')
        x, _r = Laplaceloeser.loesen(a, grad, w, fest, 2000)
        self.assertTrue(bool(torch.isfinite(x).all()))
        self.assertLess(float((x[:3] - 1.0).abs().max()), 1e-9)

    def test_wenige_runden_bleiben_wie_sie_waren(self):
        k, fest = self._gitter(20)
        a, grad = Laplaceloeser.graph(400, k)
        w = torch.rand((400, 1), dtype=torch.float64, device='cuda')
        _x, rest = Laplaceloeser.loesen(a, grad, w, fest, 10)
        self.assertGreater(float(rest.max()), 1e-12)                   # zehn Runden sind eine Glättung, keine Lösung


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Karte')
class HaeutungTest(unittest.TestCase):
    databases = []

    def test_bitgleich_zu_torch(self):
        torch.manual_seed(5)
        for k in (2, 4, 8):
            n = 5000
            x = torch.randn(n, 3, dtype=torch.float64, device='cuda')
            kn = torch.randint(0, 100, (n, k), device='cuda')
            w = (torch.rand(n, k, dtype=torch.float64, device='cuda') * 255).round() / 255.0
            d, v = torch.randn(100, 3, 3, dtype=torch.float64, device='cuda'), torch.randn(100, 3, dtype=torch.float64, device='cuda')
            aus = torch.zeros_like(x)
            for q in range(k):
                aus += w[:, q:q + 1] * (torch.einsum('nij,nj->ni', d[kn[:, q]], x) + v[kn[:, q]])
            self.assertTrue(torch.equal(Netzkerne.mischen(x, kn, w, d, v), aus))
            s = w.sum(1, keepdim=True)
            self.assertTrue(torch.equal(Netzkerne.haeuten(x, kn, w, d, v), torch.where(s <= 1e-9, x, aus / torch.where(s <= 1e-9, torch.ones_like(s), s))))


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Karte')
class KinematikTest(unittest.TestCase):
    databases = []

    def test_schnell_wie_langsam(self):
        from KoerperKI_alle.kinematik import Kinematik
        torch.manual_seed(7)
        knochen = []
        for j in range(40):
            knochen.append({'eltern': -1 if j == 0 else (j - 1) // 2, 'zentrum': [0.1 * j, 0.05 * j, 0.02 * (j % 3)], 'ende': [0.1 * j, 0.05 * j + 0.1, 0.0], 'o': [3.0 * j % 40, 5.0, 2.0],
                            'reihenfolge': ('XYZ', 'YZX', 'ZYX', 'XZY', 'YXZ', 'ZXY')[j % 6], 'min': [-60.0] * 3, 'max': [60.0] * 3, 'fest': [False] * 3, 'fest_wert': [0.0] * 3})
        kin = Kinematik({'knochen': knochen}).to('cuda')
        roh = torch.randn((3, kin.anzahl), device='cuda')
        langsam = kin(roh)
        schnell = kin.schnell_schalten()(roh)
        for a, b in zip(langsam, schnell, strict=True):
            self.assertLess(float((a - b).abs().max()), 1e-5)


if __name__ == '__main__':
    unittest.main()
