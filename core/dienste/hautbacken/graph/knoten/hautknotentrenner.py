# -*- coding: utf-8 -*-
"""Hautknotentrenner — Trennen und Zusammensetzen von Farben und Vektoren, dazu die festen Werte: „Separate/Combine Color" (RGB, HSV, HSL), „Separate/Combine XYZ", „Value", „RGB".
Übernommen aus `intern/cycles/kernel/svm/sepcomb_color.h` + `color_util.h` (`svm_separate_color`, `svm_combine_color`) und `svm/sepcomb_vector.h`; „Value" und „RGB" sind
`ValueNode`/`ColorNode` (der Wert steht im Export als `wert`). Blender-Quelltext vom 10.10.2026.
"""

import warp as wp

from ...hautfunktionen import hsl_to_rgb, hsv_to_rgb, rgb_to_hsl, rgb_to_hsv
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotentrenner']

MODI = {'RGB': 0, 'HSV': 1, 'HSL': 2}


@wp.kernel
def _trennen(farbe: wp.array(dtype=wp.vec3), modus: int, r: wp.array(dtype=wp.float32), g: wp.array(dtype=wp.float32), b: wp.array(dtype=wp.float32)):
    """`svm_node_separate_color` (`svm_separate_color`)."""
    i = wp.tid()
    c = farbe[i]
    if modus == 1:
        c = rgb_to_hsv(c)
    elif modus == 2:
        c = rgb_to_hsl(c)
    r[i] = c[0]
    g[i] = c[1]
    b[i] = c[2]


@wp.kernel
def _zusammen(r: wp.array(dtype=wp.float32), g: wp.array(dtype=wp.float32), b: wp.array(dtype=wp.float32), modus: int, aus: wp.array(dtype=wp.vec3)):
    """`svm_node_combine_color` (`svm_combine_color`)."""
    i = wp.tid()
    c = wp.vec3(r[i], g[i], b[i])
    if modus == 1:
        c = hsv_to_rgb(c)
    elif modus == 2:
        c = hsl_to_rgb(c)
    aus[i] = c


@wp.kernel
def _trennen_xyz(v: wp.array(dtype=wp.vec3), x: wp.array(dtype=wp.float32), y: wp.array(dtype=wp.float32), z: wp.array(dtype=wp.float32)):
    i = wp.tid()
    x[i] = v[i][0]
    y[i] = v[i][1]
    z[i] = v[i][2]


@wp.kernel
def _zusammen_xyz(x: wp.array(dtype=wp.float32), y: wp.array(dtype=wp.float32), z: wp.array(dtype=wp.float32), aus: wp.array(dtype=wp.vec3)):
    i = wp.tid()
    aus[i] = wp.vec3(x[i], y[i], z[i])


class Hautknotentrenner(Hautknoten):
    TYPEN = ('SEPARATE_COLOR', 'COMBINE_COLOR', 'SEPXYZ', 'COMBXYZ', 'VALUE', 'RGB')

    def pruefen(self, genutzt):
        if self.typ in ('SEPARATE_COLOR', 'COMBINE_COLOR') and self.eig.get('mode') not in MODI:
            return ['%s-Knoten mit Modus %s' % (self.typ, self.eig.get('mode'))]
        return []

    def auswerten(self, graph, ctx, modus):
        g = graph.geraet
        if self.typ == 'VALUE':
            return {'Value': ctx.konstante('f', float(self.eig['wert']))}
        if self.typ == 'RGB':
            return {'Color': ctx.konstante('c', tuple(self.eig['wert']))}
        if self.typ in ('SEPARATE_COLOR', 'SEPXYZ'):
            farbe = self.ein(graph, ctx, modus, 'Color' if self.typ == 'SEPARATE_COLOR' else 'Vector', 'c' if self.typ == 'SEPARATE_COLOR' else 'v')
            a, b, c = (Hautwert.leer('f', ctx.n, g) for _ in range(3))
            if self.typ == 'SEPARATE_COLOR':
                wp.launch(_trennen, dim=ctx.n, inputs=[farbe.daten, MODI[self.eig['mode']], a.daten, b.daten, c.daten], device=g)
                return {'Red': a, 'Green': b, 'Blue': c}
            wp.launch(_trennen_xyz, dim=ctx.n, inputs=[farbe.daten, a.daten, b.daten, c.daten], device=g)
            return {'X': a, 'Y': b, 'Z': c}
        namen = ('Red', 'Green', 'Blue') if self.typ == 'COMBINE_COLOR' else ('X', 'Y', 'Z')
        a, b, c = (self.ein(graph, ctx, modus, n, 'f') for n in namen)
        if self.typ == 'COMBINE_COLOR':
            aus = Hautwert.leer('c', ctx.n, g)
            wp.launch(_zusammen, dim=ctx.n, inputs=[a.daten, b.daten, c.daten, MODI[self.eig['mode']], aus.daten], device=g)
            return {'Color': aus}
        aus = Hautwert.leer('v', ctx.n, g)
        wp.launch(_zusammen_xyz, dim=ctx.n, inputs=[a.daten, b.daten, c.daten, aus.daten], device=g)
        return {'Vector': aus}
