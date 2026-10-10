# -*- coding: utf-8 -*-
"""Die GPU-Kernel des Hautbackens (NVIDIA Warp) — Funktionen auf Modulebene, weil Warp sie so übersetzt; die Klassen des Pakets rufen sie nur auf.

Alles rechnet je Texel einer Kachel (`ids`/`bary`: welches Dreieck der Figur, mit welchen Schwerpunktkoordinaten) und teilt sich die Treffer (`face`, `hu`, `hv`: welches
Dreieck des Quellkörpers, mit welchen Schwerpunktkoordinaten) zwischen den Kanälen — Blender schoss für jeden Kanal neu.

    rastern     UV-Dreiecke der Figur in die Kachel: je Texel Dreieck und Schwerpunkt (Texelmitte, wie `RE_bake_pixels_populate`)
    schiessen   je Texel ein Strahl vom Punkt der Figur, `auszug` nach außen, entlang der geglätteten Normale nach innen, höchstens `laenge` weit, auf den Körper
    abtasten    am Treffer die UV des Körpers, dort das Bild (bilinear, `wiederholen` wie ein Bildknoten ohne Erweiterung)
    normalen    am Treffer die Normale des Körpers, mit der Normalenkarte gestört, im Tangentenraum der Figur (Blender: `bake(type='NORMAL', normal_space='TANGENT')`)
    erweitern   ein Schritt des Rands (Blender: `bake.margin`, 16 Texel): jedes leere Texel neben belegten nimmt den Mittelwert seiner belegten Nachbarn
"""

import warp as wp

__all__ = ['rastern', 'schiessen', 'abtasten', 'normalen_backen', 'erweitern']

wp.config.log_level = wp.LOG_WARNING


@wp.kernel
def rastern(uv: wp.array(dtype=wp.vec2), tri_uv: wp.array(dtype=wp.vec3i), px: int, ox: float, oy: float,
            ids: wp.array2d(dtype=wp.int32), bary: wp.array2d(dtype=wp.vec2)):
    """Ein Thread je Dreieck: alle Texel seines Umrisses, deren Mitte (plus Versatz `ox`, `oy` in Texeln) im Dreieck liegt. Zeile 0 ist oben (v = 1)."""
    t = wp.tid()
    i = tri_uv[t]
    f = float(px)
    a = wp.vec2(uv[i[0]][0] * f, (1.0 - uv[i[0]][1]) * f)
    b = wp.vec2(uv[i[1]][0] * f, (1.0 - uv[i[1]][1]) * f)
    c = wp.vec2(uv[i[2]][0] * f, (1.0 - uv[i[2]][1]) * f)
    x0 = int(wp.floor(wp.min(a[0], wp.min(b[0], c[0])))) - 1
    x1 = int(wp.ceil(wp.max(a[0], wp.max(b[0], c[0])))) + 1
    y0 = int(wp.floor(wp.min(a[1], wp.min(b[1], c[1])))) - 1
    y1 = int(wp.ceil(wp.max(a[1], wp.max(b[1], c[1])))) + 1
    n = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
    if wp.abs(n) < 1.0e-12:
        return
    for y in range(wp.max(y0, 0), wp.min(y1 + 1, px)):
        for x in range(wp.max(x0, 0), wp.min(x1 + 1, px)):
            p = wp.vec2(float(x) + 0.5 + ox, float(y) + 0.5 + oy)
            w1 = ((p[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (p[1] - a[1])) / n
            w2 = ((b[0] - a[0]) * (p[1] - a[1]) - (p[0] - a[0]) * (b[1] - a[1])) / n
            w0 = 1.0 - w1 - w2
            if w0 >= -1.0e-6 and w1 >= -1.0e-6 and w2 >= -1.0e-6:
                ids[y, x] = t
                bary[y, x] = wp.vec2(w1, w2)


@wp.kernel
def schiessen(mesh: wp.uint64, pos: wp.array(dtype=wp.vec3), nor: wp.array(dtype=wp.vec3), tri_v: wp.array(dtype=wp.vec3i),
              ids: wp.array2d(dtype=wp.int32), bary: wp.array2d(dtype=wp.vec2), auszug: float, laenge: float,
              face: wp.array2d(dtype=wp.int32), hu: wp.array2d(dtype=wp.float32), hv: wp.array2d(dtype=wp.float32)):
    """Je Texel: `face` = Dreieck des Körpers (-1 ohne Treffer), `hu`/`hv` = Gewicht der Ecken 1 und 2 dort (Ecke 0: `1 − hu − hv`).
    Warps `mesh_query_ray` liefert `u`, `v` mit p = u·A + v·B + (1−u−v)·C — gemessen an einer Ebene (Abstand Treffer–Strahlfuß 6·10⁻⁹ m gegen 5,2·10⁻³ m bei der
    Annahme (1−u−v)·A + u·B + v·C); die ersten Messungen gegen Blender lagen deshalb um bis zu eine Dreiecksbreite daneben."""
    y, x = wp.tid()
    t = ids[y, x]
    face[y, x] = -1
    if t < 0:
        return
    i = tri_v[t]
    w1 = bary[y, x][0]
    w2 = bary[y, x][1]
    w0 = 1.0 - w1 - w2
    p = pos[i[0]] * w0 + pos[i[1]] * w1 + pos[i[2]] * w2
    n = wp.normalize(nor[i[0]] * w0 + nor[i[1]] * w1 + nor[i[2]] * w2)
    q = wp.mesh_query_ray(mesh, p + n * auszug, -n, laenge)
    if q.result:
        face[y, x] = q.face
        hu[y, x] = q.v
        hv[y, x] = 1.0 - q.u - q.v


@wp.kernel
def abtasten(face: wp.array2d(dtype=wp.int32), hu: wp.array2d(dtype=wp.float32), hv: wp.array2d(dtype=wp.float32), uv_ecken: wp.array(dtype=wp.vec2),
             bild: wp.array3d(dtype=wp.uint8), aus: wp.array3d(dtype=wp.uint8)):
    """Die Farbe des Bildes am Treffer, bilinear auf den gespeicherten Werten (Cycles mischt Byte-Bilder vor dem Umrechnen), als Byte-Bild. Ohne Treffer bleibt `aus`."""
    y, x = wp.tid()
    f = face[y, x]
    if f < 0:
        return
    u = hu[y, x]
    v = hv[y, x]
    uv = uv_ecken[f * 3] * (1.0 - u - v) + uv_ecken[f * 3 + 1] * u + uv_ecken[f * 3 + 2] * v
    h = bild.shape[0]
    w = bild.shape[1]
    fx = uv[0] * float(w) - 0.5
    fy = (1.0 - uv[1]) * float(h) - 0.5
    x0 = int(wp.floor(fx))
    y0 = int(wp.floor(fy))
    ax = fx - float(x0)
    ay = fy - float(y0)
    for k in range(3):
        s = float(0.0)
        for dy in range(2):
            for dx in range(2):
                xx = ((x0 + dx) % w + w) % w
                yy = ((y0 + dy) % h + h) % h
                gew = (ax if dx == 1 else 1.0 - ax) * (ay if dy == 1 else 1.0 - ay)
                s += gew * float(bild[yy, xx, k])
        aus[y, x, k] = wp.uint8(wp.min(wp.max(s + 0.5, 0.0), 255.0))


@wp.kernel
def normalen_backen(face: wp.array2d(dtype=wp.int32), hu: wp.array2d(dtype=wp.float32), hv: wp.array2d(dtype=wp.float32),
                    q_tri: wp.array(dtype=wp.vec3i), q_nor: wp.array(dtype=wp.vec3), q_tang: wp.array(dtype=wp.vec4),
                    uv_ecken: wp.array(dtype=wp.vec2), karte: wp.array3d(dtype=wp.uint8), staerke: float,
                    ids: wp.array2d(dtype=wp.int32), bary: wp.array2d(dtype=wp.vec2), f_tri: wp.array(dtype=wp.vec3i), f_nor: wp.array(dtype=wp.vec3),
                    f_tang: wp.array(dtype=wp.vec4), aus: wp.array3d(dtype=wp.uint8)):
    """Die Normale des Körpers am Treffer (geglättet, mit der Normalenkarte gestört) im Tangentenraum der Figur an diesem Texel: (x, y, z) · 0,5 + 0,5 als Byte.
    Die Tangenten (`q_tang`, `f_tang`) stehen je Ecke (`Dreieck * 3 + Ecke`)."""
    y, x = wp.tid()
    f = face[y, x]
    if f < 0:
        return
    u = hu[y, x]
    v = hv[y, x]
    w0 = 1.0 - u - v
    i = q_tri[f]
    n = wp.normalize(q_nor[i[0]] * w0 + q_nor[i[1]] * u + q_nor[i[2]] * v)
    t4 = q_tang[f * 3] * w0 + q_tang[f * 3 + 1] * u + q_tang[f * 3 + 2] * v
    t = wp.vec3(t4[0], t4[1], t4[2])
    t = wp.normalize(t - n * wp.dot(n, t))
    b = wp.cross(n, t) * q_tang[f * 3][3]
    uv = uv_ecken[f * 3] * w0 + uv_ecken[f * 3 + 1] * u + uv_ecken[f * 3 + 2] * v
    h = karte.shape[0]
    w = karte.shape[1]
    fx = uv[0] * float(w) - 0.5
    fy = (1.0 - uv[1]) * float(h) - 0.5
    x0 = int(wp.floor(fx))
    y0 = int(wp.floor(fy))
    ax = fx - float(x0)
    ay = fy - float(y0)
    m = wp.vec3(0.0, 0.0, 0.0)
    for k in range(3):
        s = float(0.0)
        for dy in range(2):
            for dx in range(2):
                xx = ((x0 + dx) % w + w) % w
                yy = ((y0 + dy) % h + h) % h
                gew = (ax if dx == 1 else 1.0 - ax) * (ay if dy == 1 else 1.0 - ay)
                s += gew * float(karte[yy, xx, k])
        m[k] = s / 255.0 * 2.0 - 1.0
    # Cycles, Knoten „Normal Map" (Tangentenraum): N' = x·T + y·B + z·N, bei Stärke ≠ 1 zur Normale hin gemischt
    nk = wp.normalize(t * m[0] + b * m[1] + n * m[2])
    ns = wp.normalize(n + (nk - n) * staerke)
    # Tangentenraum der Figur am Texel
    tt = ids[y, x]
    j = f_tri[tt]
    w1 = bary[y, x][0]
    w2 = bary[y, x][1]
    c0 = 1.0 - w1 - w2
    fn = wp.normalize(f_nor[j[0]] * c0 + f_nor[j[1]] * w1 + f_nor[j[2]] * w2)
    f4 = f_tang[tt * 3] * c0 + f_tang[tt * 3 + 1] * w1 + f_tang[tt * 3 + 2] * w2
    ft = wp.vec3(f4[0], f4[1], f4[2])
    ft = wp.normalize(ft - fn * wp.dot(fn, ft))
    fb = wp.cross(fn, ft) * f_tang[tt * 3][3]
    r = wp.vec3(wp.dot(ns, ft), wp.dot(ns, fb), wp.dot(ns, fn))
    for k in range(3):
        aus[y, x, k] = wp.uint8(wp.min(wp.max((r[k] * 0.5 + 0.5) * 255.0 + 0.5, 0.0), 255.0))


@wp.kernel
def erweitern(bild: wp.array3d(dtype=wp.uint8), maske: wp.array2d(dtype=wp.uint8), nah: wp.array2d(dtype=wp.uint8), radius: int, aus: wp.array3d(dtype=wp.uint8),
              aus_maske: wp.array2d(dtype=wp.uint8)):
    """Der Rand: jedes leere Texel, das höchstens `radius` Texel (euklidisch) von einem belegten entfernt liegt, nimmt die Farbe des nächsten belegten und gilt danach als belegt.
    `nah` ist die vorab (CPU, schnell) berechnete Umgebung der belegten Texel — nur dort wird gesucht."""
    y, x = wp.tid()
    h = bild.shape[0]
    w = bild.shape[1]
    for k in range(3):
        aus[y, x, k] = bild[y, x, k]
    if maske[y, x] != wp.uint8(0):
        aus_maske[y, x] = wp.uint8(1)
        return
    aus_maske[y, x] = wp.uint8(0)
    if nah[y, x] == wp.uint8(0):
        return
    beste = radius * radius + 1
    by = int(-1)
    bx = int(-1)
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            yy = y + dy
            xx = x + dx
            if yy >= 0 and yy < h and xx >= 0 and xx < w:
                if maske[yy, xx] != wp.uint8(0):
                    d = dy * dy + dx * dx
                    if d < beste:
                        beste = d
                        by = yy
                        bx = xx
    if by >= 0:
        aus_maske[y, x] = wp.uint8(1)
        for k in range(3):
            aus[y, x, k] = bild[by, bx, k]
