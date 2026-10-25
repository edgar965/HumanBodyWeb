# -*- coding: utf-8 -*-
"""Tests für `HaarKI.haarschale.Haarschale` (24.10.2026, Besitzer 2d-3d-AI): Auswahl der Kopfdreiecke, Teilung, Normalen, leere Felder.

WARUM: Fotos (`KopfKI.Fotohaarschale`) und Netz (`mesh3dai/mesh3dai_haarbeobachtung.py`, Sitzung 3dtools-cc) schreiben ihre Beobachtung je Schalenpunkt — Punkt i muss auf beiden Seiten
derselbe sein. Das hält nur, wenn die Teilung deterministisch ist, gemeinsame Kanten keinen Punkt doppelt erzeugen und die Normalen nach außen zeigen (Höhe entlang der Normale).
"""
import sys
import unittest

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from HaarKI.haarschale import Haarschale  # noqa: E402


class DieHaarschale(unittest.TestCase):
    EBENE = torch.tensor([[0.0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]])
    ZWEI = torch.tensor([[0, 1, 2], [1, 3, 2]])
    #: Tetraeder mit nach außen zeigender Reihenfolge
    TETRA = torch.tensor([[1.0, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]])
    TETRA_D = torch.tensor([[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]])

    def test_ein_dreieck_zweimal_geteilt(self):
        s = Haarschale(self.EBENE[:3], self.ZWEI[:1])
        self.assertEqual(len(s.dreiecke), 16)
        self.assertEqual(len(s.punkte), 15)
        self.assertTrue(torch.allclose(s.normalen, torch.tensor([0.0, 0, 1]).expand(15, 3)))
        flaeche = 0.5 * torch.cross(s.punkte[s.dreiecke[:, 1]] - s.punkte[s.dreiecke[:, 0]], s.punkte[s.dreiecke[:, 2]] - s.punkte[s.dreiecke[:, 0]], dim=1)
        self.assertTrue(torch.allclose(flaeche[:, 2], torch.full((16,), 0.5 / 16)))
        self.assertEqual(s.punkte.dtype, torch.float32)

    def test_gemeinsame_kante_ohne_doppelte_punkte(self):
        s = Haarschale(self.EBENE, self.ZWEI)
        self.assertEqual(len(s.dreiecke), 32)
        self.assertEqual(len(s.punkte), 25)                         # 5 × 5-Gitter auf dem Quadrat
        self.assertEqual(len(torch.unique(s.punkte, dim=0)), 25)

    def test_nur_dreiecke_ganz_im_kopf(self):
        s = Haarschale(self.EBENE, self.ZWEI, kopf_index=torch.tensor([1, 2, 3]))
        self.assertEqual(len(s.dreiecke), 16)
        self.assertTrue(torch.equal(s.punkte[:3], self.EBENE[[1, 2, 3]]))
        self.assertTrue(set(s.basis.tolist()) <= {1, 2, 3})
        self.assertEqual(s.kopf_index.tolist(), [1, 2, 3])

    def test_normalen_zeigen_nach_aussen(self):
        s = Haarschale(self.TETRA, self.TETRA_D)
        self.assertTrue(bool(((s.normalen * s.punkte).sum(1) > 0).all()))
        self.assertTrue(torch.allclose(s.normalen.norm(dim=1), torch.ones(len(s.punkte))))

    def test_zweimal_gebaut_gleich(self):
        a, b = Haarschale(self.TETRA, self.TETRA_D), Haarschale(self.TETRA, self.TETRA_D)
        self.assertTrue(torch.equal(a.punkte, b.punkte))
        self.assertTrue(torch.equal(a.dreiecke, b.dreiecke))
        self.assertTrue(torch.equal(a.basis, b.basis))

    def test_leer_fuenf_felder_nicht_beobachtet(self):
        s = Haarschale(self.TETRA, self.TETRA_D)
        f = s.leer()
        v = len(s.punkte)
        self.assertEqual(sorted(f), ['deckung', 'farbe', 'gewicht', 'hoehe', 'richtung'])
        self.assertEqual({k: tuple(t.shape) for k, t in f.items()}, {'hoehe': (v,), 'deckung': (v,), 'farbe': (v, 3), 'richtung': (v, 2), 'gewicht': (v,)})
        self.assertEqual(float(f['gewicht'].abs().sum()), 0.0)
