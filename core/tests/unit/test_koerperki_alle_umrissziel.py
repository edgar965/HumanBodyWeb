# -*- coding: utf-8 -*-
"""Tests für `KoerperKI_alle.umrissziel.Umrissziel` (24.10.2026, Besitzer 2d-3d-AI): Abstand zum Umriss, Haut, nah, Deckung — an einem Quadrat als Person.

WARUM: Das Einpassen der Figur in die Fotos (`KoerperKI_Fotos.Fotoeinpassung`) rechnet Umriss, Haut und Rand nur über diese Klasse, und Mesh3D-AI kann sie für gerenderte Netzansichten nehmen.
Ein Abstandsfeld, das in Bildpunkten der kleinen Karte statt des ganzen Bildes misst, oder ein Rand, der nach außen nicht weiter wächst, ließe die Figur stumm aus dem Umriss laufen.
"""
import sys
import unittest

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_alle.umrissziel import Umrissziel  # noqa: E402


class DasUmrissziel(unittest.TestCase):
    """Person = Quadrat x, y ∈ [16, 48) in einem Bild 64 × 64."""

    def setUp(self):
        self.person = torch.zeros((64, 64), dtype=torch.bool)
        self.person[16:48, 16:48] = True

    def test_abstand_genau_bei_teiler_eins(self):
        z = Umrissziel(self.person, teiler=1)
        uv = torch.tensor([[32.0, 32.0], [60.0, 32.0], [32.0, 3.0], [-10.0, 32.0]])
        self.assertEqual([round(v, 3) for v in z.aussen(uv).tolist()], [0.0, 13.0, 13.0, 26.0])    # rechts 60 − 47, oben 16 − 3, links außerhalb des Bildes 16 + 10

    def test_abstand_in_bildpunkten_des_ganzen_bildes_bei_teiler_vier(self):
        z = Umrissziel(self.person, teiler=4)
        d = z.aussen(torch.tensor([[32.0, 32.0], [60.0, 32.0], [32.0, 3.0], [80.0, 32.0]])).tolist()
        self.assertEqual(d[0], 0.0)
        for ist, soll in zip(d[1:], (13.0, 13.0, 33.0), strict=True):
            self.assertAlmostEqual(ist, soll, delta=4.0)

    def test_gradient_zeigt_nach_aussen(self):
        z = Umrissziel(self.person, teiler=1)
        uv = torch.tensor([[60.0, 32.0], [32.0, 60.0]], requires_grad=True)
        z.aussen(uv).sum().backward()
        g = uv.grad
        self.assertGreater(float(g[0, 0]), 0.5)
        self.assertGreater(float(g[1, 1]), 0.5)
        self.assertLess(abs(float(g[0, 1])), 0.1)

    def test_haut_auf_dem_koerper_ist_null(self):
        haut = self.person.clone()
        haut[:, 32:] = False
        z = Umrissziel(self.person, haut, teiler=1)
        ys, xs = torch.nonzero(self.person, as_tuple=True)
        koerper = torch.stack([xs, ys], 1).float()
        self.assertEqual(float(z.haut(koerper).max()), 0.0)
        self.assertGreaterEqual(float(z.haut(koerper + torch.tensor([20.0, 0.0])).min()), 4.0)     # Haut x 16…31, Körper ab x 36

    def test_ohne_haut_leer(self):
        z = Umrissziel(self.person, None)
        self.assertEqual(len(z.haut(torch.zeros((5, 2)))), 0)
        z = Umrissziel(self.person, torch.zeros_like(self.person))
        self.assertIsNone(z.haut_uv)

    def test_nah_zaehlt_nur_unter_der_grenze(self):
        z = Umrissziel(self.person, teiler=1)
        mitte = torch.tensor([[31.5, 31.5]])
        self.assertEqual(float(z.nah(mitte, 10.0).abs().sum()), 0.0)            # Rand 15,5 … 22 px von der Mitte
        weit = z.nah(mitte, 100.0)
        self.assertGreaterEqual(float(weit.min()), 15.5)
        self.assertLessEqual(float(weit.max()), 22.0)

    def test_randpunkte_liegen_auf_dem_rand(self):
        z = Umrissziel(self.person, teiler=1)
        x, y = z.rand_uv[:, 0], z.rand_uv[:, 1]
        auf = (x == 16) | (x == 47) | (y == 16) | (y == 47)
        self.assertTrue(bool(auf.all()))

    def test_deckung(self):
        z = Umrissziel(self.person)
        haelfte = self.person.clone()
        haelfte[:, 32:] = False
        self.assertEqual(z.deckung(self.person), 1.0)
        self.assertEqual(z.deckung(haelfte), 0.5)
        self.assertEqual(z.deckung(torch.zeros_like(self.person)), 0.0)

    def test_gleiche_saat_gleiche_punkte(self):
        a, b = Umrissziel(self.person, self.person, saat=3), Umrissziel(self.person, self.person, saat=3)
        self.assertTrue(torch.equal(a.haut_uv, b.haut_uv))
        self.assertTrue(torch.equal(a.rand_uv, b.rand_uv))
