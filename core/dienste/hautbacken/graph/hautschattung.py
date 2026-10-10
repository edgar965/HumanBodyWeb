# -*- coding: utf-8 -*-
"""Hautbackenschattung — die Netzdaten des Quellkörpers, die ein Knotengraph am Treffer braucht, auf der GPU: Dreiecke, Punkte (Ruhelage), glatt/flach, Eckennormalen,
UV-Karten, Farbattribute und Tangenten.

Die Daten kommen aus dem Export (`blendexport.py`, `.npz` + Netzeintrag des Inventars: `uv_karten`, `farbattribute`) und aus den Punkten in der Ruhelage der Figur
(`koerper_ruhe.npy`). Eckennormalen und Tangenten liefern die Aufrufer (Blenders Normalenrechnung, MikkTSpace) — hier wird nichts davon neu erfunden.
"""

import numpy as np
import warp as wp

from . import hautkontextkernel as kern

__all__ = ['Hautbackenschattung']


@wp.kernel
def _packen(n: wp.array(dtype=wp.vec3), aus: wp.array(dtype=wp.vec3)):
    i = wp.tid()
    aus[i] = kern.packed_normal(n[i])


class Hautbackenschattung:
    def __init__(self, punkte, dreiecke, npz, info, ecken_normalen, tangenten_fn, geraet='cuda:0'):
        """`punkte` (N, 3) Ruhelage, `dreiecke` (T, 3); `npz`: die Arrays des Netzes (`uv_<i>`, `farbe_<i>`, `glatt`, `material`); `info`: Netzeintrag des Inventars;
        `ecken_normalen` (T, 3, 3): Eckennormalen, wie Blender sie für diese Punkte rechnet; `tangenten_fn(uv_index)` → `(tangenten (T, 3, 3), vorzeichen (T, 3))`."""
        self.geraet, self.info, self.npz = geraet, info, npz
        self.dreiecke = np.ascontiguousarray(dreiecke, dtype=np.int32)
        self.anzahl = len(self.dreiecke)
        self.tri = wp.array(self.dreiecke, dtype=wp.vec3i, device=geraet)
        self.pos = wp.array(np.ascontiguousarray(punkte, dtype=np.float32), dtype=wp.vec3, device=geraet)
        glatt = np.asarray(npz['glatt']) if 'glatt' in npz else np.ones(self.anzahl, dtype=bool)
        if info.get('normalen_domain') == 'CORNER':
            # `Mesh::pack_shaders` (scene/mesh.cpp): Eckennormalen überschreiben das glatt/flach-Flag — die Flachheit steckt schon in den Eckennormalen.
            glatt = np.ones(self.anzahl, dtype=bool)
        self.glatt = wp.array(glatt.astype(np.int32), dtype=wp.int32, device=geraet)
        roh = wp.array(np.ascontiguousarray(ecken_normalen, dtype=np.float32).reshape(-1, 3), dtype=wp.vec3, device=geraet)
        self.ecke_n = wp.zeros_like(roh)
        wp.launch(_packen, dim=len(roh), inputs=[roh, self.ecke_n], device=geraet)
        self.material = np.asarray(npz['material']).astype(np.int64)
        self._tangenten_fn = tangenten_fn
        self._uv, self._farbe, self._tangenten = {}, {}, {}

    # ------------------------------------------------------------------ UV

    def uv_eintrag(self, name):
        """Der Eintrag der UV-Karte `name` (`''` = die Standard-UV, Cycles' `ATTR_STD_UV`: die Karte mit `render`, sonst die aktive) oder None."""
        karten = self.info.get('uv_karten') or []
        if name:
            return next((k for k in karten if k['name'] == name), None)
        return next((k for k in karten if k['render']), None) or next((k for k in karten if k['aktiv']), None) or (karten[0] if karten else None)

    def uv(self, name):
        """`(Feld vec2 (T·3), Eintrag)` der UV-Karte; None, wenn das Netz sie nicht hat."""
        eintrag = self.uv_eintrag(name)
        if eintrag is None:
            return None
        if eintrag['schluessel'] not in self._uv:
            roh = np.ascontiguousarray(self.npz[eintrag['schluessel']], dtype=np.float32).reshape(-1, 2)
            self._uv[eintrag['schluessel']] = wp.array(roh, dtype=wp.vec2, device=self.geraet)
        return self._uv[eintrag['schluessel']], eintrag

    # ------------------------------------------------------------ Farbattribute

    def farbe(self, name):
        """Feld vec4 (T·3), linear, des Farbattributs `name` (`''` = die Standardfarbe); None, wenn das Netz es nicht (oder nicht exportiert) hat."""
        karten = self.info.get('farbattribute') or []
        eintrag = next((k for k in karten if k.get('standard')), None) if not name else next((k for k in karten if k['name'] == name), None)
        if eintrag is None or 'schluessel' not in eintrag:
            return None
        if eintrag['schluessel'] not in self._farbe:
            roh = np.ascontiguousarray(self.npz[eintrag['schluessel']], dtype=np.float32).reshape(-1, 4)
            self._farbe[eintrag['schluessel']] = wp.array(roh, dtype=wp.vec4, device=self.geraet)
        return self._farbe[eintrag['schluessel']]

    # ---------------------------------------------------------------- Tangenten

    def tangenten(self, uv_name):
        """`(Tangenten vec3 (T·3), Vorzeichen float (T·3))` für die UV-Karte `uv_name` (`''` = Standard-UV)."""
        eintrag = self.uv_eintrag(uv_name)
        if eintrag is None:
            return None
        schluessel = eintrag['schluessel']
        if schluessel not in self._tangenten:
            t, s = self._tangenten_fn(int(schluessel.split('_')[1]))
            self._tangenten[schluessel] = (wp.array(np.ascontiguousarray(t, dtype=np.float32).reshape(-1, 3), dtype=wp.vec3, device=self.geraet),
                                           wp.array(np.ascontiguousarray(s, dtype=np.float32).reshape(-1), dtype=wp.float32, device=self.geraet))
        return self._tangenten[schluessel]
