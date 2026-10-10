# -*- coding: utf-8 -*-
"""Hautknotenfarbe — Farbkorrektur-Knoten: „Hue/Saturation/Value", „Brightness/Contrast", „Gamma", „Invert", „RGB to BW". Übernommen aus `intern/cycles/kernel/svm/hsv.h`
(`svm_node_hsv`), `svm/brightness.h` + `color_util.h` (`svm_brightness_contrast`), `svm/gamma.h` + `math_util.h` (`svm_math_gamma_color`), `svm/invert.h`, `svm/convert.h`
(RGB to BW ist `NODE_CONVERT_CF`, siehe `Hautumwandlung`). Blender-Quelltext vom 10.10.2026.
"""

import warp as wp

from ...hautfunktionen import fractf, hsv_to_rgb, rgb_to_hsv
from ..hautumwandlung import Hautumwandlung
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotenfarbe']


@wp.kernel
def _hsv(farbe: wp.array(dtype=wp.vec3), farbton: wp.array(dtype=wp.float32), saettigung: wp.array(dtype=wp.float32), wert: wp.array(dtype=wp.float32),
         fac: wp.array(dtype=wp.float32), aus: wp.array(dtype=wp.vec3)):
    """`svm_node_hsv`."""
    i = wp.tid()
    in_color = farbe[i]
    c = rgb_to_hsv(in_color)
    c = wp.vec3(fractf(c[0] + farbton[i] + 0.5), wp.clamp(c[1] * saettigung[i], 0.0, 1.0), c[2] * wert[i])
    c = hsv_to_rgb(c)
    f = fac[i]
    c = wp.vec3(f * c[0] + (1.0 - f) * in_color[0], f * c[1] + (1.0 - f) * in_color[1], f * c[2] + (1.0 - f) * in_color[2])
    aus[i] = wp.vec3(wp.max(c[0], 0.0), wp.max(c[1], 0.0), wp.max(c[2], 0.0))     # „Clamp color to prevent negative values caused by over saturation"


@wp.kernel
def _helligkeit(farbe: wp.array(dtype=wp.vec3), helligkeit: wp.array(dtype=wp.float32), kontrast: wp.array(dtype=wp.float32), aus: wp.array(dtype=wp.vec3)):
    """`svm_node_brightness` → `svm_brightness_contrast`."""
    i = wp.tid()
    a = 1.0 + kontrast[i]
    b = helligkeit[i] - kontrast[i] * 0.5
    c = farbe[i]
    aus[i] = wp.vec3(wp.max(a * c[0] + b, 0.0), wp.max(a * c[1] + b, 0.0), wp.max(a * c[2] + b, 0.0))


@wp.kernel
def _gamma(farbe: wp.array(dtype=wp.vec3), gamma: wp.array(dtype=wp.float32), aus: wp.array(dtype=wp.vec3)):
    """`svm_node_gamma` → `svm_math_gamma_color`: Gamma 0 → Weiß; nur positive Komponenten werden potenziert."""
    i = wp.tid()
    c = farbe[i]
    g = gamma[i]
    if g == 0.0:
        aus[i] = wp.vec3(1.0, 1.0, 1.0)
        return
    for k in range(3):
        if c[k] > 0.0:
            c[k] = wp.pow(c[k], g)
    aus[i] = c


@wp.kernel
def _invertieren(farbe: wp.array(dtype=wp.vec3), fac: wp.array(dtype=wp.float32), aus: wp.array(dtype=wp.vec3)):
    """`svm_node_invert`: factor · (1 − color) + (1 − factor) · color."""
    i = wp.tid()
    c = farbe[i]
    f = fac[i]
    aus[i] = wp.vec3(f * (1.0 - c[0]) + (1.0 - f) * c[0], f * (1.0 - c[1]) + (1.0 - f) * c[1], f * (1.0 - c[2]) + (1.0 - f) * c[2])


class Hautknotenfarbe(Hautknoten):
    TYPEN = ('HUE_SAT', 'BRIGHTCONTRAST', 'GAMMA', 'INVERT', 'RGBTOBW')

    def auswerten(self, graph, ctx, modus):
        g = graph.geraet
        if self.typ == 'RGBTOBW':
            return {'Val': Hautumwandlung.nach(self.ein(graph, ctx, modus, 'Color', 'c'), 'f', g)}
        farbe = self.ein(graph, ctx, modus, 'Color', 'c')
        aus = Hautwert.leer('c', ctx.n, g)
        if self.typ == 'HUE_SAT':
            h, s, v, f = (self.ein(graph, ctx, modus, n, 'f') for n in ('Hue', 'Saturation', 'Value', 'Fac'))
            wp.launch(_hsv, dim=ctx.n, inputs=[farbe.daten, h.daten, s.daten, v.daten, f.daten, aus.daten], device=g)
        elif self.typ == 'BRIGHTCONTRAST':
            helle, kontrast = (self.ein(graph, ctx, modus, n, 'f') for n in ('Bright', 'Contrast'))
            wp.launch(_helligkeit, dim=ctx.n, inputs=[farbe.daten, helle.daten, kontrast.daten, aus.daten], device=g)
        elif self.typ == 'GAMMA':
            wp.launch(_gamma, dim=ctx.n, inputs=[farbe.daten, self.ein(graph, ctx, modus, 'Gamma', 'f').daten, aus.daten], device=g)
        else:
            wp.launch(_invertieren, dim=ctx.n, inputs=[farbe.daten, self.ein(graph, ctx, modus, 'Fac', 'f').daten, aus.daten], device=g)
        return {'Color': aus}
