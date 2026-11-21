# -*- coding: utf-8 -*-
"""Hautbackenquelle — der Körper der fremden Datei als Ziel der Strahlen: Suchbaum auf der Karte und seine UV je Ecke.

Eingabe sind die Daten, die `blendexport.py` ohnehin liefert (`punkte`, `dreiecke`, `uv_ecken` der `.npz` des Körpers) und die Punkte in der Ruhelage der Figur
(`koerper_ruhe.npy`, Blender-Achsen) — dieselben, die `blendbacken.py` dem Körper in Blender setzt. Normalen, Tangenten und Attribute am Treffer liefert `graph/Hautbackenschattung`.
Der Baum ist GarmentCodes `Dreiecksbaum` (Warps LBVH nachgebaut; bis 21.11.2026 `wp.Mesh`), die Strahlen gehen über `kartenstrahl.cuh` (Warp 1.17 `mesh_query_ray`).
"""

import torch

from Assets.GarmentCode.dreiecksbaum import Dreiecksbaum
from KoerperKI_alle.torchfeld import Torchfeld

from .hautbackenflaeche import Hautbackenflaeche

__all__ = ['Hautbackenquelle']


class Hautbackenquelle:
    def __init__(self, punkte, dreiecke, uv_ecken, geraet='cuda:0'):
        self.flaeche = Hautbackenflaeche(punkte, dreiecke, uv_ecken)
        self.geraet = torch.device(geraet)
        with torch.cuda.device(self.geraet):
            self.baum = Dreiecksbaum(Torchfeld.feld(self.flaeche.punkte, dtype=torch.float32).to(self.geraet),
                                     Torchfeld.feld(self.flaeche.dreiecke).to(self.geraet))
        self.uv = Torchfeld.feld(self.flaeche.uv_ecken, dtype=torch.float32).to(self.geraet).reshape(-1, 2).contiguous()
