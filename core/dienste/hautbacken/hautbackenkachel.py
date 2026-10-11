# -*- coding: utf-8 -*-
"""Hautbackenkachel — eine Kachel der Figur als Raster: welches Dreieck und welcher Schwerpunkt liegt am Abtastpunkt jedes Texels (Texelmitte plus Blenders Versatz), und was die Strahlen davon treffen."""

import numpy as np
import warp as wp

from . import hautbackenkernel as kern
from .hautbackentangenten import Hautbackentangenten
from .hautbackentreffer import Hautbackentreffer

__all__ = ['Hautbackenkachel']


class Hautbackenkachel:
    #: Versatz der Abtastpunkte gegen die Texelmitte, in Texeln (Spalte, Zeile von OBEN): `RE_bake_pixels_populate` (`bake.cc`, Blender v5.2.2) legt die Ecken um `0,5 + 0,001` in u und
    #: `0,5 + 0,002` in v nach unten-links (`vec[a][0] = ... - (0.5f + 0.001f)`, "pixel aligned UVs ... where a pixel gets in between 2 faces", Fehler #18685) und tastet `zspan_scanconvert` an den
    #: ganzen Zahlen ab, also bei Texelmitte + (0,001; 0,002) in Blenders Bild (Zeile 0 unten). Unser Bild zählt die Zeilen von oben: v wird zu 1 - v, der Versatz in v kehrt sich um.
    VERSATZ = (0.001, -0.002)

    def __init__(self, figur, px, geraet='cuda:0'):
        """`figur`: `Hautbackenflaeche` der Kachel (Punkte in Blender-Achsen, UV je Ecke); `px`: Seitenlänge des Bildes. Die Strahlrichtung kommt aus Blenders Punktnormalen der Figur
        (`calc_point_from_barycentric_extrusion` in `bake.cc` nimmt `vert_normals`; `Hautbackentangenten.punktnormalen`)."""
        self.figur, self.px, self.geraet = figur, px, geraet
        self.ids = wp.full((px, px), -1, dtype=wp.int32, device=geraet)
        self.bary = wp.zeros((px, px), dtype=wp.vec2, device=geraet)
        self._pos = wp.array(figur.punkte.astype('float32'), dtype=wp.vec3, device=geraet)
        self._nor = wp.array(Hautbackentangenten.punktnormalen(figur.punkte, figur.dreiecke), dtype=wp.vec3, device=geraet)
        self._tri = wp.array(figur.dreiecke, dtype=wp.vec3i, device=geraet)
        uv = figur.uv_ecken.reshape(-1, 2)
        self._uv = wp.array(uv, dtype=wp.vec2, device=geraet)
        self._tri_uv = wp.array(np.arange(len(uv), dtype=np.int32).reshape(-1, 3), dtype=wp.vec3i, device=geraet)       # die UV stehen je Ecke hintereinander
        self.rastern(*self.VERSATZ)

    def rastern(self, ox=0.0, oy=0.0):
        """Die Dreiecke in die Kachel legen; `ox`, `oy`: Versatz der Abtastpunkte gegen die Texelmitte in Texeln (Blender: `VERSATZ`)."""
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
