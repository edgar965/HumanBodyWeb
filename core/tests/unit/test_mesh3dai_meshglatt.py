# -*- coding: utf-8 -*-
"""Glätten der Knicke in der ersten Zeile (`Mesh3daimeshglatt`, 30.10.2026) an einer Kunstfläche, auf der CPU, ohne Figur und ohne Karte.

Fläche: ebenes Gitter 21 × 21 Punkte im Abstand von 6 mm (wie das Ziel, `Mesh3daimeshziel.GITTER_M`), alle Punkte „rumpf“, Blick +Z; das Ziel ist dieselbe Ebene.
    1  eben → keine Falte; `rechnen` bewegt nichts
    2  ein Punkt 4 mm vor der Ebene (Knick ringsum ~34°, Ziel und Figur ohne Versatz 0°) → Falte „Rumpf vorn“; nach `rechnen` keine Falte mehr, der Punkt
       ist zur Ebene zurückgegangen, und ein nicht freier Punkt hat sich nicht bewegt
Sabotage (von Hand): in `rechnen` die Knickstrafe streichen → Fall 2 rot; `frei` nicht anwenden (m = 1) → Fall 2 rot (der feste Punkt wandert).
"""
import sys
import unittest

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))
sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


class Mesh3daimeshglattTest(unittest.TestCase):
    databases = []
    N, SCHRITT = 21, 0.006

    @classmethod
    def flaeche(cls):
        """→ (Punkte (N², 3) float32, Dreiecke (F, 3)), Umlauf gegen den Uhrzeigersinn von +Z gesehen."""
        import torch
        x, y = np.meshgrid(np.arange(cls.N) * cls.SCHRITT, np.arange(cls.N) * cls.SCHRITT)
        p = np.stack([x.ravel() - 0.06, y.ravel() + 1.0, np.zeros(cls.N * cls.N)], 1)
        f = []
        for i in range(cls.N - 1):
            for j in range(cls.N - 1):
                a = i * cls.N + j
                f += [[a, a + 1, a + cls.N + 1], [a, a + cls.N + 1, a + cls.N]]
        return torch.as_tensor(p, dtype=torch.float32), np.asarray(f, dtype=np.int64)

    @classmethod
    def glatt(cls, frei=None):
        import torch
        from Genesis9.koerperteile import G9koerperteile
        from mesh3dai_meshglatt import Mesh3daimeshglatt
        p, f = cls.flaeche()
        ziel = type('Ziel', (), {})()
        ziel.g, ziel.p, ziel.n = torch.device('cpu'), p.clone(), torch.tensor([[0.0, 0.0, 1.0]]).expand(len(p), 3).contiguous()
        teil = np.full(len(p), G9koerperteile.NUMMER['rumpf'])
        frei = torch.ones(len(p), dtype=torch.bool) if frei is None else frei
        return Mesh3daimeshglatt(ziel, f, teil, frei, p), p

    def test_1_eben(self):
        gl, p = self.glatt()
        self.assertTrue(all(v['cm'] == 0 for v in gl.messen(p).values()))
        neu, bericht = gl.rechnen(p.clone(), melder=lambda _t: None)
        self.assertLess(float((neu - p).abs().max()), 1e-6)
        self.assertEqual(bericht['weg_max_mm'], 0.0)

    def test_2_beule(self):
        import torch
        mitte = (self.N // 2) * self.N + self.N // 2
        fest = mitte + 3
        frei = torch.ones(self.N * self.N, dtype=torch.bool)
        frei[fest] = False
        gl, p = self.glatt(frei)
        beule = p.clone()
        beule[mitte, 2] = 0.004
        vorher = gl.messen(beule)
        self.assertGreater(vorher['Rumpf vorn']['cm'], 0.0)
        neu, _b = gl.rechnen(beule, melder=lambda _t: None)
        nachher = gl.messen(neu)
        self.assertTrue(all(v['cm'] == 0 for v in nachher.values()), nachher)
        self.assertLess(float(neu[mitte, 2]), 0.002)
        self.assertLess(float((neu[fest] - beule[fest]).abs().max()), 1e-9)
