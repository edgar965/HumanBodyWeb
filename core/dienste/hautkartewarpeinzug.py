# -*- coding: utf-8 -*-
u"""Hautkartewarpeinzug — die Kerne von `Hauteinzugrechnung` auf der Karte (18.11.2026, `Hautkarteeinzug`): je verdecktem Punkt ein Faden wie in JS.

`dicke`: `Hautdicke._dicke` (Gitter 25 mm, Schritte entlang −N; die Menge `gesehen` in JS spart nur doppelte Zellen — das Minimum bleibt dasselbe).
`einzug`: je verdecktem Punkt die Verschiebung — an einer Randecke unter die nächste Stoffkante (`Saumschnitt.verschiebung`), sonst entlang −N um
`min(Saumband.tiefe(Weg, bis), ANTEIL · Dicke)`. Float32 wie die Felder in JS (`Float32Array`): gespeichert wird gerundet, verglichen in double.
"""
import sys

import warp as wp

from .hautkartewarphilfe import untergrenze, zellnummer, zellschluessel

wp.set_module_options({'fuse_fp': False, 'enable_backward': False})


@wp.kernel
def dicke(P: wp.array2d(dtype=wp.float64), N: wp.array2d(dtype=wp.float64), schl: wp.array(dtype=wp.int64), folge: wp.array(dtype=wp.int64),
          h: wp.float64, auswahl: wp.array(dtype=wp.uint8), weite: wp.array(dtype=wp.float64), quer_m: wp.float64, quer_max: wp.float64,
          aus: wp.array(dtype=wp.float32)):
    i = wp.tid()
    if auswahl[i] == wp.uint8(0):
        return
    weit = weite[i]
    px = P[i, 0]
    py = P[i, 1]
    pz = P[i, 2]
    nx = N[i, 0]
    ny = N[i, 1]
    nz = N[i, 2]
    schritte = int(wp.ceil(weit / h)) - 1
    if schritte < 0:
        schritte = 0
    best = wp.float64(wp.inf)
    s = int(0)
    while s <= schritte:
        if best < wp.float64(s - 1) * h:
            break
        sh = wp.float64(s) * h
        ci = zellnummer(px - sh * nx, h)
        cj = zellnummer(py - sh * ny, h)
        ck = zellnummer(pz - sh * nz, h)
        for a in range(-1, 2):
            for b in range(-1, 2):
                for c in range(-1, 2):
                    sk = zellschluessel(ci + wp.int64(a), cj + wp.int64(b), ck + wp.int64(c))
                    p = untergrenze(schl, sk)
                    while p < schl.shape[0] and schl[p] == sk:
                        j = int(folge[p])
                        p = p + 1
                        if N[j, 0] * nx + N[j, 1] * ny + N[j, 2] * nz >= wp.float64(0.0):
                            continue
                        dx = px - P[j, 0]
                        dy = py - P[j, 1]
                        dz = pz - P[j, 2]
                        tiefe = dx * nx + dy * ny + dz * nz
                        if tiefe <= wp.float64(0.0) or tiefe >= best or tiefe > weit:
                            continue
                        qx = dx - tiefe * nx
                        qy = dy - tiefe * ny
                        qz = dz - tiefe * nz
                        quer = wp.max(quer_m, wp.min(wp.float64(0.5) * tiefe, quer_max))
                        if qx * qx + qy * qy + qz * qz <= quer * quer:
                            best = tiefe
        s = s + 1
    gerundet = wp.float32(best)
    if wp.float64(gerundet) <= weit:
        aus[i] = gerundet
    else:
        aus[i] = wp.float32(wp.inf)


@wp.kernel
def einzug(P: wp.array2d(dtype=wp.float64), N: wp.array2d(dtype=wp.float64), maske: wp.array(dtype=wp.uint8), ecken: wp.array(dtype=wp.uint8),
           kanten: wp.array2d(dtype=wp.float64), mschl: wp.array(dtype=wp.int64), mfolge: wp.array(dtype=wp.int64), kh: wp.float64, mit_kanten: int,
           schnapp2: wp.float64, unterkante: wp.float64, abstaende: wp.array(dtype=wp.float64), nachgeben: wp.array(dtype=wp.float32),
           tiefe_m: wp.float64, steigung: wp.float64, dicken: wp.array(dtype=wp.float32), anteil: wp.array(dtype=wp.float64),
           werte: wp.array2d(dtype=wp.float32), geschnappt: wp.array(dtype=wp.uint8)):
    i = wp.tid()
    if maske[i] == wp.uint8(0):
        return
    px = P[i, 0]
    py = P[i, 1]
    pz = P[i, 2]
    nx = N[i, 0]
    ny = N[i, 1]
    nz = N[i, 2]
    if mit_kanten != 0 and ecken[i] != wp.uint8(0):
        # `Saumschnitt.naechsterKantenpunkt`: Streckenmitten im Gitter, 27 Zellen, bester binnen SCHNAPP
        ci = zellnummer(px, kh)
        cj = zellnummer(py, kh)
        ck = zellnummer(pz, kh)
        best = schnapp2
        da = int(0)
        tx = wp.float64(0.0)
        ty = wp.float64(0.0)
        tz = wp.float64(0.0)
        for a in range(-1, 2):
            for b in range(-1, 2):
                for c in range(-1, 2):
                    sk = zellschluessel(ci + wp.int64(a), cj + wp.int64(b), ck + wp.int64(c))
                    p = untergrenze(mschl, sk)
                    while p < mschl.shape[0] and mschl[p] == sk:
                        k = int(mfolge[p])
                        p = p + 1
                        ax = kanten[k, 0]
                        ay = kanten[k, 1]
                        az = kanten[k, 2]
                        ex = kanten[k, 3] - ax
                        ey = kanten[k, 4] - ay
                        ez = kanten[k, 5] - az
                        e2 = ex * ex + ey * ey + ez * ez
                        t = wp.float64(0.0)
                        if e2 > wp.float64(0.0):
                            t = ((px - ax) * ex + (py - ay) * ey + (pz - az) * ez) / e2
                        if t < wp.float64(0.0):
                            t = wp.float64(0.0)
                        elif t > wp.float64(1.0):
                            t = wp.float64(1.0)
                        qx = ax + t * ex
                        qy = ay + t * ey
                        qz = az + t * ez
                        d2 = (qx - px) * (qx - px) + (qy - py) * (qy - py) + (qz - pz) * (qz - pz)
                        if d2 < best:
                            best = d2
                            da = 1
                            tx = qx
                            ty = qy
                            tz = qz
        if da != 0:
            dx = tx - px
            dy = ty - py
            dz = tz - pz
            entlang = dx * nx + dy * ny + dz * nz
            dx = dx - entlang * nx
            dy = dy - entlang * ny
            dz = dz - entlang * nz
            werte[i, 0] = wp.float32(dx - unterkante * nx)
            werte[i, 1] = wp.float32(dy - unterkante * ny)
            werte[i, 2] = wp.float32(dz - unterkante * nz)
            geschnappt[i] = wp.uint8(1)
            return
    bis = tiefe_m
    if nachgeben[i] > wp.float32(0.0):
        bis = wp.float64(nachgeben[i])
    tiefe = wp.min(bis, unterkante + steigung * abstaende[i])
    if anteil[0] > wp.float64(0.0):
        tiefe = wp.min(tiefe, anteil[0] * wp.float64(dicken[i]))
    werte[i, 0] = wp.float32(-tiefe * nx)
    werte[i, 1] = wp.float32(-tiefe * ny)
    werte[i, 2] = wp.float32(-tiefe * nz)


wp.load_module(sys.modules[__name__], device='cuda')
