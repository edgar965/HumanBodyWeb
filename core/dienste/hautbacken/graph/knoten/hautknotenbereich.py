# -*- coding: utf-8 -*-
"""Hautknotenbereich — „Map Range" (Zahl und Vektor) und „Clamp". Übernommen aus `intern/cycles/kernel/svm/map_range.h` (`svm_node_map_range`, `svm_node_vector_map_range`)
und `svm/clamp.h`; die Klemmung des Zahlen-Map-Range ist, wie in Cycles, ein nachgeschalteter Klemmknoten (`MapRangeNode::expand`: `NODE_CLAMP_RANGE` mit „To Min"/„To Max").
Blender-Quelltext vom 10.10.2026. Kerne `hb_bereich_zahl`, `hb_bereich_vektor`, `hb_klemmen` (`hautbackenkerne_cu/hautknotenkern.cuh`; bis 21.11.2026 Warp hier).
"""

from ...hautbackenkernbau import Hautbackenkernbau
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotenbereich']

ART = {'LINEAR': 0, 'STEPPED': 1, 'SMOOTHSTEP': 2, 'SMOOTHERSTEP': 3}


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
        rufen = Hautbackenkernbau.lauf
        if self.typ == 'CLAMP':
            wert, kleinst, groesst = (self.ein(graph, ctx, modus, n, 'f') for n in ('Value', 'Min', 'Max'))
            aus = Hautwert.leer('f', ctx.n, g)
            rufen('hb_klemmen', ctx.n, wert.daten, kleinst.daten, groesst.daten, int(self.eig['clamp_type'] == 'RANGE'), aus.daten)
            return {'Result': aus}
        art = ART[self.eig['interpolation_type']]
        klemme = int(bool(self.eig.get('clamp')))
        if self.eig['data_type'] == 'FLOAT':
            wert, a, b, c, d = (self.ein(graph, ctx, modus, n, 'f') for n in ('Value', 'From Min', 'From Max', 'To Min', 'To Max'))
            s = self.ein_oder(graph, ctx, modus, 'Steps', 'f', 4.0)
            aus = Hautwert.leer('f', ctx.n, g)
            rufen('hb_bereich_zahl', ctx.n, wert.daten, a.daten, b.daten, c.daten, d.daten, s.daten, art, klemme, aus.daten)
            return {'Result': aus}
        wert, a, b, c, d = (self.ein(graph, ctx, modus, n, 'v') for n in ('Vector', 'From_Min_FLOAT3', 'From_Max_FLOAT3', 'To_Min_FLOAT3', 'To_Max_FLOAT3'))
        s = self.ein_oder(graph, ctx, modus, 'Steps_FLOAT3', 'v', (4.0, 4.0, 4.0))
        aus = Hautwert.leer('v', ctx.n, g)
        rufen('hb_bereich_vektor', ctx.n, wert.daten, a.daten, b.daten, c.daten, d.daten, s.daten, art, klemme, aus.daten)
        return {'Vector': aus}
