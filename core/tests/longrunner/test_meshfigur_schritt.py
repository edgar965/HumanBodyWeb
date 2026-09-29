# -*- coding: utf-8 -*-
"""Der Bereich SCHRITT der Genesis-9-Grundfigur (29.09.2026) — an der Daz-Bibliothek, darum LongRunner.

Gemessen (`ProjektTemp/_wegwerf/meshto3d/schritt_bereich_messen.py`): 280 von 25.182 Käfigpunkten — die 170 des Morphs
`Hip Genital Bulge` samt zwei Kantenringen —, x ±8,1 cm, y 0,80–0,95 m, z −3,2…+10,1 cm (Füße auf 0), 260 davon am
Becken, je 10 an den Oberschenkeln. NICHT gelaufen (Tests nur auf Ansage).
"""

import unittest

import numpy as np
from django.test import SimpleTestCase
from Genesis9.formung import G9formung
from Genesis9.morphablage import G9morphablage
from Genesis9.netzbereiche import G9netzbereiche
from Genesis9.pfade import G9pfade


@unittest.skipUnless(G9pfade.vorhanden(), 'Daz-Bibliothek fehlt')
class SchrittBereichTest(SimpleTestCase):
    def setUp(self):
        self.bereich = G9netzbereiche.bereiche()
        self.schritt = np.flatnonzero(self.bereich == G9netzbereiche.SCHRITT)

    def test_alle_morphpunkte_und_ein_paar_dazu(self):
        morph = G9morphablage.holen().deltas(G9netzbereiche.SCHRITT_MORPH)
        self.assertIsNotNone(morph)
        self.assertTrue(np.isin(morph[0], self.schritt).all())
        self.assertGreater(len(self.schritt), len(morph[0]))
        self.assertLess(len(self.schritt), 4 * len(morph[0]))  # ein Klecks, nicht der halbe Körper

    def test_lage_am_becken_zwischen_den_beinen(self):
        f = G9formung({})
        p = np.asarray(f.punkte(), dtype=float) - np.array([0.0, f.boden(), 0.0])
        s = p[self.schritt]
        self.assertLess(np.abs(s[:, 0]).max(), 0.10)
        self.assertGreater(s[:, 1].min(), 0.75)
        self.assertLess(s[:, 1].max(), 1.0)

    def test_nur_becken_und_ansatz_der_oberschenkel(self):
        from Genesis9.haut import G9haut
        from Genesis9.koerperteile import G9koerperteile

        teil = G9koerperteile.genesis_punkte(G9haut.holen())
        namen = {v: k for k, v in G9koerperteile.NUMMER.items()}
        self.assertLessEqual({namen[int(k)] for k in np.unique(teil[self.schritt])}, {'becken', 'l_oberschenkel', 'r_oberschenkel'})

    def test_der_steckbrief_zaehlt_jeden_punkt_einmal(self):
        self.assertEqual(sum(G9netzbereiche.steckbrief().values()), len(self.bereich))
        self.assertEqual(G9netzbereiche.steckbrief()['schritt'], len(self.schritt))
