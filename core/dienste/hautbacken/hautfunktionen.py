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


# ------------------------------------------------------------- util/color.h

@wp.func
def color_srgb_to_linear(c: float) -> float:
    """`color_srgb_to_linear` (color.h) — die GPU-Fassung ohne die SSE-Näherung `fastpow24`."""
    if c < 0.04045:
        if c < 0.0:
            return 0.0
        return c * (1.0 / 12.92)
    return wp.pow((c + 0.055) * (1.0 / 1.055), 2.4)


@wp.func
def color_linear_to_srgb(c: float) -> float:
    if c < 0.0031308:
        if c < 0.0:
            return 0.0
        return c * 12.92
    return 1.055 * wp.pow(c, 1.0 / 2.4) - 0.055


@wp.func
def rgb_to_hsv(rgb: wp.vec3) -> wp.vec3:
    cmax = wp.max(rgb[0], wp.max(rgb[1], rgb[2]))
    cmin = wp.min(rgb[0], wp.min(rgb[1], rgb[2]))
    cdelta = cmax - cmin
    v = cmax
    s = float(0.0)
    h = float(0.0)
    if cmax != 0.0:
        s = cdelta / cmax
    if s != 0.0:
        c0 = (cmax - rgb[0]) / cdelta
        c1 = (cmax - rgb[1]) / cdelta
        c2 = (cmax - rgb[2]) / cdelta
        if rgb[0] == cmax:
            h = c2 - c1
        elif rgb[1] == cmax:
            h = 2.0 + c0 - c2
        else:
            h = 4.0 + c1 - c0
        h = h / 6.0
        if h < 0.0:
            h = h + 1.0
    else:
        h = 0.0
    return wp.vec3(h, s, v)


@wp.func
def hsv_to_rgb(hsv: wp.vec3) -> wp.vec3:
    h = hsv[0]
    s = hsv[1]
    v = hsv[2]
    rgb = wp.vec3(v, v, v)
    if s != 0.0:
        if h == 1.0:
            h = 0.0
        h = h * 6.0
        i = wp.floor(h)
        f = h - i
        p = v * (1.0 - s)
        q = v * (1.0 - (s * f))
        t = v * (1.0 - (s * (1.0 - f)))
        if i == 0.0:
            rgb = wp.vec3(v, t, p)
        elif i == 1.0:
            rgb = wp.vec3(q, v, p)
        elif i == 2.0:
            rgb = wp.vec3(p, v, t)
        elif i == 3.0:
            rgb = wp.vec3(p, q, v)
        elif i == 4.0:
            rgb = wp.vec3(t, p, v)
        else:
            rgb = wp.vec3(v, p, q)
    return rgb


@wp.func
def rgb_to_hsl(rgb: wp.vec3) -> wp.vec3:
    cmax = wp.max(rgb[0], wp.max(rgb[1], rgb[2]))
    cmin = wp.min(rgb[0], wp.min(rgb[1], rgb[2]))
    l = wp.min(1.0, (cmax + cmin) / 2.0)
    h = float(0.0)
    s = float(0.0)
    if cmax == cmin:
        h = 0.0
        s = 0.0
    else:
        cdelta = cmax - cmin
        if l > 0.5:
            s = cdelta / (2.0 - cmax - cmin)
        else:
            s = cdelta / (cmax + cmin)
        if cmax == rgb[0]:
            if rgb[1] < rgb[2]:
                h = (rgb[1] - rgb[2]) / cdelta + 6.0
            else:
                h = (rgb[1] - rgb[2]) / cdelta + 0.0
        elif cmax == rgb[1]:
            h = (rgb[2] - rgb[0]) / cdelta + 2.0
        else:
            h = (rgb[0] - rgb[1]) / cdelta + 4.0
    h = h / 6.0
    return wp.vec3(h, s, l)


@wp.func
def hsl_to_rgb(hsl: wp.vec3) -> wp.vec3:
    h = hsl[0]
    s = hsl[1]
    l = hsl[2]
    nr = wp.abs(h * 6.0 - 3.0) - 1.0
    ng = 2.0 - wp.abs(h * 6.0 - 2.0)
    nb = 2.0 - wp.abs(h * 6.0 - 4.0)
    nr = wp.clamp(nr, 0.0, 1.0)
    nb = wp.clamp(nb, 0.0, 1.0)
    ng = wp.clamp(ng, 0.0, 1.0)
    chroma = (1.0 - wp.abs(2.0 * l - 1.0)) * s
    return wp.vec3((nr - 0.5) * chroma + l, (ng - 0.5) * chroma + l, (nb - 0.5) * chroma + l)


@wp.func
def saturate3(c: wp.vec3) -> wp.vec3:
    return wp.vec3(wp.clamp(c[0], 0.0, 1.0), wp.clamp(c[1], 0.0, 1.0), wp.clamp(c[2], 0.0, 1.0))
