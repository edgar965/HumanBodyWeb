# -*- coding: utf-8 -*-
"""Gesichtspunkte der ersten Zeile (`Mesh3daimeshgesicht`, 30.10.2026): Verlust und Lage des Gesichts an einem Kunstkäfig, auf der CPU, ohne Netz, ohne Detektor und ohne Karte.

    1  Ziel = die eigenen Punkte der Figur → Verlust 0, Versatz 0, und der Gradient am Käfig ist 0
    2  Figur 10 mm nach oben → Verlust (0,01 m)², Versatz [0, −10] (y nach unten wie `Kostuemgesichtslage`: „zu hoch“), Betrag 10 mm; der Gradient zeigt nach oben (Abstieg zieht hinunter)
    3  Figur nach vorn (Z) verschoben → Verlust 0: nur die Bildebene zählt, die Tiefe bleibt der Fläche
    4  Prüfung der ersten Zeile (`Mesh3daimeshpruefung.gesicht_zeile`): 1,5 mm grün, 67 mm „zu tief“ rot, ohne Gesicht im Eingang nicht gezählt
    5  Falten je Bereich (`Mesh3daimeshpruefung.falten_zeilen`): über 10 cm rot, darunter und ohne Maß nicht
Sabotage (von Hand): in `messen` das Vorzeichen von y nicht drehen → Fall 2 rot; in `verlust` `[:, :2]` weglassen → Fall 3 rot; in `gesicht_zeile` `>` gegen `<` → Fall 4 rot.
"""
import sys
import unittest

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))
sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


class Mesh3daimeshgesichtTest(unittest.TestCase):
    databases = []

    @staticmethod
    def gesicht(kaefig):
        """Ohne `__init__` (das lädt Netz und Landmarkentabelle): 478 Punkte, jeder auf einem eigenen Kunstdreieck, Ziel = die Lage auf `kaefig`."""
        import torch
        from mesh3dai_meshgesicht import Mesh3daimeshgesicht
        ge = object.__new__(Mesh3daimeshgesicht)
        n = 478
        ge.g, ge.log = torch.device('cpu'), print
        ge.platz = np.ones(n, dtype=bool)
        ge.ecken = torch.arange(3 * n).reshape(n, 3)
        rng = np.random.default_rng(3)
        b = rng.random((n, 3))
        ge.bary = torch.as_tensor(b / b.sum(1, keepdims=True))
        ge.ziel = ge.lage(kaefig)[:, :2].detach().clone()
        ge.wahl = torch.arange(n)
        ge.aktiv = True
        return ge

    @staticmethod
    def kaefig():
        import torch
        rng = np.random.default_rng(7)
        return torch.as_tensor(rng.normal(0.0, 0.05, (3 * 478, 3)) + [0.0, 1.6, 0.1])

    def test_1_eigene_punkte(self):
        k = self.kaefig().requires_grad_(True)
        ge = self.gesicht(k.detach())
        v = ge.verlust(k)
        v.backward()
        self.assertAlmostEqual(float(v), 0.0, places=12)
        self.assertAlmostEqual(float(k.grad.abs().max()), 0.0, places=12)
        m = ge.messen(k.detach())
        self.assertEqual(m['versatz_mm'], [0.0, 0.0])
        self.assertEqual(m['punkte'], 478)

    def test_2_figur_zu_hoch(self):
        import torch
        k0 = self.kaefig()
        ge = self.gesicht(k0)
        k = (k0 + torch.tensor([0.0, 0.01, 0.0], dtype=k0.dtype)).requires_grad_(True)
        v = ge.verlust(k)
        v.backward()
        self.assertAlmostEqual(float(v), 1e-4, places=10)
        m = ge.messen(k.detach())
        self.assertAlmostEqual(m['versatz_mm'][0], 0.0, places=6)
        self.assertAlmostEqual(m['versatz_mm'][1], -10.0, places=6)
        self.assertAlmostEqual(m['betrag_mm'], 10.0, places=6)
        self.assertGreater(float(k.grad[:, 1].sum()), 0.0)

    def test_3_tiefe_zaehlt_nicht(self):
        import torch
        k0 = self.kaefig()
        ge = self.gesicht(k0)
        v = ge.verlust(k0 + torch.tensor([0.0, 0.0, 0.05], dtype=k0.dtype))
        self.assertAlmostEqual(float(v), 0.0, places=12)

    def test_4_pruefung_lage_des_gesichts(self):
        from mesh3dai_meshpruefung import Mesh3daimeshpruefung
        ge, text = Mesh3daimeshpruefung.gesicht_zeile({'eingang_erkannt': True, 'versatz_mm': [0.5, 1.4], 'betrag_mm': 1.5})
        self.assertFalse(ge['rot'])
        self.assertIsNone(text)
        ge, text = Mesh3daimeshpruefung.gesicht_zeile({'eingang_erkannt': True, 'versatz_mm': [2.6, 67.1], 'betrag_mm': 67.2})
        self.assertTrue(ge['rot'])
        self.assertIn('zu tief 67 mm', text)
        ge, text = Mesh3daimeshpruefung.gesicht_zeile({'eingang_erkannt': False})
        self.assertNotIn('rot', ge)
        self.assertIsNone(text)

    def test_5_pruefung_falten(self):
        from mesh3dai_meshpruefung import Mesh3daimeshpruefung
        rot = Mesh3daimeshpruefung.falten_zeilen({'Rumpf vorn': {'cm': 106.0, 'kanten': 92}, 'Arm links': {'cm': 9.9, 'kanten': 8}, 'Bein rechts': {'cm': 0.0, 'kanten': 0}})
        self.assertEqual(rot, ['Falte Rumpf vorn (106 cm in 92 Kanten)'])
        self.assertEqual(Mesh3daimeshpruefung.falten_zeilen(None), [])
