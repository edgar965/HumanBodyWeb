# -*- coding: utf-8 -*-
"""Hautknotentabelle — Knoten, die Cycles über Tabellen rechnet: „ColorRamp" (Farbverlauf), „RGB Curves", „Vector Curves", „Float Curve". Übernommen aus
`intern/cycles/kernel/svm/ramp.h` (`float_ramp_lookup`, `rgb_ramp_lookup`, `svm_node_rgb_ramp`, `svm_node_curves`, `svm_node_curve`; Blender-Quelltext vom 10.10.2026).
Die Tabellen (257 Einträge) wertet BLENDER im Export aus (`blendmaterialknoten.py`: Farbrampe `evaluate`, Kurven `CurveMapping.evaluate` an denselben Stellen wie
`colorramp_to_array` / `curvemapping_*_to_array`) — der lokale Backer interpoliert nur darin, wie der Kernel es tut.
"""

import numpy as np
import warp as wp

from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotentabelle']


@wp.func
def rgb_ramp_lookup(tab: wp.array(dtype=wp.vec4), f_in: float, interpolieren: int, extrapolieren: int, groesse: int) -> wp.vec4:
    """`rgb_ramp_lookup` (ramp.h)."""
    f = f_in
    if (f < 0.0 or f > 1.0) and extrapolieren > 0:
        t0 = tab[0]
        dy = wp.vec4(0.0, 0.0, 0.0, 0.0)
        if f < 0.0:
            t0 = tab[0]
            dy = t0 - tab[1]
            f = -f
        else:
            t0 = tab[groesse - 1]
            dy = t0 - tab[groesse - 2]
            f = f - 1.0
        return t0 + dy * f * float(groesse - 1)
    f = wp.clamp(f, 0.0, 1.0) * float(groesse - 1)
    i = wp.clamp(int(f), 0, groesse - 1)
    t = f - float(i)
    a = tab[i]
    if interpolieren > 0 and t > 0.0:
        a = (1.0 - t) * a + t * tab[i + 1]
    return a


@wp.func
def float_ramp_lookup(tab: wp.array(dtype=wp.float32), f_in: float, interpolieren: int, extrapolieren: int, groesse: int) -> float:
    """`float_ramp_lookup` (ramp.h)."""
    f = f_in
    if (f < 0.0 or f > 1.0) and extrapolieren > 0:
        t0 = float(0.0)
        dy = float(0.0)
        if f < 0.0:
            t0 = tab[0]
            dy = t0 - tab[1]
            f = -f
        else:
            t0 = tab[groesse - 1]
            dy = t0 - tab[groesse - 2]
            f = f - 1.0
        return t0 + dy * f * float(groesse - 1)
    f = wp.clamp(f, 0.0, 1.0) * float(groesse - 1)
    i = wp.clamp(int(f), 0, groesse - 1)
    t = f - float(i)
    a = tab[i]
    if interpolieren > 0 and t > 0.0:
        a = (1.0 - t) * a + t * tab[i + 1]
    return a


@wp.kernel
def _rampe(fac: wp.array(dtype=wp.float32), tab: wp.array(dtype=wp.vec4), interpolieren: int, groesse: int, farbe: wp.array(dtype=wp.vec3),
           alpha: wp.array(dtype=wp.float32)):
    """`svm_node_rgb_ramp` (ohne Extrapolation)."""
    i = wp.tid()
    c = rgb_ramp_lookup(tab, fac[i], interpolieren, 0, groesse)
    farbe[i] = wp.vec3(c[0], c[1], c[2])
    alpha[i] = c[3]


@wp.kernel
def _kurven(fac: wp.array(dtype=wp.float32), farbe: wp.array(dtype=wp.vec3), tab: wp.array(dtype=wp.vec4), min_x: float, max_x: float, extrapolieren: int,
            groesse: int, aus: wp.array(dtype=wp.vec3)):
    """`svm_node_curves` (RGB- und Vektorkurven)."""
    i = wp.tid()
    c = farbe[i]
    bereich = max_x - min_x
    rel = wp.vec3((c[0] - min_x) / bereich, (c[1] - min_x) / bereich, (c[2] - min_x) / bereich)
    vr = rgb_ramp_lookup(tab, rel[0], 1, extrapolieren, groesse)
    vg = rgb_ramp_lookup(tab, rel[1], 1, extrapolieren, groesse)
    vb = rgb_ramp_lookup(tab, rel[2], 1, extrapolieren, groesse)
    f = fac[i]
    aus[i] = (1.0 - f) * c + f * wp.vec3(vr[0], vg[1], vb[2])


@wp.kernel
def _kurve(fac: wp.array(dtype=wp.float32), wert: wp.array(dtype=wp.float32), tab: wp.array(dtype=wp.float32), min_x: float, max_x: float, extrapolieren: int,
           groesse: int, aus: wp.array(dtype=wp.float32)):
    """`svm_node_curve` (Zahlenkurve)."""
    i = wp.tid()
    w = wert[i]
    rel = (w - min_x) / (max_x - min_x)
    v = float_ramp_lookup(tab, rel, 1, extrapolieren, groesse)
    f = fac[i]
    aus[i] = (1.0 - f) * w + f * v


class Hautknotentabelle(Hautknoten):
    TYPEN = ('VALTORGB', 'CURVE_RGB', 'CURVE_VEC', 'CURVE_FLOAT')

    def pruefen(self, genutzt):
        return [] if self.eig.get('tabelle') else ['%s-Knoten ohne Tabelle im Export' % self.typ]

    def _tabelle(self, graph):
        if not hasattr(self, '_dev'):
            roh = np.asarray(self.eig['tabelle'], dtype=np.float32)
            if self.typ == 'CURVE_FLOAT':
                self._dev = wp.array(roh.reshape(-1), dtype=wp.float32, device=graph.geraet)
            else:
                vier = np.zeros((len(roh), 4), dtype=np.float32)
                vier[:, :roh.shape[1]] = roh
                self._dev = wp.array(vier, dtype=wp.vec4, device=graph.geraet)
        return self._dev

    def auswerten(self, graph, ctx, modus):
        g = graph.geraet
        tab = self._tabelle(graph)
        groesse = len(self.eig['tabelle'])
        if self.typ == 'VALTORGB':
            fac = self.ein(graph, ctx, modus, 'Fac', 'f')
            farbe, alpha = Hautwert.leer('c', ctx.n, g), Hautwert.leer('f', ctx.n, g)
            wp.launch(_rampe, dim=ctx.n, inputs=[fac.daten, tab, int(bool(self.eig['interpolieren'])), groesse, farbe.daten, alpha.daten], device=g)
            return {'Color': farbe, 'Alpha': alpha}
        extra = int(bool(self.eig['extrapolieren']))
        if self.typ == 'CURVE_FLOAT':
            fac, wert = self.ein(graph, ctx, modus, 'Factor', 'f'), self.ein(graph, ctx, modus, 'Value', 'f')
            aus = Hautwert.leer('f', ctx.n, g)
            wp.launch(_kurve, dim=ctx.n, inputs=[fac.daten, wert.daten, tab, float(self.eig['min_x']), float(self.eig['max_x']), extra, groesse, aus.daten], device=g)
            return {'Value': aus}
        name_f, name_w, art = ('Fac', 'Color', 'c') if self.typ == 'CURVE_RGB' else ('Fac', 'Vector', 'v')
        fac, wert = self.ein(graph, ctx, modus, name_f, 'f'), self.ein(graph, ctx, modus, name_w, art)
        aus = Hautwert.leer(art, ctx.n, g)
        wp.launch(_kurven, dim=ctx.n, inputs=[fac.daten, wert.daten, tab, float(self.eig['min_x']), float(self.eig['max_x']), extra, groesse, aus.daten], device=g)
        return {name_w: aus}
