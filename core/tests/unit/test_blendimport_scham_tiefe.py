# -*- coding: utf-8 -*-
"""Scham-Stück ohne „Steg" (Edgar, 09.10.2026: „der ‚Steg' am Ende der Vulva, zum Anus, der muss weg"): `Blendimportschamtiefe` rückt die
Tiefengrenzen des Schnitts dorthin, wo das Original auf der Figur aufliegt.

Gemessen an „cute girl" (`ProjektTemp/_wegwerf/scham_naht/tiefe_proto.py`): hinten bei Saat − 20 mm (z = −21) weicht das Original noch um 11,6 mm von
der Figur ab, erst bei z ≈ −49 mm um weniger als 2 mm. Der Rand des Stücks lag 10 mm neben dem Ring, das Verschweißen zog ihn dorthin.

Kunstwelt: Figur = die Ebene y = 0 (trimesh), Original = Punkte in einem Raster (x, z) mit y = Höhe über der Figur. Saat bei z ∈ [0, 0,05], Zugabe 20 mm.

1. Das Original steht bis z = −0,02 12 mm über der Figur und fällt dann auf 0 bei z = −0,05: die Grenze hinten rückt auf ≈ −0,048 (zwei flache Scheiben).
2. Liegt hinter der Grenze gar kein Original (das Raster endet bei z = −0,03), gilt sie wie gegeben: −0,02 — der Schnitt geht durch nichts.
3. Liegt das Original überall auf der Figur, bleibt die Grenze bei Saat − Zugabe.
4. Steht es überall 12 mm darüber, rückt die Grenze höchstens `MAX_MM` hinaus (nicht endlos).
5. Vorn ist es dasselbe Verfahren: das Original endet bei z = 0,06, die Grenze (0,07) liegt dahinter → gilt wie gegeben.

Sabotage-Gegenprobe (nicht gelaufen, aus dem Code gelesen): `FLACH_MM` 2 → 20 macht Fall 1 rot (die Grenze bleibt bei −0,02); `FLACH_MM` 2 → 0,001 macht Fall 3 nicht
rot, wohl aber Fall 1 (flach ist erst, wo das Original genau auf 0 liegt: die Grenze rückt auf −0,054, außerhalb der Toleranz).
"""

import numpy as np
import trimesh
from django.test import SimpleTestCase

from core.dienste.blendimportschamtiefe import Blendimportschamtiefe


class SchamtiefeTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _figur():
        return trimesh.Trimesh(np.array([[-1, 0, -1], [1, 0, -1], [1, 0, 1], [-1, 0, 1]], dtype=float), np.array([[0, 1, 2], [0, 2, 3]]), process=False)

    @staticmethod
    def _original(z_von, z_bis, hoehe):
        """Raster x ∈ [−0,02, 0,02] (5 mm), z von `z_von` bis `z_bis` (1 mm); y = `hoehe(z)`."""
        zs = np.arange(z_von, z_bis, 0.001)
        return np.array([[x, hoehe(z), z] for z in zs for x in np.arange(-0.02, 0.0201, 0.005)])

    def _grenzen(self, original):
        return Blendimportschamtiefe.grenzen(original, np.ones(len(original), dtype=bool), np.array([0.0, 0.05]), 20.0, self._figur())

    def test_1_die_grenze_hinten_rueckt_dorthin_wo_das_original_aufliegt(self):
        original = self._original(-0.08, 0.06, lambda z: 0.012 if z >= -0.02 else max(0.0, 0.012 * (z + 0.05) / 0.03))
        hinten, _ = self._grenzen(original)
        self.assertTrue(-0.052 <= hinten <= -0.044, hinten)

    def test_2_ohne_original_hinter_der_grenze_gilt_sie_wie_gegeben(self):
        """Das Raster beginnt VOR der Grenze (−0,015 > −0,02): die erste Scheibe hinter ihr ist leer, der Schnitt geht durch nichts."""
        original = self._original(-0.015, 0.06, lambda z: 0.012)
        hinten, _ = self._grenzen(original)
        self.assertAlmostEqual(hinten, -0.02, places=6)

    def test_2b_endet_das_original_hinter_der_grenze_endet_auch_die_grenze_dort(self):
        """Das Raster reicht bis −0,03 (10 mm hinter die Grenze) und steht überall 12 mm über der Figur: die Grenze rückt, bis die Scheibe innen leer ist —
        auf das 4-mm-Raster der Scheiben gerundet (gemessen 10.10.2026: −0,036). Vorher stand hier die Erwartung −0,02 mit der Begründung „kein Original
        dahinter" — das Raster lag aber 10 mm dahinter."""
        original = self._original(-0.03, 0.06, lambda z: 0.012)
        hinten, _ = self._grenzen(original)
        self.assertTrue(-0.03 - 2 * Blendimportschamtiefe.SCHRITT_MM / 1000.0 <= hinten <= -0.03, hinten)

    def test_3_liegt_das_original_ueberall_auf_bleibt_die_grenze(self):
        hinten, vorn = self._grenzen(self._original(-0.08, 0.1, lambda z: 0.0))
        self.assertAlmostEqual(hinten, -0.02, places=6)
        self.assertAlmostEqual(vorn, 0.07, places=6)

    def test_4_es_geht_nicht_endlos_hinaus(self):
        hinten, _ = self._grenzen(self._original(-0.2, 0.06, lambda z: 0.012))
        self.assertTrue(-0.02 - Blendimportschamtiefe.MAX_MM / 1000.0 - 0.005 <= hinten < -0.02 - 0.02, hinten)

    def test_5_vorn_gilt_dasselbe_verfahren(self):
        _, vorn = self._grenzen(self._original(-0.08, 0.06, lambda z: 0.012))
        self.assertAlmostEqual(vorn, 0.07, places=6)
