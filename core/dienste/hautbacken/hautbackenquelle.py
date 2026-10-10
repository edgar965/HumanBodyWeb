# -*- coding: utf-8 -*-
"""Hautbackenquelle — der Körper der fremden Datei als Ziel der Strahlen: BVH auf der GPU, UV und (für die Normalenkarte) Normalen und Tangenten je Ecke.

Eingabe sind die Daten, die `blendexport.py` ohnehin liefert (`punkte`, `dreiecke`, `uv_ecken` der `.npz` des Körpers) und die Punkte in der Ruhelage der Figur
(`koerper_ruhe.npy`, Blender-Achsen) — dieselben, die `blendbacken.py` dem Körper in Blender setzt.
"""

import numpy as np
import warp as wp

from .hautbackenflaeche import Hautbackenflaeche

__all__ = ['Hautbackenquelle']


class Hautbackenquelle:
    def __init__(self, punkte, dreiecke, uv_ecken, geraet='cuda:0'):
        self.flaeche = Hautbackenflaeche(punkte, dreiecke, uv_ecken)
        self.geraet = geraet
        wp.init()
        self.mesh = wp.Mesh(points=wp.array(self.flaeche.punkte.astype(np.float32), dtype=wp.vec3, device=geraet),
                            indices=wp.array(self.flaeche.dreiecke.reshape(-1), dtype=wp.int32, device=geraet))
        self.uv = wp.array(self.flaeche.uv_ecken.reshape(-1, 2), dtype=wp.vec2, device=geraet)
        self._normalen = None

    def normalen(self):
        """`(dreiecke, normalen, tangenten)` auf dem Gerät — nur für die Normalenkarte gebraucht, daher erst auf Anfrage."""
        if self._normalen is None:
            f, g = self.flaeche, self.geraet
            self._normalen = (wp.array(f.dreiecke, dtype=wp.vec3i, device=g), wp.array(f.normalen(), dtype=wp.vec3, device=g),
                              wp.array(f.tangenten().reshape(-1, 4), dtype=wp.vec4, device=g))
        return self._normalen
