# -*- coding: utf-8 -*-
"""Hautknotentabelle — Knoten, die Cycles über Tabellen rechnet: „ColorRamp" (Farbverlauf), „RGB Curves", „Vector Curves", „Float Curve". Übernommen aus
`intern/cycles/kernel/svm/ramp.h` (`float_ramp_lookup`, `rgb_ramp_lookup`, `svm_node_rgb_ramp`, `svm_node_curves`, `svm_node_curve`; Blender-Quelltext vom 10.10.2026).
Die Tabellen (257 Einträge) wertet BLENDER im Export aus (`blendmaterialknoten.py`: Farbrampe `evaluate`, Kurven `CurveMapping.evaluate` an denselben Stellen wie
`colorramp_to_array` / `curvemapping_*_to_array`) — der lokale Backer interpoliert nur darin, wie der Kernel es tut. Kerne `hb_rampe`, `hb_kurven`, `hb_kurve`
(bis 21.11.2026 Warp hier).
"""

import torch
from KoerperKI_alle.torchfeld import Torchfeld

from ...hautbackenkernbau import Hautbackenkernbau
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotentabelle']


class Hautknotentabelle(Hautknoten):
    TYPEN = ('VALTORGB', 'CURVE_RGB', 'CURVE_VEC', 'CURVE_FLOAT')

    def pruefen(self, genutzt):
        return [] if self.eig.get('tabelle') else ['%s-Knoten ohne Tabelle im Export' % self.typ]

    def _tabelle(self, graph):
        if not hasattr(self, '_dev'):
            roh = Torchfeld.feld(self.eig['tabelle'], dtype=torch.float32)
            if self.typ == 'CURVE_FLOAT':
                self._dev = roh.reshape(-1).to(graph.geraet).contiguous()
            else:
                vier = torch.zeros((len(roh), 4), dtype=torch.float32, device=graph.geraet)
                vier[:, :roh.shape[1]] = roh
                self._dev = vier
        return self._dev

    def auswerten(self, graph, ctx, modus):
        g = graph.geraet
        rufen = Hautbackenkernbau.lauf
        tab = self._tabelle(graph)
        groesse = len(self.eig['tabelle'])
        if self.typ == 'VALTORGB':
            fac = self.ein(graph, ctx, modus, 'Fac', 'f')
            farbe, alpha = Hautwert.leer('c', ctx.n, g), Hautwert.leer('f', ctx.n, g)
            rufen('hb_rampe', ctx.n, fac.daten, tab, int(bool(self.eig['interpolieren'])), groesse, farbe.daten, alpha.daten)
            return {'Color': farbe, 'Alpha': alpha}
        extra = int(bool(self.eig['extrapolieren']))
        if self.typ == 'CURVE_FLOAT':
            fac, wert = self.ein(graph, ctx, modus, 'Factor', 'f'), self.ein(graph, ctx, modus, 'Value', 'f')
            aus = Hautwert.leer('f', ctx.n, g)
            rufen('hb_kurve', ctx.n, fac.daten, wert.daten, tab, float(self.eig['min_x']), float(self.eig['max_x']), extra, groesse, aus.daten)
            return {'Value': aus}
        name_f, name_w, art = ('Fac', 'Color', 'c') if self.typ == 'CURVE_RGB' else ('Fac', 'Vector', 'v')
        fac, wert = self.ein(graph, ctx, modus, name_f, 'f'), self.ein(graph, ctx, modus, name_w, art)
        aus = Hautwert.leer(art, ctx.n, g)
        rufen('hb_kurven', ctx.n, fac.daten, wert.daten, tab, float(self.eig['min_x']), float(self.eig['max_x']), extra, groesse, aus.daten)
        return {name_w: aus}
