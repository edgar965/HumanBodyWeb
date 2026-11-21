# -*- coding: utf-8 -*-
"""Hautbackenschattung — die Netzdaten des Quellkörpers, die ein Knotengraph am Treffer braucht, auf der GPU: Dreiecke, Punkte (Ruhelage), glatt/flach, Eckennormalen,
UV-Karten, Farbattribute und Tangenten.

Die Daten kommen aus dem Export (`blendexport.py`, `.npz` + Netzeintrag des Inventars: `uv_karten`, `farbattribute`) und aus den Punkten in der Ruhelage der Figur
(`koerper_ruhe.npy`). Eckennormalen und Tangenten liefern die Aufrufer (Blenders Normalenrechnung, MikkTSpace) — hier wird nichts davon neu erfunden.
Felder als torch-Tensoren auf der Karte (bis 21.11.2026 `wp.array`); `packed_normal` im Kern `hb_packen` (`Hautbackenkernbau`).
"""

import torch
from KoerperKI_alle.torchfeld import Torchfeld

from ..hautbackenkernbau import Hautbackenkernbau

__all__ = ['Hautbackenschattung']


def _karte(x, dtype, form, geraet):
    return Torchfeld.feld(x, dtype=dtype).to(geraet).reshape(form).contiguous()


class Hautbackenschattung:
    def __init__(self, punkte, dreiecke, npz, info, ecken_normalen, tangenten_fn, geraet='cuda:0'):
        """`punkte` (N, 3) Ruhelage, `dreiecke` (T, 3); `npz`: die Arrays des Netzes (`uv_<i>`, `farbe_<i>`, `glatt`, `material`); `info`: Netzeintrag des Inventars;
        `ecken_normalen` (T, 3, 3): Eckennormalen, wie Blender sie für diese Punkte rechnet; `tangenten_fn(uv_index)` → `(tangenten (T, 3, 3), vorzeichen (T, 3))`."""
        self.geraet, self.info, self.npz = torch.device(geraet), info, npz
        geraet = self.geraet
        self.dreiecke = Torchfeld.feld(dreiecke, dtype=torch.int32)
        self.anzahl = len(self.dreiecke)
        self.tri = _karte(self.dreiecke, torch.int32, (-1, 3), geraet)
        self.pos = _karte(punkte, torch.float32, (-1, 3), geraet)
        glatt = Torchfeld.feld(npz['glatt']) if 'glatt' in npz else torch.ones(self.anzahl, dtype=torch.bool, device='cuda')
        if info.get('normalen_domain') == 'CORNER':
            # `Mesh::pack_shaders` (scene/mesh.cpp): Eckennormalen überschreiben das glatt/flach-Flag — die Flachheit steckt schon in den Eckennormalen.
            glatt = torch.ones(self.anzahl, dtype=torch.bool, device='cuda')
        self.glatt = _karte(Torchfeld.astype(glatt, torch.int32), torch.int32, (-1,), geraet)
        roh = _karte(ecken_normalen, torch.float32, (-1, 3), geraet)
        self.ecke_n = torch.zeros_like(roh)
        with torch.cuda.device(geraet):
            Hautbackenkernbau.rufen('hb_packen', len(roh), roh, self.ecke_n)
        self.material = Torchfeld.astype(Torchfeld.feld(npz['material']), torch.int64)
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
            self._uv[eintrag['schluessel']] = _karte(self.npz[eintrag['schluessel']], torch.float32, (-1, 2), self.geraet)
        return self._uv[eintrag['schluessel']], eintrag

    # ------------------------------------------------------------ Farbattribute

    def farbe(self, name):
        """Feld vec4 (T·3), linear, des Farbattributs `name` (`''` = die Standardfarbe); None, wenn das Netz es nicht (oder nicht exportiert) hat."""
        karten = self.info.get('farbattribute') or []
        eintrag = next((k for k in karten if k.get('standard')), None) if not name else next((k for k in karten if k['name'] == name), None)
        if eintrag is None or 'schluessel' not in eintrag:
            return None
        if eintrag['schluessel'] not in self._farbe:
            self._farbe[eintrag['schluessel']] = _karte(self.npz[eintrag['schluessel']], torch.float32, (-1, 4), self.geraet)
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
            self._tangenten[schluessel] = (_karte(t, torch.float32, (-1, 3), self.geraet), _karte(s, torch.float32, (-1,), self.geraet))
        return self._tangenten[schluessel]
