// hautbackenkern.cuh — Rastern, Strahlen, Rand, Ausgabe ins Bild und die kleinen Hilfskerne des Backers (bis 21.11.2026 Warp: `hautbackenkernel.py`,
// `graph/hautausgabekernel.py`, `hautalphakernel.py`, `hautglanzkernel.py`, `hautumwandlung.py`, `hautbackengraph._rueckdrehen`). Zeile für Zeile übertragen;
// die Blender-Quellen (bake.cc, data_passes.h, closure.h, convert.h) stehen dort. Der Strahl ist `kn::strahl` (Warp 1.17 `mesh_query_ray`, kartenstrahl.cuh).
#pragma once
#include "hautfunktionen.cuh"

namespace hb {

// UV-Dreiecke der Figur in die Kachel: je Texel Dreieck und Schwerpunkt (Texelmitte plus Versatz ox, oy); ein Faden je Dreieck, Zeile 0 oben (v = 1)
__global__ void k_rastern(int nt, const float* uv, const int* tri_uv, int px, float ox, float oy, int* ids, float* bary)
{
    HB_FADEN(nt)
    const int t = i;
    const int i0 = tri_uv[3 * t], i1 = tri_uv[3 * t + 1], i2 = tri_uv[3 * t + 2];
    const float f = (float)px;
    const v2 a = V2(uv[2 * i0] * f, (1.0f - uv[2 * i0 + 1]) * f);
    const v2 b = V2(uv[2 * i1] * f, (1.0f - uv[2 * i1 + 1]) * f);
    const v2 c = V2(uv[2 * i2] * f, (1.0f - uv[2 * i2 + 1]) * f);
    const int x0 = (int)floorf(fminf(a.c[0], fminf(b.c[0], c.c[0]))) - 1;
    const int x1 = (int)ceilf(fmaxf(a.c[0], fmaxf(b.c[0], c.c[0]))) + 1;
    const int y0 = (int)floorf(fminf(a.c[1], fminf(b.c[1], c.c[1]))) - 1;
    const int y1 = (int)ceilf(fmaxf(a.c[1], fmaxf(b.c[1], c.c[1]))) + 1;
    const float n = (b.c[0] - a.c[0]) * (c.c[1] - a.c[1]) - (c.c[0] - a.c[0]) * (b.c[1] - a.c[1]);
    if (fabsf(n) < 1.0e-12f)
        return;
    for (int y = imax(y0, 0); y < imin(y1 + 1, px); ++y)
        for (int x = imax(x0, 0); x < imin(x1 + 1, px); ++x) {
            const v2 p = V2((float)x + 0.5f + ox, (float)y + 0.5f + oy);
            const float w1 = ((p.c[0] - a.c[0]) * (c.c[1] - a.c[1]) - (c.c[0] - a.c[0]) * (p.c[1] - a.c[1])) / n;
            const float w2 = ((b.c[0] - a.c[0]) * (p.c[1] - a.c[1]) - (p.c[0] - a.c[0]) * (b.c[1] - a.c[1])) / n;
            const float w0 = 1.0f - w1 - w2;
            if (w0 >= -1.0e-6f && w1 >= -1.0e-6f && w2 >= -1.0e-6f) {
                const long long q = (long long)y * px + x;
                ids[q] = t;
                bary[2 * q] = w1;
                bary[2 * q + 1] = w2;
            }
        }
}

// je Texel ein Strahl vom Punkt der Figur, `auszug` nach außen, entlang der geglätteten Normale nach innen bis `laenge`; hu/hv = Gewichte der Ecken 1, 2
__global__ void k_schiessen(int nn, fl::Netzbaum netz, const float* pos, const float* nor, const int* tri_v, const int* ids, const float* bary, float auszug,
                            float laenge, int* face, float* hu, float* hv)
{
    HB_FADEN(nn)
    const int t = ids[i];
    face[i] = -1;
    if (t < 0)
        return;
    const int j0 = tri_v[3 * t], j1 = tri_v[3 * t + 1], j2 = tri_v[3 * t + 2];
    const float w1 = bary[2 * i], w2 = bary[2 * i + 1];
    const float w0 = 1.0f - w1 - w2;
    const v3 p = add(add(mul(lies3(pos, j0), w0), mul(lies3(pos, j1), w1)), mul(lies3(pos, j2), w2));
    const v3 n = normalize(add(add(mul(lies3(nor, j0), w0), mul(lies3(nor, j1), w1)), mul(lies3(nor, j2), w2)));
    const v3 start = add(p, mul(n, auszug));
    const v3 dir = neg(n);
    float qt, qu, qv;
    int qf;
    if (kn::strahl(netz, fl::V3(start.c[0], start.c[1], start.c[2]), fl::V3(dir.c[0], dir.c[1], dir.c[2]), laenge, qt, qf, qu, qv)) {
        face[i] = qf;
        hu[i] = qv;
        hv[i] = 1.0f - qu - qv;
    }
}

// der Rand: jedes leere Texel bis `radius` (euklidisch) neben einem belegten nimmt die Farbe des nächsten belegten; `nah` = vorab berechnete Umgebung
__global__ void k_erweitern(int h, int w, const u8* bild, const u8* maske, const u8* nah, int radius, u8* aus, u8* aus_maske)
{
    HB_FADEN(h * w)
    const int y = i / w, x = i % w;
    for (int k = 0; k < 3; ++k)
        aus[3 * i + k] = bild[3 * i + k];
    if (maske[i] != 0) {
        aus_maske[i] = 1;
        return;
    }
    aus_maske[i] = 0;
    if (nah[i] == 0)
        return;
    int beste = radius * radius + 1, by = -1, bx = -1;
    for (int dy = -radius; dy < radius + 1; ++dy)
        for (int dx = -radius; dx < radius + 1; ++dx) {
            const int yy = y + dy, xx = x + dx;
            if (yy >= 0 && yy < h && xx >= 0 && xx < w)
                if (maske[yy * w + xx] != 0) {
                    const int d = dy * dy + dx * dx;
                    if (d < beste) {
                        beste = d;
                        by = yy;
                        bx = xx;
                    }
                }
        }
    if (by >= 0) {
        aus_maske[i] = 1;
        for (int k = 0; k < 3; ++k)
            aus[3 * i + k] = bild[3 * (by * w + bx) + k];
    }
}

__device__ __forceinline__ u8 hb_byte(float x) { return (u8)wclamp(x * 255.0f + 0.5f, 0.0f, 255.0f); }

__global__ void k_holen(int n, const int* idx, const int* face_flach, const float* hu_flach, const float* hv_flach, int* face, float* hu, float* hv)
{
    HB_FADEN(n)
    const int t = idx[i];
    face[i] = face_flach[t];
    hu[i] = hu_flach[t];
    hv[i] = hv_flach[t];
}

__global__ void k_schreiben_farbe(int n, const int* idx, const float* linear, u8* aus)
{
    HB_FADEN(n)
    const int t = idx[i];
    for (int k = 0; k < 3; ++k)
        aus[3 * t + k] = hb_byte(color_linear_to_srgb(linear[3 * i + k]));
}

__global__ void k_schreiben_rauheit(int n, const int* idx, const float* wert, u8* aus)
{
    HB_FADEN(n)
    const int t = idx[i];
    for (int k = 0; k < 3; ++k)
        aus[3 * t + k] = hb_byte(wert[3 * i + k]);
}

// `RE_bake_normal_world_to_tangent`: Normale (geglättet, nicht normiert), Tangente (interpoliert), Basis (T, B, N) invertieren, normieren, n/2 + 0,5 + 1e-5
__global__ void k_schreiben_normale(int n, const int* idx, const float* n_welt, const int* f_ids, const float* f_bary, const int* f_tri, const float* f_nor,
                                    const float* f_tang, u8* aus)
{
    HB_FADEN(n)
    const int t = idx[i];
    const int tri = f_ids[t];
    const int j0 = f_tri[3 * tri], j1 = f_tri[3 * tri + 1], j2 = f_tri[3 * tri + 2];
    const float w1 = f_bary[2 * t], w2 = f_bary[2 * t + 1];
    const float w0 = 1.0f - w1 - w2;
    const v3 nor = add(add(mul(lies3(f_nor, j0), w0), mul(lies3(f_nor, j1), w1)), mul(lies3(f_nor, j2), w2));
    const v4 t0 = lies4(f_tang, 3LL * tri), t1 = lies4(f_tang, 3LL * tri + 1), t2 = lies4(f_tang, 3LL * tri + 2);
    const v3 tang = add(add(mul(V3(t0.c[0], t0.c[1], t0.c[2]), w0), mul(V3(t1.c[0], t1.c[1], t1.c[2]), w1)), mul(V3(t2.c[0], t2.c[1], t2.c[2]), w2));
    float vorz = 1.0f;
    if (t0.c[3] * w0 + t1.c[3] * w1 + t2.c[3] * w2 < 0.0f)
        vorz = -1.0f;
    const v3 bin = mul(cross(nor, tang), vorz);
    const m33 m = M33(tang.c[0], bin.c[0], nor.c[0], tang.c[1], bin.c[1], nor.c[1], tang.c[2], bin.c[2], nor.c[2]);
    const v3 x = normalize(mul(inverse(m), lies3(n_welt, i)));
    for (int c = 0; c < 3; ++c)
        aus[3 * t + c] = hb_byte(x.c[c] / 2.0f + 0.5f + 1.0e-5f);
}

// Normal-Pass bei kleinem Alpha: der Nullvektor, wenn saturate(alpha) < schwelle
__global__ void k_nullen(int n, const float* alpha, float schwelle, const float* welt, float* aus)
{
    HB_FADEN(n)
    const float a = wclamp(alpha[i], 0.0f, 1.0f);
    schreib3(aus, i, a < schwelle ? null3() : lies3(welt, i));
}

// greift die Glanz-Normalen-Korrektur (Spiegelung unter der Fläche)?
__global__ void k_korrektur_noetig(int n, const float* nf, const float* ngf, const float* n_glatt, const int* rueck, int* aus)
{
    HB_FADEN(n)
    v3 wi = lies3(n_glatt, i);
    if (rueck[i] != 0)
        wi = neg(wi);
    v3 nn = safe_normalize3(lies3(nf, i));
    if (null(nn))
        nn = lies3(n_glatt, i);
    const v3 g = lies3(ngf, i);
    if (nn.c[0] == g.c[0] && nn.c[1] == g.c[1] && nn.c[2] == g.c[2]) {
        aus[i] = 0;
        return;
    }
    const v3 r = sub(mul(2.0f * dot(nn, wi), nn), wi);
    const float iz = dot(wi, g);
    const float schwelle = fminf(0.9f * iz, 0.01f);
    aus[i] = dot(g, r) >= schwelle ? 0 : 1;
}

__global__ void k_rueckdrehen(int n, const float* nf, const int* rueck, float* aus)
{
    HB_FADEN(n)
    const v3 v = lies3(nf, i);
    schreib3(aus, i, rueck[i] != 0 ? neg(v) : v);
}

// Umwandlungen der Buchsenarten (convert.h): Zahl → Vektor, Farbe → Zahl (dot mit den Leuchtdichte-Gewichten), Vektor → Zahl (Mittel)
__global__ void k_f_zu_v(int n, const float* a, float* aus)
{
    HB_FADEN(n)
    schreib3(aus, i, V3(a[i], a[i], a[i]));
}
__global__ void k_c_zu_f(int n, const float* a, float y0, float y1, float y2, float* aus)
{
    HB_FADEN(n)
    aus[i] = dot(lies3(a, i), V3(y0, y1, y2));
}
__global__ void k_v_zu_f(int n, const float* a, float* aus)
{
    HB_FADEN(n)
    aus[i] = average3(lies3(a, i));
}

// `packed_normal` (types_normal.h): oktaedrisch in 2 × 16 Bit gepackt und wieder entpackt
__device__ v3 packed_normal(v3 n)
{
    const float mu = 65535.0f;
    const float hmu = mu / 2.0f;
    const float inv_l1 = 1.0f / (fabsf(n.c[0]) + fabsf(n.c[1]) + fabsf(n.c[2]) + 1.0e-6f);
    float vx = n.c[0] * inv_l1, vy = n.c[1] * inv_l1;
    float sx = 1.0f, sy = 1.0f;
    if (n.c[0] < 0.0f)
        sx = -1.0f;
    if (n.c[1] < 0.0f)
        sy = -1.0f;
    const float wrapx = (1.0f - fabsf(vy)) * sx;
    const float wrapy = (1.0f - fabsf(vx)) * sy;
    if (n.c[2] < 0.0f) {
        vx = wrapx;
        vy = wrapy;
    }
    const float dx = (float)(int)wclamp(vx * hmu + (hmu + 0.5f), 0.0f, mu);
    const float dy = (float)(int)wclamp(vy * hmu + (hmu + 0.5f), 0.0f, mu);
    const float inv_hmu = 2.0f / mu;
    float nx = dx * inv_hmu - 1.0f, ny = dy * inv_hmu - 1.0f;
    const float nz = 1.0f - fabsf(nx) - fabsf(ny);
    const float t = fmaxf(wneg(nz), 0.0f);
    if (wneg(nx) < 0.0f)
        nx = nx - t;
    else
        nx = nx + t;
    if (wneg(ny) < 0.0f)
        ny = ny - t;
    else
        ny = ny + t;
    return normalize(V3(nx, ny, nz));
}
__global__ void k_packen(int n, const float* roh, float* aus)
{
    HB_FADEN(n)
    schreib3(aus, i, packed_normal(lies3(roh, i)));
}

HB_EXPORT hb_rastern(void* s, int nt, const float* uv, const int* tri_uv, int px, float ox, float oy, int* ids, float* bary)
{
    if (nt > 0)
        k_rastern<<<HB_GITTER(nt)>>>(nt, uv, tri_uv, px, ox, oy, ids, bary);
    HB_ENDE;
}
HB_EXPORT hb_schiessen(void* s, int nn, const void* lo, const void* hi, const int* wurzel, const float* qp, const int* qf, const float* pos, const float* nor,
                       const int* tri_v, const int* ids, const float* bary, float auszug, float laenge, int* face, float* hu, float* hv)
{
    fl::Netzbaum b;
    b.lowers = (const fl::Knoten*)lo;
    b.uppers = (const fl::Knoten*)hi;
    b.root = wurzel;
    b.points = qp;
    b.indices = qf;
    if (nn > 0)
        k_schiessen<<<HB_GITTER(nn)>>>(nn, b, pos, nor, tri_v, ids, bary, auszug, laenge, face, hu, hv);
    HB_ENDE;
}
HB_EXPORT hb_erweitern(void* s, int h, int w, const u8* bild, const u8* maske, const u8* nah, int radius, u8* aus, u8* aus_maske)
{
    if (h * w > 0)
        k_erweitern<<<HB_GITTER(h * w)>>>(h, w, bild, maske, nah, radius, aus, aus_maske);
    HB_ENDE;
}
HB_EXPORT hb_holen(void* s, int n, const int* idx, const int* ff, const float* hf, const float* vf, int* face, float* hu, float* hv)
{
    if (n > 0)
        k_holen<<<HB_GITTER(n)>>>(n, idx, ff, hf, vf, face, hu, hv);
    HB_ENDE;
}
HB_EXPORT hb_schreiben_farbe(void* s, int n, const int* idx, const float* linear, u8* aus)
{
    if (n > 0)
        k_schreiben_farbe<<<HB_GITTER(n)>>>(n, idx, linear, aus);
    HB_ENDE;
}
HB_EXPORT hb_schreiben_rauheit(void* s, int n, const int* idx, const float* wert, u8* aus)
{
    if (n > 0)
        k_schreiben_rauheit<<<HB_GITTER(n)>>>(n, idx, wert, aus);
    HB_ENDE;
}
HB_EXPORT hb_schreiben_normale(void* s, int n, const int* idx, const float* n_welt, const int* f_ids, const float* f_bary, const int* f_tri, const float* f_nor,
                               const float* f_tang, u8* aus)
{
    if (n > 0)
        k_schreiben_normale<<<HB_GITTER(n)>>>(n, idx, n_welt, f_ids, f_bary, f_tri, f_nor, f_tang, aus);
    HB_ENDE;
}
HB_EXPORT hb_nullen(void* s, int n, const float* alpha, float schwelle, const float* welt, float* aus)
{
    if (n > 0)
        k_nullen<<<HB_GITTER(n)>>>(n, alpha, schwelle, welt, aus);
    HB_ENDE;
}
HB_EXPORT hb_korrektur_noetig(void* s, int n, const float* nf, const float* ng, const float* n_glatt, const int* rueck, int* aus)
{
    if (n > 0)
        k_korrektur_noetig<<<HB_GITTER(n)>>>(n, nf, ng, n_glatt, rueck, aus);
    HB_ENDE;
}
HB_EXPORT hb_rueckdrehen(void* s, int n, const float* nf, const int* rueck, float* aus)
{
    if (n > 0)
        k_rueckdrehen<<<HB_GITTER(n)>>>(n, nf, rueck, aus);
    HB_ENDE;
}
HB_EXPORT hb_f_zu_v(void* s, int n, const float* a, float* aus)
{
    if (n > 0)
        k_f_zu_v<<<HB_GITTER(n)>>>(n, a, aus);
    HB_ENDE;
}
HB_EXPORT hb_c_zu_f(void* s, int n, const float* a, float y0, float y1, float y2, float* aus)
{
    if (n > 0)
        k_c_zu_f<<<HB_GITTER(n)>>>(n, a, y0, y1, y2, aus);
    HB_ENDE;
}
HB_EXPORT hb_v_zu_f(void* s, int n, const float* a, float* aus)
{
    if (n > 0)
        k_v_zu_f<<<HB_GITTER(n)>>>(n, a, aus);
    HB_ENDE;
}
HB_EXPORT hb_packen(void* s, int n, const float* roh, float* aus)
{
    if (n > 0)
        k_packen<<<HB_GITTER(n)>>>(n, roh, aus);
    HB_ENDE;
}

}  // namespace hb
