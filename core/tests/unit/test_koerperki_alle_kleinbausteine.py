"""Kleine gemeinsame Bausteine aus `KoerperKI_alle` (01.11.2026, abgestimmt mit 3dtools-80):
`Farblab`, `Achsdrehung`, `Baryanteile` — CPU, Kunstwerte, ohne Figur.

1. Farblab: Weiß → L 100, a/b ≈ 0; Schwarz → 0; numpy und torch gleich; Gradient endlich an 0 und
   an der Schwelle. `srgb` kehrt `linear` um (numpy und torch), klemmt auf 0..1.
2. Achsdrehung: orthonormal mit det 1, 90° um z bildet x auf y ab, w = 0 → Einheitsmatrix,
   gestapelt wie einzeln.
3. Baryanteile: Punkt aus bekannten Anteilen kommt zurück; geklemmt ≥ 0 mit Summe 1; außerhalb
   ungeklemmt negativ.
"""
import math
import sys
import unittest

import numpy as np
import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_alle.achsdrehung import Achsdrehung  # noqa: E402
from KoerperKI_alle.baryanteile import Baryanteile  # noqa: E402
from KoerperKI_alle.farblab import Farblab  # noqa: E402

D = torch.float64


class Kleinbausteinetest(unittest.TestCase):

    def test_1_farblab(self):
        lab = Farblab.aus_srgb(np.array([[255.0, 255.0, 255.0], [0.0, 0.0, 0.0]]), 255.0)
        self.assertAlmostEqual(float(lab[0, 0]), 100.0, places=2)
        self.assertLess(float(np.abs(lab[0, 1:]).max()), 0.05)
        self.assertLess(float(np.abs(lab[1]).max()), 1e-12)
        c = np.random.default_rng(1).uniform(0, 1, (50, 3))
        c[0] = 0.0
        c[1] = 0.04045
        t = torch.tensor(c, requires_grad=True)
        lab_t = Farblab.aus_srgb(t)
        self.assertLess(float(np.abs(lab_t.detach().numpy() - Farblab.aus_srgb(c)).max()), 1e-12)
        lab_t.sum().backward()
        self.assertTrue(bool(torch.isfinite(t.grad).all()))

    def test_1b_farblab_srgb_kehrt_linear_um(self):
        c = np.random.default_rng(2).uniform(0, 1, (50, 3))
        c[0], c[1] = 0.0, 0.04045
        self.assertLess(float(np.abs(Farblab.srgb(Farblab.linear(c)) - c).max()), 1e-12)
        t = torch.tensor(c)
        self.assertLess(float((Farblab.srgb(Farblab.linear(t)) - t).abs().max()), 1e-12)
        geklemmt = Farblab.srgb(np.array([-0.5, 2.0]))          # 1,055 · 1 − 0,055 = 0,9999999999999999
        self.assertEqual(float(geklemmt[0]), 0.0)
        self.assertAlmostEqual(float(geklemmt[1]), 1.0, places=12)

    def test_2_achsdrehung(self):
        r = Achsdrehung.matrix(torch.tensor([0.0, 0.0, math.pi / 2], dtype=D))
        y = r @ torch.tensor([1.0, 0.0, 0.0], dtype=D)
        self.assertLess(float((y - torch.tensor([0.0, 1.0, 0.0], dtype=D)).abs().max()), 1e-15)
        self.assertTrue(torch.equal(Achsdrehung.matrix(torch.zeros(3)), torch.eye(3)))
        w = torch.randn(32, 3, generator=torch.Generator().manual_seed(2), dtype=D) * 2
        rs = Achsdrehung.matrix(w)
        self.assertLess(float((rs.transpose(-1, -2) @ rs - torch.eye(3, dtype=D)).abs().max()), 1e-14)
        self.assertLess(float((torch.linalg.det(rs) - 1).abs().max()), 1e-14)
        self.assertLess(float((torch.stack([Achsdrehung.matrix(x) for x in w]) - rs).abs().max()), 1e-15)
        aw = Achsdrehung.achse_winkel(torch.tensor([0.0, 0.0, 5.0]), math.pi / 2)
        self.assertLess(float((aw - r.float()).abs().max()), 1e-6)

    def test_3_baryanteile(self):
        e = torch.randn(200, 3, 3, generator=torch.Generator().manual_seed(3), dtype=D)
        a, b, c = e[:, 0], e[:, 1], e[:, 2]
        soll = torch.tensor([0.2, 0.3, 0.5], dtype=D)
        x = (e * soll[None, :, None]).sum(1)
        self.assertLess(float((Baryanteile.anteile(x, a, b, c, klemmen=False) - soll).abs().max()), 1e-10)
        aussen = a + 2.0 * (a - b)
        roh = Baryanteile.anteile(aussen, a, b, c, klemmen=False)
        self.assertTrue(bool((roh.min(-1).values < 0).all()))
        lam = Baryanteile.anteile(aussen, a, b, c)
        self.assertTrue(bool((lam >= 0).all()))
        self.assertLess(float((lam.sum(-1) - 1).abs().max()), 1e-12)
