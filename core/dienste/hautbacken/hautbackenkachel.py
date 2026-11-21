# -*- coding: utf-8 -*-
"""Hautbackenkachel — eine Kachel der Figur als Raster: welches Dreieck und welcher Schwerpunkt liegt am Abtastpunkt jedes Texels (Texelmitte plus Blenders Versatz), und was die
Strahlen davon treffen. Kerne `hb_rastern`, `hb_schiessen` (`Hautbackenkernbau`; bis 21.11.2026 Warp in `hautbackenkernel.py`)."""

import torch

from KoerperKI_alle.torchfeld import Torchfeld

from .hautbackenkernbau import Hautbackenkernbau
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
        self.figur, self.px, self.geraet = figur, px, torch.device(geraet)
        g = self.geraet
        self.ids = torch.full((px, px), -1, dtype=torch.int32, device=g)
        self.bary = torch.zeros((px, px, 2), dtype=torch.float32, device=g)
        self._pos = Torchfeld.feld(figur.punkte, dtype=torch.float32).to(g).reshape(-1, 3).contiguous()
        self._nor = Torchfeld.feld(Hautbackentangenten.punktnormalen(figur.punkte, figur.dreiecke), dtype=torch.float32).to(g).reshape(-1, 3).contiguous()
        self._tri = Torchfeld.feld(figur.dreiecke).to(device=g, dtype=torch.int32).reshape(-1, 3).contiguous()
        uv = Torchfeld.feld(figur.uv_ecken, dtype=torch.float32).to(g).reshape(-1, 2).contiguous()
        self._uv = uv
        self._tri_uv = torch.arange(len(uv), dtype=torch.int32, device=g).reshape(-1, 3).contiguous()      # die UV stehen je Ecke hintereinander
        self.rastern(*self.VERSATZ)

    def rastern(self, ox=0.0, oy=0.0):
        """Die Dreiecke in die Kachel legen; `ox`, `oy`: Versatz der Abtastpunkte gegen die Texelmitte in Texeln (Blender: `VERSATZ`)."""
        self.ids.fill_(-1)
        with torch.cuda.device(self.geraet):
            Hautbackenkernbau.rufen('hb_rastern', len(self._tri_uv), self._uv, self._tri_uv, self.px, float(ox), float(oy), self.ids, self.bary)

    def belegt(self):
        """`(px, px)` bool im Speicher (wie vorher `ids.numpy() >= 0`): Texel, die ein Dreieck der Figur deckt."""
        return (self.ids >= 0).cpu().numpy()

    def schiessen(self, quelle, auszug, laenge):
        """Je belegtem Texel ein Strahl auf den Körper (`Hautbackenquelle`): `auszug` Meter nach außen, dann `laenge` Meter entlang der Normale nach innen."""
        g, px = self.geraet, self.px
        face = torch.zeros((px, px), dtype=torch.int32, device=g)
        hu = torch.zeros((px, px), dtype=torch.float32, device=g)
        hv = torch.zeros((px, px), dtype=torch.float32, device=g)
        with torch.cuda.device(g):
            Hautbackenkernbau.rufen('hb_schiessen', px * px, *quelle.baum.zeiger(), self._pos, self._nor, self._tri, self.ids, self.bary, float(auszug), float(laenge),
                                    face, hu, hv)
        return Hautbackentreffer(px, face, hu, hv)
