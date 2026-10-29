# -*- coding: utf-8 -*-
"""Kostüm-Prüfung „Höhe am Halsansatz wie der Eingang“ (`Kostuemhalsansatz.messen`) an Kunstmasken, 1 mm je Bildpunkt, auf der CPU.

Kunstfigur 200 × 200: Schultern ab Zeile 100 (Spalten 20–180), Hals und Kopf Spalten 90–110 ab Zeile 40; ViTPose Schultern (40|160, 120), Ohren in Zeile 50.
    1  Eingang gegen sich selbst → Strecke 0 auf beiden Seiten; Hals und Kopf (Oberkante über den Ohren) zählen nicht: 50 Spalten je Seite
    2  Schulter der Person links (Punkt 5, rechts im Bild) 10 mm tiefer → Strecke ≥ 15 mm, größte +10 mm; die andere Seite 0
    3  ein schmaler Ausreißer (5 Spalten 20 mm tiefer) → größte +20 mm, Strecke 5 mm (unter `STRECKE_MM`)
    4  Schultern 40 mm auseinander (Figur seitlich) → nicht messbar
Gegenprobe am echten Lauf: `ProjektTemp/_wegwerf/regler_ki/halsansatz_probe.py` (edgar links rot, Eingang gegen sich selbst 0).
Sabotage (von Hand): `gilt` ohne die Ohren (`(oe >= 0) & (orr >= 0)`) → Fall 1 zählt Hals und Kopf mit (61 Spalten, rot); `tiefer` mit `oe - orr` → Fall 2 rot (−10 mm).
"""
import sys
import unittest

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))
sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


def kunstfigur(tiefer=0, von=111, bis=181):
    import torch
    m = torch.zeros((200, 200), dtype=torch.bool)
    m[100:, 20:181] = True
    m[40:, 90:111] = True
    m[100:100 + tiefer, von:bis] = False
    return m


def punkte(halb=60):
    xy, w = np.zeros((133, 2)), np.zeros(133)
    xy[5], xy[6], xy[3], xy[4] = (100 + halb, 120), (100 - halb, 120), (115, 50), (85, 50)
    w[[3, 4, 5, 6]] = 1.0
    return xy, w


@unittest.skipUnless(__import__('importlib').util.find_spec('torch'), 'torch fehlt')
class KostuemhalsansatzTest(unittest.TestCase):
    databases = set()

    def messen(self, ergebnis, halb=60):
        from mesh3dai_kostuem_halsansatz import Kostuemhalsansatz
        return Kostuemhalsansatz.messen(kunstfigur(), ergebnis, *punkte(halb), 1.0)

    def test_gleich(self):
        m = self.messen(kunstfigur())
        for seite in ('links', 'rechts'):
            self.assertEqual(m[seite]['strecke_mm'], 0.0)
            self.assertEqual(m[seite]['spalten'], 50)

    def test_schulter_tiefer(self):
        from mesh3dai_kostuem_halsansatz import Kostuemhalsansatz
        m = self.messen(kunstfigur(tiefer=10))
        self.assertGreaterEqual(m['links']['strecke_mm'], Kostuemhalsansatz.STRECKE_MM)
        self.assertEqual(m['links']['groesste_mm'], 10.0)
        self.assertEqual(m['rechts']['strecke_mm'], 0.0)

    def test_schmaler_ausreisser(self):
        from mesh3dai_kostuem_halsansatz import Kostuemhalsansatz
        m = self.messen(kunstfigur(tiefer=20, von=130, bis=135))
        self.assertEqual(m['links']['groesste_mm'], 20.0)
        self.assertLess(m['links']['strecke_mm'], Kostuemhalsansatz.STRECKE_MM)

    def test_seitlich(self):
        self.assertIn('fehlt', self.messen(kunstfigur(), halb=20))


if __name__ == '__main__':
    unittest.main()
