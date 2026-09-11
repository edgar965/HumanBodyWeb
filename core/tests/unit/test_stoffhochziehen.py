# -*- coding: utf-8 -*-
u"""`Stoffhochziehen`: eine Hose hochziehen, bevor sie angelegt wird.

Kunstkoerper: zwei Beine (Zylinder, Radius 8 cm, bei x = -12 und +12 cm,
z 0..0,80) mit Fuessen (breite Scheibe, z 0..0,05) und ein Rumpf darueber
(Zylinder Radius 22 cm, z 0,80..1,60). Der Schritt liegt damit bei
z = 0,80 (die Haelfte der Hoehe, wie beim Menschen), der Knoechel bei
z = 0,05 (dort endet der Fuss).

Sabotage-Gegenprobe: `HOSE_AB_M = 10.0` (keine Hose erkannt) macht
`test_hose_wird_hochgezogen` rot; `KNOECHEL_ANTEIL = (0.2, 0.3)` macht
`test_saum_kommt_auf_den_knoechel` rot; `koerperseiten` ohne z-Bedingung
macht `test_koerperseiten` rot.
"""
import numpy as np
from django.test import SimpleTestCase

from GarmentCode.stoffhochziehen import Stoffhochziehen


def _zylinder(x0, radius, z_von, z_bis, n=36, reihen=None):
    reihen = reihen or max(2, int((z_bis - z_von) / 0.01))
    w = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ringe = [np.column_stack([x0 + radius * np.cos(w), radius * np.sin(w), np.full(n, z)])
             for z in np.linspace(z_von, z_bis, reihen)]
    return np.vstack(ringe)


def _koerper():
    teile = []
    for x0 in (-0.12, 0.12):
        teile.append(_zylinder(x0, 0.08, 0.05, 0.80))
        teile.append(_zylinder(x0, 0.13, 0.0, 0.05, reihen=6))       # Fuss
    teile.append(_zylinder(0.0, 0.22, 0.80, 1.60))                   # Rumpf
    teile.append(np.array([[0.0, 0.0, 0.80]]))                       # der Schritt
    return np.vstack(teile)


def _hose():
    u"""Zwei Stoffrohre um die Beine, Schritt 15 cm unter dem Koerperschritt,
    Saum 4 cm unter dem Boden, Bund bei z 1,10 (45 cm ueber dem Hosenschritt)."""
    teile = [_zylinder(x0, 0.10, -0.04, 0.65) for x0 in (-0.12, 0.12)]
    teile.append(_zylinder(0.0, 0.26, 0.65, 1.10))
    teile.append(np.array([[0.0, 0.0, 0.65]]))                       # Hosenschritt
    return np.vstack(teile)


class StoffhochziehenTest(SimpleTestCase):

    databases = []

    def setUp(self):
        self.hoch = Stoffhochziehen(_koerper())

    def test_koerperschritt_und_knoechel(self):
        self.assertIsNotNone(self.hoch.schritt)
        self.assertAlmostEqual(self.hoch.schritt[1], 0.80, delta=0.005)
        self.assertAlmostEqual(self.hoch.schritt[0], 0.0, delta=0.005)
        self.assertIsNotNone(self.hoch.knoechel)
        self.assertGreaterEqual(self.hoch.knoechel, 0.05)
        self.assertLess(self.hoch.knoechel, 0.09)

    def test_hose_wird_hochgezogen(self):
        hose = _hose()
        self.assertAlmostEqual(self.hoch.hosenschritt(hose), 0.65, delta=1e-9)
        neu, bilanz = self.hoch.anwenden(hose)
        schritt = neu[-1]
        self.assertAlmostEqual(schritt[2], 0.80, delta=0.005, msg=schritt)
        self.assertAlmostEqual(bilanz['hochgezogen_mm'], 150.0, delta=5)
        # Der Bund bleibt, wo die Simulation ihn liess (`AUSLAUF_M` darueber).
        self.assertAlmostEqual(neu[:, 2].max(), 1.10, delta=1e-6)
        # Die Hoehe bleibt monoton: kein Punkt ueberholt einen anderen.
        reihe = np.argsort(hose[:, 2])
        self.assertTrue((np.diff(neu[reihe, 2]) >= -1e-9).all())
        # x und y unveraendert — nur die Hoehe wird umgerechnet.
        np.testing.assert_allclose(neu[:, :2], hose[:, :2])

    def test_saum_kommt_auf_den_knoechel(self):
        neu, bilanz = self.hoch.anwenden(_hose())
        self.assertAlmostEqual(neu[:, 2].min(), self.hoch.knoechel, delta=1e-6)
        self.assertGreater(bilanz['saum_gehoben_mm'], 80)

    def test_saum_ueber_dem_knoechel_bleibt(self):
        u"""Eine Dreiviertelhose endet, wo sie endet."""
        hose = _hose()
        hose = hose[hose[:, 2] > 0.30]
        neu, bilanz = self.hoch.anwenden(hose)
        self.assertAlmostEqual(neu[:, 2].min(), hose[:, 2].min(), delta=1e-6)
        self.assertEqual(bilanz['saum_gehoben_mm'], 0.0)

    def test_rock_bleibt_unangetastet(self):
        u"""Ohne Schritt keine Hose: tiefster Mittelpunkt IST der Saum."""
        rock = _zylinder(0.0, 0.26, 0.55, 1.10)
        rock = np.vstack([rock, [[0.0, 0.0, 0.55]]])
        self.assertIsNone(self.hoch.hosenschritt(rock))
        neu, bilanz = self.hoch.anwenden(rock)
        np.testing.assert_allclose(neu, rock)
        self.assertEqual(bilanz['hochgezogen_mm'], 0.0)

    def test_koerperseiten(self):
        seiten = self.hoch.koerperseiten()
        k = self.hoch.koerper
        unten = k[:, 2] < 0.80
        self.assertTrue((seiten[unten & (k[:, 0] < 0)] == -1).all())
        self.assertTrue((seiten[unten & (k[:, 0] > 0)] == 1).all())
        self.assertTrue((seiten[~unten] == 0).all())
        stoff = self.hoch.stoffseiten(np.array([[-0.2, 0, 0.3], [0.2, 0, 0.3], [0.2, 0, 1.0]]))
        self.assertEqual(stoff.tolist(), [-1, 1, 1])

    def test_ohne_schritt_kein_absturz(self):
        u"""Ein Koerper ohne Beine (eine Saeule): unter dem tiefsten
        Mittelpunkt ist keine Luft, also kein Schritt — nichts wird getan."""
        hoch = Stoffhochziehen(_zylinder(0.3, 0.08, 0.0, 1.6))
        self.assertIsNone(hoch.schritt)
        hose = _hose()
        neu, _ = hoch.anwenden(hose)
        np.testing.assert_allclose(neu, hose)
        self.assertTrue((hoch.koerperseiten() == 0).all())
