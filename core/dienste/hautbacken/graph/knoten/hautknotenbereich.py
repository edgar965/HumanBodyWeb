# -*- coding: utf-8 -*-
"""Hautknotenbereich — „Map Range" (Zahl und Vektor) und „Clamp". Übernommen aus `intern/cycles/kernel/svm/map_range.h` (`svm_node_map_range`, `svm_node_vector_map_range`)
und `svm/clamp.h`; die Klemmung des Zahlen-Map-Range ist, wie in Cycles, ein nachgeschalteter Klemmknoten (`MapRangeNode::expand`: `NODE_CLAMP_RANGE` mit „To Min"/„To Max").
Blender-Quelltext vom 10.10.2026.
"""

import warp as wp

from ...hautfunktionen import safe_divide, safe_divide3, smootherstep, smoothstep_cycles
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotenbereich']

ART = {'LINEAR': 0, 'STEPPED': 1, 'SMOOTHSTEP': 2, 'SMOOTHERSTEP': 3}


@wp.kernel
def _bereich_zahl(wert: wp.array(dtype=wp.float32), von_min: wp.array(dtype=wp.float32), von_max: wp.array(dtype=wp.float32), nach_min: wp.array(dtype=wp.float32),
                  nach_max: wp.array(dtype=wp.float32), schritte: wp.array(dtype=wp.float32), art: int, klemme: int, aus: wp.array(dtype=wp.float32)):
    """`svm_node_map_range`, danach (bei `klemme`) `svm_node_clamp` im Bereich To Min … To Max."""
    i = wp.tid()
    value = wert[i]
    f0 = von_min[i]
    f1 = von_max[i]
    t0 = nach_min[i]
    t1 = nach_max[i]
    result = float(0.0)
    if f1 != f0:
        factor = value
        if art == 0:
            factor = (value - f0) / (f1 - f0)
        elif art == 1:
            factor = (value - f0) / (f1 - f0)
            if schritte[i] > 0.0:
                factor = wp.floor(factor * (schritte[i] + 1.0)) / schritte[i]
            else:
                factor = 0.0
        elif art == 2:
            if f0 > f1:
                factor = 1.0 - smoothstep_cycles(f1, f0, factor)
            else:
                factor = smoothstep_cycles(f0, f1, factor)
        else:
            if f0 > f1:
                factor = 1.0 - smootherstep(f1, f0, factor)
            else:
                factor = smootherstep(f0, f1, factor)
        result = t0 + factor * (t1 - t0)
    if klemme > 0:
        if t0 > t1:
            result = wp.clamp(result, t1, t0)
        else:
            result = wp.clamp(result, t0, t1)
    aus[i] = result


@wp.kernel
def _bereich_vektor(wert: wp.array(dtype=wp.vec3), von_min: wp.array(dtype=wp.vec3), von_max: wp.array(dtype=wp.vec3), nach_min: wp.array(dtype=wp.vec3),
                    nach_max: wp.array(dtype=wp.vec3), schritte: wp.array(dtype=wp.vec3), art: int, klemme_in: int, aus: wp.array(dtype=wp.vec3)):
    """`svm_node_vector_map_range`."""
    i = wp.tid()
    value = wert[i]
    f0 = von_min[i]
    f1 = von_max[i]
    t0 = nach_min[i]
    t1 = nach_max[i]
    klemme = klemme_in
    if art == 2 or art == 3:
        klemme = 0
    factor = value
    if art == 0:
        factor = safe_divide3(value - f0, f1 - f0)
    elif art == 1:
        factor = safe_divide3(value - f0, f1 - f0)
        s = schritte[i]
        for k in range(3):
            if s[k] > 0.0:
                factor[k] = wp.floor(factor[k] * (s[k] + 1.0)) / s[k]
            else:
                factor[k] = 0.0
    elif art == 2:
        factor = safe_divide3(value - f0, f1 - f0)
        for k in range(3):
            x = wp.clamp(factor[k], 0.0, 1.0)
            factor[k] = (3.0 - 2.0 * x) * (x * x)
    else:
        factor = safe_divide3(value - f0, f1 - f0)
        for k in range(3):
            x = wp.clamp(factor[k], 0.0, 1.0)
            factor[k] = x * x * x * (x * (x * 6.0 - 15.0) + 10.0)
    result = t0 + wp.cw_mul(factor, t1 - t0)
    if klemme > 0:
        for k in range(3):
            if t0[k] > t1[k]:
                result[k] = wp.clamp(result[k], t1[k], t0[k])
            else:
                result[k] = wp.clamp(result[k], t0[k], t1[k])
    aus[i] = result


@wp.kernel
def _klemmen(wert: wp.array(dtype=wp.float32), kleinst: wp.array(dtype=wp.float32), groesst: wp.array(dtype=wp.float32), bereich: int, aus: wp.array(dtype=wp.float32)):
    """`svm_node_clamp`: im Modus RANGE und Min > Max sind die Grenzen vertauscht."""
    i = wp.tid()
    if bereich > 0 and kleinst[i] > groesst[i]:
        aus[i] = wp.clamp(wert[i], groesst[i], kleinst[i])
    else:
        aus[i] = wp.clamp(wert[i], kleinst[i], groesst[i])


class Hautknotenbereich(Hautknoten):
    TYPEN = ('MAP_RANGE', 'CLAMP')

    def pruefen(self, genutzt):
        if self.typ == 'CLAMP':
            return [] if self.eig.get('clamp_type') in ('MINMAX', 'RANGE') else ['Clamp-Knoten mit Art %s' % self.eig.get('clamp_type')]
        gruende = []
        if self.eig.get('interpolation_type') not in ART:
            gruende.append('Map-Range-Knoten mit Art %s' % self.eig.get('interpolation_type'))
        if self.eig.get('data_type') not in ('FLOAT', 'FLOAT_VECTOR'):
            gruende.append('Map-Range-Knoten mit Datenart %s' % self.eig.get('data_type'))
        return gruende

    def auswerten(self, graph, ctx, modus):
        g = graph.geraet
        if self.typ == 'CLAMP':
            wert, kleinst, groesst = (self.ein(graph, ctx, modus, n, 'f') for n in ('Value', 'Min', 'Max'))
            aus = Hautwert.leer('f', ctx.n, g)
            wp.launch(_klemmen, dim=ctx.n, inputs=[wert.daten, kleinst.daten, groesst.daten, int(self.eig['clamp_type'] == 'RANGE'), aus.daten], device=g)
            return {'Result': aus}
        art = ART[self.eig['interpolation_type']]
        klemme = int(bool(self.eig.get('clamp')))
        if self.eig['data_type'] == 'FLOAT':
            wert, a, b, c, d = (self.ein(graph, ctx, modus, n, 'f') for n in ('Value', 'From Min', 'From Max', 'To Min', 'To Max'))
            s = self.ein_oder(graph, ctx, modus, 'Steps', 'f', 4.0)
            aus = Hautwert.leer('f', ctx.n, g)
            wp.launch(_bereich_zahl, dim=ctx.n, inputs=[wert.daten, a.daten, b.daten, c.daten, d.daten, s.daten, art, klemme, aus.daten], device=g)
            return {'Result': aus}
        wert, a, b, c, d = (self.ein(graph, ctx, modus, n, 'v') for n in ('Vector', 'From_Min_FLOAT3', 'From_Max_FLOAT3', 'To_Min_FLOAT3', 'To_Max_FLOAT3'))
        s = self.ein_oder(graph, ctx, modus, 'Steps_FLOAT3', 'v', (4.0, 4.0, 4.0))
        aus = Hautwert.leer('v', ctx.n, g)
        wp.launch(_bereich_vektor, dim=ctx.n, inputs=[wert.daten, a.daten, b.daten, c.daten, d.daten, s.daten, art, klemme, aus.daten], device=g)
        return {'Vector': aus}
