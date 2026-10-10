# -*- coding: utf-8 -*-
"""Hautbackenkachel — eine Kachel der Figur als Raster: welches Dreieck und welcher Schwerpunkt liegt in der Mitte jedes Texels, und was die Strahlen davon treffen."""

import numpy as np
import warp as wp

from . import hautbackenkernel as kern
from .hautbackentreffer import Hautbackentreffer

__all__ = ['Hautbackenkachel']


class Hautbackenkachel:
    def __init__(self, figur, px, geraet='cuda:0'):
        """`figur`: `Hautbackenflaeche` der Kachel (Punkte in Blender-Achsen, UV je Ecke); `px`: Seitenlänge des Bildes."""
        self.figur, self.px, self.geraet = figur, px, geraet
        self.ids = wp.full((px, px), -1, dtype=wp.int32, device=geraet)
        self.bary = wp.zeros((px, px), dtype=wp.vec2, device=geraet)
        self._pos = wp.array(figur.punkte.astype('float32'), dtype=wp.vec3, device=geraet)
        self._nor = wp.array(figur.normalen(), dtype=wp.vec3, device=geraet)
        self._tri = wp.array(figur.dreiecke, dtype=wp.vec3i, device=geraet)
        uv = figur.uv_ecken.reshape(-1, 2)
        self._uv = wp.array(uv, dtype=wp.vec2, device=geraet)
        self._tri_uv = wp.array(np.arange(len(uv), dtype=np.int32).reshape(-1, 3), dtype=wp.vec3i, device=geraet)       # die UV stehen je Ecke hintereinander
        self.rastern()

    def rastern(self, ox=0.0, oy=0.0):
        """Die Dreiecke in die Kachel legen; `ox`, `oy`: Versatz der Abtastpunkte in Texeln (0 = Texelmitte, wie Blender)."""
        self.ids.fill_(-1)
        wp.launch(kern.rastern, dim=len(self._tri_uv), inputs=[self._uv, self._tri_uv, self.px, float(ox), float(oy), self.ids, self.bary], device=self.geraet)

    def belegt(self):
        """`(px, px)` bool: Texel, die ein Dreieck der Figur deckt."""
        return self.ids.numpy() >= 0

    def schiessen(self, quelle, auszug, laenge):
        """Je belegtem Texel ein Strahl auf den Körper (`Hautbackenquelle`): `auszug` Meter nach außen, dann `laenge` Meter entlang der Normale nach innen."""
        face = wp.zeros((self.px, self.px), dtype=wp.int32, device=self.geraet)
        hu = wp.zeros((self.px, self.px), dtype=wp.float32, device=self.geraet)
        hv = wp.zeros((self.px, self.px), dtype=wp.float32, device=self.geraet)
        wp.launch(kern.schiessen, dim=(self.px, self.px),
                  inputs=[quelle.mesh.id, self._pos, self._nor, self._tri, self.ids, self.bary, float(auszug), float(laenge), face, hu, hv], device=self.geraet)
        return Hautbackentreffer(self.px, face, hu, hv)
