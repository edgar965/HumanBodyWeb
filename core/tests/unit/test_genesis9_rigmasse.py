# -*- coding: utf-8 -*-
"""G9rigmasse (20.09.2026): Gelenkhöhen und Kopfmaße aus dem Rig eines Körperfotos, geeicht an Ursula.

Kunstfoto: Maske von Zeile 100 bis 1099 (1000 px), Rig-Punkte in Bildanteilen; die Eichung wird
je Ansicht abgezogen — die Sabotage (Ansicht ohne Eichung) liefert nichts.
"""

import unittest

import numpy as np
from Genesis9.rigmasse import G9rigmasse


def foto(ansicht='vorne', rigs=None):
    return {'ansicht': ansicht, 'breite': 800, 'hoehe': 1200,
            'textur': {'profil': {'oben': 100, 'unten': 1099}}, 'rigs': rigs or {}}


def yolo(knie_y=0.75, sicht=0.9):
    p = [[0.5, 0.15, 0.9]] + [[0.5, 0.2, 0.9]] * 16
    p[3], p[4] = [0.45, 0.16, sicht], [0.55, 0.16, sicht]            # Ohren: 0,10 Bildbreite = 80 px
    p[5], p[6] = [0.4, 0.3, 0.9], [0.6, 0.3, 0.9]                    # Schulter
    p[11], p[12] = [0.45, 0.5, 0.9], [0.55, 0.5, 0.9]                # Hüfte
    p[13], p[14] = [0.45, knie_y, 0.9], [0.55, knie_y, 0.9]          # Knie
    p[15], p[16] = [0.45, 0.9, 0.9], [0.55, 0.9, 0.9]                # Knöchel
    return {'punkte': p}


class RigmasseTest(unittest.TestCase):
    databases = []

    def test_gelenkhoehen_geeicht_je_ansicht(self):
        h = G9rigmasse(foto('vorne', {'yolo': yolo()})).gelenkhoehen()
        # Knie bei y = 0,75 · 1200 = 900 px: (1099 − 900) / 1000 = 0,199, minus Eichung vorn 0,0237.
        self.assertAlmostEqual(h['knie'], 0.199 - 0.0237, places=4)
        self.assertAlmostEqual(h['huefte'], (1099 - 600) / 1000 - 0.0125, places=4)
        hinten = G9rigmasse(foto('hinten', {'yolo': yolo()})).gelenkhoehen()
        self.assertAlmostEqual(hinten['knie'], 0.199 + 0.0019, places=4)
        self.assertIn('ellbogen', h)                                     # alle sechs sicher gesetzt
        # Sabotage: eine Ansicht ohne Eichung (Seite) liefert nichts.
        self.assertEqual(G9rigmasse(foto('seite', {'yolo': yolo()})).gelenkhoehen(), {})

    def test_gelenke_ziel_setzt_nur_die_hoehe(self):
        gelenke = {'l_shin': np.array([0.1, 0.5, 0.02]), 'r_shin': np.array([-0.1, 0.5, 0.02]),
                   'head': np.array([0.0, 1.6, 0.0])}
        aus = G9rigmasse.gelenke_ziel(gelenke, {'knie': 0.28}, 1.7)
        np.testing.assert_allclose(aus['l_shin'], [0.1, 0.28 * 1.7, 0.02])
        np.testing.assert_allclose(aus['r_shin'], [-0.1, 0.28 * 1.7, 0.02])
        np.testing.assert_allclose(aus['head'], gelenke['head'])
        np.testing.assert_allclose(gelenke['l_shin'][1], 0.5)             # Eingabe unverändert

    def test_kopfmasse_ohren_und_kinn(self):
        pif = {'punkte': [[0.5, 0.2, 0.0]] * 133}
        pif['punkte'][23 + 8] = [0.5, 0.25, 0.9]                             # Kinn bei 300 px
        for i in range(23 + 36, 23 + 48):
            pif['punkte'][i] = [0.5, 0.2, 0.9]                                # Augenlinie bei 240 px
        m = G9rigmasse(foto('vorne', {'yolo': yolo(), 'openpifpaf': pif})).kopfmasse(1.7)
        # Ohren aus YOLO (openpifpaf-Ohren unsicher): 80 px · (1,7 m / 1000 px) · 1,167
        self.assertAlmostEqual(m['kopf_breite'], 80 * 1.7 / 1000 * 1.167, places=5)
        # Kopfhöhe = 2,197 × (Kinn − Augenlinie) = 60 px
        self.assertAlmostEqual(m['kopf_hoehe'], 60 * 1.7 / 1000 * 2.197, places=5)
        self.assertEqual(G9rigmasse(foto('hinten', {'yolo': yolo()})).kopfmasse(1.7), {})
        self.assertNotIn('kopf_breite', G9rigmasse(foto('vorne', {'yolo': yolo(sicht=0.1)})).kopfmasse(1.7))
