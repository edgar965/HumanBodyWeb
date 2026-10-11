# -*- coding: utf-8 -*-
"""`Schammessungnaht` — wie sitzt der Rand des Scham-Stücks auf dem Loch der Haut? (10.10.2026), an der Kunsthaut `_nahtwelt.Nahtwelt`.

Edgar: „die Naht ist noch sichtbar". Die Zahlen, die vor dem Bild stehen: Rand ↔ Ring (0 heißt Kante an Kante, ein Spalt beginnt über ~0,1 mm), Glättung des Rings, Normalenwinkel am Rand.

1. Ein Stück, dessen Rand genau die 16 Ecken des Rings sind: 16 Randpunkte, Abstand Rand ↔ Ring 0 in beide Richtungen, Normalenwinkel 0°, nichts umgekehrt.
2. Liegt das ganze Stück 1 mm über dem Ring, beträgt der Abstand 1 mm (Median) — die Messung sieht den Spalt.
3. Ist das Stück gekippt (innerer Ring 5 mm hoch), kippen die Normalen am Rand: Winkel über 0°; ist die Wicklung umgekehrt (Dreiecke vertauscht), melden die Randpunkte `umgekehrt` 1.
4. `ring_d` (Verschiebung der Glättung) erscheint als `ring_glaettung_mm`.
5. `randpunkte` findet den Rand auch bei aufgespaltenen Punkten (UV-Nähte: jedes Dreieck mit eigenen Punkten) — dieselben 16.
6. Ein Stück ohne Rand (geschlossene Fläche) meldet einen Hinweis, keinen Fehler.

Sabotage-Gegenprobe (nicht gelaufen): `LAGE_M` auf 1e-12 stellen macht Fall 5 rot (die Nähte bleiben offen und zählen als Rand).
"""
import numpy as np
from django.test import SimpleTestCase

from core.dienste.schammessungnaht import Schammessungnaht

from ._nahtwelt import Nahtwelt


class SchammessungnahtTest(SimpleTestCase):
    databases = set()

    def _naht(self, abstand_mm=5.0, hub_mm=0.0, hoch_mm=0.0, umkehren=False, ring_d=None):
        _figur, loch = Nahtwelt.haut()
        punkte, dreiecke = Nahtwelt.stueck(abstand_mm, hub_mm)
        punkte = punkte + np.array([0.0, 0.0, hoch_mm / 1000.0])
        if umkehren:
            dreiecke = dreiecke[:, ::-1]
        normalen = np.tile([0.0, 0.0, 1.0], (len(loch['ring']), 1))
        return Schammessungnaht(punkte, dreiecke, loch['ring'], normalen, ring_d), punkte, dreiecke

    def test_1_rand_auf_dem_ring_misst_null(self):
        naht, _p, _d = self._naht()
        m = naht.messen()
        self.assertEqual((m['randpunkte'], m['ringecken']), (16, 16))
        self.assertEqual((m['rand_zu_ring_mm']['max'], m['ring_zu_rand_mm']['max']), (0.0, 0.0))
        self.assertLess(m['normalen_grad']['max'], 0.01)
        self.assertEqual(m['normalen_grad']['umgekehrt'], 0.0)

    def test_2_ein_spalt_wird_gemessen(self):
        m = self._naht(hoch_mm=1.0)[0].messen()
        self.assertAlmostEqual(m['rand_zu_ring_mm']['median'], 1.0, places=2)
        self.assertAlmostEqual(m['ring_zu_rand_mm']['max'], 1.0, places=2)

    def test_3_gekippte_und_umgekehrte_normalen(self):
        gekippt = self._naht(abstand_mm=5.0, hub_mm=5.0)[0].messen()
        self.assertGreater(gekippt['normalen_grad']['median'], 5.0)
        umgekehrt = self._naht(umkehren=True)[0].messen()
        self.assertEqual(umgekehrt['normalen_grad']['umgekehrt'], 1.0)
        self.assertLess(umgekehrt['normalen_grad']['max'], 0.01, 'der Betrag des Skalarprodukts: der Winkel ist 0, nur der Drehsinn fehlt')

    def test_4_die_verschiebung_der_glaettung_wird_gemeldet(self):
        d = np.zeros((16, 3))
        d[:4, 2] = 0.002
        m = self._naht(ring_d=d)[0].messen()
        self.assertEqual(m['ring_glaettung_mm']['max'], 2.0)
        self.assertNotIn('ring_glaettung_mm', self._naht()[0].messen())

    def test_5_randpunkte_findet_den_rand_auch_bei_aufgespaltenen_punkten(self):
        punkte, dreiecke = Nahtwelt.stueck(5.0)
        zusammen = Schammessungnaht.randpunkte(punkte, dreiecke)
        offen = Schammessungnaht.randpunkte(punkte[dreiecke].reshape(-1, 3), np.arange(len(dreiecke) * 3).reshape(-1, 3))
        self.assertEqual((len(zusammen), len(offen)), (16, 16))

    def test_6_ein_stueck_ohne_rand_gibt_einen_hinweis(self):
        tetraeder = np.array([[0.0, 0.0, 0.0], [0.01, 0.0, 0.0], [0.0, 0.01, 0.0], [0.0, 0.0, 0.01]])
        faces = np.array([[0, 2, 1], [0, 1, 3], [1, 2, 3], [0, 3, 2]])
        naht = Schammessungnaht(tetraeder, faces, np.zeros((0, 3)), np.zeros((0, 3)))
        self.assertIn('hinweis', naht.messen())
