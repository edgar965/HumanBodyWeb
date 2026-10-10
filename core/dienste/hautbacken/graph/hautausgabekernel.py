# -*- coding: utf-8 -*-
"""Hautausgabekernel — vom ausgewerteten Graphen ins Bild der Kachel: Farbe (linear → sRGB), Rauheit, Normale in den Tangentenraum der Figur.

Quellen (Blender-Repo, gelesen 10.10.2026): `source/blender/render/intern/bake.cc` (`RE_bake_normal_world_to_tangent`, `normal_compress`: Tangentenraum der Figur aus den
geglätteten, NICHT normierten Punktnormalen und der interpolierten Tangente, `B = Vorzeichen · cross(N, T)`, die Basis wird INVERTIERT — nicht per Skalarprodukt —, Ergebnis
`n/2 + 0,5 + 1e-5`), `intern/cycles/util/color.h` (`color_linear_to_srgb`) und die Byte-Umrechnung von Blenders Bildpuffer (`x · 255 + 0,5`, geklemmt).
"""

import warp as wp

from ..hautfunktionen import color_linear_to_srgb

__all__ = ['holen', 'schreiben_farbe', 'schreiben_rauheit', 'schreiben_normale']


@wp.func
def _byte(x: float) -> wp.uint8:
    return wp.uint8(wp.clamp(x * 255.0 + 0.5, 0.0, 255.0))


@wp.kernel
def holen(idx: wp.array(dtype=wp.int32), face_flach: wp.array(dtype=wp.int32), hu_flach: wp.array(dtype=wp.float32), hv_flach: wp.array(dtype=wp.float32),
          face: wp.array(dtype=wp.int32), hu: wp.array(dtype=wp.float32), hv: wp.array(dtype=wp.float32)):
    """Die Treffer der Texel `idx` (flacher Index in die Kachel) für einen Stapel."""
    i = wp.tid()
    t = idx[i]
    face[i] = face_flach[t]
    hu[i] = hu_flach[t]
    hv[i] = hv_flach[t]


@wp.kernel
def schreiben_farbe(idx: wp.array(dtype=wp.int32), linear: wp.array(dtype=wp.vec3), aus: wp.array(dtype=wp.uint8)):
    """Linear → sRGB → Byte; Bildspeicher `(px·px·3)`."""
    i = wp.tid()
    t = idx[i]
    c = linear[i]
    for k in range(3):
        aus[t * 3 + k] = _byte(color_linear_to_srgb(c[k]))


@wp.kernel
def schreiben_rauheit(idx: wp.array(dtype=wp.int32), wert: wp.array(dtype=wp.float32), aus: wp.array(dtype=wp.uint8)):
    """Die Zahl als Grau (Non-Color, ohne Umrechnung) — Blender backt die Rauheit als Emission in ein Non-Color-Bild: R = G = B."""
    i = wp.tid()
    t = idx[i]
    b = _byte(wert[i])
    aus[t * 3] = b
    aus[t * 3 + 1] = b
    aus[t * 3 + 2] = b


@wp.kernel
def schreiben_normale(idx: wp.array(dtype=wp.int32), n_welt: wp.array(dtype=wp.vec3), f_ids: wp.array(dtype=wp.int32), f_bary: wp.array(dtype=wp.vec2),
                      f_tri: wp.array(dtype=wp.vec3i), f_nor: wp.array(dtype=wp.vec3), f_tang: wp.array(dtype=wp.vec4), aus: wp.array(dtype=wp.uint8)):
    """`RE_bake_normal_world_to_tangent` für ein Dreieck der Figur: Normale (geglättet, nicht normiert), Tangente (interpoliert, nicht normiert), Vorzeichen, Basis (T, B, N)
    invertieren, die Normale hineinrechnen, normieren, nach `n/2 + 0,5 + 1e-5` verdichten."""
    k = wp.tid()
    t = idx[k]
    tri = f_ids[t]
    j = f_tri[tri]
    w1 = f_bary[t][0]
    w2 = f_bary[t][1]
    w0 = 1.0 - w1 - w2
    nor = f_nor[j[0]] * w0 + f_nor[j[1]] * w1 + f_nor[j[2]] * w2
    t0 = f_tang[tri * 3]
    t1 = f_tang[tri * 3 + 1]
    t2 = f_tang[tri * 3 + 2]
    tang = wp.vec3(t0[0], t0[1], t0[2]) * w0 + wp.vec3(t1[0], t1[1], t1[2]) * w1 + wp.vec3(t2[0], t2[1], t2[2]) * w2
    vorz = float(1.0)
    if t0[3] * w0 + t1[3] * w1 + t2[3] * w2 < 0.0:
        vorz = -1.0
    bin_ = wp.cross(nor, tang) * vorz
    m = wp.mat33(tang[0], bin_[0], nor[0], tang[1], bin_[1], nor[1], tang[2], bin_[2], nor[2])
    x = wp.normalize(wp.inverse(m) * n_welt[k])
    for c in range(3):
        aus[t * 3 + c] = _byte(x[c] / 2.0 + 0.5 + 1.0e-5)
