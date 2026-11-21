// hautkontextkern.cuh — die Kerne des Schattierungskontexts (`ShaderData`; bis 21.11.2026 Warp: `graph/hautkontextkernel.py`, dort die Quellen
// init_from_bake.h, triangle.h, differential.h, bake.cc). Schwerpunktkoordinaten: u, v = Gewichte der Ecken 1 und 2 (P = (1−u−v)·P0 + u·P1 + v·P2).
#pragma once
#include "hautfunktionen.cuh"

namespace hb {

// Ng, N, dPdu, dPdv und Rückseite je Treffer (`triangle_shader_setup` + Rückseitenprüfung, wi = N)
__global__ void k_geometrie(int n, const int* face, const float* hu, const float* hv, const int* tri, const float* pos, const float* ecke_n, const int* glatt,
                            float* ng_aus, float* n_aus, float* dpdu_aus, float* dpdv_aus, int* rueck_aus)
{
    HB_FADEN(n)
    const int f = face[i];
    const v3 p0 = lies3(pos, tri[3 * f]), p1 = lies3(pos, tri[3 * f + 1]), p2 = lies3(pos, tri[3 * f + 2]);
    const float u = hu[i], v = hv[i];
    v3 ng = normalize(cross(sub(p1, p0), sub(p2, p0)));
    v3 nn = ng;
    if (glatt[f] != 0) {
        v3 s = safe_normalize3(add(add(mul(1.0f - u - v, lies3(ecke_n, 3LL * f)), mul(u, lies3(ecke_n, 3LL * f + 1))), mul(v, lies3(ecke_n, 3LL * f + 2))));
        if (null(s))
            s = ng;
        nn = s;
    }
    v3 dpdu = sub(p1, p0), dpdv = sub(p2, p0);
    int rueck = 0;
    if (dot(ng, nn) < 0.0f) {
        ng = neg(ng);
        nn = neg(nn);
        dpdu = neg(dpdu);
        dpdv = neg(dpdv);
        rueck = 1;
    }
    schreib3(ng_aus, i, ng);
    schreib3(n_aus, i, nn);
    schreib3(dpdu_aus, i, dpdu);
    schreib3(dpdv_aus, i, dpdv);
    rueck_aus[i] = rueck;
}

// die gepackte Pixel-Ableitung dP nach `cast_ray_highpoly` (bake.cc)
__global__ void k_differenzial(int n, const int* idx, const int* face, const int* f_ids, const float* f_bary, const float* f_pos, const float* f_nor,
                               const int* f_tri, const float* f_uv, int px, const float* q_pos, const int* q_tri, float* dp_aus)
{
    HB_FADEN(n)
    const int texel = idx[i];
    const int t = f_ids[texel];
    const int j0 = f_tri[3 * t], j1 = f_tri[3 * t + 1], j2 = f_tri[3 * t + 2];
    const float w1 = f_bary[2 * texel], w2 = f_bary[2 * texel + 1];
    const float w0 = 1.0f - w1 - w2;
    const float c = (float)px;
    const v2 a = mul(lies2(f_uv, 3LL * t), c), b = mul(lies2(f_uv, 3LL * t + 1), c), d = mul(lies2(f_uv, 3LL * t + 2), c);
    float bruch = (b.c[0] - a.c[0]) * (d.c[1] - a.c[1]) - (d.c[0] - a.c[0]) * (b.c[1] - a.c[1]);
    float du_dx = 0.0f, dv_dx = 0.0f, du_dy = 0.0f, dv_dy = 0.0f;
    if (fabsf(bruch) > 1.1920929e-07f) {
        bruch = 1.0f / bruch;
        du_dx = (b.c[1] - d.c[1]) * bruch;
        dv_dx = (d.c[1] - a.c[1]) * bruch;
        du_dy = (d.c[0] - b.c[0]) * bruch;
        dv_dy = (a.c[0] - d.c[0]) * bruch;
    }
    const v3 duco = sub(lies3(f_pos, j0), lies3(f_pos, j2));
    const v3 dvco = sub(lies3(f_pos, j1), lies3(f_pos, j2));
    v3 dxco = add(mul(duco, du_dx), mul(dvco, dv_dx));
    v3 dyco = add(mul(duco, du_dy), mul(dvco, dv_dy));
    const v3 r = neg(normalize(add(add(mul(lies3(f_nor, j0), w0), mul(lies3(f_nor, j1), w1)), mul(lies3(f_nor, j2), w2))));
    const int q = face[i];
    const v3 q0 = lies3(q_pos, q_tri[3 * q]), q1 = lies3(q_pos, q_tri[3 * q + 1]), q2 = lies3(q_pos, q_tri[3 * q + 2]);
    const v3 nh = normalize(cross(sub(q1, q0), sub(q2, q0)));
    const v3 tmp = mul(r, 1.0f / dot(r, nh));
    dxco = sub(dxco, mul(tmp, dot(dxco, nh)));
    dyco = sub(dyco, mul(tmp, dot(dyco, nh)));
    dp_aus[i] = 0.5f * (length(dxco) + length(dyco));
}

// `differential_from_compact(Ng, dP)` und `differential_dudv`
__global__ void k_differenzial_uv(int n, const float* ngf, const float* dpduf, const float* dpdvf, const float* dp, float* dpx_aus, float* dpy_aus,
                                  float* dudx_aus, float* dvdx_aus, float* dudy_aus, float* dvdy_aus)
{
    HB_FADEN(n)
    const v3 nn = lies3(ngf, i);
    const v3 a = make_orthonormals_a(nn);
    const v3 b = cross(nn, a);
    const v3 pdx = mul(a, dp[i]), pdy = mul(b, dp[i]);
    schreib3(dpx_aus, i, pdx);
    schreib3(dpy_aus, i, pdy);
    const v3 dpdu = lies3(dpduf, i), dpdv = lies3(dpdvf, i);
    const float xn = fabsf(nn.c[0]), yn = fabsf(nn.c[1]), zn = fabsf(nn.c[2]);
    v2 u2 = V2(dpdu.c[0], dpdu.c[1]), v2_ = V2(dpdv.c[0], dpdv.c[1]), px2 = V2(pdx.c[0], pdx.c[1]), py2 = V2(pdy.c[0], pdy.c[1]);
    if (zn < xn || zn < yn) {
        if (yn < xn || yn < zn) {
            u2 = V2(dpdu.c[1], u2.c[1]);
            v2_ = V2(dpdv.c[1], v2_.c[1]);
            px2 = V2(pdx.c[1], px2.c[1]);
            py2 = V2(pdy.c[1], py2.c[1]);
        }
        u2 = V2(u2.c[0], dpdu.c[2]);
        v2_ = V2(v2_.c[0], dpdv.c[2]);
        px2 = V2(px2.c[0], pdx.c[2]);
        py2 = V2(py2.c[0], pdy.c[2]);
    }
    float det = u2.c[0] * v2_.c[1] - v2_.c[0] * u2.c[1];
    if (det != 0.0f)
        det = 1.0f / det;
    dudx_aus[i] = (px2.c[0] * v2_.c[1] - px2.c[1] * v2_.c[0]) * det;
    dvdx_aus[i] = (px2.c[1] * u2.c[0] - px2.c[0] * u2.c[1]) * det;
    dudy_aus[i] = (py2.c[0] * v2_.c[1] - py2.c[1] * v2_.c[0]) * det;
    dvdy_aus[i] = (py2.c[1] * u2.c[0] - py2.c[0] * u2.c[1]) * det;
}

// ein Ecken-Attribut (UV: 2 Komponenten, Farbe: 4) am Treffer samt Ableitungen (`triangle_attribute` mit dual2/dual4)
template <int N, typename V>
__device__ __forceinline__ void attribut(int i, const int* face, const float* hu, const float* hv, const float* ecken, const float* dudx, const float* dvdx,
                                         const float* dudy, const float* dvdy, float* val, float* dx, float* dy)
{
    const long long f = face[i];
    V f0, f1, f2;
    for (int k = 0; k < N; ++k) {
        f0.c[k] = ecken[(3 * f) * N + k];
        f1.c[k] = ecken[(3 * f + 1) * N + k];
        f2.c[k] = ecken[(3 * f + 2) * N + k];
    }
    const float u = hu[i], v = hv[i];
    const V w = add(add(mul(1.0f - u - v, f0), mul(u, f1)), mul(v, f2));
    const V x = sub(add(mul(dudx[i], f1), mul(dvdx[i], f2)), mul(dudx[i] + dvdx[i], f0));
    const V y = sub(add(mul(dudy[i], f1), mul(dvdy[i], f2)), mul(dudy[i] + dvdy[i], f0));
    for (int k = 0; k < N; ++k) {
        val[(long long)i * N + k] = w.c[k];
        dx[(long long)i * N + k] = x.c[k];
        dy[(long long)i * N + k] = y.c[k];
    }
}
__global__ void k_attribut2(int n, const int* face, const float* hu, const float* hv, const float* ecken, const float* dudx, const float* dvdx, const float* dudy,
                            const float* dvdy, float* val, float* dx, float* dy)
{
    HB_FADEN(n)
    attribut<2, v2>(i, face, hu, hv, ecken, dudx, dvdx, dudy, dvdy, val, dx, dy);
}
__global__ void k_attribut4(int n, const int* face, const float* hu, const float* hv, const float* ecken, const float* dudx, const float* dvdx, const float* dudy,
                            const float* dvdy, float* val, float* dx, float* dy)
{
    HB_FADEN(n)
    attribut<4, v4>(i, face, hu, hv, ecken, dudx, dvdx, dudy, dvdy, val, dx, dy);
}

// `triangle_smooth_normal_unnormalized_object_space` (normiert; Null → Ng)
__global__ void k_normale_unnormiert(int n, const int* face, const float* hu, const float* hv, const float* ecken, const int* glatt, const float* ng, float* aus)
{
    HB_FADEN(n)
    const long long f = face[i];
    const float u = hu[i], v = hv[i];
    v3 s = safe_normalize3(add(add(mul(1.0f - u - v, lies3(ecken, 3 * f)), mul(u, lies3(ecken, 3 * f + 1))), mul(v, lies3(ecken, 3 * f + 2))));
    if (null(s))
        s = lies3(ng, i);
    schreib3(aus, i, s);
}

__global__ void k_glatt_je_treffer(int n, const int* face, const int* glatt, int* aus)
{
    HB_FADEN(n)
    aus[i] = glatt[face[i]];
}

// Tangente und Vorzeichen der Bitangente am Treffer, ohne Normierung
__global__ void k_tangente_interpoliert(int n, const int* face, const float* hu, const float* hv, const float* tang, const float* vorz, float* t_aus, float* s_aus)
{
    HB_FADEN(n)
    const long long f = face[i];
    const float u = hu[i], v = hv[i];
    const float w = 1.0f - u - v;
    schreib3(t_aus, i, add(add(mul(w, lies3(tang, 3 * f)), mul(u, lies3(tang, 3 * f + 1))), mul(v, lies3(tang, 3 * f + 2))));
    s_aus[i] = w * vorz[3 * f] + u * vorz[3 * f + 1] + v * vorz[3 * f + 2];
}

// ziel[idx[i]] = quelle[i] — die Ergebnisse eines Stapels ins Bild (3 Komponenten bzw. eine)
__global__ void k_verteilen_vec3(int n, const int* idx, const float* quelle, float* ziel)
{
    HB_FADEN(n)
    schreib3(ziel, idx[i], lies3(quelle, i));
}

HB_EXPORT hb_geometrie(void* s, int n, const int* face, const float* hu, const float* hv, const int* tri, const float* pos, const float* ecke_n, const int* glatt,
                       float* ng, float* nn, float* dpdu, float* dpdv, int* rueck)
{
    if (n > 0)
        k_geometrie<<<HB_GITTER(n)>>>(n, face, hu, hv, tri, pos, ecke_n, glatt, ng, nn, dpdu, dpdv, rueck);
    HB_ENDE;
}
HB_EXPORT hb_differenzial(void* s, int n, const int* idx, const int* face, const int* f_ids, const float* f_bary, const float* f_pos, const float* f_nor,
                          const int* f_tri, const float* f_uv, int px, const float* q_pos, const int* q_tri, float* dp)
{
    if (n > 0)
        k_differenzial<<<HB_GITTER(n)>>>(n, idx, face, f_ids, f_bary, f_pos, f_nor, f_tri, f_uv, px, q_pos, q_tri, dp);
    HB_ENDE;
}
HB_EXPORT hb_differenzial_uv(void* s, int n, const float* ng, const float* dpdu, const float* dpdv, const float* dp, float* dpx, float* dpy, float* dudx,
                             float* dvdx, float* dudy, float* dvdy)
{
    if (n > 0)
        k_differenzial_uv<<<HB_GITTER(n)>>>(n, ng, dpdu, dpdv, dp, dpx, dpy, dudx, dvdx, dudy, dvdy);
    HB_ENDE;
}
HB_EXPORT hb_attribut2(void* s, int n, const int* face, const float* hu, const float* hv, const float* ecken, const float* dudx, const float* dvdx,
                       const float* dudy, const float* dvdy, float* val, float* dx, float* dy)
{
    if (n > 0)
        k_attribut2<<<HB_GITTER(n)>>>(n, face, hu, hv, ecken, dudx, dvdx, dudy, dvdy, val, dx, dy);
    HB_ENDE;
}
HB_EXPORT hb_attribut4(void* s, int n, const int* face, const float* hu, const float* hv, const float* ecken, const float* dudx, const float* dvdx,
                       const float* dudy, const float* dvdy, float* val, float* dx, float* dy)
{
    if (n > 0)
        k_attribut4<<<HB_GITTER(n)>>>(n, face, hu, hv, ecken, dudx, dvdx, dudy, dvdy, val, dx, dy);
    HB_ENDE;
}
HB_EXPORT hb_normale_unnormiert(void* s, int n, const int* face, const float* hu, const float* hv, const float* ecken, const int* glatt, const float* ng, float* aus)
{
    if (n > 0)
        k_normale_unnormiert<<<HB_GITTER(n)>>>(n, face, hu, hv, ecken, glatt, ng, aus);
    HB_ENDE;
}
HB_EXPORT hb_glatt_je_treffer(void* s, int n, const int* face, const int* glatt, int* aus)
{
    if (n > 0)
        k_glatt_je_treffer<<<HB_GITTER(n)>>>(n, face, glatt, aus);
    HB_ENDE;
}
HB_EXPORT hb_tangente_interpoliert(void* s, int n, const int* face, const float* hu, const float* hv, const float* tang, const float* vorz, float* t_aus,
                                   float* s_aus)
{
    if (n > 0)
        k_tangente_interpoliert<<<HB_GITTER(n)>>>(n, face, hu, hv, tang, vorz, t_aus, s_aus);
    HB_ENDE;
}
HB_EXPORT hb_verteilen_vec3(void* s, int n, const int* idx, const float* quelle, float* ziel)
{
    if (n > 0)
        k_verteilen_vec3<<<HB_GITTER(n)>>>(n, idx, quelle, ziel);
    HB_ENDE;
}

}  // namespace hb
