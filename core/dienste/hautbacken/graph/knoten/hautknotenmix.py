# -*- coding: utf-8 -*-
"""Hautknotenmix — die Mix-Knoten: „Mix" (neu, Farbe/Zahl/Vektor) und „MixRGB" (alt). Übernommen aus `intern/cycles/kernel/svm/mix.h` und `svm/color_util.h`
(`svm_mix`, `svm_mix_*`; Blender-Quelltext vom 10.10.2026), die Übersetzung der Knoteneinstellungen aus `scene/shader_nodes.cpp` (`MixNode`, `MixColorNode`,
`MixFloatNode`, `MixVectorNode`, `MixVectorNonUniformNode`).
"""

import warp as wp

from ...hautfunktionen import hsv_to_rgb, rgb_to_hsv, saturate3
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotenmix']

#: Blender-Name der Überblendung → `NodeMix` in Cycles (`kernel/types.h`).
MISCHART = {'MIX': 0, 'ADD': 1, 'MULTIPLY': 2, 'SUBTRACT': 3, 'SCREEN': 4, 'DIVIDE': 5, 'DIFFERENCE': 6, 'DARKEN': 7, 'LIGHTEN': 8, 'OVERLAY': 9, 'DODGE': 10,
            'BURN': 11, 'HUE': 12, 'SATURATION': 13, 'VALUE': 14, 'COLOR': 15, 'SOFT_LIGHT': 16, 'LINEAR_LIGHT': 17, 'EXCLUSION': 18}
CLAMP = 19


@wp.func
def _ueberlagern(c1: float, c2: float, t: float, tm: float) -> float:
    """Eine Komponente von `svm_mix_overlay`."""
    if c1 < 0.5:
        return c1 * (tm + 2.0 * t * c2)
    return 1.0 - (tm + 2.0 * t * (1.0 - c2)) * (1.0 - c1)


@wp.func
def _teilen(c1: float, c2: float, t: float, tm: float) -> float:
    """Eine Komponente von `svm_mix_div`."""
    if c2 != 0.0:
        return tm * c1 + t * c1 / c2
    return c1


@wp.func
def _abwedeln(c1: float, c2: float, t: float) -> float:
    """Eine Komponente von `svm_mix_dodge`."""
    if c1 != 0.0:
        tmp = 1.0 - t * c2
        if tmp <= 0.0:
            return 1.0
        tmp = c1 / tmp
        if tmp > 1.0:
            return 1.0
        return tmp
    return c1


@wp.func
def _nachbelichten(c1: float, c2: float, t: float, tm: float) -> float:
    """Eine Komponente von `svm_mix_burn`."""
    tmp = tm + t * c2
    if tmp <= 0.0:
        return 0.0
    tmp = 1.0 - (1.0 - c1) / tmp
    if tmp < 0.0:
        return 0.0
    if tmp > 1.0:
        return 1.0
    return tmp


@wp.func
def svm_mix(typ: int, t: float, c1: wp.vec3, c2: wp.vec3) -> wp.vec3:
    """`svm_mix(NodeMix type, t, c1, c2)` (color_util.h)."""
    tm = 1.0 - t
    one = wp.vec3(1.0, 1.0, 1.0)
    out = c1
    if typ == 0:                                           # svm_mix_blend: endvalue_preserving_mix
        out = (1.0 - t) * c1 + t * c2
    elif typ == 1:                                         # add
        out = c1 + t * c2
    elif typ == 2:                                         # mul
        out = wp.cw_mul(c1, wp.vec3(tm, tm, tm) + t * c2)
    elif typ == 3:                                         # sub
        out = c1 - t * c2
    elif typ == 4:                                         # screen
        out = one - wp.cw_mul(wp.vec3(tm, tm, tm) + t * (one - c2), one - c1)
    elif typ == 5:                                         # div
        out = wp.vec3(_teilen(c1[0], c2[0], t, tm), _teilen(c1[1], c2[1], t, tm), _teilen(c1[2], c2[2], t, tm))
    elif typ == 6:                                         # diff: interp(col1, fabs(col1 - col2), t)
        out = c1 + t * (wp.vec3(wp.abs(c1[0] - c2[0]), wp.abs(c1[1] - c2[1]), wp.abs(c1[2] - c2[2])) - c1)
    elif typ == 7:                                         # dark: interp(col1, min(col1, col2), t)
        out = c1 + t * (wp.vec3(wp.min(c1[0], c2[0]), wp.min(c1[1], c2[1]), wp.min(c1[2], c2[2])) - c1)
    elif typ == 8:                                         # light
        out = c1 + t * (wp.vec3(wp.max(c1[0], c2[0]), wp.max(c1[1], c2[1]), wp.max(c1[2], c2[2])) - c1)
    elif typ == 9:                                         # overlay
        out = wp.vec3(_ueberlagern(c1[0], c2[0], t, tm), _ueberlagern(c1[1], c2[1], t, tm), _ueberlagern(c1[2], c2[2], t, tm))
    elif typ == 10:                                        # dodge
        out = wp.vec3(_abwedeln(c1[0], c2[0], t), _abwedeln(c1[1], c2[1], t), _abwedeln(c1[2], c2[2], t))
    elif typ == 11:                                        # burn
        out = wp.vec3(_nachbelichten(c1[0], c2[0], t, tm), _nachbelichten(c1[1], c2[1], t, tm), _nachbelichten(c1[2], c2[2], t, tm))
    elif typ == 12:                                        # hue
        hsv2 = rgb_to_hsv(c2)
        if hsv2[1] != 0.0:
            hsv = rgb_to_hsv(c1)
            hsv = wp.vec3(hsv2[0], hsv[1], hsv[2])
            tmp = hsv_to_rgb(hsv)
            out = c1 + t * (tmp - c1)
    elif typ == 13:                                        # sat
        hsv = rgb_to_hsv(c1)
        if hsv[1] != 0.0:
            hsv2 = rgb_to_hsv(c2)
            hsv = wp.vec3(hsv[0], tm * hsv[1] + t * hsv2[1], hsv[2])
            out = hsv_to_rgb(hsv)
    elif typ == 14:                                        # val
        hsv = rgb_to_hsv(c1)
        hsv2 = rgb_to_hsv(c2)
        hsv = wp.vec3(hsv[0], hsv[1], tm * hsv[2] + t * hsv2[2])
        out = hsv_to_rgb(hsv)
    elif typ == 15:                                        # color
        hsv2 = rgb_to_hsv(c2)
        if hsv2[1] != 0.0:
            hsv = rgb_to_hsv(c1)
            hsv = wp.vec3(hsv2[0], hsv2[1], hsv[2])
            tmp = hsv_to_rgb(hsv)
            out = c1 + t * (tmp - c1)
    elif typ == 16:                                        # soft
        scr = one - wp.cw_mul(one - c2, one - c1)
        out = tm * c1 + t * (wp.cw_mul(wp.cw_mul(one - c1, c2), c1) + wp.cw_mul(c1, scr))
    elif typ == 17:                                        # linear
        out = c1 + t * (2.0 * c2 + wp.vec3(-1.0, -1.0, -1.0))
    elif typ == 18:                                        # exclusion: max(interp(col1, col1 + col2 - 2 col1 col2, t), 0)
        e = c1 + t * (c1 + c2 - 2.0 * wp.cw_mul(c1, c2) - c1)
        out = wp.vec3(wp.max(e[0], 0.0), wp.max(e[1], 0.0), wp.max(e[2], 0.0))
    elif typ == 19:                                        # clamp
        out = saturate3(c1)
    return out


@wp.kernel
def _mix_farbe(a: wp.array(dtype=wp.vec3), b: wp.array(dtype=wp.vec3), fac: wp.array(dtype=wp.float32), typ: int, klemme: int, klemme_ergebnis: int,
               aus: wp.array(dtype=wp.vec3)):
    """`svm_node_mix_color`."""
    i = wp.tid()
    t = fac[i]
    if klemme > 0:
        t = wp.clamp(t, 0.0, 1.0)
    r = svm_mix(typ, t, a[i], b[i])
    if klemme_ergebnis > 0:
        r = saturate3(r)
    aus[i] = r


@wp.kernel
def _mix_alt(a: wp.array(dtype=wp.vec3), b: wp.array(dtype=wp.vec3), fac: wp.array(dtype=wp.float32), typ: int, klemme: int, aus: wp.array(dtype=wp.vec3)):
    """`svm_node_mix` (MixRGB): der Faktor wird immer auf 0…1 geklemmt (`svm_mix_clamped_factor`); `use_clamp` klemmt danach das Ergebnis (zweiter Knoten `NODE_MIX_CLAMP`)."""
    i = wp.tid()
    r = svm_mix(typ, wp.clamp(fac[i], 0.0, 1.0), a[i], b[i])
    if klemme > 0:
        r = saturate3(r)
    aus[i] = r


@wp.kernel
def _mix_zahl(a: wp.array(dtype=wp.float32), b: wp.array(dtype=wp.float32), fac: wp.array(dtype=wp.float32), klemme: int, aus: wp.array(dtype=wp.float32)):
    """`svm_node_mix_float`: endvalue_preserving_mix."""
    i = wp.tid()
    t = fac[i]
    if klemme > 0:
        t = wp.clamp(t, 0.0, 1.0)
    aus[i] = (1.0 - t) * a[i] + t * b[i]


@wp.kernel
def _mix_vektor(a: wp.array(dtype=wp.vec3), b: wp.array(dtype=wp.vec3), fac: wp.array(dtype=wp.float32), klemme: int, aus: wp.array(dtype=wp.vec3)):
    """`svm_node_mix_vector`."""
    i = wp.tid()
    t = fac[i]
    if klemme > 0:
        t = wp.clamp(t, 0.0, 1.0)
    aus[i] = (1.0 - t) * a[i] + t * b[i]


@wp.kernel
def _mix_vektor_ungleich(a: wp.array(dtype=wp.vec3), b: wp.array(dtype=wp.vec3), fac: wp.array(dtype=wp.vec3), klemme: int, aus: wp.array(dtype=wp.vec3)):
    """`svm_node_mix_vector_non_uniform`: ein Faktor je Komponente."""
    i = wp.tid()
    t = fac[i]
    if klemme > 0:
        t = saturate3(t)
    aus[i] = wp.cw_mul(wp.vec3(1.0, 1.0, 1.0) - t, a[i]) + wp.cw_mul(t, b[i])


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
        if self.typ == 'MIX_RGB':
            a, b, fac = (self.ein(graph, ctx, modus, n, art) for n, art in (('Color1', 'c'), ('Color2', 'c'), ('Fac', 'f')))
            aus = Hautwert.leer('c', ctx.n, g)
            wp.launch(_mix_alt, dim=ctx.n, inputs=[a.daten, b.daten, fac.daten, MISCHART[self.eig['blend_type']], int(bool(self.eig.get('use_clamp'))), aus.daten], device=g)
            return {'Color': aus}
        art = self.eig['data_type']
        klemme = int(bool(self.eig.get('clamp_factor')))
        if art == 'RGBA':
            a, b, fac = (self.ein(graph, ctx, modus, n, k) for n, k in (('A_Color', 'c'), ('B_Color', 'c'), ('Factor_Float', 'f')))
            aus = Hautwert.leer('c', ctx.n, g)
            wp.launch(_mix_farbe, dim=ctx.n, inputs=[a.daten, b.daten, fac.daten, MISCHART[self.eig['blend_type']], klemme, int(bool(self.eig.get('clamp_result'))), aus.daten],
                      device=g)
            return {'Result_Color': aus}
        if art == 'FLOAT':
            a, b, fac = (self.ein(graph, ctx, modus, n, 'f') for n in ('A_Float', 'B_Float', 'Factor_Float'))
            aus = Hautwert.leer('f', ctx.n, g)
            wp.launch(_mix_zahl, dim=ctx.n, inputs=[a.daten, b.daten, fac.daten, klemme, aus.daten], device=g)
            return {'Result_Float': aus}
        a, b = (self.ein(graph, ctx, modus, n, 'v') for n in ('A_Vector', 'B_Vector'))
        aus = Hautwert.leer('v', ctx.n, g)
        if self.eig.get('factor_mode') == 'NON_UNIFORM':
            fac = self.ein(graph, ctx, modus, 'Factor_Vector', 'v')
            wp.launch(_mix_vektor_ungleich, dim=ctx.n, inputs=[a.daten, b.daten, fac.daten, klemme, aus.daten], device=g)
        else:
            fac = self.ein(graph, ctx, modus, 'Factor_Float', 'f')
            wp.launch(_mix_vektor, dim=ctx.n, inputs=[a.daten, b.daten, fac.daten, klemme, aus.daten], device=g)
        return {'Result_Vector': aus}
