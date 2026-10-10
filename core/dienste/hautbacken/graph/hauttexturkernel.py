# -*- coding: utf-8 -*-
"""Hauttexturkernel — das Abtasten eines Bildes wie Cycles: Wiederholen/Erweitern/Klemmen/Spiegeln, nächster Nachbar, bilinear und kubisch (B-Spline).

Übernommen aus `intern/cycles/kernel/util/image.h` (`ImageInterpolator::interp_closest/interp_linear/interp_cubic`, `wrap_*`, `frac`, `SET_CUBIC_SPLINE_WEIGHTS`) und
`kernel/svm/image.h` (`svm_image_texture`: Alpha ent-assoziieren, sRGB nach der Interpolation umrechnen); Blender-Quelltext vom 10.10.2026. Das Bild liegt wie in Cycles
unten-zuerst im Speicher (Zeile 0 = unterer Bildrand, v = 0) als RGBA-Bytes. Nicht übernommen: Mip-Stufen/Texturcache (dort rechnet Cycles mit Ableitungen; ohne
Cache, wie beim Backen mit der Vorgabe, tastet es immer die volle Auflösung ab).
"""

import warp as wp

from ..hautfunktionen import color_srgb_to_linear

__all__ = ['abtasten']

#: `INTERPOLATION_*` und `EXTENSION_*` (types_image.h): Blender-Namen siehe `Hauttextur`.
CLOSEST = 1
LINEAR = 0
CUBIC = 2
REPEAT = 0
EXTEND = 1
CLIP = 2
MIRROR = 3


@wp.func
def _frac_i(x: float) -> int:
    """`frac`: der ganze Teil — (int)x, bei negativem x um 1 kleiner (`ImageInterpolator::frac`)."""
    r = int(x)
    if x < 0.0:
        r = r - 1
    return r


@wp.func
def _wrap_periodic(x_in: int, breite: int) -> int:
    x = x_in % breite
    if x < 0:
        x = x + breite
    return x


@wp.func
def _wrap_mirror(x: int, breite: int) -> int:
    xx = x
    if x < 0:
        xx = x + 1
    m = wp.abs(xx) % (2 * breite)
    if m >= breite:
        return 2 * breite - m - 1
    return m


@wp.func
def _lies(daten: wp.array(dtype=wp.uint8), x: int, y: int, breite: int, hoehe: int) -> wp.vec4:
    """`read_clip`: außerhalb des Bildes transparentes Schwarz."""
    if x < 0 or x >= breite or y < 0 or y >= hoehe:
        return wp.vec4(0.0, 0.0, 0.0, 0.0)
    k = (y * breite + x) * 4
    s = 1.0 / 255.0
    return wp.vec4(float(daten[k]) * s, float(daten[k + 1]) * s, float(daten[k + 2]) * s, float(daten[k + 3]) * s)


@wp.func
def _gewicht(t: float, k: int) -> float:
    """`SET_CUBIC_SPLINE_WEIGHTS`: das k-te der vier Gewichte."""
    if k == 0:
        return (((-1.0 / 6.0) * t + 0.5) * t - 0.5) * t + (1.0 / 6.0)
    if k == 1:
        return ((0.5 * t - 1.0) * t) * t + (2.0 / 3.0)
    if k == 2:
        return ((-0.5 * t + 0.5) * t + 0.5) * t + (1.0 / 6.0)
    return (1.0 / 6.0) * t * t * t


@wp.func
def _naechster(daten: wp.array(dtype=wp.uint8), breite: int, hoehe: int, x: float, y: float, erweiterung: int) -> wp.vec4:
    ix = _frac_i(x)
    iy = _frac_i(y)
    if erweiterung == 0:
        ix = _wrap_periodic(ix, breite)
        iy = _wrap_periodic(iy, hoehe)
    elif erweiterung == 2:
        if ix < 0 or ix >= breite or iy < 0 or iy >= hoehe:
            return wp.vec4(0.0, 0.0, 0.0, 0.0)
    elif erweiterung == 1:
        ix = wp.clamp(ix, 0, breite - 1)
        iy = wp.clamp(iy, 0, hoehe - 1)
    else:
        ix = _wrap_mirror(ix, breite)
        iy = _wrap_mirror(iy, hoehe)
    return _lies(daten, ix, iy, breite, hoehe)


@wp.func
def _linear(daten: wp.array(dtype=wp.uint8), breite: int, hoehe: int, x: float, y: float, erweiterung: int) -> wp.vec4:
    ix = _frac_i(x - 0.5)
    iy = _frac_i(y - 0.5)
    tx = (x - 0.5) - float(ix)
    ty = (y - 0.5) - float(iy)
    nix = ix + 1
    niy = iy + 1
    if erweiterung == 0:
        ix = _wrap_periodic(ix, breite)
        nix = _wrap_periodic(ix + 1, breite)
        iy = _wrap_periodic(iy, hoehe)
        niy = _wrap_periodic(iy + 1, hoehe)
    elif erweiterung == 2:
        if ix < -1 or ix >= breite or iy < -1 or iy >= hoehe:
            return wp.vec4(0.0, 0.0, 0.0, 0.0)
    elif erweiterung == 1:
        nix = wp.clamp(ix + 1, 0, breite - 1)
        ix = wp.clamp(ix, 0, breite - 1)
        niy = wp.clamp(iy + 1, 0, hoehe - 1)
        iy = wp.clamp(iy, 0, hoehe - 1)
    else:
        nix = _wrap_mirror(ix + 1, breite)
        ix = _wrap_mirror(ix, breite)
        niy = _wrap_mirror(iy + 1, hoehe)
        iy = _wrap_mirror(iy, hoehe)
    return (1.0 - ty) * (1.0 - tx) * _lies(daten, ix, iy, breite, hoehe) + (1.0 - ty) * tx * _lies(daten, nix, iy, breite, hoehe) + \
        ty * (1.0 - tx) * _lies(daten, ix, niy, breite, hoehe) + ty * tx * _lies(daten, nix, niy, breite, hoehe)


@wp.func
def _kubisch(daten: wp.array(dtype=wp.uint8), breite: int, hoehe: int, x: float, y: float, erweiterung: int) -> wp.vec4:
    ix = _frac_i(x - 0.5)
    iy = _frac_i(y - 0.5)
    tx = (x - 0.5) - float(ix)
    ty = (y - 0.5) - float(iy)
    pix = ix - 1
    nix = ix + 1
    nnix = ix + 2
    piy = iy - 1
    niy = iy + 1
    nniy = iy + 2
    if erweiterung == 0:
        ix = _wrap_periodic(ix, breite)
        pix = _wrap_periodic(ix - 1, breite)
        nix = _wrap_periodic(ix + 1, breite)
        nnix = _wrap_periodic(ix + 2, breite)
        iy = _wrap_periodic(iy, hoehe)
        piy = _wrap_periodic(iy - 1, hoehe)
        niy = _wrap_periodic(iy + 1, hoehe)
        nniy = _wrap_periodic(iy + 2, hoehe)
    elif erweiterung == 2:
        if ix < -2 or ix > breite or iy < -2 or iy > hoehe:
            return wp.vec4(0.0, 0.0, 0.0, 0.0)
    elif erweiterung == 1:
        pix = wp.clamp(ix - 1, 0, breite - 1)
        nix = wp.clamp(ix + 1, 0, breite - 1)
        nnix = wp.clamp(ix + 2, 0, breite - 1)
        ix = wp.clamp(ix, 0, breite - 1)
        piy = wp.clamp(iy - 1, 0, hoehe - 1)
        niy = wp.clamp(iy + 1, 0, hoehe - 1)
        nniy = wp.clamp(iy + 2, 0, hoehe - 1)
        iy = wp.clamp(iy, 0, hoehe - 1)
    else:
        pix = _wrap_mirror(ix - 1, breite)
        nix = _wrap_mirror(ix + 1, breite)
        nnix = _wrap_mirror(ix + 2, breite)
        ix = _wrap_mirror(ix, breite)
        piy = _wrap_mirror(iy - 1, hoehe)
        niy = _wrap_mirror(iy + 1, hoehe)
        nniy = _wrap_mirror(iy + 2, hoehe)
        iy = _wrap_mirror(iy, hoehe)
    s = wp.vec4(0.0, 0.0, 0.0, 0.0)
    for j in range(4):
        yy = piy
        if j == 1:
            yy = iy
        elif j == 2:
            yy = niy
        elif j == 3:
            yy = nniy
        zeile = _gewicht(ty, j) * (_gewicht(tx, 0) * _lies(daten, pix, yy, breite, hoehe) + _gewicht(tx, 1) * _lies(daten, ix, yy, breite, hoehe) +
                                   _gewicht(tx, 2) * _lies(daten, nix, yy, breite, hoehe) + _gewicht(tx, 3) * _lies(daten, nnix, yy, breite, hoehe))
        s = s + zeile
    return s


@wp.kernel
def abtasten(daten: wp.array(dtype=wp.uint8), breite: int, hoehe: int, koordinate: wp.array(dtype=wp.vec3), interpolation: int, erweiterung: int, srgb: int,
             entassoziieren: int, aus: wp.array(dtype=wp.vec4)):
    """`svm_node_tex_image` (Projektion FLAT) + `svm_image_texture`: Pixelkoordinate = (u · Breite, v · Höhe), dann je nach Einstellung abtasten, bei Bedarf das Alpha
    entfernen (r /= alpha, nur wenn alpha ≠ 0 und ≠ 1) und sRGB nach der Interpolation in Linear umrechnen (nur RGB)."""
    i = wp.tid()
    x = koordinate[i][0] * float(breite)
    y = koordinate[i][1] * float(hoehe)
    r = wp.vec4(0.0, 0.0, 0.0, 0.0)
    if interpolation == 1:
        r = _naechster(daten, breite, hoehe, x, y, erweiterung)
    elif interpolation == 0:
        r = _linear(daten, breite, hoehe, x, y, erweiterung)
    else:
        r = _kubisch(daten, breite, hoehe, x, y, erweiterung)
    alpha = r[3]
    if entassoziieren > 0 and alpha != 1.0 and alpha != 0.0:
        r = r / alpha
        r = wp.vec4(r[0], r[1], r[2], alpha)
    if srgb > 0:
        r = wp.vec4(color_srgb_to_linear(r[0]), color_srgb_to_linear(r[1]), color_srgb_to_linear(r[2]), r[3])
    aus[i] = r
