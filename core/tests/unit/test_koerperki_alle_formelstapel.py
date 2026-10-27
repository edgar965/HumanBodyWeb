# -*- coding: utf-8 -*-
"""Tests für `KoerperKI_alle.formelstapel.Formelstapel` (27.10.2026, Besitzer Mesh3D-AI).

Seltene Daz-Formeln auf Tensoren, wie `G9formeln.rechnen`.

WARUM: Der `Formgraph` rechnet die Splines und Produkte des Formelgraphen über diese Klasse. Eine Formel,
die anders rechnet als Daz (Spline außerhalb der Knoten, Teilen durch 0, Produkt zweier Kanäle), ließe die
Formrechnung stumm neben G9formung laufen — genau der Fehler, den der Graph beheben soll (13–17 mm an den
Vorhersagen, 27.10.2026).
"""
import sys
import unittest

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from Genesis9.formeln import G9formeln  # noqa: E402
from KoerperKI_alle.formelstapel import Formelstapel  # noqa: E402

MULT, ADD = ('mult', None), ('add', None)


class DerFormelstapel(unittest.TestCase):
    def setUp(self):
        self.v = torch.tensor([[0.0, 2.0], [0.5, -1.0], [2.0, 0.0]])

    def test_produkt_zweier_kanaele_plus_linear(self):
        # `K Z mult K K mult Z mult add` = 0,5·a + (a·b)·2
        ops = [('v', 0), ('z', 0.5), MULT, ('v', 0), ('v', 1), MULT, ('z', 2.0), MULT, ADD]
        a, b = self.v[:, 0], self.v[:, 1]
        self.assertTrue(torch.allclose(Formelstapel.rechnen(ops, self.v), 0.5 * a + a * b * 2.0))

    def test_spline_wie_g9formeln(self):
        knoten = [[0.0, 0.0, 0, 0, 0], [1.0, 2.0, 0, 0, 0], [1.5, 1.0, 0, 0, 0]]
        for x in (-1.0, 0.0, 0.25, 1.0, 1.2, 1.5, 3.0):
            ist = Formelstapel.spline(knoten, torch.tensor([x]))
            self.assertAlmostEqual(float(ist[0]), G9formeln.spline(knoten, x), places=6, msg='x = %s' % x)

    def test_spline_ueber_den_stapel(self):
        knoten = [('l', [0.0, 0.0, 0, 0, 0]), ('l', [1.0, 4.0, 0, 0, 0])]
        ops = [('v', 0)] + knoten + [('z', 2.0), ('spline_linear', None)]
        self.assertTrue(torch.allclose(Formelstapel.rechnen(ops, self.v), torch.tensor([0.0, 2.0, 4.0])))

    def test_teilen_durch_null_ergibt_null(self):
        ops = [('z', 1.0), ('v', 0), ('div', None)]
        self.assertTrue(torch.allclose(Formelstapel.rechnen(ops, self.v), torch.tensor([0.0, 2.0, 0.5])))

    def test_unvollstaendige_formel_ergibt_null(self):
        self.assertTrue(torch.equal(Formelstapel.rechnen([('v', 0), MULT], self.v), torch.zeros(3)))


if __name__ == '__main__':
    unittest.main()
