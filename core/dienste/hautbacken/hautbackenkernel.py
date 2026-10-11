# -*- coding: utf-8 -*-
"""Die GPU-Kernel des Hautbackens (NVIDIA Warp) — Funktionen auf Modulebene, weil Warp sie so übersetzt; die Klassen des Pakets rufen sie nur auf.

Alles rechnet je Texel einer Kachel (`ids`/`bary`: welches Dreieck der Figur, mit welchen Schwerpunktkoordinaten) und teilt sich die Treffer (`face`, `hu`, `hv`: welches
Dreieck des Quellkörpers, mit welchen Schwerpunktkoordinaten) zwischen den Kanälen — Blender schoss für jeden Kanal neu.

    rastern     UV-Dreiecke der Figur in die Kachel: je Texel Dreieck und Schwerpunkt (Texelmitte plus Blenders Versatz, `Hautbackenkachel.VERSATZ`, wie `RE_bake_pixels_populate`)
    schiessen   je Texel ein Strahl vom Punkt der Figur, `auszug` nach außen, entlang der geglätteten Normale nach innen, höchstens `laenge` weit, auf den Körper
    erweitern   ein Schritt des Rands (Blender: `bake.margin`, 16 Texel): jedes leere Texel neben belegten nimmt den Mittelwert seiner belegten Nachbarn
"""

import warp as wp

__all__ = ['rastern', 'schiessen', 'erweitern']

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
