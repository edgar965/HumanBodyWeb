# -*- coding: utf-8 -*-
"""Hautfunktionen — die kleinen Rechenfunktionen von Cycles als Warp-Funktionen (GPU), Zeile für Zeile aus dem Blender-Quelltext übernommen.

Quellen (Blender-Repo `github.com/blender/blender`, Zweig main, gelesen 10.10.2026; lokal unter `ProjektTemp/_wegwerf/cycles_quelle/`):
`intern/cycles/util/math_base.h` (u_math_base.h), `util/math_float3.h` (u_math_float3.h), `util/color.h` (u_color.h), `kernel/svm/color_util.h` (color_util.h),
`kernel/svm/map_range.h`, `kernel/svm/math_util.h`. Jede Funktion nennt ihr Vorbild. Eine Abweichung von Cycles ist hier ein Fehler — nichts ist „sinngemäß" nachgebaut.
Warp-Funktionen müssen auf Modulebene stehen; die Kernel der Knoten (`knoten/`) rufen sie auf.
"""

import warp as wp

__all__ = []

PI_F = 3.1415926535897932


# ------------------------------------------------------------ util/math_base.h

@wp.func
def saturatef(a: float) -> float:
    """`saturatef`: clamp(a, 0, 1) (CPU-Fassung)."""
    return wp.clamp(a, 0.0, 1.0)


@wp.func
def fractf(x: float) -> float:
    """`fractf`: x - floorf(x)."""
    return x - wp.floor(x)


@wp.func
def safe_divide(a: float, b: float) -> float:
    """`safe_divide`: (b != 0) ? a / b : 0."""
    if b != 0.0:
        return a / b
    return 0.0


@wp.func
def safe_sqrtf(f: float) -> float:
    return wp.sqrt(wp.max(f, 0.0))


@wp.func
def inversesqrtf(f: float) -> float:
    if f > 0.0:
        return 1.0 / wp.sqrt(f)
    return 0.0


@wp.func
def safe_asinf(a: float) -> float:
    return wp.asin(wp.clamp(a, -1.0, 1.0))


@wp.func
def safe_acosf(a: float) -> float:
    return wp.acos(wp.clamp(a, -1.0, 1.0))


@wp.func
def compatible_powf(x: float, y: float) -> float:
    """`compatible_powf` in der GPU-Fassung (`__KERNEL_GPU__`): x^0 = 1, 0^y = 0, negatives x über |x| mit dem Vorzeichen von y gerade/ungerade."""
    if y == 0.0:
        return 1.0
    if x == 0.0:
        return 0.0
    if x < 0.0:
        if wp.mod(-y, 2.0) == 0.0:
            return wp.pow(-x, y)
        return -wp.pow(-x, y)
    return wp.pow(x, y)


@wp.func
def safe_powf(a: float, b: float) -> float:
    if a < 0.0 and b != float(int(b)):
        return 0.0
    return compatible_powf(a, b)


@wp.func
def safe_logf(a: float, b: float) -> float:
    if a <= 0.0 or b <= 0.0:
        return 0.0
    return safe_divide(wp.log(a), wp.log(b))


@wp.func
def safe_modulo(a: float, b: float) -> float:
    if b != 0.0:
        return wp.mod(a, b)
    return 0.0


@wp.func
def safe_floored_modulo(a: float, b: float) -> float:
    if b != 0.0:
        return a - wp.floor(a / b) * b
    return 0.0


@wp.func
def wrapf(value: float, maxv: float, minv: float) -> float:
    rng = maxv - minv
    if rng != 0.0:
        return value - (rng * wp.floor((value - minv) / rng))
    return minv


@wp.func
def pingpongf(a: float, b: float) -> float:
    if b != 0.0:
        return wp.abs(fractf((a - b) / (b * 2.0)) * b * 2.0 - b)
    return 0.0


@wp.func
def smoothminf(a: float, b: float, k: float) -> float:
    if k != 0.0:
        h = wp.max(k - wp.abs(a - b), 0.0) / k
        return wp.min(a, b) - h * h * h * k * (1.0 / 6.0)
    return wp.min(a, b)


@wp.func
def signf(f: float) -> float:
    if f < 0.0:
        return -1.0
    return 1.0


@wp.func
def compatible_signf(f: float) -> float:
    if f == 0.0:
        return 0.0
    return signf(f)


@wp.func
def compatible_atan2(y: float, x: float) -> float:
    if x == 0.0 and y == 0.0:
        return 0.0
    return wp.atan2(y, x)


@wp.func
def smoothstep_cycles(edge0: float, edge1: float, x: float) -> float:
    """`smoothstep` (math_base.h) — nicht das von OpenGL: unterhalb edge0 → 0, ab edge1 → 1."""
    if x < edge0:
        return 0.0
    if x >= edge1:
        return 1.0
    t = (x - edge0) / (edge1 - edge0)
    return (3.0 - 2.0 * t) * (t * t)


@wp.func
def smootherstep(edge0: float, edge1: float, x: float) -> float:
    """`smootherstep` (map_range.h)."""
    xx = wp.clamp(safe_divide(x - edge0, edge1 - edge0), 0.0, 1.0)
    return xx * xx * xx * (xx * (xx * 6.0 - 15.0) + 10.0)


# --------------------------------------------------------- util/math_float3.h

@wp.func
def safe_normalize3(a: wp.vec3) -> wp.vec3:
    """`safe_normalize(float3)`: t = len(a); (t != 0) ? a * (1/t) : a."""
    t = wp.length(a)
    if t != 0.0:
        return a * (1.0 / t)
    return a


@wp.func
def is_zero3(a: wp.vec3) -> bool:
    return a[0] == 0.0 and a[1] == 0.0 and a[2] == 0.0


@wp.func
def average3(a: wp.vec3) -> float:
    return (a[0] + a[1] + a[2]) * (1.0 / 3.0)


@wp.func
def safe_divide3(a: wp.vec3, b: wp.vec3) -> wp.vec3:
    return wp.vec3(safe_divide(a[0], b[0]), safe_divide(a[1], b[1]), safe_divide(a[2], b[2]))


@wp.func
def safe_pow3(a: wp.vec3, b: wp.vec3) -> wp.vec3:
    return wp.vec3(safe_powf(a[0], b[0]), safe_powf(a[1], b[1]), safe_powf(a[2], b[2]))


@wp.func
def project3(v: wp.vec3, v_proj: wp.vec3) -> wp.vec3:
    len_squared = wp.dot(v_proj, v_proj)
    if len_squared != 0.0:
        return (wp.dot(v, v_proj) / len_squared) * v_proj
    return wp.vec3(0.0, 0.0, 0.0)


@wp.func
def reflect3(incident: wp.vec3, unit_normal: wp.vec3) -> wp.vec3:
    return incident - 2.0 * unit_normal * wp.dot(incident, unit_normal)


@wp.func
def refract3(incident: wp.vec3, normal: wp.vec3, eta: float) -> wp.vec3:
    k = 1.0 - eta * eta * (1.0 - wp.dot(normal, incident) * wp.dot(normal, incident))
    if k < 0.0:
        return wp.vec3(0.0, 0.0, 0.0)
    return eta * incident - (eta * wp.dot(normal, incident) + wp.sqrt(k)) * normal


@wp.func
def faceforward3(vector: wp.vec3, incident: wp.vec3, reference: wp.vec3) -> wp.vec3:
    if wp.dot(reference, incident) < 0.0:
        return vector
    return -vector


@wp.func
def safe_floored_fmod3(a: wp.vec3, b: wp.vec3) -> wp.vec3:
    """`safe_floored_fmod(float3)`: je Komponente b == 0 → 0, sonst a - floor(a / b) * b."""
    r = wp.vec3(0.0, 0.0, 0.0)
    for i in range(3):
        if b[i] != 0.0:
            r[i] = a[i] - wp.floor(a[i] / b[i]) * b[i]
    return r


@wp.func
def wrap3(value: wp.vec3, maxv: wp.vec3, minv: wp.vec3) -> wp.vec3:
    return safe_floored_fmod3(value - minv, maxv - minv) + minv


@wp.func
def safe_fmod3(a: wp.vec3, b: wp.vec3) -> wp.vec3:
    r = wp.vec3(0.0, 0.0, 0.0)
    for i in range(3):
        if b[i] != 0.0:
            r[i] = wp.mod(a[i], b[i])
    return r


@wp.func
def make_orthonormals_a(n: wp.vec3) -> wp.vec3:
    """`make_orthonormals` (math_float3.h), erster Vektor `a`: (1,1,1) × N, bei N.x == N.y == N.z (−1,1,1) × N; normalisiert."""
    a = wp.vec3(0.0, 0.0, 0.0)
    if n[0] != n[1] or n[0] != n[2]:
        a = wp.vec3(n[2] - n[1], n[0] - n[2], n[1] - n[0])
    else:
        a = wp.vec3(n[2] - n[1], n[0] + n[2], -n[1] - n[0])
    return wp.normalize(a)
