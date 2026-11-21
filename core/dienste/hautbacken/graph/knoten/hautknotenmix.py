# -*- coding: utf-8 -*-
"""Hautknotenmix — die Mix-Knoten: „Mix" (neu, Farbe/Zahl/Vektor) und „MixRGB" (alt). Übernommen aus `intern/cycles/kernel/svm/mix.h` und `svm/color_util.h`
(`svm_mix`, `svm_mix_*`; Blender v5.2.2 — die Überblendungen rechnen dort mit `interp(a, b, t) = a + t * (b - a)`, nicht mit `endvalue_preserving_mix` wie `main`), die Übersetzung der
Knoteneinstellungen aus `scene/shader_nodes.cpp` (`MixNode`, `MixColorNode`, `MixFloatNode`, `MixVectorNode`, `MixVectorNonUniformNode`).
Kerne `hb_mix_*` (`hautbackenkerne_cu/hautknotenkern.cuh`: `svm_mix`; bis 21.11.2026 Warp hier) — die Nummern in `MISCHART` gehören zu den `case` dort.
"""

from ...hautbackenkernbau import Hautbackenkernbau
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotenmix']

MISCHART = {'MIX': 0, 'ADD': 1, 'MULTIPLY': 2, 'SUBTRACT': 3, 'SCREEN': 4, 'DIVIDE': 5, 'DIFFERENCE': 6, 'DARKEN': 7, 'LIGHTEN': 8, 'OVERLAY': 9, 'DODGE': 10,
            'BURN': 11, 'HUE': 12, 'SATURATION': 13, 'VALUE': 14, 'COLOR': 15, 'SOFT_LIGHT': 16, 'LINEAR_LIGHT': 17, 'EXCLUSION': 18}
CLAMP = 19


class Hautknotenmix(Hautknoten):
    TYPEN = ('MIX', 'MIX_RGB')

    def pruefen(self, genutzt):
        gruende = []
        if self.typ == 'MIX':
            art = self.eig.get('data_type')
            if art not in ('RGBA', 'FLOAT', 'VECTOR'):
                gruende.append('Mix-Knoten mit Datenart %s' % art)
            elif art == 'RGBA' and self.eig.get('blend_type') not in MISCHART:
                gruende.append('Mix-Knoten mit Überblendung %s' % self.eig.get('blend_type'))
        elif self.eig.get('blend_type') not in MISCHART:
            gruende.append('MixRGB-Knoten mit Überblendung %s' % self.eig.get('blend_type'))
        return gruende

    def auswerten(self, graph, ctx, modus):
        g = graph.geraet
        rufen = Hautbackenkernbau.lauf
        if self.typ == 'MIX_RGB':
            a, b, fac = (self.ein(graph, ctx, modus, n, art) for n, art in (('Color1', 'c'), ('Color2', 'c'), ('Fac', 'f')))
            aus = Hautwert.leer('c', ctx.n, g)
            rufen('hb_mix_alt', ctx.n, a.daten, b.daten, fac.daten, MISCHART[self.eig['blend_type']], int(bool(self.eig.get('use_clamp'))), aus.daten)
            return {'Color': aus}
        art = self.eig['data_type']
        klemme = int(bool(self.eig.get('clamp_factor')))
        if art == 'RGBA':
            a, b, fac = (self.ein(graph, ctx, modus, n, k) for n, k in (('A_Color', 'c'), ('B_Color', 'c'), ('Factor_Float', 'f')))
            aus = Hautwert.leer('c', ctx.n, g)
            rufen('hb_mix_farbe', ctx.n, a.daten, b.daten, fac.daten, MISCHART[self.eig['blend_type']], klemme, int(bool(self.eig.get('clamp_result'))), aus.daten)
            return {'Result_Color': aus}
        if art == 'FLOAT':
            a, b, fac = (self.ein(graph, ctx, modus, n, 'f') for n in ('A_Float', 'B_Float', 'Factor_Float'))
            aus = Hautwert.leer('f', ctx.n, g)
            rufen('hb_mix_zahl', ctx.n, a.daten, b.daten, fac.daten, klemme, aus.daten)
            return {'Result_Float': aus}
        a, b = (self.ein(graph, ctx, modus, n, 'v') for n in ('A_Vector', 'B_Vector'))
        aus = Hautwert.leer('v', ctx.n, g)
        if self.eig.get('factor_mode') == 'NON_UNIFORM':
            fac = self.ein(graph, ctx, modus, 'Factor_Vector', 'v')
            rufen('hb_mix_vektor_ungleich', ctx.n, a.daten, b.daten, fac.daten, klemme, aus.daten)
        else:
            fac = self.ein(graph, ctx, modus, 'Factor_Float', 'f')
            rufen('hb_mix_vektor', ctx.n, a.daten, b.daten, fac.daten, klemme, aus.daten)
        return {'Result_Vector': aus}
