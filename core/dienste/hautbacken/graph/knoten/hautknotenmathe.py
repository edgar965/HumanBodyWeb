# -*- coding: utf-8 -*-
"""Hautknotenmathe — die Knoten „Math" und „Vector Math". Übernommen aus `intern/cycles/kernel/svm/math_util.h` (`svm_math`, `svm_vector_math`; Blender-Quelltext vom
10.10.2026); „Use Clamp" folgt `MathNode::expand` (`scene/shader_nodes.cpp`): ein Klemmknoten 0…1 hinter dem Ergebnis.
"""

import warp as wp

from ...hautfunktionen import (
    PI_F,
    compatible_atan2,
    compatible_signf,
    faceforward3,
    inversesqrtf,
    pingpongf,
    project3,
    reflect3,
    refract3,
    safe_acosf,
    safe_asinf,
    safe_divide,
    safe_divide3,
    safe_floored_modulo,
    safe_fmod3,
    safe_logf,
    safe_modulo,
    safe_normalize3,
    safe_pow3,
    safe_powf,
    safe_sqrtf,
    smoothminf,
    wrap3,
    wrapf,
)
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotenmathe']

#: Blender-Name der Rechenart → eigene Nummer (die Reihenfolge ist egal, Kernel und Tabelle gehören zusammen).
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
M_PI_F = wp.constant(PI_F)
FLT_EPSILON = wp.constant(1.1920929e-07)


@wp.func
def svm_math(typ: int, a: float, b: float, c: float) -> float:
    """`svm_math(NodeMathType, a, b, c)` (math_util.h)."""
    r = float(0.0)
    if typ == 0:
        r = a + b
    elif typ == 1:
        r = a - b
    elif typ == 2:
        r = a * b
    elif typ == 3:
        r = safe_divide(a, b)
    elif typ == 4:
        r = a * b + c
    elif typ == 5:
        r = safe_powf(a, b)
    elif typ == 6:
        r = safe_logf(a, b)
    elif typ == 7:
        r = safe_sqrtf(a)
    elif typ == 8:
        r = inversesqrtf(a)
    elif typ == 9:
        r = wp.abs(a)
    elif typ == 10:
        r = wp.exp(a)
    elif typ == 11:
        r = wp.min(a, b)
    elif typ == 12:
        r = wp.max(a, b)
    elif typ == 13:
        if a < b:
            r = 1.0
    elif typ == 14:
        if a > b:
            r = 1.0
    elif typ == 15:
        r = compatible_signf(a)
    elif typ == 16:
        if a == b or wp.abs(a - b) <= wp.max(c, FLT_EPSILON):
            r = 1.0
    elif typ == 17:
        r = smoothminf(a, b, c)
    elif typ == 18:
        r = -smoothminf(-a, -b, c)
    elif typ == 19:
        r = wp.floor(a + 0.5)
    elif typ == 20:
        r = wp.floor(a)
    elif typ == 21:
        r = wp.ceil(a)
    elif typ == 22:
        if a >= 0.0:
            r = wp.floor(a)
        else:
            r = wp.ceil(a)
    elif typ == 23:
        r = a - wp.floor(a)
    elif typ == 24:
        r = safe_modulo(a, b)
    elif typ == 25:
        r = safe_floored_modulo(a, b)
    elif typ == 26:
        r = wrapf(a, b, c)
    elif typ == 27:
        r = wp.floor(safe_divide(a, b)) * b
    elif typ == 28:
        r = pingpongf(a, b)
    elif typ == 29:
        r = wp.sin(a)
    elif typ == 30:
        r = wp.cos(a)
    elif typ == 31:
        r = wp.tan(a)
    elif typ == 32:
        r = safe_asinf(a)
    elif typ == 33:
        r = safe_acosf(a)
    elif typ == 34:
        r = wp.atan(a)
    elif typ == 35:
        r = compatible_atan2(a, b)
    elif typ == 36:
        r = wp.sinh(a)
    elif typ == 37:
        r = wp.cosh(a)
    elif typ == 38:
        r = wp.tanh(a)
    elif typ == 39:
        r = a * (M_PI_F / 180.0)
    elif typ == 40:
        r = a * (180.0 / M_PI_F)
    return r


@wp.kernel
def _mathe(a: wp.array(dtype=wp.float32), b: wp.array(dtype=wp.float32), c: wp.array(dtype=wp.float32), typ: int, klemme: int, aus: wp.array(dtype=wp.float32)):
    i = wp.tid()
    r = svm_math(typ, a[i], b[i], c[i])
    if klemme > 0:
        r = wp.clamp(r, 0.0, 1.0)             # `ClampNode` (MINMAX, 0…1) hinter dem Ergebnis, `MathNode::expand`
    aus[i] = r


@wp.func
def _komponenten(f: wp.vec3, g: wp.vec3, wahl: int) -> wp.vec3:
    """Hilfe für die einfachen Komponentenrechnungen der Vektor-Math-Knoten (siehe `svm_vector_math`)."""
    r = wp.vec3(0.0, 0.0, 0.0)
    for k in range(3):
        if wahl == 0:                                    # MINIMUM
            r[k] = wp.min(f[k], g[k])
        elif wahl == 1:                                  # MAXIMUM
            r[k] = wp.max(f[k], g[k])
        elif wahl == 2:                                  # ABSOLUTE
            r[k] = wp.abs(f[k])
        elif wahl == 3:                                  # FLOOR
            r[k] = wp.floor(f[k])
        elif wahl == 4:                                  # CEIL
            r[k] = wp.ceil(f[k])
        elif wahl == 5:                                  # FRACTION: a - floor(a)
            r[k] = f[k] - wp.floor(f[k])
        elif wahl == 6:                                  # ROUND: floor(a + 0.5)
            r[k] = wp.floor(f[k] + 0.5)
        elif wahl == 7:                                  # SINE
            r[k] = wp.sin(f[k])
        elif wahl == 8:                                  # COSINE
            r[k] = wp.cos(f[k])
        elif wahl == 9:                                  # TANGENT
            r[k] = wp.tan(f[k])
        elif wahl == 10:                                 # SIGN: compatible_sign
            r[k] = compatible_signf(f[k])
        elif wahl == 11:                                 # SNAP: floor(safe_divide(a, b)) * b
            r[k] = wp.floor(safe_divide(f[k], g[k])) * g[k]
    return r


@wp.kernel
def _vektor_mathe(a: wp.array(dtype=wp.vec3), b: wp.array(dtype=wp.vec3), c: wp.array(dtype=wp.vec3), skala: wp.array(dtype=wp.float32), typ: int,
                  vektor_aus: wp.array(dtype=wp.vec3), wert_aus: wp.array(dtype=wp.float32)):
    """`svm_vector_math` (math_util.h)."""
    i = wp.tid()
    x = a[i]
    y = b[i]
    z = c[i]
    v = wp.vec3(0.0, 0.0, 0.0)
    w = float(0.0)
    if typ == 0:
        v = x + y
    elif typ == 1:
        v = x - y
    elif typ == 2:
        v = wp.cw_mul(x, y)
    elif typ == 3:
        v = safe_divide3(x, y)
    elif typ == 4:
        v = wp.cw_mul(x, y) + z
    elif typ == 5:
        v = wp.cross(x, y)
    elif typ == 6:
        v = project3(x, y)
    elif typ == 7:
        v = reflect3(x, safe_normalize3(y))
    elif typ == 8:
        v = refract3(x, safe_normalize3(y), skala[i])
    elif typ == 9:
        v = faceforward3(x, y, z)
    elif typ == 10:
        w = wp.dot(x, y)
    elif typ == 11:
        w = wp.length(x - y)
    elif typ == 12:
        w = wp.length(x)
    elif typ == 13:
        v = x * skala[i]
    elif typ == 14:
        v = safe_normalize3(x)
    elif typ == 15:
        v = _komponenten(x, y, 2)
    elif typ == 16:
        v = safe_pow3(x, y)
    elif typ == 17:
        v = _komponenten(x, y, 10)
    elif typ == 18:
        v = _komponenten(x, y, 0)
    elif typ == 19:
        v = _komponenten(x, y, 1)
    elif typ == 20:
        v = _komponenten(x, y, 6)
    elif typ == 21:
        v = _komponenten(x, y, 3)
    elif typ == 22:
        v = _komponenten(x, y, 4)
    elif typ == 23:
        v = _komponenten(x, y, 5)
    elif typ == 24:
        v = safe_fmod3(x, y)
    elif typ == 25:
        v = wrap3(x, y, z)
    elif typ == 26:
        v = _komponenten(x, y, 11)
    elif typ == 27:
        v = _komponenten(x, y, 7)
    elif typ == 28:
        v = _komponenten(x, y, 8)
    elif typ == 29:
        v = _komponenten(x, y, 9)
    vektor_aus[i] = v
    wert_aus[i] = w


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
            wp.launch(_mathe, dim=ctx.n, inputs=[a, b, c, MATHE[self.eig['operation']], int(bool(self.eig.get('use_clamp'))), aus.daten], device=g)
            return {'Value': aus}
        a, b, c = (self._eingang_oder_null(graph, ctx, modus, n, 'v') for n in ('Vector', 'Vector_001', 'Vector_002'))
        skala = self._eingang_oder_null(graph, ctx, modus, 'Scale', 'f')
        vektor, wert = Hautwert.leer('v', ctx.n, g), Hautwert.leer('f', ctx.n, g)
        wp.launch(_vektor_mathe, dim=ctx.n, inputs=[a, b, c, skala, VEKTOR[self.eig['operation']], vektor.daten, wert.daten], device=g)
        return {'Vector': vektor, 'Value': wert}
