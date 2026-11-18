# -*- coding: utf-8 -*-
u"""Hautkartewarphilfe — gemeinsame Warp-Bausteine der Haut-Maske auf der Karte (18.11.2026, Edgar: „Hautverdeckung auf GPU, alles auf GPU!“).

Die Kerne bilden `gemeinsam/hautmaske*.js` nach: JS rechnet in double ohne FMA — hier `fuse_fp: False` (Warp 1.17, Moduloption) und dieselbe Reihenfolge
der Rechenschritte. `hypot3` ist V8s `Math.hypot` (`src/builtins/math.tq`: größter Betrag, Quotienten mit Kahan summiert, Wurzel mal Größtem).
Das Gitter (`Hautkartegitter`) ist das von `Hautmaskegeometrie.punktgitter`: Zelle `floor(p / h)`, Schlüssel `zelle(i, j, k)` wie dort, je Zelle die
Punkte aufsteigend — also dieselbe Reihenfolge, in der JS sie ansieht.
"""
import sys

import warp as wp

wp.config.quiet = True
wp.init()
wp.set_module_options({'fuse_fp': False, 'enable_backward': False})


@wp.func
def zellschluessel(i: wp.int64, j: wp.int64, k: wp.int64) -> wp.int64:
    return ((i + wp.int64(1024)) * wp.int64(2048) + (j + wp.int64(1024))) * wp.int64(2048) + (k + wp.int64(1024))


@wp.func
def zellnummer(x: wp.float64, h: wp.float64) -> wp.int64:
    return wp.int64(wp.floor(x / h))


@wp.func
def untergrenze(schl: wp.array(dtype=wp.int64), wert: wp.int64) -> int:
    lo = int(0)
    hi = schl.shape[0]
    while lo < hi:
        mitte = (lo + hi) // 2
        if schl[mitte] < wert:
            lo = mitte + 1
        else:
            hi = mitte
    return lo


@wp.func
def hypot3(x: wp.float64, y: wp.float64, z: wp.float64) -> wp.float64:
    ax = wp.abs(x)
    ay = wp.abs(y)
    az = wp.abs(z)
    m = ax
    if ay > m:
        m = ay
    if az > m:
        m = az
    if m == wp.float64(0.0):
        return wp.float64(0.0)
    s = wp.float64(0.0)
    c = wp.float64(0.0)
    n = ax / m
    summand = n * n - c
    vorl = s + summand
    c = (vorl - s) - summand
    s = vorl
    n = ay / m
    summand = n * n - c
    vorl = s + summand
    c = (vorl - s) - summand
    s = vorl
    n = az / m
    summand = n * n - c
    vorl = s + summand
    c = (vorl - s) - summand
    s = vorl
    return wp.sqrt(s) * m


@wp.func
def strahl_dreieck(P: wp.array2d(dtype=wp.float64), a: int, b: int, c: int, px: wp.float64, py: wp.float64, pz: wp.float64,
                   rx: wp.float64, ry: wp.float64, rz: wp.float64) -> wp.float64:
    # `Hautmaskegeometrie.strahlDreieck` (Möller–Trumbore, beidseitig); kein Treffer: NaN
    ax = P[a, 0]
    ay = P[a, 1]
    az = P[a, 2]
    e1x = P[b, 0] - ax
    e1y = P[b, 1] - ay
    e1z = P[b, 2] - az
    e2x = P[c, 0] - ax
    e2y = P[c, 1] - ay
    e2z = P[c, 2] - az
    hx = ry * e2z - rz * e2y
    hy = rz * e2x - rx * e2z
    hz = rx * e2y - ry * e2x
    det = e1x * hx + e1y * hy + e1z * hz
    keins = wp.float64(wp.nan)
    if det > wp.float64(-1e-12) and det < wp.float64(1e-12):
        return keins
    f = wp.float64(1.0) / det
    sx = px - ax
    sy = py - ay
    sz = pz - az
    u = f * (sx * hx + sy * hy + sz * hz)
    if u < wp.float64(0.0) or u > wp.float64(1.0):
        return keins
    qx = sy * e1z - sz * e1y
    qy = sz * e1x - sx * e1z
    qz = sx * e1y - sy * e1x
    v = f * (rx * qx + ry * qy + rz * qz)
    if v < wp.float64(0.0) or u + v > wp.float64(1.0):
        return keins
    return f * (e2x * qx + e2y * qy + e2z * qz)


@wp.func
def naechster(P: wp.array2d(dtype=wp.float64), schl: wp.array(dtype=wp.int64), folge: wp.array(dtype=wp.int64), h: wp.float64,
              px: wp.float64, py: wp.float64, pz: wp.float64) -> wp.vec2d:
    # `Hautmaskegeometrie.naechsterPunkt`: nächster Punkt in den 27 Zellen — (j, d2), j = -1 ohne Punkt
    ci = zellnummer(px, h)
    cj = zellnummer(py, h)
    ck = zellnummer(pz, h)
    best = wp.float64(wp.inf)
    bj = wp.float64(-1.0)
    for a in range(-1, 2):
        for b in range(-1, 2):
            for c in range(-1, 2):
                s = zellschluessel(ci + wp.int64(a), cj + wp.int64(b), ck + wp.int64(c))
                p = untergrenze(schl, s)
                while p < schl.shape[0] and schl[p] == s:
                    j = int(folge[p])
                    dx = P[j, 0] - px
                    dy = P[j, 1] - py
                    dz = P[j, 2] - pz
                    d2 = dx * dx + dy * dy + dz * dz
                    if d2 < best:
                        best = d2
                        bj = wp.float64(j)
                    p = p + 1
    return wp.vec2d(bj, best)


wp.load_module(sys.modules[__name__], device='cuda')
