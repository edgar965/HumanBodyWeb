# -*- coding: utf-8 -*-
"""Hautbackengraph — backt die Bilder einer Kachel aus den Knotengraphen der Materialien des Quellkörpers, ohne Blender.

    treiber = Hautbackengraph(schattung, graphen, px)            # graphen: {Materialindex: Hautgraph | None}
    bilder = treiber.backen(figur, kachel_tangenten)              # {'farbe'|'rauheit'|'normalen': (px, px, 3) uint8, 'maske': getroffen, 'ohne_graph': Texel ohne Graph}

Ablauf wie `blendbacken.py` (Cycles „Selected to Active"): ein Strahl je Texel auf den Körper (`Hautbackenkachel.schiessen`), am Treffer wertet der Graph des Materials des
getroffenen Dreiecks Base Color, Roughness und Normal aus (`Hautgraph.auswerten`), die Farbe geht linear → sRGB, die Normale in den Tangentenraum der Figur (`hb_schreiben_normale`).
Die Texel eines Materials werden in Stapeln (`STAPEL`) ausgewertet. Texel, deren Material keinen Graph hat (kein Principled BSDF), bleiben schwarz/flach und stehen in `ohne_graph`.
Felder als torch-Tensoren, Kerne `hb_holen`, `hb_differenzial`, `hb_schreiben_*`, `hb_rueckdrehen` (`Hautbackenkernbau`; bis 21.11.2026 Warp).
"""

import torch
from KoerperKI_alle.torchfeld import Torchfeld

from ..hautbackenkachel import Hautbackenkachel
from ..hautbackenkernbau import Hautbackenkernbau
from .hautalpha import Hautalpha
from .hautglanz import Hautglanz
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
        """`quelle`: `Hautbackenquelle` (BVH); `figur`: `Hautbackenflaeche` der Kachel; `figur_tangenten`: `(M, 3, 4)` float32 — Tangenten (xyz) und Vorzeichen (w) je Ecke
        (`Hautschattungbau.figur_tangenten`). Gibt `{'farbe'|'rauheit'|'normalen': (px, px, 3) uint8, 'maske', 'material', 'treffer', 'ohne_graph', 'glanz_korrektur' (nicht gerechnet: {Material: {'texel', 'grund'}}), 'glanz_gerechnet' ({Material: Texel})}`."""
        g, px = torch.device(self.geraet), self.px
        rufen = Hautbackenkernbau.lauf
        kachel = Hautbackenkachel(figur, px, g)
        treffer = kachel.schiessen(quelle, self.AUSZUG_M, self.STRAHL_M)
        face_k = treffer.face.reshape(-1)
        treffer_idx = torch.nonzero(face_k >= 0, as_tuple=True)[0].to(torch.int32)
        material = self.s.material[face_k[treffer_idx].long()]
        n = px * px
        bilder = {}
        if 'farbe' in kanaele:
            bilder['farbe'] = torch.zeros(n * 3, dtype=torch.uint8, device=g)
        if 'rauheit' in kanaele:
            bilder['rauheit'] = torch.zeros(n * 3, dtype=torch.uint8, device=g)
        if 'normalen' in kanaele:
            bilder['normalen'] = torch.tensor([128, 128, 255], dtype=torch.uint8, device=g).repeat(n).contiguous()
        ids = kachel.ids.reshape(-1)
        bary = kachel.bary.reshape(-1, 2)
        f_tri = kachel._tri
        f_nor = kachel._nor
        f_pos = kachel._pos
        f_uv = kachel._uv
        f_tang = Torchfeld.feld(figur_tangenten, dtype=torch.float32).to(g).reshape(-1, 4).contiguous()
        face_f, hu_f, hv_f = face_k, treffer.hu.reshape(-1), treffer.hv.reshape(-1)
        ohne_graph = torch.zeros(0, dtype=torch.int32, device='cuda')
        glanz, alpha = Hautglanz(g), Hautalpha(g)
        korrektur = {'gerechnet': {}, 'ungerechnet': {}}
        for m in Torchfeld.liste(Torchfeld.unique(material)):
            idx_m = treffer_idx[material == m]
            graph = self.graphen.get(int(m))
            if graph is None:
                ohne_graph = Torchfeld.cat([ohne_graph, idx_m])
                continue
            for von in range(0, len(idx_m), self.STAPEL):
                idx = idx_m[von:von + self.STAPEL].contiguous()
                k = len(idx)
                face = torch.zeros(k, dtype=torch.int32, device=g)
                hu, hv = torch.zeros(k, dtype=torch.float32, device=g), torch.zeros(k, dtype=torch.float32, device=g)
                rufen('hb_holen', k, idx, face_f, hu_f, hv_f, face, hu, hv)
                dp = torch.zeros(k, dtype=torch.float32, device=g)
                rufen('hb_differenzial', k, idx, face, ids, bary, f_pos, f_nor, f_tri, f_uv, px, self.s.pos, self.s.tri, dp)
                ctx = Hautkontext(self.s, face, hu, hv, dp, g)
                werte = graph.auswerten(ctx, tuple({'farbe': 'farbe', 'rauheit': 'rauheit', 'normalen': 'normal'}[c] for c in kanaele))
                if 'farbe' in werte:
                    rufen('hb_schreiben_farbe', k, idx, werte['farbe'].daten.contiguous(), bilder['farbe'])
                if 'rauheit' in werte:
                    rufen('hb_schreiben_rauheit', k, idx, werte['rauheit'].daten.contiguous(), bilder['rauheit'])
                if 'normal' in werte:
                    welt = werte['normal'].daten if werte['normal'] is not None else self._glatte_normale(ctx)
                    if werte['normal'] is not None:
                        welt = glanz.anwenden(graph, ctx, welt, korrektur)
                        welt = alpha.anwenden(graph, ctx, welt)
                    rufen('hb_schreiben_normale', k, idx, welt.contiguous(), ids, bary, f_tri, f_nor, f_tang, bilder['normalen'])
        aus = {name: feld.reshape(px, px, 3).cpu().numpy() for name, feld in bilder.items()}
        getroffen = face_k >= 0
        aus['maske'] = getroffen.reshape(px, px).cpu().numpy()
        aus['material'] = torch.where(getroffen, self.s.material[face_k.long().clamp_min(0)], -1).reshape(px, px)
        aus['treffer'] = treffer
        aus['ohne_graph'] = int(len(ohne_graph))
        aus['glanz_korrektur'] = korrektur['ungerechnet']
        aus['glanz_gerechnet'] = korrektur['gerechnet']
        return aus

    @staticmethod
    def _glatte_normale(ctx):
        """Ohne verbundenen Normal-Eingang schreibt Cycles die geglättete Normale der Körperfläche selbst (`integrator_init_from_bake`, schneller Weg ohne `SD_HAS_BUMP`),
        unverändert durch die Rückseitenprüfung."""
        _ng, n, _u, _v, rueck = ctx.geometrie()
        roh = torch.zeros((ctx.n, 3), dtype=torch.float32, device=ctx.geraet)
        Hautbackenkernbau.lauf('hb_rueckdrehen', ctx.n, n, rueck, roh)
        return roh
