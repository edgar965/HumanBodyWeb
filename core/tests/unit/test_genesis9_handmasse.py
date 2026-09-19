# -*- coding: utf-8 -*-
"""`G9handmasse`: Verhältnisse aus 21 Handpunkten, Median über sichere Hände (19.09.2026).

Kunstpunkte, keine Bibliothek. Die Wahrheitsprobe am Genesis-Skelett
(Regler 0,6 → 0,6 zurück, Sabotage) steht im LongRunner.
"""

import unittest

import numpy as np

from Genesis9.handmasse import G9handmasse


def kunsthand(handflaeche=0.10, glied=0.03, breite=0.08):
    """Handgelenk im Ursprung, Mittelfinger auf der y-Achse, Zeige- und Kleinfinger seitlich."""
    p = np.zeros((21, 3))
    p[G9handmasse.MID_MCP] = (0, handflaeche, 0)
    p[G9handmasse.MID_PIP] = (0, handflaeche + glied, 0)
    p[G9handmasse.MID_DIP] = (0, handflaeche + 2 * glied, 0)
    p[G9handmasse.MID_TIP] = (0, handflaeche + 3 * glied, 0)
    p[G9handmasse.INDEX_MCP] = (-breite / 2, handflaeche, 0)
    p[G9handmasse.PINKY_MCP] = (breite / 2, handflaeche, 0)
    return p.tolist()


class DieVerhaeltnisse(unittest.TestCase):
    def test_finger_ist_die_gliedsumme_durch_die_handflaeche(self):
        v = G9handmasse.verhaeltnisse(kunsthand())
        self.assertAlmostEqual(v['finger'], 0.9, places=9)
        self.assertAlmostEqual(v['breite'], 0.8, places=9)

    def test_ein_gebeugter_finger_bleibt_gleich_lang(self):
        p = np.array(kunsthand())
        # Endglied um 90° abgeknickt: Spitze seitlich statt weiter oben.
        p[G9handmasse.MID_TIP] = p[G9handmasse.MID_DIP] + (0.03, 0, 0)
        self.assertAlmostEqual(G9handmasse.verhaeltnisse(p.tolist())['finger'], 0.9, places=9)

    def test_zu_kleine_oder_falsche_haende_geben_nichts(self):
        self.assertIsNone(G9handmasse.verhaeltnisse(kunsthand(handflaeche=0.01)))
        self.assertIsNone(G9handmasse.verhaeltnisse([[0, 0, 0]] * 20))

    def test_median_ueber_sichere_haende(self):
        bilder = [
            {'haende_punkte': [{'guete': 0.95, 'welt': kunsthand(glied=0.03)}]},
            {'haende_punkte': [{'guete': 0.9, 'welt': kunsthand(glied=0.04)},
                               {'guete': 0.5, 'welt': kunsthand(glied=0.10)}]},
            {'haende_punkte': [{'guete': 0.85, 'welt': kunsthand(glied=0.05)}]},
            {},
        ]
        aus = G9handmasse.aus_bildern(bilder)
        self.assertEqual(aus['haende'], 3, 'die unsichere Hand (0,5) zählt nicht')
        self.assertAlmostEqual(aus['finger'], 1.2, places=9)
        self.assertIsNone(G9handmasse.aus_bildern([{}]))
