# -*- coding: utf-8 -*-
"""Scham-Stück ohne Verformung (Edgar, 09.10.2026: „warum so unregelmäßig???"): `Blendimportschamregister.anwenden` verschiebt das GANZE Stück um den Median
der Umgebung.

Gemessen an „cute girl" (`ProjektTemp/_wegwerf/scham_naht/register_proto.py`; das Original ist symmetrisch, Spiegelabstand 0,34 mm): die Fassung davor
(1/d²-gewichtete Vektoren der Umgebung, danach des Rands) schob die Lippen im Median um 9,8 mm und machte sie unsymmetrisch (Spiegelabstand p90 5,6 mm);
eine einheitliche Verschiebung lässt sie bei 1,1 mm (0,43 mm).

Kunstwelt: Figur = die Ebene y = 0 (trimesh); Umgebung = Punkte eines Rasters (x, z) um das Stück, y = Höhe über der Figur; Stück = Raster 5 × 5 bei y = 0,02.

1. Steht die Umgebung links 1 mm und rechts 9 mm über der Figur, bekommen ALLE Punkte des Stücks dieselbe Verschiebung (Median: 5 mm, nach unten); die Form des
   Stücks bleibt (Abstände der Punkte untereinander unverändert).
2. Der Bericht nennt die Länge der Verschiebung (5,0 mm).
3. Steht die Umgebung 50 mm über der Figur (mehr als `MAX_SCHUB_MM` 20), gibt es kein Stück (`aus`), und die Punkte bleiben.

Sabotage-Gegenprobe (nicht gelaufen): in `anwenden` `_verschieben` durch die gewichtete Verschiebung (`_schritt`) ersetzen macht Fall 1 rot (die Punkte links und rechts
bekommen verschiedene Verschiebungen); `MAX_SCHUB_MM` auf 1000 macht Fall 3 rot.
"""

import numpy as np
import trimesh
from django.test import SimpleTestCase

from core.dienste.blendimportschamregister import Blendimportschamregister


class SchamregisterTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _figur():
        return trimesh.Trimesh(np.array([[-1, 0, -1], [1, 0, -1], [1, 0, 1], [-1, 0, 1]], dtype=float), np.array([[0, 1, 2], [0, 2, 3]]), process=False)

    @staticmethod
    def _umgebung(hoehe_links, hoehe_rechts):
        """10 × 10 Punkte (x, z ∈ ±20 mm, je 5 Spalten links und rechts von x = 0): alle liegen innerhalb von 25 mm um das Stück."""
        raster = np.linspace(-0.02, 0.02, 10)
        return np.array([[x, hoehe_links if x < 0 else hoehe_rechts, z] for x in raster for z in raster])

    @staticmethod
    def _stueck(hoehe=0.02):
        return np.array([[x, hoehe, z] for x in np.linspace(-0.01, 0.01, 5) for z in np.linspace(-0.01, 0.01, 5)])

    def _anwenden(self, umgebung, hoehe=0.02):
        stueck = self._stueck(hoehe)
        return stueck, Blendimportschamregister.anwenden(self._figur(), umgebung, np.ones(len(umgebung)), stueck)

    def test_1_alle_punkte_bekommen_dieselbe_verschiebung(self):
        stueck, (neu, _) = self._anwenden(self._umgebung(0.001, 0.009))
        schub = neu - stueck
        self.assertTrue(np.allclose(schub, schub[0], atol=1e-9), schub.std(axis=0))
        self.assertTrue(np.allclose(schub[0], [0.0, -0.005, 0.0], atol=1e-4), schub[0])

    def test_2_der_bericht_nennt_die_laenge_der_verschiebung(self):
        _, (_, bericht) = self._anwenden(self._umgebung(0.001, 0.009))
        self.assertAlmostEqual(bericht['umgebung']['verschiebung_mm'], 5.0, delta=0.3)

    def test_3_weicht_die_umgebung_zu_weit_ab_gibt_es_kein_stueck(self):
        stueck, (neu, bericht) = self._anwenden(self._umgebung(0.05, 0.05), hoehe=0.05)
        self.assertIn('aus', bericht)
        self.assertTrue(np.array_equal(neu, stueck))
