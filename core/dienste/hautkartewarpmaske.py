# -*- coding: utf-8 -*-
u"""Hautkartewarpmaske — die Kerne von `Hautmaske` auf der Karte (18.11.2026, `Hautkartemaske`): je Körperpunkt ein Faden, dieselben Schleifen wie JS.

`locker`: `Hautmaske.lockereRandpunkte` (je Randpunkt des Stoffs). `stueck`: `Hautmaske._einStueck` — nächster Stoffpunkt in den 27 Zellen, dann die Dreiecke
um ihn (zwei Nachbarringe, nur erlaubte), Strahl entlang der Normale, bei starren Stücken der Abstandstest. `ersatz`: `Hautmaskeersatz.maskieren`.
`durch`: `Hautdurchsicht.stueck`. Jeder Faden schreibt nur seinen Punkt; die Stücke laufen nacheinander wie in JS.
"""
import sys

import warp as wp

from .hautkartewarphilfe import naechster, strahl_dreieck, untergrenze, zellnummer, zellschluessel

wp.set_module_options({'fuse_fp': False, 'enable_backward': False})


@wp.func
def punkt_dreieck2(P: wp.array2d(dtype=wp.float64), a: int, b: int, c: int, px: wp.float64, py: wp.float64, pz: wp.float64) -> wp.float64:
    # `Hautmaskegeometrie.punktDreieckAbstand2` (Ericson)
    ax = P[a, 0]
    ay = P[a, 1]
    az = P[a, 2]
    bx = P[b, 0]
    by = P[b, 1]
    bz = P[b, 2]
    cx = P[c, 0]
    cy = P[c, 1]
    cz = P[c, 2]
    abx = bx - ax
    aby = by - ay
    abz = bz - az
    acx = cx - ax
    acy = cy - ay
    acz = cz - az
    apx = px - ax
    apy = py - ay
    apz = pz - az
    d1 = abx * apx + aby * apy + abz * apz
    d2 = acx * apx + acy * apy + acz * apz
    null = wp.float64(0.0)
    if d1 <= null and d2 <= null:
        return apx * apx + apy * apy + apz * apz
    bpx = px - bx
    bpy = py - by
    bpz = pz - bz
    d3 = abx * bpx + aby * bpy + abz * bpz
    d4 = acx * bpx + acy * bpy + acz * bpz
    if d3 >= null and d4 <= d3:
        return bpx * bpx + bpy * bpy + bpz * bpz
    vc = d1 * d4 - d3 * d2
    if vc <= null and d1 >= null and d3 <= null:
        t = d1 / (d1 - d3)
        qx = ax + t * abx - px
        qy = ay + t * aby - py
        qz = az + t * abz - pz
        return qx * qx + qy * qy + qz * qz
    cpx = px - cx
    cpy = py - cy
    cpz = pz - cz
    d5 = abx * cpx + aby * cpy + abz * cpz
    d6 = acx * cpx + acy * cpy + acz * cpz
    if d6 >= null and d5 <= d6:
        return cpx * cpx + cpy * cpy + cpz * cpz
    vb = d5 * d2 - d1 * d6
    if vb <= null and d2 >= null and d6 <= null:
        t = d2 / (d2 - d6)
        qx = ax + t * acx - px
        qy = ay + t * acy - py
        qz = az + t * acz - pz
        return qx * qx + qy * qy + qz * qz
    va = d3 * d6 - d5 * d4
    if va <= null and (d4 - d3) >= null and (d5 - d6) >= null:
        t = (d4 - d3) / ((d4 - d3) + (d5 - d6))
        qx = bx + t * (cx - bx) - px
        qy = by + t * (cy - by) - py
        qz = bz + t * (cz - bz) - pz
        return qx * qx + qy * qy + qz * qz
    nenner = wp.float64(1.0) / (va + vb + vc)
    v = vb * nenner
    w = vc * nenner
    qx = ax + abx * v + acx * w - px
    qy = ay + aby * v + acy * w - py
    qz = az + abz * v + acz * w - pz
    return qx * qx + qy * qy + qz * qz


@wp.func
def in_huelle(px: wp.float64, py: wp.float64, pz: wp.float64, hl: wp.array(dtype=wp.float64)) -> bool:
    return not (px < hl[0] or px > hl[3] or py < hl[1] or py > hl[4] or pz < hl[2] or pz > hl[5])


@wp.func
def pruefe(S: wp.array2d(dtype=wp.float64), ST: wp.array2d(dtype=wp.int64), k: int, px: wp.float64, py: wp.float64, pz: wp.float64, nx: wp.float64,
           ny: wp.float64, nz: wp.float64, tiefe: wp.float64, abstand: wp.float64, nahe: wp.float64, n2: wp.float64) -> wp.vec2d:
    # (Treffer 1/0, Abstand² für den Abstandstest — inf ohne)
    a = int(ST[k, 0])
    b = int(ST[k, 1])
    c = int(ST[k, 2])
    t = strahl_dreieck(S, a, b, c, px, py, pz, nx, ny, nz)
    if not wp.isnan(t) and t >= -tiefe and t <= abstand:
        return wp.vec2d(wp.float64(1.0), n2)
    if nahe > wp.float64(0.0):
        d2 = punkt_dreieck2(S, a, b, c, px, py, pz)
        if d2 < n2:
            n2 = d2
    return wp.vec2d(wp.float64(0.0), n2)


@wp.kernel
def locker(S: wp.array2d(dtype=wp.float64), rand: wp.array(dtype=wp.int64), K: wp.array2d(dtype=wp.float64), N: wp.array2d(dtype=wp.float64),
           kschl: wp.array(dtype=wp.int64), kfolge: wp.array(dtype=wp.int64), h: wp.float64, eng: wp.float64, aus: wp.array(dtype=wp.uint8)):
    v = int(rand[wp.tid()])
    qx = S[v, 0]
    qy = S[v, 1]
    qz = S[v, 2]
    nah = naechster(K, kschl, kfolge, h, qx, qy, qz)
    if nah[0] < wp.float64(0.0):
        aus[v] = wp.uint8(1)
        return
    i = int(nah[0])
    d = (qx - K[i, 0]) * N[i, 0] + (qy - K[i, 1]) * N[i, 1] + (qz - K[i, 2]) * N[i, 2]
    if wp.abs(d) > eng:
        aus[v] = wp.uint8(1)


@wp.kernel
def stueck(K: wp.array2d(dtype=wp.float64), N: wp.array2d(dtype=wp.float64), S: wp.array2d(dtype=wp.float64), ST: wp.array2d(dtype=wp.int64),
           sschl: wp.array(dtype=wp.int64), sfolge: wp.array(dtype=wp.int64), h: wp.float64, hl: wp.array(dtype=wp.float64), grenze2: wp.float64,
           tiefe: wp.float64, abstand: wp.float64, nahe: wp.float64, nach_a: wp.array(dtype=wp.int64), nach_z: wp.array(dtype=wp.int64),
           inz_a: wp.array(dtype=wp.int64), inz_z: wp.array(dtype=wp.int64), wert: wp.float64, maske: wp.array(dtype=wp.uint8),
           nachgeben: wp.array(dtype=wp.float32)):
    i = wp.tid()
    if maske[i] != wp.uint8(0) and not (wert > wp.float64(nachgeben[i])):
        return
    px = K[i, 0]
    py = K[i, 1]
    pz = K[i, 2]
    if not in_huelle(px, py, pz, hl):
        return
    nah = naechster(S, sschl, sfolge, h, px, py, pz)
    if nah[0] < wp.float64(0.0) or nah[1] > grenze2:
        return
    j = int(nah[0])
    nx = N[i, 0]
    ny = N[i, 1]
    nz = N[i, 2]
    n2 = wp.float64(wp.inf)
    hit = wp.float64(0.0)
    # Die Dreiecke um j: an j, an seinen Nachbarn w und an deren Nachbarn x (Doppelte schaden nicht: Treffer ODER, Abstand Minimum)
    e = int(inz_a[j])
    while e < int(inz_a[j + 1]) and hit == wp.float64(0.0):
        r = pruefe(S, ST, int(inz_z[e]), px, py, pz, nx, ny, nz, tiefe, abstand, nahe, n2)
        hit = r[0]
        n2 = r[1]
        e = e + 1
    m = int(nach_a[j])
    while m < int(nach_a[j + 1]) and hit == wp.float64(0.0):
        w = int(nach_z[m])
        e = int(inz_a[w])
        while e < int(inz_a[w + 1]) and hit == wp.float64(0.0):
            r = pruefe(S, ST, int(inz_z[e]), px, py, pz, nx, ny, nz, tiefe, abstand, nahe, n2)
            hit = r[0]
            n2 = r[1]
            e = e + 1
        o = int(nach_a[w])
        while o < int(nach_a[w + 1]) and hit == wp.float64(0.0):
            x = int(nach_z[o])
            e = int(inz_a[x])
            while e < int(inz_a[x + 1]) and hit == wp.float64(0.0):
                r = pruefe(S, ST, int(inz_z[e]), px, py, pz, nx, ny, nz, tiefe, abstand, nahe, n2)
                hit = r[0]
                n2 = r[1]
                e = e + 1
            o = o + 1
        m = m + 1
    if hit == wp.float64(0.0) and n2 <= nahe * nahe:
        hit = wp.float64(1.0)
    if hit != wp.float64(0.0):
        maske[i] = wp.uint8(1)
        if wert > wp.float64(nachgeben[i]):
            nachgeben[i] = wp.float32(wert)


@wp.func
def hoechster(S: wp.array2d(dtype=wp.float64), sschl: wp.array(dtype=wp.int64), sfolge: wp.array(dtype=wp.int64), h: wp.float64, px: wp.float64,
              py: wp.float64, pz: wp.float64, nx: wp.float64, ny: wp.float64, nz: wp.float64, abstand: wp.float64, tiefe: wp.float64,
              r2: wp.float64) -> wp.vec2d:
    # `Hautmaskeersatz._hoechster`: (größte Höhe t im Zylinder, Nummer des Stückpunkts) — −inf / −1 ohne
    ci = zellnummer(px, h)
    cj = zellnummer(py, h)
    ck = zellnummer(pz, h)
    best = wp.float64(-wp.inf)
    tj = wp.float64(-1.0)
    for a in range(-1, 2):
        for b in range(-1, 2):
            for c in range(-1, 2):
                s = zellschluessel(ci + wp.int64(a), cj + wp.int64(b), ck + wp.int64(c))
                p = untergrenze(sschl, s)
                while p < sschl.shape[0] and sschl[p] == s:
                    j = int(sfolge[p])
                    vx = S[j, 0] - px
                    vy = S[j, 1] - py
                    vz = S[j, 2] - pz
                    t = vx * nx + vy * ny + vz * nz
                    if t >= -tiefe and t <= abstand:
                        if vx * vx + vy * vy + vz * vz - t * t <= r2 and t > best:
                            best = t
                            tj = wp.float64(j)
                    p = p + 1
    return wp.vec2d(best, tj)


@wp.kernel
def ersatz(K: wp.array2d(dtype=wp.float64), N: wp.array2d(dtype=wp.float64), S: wp.array2d(dtype=wp.float64), sschl: wp.array(dtype=wp.int64),
           sfolge: wp.array(dtype=wp.int64), h: wp.float64, hl: wp.array(dtype=wp.float64), abstand: wp.float64, tiefe: wp.float64, r2: wp.float64,
           r2weit: wp.float64, randabstand: wp.array(dtype=wp.float64), maske: wp.array(dtype=wp.uint8), ers: wp.array(dtype=wp.uint8),
           hoehe: wp.array(dtype=wp.float32), rand: wp.array(dtype=wp.float32)):
    i = wp.tid()
    px = K[i, 0]
    py = K[i, 1]
    pz = K[i, 2]
    if not in_huelle(px, py, pz, hl):
        return
    r = hoechster(S, sschl, sfolge, h, px, py, pz, N[i, 0], N[i, 1], N[i, 2], abstand, tiefe, r2)
    if r[0] != wp.float64(-wp.inf):
        maske[i] = wp.uint8(1)
        ers[i] = wp.uint8(1)
        if r[0] > wp.float64(hoehe[i]):
            hoehe[i] = wp.float32(r[0])
        ra = randabstand[int(r[1])]
        if ra < wp.float64(rand[i]):
            rand[i] = wp.float32(ra)
    else:
        w = hoechster(S, sschl, sfolge, h, px, py, pz, N[i, 0], N[i, 1], N[i, 2], abstand, tiefe, r2weit)
        if w[0] > wp.float64(hoehe[i]):
            hoehe[i] = wp.float32(w[0])


@wp.kernel
def durch(K: wp.array2d(dtype=wp.float64), N: wp.array2d(dtype=wp.float64), S: wp.array2d(dtype=wp.float64), ST: wp.array2d(dtype=wp.int64),
          sschl: wp.array(dtype=wp.int64), sfolge: wp.array(dtype=wp.int64), h: wp.float64, hl: wp.array(dtype=wp.float64), grenze2: wp.float64,
          tiefe: wp.float64, luft: wp.float64, grenze: wp.float64, nach_a: wp.array(dtype=wp.int64), nach_z: wp.array(dtype=wp.int64),
          inz_a: wp.array(dtype=wp.int64), inz_z: wp.array(dtype=wp.int64), naechste: int, aus: wp.array(dtype=wp.float32)):
    # `Hautdurchsicht.stueck`: die Tiefe, um die die Haut hinter den Stoff muss (alle Dreiecke um den nächsten Stoffpunkt); `naechste`: hinter die nächste Lage
    i = wp.tid()
    px = K[i, 0]
    py = K[i, 1]
    pz = K[i, 2]
    if not in_huelle(px, py, pz, hl):
        return
    nah = naechster(S, sschl, sfolge, h, px, py, pz)
    if nah[0] < wp.float64(0.0) or nah[1] > grenze2:
        return
    j = int(nah[0])
    noetig = wp.float64(0.0)
    vorne = int(0)  # noqa: UP018 - Warp: in der Schleife gesetzte Variable braucht den Typkonstruktor
    m = int(nach_a[j]) - 1
    while m < int(nach_a[j + 1]):
        w = j
        if m >= int(nach_a[j]):
            w = int(nach_z[m])
        o = int(nach_a[w]) - 1
        while o < int(nach_a[w + 1]):
            x = w
            if o >= int(nach_a[w]):
                x = int(nach_z[o])
            for e in range(int(inz_a[x]), int(inz_a[x + 1])):
                k = int(inz_z[e])
                t = strahl_dreieck(S, int(ST[k, 0]), int(ST[k, 1]), int(ST[k, 2]), px, py, pz, N[i, 0], N[i, 1], N[i, 2])
                if not wp.isnan(t) and t >= -tiefe and t < luft:
                    if naechste != 0 and noetig > wp.float64(0.0):
                        noetig = wp.min(noetig, luft - t)
                    elif luft - t > noetig:
                        noetig = luft - t
                elif naechste != 0 and not wp.isnan(t) and t >= luft and t <= tiefe:
                    vorne = 1                                                 # Stoff auch vor der Haut: deckt von außen, kein Durchstich
            o = o + 1
        m = m + 1
    if vorne != 0:
        noetig = wp.float64(0.0)
    if noetig > wp.float64(0.0):
        neu = wp.min(noetig, grenze)
        if neu > wp.float64(aus[i]):
            aus[i] = wp.float32(neu)


wp.load_module(sys.modules[__name__], device='cuda')
