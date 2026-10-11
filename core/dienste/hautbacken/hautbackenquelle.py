# -*- coding: utf-8 -*-
"""Hautbackenquelle — der Körper der fremden Datei als Ziel der Strahlen: BVH auf der GPU (Warp) und seine UV je Ecke.

Eingabe sind die Daten, die `blendexport.py` ohnehin liefert (`punkte`, `dreiecke`, `uv_ecken` der `.npz` des Körpers) und die Punkte in der Ruhelage der Figur
(`koerper_ruhe.npy`, Blender-Achsen) — dieselben, die `blendbacken.py` dem Körper in Blender setzt. Normalen, Tangenten und Attribute am Treffer liefert `graph/Hautbackenschattung`.
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
