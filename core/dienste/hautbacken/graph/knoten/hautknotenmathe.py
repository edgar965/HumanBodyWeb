# -*- coding: utf-8 -*-
"""Hautknotenmathe — die Knoten „Math" und „Vector Math". Übernommen aus `intern/cycles/kernel/svm/math_util.h` (`svm_math`, `svm_vector_math`; Blender-Quelltext vom
10.10.2026); „Use Clamp" folgt `MathNode::expand` (`scene/shader_nodes.cpp`): ein Klemmknoten 0…1 hinter dem Ergebnis. Kerne `hb_mathe`, `hb_vektor_mathe`
(`hautbackenkerne_cu/hautknotenkern.cuh`: `svm_math`, `komponenten`; bis 21.11.2026 Warp hier) — die Nummern der Rechenarten gehören zu den `case` dort.
"""

from ...hautbackenkernbau import Hautbackenkernbau
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotenmathe']

#: Blender-Name der Rechenart → eigene Nummer (Kern und Tabelle gehören zusammen).
MATHE = {name: i for i, name in enumerate((
    'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MULTIPLY_ADD', 'POWER', 'LOGARITHM', 'SQRT', 'INVERSE_SQRT', 'ABSOLUTE', 'EXPONENT', 'MINIMUM', 'MAXIMUM', 'LESS_THAN',
    'GREATER_THAN', 'SIGN', 'COMPARE', 'SMOOTH_MIN', 'SMOOTH_MAX', 'ROUND', 'FLOOR', 'CEIL', 'TRUNC', 'FRACT', 'MODULO', 'FLOORED_MODULO', 'WRAP', 'SNAP', 'PINGPONG',
    'SINE', 'COSINE', 'TANGENT', 'ARCSINE', 'ARCCOSINE', 'ARCTANGENT', 'ARCTAN2', 'SINH', 'COSH', 'TANH', 'RADIANS', 'DEGREES'))}
VEKTOR = {name: i for i, name in enumerate((
    'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MULTIPLY_ADD', 'CROSS_PRODUCT', 'PROJECT', 'REFLECT', 'REFRACT', 'FACEFORWARD', 'DOT_PRODUCT', 'DISTANCE', 'LENGTH',
    'SCALE', 'NORMALIZE', 'ABSOLUTE', 'POWER', 'SIGN', 'MINIMUM', 'MAXIMUM', 'ROUND', 'FLOOR', 'CEIL', 'FRACTION', 'MODULO', 'WRAP', 'SNAP', 'SINE', 'COSINE',
    'TANGENT'))}
#: Die Vektor-Rechenarten, die eine Zahl statt eines Vektors liefern (Ausgang „Value").
VEKTOR_ZAHL = {'DOT_PRODUCT', 'DISTANCE', 'LENGTH'}


class Hautknotenmathe(Hautknoten):
    TYPEN = ('MATH', 'VECT_MATH')

    def pruefen(self, genutzt):
        tabelle = MATHE if self.typ == 'MATH' else VEKTOR
        op = self.eig.get('operation')
        return [] if op in tabelle else ['%s-Knoten mit Rechenart %s' % (self.typ, op)]

    def _eingang_oder_null(self, graph, ctx, modus, name, art):
        if self.hat(name):
            return self.ein(graph, ctx, modus, name, art).daten
        return ctx.konstante(art, 0.0 if art == 'f' else (0.0, 0.0, 0.0)).daten

    def auswerten(self, graph, ctx, modus):
        g = graph.geraet
        if self.typ == 'MATH':
            a, b, c = (self._eingang_oder_null(graph, ctx, modus, n, 'f') for n in ('Value', 'Value_001', 'Value_002'))
            aus = Hautwert.leer('f', ctx.n, g)
            Hautbackenkernbau.lauf('hb_mathe', ctx.n, a, b, c, MATHE[self.eig['operation']], int(bool(self.eig.get('use_clamp'))), aus.daten)
            return {'Value': aus}
        a, b, c = (self._eingang_oder_null(graph, ctx, modus, n, 'v') for n in ('Vector', 'Vector_001', 'Vector_002'))
        skala = self._eingang_oder_null(graph, ctx, modus, 'Scale', 'f')
        vektor, wert = Hautwert.leer('v', ctx.n, g), Hautwert.leer('f', ctx.n, g)
        Hautbackenkernbau.lauf('hb_vektor_mathe', ctx.n, a, b, c, skala, VEKTOR[self.eig['operation']], vektor.daten, wert.daten)
        return {'Vector': vektor, 'Value': wert}
