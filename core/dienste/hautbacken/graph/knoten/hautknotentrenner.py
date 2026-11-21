# -*- coding: utf-8 -*-
"""Hautknotentrenner — Trennen und Zusammensetzen von Farben und Vektoren, dazu die festen Werte: „Separate/Combine Color" (RGB, HSV, HSL), „Separate/Combine XYZ", „Value", „RGB".
Übernommen aus `intern/cycles/kernel/svm/sepcomb_color.h` + `color_util.h` (`svm_separate_color`, `svm_combine_color`) und `svm/sepcomb_vector.h`; „Value" und „RGB" sind
`ValueNode`/`ColorNode` (der Wert steht im Export als `wert`). Blender-Quelltext vom 10.10.2026. Kerne `hb_farbe_trennen`, `hb_farbe_zusammen`, `hb_trennen_xyz`,
`hb_zusammen_xyz` (bis 21.11.2026 Warp hier).
"""

from ...hautbackenkernbau import Hautbackenkernbau
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotentrenner']

MODI = {'RGB': 0, 'HSV': 1, 'HSL': 2}


class Hautknotentrenner(Hautknoten):
    TYPEN = ('SEPARATE_COLOR', 'COMBINE_COLOR', 'SEPXYZ', 'COMBXYZ', 'VALUE', 'RGB')

    def pruefen(self, genutzt):
        if self.typ in ('SEPARATE_COLOR', 'COMBINE_COLOR') and self.eig.get('mode') not in MODI:
            return ['%s-Knoten mit Modus %s' % (self.typ, self.eig.get('mode'))]
        return []

    def auswerten(self, graph, ctx, modus):
        g = graph.geraet
        rufen = Hautbackenkernbau.lauf
        if self.typ == 'VALUE':
            return {'Value': ctx.konstante('f', float(self.eig['wert']))}
        if self.typ == 'RGB':
            return {'Color': ctx.konstante('c', tuple(self.eig['wert']))}
        if self.typ in ('SEPARATE_COLOR', 'SEPXYZ'):
            farbe = self.ein(graph, ctx, modus, 'Color' if self.typ == 'SEPARATE_COLOR' else 'Vector', 'c' if self.typ == 'SEPARATE_COLOR' else 'v')
            a, b, c = (Hautwert.leer('f', ctx.n, g) for _ in range(3))
            if self.typ == 'SEPARATE_COLOR':
                rufen('hb_farbe_trennen', ctx.n, farbe.daten, MODI[self.eig['mode']], a.daten, b.daten, c.daten)
                return {'Red': a, 'Green': b, 'Blue': c}
            rufen('hb_trennen_xyz', ctx.n, farbe.daten, a.daten, b.daten, c.daten)
            return {'X': a, 'Y': b, 'Z': c}
        namen = ('Red', 'Green', 'Blue') if self.typ == 'COMBINE_COLOR' else ('X', 'Y', 'Z')
        a, b, c = (self.ein(graph, ctx, modus, n, 'f') for n in namen)
        if self.typ == 'COMBINE_COLOR':
            aus = Hautwert.leer('c', ctx.n, g)
            rufen('hb_farbe_zusammen', ctx.n, a.daten, b.daten, c.daten, MODI[self.eig['mode']], aus.daten)
            return {'Color': aus}
        aus = Hautwert.leer('v', ctx.n, g)
        rufen('hb_zusammen_xyz', ctx.n, a.daten, b.daten, c.daten, aus.daten)
        return {'Vector': aus}
