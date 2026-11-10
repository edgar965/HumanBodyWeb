# -*- coding: utf-8 -*-
"""`Hauthartlicht.sichtbar` und `Kostuemhautschatten.rot` an Kunstfiguren (05.11.2026). Geschrieben, nicht gelaufen."""
import sys
import unittest

import torch

sys.path.insert(0, r'A:\3DTools\meshgenesis')

from meshgenesis_haut_hartlicht import Hauthartlicht  # noqa: E402
from meshgenesis_kostuem_hautschatten import Kostuemhautschatten  # noqa: E402


def platte(hoehe):
    a = torch.linspace(-0.2, 0.2, 200)
    x, z = torch.meshgrid(a, a, indexing='ij')
    return torch.stack([x.flatten(), torch.full_like(x.flatten(), hoehe), z.flatten()], 1)


class HauthartlichtTest(unittest.TestCase):
    databases = []

    def _licht(self, ort):
        h = Hauthartlicht.__new__(Hauthartlicht)
        h.ort = ort
        return h

    def test_obere_platte_beschattet_die_untere(self):
        oben, unten = platte(0.3), platte(0.0)
        h = self._licht(torch.cat([oben, unten]))
        s = h.sichtbar(torch.tensor([0.0, 1.0, 0.0]), torch.ones(len(h.ort)))
        self.assertTrue(bool(s[:len(oben)].all()))
        self.assertFalse(bool(s[len(oben):].any()))

    def test_seitliche_sonne_laesst_beide_frei(self):
        oben, unten = platte(0.3)[:, :], platte(0.0) + torch.tensor([1.0, 0.0, 0.0])
        h = self._licht(torch.cat([oben, unten]))
        s = h.sichtbar(torch.tensor([0.0, 1.0, 0.0]), torch.ones(len(h.ort)))
        self.assertTrue(bool(s.all()))

    def test_flach_beschienene_flaeche_beschattet_sich_nicht_selbst(self):
        schraeg = platte(0.0) @ torch.tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        schraeg[:, 1] = schraeg[:, 0] * 3.0
        h = self._licht(schraeg)
        c = torch.full((len(schraeg),), 0.3)
        self.assertGreater(float(h.sichtbar(torch.tensor([0.0, 1.0, 0.0]), c).float().mean()), 0.99)


class KostuemhautschattenTest(unittest.TestCase):
    databases = []

    def test_grenze_liegt_unter_der_wahrheit(self):
        self.assertFalse(Kostuemhautschatten.rot(0.525))
        self.assertTrue(Kostuemhautschatten.rot(0.44))
