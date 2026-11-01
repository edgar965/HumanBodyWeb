"""Gemeinsamer Löser `KoerperKI_alle.Laplaceloeser` (01.11.2026, abgestimmt mit 3dtools-80: die CG aus `Kostuemergaenzung`, auch für `Ergaenzung.flaeche`) — an einem Kunstgitter
(21 × 21, Dreiecke mit einer Diagonale), CPU, ohne Figur.

1. Feste Randknoten mit einer linearen Funktion: innen kommt dieselbe lineare Funktion heraus (auf diesem Gitter ist sie harmonisch, sechs Nachbarn mit Versatz-Summe 0).
2. Weiche Bindung (`zusatz` = s·d/(1 − s)): die Lösung ist der Fixpunkt von x = s·w + (1 − s)·Mittel der Nachbarn, den `Ergaenzung.flaeche` bis 01.11.2026 mit Jacobi-Runden suchte.
3. Eine Komponente ohne festen Knoten und ohne Bindung bleibt auf ihrem Start.
"""
import sys
import unittest

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_alle.laplaceloeser import Laplaceloeser  # noqa: E402

N = 21


def gitter():
    """→ (Lage (n, 2), ungerichtete Kanten (E, 2))."""
    i = torch.arange(N * N).reshape(N, N)
    d = torch.cat([torch.stack([i[:-1, :-1], i[1:, :-1], i[:-1, 1:]], -1).reshape(-1, 3), torch.stack([i[1:, :-1], i[1:, 1:], i[:-1, 1:]], -1).reshape(-1, 3)])
    e = torch.unique(torch.sort(torch.cat([d[:, [0, 1]], d[:, [1, 2]], d[:, [2, 0]]]), 1).values, dim=0)
    lage = torch.stack(torch.meshgrid(torch.arange(N), torch.arange(N), indexing='ij'), -1).reshape(-1, 2).double()
    return lage, e


class Laplaceloesertest(unittest.TestCase):

    def test_1_lineare_funktion_bleibt_linear(self):
        lage, e = gitter()
        a, grad = Laplaceloeser.graph(N * N, e)
        rand = (lage[:, 0] == 0) | (lage[:, 0] == N - 1) | (lage[:, 1] == 0) | (lage[:, 1] == N - 1)
        linear = (2.0 * lage[:, 0] - lage[:, 1] + 0.5)[:, None]
        werte = torch.where(rand[:, None], linear, torch.zeros_like(linear))
        x, rest = Laplaceloeser.loesen(a, grad, werte, rand, 500)
        self.assertLess(float((x - linear).abs().max()), 1e-9)
        self.assertLess(float(rest.max()), 1e-18)

    def test_2_weiche_bindung_ist_der_jacobi_fixpunkt(self):
        lage, e = gitter()
        n = N * N
        a, grad = Laplaceloeser.graph(n, e)
        g = torch.Generator().manual_seed(5)
        s = torch.where(torch.rand(n, generator=g) < 0.3, torch.rand(n, generator=g), torch.zeros(n)).double()
        s[::37] = 1.0
        w = torch.rand(n, 2, generator=g, dtype=torch.float64)
        zusatz = torch.where(s < 1, s * grad / (1 - s).clamp_min(1e-12), torch.zeros_like(s))
        x, _rest = Laplaceloeser.loesen(a, grad, w, s >= 1, 2000, start=torch.zeros_like(w), zusatz=zusatz)
        mittel = (a @ x) / grad[:, None]
        self.assertLess(float((s[:, None] * w + (1 - s[:, None]) * mittel - x).abs().max()), 1e-10)

    def test_3_komponente_ohne_festen_knoten_bleibt_auf_dem_start(self):
        _lage, e = gitter()
        n = N * N
        a, grad = Laplaceloeser.graph(2 * n, torch.cat([e, e + n]))
        fest = torch.zeros(2 * n, dtype=torch.bool)
        fest[:n:5] = True
        werte = torch.rand(2 * n, 1, dtype=torch.float64)
        x, _rest = Laplaceloeser.loesen(a, grad, werte, fest, 300, start=torch.full((2 * n, 1), 0.25, dtype=torch.float64))
        self.assertTrue(bool((x[n:] == 0.25).all()))
        self.assertTrue(torch.equal(x[:n][fest[:n]], werte[:n][fest[:n]]))
