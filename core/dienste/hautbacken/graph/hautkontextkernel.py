# -*- coding: utf-8 -*-
"""Die Kernel des Schattierungskontexts — was Cycles in `ShaderData` hält, wenn es einen Knotengraph an einem Backpunkt auswertet.

Quellen (Blender-Repo, Zweig main, gelesen 10.10.2026, lokal `ProjektTemp/_wegwerf/cycles_quelle/`):
    `kernel/integrator/init_from_bake.h`   Strahl, Differenziale (`dP = dPdu·dudx + dPdv·dvdx`, gepackt als Mittel der Längen), Rückseiten-Prüfung
    `kernel/geom/triangle.h`                `triangle_point_normal`, `triangle_smooth_normal`, `triangle_dPdudv`, `triangle_attribute` (mit Ableitungen)
    `kernel/util/differential.h`            `differential_from_compact`, `differential_dudv`
    `source/blender/render/intern/bake.cc`  die Pixel-Differenziale (`bake_differentials`, `cast_ray_highpoly`)
Schwerpunktkoordinaten: `u`, `v` sind die Gewichte der Ecken 1 und 2 (Cycles-Konvention: P = (1−u−v)·P0 + u·P1 + v·P2).
"""

import warp as wp

from ..hautfunktionen import make_orthonormals_a, safe_normalize3

__all__ = ['geometrie', 'differenzial', 'differenzial_uv', 'attribut2', 'attribut4', 'normale_unnormiert', 'normale_roh', 'glatt_je_treffer', 'tangente_interpoliert',
           'verteilen_vec3', 'verteilen_float']


@wp.func
def packed_normal(n: wp.vec3) -> wp.vec3:
    """`packed_normal` (Cycles, `util/types_normal.h`): oktaedrisch in 2 × 16 Bit gepackt und wieder entpackt — so liegen die Normalen im Kernel."""
    mu = 65535.0
    hmu = mu / 2.0
    inv_l1 = 1.0 / (wp.abs(n[0]) + wp.abs(n[1]) + wp.abs(n[2]) + 1.0e-6)
    vx = n[0] * inv_l1
    vy = n[1] * inv_l1
    sx = float(1.0)
    sy = float(1.0)
    if n[0] < 0.0:
        sx = -1.0
    if n[1] < 0.0:
        sy = -1.0
    wrapx = (1.0 - wp.abs(vy)) * sx
    wrapy = (1.0 - wp.abs(vx)) * sy
    if n[2] < 0.0:
        vx = wrapx
        vy = wrapy
    dx = float(int(wp.clamp(vx * hmu + (hmu + 0.5), 0.0, mu)))
    dy = float(int(wp.clamp(vy * hmu + (hmu + 0.5), 0.0, mu)))
    inv_hmu = 2.0 / mu
    nx = dx * inv_hmu - 1.0
    ny = dy * inv_hmu - 1.0
    nz = 1.0 - wp.abs(nx) - wp.abs(ny)
    t = wp.max(-nz, 0.0)
    if -nx < 0.0:
        nx = nx - t
    else:
        nx = nx + t
    if -ny < 0.0:
        ny = ny - t
    else:
        ny = ny + t
    return wp.normalize(wp.vec3(nx, ny, nz))


@wp.kernel
def geometrie(face: wp.array(dtype=wp.int32), hu: wp.array(dtype=wp.float32), hv: wp.array(dtype=wp.float32), tri: wp.array(dtype=wp.vec3i),
              pos: wp.array(dtype=wp.vec3), ecke_n: wp.array(dtype=wp.vec3), glatt: wp.array(dtype=wp.int32), ng_aus: wp.array(dtype=wp.vec3),
              n_aus: wp.array(dtype=wp.vec3), dpdu_aus: wp.array(dtype=wp.vec3), dpdv_aus: wp.array(dtype=wp.vec3), rueck_aus: wp.array(dtype=wp.int32)):
    """Je Treffer `Ng`, `N`, `dPdu`, `dPdv` wie `triangle_shader_setup` + Rückseitenprüfung in `shader_setup_from_ray`: wi = −ray.D = N (der geglättete Normalenvektor, `init_from_bake.h`),
    Rückseite, wenn dot(Ng, wi) < 0 — dann kehren Ng, N, dPdu, dPdv um. `ecke_n`: die Eckennormalen (T·3), vorher durch `packed_normal` geschickt."""
    i = wp.tid()
    f = face[i]
    t = tri[f]
    p0 = pos[t[0]]
    p1 = pos[t[1]]
    p2 = pos[t[2]]
    u = hu[i]
    v = hv[i]
    ng = wp.normalize(wp.cross(p1 - p0, p2 - p0))
    n = ng
    if glatt[f] != 0:
        s = safe_normalize3((1.0 - u - v) * ecke_n[f * 3] + u * ecke_n[f * 3 + 1] + v * ecke_n[f * 3 + 2])
        if s[0] == 0.0 and s[1] == 0.0 and s[2] == 0.0:
            s = ng
        n = s
    dpdu = p1 - p0
    dpdv = p2 - p0
    rueck = int(0)
    if wp.dot(ng, n) < 0.0:
        ng = -ng
        n = -n
        dpdu = -dpdu
        dpdv = -dpdv
        rueck = 1
    ng_aus[i] = ng
    n_aus[i] = n
    dpdu_aus[i] = dpdu
    dpdv_aus[i] = dpdv
    rueck_aus[i] = rueck


@wp.kernel
def differenzial(idx: wp.array(dtype=wp.int32), face: wp.array(dtype=wp.int32), f_ids: wp.array(dtype=wp.int32), f_bary: wp.array(dtype=wp.vec2),
                 f_pos: wp.array(dtype=wp.vec3), f_nor: wp.array(dtype=wp.vec3), f_tri: wp.array(dtype=wp.vec3i), f_uv: wp.array(dtype=wp.vec2), px: int,
                 q_pos: wp.array(dtype=wp.vec3), q_tri: wp.array(dtype=wp.vec3i), dp_aus: wp.array(dtype=wp.float32)):
    """Je Treffer die gepackte Pixel-Ableitung `dP` (Mittel der Längen von dP.dx und dP.dy, `differential_make_compact`) nach `cast_ray_highpoly` (`bake.cc`):
    Positionsdifferenzial auf der Figur (`bake_differentials` aus den UV der Dreiecksecken in Texeln), entlang der Strahlrichtung auf die Ebene des getroffenen Dreiecks übertragen."""
    k = wp.tid()
    texel = idx[k]
    t = f_ids[texel]
    i = f_tri[t]
    w1 = f_bary[texel][0]
    w2 = f_bary[texel][1]
    w0 = 1.0 - w1 - w2
    # UV der Figur in Texeln (u · px, v · px): bake_differentials (bake.cc) rechnet mit (uv − offset) · Breite, ohne Spiegelung
    c = float(px)
    a = f_uv[t * 3] * c
    b = f_uv[t * 3 + 1] * c
    d = f_uv[t * 3 + 2] * c
    bruch = (b[0] - a[0]) * (d[1] - a[1]) - (d[0] - a[0]) * (b[1] - a[1])
    du_dx = float(0.0)
    dv_dx = float(0.0)
    du_dy = float(0.0)
    dv_dy = float(0.0)
    if wp.abs(bruch) > 1.1920929e-07:
        bruch = 1.0 / bruch
        du_dx = (b[1] - d[1]) * bruch
        dv_dx = (d[1] - a[1]) * bruch
        du_dy = (d[0] - b[0]) * bruch
        dv_dy = (a[0] - d[0]) * bruch
    duco = f_pos[i[0]] - f_pos[i[2]]
    dvco = f_pos[i[1]] - f_pos[i[2]]
    dxco = duco * du_dx + dvco * dv_dx
    dyco = duco * du_dy + dvco * dv_dy
    # Strahlrichtung: −normalize(Eckennormalen der Figur, geglättet) (calc_point_from_barycentric_extrusion)
    r = -wp.normalize(f_nor[i[0]] * w0 + f_nor[i[1]] * w1 + f_nor[i[2]] * w2)
    q = q_tri[face[k]]
    nh = wp.normalize(wp.cross(q_pos[q[1]] - q_pos[q[0]], q_pos[q[2]] - q_pos[q[0]]))
    tmp = r * (1.0 / wp.dot(r, nh))
    dxco = dxco - tmp * wp.dot(dxco, nh)
    dyco = dyco - tmp * wp.dot(dyco, nh)
    dp_aus[k] = 0.5 * (wp.length(dxco) + wp.length(dyco))


@wp.kernel
def differenzial_uv(ng: wp.array(dtype=wp.vec3), dpdu: wp.array(dtype=wp.vec3), dpdv: wp.array(dtype=wp.vec3), dp: wp.array(dtype=wp.float32),
                    dpx_aus: wp.array(dtype=wp.vec3), dpy_aus: wp.array(dtype=wp.vec3), dudx_aus: wp.array(dtype=wp.float32), dvdx_aus: wp.array(dtype=wp.float32),
                    dudy_aus: wp.array(dtype=wp.float32), dvdy_aus: wp.array(dtype=wp.float32)):
    """`differential_from_compact(Ng, dP)` (dP.dx = dP · a, dP.dy = dP · b mit den Orthonormalen von Ng) und daraus `differential_dudv`: die Ableitungen der Schwerpunktkoordinaten
    nach x und y (Cramersche Regel nach Projektion auf die stabilste Achse von Ng)."""
    i = wp.tid()
    n = ng[i]
    a = make_orthonormals_a(n)
    b = wp.cross(n, a)
    pdx = a * dp[i]
    pdy = b * dp[i]
    dpx_aus[i] = pdx
    dpy_aus[i] = pdy
    xn = wp.abs(n[0])
    yn = wp.abs(n[1])
    zn = wp.abs(n[2])
    u2 = wp.vec2(dpdu[i][0], dpdu[i][1])
    v2 = wp.vec2(dpdv[i][0], dpdv[i][1])
    px2 = wp.vec2(pdx[0], pdx[1])
    py2 = wp.vec2(pdy[0], pdy[1])
    if zn < xn or zn < yn:
        if yn < xn or yn < zn:
            u2 = wp.vec2(dpdu[i][1], u2[1])
            v2 = wp.vec2(dpdv[i][1], v2[1])
            px2 = wp.vec2(pdx[1], px2[1])
            py2 = wp.vec2(pdy[1], py2[1])
        u2 = wp.vec2(u2[0], dpdu[i][2])
        v2 = wp.vec2(v2[0], dpdv[i][2])
        px2 = wp.vec2(px2[0], pdx[2])
        py2 = wp.vec2(py2[0], pdy[2])
    det = u2[0] * v2[1] - v2[0] * u2[1]
    if det != 0.0:
        det = 1.0 / det
    dudx_aus[i] = (px2[0] * v2[1] - px2[1] * v2[0]) * det
    dvdx_aus[i] = (px2[1] * u2[0] - px2[0] * u2[1]) * det
    dudy_aus[i] = (py2[0] * v2[1] - py2[1] * v2[0]) * det
    dvdy_aus[i] = (py2[1] * u2[0] - py2[0] * u2[1]) * det


@wp.kernel
def attribut2(face: wp.array(dtype=wp.int32), hu: wp.array(dtype=wp.float32), hv: wp.array(dtype=wp.float32), ecken: wp.array(dtype=wp.vec2),
              dudx: wp.array(dtype=wp.float32), dvdx: wp.array(dtype=wp.float32), dudy: wp.array(dtype=wp.float32), dvdy: wp.array(dtype=wp.float32),
              val: wp.array(dtype=wp.vec2), dx: wp.array(dtype=wp.vec2), dy: wp.array(dtype=wp.vec2)):
    """Ein Ecken-Attribut (UV) am Treffer samt Ableitungen: `triangle_attribute` mit `dual2` (`triangle_interpolate`, `triangle_attribute_dfdx/dfdy`)."""
    i = wp.tid()
    f = face[i]
    f0 = ecken[f * 3]
    f1 = ecken[f * 3 + 1]
    f2 = ecken[f * 3 + 2]
    u = hu[i]
    v = hv[i]
    val[i] = (1.0 - u - v) * f0 + u * f1 + v * f2
    dx[i] = dudx[i] * f1 + dvdx[i] * f2 - (dudx[i] + dvdx[i]) * f0
    dy[i] = dudy[i] * f1 + dvdy[i] * f2 - (dudy[i] + dvdy[i]) * f0


@wp.kernel
def attribut4(face: wp.array(dtype=wp.int32), hu: wp.array(dtype=wp.float32), hv: wp.array(dtype=wp.float32), ecken: wp.array(dtype=wp.vec4),
              dudx: wp.array(dtype=wp.float32), dvdx: wp.array(dtype=wp.float32), dudy: wp.array(dtype=wp.float32), dvdy: wp.array(dtype=wp.float32),
              val: wp.array(dtype=wp.vec4), dx: wp.array(dtype=wp.vec4), dy: wp.array(dtype=wp.vec4)):
    """Wie `attribut2` für ein Farbattribut (`dual4`)."""
    i = wp.tid()
    f = face[i]
    f0 = ecken[f * 3]
    f1 = ecken[f * 3 + 1]
    f2 = ecken[f * 3 + 2]
    u = hu[i]
    v = hv[i]
    val[i] = (1.0 - u - v) * f0 + u * f1 + v * f2
    dx[i] = dudx[i] * f1 + dvdx[i] * f2 - (dudx[i] + dvdx[i]) * f0
    dy[i] = dudy[i] * f1 + dvdy[i] * f2 - (dudy[i] + dvdy[i]) * f0


@wp.kernel
def normale_unnormiert(face: wp.array(dtype=wp.int32), hu: wp.array(dtype=wp.float32), hv: wp.array(dtype=wp.float32), ecken: wp.array(dtype=wp.vec3),
                       glatt: wp.array(dtype=wp.int32), ng: wp.array(dtype=wp.vec3), aus: wp.array(dtype=wp.vec3)):
    """`triangle_smooth_normal_unnormalized_object_space` (triangle.h): sie normiert trotz des Namens (`safe_normalize(triangle_interpolate(…))`); Null → Ng.
    Bei einem flachen Dreieck (`sd->shader & SHADER_SMOOTH_NORMAL` unwahr) ruft Cycles diese Funktion nicht auf (der Normal-Map-Knoten nimmt dann `sd->Ng`)."""
    i = wp.tid()
    f = face[i]
    u = hu[i]
    v = hv[i]
    s = safe_normalize3((1.0 - u - v) * ecken[f * 3] + u * ecken[f * 3 + 1] + v * ecken[f * 3 + 2])
    if s[0] == 0.0 and s[1] == 0.0 and s[2] == 0.0:
        s = ng[i]
    aus[i] = s


@wp.kernel
def normale_roh(face: wp.array(dtype=wp.int32), hu: wp.array(dtype=wp.float32), hv: wp.array(dtype=wp.float32), ecken: wp.array(dtype=wp.vec3),
                aus: wp.array(dtype=wp.vec3)):
    """Die Eckennormalen linear gemischt, NICHT normiert — das Attribut `ATTR_STD_NORMAL_UNDISPLACED` des Normal-Map-Knotens mit Basis „Original" (`triangle_attribute`)."""
    i = wp.tid()
    f = face[i]
    u = hu[i]
    v = hv[i]
    aus[i] = (1.0 - u - v) * ecken[f * 3] + u * ecken[f * 3 + 1] + v * ecken[f * 3 + 2]


@wp.kernel
def glatt_je_treffer(face: wp.array(dtype=wp.int32), glatt: wp.array(dtype=wp.int32), aus: wp.array(dtype=wp.int32)):
    i = wp.tid()
    aus[i] = glatt[face[i]]


@wp.kernel
def tangente_interpoliert(face: wp.array(dtype=wp.int32), hu: wp.array(dtype=wp.float32), hv: wp.array(dtype=wp.float32), tang: wp.array(dtype=wp.vec3),
                          vorz: wp.array(dtype=wp.float32), t_aus: wp.array(dtype=wp.vec3), s_aus: wp.array(dtype=wp.float32)):
    """Tangente und Vorzeichen der Bitangente am Treffer, ohne Normierung (`primitive_surface_attribute<float3>` / `<float>` im Normal-Map-Knoten, `tex_coord.h`)."""
    i = wp.tid()
    f = face[i]
    u = hu[i]
    v = hv[i]
    w = 1.0 - u - v
    t_aus[i] = w * tang[f * 3] + u * tang[f * 3 + 1] + v * tang[f * 3 + 2]
    s_aus[i] = w * vorz[f * 3] + u * vorz[f * 3 + 1] + v * vorz[f * 3 + 2]


@wp.kernel
def verteilen_vec3(idx: wp.array(dtype=wp.int32), quelle: wp.array(dtype=wp.vec3), ziel: wp.array(dtype=wp.vec3)):
    """`ziel[idx[i]] = quelle[i]` — die Ergebnisse eines Stapels ins Bild."""
    i = wp.tid()
    ziel[idx[i]] = quelle[i]


@wp.kernel
def verteilen_float(idx: wp.array(dtype=wp.int32), quelle: wp.array(dtype=wp.float32), ziel: wp.array(dtype=wp.float32)):
    i = wp.tid()
    ziel[idx[i]] = quelle[i]
