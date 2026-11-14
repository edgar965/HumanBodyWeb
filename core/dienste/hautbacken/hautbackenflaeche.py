# -*- coding: utf-8 -*-
"""Hautbackenflaeche — ein Dreiecksnetz mit UV je Ecke (Grundlage von Figur und Quellkörper des Backens).

Nur die Daten: Punkte, Dreiecke und UV je Dreiecksecke. Normalen und Tangenten rechnet `Hautbackentangenten` (MikkTSpace und Blenders Punktnormalen, aus dem Blender-Quelltext), nicht
diese Klasse — frühere Näherungen hier (winkelgewichtete Normalen in float64, Tangenten aus Summen je UV-Naht) sind weg, sie waren nicht Blenders Rechnung.
"""

import torch
from KoerperKI_alle.torchfeld import Torchfeld

__all__ = ['Hautbackenflaeche']


class Hautbackenflaeche:
    def __init__(self, punkte, dreiecke, uv_ecken):
        self.punkte = Torchfeld.feld(punkte, dtype=torch.float64)
        self.dreiecke = Torchfeld.feld(dreiecke, dtype=torch.int32)
        self.uv_ecken = Torchfeld.feld(uv_ecken, dtype=torch.float32)
        if self.dreiecke.ndim != 2 or self.dreiecke.shape[1] != 3 or self.uv_ecken.shape != (len(self.dreiecke), 3, 2):
            raise ValueError('Dreiecke %s und UV je Ecke %s passen nicht zusammen' % (self.dreiecke.shape, self.uv_ecken.shape))

    @classmethod
    def aus_obj(cls, pfad):
        """Ein OBJ, wie `Blendimportlage.genesis_objs` es schreibt: `v`, `vt` und Dreiecke mit `Punkt/UV` — die UV stehen je Ecke."""
        v, uv, ecken = [], [], []
        with open(pfad, encoding='utf-8') as datei:
            for zeile in datei:
                if zeile.startswith('v '):
                    v.append([float(a) for a in zeile.split()[1:4]])
                elif zeile.startswith('vt '):
                    uv.append([float(a) for a in zeile.split()[1:3]])
                elif zeile.startswith('f '):
                    ecken.append([tuple(int(i) - 1 for i in teil.split('/')[:2]) for teil in zeile.split()[1:]])
        dreiecke, uv_ecken = [], []
        for f in ecken:
            for k in range(1, len(f) - 1):                      # Fächer: ein Viereck wird zwei Dreiecke
                dreiecke.append([f[0][0], f[k][0], f[k + 1][0]])
                uv_ecken.append([uv[f[0][1]], uv[f[k][1]], uv[f[k + 1][1]]])
        return cls(Torchfeld.feld(v, copy=True), Torchfeld.feld(dreiecke, copy=True), Torchfeld.feld(uv_ecken, copy=True))
