# -*- coding: utf-8 -*-
"""Die gerundete Zehenbox eines Schuhs (`G9hbschuhhuelle`, 05.10.2026).

Edgar (05.10.2026): „es ist immer noch eine Beule da, der Schuh muss oben gleichmässig sein, wie eine Rundung!“ Gemessen an F2_ShirtLeggins (Angie Sneakers,
`_wegwerf/edgar/schuh_ueberstand.py`): Der Hub aus der Haut gab der Kappe die Form der gespreizten Zehen. Zusagen (mit einem Kunstfuss, ohne Netze):

1. Die Kappe steht mindestens `HUELLE_ABSTAND` über der konvexen Hülle der Vorfuss-Haut (Zehenlücken überbrückt).
2. Eine einzelne Spitze in der Kappe wird abgeflacht.
3. Die Sohle (unter `KAPPE_AB`) und alles hinter `VORFUSS_AB` bleiben unberührt.
4. Beide Seiten (x > 0, x < 0) werden behandelt.
5. Ohne genug Hautpunkte des Vorfusses bleibt der Schuh, wie er ist — kein Fehler.
"""
from types import SimpleNamespace

import numpy as np
from django.test import SimpleTestCase

from core.dienste.g9hbschuhhuelle import G9hbschuhhuelle


def _haut(seite=1.0, n=400):
    """Vorfuss als Quader: x 0,06–0,12 (je Seite), y 0–0,03, z 0,15–0,23."""
    zufall = np.random.RandomState(3)
    punkte = np.column_stack([zufall.uniform(0.06, 0.12, n) * seite, zufall.uniform(0.0, 0.03, n), zufall.uniform(0.15, 0.23, n)])
    return punkte, np.tile([0.0, 1.0, 0.0], (n, 1))


def _traeger(haut):
    return SimpleNamespace(koerperflaeche=lambda: (haut[0], haut[1], None))


def _kappe(seite=1.0, hoehe=0.045):
    """Dichtes Raster der Kappe ueber dem Vorfuss (4 mm), eine Spitze in der Mitte."""
    xs, zs = np.meshgrid(np.arange(0.06, 0.1201, 0.004), np.arange(0.15, 0.2301, 0.004))
    punkte = np.column_stack([xs.ravel() * seite, np.full(xs.size, hoehe), zs.ravel()])
    mitte = int(np.argmin(np.abs(punkte[:, 0] - 0.09 * seite) + np.abs(punkte[:, 2] - 0.19)))
    punkte[mitte, 1] += 0.015
    return punkte, mitte


class DieGerundeteZehenbox(SimpleTestCase):
    def test_1_die_kappe_steht_ueber_der_huelle_der_haut(self):
        haut = _haut()
        kappe = np.column_stack([np.linspace(0.07, 0.11, 30), np.full(30, 0.031), np.linspace(0.16, 0.22, 30)])   # 1 mm ueber der Haut
        aus = G9hbschuhhuelle.runden(_traeger(haut), kappe)
        self.assertGreaterEqual(float(aus[:, 1].min()), 0.03 + G9hbschuhhuelle.HUELLE_ABSTAND - 1.5e-3)

    def test_2_eine_einzelne_spitze_wird_abgeflacht(self):
        haut = _haut()
        kappe, mitte = _kappe()
        aus = G9hbschuhhuelle.runden(_traeger(haut), kappe)
        self.assertLess(aus[mitte, 1], kappe[mitte, 1] - 0.005)
        self.assertGreater(aus[mitte, 1], 0.03 + G9hbschuhhuelle.HUELLE_ABSTAND - 1.5e-3)      # ... aber nicht in die Huelle

    def test_3_sohle_und_alles_hinter_dem_vorfuss_bleiben(self):
        haut = _haut()
        sohle = np.array([[0.09, 0.005, 0.2], [0.09, -0.01, 0.23]])
        hinten = np.array([[0.09, 0.03, 0.05], [0.09, 0.04, 0.08]])
        alle = np.vstack([sohle, hinten, _kappe()[0]])
        aus = G9hbschuhhuelle.runden(_traeger(haut), alle)
        np.testing.assert_array_equal(aus[:4], alle[:4])

    def test_4_beide_seiten_werden_behandelt(self):
        rechts = G9hbschuhhuelle.runden(_traeger(_haut(-1.0)), _kappe(-1.0)[0])
        links = G9hbschuhhuelle.runden(_traeger(_haut(1.0)), _kappe(1.0)[0])
        np.testing.assert_allclose(rechts[:, 1], links[:, 1], atol=1e-6)
        both = G9hbschuhhuelle.runden(_traeger((np.vstack([_haut(1.0)[0], _haut(-1.0)[0]]), np.zeros((800, 3)))),
                                      np.vstack([_kappe(1.0)[0], _kappe(-1.0)[0]]))
        self.assertAlmostEqual(float(both[:len(links), 1].max()), float(links[:, 1].max()), places=6)

    def test_5_ohne_genug_hautpunkte_bleibt_der_schuh(self):
        haut = (np.zeros((10, 3)), np.zeros((10, 3)))
        kappe = _kappe()[0]
        np.testing.assert_array_equal(G9hbschuhhuelle.runden(_traeger(haut), kappe), kappe)

    def test_6_leere_punkte_gehen_durch(self):
        self.assertEqual(G9hbschuhhuelle.runden(_traeger(_haut()), np.zeros((0, 3))).shape, (0, 3))
