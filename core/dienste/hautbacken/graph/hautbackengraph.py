# -*- coding: utf-8 -*-
"""Hautbackengraph — backt die Bilder einer Kachel aus den Knotengraphen der Materialien des Quellkörpers, ohne Blender.

    treiber = Hautbackengraph(schattung, graphen, px)            # graphen: {Materialindex: Hautgraph | None}
    bilder = treiber.backen(figur, kachel_tangenten)              # {'farbe'|'rauheit'|'normalen': (px, px, 3) uint8, 'maske': getroffen, 'ohne_graph': Texel ohne Graph}

Ablauf wie `blendbacken.py` (Cycles „Selected to Active"): ein Strahl je Texel auf den Körper (`Hautbackenkachel.schiessen`), am Treffer wertet der Graph des Materials des
getroffenen Dreiecks Base Color, Roughness und Normal aus (`Hautgraph.auswerten`), die Farbe geht linear → sRGB, die Normale in den Tangentenraum der Figur (`hautausgabekernel`).
Die Texel eines Materials werden in Stapeln (`STAPEL`) ausgewertet. Texel, deren Material keinen Graph hat (kein Principled BSDF), bleiben schwarz/flach und stehen in `ohne_graph`.
"""

import numpy as np
import warp as wp

from ..hautbackenkachel import Hautbackenkachel
from . import hautausgabekernel as aus_kern
from . import hautkontextkernel as kern
from .hautkontext import Hautkontext

__all__ = ['Hautbackengraph']


class Hautbackengraph:
    #: Texel je Stapel (Speicher: einige hundert Byte je Texel und Knoten).
    STAPEL = 1 << 21
    AUSZUG_M = 0.015
    STRAHL_M = 0.035

    def __init__(self, schattung, graphen, px, geraet='cuda:0'):
        self.s, self.graphen, self.px, self.geraet = schattung, graphen, int(px), geraet

    def backen(self, quelle, figur, figur_tangenten, kanaele=('farbe', 'rauheit', 'normalen')):
        """`quelle`: `Hautbackenquelle` (BVH); `figur`: `Hautbackenflaeche` der Kachel; `figur_tangenten`: `(M, 3, 4)` float32 — Tangenten (xyz) und Vorzeichen (w) je Ecke."""
        g, px = self.geraet, self.px
        kachel = Hautbackenkachel(figur, px, g)
        treffer = kachel.schiessen(quelle, self.AUSZUG_M, self.STRAHL_M)
        face_np = treffer.face.numpy().reshape(-1)
        treffer_idx = np.nonzero(face_np >= 0)[0].astype(np.int32)
        material = self.s.material[face_np[treffer_idx]]
        n = px * px
        bilder = {}
        if 'farbe' in kanaele:
            bilder['farbe'] = wp.zeros(n * 3, dtype=wp.uint8, device=g)
        if 'rauheit' in kanaele:
            bilder['rauheit'] = wp.zeros(n * 3, dtype=wp.uint8, device=g)
        if 'normalen' in kanaele:
            bilder['normalen'] = wp.array(np.tile(np.array([128, 128, 255], dtype=np.uint8), n), dtype=wp.uint8, device=g)
        ids = kachel.ids.reshape(-1)
        bary = kachel.bary.reshape(-1)
        f_tri = wp.array(figur.dreiecke, dtype=wp.vec3i, device=g)
        f_nor = wp.array(figur.normalen(), dtype=wp.vec3, device=g)
        f_pos = wp.array(figur.punkte.astype(np.float32), dtype=wp.vec3, device=g)
        f_uv = wp.array(figur.uv_ecken.reshape(-1, 2), dtype=wp.vec2, device=g)
        f_tang = wp.array(np.ascontiguousarray(figur_tangenten, dtype=np.float32).reshape(-1, 4), dtype=wp.vec4, device=g)
        face_f, hu_f, hv_f = treffer.face.reshape(-1), treffer.hu.reshape(-1), treffer.hv.reshape(-1)
        ohne_graph = np.zeros(0, dtype=np.int32)
        for m in np.unique(material):
            idx_m = treffer_idx[material == m]
            graph = self.graphen.get(int(m))
            if graph is None:
                ohne_graph = np.concatenate([ohne_graph, idx_m])
                continue
            for von in range(0, len(idx_m), self.STAPEL):
                idx = wp.array(idx_m[von:von + self.STAPEL], dtype=wp.int32, device=g)
                k = len(idx)
                face, hu, hv = (wp.zeros(k, dtype=t, device=g) for t in (wp.int32, wp.float32, wp.float32))
                wp.launch(aus_kern.holen, dim=k, inputs=[idx, face_f, hu_f, hv_f, face, hu, hv], device=g)
                dp = wp.zeros(k, dtype=wp.float32, device=g)
                wp.launch(kern.differenzial, dim=k, inputs=[idx, face, ids, bary, f_pos, f_nor, f_tri, f_uv, px, self.s.pos, self.s.tri, dp], device=g)
                ctx = Hautkontext(self.s, face, hu, hv, dp, g)
                werte = graph.auswerten(ctx, tuple({'farbe': 'farbe', 'rauheit': 'rauheit', 'normalen': 'normal'}[c] for c in kanaele))
                if 'farbe' in werte:
                    wp.launch(aus_kern.schreiben_farbe, dim=k, inputs=[idx, werte['farbe'].daten, bilder['farbe']], device=g)
                if 'rauheit' in werte:
                    wp.launch(aus_kern.schreiben_rauheit, dim=k, inputs=[idx, werte['rauheit'].daten, bilder['rauheit']], device=g)
                if 'normal' in werte:
                    welt = werte['normal'].daten if werte['normal'] is not None else self._glatte_normale(ctx)
                    wp.launch(aus_kern.schreiben_normale, dim=k, inputs=[idx, welt, ids, bary, f_tri, f_nor, f_tang, bilder['normalen']], device=g)
        aus = {name: feld.numpy().reshape(px, px, 3) for name, feld in bilder.items()}
        aus['maske'] = (face_np >= 0).reshape(px, px)
        aus['treffer'] = treffer
        aus['ohne_graph'] = int(len(ohne_graph))
        return aus

    @staticmethod
    def _glatte_normale(ctx):
        """Ohne verbundenen Normal-Eingang schreibt Cycles die geglättete Normale der Körperfläche selbst (`integrator_init_from_bake`, schneller Weg ohne `SD_HAS_BUMP`),
        unverändert durch die Rückseitenprüfung."""
        _ng, n, _u, _v, rueck = ctx.geometrie()
        roh = wp.zeros(ctx.n, dtype=wp.vec3, device=ctx.geraet)
        wp.launch(_rueckdrehen, dim=ctx.n, inputs=[n, rueck, roh], device=ctx.geraet)
        return roh


@wp.kernel
def _rueckdrehen(n: wp.array(dtype=wp.vec3), rueck: wp.array(dtype=wp.int32), aus: wp.array(dtype=wp.vec3)):
    i = wp.tid()
    if rueck[i] != 0:
        aus[i] = -n[i]
    else:
        aus[i] = n[i]
