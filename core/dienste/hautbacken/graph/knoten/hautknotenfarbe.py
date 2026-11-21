# -*- coding: utf-8 -*-
"""Hautknotenfarbe — Farbkorrektur-Knoten: „Hue/Saturation/Value", „Brightness/Contrast", „Gamma", „Invert", „RGB to BW". Übernommen aus `intern/cycles/kernel/svm/hsv.h`
(`svm_node_hsv`), `svm/brightness.h` + `color_util.h` (`svm_brightness_contrast`), `svm/gamma.h` + `math_util.h` (`svm_math_gamma_color`), `svm/invert.h`, `svm/convert.h`
(RGB to BW ist `NODE_CONVERT_CF`, siehe `Hautumwandlung`). Blender-Quelltext vom 10.10.2026. Kerne `hb_hsv`, `hb_helligkeit`, `hb_gamma`, `hb_invertieren` (bis 21.11.2026 Warp hier).
"""

from ...hautbackenkernbau import Hautbackenkernbau
from ..hautumwandlung import Hautumwandlung
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotenfarbe']


class Hautknotenfarbe(Hautknoten):
    TYPEN = ('HUE_SAT', 'BRIGHTCONTRAST', 'GAMMA', 'INVERT', 'RGBTOBW')

    def auswerten(self, graph, ctx, modus):
        g = graph.geraet
        rufen = Hautbackenkernbau.lauf
        if self.typ == 'RGBTOBW':
            return {'Val': Hautumwandlung.nach(self.ein(graph, ctx, modus, 'Color', 'c'), 'f', g)}
        farbe = self.ein(graph, ctx, modus, 'Color', 'c')
        aus = Hautwert.leer('c', ctx.n, g)
        if self.typ == 'HUE_SAT':
            h, s, v, f = (self.ein(graph, ctx, modus, n, 'f') for n in ('Hue', 'Saturation', 'Value', 'Fac'))
            rufen('hb_hsv', ctx.n, farbe.daten, h.daten, s.daten, v.daten, f.daten, aus.daten)
        elif self.typ == 'BRIGHTCONTRAST':
            helle, kontrast = (self.ein(graph, ctx, modus, n, 'f') for n in ('Bright', 'Contrast'))
            rufen('hb_helligkeit', ctx.n, farbe.daten, helle.daten, kontrast.daten, aus.daten)
        elif self.typ == 'GAMMA':
            rufen('hb_gamma', ctx.n, farbe.daten, self.ein(graph, ctx, modus, 'Gamma', 'f').daten, aus.daten)
        else:
            rufen('hb_invertieren', ctx.n, farbe.daten, self.ein(graph, ctx, modus, 'Fac', 'f').daten, aus.daten)
        return {'Color': aus}
