# -*- coding: utf-8 -*-
"""Haarstraehnen — die Strähnen eines Stranghaar-Teils für die Haar-Dynamik (02.10.2026): Index-Rückabbildung auf die Käfigpunkte,
die Wurzel zuerst, die Wurzeln ohne Delta, die Wurzelnormale. Kunstdaten (`Haardaten`), keine Bibliothek.

Gemessen an der echten Geometrie (Pixie, Hime Cut): `G9haarzusatz.ketten` liefert die Wurzel vorn, keine Kette wird umgedreht —
das hält der Test mit Kunstdaten für BEIDE Fälle fest (umgedreht, wo der erste Punkt fern der Haut liegt und der letzte nah;
unangetastet, wo beide Enden an der Haut liegen).

Sabotage-Gegenproben: in `Haarstraehnen.delta` die Zeile `aus[self.reihe[self.wurzeln]] = 0.0` weglassen → „Wurzeln bekommen
genau null“ rot; in `_wurzel_vorn` die Bedingung `(erst > cls.FERN_M)` weglassen → der flach liegende Fall rot (dessen letzter
Punkt liegt näher an der Haut als der erste, beide innerhalb von `FERN_M`)."""

import numpy as np
from django.test import SimpleTestCase
from Genesis9.haarzusatz import G9haarzusatz

from core.dienste.haarstraehnen import Haarstraehnen

from ._haardaten import Haardaten

HAUT = Haardaten.haut()
PUNKTE = Haardaten.punkte()


def straehnen(segmente=Haardaten.SEGMENTE, punkte=PUNKTE, haut=HAUT):
    return Haarstraehnen(punkte, G9haarzusatz.ketten(segmente, len(punkte)), haut)


class HaarstraehnenTest(SimpleTestCase):
    def test_die_index_rueckabbildung_legt_das_delta_auf_die_kaefigpunkte_der_ketten(self):
        s = straehnen()
        self.assertEqual(s.reihe.tolist(), [4, 1, 7, 2, 9, 0, 5])
        self.assertEqual((s.laengen.tolist(), s.wurzeln.tolist()), ([4, 3], [0, 4]))
        np.testing.assert_array_equal(s.punkte, PUNKTE[s.reihe])
        lage = s.punkte.astype(np.float32).astype(np.float64) + (0.0, -0.02, 0.0)
        delta = s.delta(lage)
        np.testing.assert_allclose(delta[[1, 7, 2, 0, 5]], (0.0, -0.02, 0.0), atol=1e-12)
        np.testing.assert_array_equal(delta[[3, 6, 8]], 0.0)                         # Punkte ohne Kette bleiben stehen

    def test_die_wurzeln_bekommen_genau_null_auch_wenn_der_solver_rundungsrauschen_liefert(self):
        s = straehnen()
        delta = s.delta(s.punkte.astype(np.float32).astype(np.float64) + 1e-7)
        np.testing.assert_array_equal(delta[[4, 9]], 0.0)
        self.assertGreater(float(np.abs(delta[[1, 7, 2, 0, 5]]).min()), 0.0)

    def test_eine_falsche_form_oder_nicht_endliche_punkte_sind_ein_klarer_fehler(self):
        s = straehnen()
        with self.assertRaises(ValueError):
            s.delta(s.punkte[:-1])
        lage = s.punkte.copy()
        lage[2, 1] = np.nan
        with self.assertRaises(RuntimeError) as fehler:
            s.delta(lage)
        self.assertIn('nicht endlich', str(fehler.exception))

    def test_eine_kette_mit_der_wurzel_hinten_wird_umgedreht_eine_flach_liegende_nicht(self):
        punkte = np.array([(0.0, 0.10, 0.0), (0.0, 0.003, 0.0), (0.5, 0.010, 0.0), (0.5, 0.002, 0.2)])
        s = straehnen(np.array([(0, 1), (2, 3)]), punkte)
        self.assertEqual(s.umgedreht, 1)
        self.assertEqual(s.reihe.tolist(), [1, 0, 2, 3])                              # Kette 0 → 1: Wurzel (an der Haut) vorn
        s = straehnen(np.array([(2, 3)]), punkte)
        self.assertEqual((s.umgedreht, s.reihe.tolist()), (0, [2, 3]))               # beide Enden nah an der Haut: unangetastet

    def test_die_wurzelnormale_zeigt_nach_aussen_auch_bei_verkehrter_dreiecksreihenfolge(self):
        for dreiecke in (HAUT['dreiecke'], HAUT['dreiecke'][:, ::-1]):
            s = straehnen(haut=dict(HAUT, dreiecke=dreiecke))
            np.testing.assert_allclose(s.normalen, [(0.0, 1.0, 0.0)] * 2, atol=1e-9)
            self.assertEqual(s.normalen_ausgerichtet, 1.0)

    def test_der_abstand_der_wurzeln_zur_haut_steht_im_steckbrief(self):
        s = straehnen()
        self.assertEqual((s.wurzel_fern, s.wurzel_abstand_max_mm), (0, 4.0))
        fern = PUNKTE.copy()
        fern[4, 1] = 0.5
        self.assertEqual(straehnen(punkte=fern).wurzel_fern, 1)

    def test_ketten_die_sich_einen_punkt_teilen_stehen_als_doppelt_im_steckbrief(self):
        s = straehnen(np.array([(4, 1), (9, 1)]))                                    # zwei Ketten münden im Punkt 1
        self.assertEqual(s.doppelt, 1)
        self.assertEqual(straehnen().doppelt, 0)
