# -*- coding: utf-8 -*-
"""Schamtiefenfeld — die Lücke zur Haut am Rand läuft als weiches Feld ins Stück (11.10.2026, „cute girl alt4").

Edgar, 11.10.2026: „alt3 hat eine Naht, und die Scham ist ca. 1 cm tiefer als die Haut daneben". Gemessen: 10–15 mm Lücke zwischen Original und Haut am Ring, die das Randband (8 mm) und das Ausklingen
der Naht (10–16 mm) nicht überbrücken. Kunstwelt: ein ebenes Stück (Gitter 13 × 13 Punkte, Zelle 4 mm, y = 0), dessen Rand VOR dem Einrasten 10 mm tiefer lag (`rand_vorher`).

1. `randpunkte` / `aussenring`: der Rand eines Gitters ist ein Ring von 48 Punkten; ein Loch im Innern ist ein weiterer Ring und kein Rand zur Haut.
2. `fortsetzen`: konstante Randwerte ergeben im Innern dieselbe Konstante, ein linearer Verlauf (x) bleibt linear (harmonisch); der Rand selbst bekommt 0.
3. `anwenden` ohne Einblenden: das ganze Innere hebt sich um die Lücke (10 mm), der Rand bleibt, wo er ist.
4. `anwenden` mit Einblenden: die erste Reihe hinter dem Rand folgt dem Feld nur zur Hälfte (Hermite bei halbem Weg), ab `EINBLENDEN_MM` ganz.
5. Ein Loch im Innern gibt dem Feld nichts vor (weder Rand noch Lücke); der Bericht zählt es als weiteren Ring.
6. `STAERKE` skaliert das Feld.

Die erwarteten Zahlen sind mit denselben Aufrufen nachgerechnet (`ProjektTemp/_wegwerf/tiefenfeld_erwartung.py`), die Tests selbst nicht gelaufen. Sabotage-Gegenprobe NICHT gemacht (erst auf Ansage): vorgesehen sind den Rand dem
Feld überlassen (Fall 3 rot), `aussenring` ohne Sortierung nach Länge (Fall 5 rot), `STAERKE` ignorieren (Fall 6 rot).

Nicht gelaufen (Stand 11.10.2026) — läuft nur auf Ansage.
"""
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.schamtiefenfeld import Schamtiefenfeld


class SchamtiefenfeldTest(SimpleTestCase):
    databases = set()

    N, ZELLE = 13, 0.004

    @classmethod
    def _gitter(cls, loch=False):
        """`(punkte, dreiecke)`: ebenes Gitter in y = 0, je Zelle zwei Dreiecke; mit `loch` fehlen die beiden Dreiecke einer Zelle in der Mitte."""
        n = cls.N
        punkte = np.array([[(c - n // 2) * cls.ZELLE, 0.0, (r - n // 2) * cls.ZELLE] for r in range(n) for c in range(n)])
        dreiecke = []
        for r in range(n - 1):
            for c in range(n - 1):
                a = r * n + c
                if loch and (r, c) == (n // 2, n // 2):
                    continue
                dreiecke += [[a, a + 1, a + n], [a + 1, a + n + 1, a + n]]
        return punkte, np.array(dreiecke, dtype=np.int64)

    def _rand_vorher(self, punkte, dreiecke, tiefer=0.010):
        return punkte[Schamtiefenfeld.randpunkte(dreiecke)] - np.array([0.0, tiefer, 0.0])

    def test_1_der_rand_eines_gitters_ist_ein_ring(self):
        punkte, dreiecke = self._gitter()
        self.assertEqual(len(Schamtiefenfeld.randpunkte(dreiecke)), 4 * (self.N - 1))
        ring, weitere = Schamtiefenfeld.aussenring(dreiecke)
        self.assertEqual(len(ring), 4 * (self.N - 1))
        self.assertEqual(len(set(ring.tolist())), len(ring), 'jeder Punkt einmal')
        self.assertEqual(weitere, 0)
        schritt = np.linalg.norm(punkte[np.roll(ring, -1)] - punkte[ring], axis=1)
        self.assertLessEqual(float(schritt.max()), self.ZELLE + 1e-12, 'in Reihenfolge: ein Schritt ist eine Kante')

    def test_2_fortsetzen_haelt_konstanten_und_lineare_verlaeufe(self):
        punkte, dreiecke = self._gitter()
        rand = Schamtiefenfeld.randpunkte(dreiecke)
        konstant, _ = Schamtiefenfeld.fortsetzen(punkte, dreiecke, rand, np.tile([0.0, 0.01, 0.0], (len(rand), 1)))
        innen = np.setdiff1d(np.arange(len(punkte)), rand)
        np.testing.assert_allclose(konstant[innen], np.tile([0.0, 0.01, 0.0], (len(innen), 1)), atol=1e-9)
        np.testing.assert_array_equal(konstant[rand], 0.0)
        linear, _ = Schamtiefenfeld.fortsetzen(punkte, dreiecke, rand, np.column_stack([punkte[rand][:, 0], np.zeros(len(rand)), np.zeros(len(rand))]))
        np.testing.assert_allclose(linear[innen][:, 0], punkte[innen][:, 0], atol=1e-9)

    def test_3_das_innere_hebt_sich_um_die_luecke_der_rand_bleibt(self):
        punkte, dreiecke = self._gitter()
        with mock.patch.object(Schamtiefenfeld, 'EINBLENDEN_MM', 0.0), mock.patch.object(Schamtiefenfeld, 'STAERKE', 1.0):
            neu, bericht = Schamtiefenfeld.anwenden(punkte, dreiecke, self._rand_vorher(punkte, dreiecke))
        rand = Schamtiefenfeld.randpunkte(dreiecke)
        innen = np.setdiff1d(np.arange(len(punkte)), rand)
        np.testing.assert_array_equal(neu[rand], punkte[rand])
        np.testing.assert_allclose(neu[innen][:, 1], 0.010, atol=1e-9)
        self.assertEqual(bericht['umgeklappt'], 0)
        self.assertAlmostEqual(bericht['luecke_median_mm'], 10.0, places=3)

    def test_4_das_einblenden_haelt_die_erste_reihe_zurueck(self):
        punkte, dreiecke = self._gitter()
        with mock.patch.object(Schamtiefenfeld, 'EINBLENDEN_MM', 8.0), mock.patch.object(Schamtiefenfeld, 'STAERKE', 1.0):
            neu, _ = Schamtiefenfeld.anwenden(punkte, dreiecke, self._rand_vorher(punkte, dreiecke))
        n = self.N
        reihe_1 = n * 1 + n // 2                    # eine Zelle (4 mm) vom Rand: Hermite(0,5) = 0,5
        reihe_3 = n * 3 + n // 2                    # 12 mm vom Rand: voll
        self.assertAlmostEqual(float(neu[reihe_1, 1]), 0.005, places=6)
        self.assertAlmostEqual(float(neu[reihe_3, 1]), 0.010, places=6)

    def test_5_ein_loch_im_innern_gibt_dem_feld_nichts_vor(self):
        punkte, dreiecke = self._gitter(loch=True)
        ring, weitere = Schamtiefenfeld.aussenring(dreiecke)
        self.assertEqual(len(ring), 4 * (self.N - 1), 'der äußere Ring ist der längere')
        self.assertEqual(weitere, 1)
        with mock.patch.object(Schamtiefenfeld, 'EINBLENDEN_MM', 0.0):
            neu, bericht = Schamtiefenfeld.anwenden(punkte, dreiecke, self._rand_vorher(punkte, dreiecke))
        self.assertEqual(bericht['weitere_ringe'], 1)
        np.testing.assert_allclose(neu[self.N * (self.N // 2) + self.N // 2][1], 0.010, atol=1e-9)

    def test_6_die_staerke_skaliert_das_feld(self):
        punkte, dreiecke = self._gitter()
        with mock.patch.object(Schamtiefenfeld, 'EINBLENDEN_MM', 0.0), mock.patch.object(Schamtiefenfeld, 'STAERKE', 0.5):
            neu, _ = Schamtiefenfeld.anwenden(punkte, dreiecke, self._rand_vorher(punkte, dreiecke))
        mitte = self.N * (self.N // 2) + self.N // 2
        self.assertAlmostEqual(float(neu[mitte, 1]), 0.005, places=6)
