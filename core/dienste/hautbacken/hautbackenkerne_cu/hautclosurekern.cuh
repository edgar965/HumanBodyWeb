// hautclosurekern.cuh — `normale_mittel`: die gebackene Normale `normalize(Σ sc->N · |average(sc->weight)|)` je Texel (bis 21.11.2026 Warp-Kern in
// `closure/hautclosurekernel.py`, dort die Herleitung je Schicht: Sheen → Lack → Metall → Transmission → Glanz → Untergrundstreuung/Diffus).
#pragma once
#include "hautclosure.cuh"

namespace hb {

__global__ void k_normale_mittel(int n_ges, const float* n_in, const float* ng_a, const float* n_glatt, const int* rueck, const float* basis, const float* metallisch,
                                 const float* rauheit, const float* ior_a, const float* spec_stufe, const float* spec_tint, const float* aniso, const float* sheen_g,
                                 const float* sheen_r, const float* sheen_t, const float* coat_g, const float* coat_r, const float* coat_i, const float* coat_t,
                                 const float* coat_n, int coat_n_verbunden, const float* trans_g, const float* sss_g, const float* sss_radius,
                                 const float* sss_skala, int multi_ggx, int tang_gueltig, int korrektur_an, const float* ggx_E, const float* ggx_Eavg,
                                 const float* ggx_s_ior, const float* sheen_ltc, const float* glass_E, const float* glass_Eavg, const float* glass_inv_E,
                                 const float* glass_inv_Eavg, float* aus)
{
    HB_FADEN(n_ges)
    const v3 ng = lies3(ng_a, i);
    const v3 nsd = lies3(n_glatt, i);
    v3 wi = nsd;
    if (rueck[i] != 0)
        wi = neg(nsd);
    v3 n = safe_normalize3(lies3(n_in, i));
    if (null(n))
        n = nsd;
    v3 gueltig = n;
    if (korrektur_an != 0)
        gueltig = gueltige_normale(ng, wi, n);
    const v3 eins = V3(1.0f, 1.0f, 1.0f);
    v3 schicht = eins;
    v3 summe = null3();
    v3 nc = nsd;
    if (coat_n_verbunden != 0) {
        nc = safe_normalize3(lies3(coat_n, i));
        if (null(nc))
            nc = nsd;
    }
    v3 lack_normale = nc;
    if (korrektur_an != 0)
        lack_normale = gueltige_normale(ng, wi, nc);
    // ---- Sheen
    const float sheen_w = fmaxf(sheen_g[i], 0.0f);
    const float coat_w = fmaxf(coat_g[i], 0.0f);
    if (sheen_w > CUTOFF) {
        v3 w_s = null_hoch(mul(sheen_w, cw_mul(null_hoch(lies3(sheen_t, i)), schicht)));
        if (mittel3(w_s) >= CUTOFF) {
            const float cm = saturatef(coat_g[i]);
            const v3 n_s = safe_normalize3(add(n, mul(cm, sub(nc, n))));
            const float rau = wclamp(saturatef(sheen_r[i]), 1.0e-3f, 1.0f);
            const float cos_ni = dot(n_s, wi);
            const float a = lookup_table_read_2D(sheen_ltc, cos_ni, rau, 0, 32, 32);
            const float albedo = lookup_table_read_2D(sheen_ltc, cos_ni, rau, 2 * 32 * 32, 32, 32);
            if (!(fabsf(a) < 1.0e-5f || albedo < 1.0e-5f)) {
                w_s = mul(w_s, albedo);
                summe = add(summe, mul(n_s, fabsf(mittel3(w_s))));
                schicht = closure_layering_weight(w_s, schicht);
            }
        }
    }
    // ---- Lack (Coat)
    if (coat_w > CUTOFF) {
        const float c_rau = saturatef(coat_r[i]);
        const float c_ior = fmaxf(coat_i[i], 1.0f);
        v3 w_c = null_hoch(mul(coat_w, schicht));
        if (mittel3(w_c) >= CUTOFF) {
            const float alpha = saturatef(c_rau * c_rau);
            const float rau4 = sqrtf(alpha);
            const float mu = dot(wi, lack_normale);
            const float fss = fresnel_dielectric_Fss(c_ior);
            w_c = cw_mul(w_c, ggx_darkening(ggx_E, ggx_Eavg, mu, rau4, V3(fss, fss, fss)));
            summe = add(summe, mul(lack_normale, fabsf(mittel3(w_c))));
            float f = 0.0f;
            if (c_ior > 1.0f) {
                const float s_c = schlick_s_ior(ggx_s_ior, rau4, mu, c_ior);
                f = F0_from_ior(c_ior) * (1.0f - s_c) + s_c;
            }
            schicht = closure_layering_weight(mul(w_c, f), schicht);
        }
        const v3 tint = null_hoch(lies3(coat_t, i));
        if (!(tint.c[0] == 1.0f && tint.c[1] == 1.0f && tint.c[2] == 1.0f)) {
            const float cos_ni = dot(wi, lack_normale);
            const float cos_nt = sqrtf(1.0f - (1.0f / c_ior) * (1.0f / c_ior) * (1.0f - cos_ni * cos_ni));
            const float tiefe = 1.0f / cos_nt;
            const v3 potenz = V3(powf(tint.c[0], tiefe), powf(tint.c[1], tiefe), powf(tint.c[2], tiefe));
            schicht = cw_mul(schicht, add(mul(eins, 1.0f - coat_w), mul(potenz, coat_w)));
        }
    }
    // ---- Grundwerte
    const v3 farbe = null_hoch(lies3(basis, i));
    const v3 farbe_k = V3(fminf(farbe.c[0], 1.0f), fminf(farbe.c[1], 1.0f), fminf(farbe.c[2], 1.0f));
    const float ior = fmaxf(ior_a[i], 1.0e-5f);
    const float rau = saturatef(rauheit[i]);
    float alpha_x = rau * rau, alpha_y = rau * rau;
    const float an = saturatef(aniso[i]);
    if (an > 0.0f && tang_gueltig != 0) {
        const float aspekt = sqrtf(1.0f - an * 0.9f);
        alpha_x = alpha_x / aspekt;
        alpha_y = alpha_y * aspekt;
    }
    alpha_x = saturatef(alpha_x);
    alpha_y = saturatef(alpha_y);
    const float rau4 = sqrtf(sqrtf(alpha_x * alpha_y));
    const float mu = dot(wi, gueltig);
    // ---- Metall (F82-Tint)
    const float met = saturatef(metallisch[i]);
    if (met > CUTOFF) {
        v3 w_m = null_hoch(mul(met, schicht));
        if (mittel3(w_m) >= CUTOFF) {
            if (multi_ggx != 0) {
                v3 f82 = null_hoch(lies3(spec_tint, i));
                f82 = V3(fminf(f82.c[0], 1.0f), fminf(f82.c[1], 1.0f), fminf(f82.c[2], 1.0f));
                v3 b = null3();
                if (!(f82.c[0] == 1.0f && f82.c[1] == 1.0f && f82.c[2] == 1.0f))
                    b = fresnel_f82tint_B(farbe_k, f82);
                w_m = cw_mul(w_m, ggx_darkening(ggx_E, ggx_Eavg, mu, rau4, fresnel_f82_Fss(farbe_k, b)));
            }
            summe = add(summe, mul(gueltig, fabsf(mittel3(w_m))));
        }
        schicht = mul(schicht, 1.0f - met);
    }
    // ---- Transmission (Glas, nicht dünnwandig)
    const float tw = saturatef(trans_g[i]);
    if (tw > CUTOFF) {
        v3 w_t = null_hoch(mul(tw, schicht));
        if (mittel3(w_t) >= CUTOFF) {
            if (multi_ggx != 0) {
                const float alpha_g = saturatef(rau * rau);
                const float rau_g = sqrtf(sqrtf(alpha_g * alpha_g));
                float ior_g = ior;
                if (rueck[i] != 0)
                    ior_g = 1.0f / ior;
                const v3 durchlass = V3(sqrtf(farbe_k.c[0]), sqrtf(farbe_k.c[1]), sqrtf(farbe_k.c[2]));
                v3 fss_g = durchlass;
                if (null(durchlass)) {
                    const float s_g = saturatef(inverse_lerp(F0_from_ior(ior_g), 1.0f, fresnel_dielectric_Fss(ior_g)));
                    v3 f0g = mul(F0_from_ior(ior), null_hoch(lies3(spec_tint, i)));
                    f0g = V3(saturatef(f0g.c[0]), saturatef(f0g.c[1]), saturatef(f0g.c[2]));
                    fss_g = add(mul(f0g, 1.0f - s_g), mul(eins, s_g));
                }
                w_t = cw_mul(w_t, glass_darkening(glass_E, glass_Eavg, glass_inv_E, glass_inv_Eavg, mu, rau_g, ior_g, fss_g));
            }
            summe = add(summe, mul(gueltig, fabsf(mittel3(w_t))));
        }
        schicht = mul(schicht, 1.0f - tw);
    }
    // ---- Glanz (verallgemeinertes Schlick, Exponent −eta)
    const float stufe = fmaxf(spec_stufe[i], 0.0f);
    float eta = ior;
    float f0 = F0_from_ior(eta);
    if (stufe != 0.5f) {
        f0 = f0 * 2.0f * stufe;
        eta = ior_from_F0(f0);
        if (ior < 1.0f)
            eta = 1.0f / eta;
    }
    if (eta != 1.0f) {
        v3 w_g = null_hoch(schicht);
        if (mittel3(w_g) >= CUTOFF) {
            const v3 tint = null_hoch(lies3(spec_tint, i));
            v3 f0v = mul(f0, tint);
            f0v = V3(saturatef(f0v.c[0]), saturatef(f0v.c[1]), saturatef(f0v.c[2]));
            if (multi_ggx != 0) {
                const float s = saturatef(inverse_lerp(F0_from_ior(eta), 1.0f, fresnel_dielectric_Fss(eta)));
                w_g = cw_mul(w_g, ggx_darkening(ggx_E, ggx_Eavg, mu, rau4, add(mul(f0v, 1.0f - s), mul(eins, s))));
            }
            summe = add(summe, mul(gueltig, fabsf(mittel3(w_g))));
            const float sl = schlick_s_ior(ggx_s_ior, rau4, mu, eta);
            schicht = closure_layering_weight(cw_mul(w_g, add(mul(f0v, 1.0f - sl), mul(eins, sl))), schicht);
        }
    }
    // ---- Untergrundstreuung und Diffus
    const float sss = saturatef(sss_g[i]);
    if (sss > CUTOFF) {
        const v3 gew = null_hoch(mul(cw_mul(farbe_k, schicht), sss));
        if (mittel3(gew) >= CUTOFF) {
            const v3 radius = null_hoch(mul(lies3(sss_radius, i), sss_skala[i]));
            v3 diffus = null3();
            v3 streu = gew;
            int kanaele = 3;
            for (int k = 0; k < 3; ++k) {
                if (radius.c[k] < BSSRDF_MIN_RADIUS) {
                    diffus.c[k] = gew.c[k];
                    streu.c[k] = 0.0f;
                    kanaele = kanaele - 1;
                }
            }
            if (kanaele < 3 && mittel3(diffus) >= CUTOFF)
                summe = add(summe, mul(gueltig, fabsf(mittel3(diffus))));
            if (kanaele > 0)
                summe = add(summe, mul(gueltig, fabsf(mittel3(streu))));
        }
    }
    const v3 w_d = null_hoch(mul(cw_mul(farbe, schicht), 1.0f - sss));
    if (mittel3(w_d) >= CUTOFF)
        summe = add(summe, mul(n, fabsf(mittel3(w_d))));
    if (null(summe))
        schreib3(aus, i, nsd);
    else
        schreib3(aus, i, normalize(summe));
}

HB_EXPORT hb_normale_mittel(void* s, int n, const float* n_in, const float* ng_a, const float* n_glatt, const int* rueck, const float* basis,
                            const float* metallisch, const float* rauheit, const float* ior_a, const float* spec_stufe, const float* spec_tint, const float* aniso,
                            const float* sheen_g, const float* sheen_r, const float* sheen_t, const float* coat_g, const float* coat_r, const float* coat_i,
                            const float* coat_t, const float* coat_n, int coat_n_verbunden, const float* trans_g, const float* sss_g, const float* sss_radius,
                            const float* sss_skala, int multi_ggx, int tang_gueltig, int korrektur_an, const float* ggx_E, const float* ggx_Eavg,
                            const float* ggx_s_ior, const float* sheen_ltc, const float* glass_E, const float* glass_Eavg, const float* glass_inv_E,
                            const float* glass_inv_Eavg, float* aus)
{
    if (n > 0)
        k_normale_mittel<<<HB_GITTER(n)>>>(n, n_in, ng_a, n_glatt, rueck, basis, metallisch, rauheit, ior_a, spec_stufe, spec_tint, aniso, sheen_g, sheen_r,
                                           sheen_t, coat_g, coat_r, coat_i, coat_t, coat_n, coat_n_verbunden, trans_g, sss_g, sss_radius, sss_skala, multi_ggx,
                                           tang_gueltig, korrektur_an, ggx_E, ggx_Eavg, ggx_s_ior, sheen_ltc, glass_E, glass_Eavg, glass_inv_E, glass_inv_Eavg, aus);
    HB_ENDE;
}

}  // namespace hb
