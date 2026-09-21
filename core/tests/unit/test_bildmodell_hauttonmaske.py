# -*- coding: utf-8 -*-
"""Hautton-Positivliste im Freisteller (21.09.2026): Proben aus Strichen/Punkten, Palette ohne
Grau, Maske nach Toleranz. Kunstbild: Hautfläche auf grauem Verlauf, kein Netz, keine Datenbank."""
import unittest

import numpy as np

from core.dienste.bildmodellhauttonmaske import Bildmodellhauttonmaske as H


def kunstbild():
    """(200, 160, 3) uint8: grauer Verlauf, Hautrechteck (Zeilen 40–160, Spalten 40–120) mit
    hellerem Streifen, dazu ein dunkelbrauner „Haar"-Block oben."""
    y = np.linspace(60, 140, 200)[:, None, None]
    rgb = np.repeat(np.repeat(y, 160, axis=1), 3, axis=2).astype(np.uint8)
    rgb[40:160, 40:120] = (222, 172, 140)
    rgb[100:120, 40:120] = (240, 200, 170)      # Lichtkante der Haut
    rgb[10:40, 60:100] = (60, 40, 30)           # Haar
    return rgb


class HauttonmaskeTest(unittest.TestCase):
    databases = []

    def test_proben_aus_strich_und_punkt(self):
        regler = {'striche': [{'art': 'drin', 'breite': 0.02, 'punkte': [[0.5, 0.4], [0.5, 0.6]]}],
                  'punkte': [[0.3, 0.3, 1], [0.9, 0.9, 0]]}
        p = H.proben((200, 160), regler)
        self.assertTrue(p[100, 80])                 # Strich
        self.assertTrue(p[60, 48])                  # Punkt Person
        self.assertFalse(p[180, 144])               # Punkt Hintergrund zählt nicht
        self.assertIsNone(H.proben((200, 160), {'striche': [], 'punkte': [[0.9, 0.9, 0]]}))

    def test_maske_haut_ohne_grund_und_haar(self):
        rgb = kunstbild()
        proben = np.zeros((200, 160), dtype=bool)
        proben[80:90, 70:90] = True
        maske = H.aus(rgb, proben, 20)
        self.assertGreater(maske[60:150, 50:110].mean(), 250)       # Haut drin, auch die Lichtkante
        self.assertLess(maske[:, :30].mean(), 5)                    # grauer Grund draußen
        self.assertLess(maske[10:40, 60:100].mean(), 5)             # Haar draußen
        self.assertEqual(maske.shape, (200, 160))

    def test_toleranz_weitet(self):
        rgb = kunstbild()
        proben = np.zeros((200, 160), dtype=bool)
        proben[80:90, 70:90] = True
        eng, weit = H.aus(rgb, proben, 5), H.aus(rgb, proben, 60)
        self.assertLess((eng > 127).mean(), (weit > 127).mean())
        self.assertGreater((weit > 127).mean(), 0.8)               # bei 60 ist fast alles „Haut"

    def test_palette_ohne_grau(self):
        lab = np.zeros((10, 10, 3), dtype=np.float32)
        lab[:5] = (60, 20, 25)
        lab[5:] = (30, 0, 0)                                       # grau
        mitten = H.palette(np.repeat(np.repeat(lab, 20, axis=0), 20, axis=1), np.ones((200, 200), dtype=bool))
        self.assertTrue((np.hypot(mitten[:, 1], mitten[:, 2]) >= H.CHROMA_MIN).all())

    def test_verbunden_nur_flecken_an_der_figur(self):
        maske = np.zeros((50, 50), dtype=np.uint8)
        maske[10:20, 10:20] = 255                                  # berührt die Figur
        maske[30:40, 30:40] = 255                                  # frei schwebend
        figur = np.zeros((50, 50), dtype=bool)
        figur[5:12, 5:12] = True
        v = H.verbunden(maske, figur)
        self.assertEqual(int(v[15, 15]), 255)
        self.assertEqual(int(v[35, 35]), 0)
        self.assertEqual(int(H.verbunden(maske, np.zeros((50, 50), dtype=bool)).max()), 0)

    def test_erweitern_laesst_den_kern_ganz(self):
        """Kern über Haut UND Haar; die Positivliste nimmt im Kern nichts weg und holt den
        hautfarbenen Anhang außerhalb dazu."""
        rgb = kunstbild()
        rgb[100:110, 120:150] = (222, 172, 140)                    # „Arm" rechts neben der Figur
        kern = np.zeros((200, 160), dtype=bool)
        kern[10:160, 40:120] = True                                # Haar (10–40) und Haut (40–160)
        aus = H.erweitern(rgb, kern, {'toleranz': 20, 'striche': [], 'punkte': []})
        self.assertGreater(aus[10:40, 60:100].mean(), 250)          # Haar bleibt (im Kern)
        self.assertGreater(aus[102:108, 125:145].mean(), 250)       # Arm kommt dazu
        self.assertLess(aus[:, :30].mean(), 5)                      # grauer Grund bleibt draußen

    def test_kern_ist_inneres_plus_marken(self):
        maske = np.zeros((100, 100), dtype=np.uint8)
        maske[20:80, 20:80] = 255
        k = H.kern(maske, {'striche': [], 'punkte': [[0.05, 0.05, 1]]})
        self.assertTrue(k[50, 50])                                  # Inneres
        self.assertTrue(k[5, 5])                                    # Punkt Person außerhalb der Maske
        self.assertFalse(k[21, 21])                                 # Rand erodiert

    def test_innen_erodiert(self):
        maske = np.zeros((100, 100), dtype=np.uint8)
        maske[20:80, 20:80] = 255
        i = H.innen(maske)
        self.assertTrue(i[50, 50])
        self.assertFalse(i[21, 21])


if __name__ == '__main__':
    unittest.main()
