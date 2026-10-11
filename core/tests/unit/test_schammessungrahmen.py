# -*- coding: utf-8 -*-
"""`Schammessungrahmen` — das Koordinatensystem und die Zonen der Scham-Messung (10.10.2026), mit Zahlen von Hand.

Edgar: „die Geometrie an verschiedenen Punkten gemessen". Alle Messungen lesen ihre Orte aus EINEM Rahmen, damit „Hügel", „Lippen" und „Damm" in Form, Naht und Textur dieselben Punkte meinen.

Rahmen: Mitte im Ursprung, `vorne` = +z, dann ist `quer` = +x und `laengs` = +y (nach oben); Stück 40 mm breit (x ±20), 60 mm lang (y ±30), 10 mm tief.

1. `koordinaten` rechnet in (quer, längs, vorne) um; die `grenzen` kommen aus dem Stück.
2. Die Zonen: Drittel von oben nach unten (Hügel, Lippen, Damm), je Mitte (|quer| < 12 mm) und seitlich — `zone` und `zonenname` stimmen mit der Hand überein.
3. `spiegeln` an der Mittelebene dreht nur das Vorzeichen von quer um.
4. `tabelle` fasst Werte je Zone zusammen und lässt leere Zonen weg; `statistik` ist None ohne endliche Werte.
5. `von_ring`: Mitte = Mittel der Ringpunkte, vorne = gemittelte Normale.
"""
import numpy as np
from django.test import SimpleTestCase

from core.dienste.schammessungrahmen import Schammessungrahmen


class SchammessungrahmenTest(SimpleTestCase):
    databases = set()

    def _rahmen(self):
        stueck = np.array([[-0.020, -0.030, 0.0], [0.020, 0.030, 0.010]])
        return Schammessungrahmen([0.0, 0.0, 0.0], [0.0, 0.0, 2.0], stueck)

    def test_1_koordinaten_und_grenzen(self):
        r = self._rahmen()
        self.assertEqual(r.quer.round(9).tolist(), [1.0, 0.0, 0.0])
        self.assertEqual(r.laengs.round(9).tolist(), [0.0, 1.0, 0.0])
        self.assertEqual(r.koordinaten([[0.01, 0.02, 0.005]]).round(9).tolist(), [[0.01, 0.02, 0.005]])
        self.assertEqual([tuple(round(x, 9) for x in g) for g in r.grenzen], [(-0.02, 0.02), (-0.03, 0.03), (0.0, 0.01)])

    def test_2_die_zonen_stimmen_mit_der_hand(self):
        r = self._rahmen()
        punkte = np.array([[0.0, 0.025, 0.0], [0.0, 0.0, 0.0], [0.0, -0.028, 0.0], [0.015, 0.0, 0.0], [-0.015, 0.025, 0.0], [0.011, -0.025, 0.0]])
        zonen = r.zone(punkte)
        self.assertEqual(zonen.tolist(), [0, 2, 4, 3, 1, 4], 'Hügel Mitte, Lippen Mitte, Damm Mitte, Lippen seitlich, Hügel seitlich, Damm Mitte (11 mm < 12 mm)')
        self.assertEqual(r.zonenname(0), 'Hügel (oben), Mitte')
        self.assertEqual(r.zonenname(3), 'Lippen (mitte), seitlich')
        self.assertEqual(r.zonenname(4), 'Damm (unten), Mitte')

    def test_3_spiegeln_dreht_nur_quer_um(self):
        r = self._rahmen()
        self.assertEqual(r.spiegeln([[0.01, 0.02, 0.005]]).round(9).tolist(), [[-0.01, 0.02, 0.005]])

    def test_4_tabelle_und_statistik(self):
        r = self._rahmen()
        punkte = np.array([[0.0, 0.025, 0.0], [0.0, 0.026, 0.0], [0.0, -0.028, 0.0]])
        zeilen = r.tabelle([1.0, 3.0, 10.0], punkte)
        self.assertEqual([z['zone'] for z in zeilen], ['Hügel (oben), Mitte', 'Damm (unten), Mitte'])
        self.assertEqual((zeilen[0]['n'], zeilen[0]['median'], zeilen[1]['median']), (2, 2.0, 10.0))
        self.assertIsNone(Schammessungrahmen.statistik([float('nan'), float('inf')]))
        self.assertEqual(Schammessungrahmen.statistik([1.0, 2.0, 3.0, float('nan')])['n'], 3)

    def test_5_von_ring_nimmt_die_mitte_und_die_mittlere_normale(self):
        figur = np.array([[0.0, 0.0, 0.0], [0.02, 0.0, 0.0], [0.0, 0.02, 0.0], [0.5, 0.5, 0.5]])
        normalen = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]])
        r = Schammessungrahmen.von_ring(figur, normalen, [0, 1, 2], np.array([[0.0, 0.0, 0.0], [0.01, 0.01, 0.01]]))
        self.assertAlmostEqual(float(r.mitte[0]), 0.02 / 3, places=9)
        self.assertAlmostEqual(float(r.mitte[1]), 0.02 / 3, places=9)
        self.assertEqual(r.vorne.round(9).tolist(), [0.0, 0.0, 1.0])
