# -*- coding: utf-8 -*-
"""Hautfarbfunktionen — die Farbfunktionen von Cycles als Warp-Funktionen (GPU), Zeile für Zeile aus dem Blender-Quelltext übernommen: sRGB ↔ linear (`util/color.h`), HSV und HSL
(`kernel/svm/color_util.h`). Siehe `hautfunktionen.py` für die Quellen und die Regel (eine Abweichung von Cycles ist ein Fehler)."""

import warp as wp

__all__ = []


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

