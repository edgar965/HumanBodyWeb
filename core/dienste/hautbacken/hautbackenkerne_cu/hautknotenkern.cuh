// hautknotenkern.cuh — die Kerne der Shaderknoten (bis 21.11.2026 Warp-Kerne in `graph/knoten/*.py`; dort je Knoten die Cycles-Quelle: svm/attribute.h,
// vertex_color.h, map_range.h, clamp.h, image.h, displace.h, hsv.h, brightness.h, gamma.h, invert.h, mapping.h, math_util.h, mix.h, color_util.h,
// tex_coord.h, ramp.h, sepcomb_*.h). Zeile für Zeile übertragen.
#pragma once
#include "hautfunktionen.cuh"

namespace hb {

// ------------------------------------------------------------ Attribut, Bild, UV
__global__ void k_farbattribut(int n, const float* val, const float* dx, const float* dy, int modus, float breite, float* farbe, float* alpha, float* fac)
{
    HB_FADEN(n)
    v4 v = lies4(val, i);
    if (modus == 1)
        v = add(v, mul(lies4(dx, i), breite));
    else if (modus == 2)
        v = add(v, mul(lies4(dy, i), breite));
    const v3 rgb = V3(v.c[0], v.c[1], v.c[2]);
    schreib3(farbe, i, rgb);
    alpha[i] = v.c[3];
    fac[i] = average3(rgb);
}
__global__ void k_bild_trennen(int n, const float* r, float* farbe, float* alpha)
{
    HB_FADEN(n)
    const v4 v = lies4(r, i);
    schreib3(farbe, i, V3(v.c[0], v.c[1], v.c[2]));
    alpha[i] = v.c[3];
}
__global__ void k_uv_koordinate(int n, const float* val, const float* dx, const float* dy, int modus, float breite, float* aus)
{
    HB_FADEN(n)
    v2 v = lies2(val, i);
    if (modus == 1)
        v = add(v, mul(lies2(dx, i), breite));
    else if (modus == 2)
        v = add(v, mul(lies2(dy, i), breite));
    schreib3(aus, i, V3(v.c[0], v.c[1], 0.0f));
}

// ------------------------------------------------------------ Map Range, Clamp
__global__ void k_bereich_zahl(int n, const float* wert, const float* von_min, const float* von_max, const float* nach_min, const float* nach_max,
                               const float* schritte, int art, int klemme, float* aus)
{
    HB_FADEN(n)
    const float value = wert[i], f0 = von_min[i], f1 = von_max[i], t0 = nach_min[i], t1 = nach_max[i];
    float result = 0.0f;
    if (f1 != f0) {
        float factor = value;
        if (art == 0) {
            factor = (value - f0) / (f1 - f0);
        } else if (art == 1) {
            factor = (value - f0) / (f1 - f0);
            if (schritte[i] > 0.0f)
                factor = floorf(factor * (schritte[i] + 1.0f)) / schritte[i];
            else
                factor = 0.0f;
        } else if (art == 2) {
            factor = f0 > f1 ? 1.0f - smoothstep_cycles(f1, f0, factor) : smoothstep_cycles(f0, f1, factor);
        } else {
            factor = f0 > f1 ? 1.0f - smootherstep(f1, f0, factor) : smootherstep(f0, f1, factor);
        }
        result = t0 + factor * (t1 - t0);
    }
    if (klemme > 0)
        result = t0 > t1 ? wclamp(result, t1, t0) : wclamp(result, t0, t1);
    aus[i] = result;
}
__global__ void k_bereich_vektor(int n, const float* wert, const float* von_min, const float* von_max, const float* nach_min, const float* nach_max,
                                 const float* schritte, int art, int klemme_in, float* aus)
{
    HB_FADEN(n)
    const v3 value = lies3(wert, i), f0 = lies3(von_min, i), f1 = lies3(von_max, i), t0 = lies3(nach_min, i), t1 = lies3(nach_max, i);
    int klemme = klemme_in;
    if (art == 2 || art == 3)
        klemme = 0;
    v3 factor = value;
    if (art == 0) {
        factor = safe_divide3(sub(value, f0), sub(f1, f0));
    } else if (art == 1) {
        factor = safe_divide3(sub(value, f0), sub(f1, f0));
        const v3 s = lies3(schritte, i);
        for (int k = 0; k < 3; ++k)
            factor.c[k] = s.c[k] > 0.0f ? floorf(factor.c[k] * (s.c[k] + 1.0f)) / s.c[k] : 0.0f;
    } else if (art == 2) {
        factor = safe_divide3(sub(value, f0), sub(f1, f0));
        for (int k = 0; k < 3; ++k) {
            const float x = wclamp(factor.c[k], 0.0f, 1.0f);
            factor.c[k] = (3.0f - 2.0f * x) * (x * x);
        }
    } else {
        factor = safe_divide3(sub(value, f0), sub(f1, f0));
        for (int k = 0; k < 3; ++k) {
            const float x = wclamp(factor.c[k], 0.0f, 1.0f);
            factor.c[k] = x * x * x * (x * (x * 6.0f - 15.0f) + 10.0f);
        }
    }
    v3 result = add(t0, cw_mul(factor, sub(t1, t0)));
    if (klemme > 0)
        for (int k = 0; k < 3; ++k)
            result.c[k] = t0.c[k] > t1.c[k] ? wclamp(result.c[k], t1.c[k], t0.c[k]) : wclamp(result.c[k], t0.c[k], t1.c[k]);
    schreib3(aus, i, result);
}
__global__ void k_klemmen(int n, const float* wert, const float* kleinst, const float* groesst, int bereich, float* aus)
{
    HB_FADEN(n)
    aus[i] = (bereich > 0 && kleinst[i] > groesst[i]) ? wclamp(wert[i], groesst[i], kleinst[i]) : wclamp(wert[i], kleinst[i], groesst[i]);
}

// ------------------------------------------------------------ Bump
__global__ void k_bump(int n, const float* h_c, const float* h_x, const float* h_y, const float* normal_ein, const float* dpx, const float* dpy,
                       const float* staerke, const float* abstand, float breite, int umkehren, float* aus)
{
    HB_FADEN(n)
    const v3 nn = lies3(normal_ein, i);
    const v3 rx = cross(lies3(dpy, i), nn);
    const v3 ry = cross(nn, lies3(dpx, i));
    const float c = h_c[i];
    const float det = dot(lies3(dpx, i), rx);
    const v3 surfgrad = add(mul(h_x[i] - c, rx), mul(h_y[i] - c, ry));
    const float absdet = fabsf(det);
    float s = staerke[i];
    float scale = abstand[i];
    if (umkehren > 0)
        scale = scale * -1.0f;
    s = fmaxf(s, 0.0f);
    v3 ergebnis = safe_normalize3(sub(mul(breite * absdet, nn), mul(scale * signf(det), surfgrad)));
    if (null(ergebnis))
        ergebnis = nn;
    else
        ergebnis = normalize(add(mul(s, ergebnis), mul(1.0f - s, nn)));
    schreib3(aus, i, ergebnis);
}

// ------------------------------------------------------------ Farbe
__global__ void k_hsv(int n, const float* farbe, const float* farbton, const float* saettigung, const float* wert, const float* fac, float* aus)
{
    HB_FADEN(n)
    const v3 in_color = lies3(farbe, i);
    v3 c = rgb_to_hsv(in_color);
    c = V3(fractf(c.c[0] + farbton[i] + 0.5f), wclamp(c.c[1] * saettigung[i], 0.0f, 1.0f), c.c[2] * wert[i]);
    c = hsv_to_rgb(c);
    const float f = fac[i];
    c = V3(f * c.c[0] + (1.0f - f) * in_color.c[0], f * c.c[1] + (1.0f - f) * in_color.c[1], f * c.c[2] + (1.0f - f) * in_color.c[2]);
    schreib3(aus, i, V3(fmaxf(c.c[0], 0.0f), fmaxf(c.c[1], 0.0f), fmaxf(c.c[2], 0.0f)));
}
__global__ void k_helligkeit(int n, const float* farbe, const float* helligkeit, const float* kontrast, float* aus)
{
    HB_FADEN(n)
    const float a = 1.0f + kontrast[i];
    const float b = helligkeit[i] - kontrast[i] * 0.5f;
    const v3 c = lies3(farbe, i);
    schreib3(aus, i, V3(fmaxf(a * c.c[0] + b, 0.0f), fmaxf(a * c.c[1] + b, 0.0f), fmaxf(a * c.c[2] + b, 0.0f)));
}
__global__ void k_gamma(int n, const float* farbe, const float* gamma, float* aus)
{
    HB_FADEN(n)
    v3 c = lies3(farbe, i);
    const float g = gamma[i];
    if (g == 0.0f) {
        schreib3(aus, i, V3(1.0f, 1.0f, 1.0f));
        return;
    }
    for (int k = 0; k < 3; ++k)
        if (c.c[k] > 0.0f)
            c.c[k] = powf(c.c[k], g);
    schreib3(aus, i, c);
}
__global__ void k_invertieren(int n, const float* farbe, const float* fac, float* aus)
{
    HB_FADEN(n)
    const v3 c = lies3(farbe, i);
    const float f = fac[i];
    schreib3(aus, i, V3(f * (1.0f - c.c[0]) + (1.0f - f) * c.c[0], f * (1.0f - c.c[1]) + (1.0f - f) * c.c[1], f * (1.0f - c.c[2]) + (1.0f - f) * c.c[2]));
}

// ------------------------------------------------------------ Mapping
__device__ __forceinline__ m33 euler(v3 e)
{
    const float cx = cosf(e.c[0]), cy = cosf(e.c[1]), cz = cosf(e.c[2]);
    const float sx = sinf(e.c[0]), sy = sinf(e.c[1]), sz = sinf(e.c[2]);
    return M33(cy * cz, sy * sx * cz - cx * sz, sy * cx * cz + sx * sz,
               cy * sz, sy * sx * sz + cx * cz, sy * cx * sz - sx * cz,
               wneg(sy), cy * sx, cy * cx);
}
__global__ void k_abbilden(int n, const float* vektor, const float* ort, const float* drehung, const float* skala, int art, float* aus)
{
    HB_FADEN(n)
    const m33 r = euler(lies3(drehung, i));
    const v3 v = lies3(vektor, i), s = lies3(skala, i), o = lies3(ort, i);
    v3 e;
    if (art == 0)
        e = add(mul(r, cw_mul(v, s)), o);
    else if (art == 1)
        e = safe_divide3(mul(transpose(r), sub(v, o)), s);
    else if (art == 2)
        e = mul(r, cw_mul(v, s));
    else
        e = safe_normalize3(mul(r, safe_divide3(v, s)));
    schreib3(aus, i, e);
}

// ------------------------------------------------------------ Math, Vector Math
#define FLT_EPS_HB 1.1920929e-07f
__device__ float svm_math(int typ, float a, float b, float c)
{
    float r = 0.0f;
    switch (typ) {
    case 0: r = a + b; break;
    case 1: r = a - b; break;
    case 2: r = a * b; break;
    case 3: r = safe_divide(a, b); break;
    case 4: r = a * b + c; break;
    case 5: r = safe_powf(a, b); break;
    case 6: r = safe_logf(a, b); break;
    case 7: r = safe_sqrtf(a); break;
    case 8: r = inversesqrtf(a); break;
    case 9: r = fabsf(a); break;
    case 10: r = expf(a); break;
    case 11: r = fminf(a, b); break;
    case 12: r = fmaxf(a, b); break;
    case 13: if (a < b) r = 1.0f; break;
    case 14: if (a > b) r = 1.0f; break;
    case 15: r = compatible_signf(a); break;
    case 16: if (a == b || fabsf(a - b) <= fmaxf(c, FLT_EPS_HB)) r = 1.0f; break;
    case 17: r = smoothminf(a, b, c); break;
    case 18: r = wneg(smoothminf(wneg(a), wneg(b), c)); break;
    case 19: r = floorf(a + 0.5f); break;
    case 20: r = floorf(a); break;
    case 21: r = ceilf(a); break;
    case 22: r = a >= 0.0f ? floorf(a) : ceilf(a); break;
    case 23: r = a - floorf(a); break;
    case 24: r = safe_modulo(a, b); break;
    case 25: r = safe_floored_modulo(a, b); break;
    case 26: r = wrapf(a, b, c); break;
    case 27: r = floorf(safe_divide(a, b)) * b; break;
    case 28: r = pingpongf(a, b); break;
    case 29: r = sinf(a); break;
    case 30: r = cosf(a); break;
    case 31: r = tanf(a); break;
    case 32: r = safe_asinf(a); break;
    case 33: r = safe_acosf(a); break;
    case 34: r = atanf(a); break;
    case 35: r = compatible_atan2(a, b); break;
    case 36: r = sinhf(a); break;
    case 37: r = coshf(a); break;
    case 38: r = tanhf(a); break;
    case 39: r = a * (PI_F / 180.0f); break;
    case 40: r = a * (180.0f / PI_F); break;
    default: break;
    }
    return r;
}
__global__ void k_mathe(int n, const float* a, const float* b, const float* c, int typ, int klemme, float* aus)
{
    HB_FADEN(n)
    float r = svm_math(typ, a[i], b[i], c[i]);
    if (klemme > 0)
        r = wclamp(r, 0.0f, 1.0f);
    aus[i] = r;
}
__device__ v3 komponenten(v3 f, v3 g, int wahl)
{
    v3 r = null3();
    for (int k = 0; k < 3; ++k) {
        switch (wahl) {
        case 0: r.c[k] = fminf(f.c[k], g.c[k]); break;
        case 1: r.c[k] = fmaxf(f.c[k], g.c[k]); break;
        case 2: r.c[k] = fabsf(f.c[k]); break;
        case 3: r.c[k] = floorf(f.c[k]); break;
        case 4: r.c[k] = ceilf(f.c[k]); break;
        case 5: r.c[k] = f.c[k] - floorf(f.c[k]); break;
        case 6: r.c[k] = floorf(f.c[k] + 0.5f); break;
        case 7: r.c[k] = sinf(f.c[k]); break;
        case 8: r.c[k] = cosf(f.c[k]); break;
        case 9: r.c[k] = tanf(f.c[k]); break;
        case 10: r.c[k] = compatible_signf(f.c[k]); break;
        case 11: r.c[k] = floorf(safe_divide(f.c[k], g.c[k])) * g.c[k]; break;
        default: break;
        }
    }
    return r;
}
__global__ void k_vektor_mathe(int n, const float* a, const float* b, const float* c, const float* skala, int typ, float* vektor_aus, float* wert_aus)
{
    HB_FADEN(n)
    const v3 x = lies3(a, i), y = lies3(b, i), z = lies3(c, i);
    v3 v = null3();
    float w = 0.0f;
    switch (typ) {
    case 0: v = add(x, y); break;
    case 1: v = sub(x, y); break;
    case 2: v = cw_mul(x, y); break;
    case 3: v = safe_divide3(x, y); break;
    case 4: v = add(cw_mul(x, y), z); break;
    case 5: v = cross(x, y); break;
    case 6: v = project3(x, y); break;
    case 7: v = reflect3(x, safe_normalize3(y)); break;
    case 8: v = refract3(x, safe_normalize3(y), skala[i]); break;
    case 9: v = faceforward3(x, y, z); break;
    case 10: w = dot(x, y); break;
    case 11: w = length(sub(x, y)); break;
    case 12: w = length(x); break;
    case 13: v = mul(x, skala[i]); break;
    case 14: v = safe_normalize3(x); break;
    case 15: v = komponenten(x, y, 2); break;
    case 16: v = safe_pow3(x, y); break;
    case 17: v = komponenten(x, y, 10); break;
    case 18: v = komponenten(x, y, 0); break;
    case 19: v = komponenten(x, y, 1); break;
    case 20: v = komponenten(x, y, 6); break;
    case 21: v = komponenten(x, y, 3); break;
    case 22: v = komponenten(x, y, 4); break;
    case 23: v = komponenten(x, y, 5); break;
    case 24: v = safe_fmod3(x, y); break;
    case 25: v = wrap3(x, y, z); break;
    case 26: v = komponenten(x, y, 11); break;
    case 27: v = komponenten(x, y, 7); break;
    case 28: v = komponenten(x, y, 8); break;
    case 29: v = komponenten(x, y, 9); break;
    default: break;
    }
    schreib3(vektor_aus, i, v);
    wert_aus[i] = w;
}

// ------------------------------------------------------------ Mix
__device__ __forceinline__ float ueberlagern(float c1, float c2, float t, float tm)
{
    if (c1 < 0.5f)
        return c1 * (tm + 2.0f * t * c2);
    return 1.0f - (tm + 2.0f * t * (1.0f - c2)) * (1.0f - c1);
}
__device__ __forceinline__ float mix_teilen(float c1, float c2, float t, float tm) { return c2 != 0.0f ? tm * c1 + t * c1 / c2 : c1; }
__device__ __forceinline__ float abwedeln(float c1, float c2, float t)
{
    if (c1 != 0.0f) {
        float tmp = 1.0f - t * c2;
        if (tmp <= 0.0f)
            return 1.0f;
        tmp = c1 / tmp;
        if (tmp > 1.0f)
            return 1.0f;
        return tmp;
    }
    return c1;
}
__device__ __forceinline__ float nachbelichten(float c1, float c2, float t, float tm)
{
    float tmp = tm + t * c2;
    if (tmp <= 0.0f)
        return 0.0f;
    tmp = 1.0f - (1.0f - c1) / tmp;
    if (tmp < 0.0f)
        return 0.0f;
    if (tmp > 1.0f)
        return 1.0f;
    return tmp;
}
__device__ v3 svm_mix(int typ, float t, v3 c1, v3 c2)
{
    const float tm = 1.0f - t;
    const v3 one = V3(1.0f, 1.0f, 1.0f);
    v3 out = c1;
    switch (typ) {
    case 0: out = add(c1, mul(t, sub(c2, c1))); break;
    case 1: out = add(c1, mul(t, sub(add(c1, c2), c1))); break;
    case 2: out = add(c1, mul(t, sub(cw_mul(c1, c2), c1))); break;
    case 3: out = add(c1, mul(t, sub(sub(c1, c2), c1))); break;
    case 4: out = sub(one, cw_mul(add(V3(tm, tm, tm), mul(t, sub(one, c2))), sub(one, c1))); break;
    case 5: out = V3(mix_teilen(c1.c[0], c2.c[0], t, tm), mix_teilen(c1.c[1], c2.c[1], t, tm), mix_teilen(c1.c[2], c2.c[2], t, tm)); break;
    case 6: out = add(c1, mul(t, sub(V3(fabsf(c1.c[0] - c2.c[0]), fabsf(c1.c[1] - c2.c[1]), fabsf(c1.c[2] - c2.c[2])), c1))); break;
    case 7: out = add(c1, mul(t, sub(V3(fminf(c1.c[0], c2.c[0]), fminf(c1.c[1], c2.c[1]), fminf(c1.c[2], c2.c[2])), c1))); break;
    case 8: out = add(c1, mul(t, sub(V3(fmaxf(c1.c[0], c2.c[0]), fmaxf(c1.c[1], c2.c[1]), fmaxf(c1.c[2], c2.c[2])), c1))); break;
    case 9: out = V3(ueberlagern(c1.c[0], c2.c[0], t, tm), ueberlagern(c1.c[1], c2.c[1], t, tm), ueberlagern(c1.c[2], c2.c[2], t, tm)); break;
    case 10: out = V3(abwedeln(c1.c[0], c2.c[0], t), abwedeln(c1.c[1], c2.c[1], t), abwedeln(c1.c[2], c2.c[2], t)); break;
    case 11: out = V3(nachbelichten(c1.c[0], c2.c[0], t, tm), nachbelichten(c1.c[1], c2.c[1], t, tm), nachbelichten(c1.c[2], c2.c[2], t, tm)); break;
    case 12: {
        const v3 hsv2 = rgb_to_hsv(c2);
        if (hsv2.c[1] != 0.0f) {
            v3 hsv = rgb_to_hsv(c1);
            hsv = V3(hsv2.c[0], hsv.c[1], hsv.c[2]);
            out = add(c1, mul(t, sub(hsv_to_rgb(hsv), c1)));
        }
        break;
    }
    case 13: {
        v3 hsv = rgb_to_hsv(c1);
        if (hsv.c[1] != 0.0f) {
            const v3 hsv2 = rgb_to_hsv(c2);
            hsv = V3(hsv.c[0], tm * hsv.c[1] + t * hsv2.c[1], hsv.c[2]);
            out = hsv_to_rgb(hsv);
        }
        break;
    }
    case 14: {
        v3 hsv = rgb_to_hsv(c1);
        const v3 hsv2 = rgb_to_hsv(c2);
        hsv = V3(hsv.c[0], hsv.c[1], tm * hsv.c[2] + t * hsv2.c[2]);
        out = hsv_to_rgb(hsv);
        break;
    }
    case 15: {
        const v3 hsv2 = rgb_to_hsv(c2);
        if (hsv2.c[1] != 0.0f) {
            v3 hsv = rgb_to_hsv(c1);
            hsv = V3(hsv2.c[0], hsv2.c[1], hsv.c[2]);
            out = add(c1, mul(t, sub(hsv_to_rgb(hsv), c1)));
        }
        break;
    }
    case 16: {
        const v3 scr = sub(one, cw_mul(sub(one, c2), sub(one, c1)));
        out = add(mul(tm, c1), mul(t, add(cw_mul(cw_mul(sub(one, c1), c2), c1), cw_mul(c1, scr))));
        break;
    }
    case 17: out = add(c1, mul(t, add(mul(2.0f, c2), V3(-1.0f, -1.0f, -1.0f)))); break;
    case 18: {
        const v3 e = add(c1, mul(t, sub(sub(add(c1, c2), mul(2.0f, cw_mul(c1, c2))), c1)));
        out = V3(fmaxf(e.c[0], 0.0f), fmaxf(e.c[1], 0.0f), fmaxf(e.c[2], 0.0f));
        break;
    }
    case 19: out = saturate3(c1); break;
    default: break;
    }
    return out;
}
__global__ void k_mix_farbe(int n, const float* a, const float* b, const float* fac, int typ, int klemme, int klemme_ergebnis, float* aus)
{
    HB_FADEN(n)
    float t = fac[i];
    if (klemme > 0)
        t = wclamp(t, 0.0f, 1.0f);
    v3 r = svm_mix(typ, t, lies3(a, i), lies3(b, i));
    if (klemme_ergebnis > 0)
        r = saturate3(r);
    schreib3(aus, i, r);
}
__global__ void k_mix_alt(int n, const float* a, const float* b, const float* fac, int typ, int klemme, float* aus)
{
    HB_FADEN(n)
    v3 r = svm_mix(typ, wclamp(fac[i], 0.0f, 1.0f), lies3(a, i), lies3(b, i));
    if (klemme > 0)
        r = saturate3(r);
    schreib3(aus, i, r);
}
__global__ void k_mix_zahl(int n, const float* a, const float* b, const float* fac, int klemme, float* aus)
{
    HB_FADEN(n)
    float t = fac[i];
    if (klemme > 0)
        t = wclamp(t, 0.0f, 1.0f);
    aus[i] = (1.0f - t) * a[i] + t * b[i];
}
__global__ void k_mix_vektor(int n, const float* a, const float* b, const float* fac, int klemme, float* aus)
{
    HB_FADEN(n)
    float t = fac[i];
    if (klemme > 0)
        t = wclamp(t, 0.0f, 1.0f);
    schreib3(aus, i, add(mul(1.0f - t, lies3(a, i)), mul(t, lies3(b, i))));
}
__global__ void k_mix_vektor_ungleich(int n, const float* a, const float* b, const float* fac, int klemme, float* aus)
{
    HB_FADEN(n)
    v3 t = lies3(fac, i);
    if (klemme > 0)
        t = saturate3(t);
    schreib3(aus, i, add(cw_mul(sub(V3(1.0f, 1.0f, 1.0f), t), lies3(a, i)), cw_mul(t, lies3(b, i))));
}

// ------------------------------------------------------------ Normal Map
__global__ void k_normalkarte(int n, const float* farbe, const float* staerke, const float* tang, const float* vorz, const float* normale, const float* ngf,
                              const int* glatt, const float* n_shader, const int* rueck, int dx_umkehren, float* aus)
{
    HB_FADEN(n)
    v3 c = lies3(farbe, i);
    c = V3(2.0f * (c.c[0] - 0.5f), 2.0f * (c.c[1] - 0.5f), 2.0f * (c.c[2] - 0.5f));
    if (dx_umkehren > 0)
        c = V3(c.c[0], wneg(c.c[1]), c.c[2]);
    const float s = staerke[i];
    v3 nn = lies3(normale, i);
    if (glatt[i] == 0) {
        nn = lies3(ngf, i);
        if (rueck[i] != 0)
            nn = neg(nn);
    }
    c = V3(c.c[0] * s, c.c[1] * s, (1.0f - wclamp(s, 0.0f, 1.0f)) + wclamp(s, 0.0f, 1.0f) * c.c[2]);
    const v3 t = lies3(tang, i);
    const v3 b = mul(vorz[i], cross(nn, t));
    v3 r = safe_normalize3(add(add(mul(c.c[0], t), mul(c.c[1], b)), mul(c.c[2], nn)));
    if (rueck[i] != 0)
        r = neg(r);
    if (null(r) || isnan(r.c[0]) || isnan(r.c[1]) || isnan(r.c[2]))
        r = lies3(n_shader, i);
    schreib3(aus, i, r);
}
__global__ void k_normalkarte_fest(int n, const float* farbe, const float* staerke, const float* n_shader, const int* rueck, int blender, float* aus)
{
    HB_FADEN(n)
    v3 c = lies3(farbe, i);
    c = V3(2.0f * (c.c[0] - 0.5f), 2.0f * (c.c[1] - 0.5f), 2.0f * (c.c[2] - 0.5f));
    if (blender > 0)
        c = V3(c.c[0], wneg(c.c[1]), wneg(c.c[2]));
    v3 r = safe_normalize3(c);
    if (rueck[i] != 0)
        r = neg(r);
    float s = staerke[i];
    const v3 ns = lies3(n_shader, i);
    if (s != 1.0f) {
        s = fmaxf(s, 0.0f);
        r = safe_normalize3(add(ns, mul(sub(r, ns), s)));
    }
    if (null(r))
        r = ns;
    schreib3(aus, i, r);
}

// ------------------------------------------------------------ ColorRamp, Kurven
__device__ v4 rgb_ramp_lookup(const float* tab, float f_in, int interpolieren, int extrapolieren, int groesse)
{
    float f = f_in;
    if ((f < 0.0f || f > 1.0f) && extrapolieren > 0) {
        v4 t0, dy;
        if (f < 0.0f) {
            t0 = lies4(tab, 0);
            dy = sub(t0, lies4(tab, 1));
            f = wneg(f);
        } else {
            t0 = lies4(tab, groesse - 1);
            dy = sub(t0, lies4(tab, groesse - 2));
            f = f - 1.0f;
        }
        return add(t0, mul(mul(dy, f), (float)(groesse - 1)));
    }
    f = wclamp(f, 0.0f, 1.0f) * (float)(groesse - 1);
    const int i = iclamp((int)f, 0, groesse - 1);
    const float t = f - (float)i;
    v4 a = lies4(tab, i);
    if (interpolieren > 0 && t > 0.0f)
        a = add(mul(1.0f - t, a), mul(t, lies4(tab, i + 1)));
    return a;
}
__device__ float float_ramp_lookup(const float* tab, float f_in, int interpolieren, int extrapolieren, int groesse)
{
    float f = f_in;
    if ((f < 0.0f || f > 1.0f) && extrapolieren > 0) {
        float t0, dy;
        if (f < 0.0f) {
            t0 = tab[0];
            dy = t0 - tab[1];
            f = wneg(f);
        } else {
            t0 = tab[groesse - 1];
            dy = t0 - tab[groesse - 2];
            f = f - 1.0f;
        }
        return t0 + dy * f * (float)(groesse - 1);
    }
    f = wclamp(f, 0.0f, 1.0f) * (float)(groesse - 1);
    const int i = iclamp((int)f, 0, groesse - 1);
    const float t = f - (float)i;
    float a = tab[i];
    if (interpolieren > 0 && t > 0.0f)
        a = (1.0f - t) * a + t * tab[i + 1];
    return a;
}
__global__ void k_rampe(int n, const float* fac, const float* tab, int interpolieren, int groesse, float* farbe, float* alpha)
{
    HB_FADEN(n)
    const v4 c = rgb_ramp_lookup(tab, fac[i], interpolieren, 0, groesse);
    schreib3(farbe, i, V3(c.c[0], c.c[1], c.c[2]));
    alpha[i] = c.c[3];
}
__global__ void k_kurven(int n, const float* fac, const float* farbe, const float* tab, float min_x, float max_x, int extrapolieren, int groesse, float* aus)
{
    HB_FADEN(n)
    const v3 c = lies3(farbe, i);
    const float bereich = max_x - min_x;
    const v3 rel = V3((c.c[0] - min_x) / bereich, (c.c[1] - min_x) / bereich, (c.c[2] - min_x) / bereich);
    const v4 vr = rgb_ramp_lookup(tab, rel.c[0], 1, extrapolieren, groesse);
    const v4 vg = rgb_ramp_lookup(tab, rel.c[1], 1, extrapolieren, groesse);
    const v4 vb = rgb_ramp_lookup(tab, rel.c[2], 1, extrapolieren, groesse);
    const float f = fac[i];
    schreib3(aus, i, add(mul(1.0f - f, c), mul(f, V3(vr.c[0], vg.c[1], vb.c[2]))));
}
__global__ void k_kurve(int n, const float* fac, const float* wert, const float* tab, float min_x, float max_x, int extrapolieren, int groesse, float* aus)
{
    HB_FADEN(n)
    const float w = wert[i];
    const float rel = (w - min_x) / (max_x - min_x);
    const float v = float_ramp_lookup(tab, rel, 1, extrapolieren, groesse);
    const float f = fac[i];
    aus[i] = (1.0f - f) * w + f * v;
}

// ------------------------------------------------------------ Trennen, Zusammensetzen
__global__ void k_farbe_trennen(int n, const float* farbe, int modus, float* r, float* g, float* b)
{
    HB_FADEN(n)
    v3 c = lies3(farbe, i);
    if (modus == 1)
        c = rgb_to_hsv(c);
    else if (modus == 2)
        c = rgb_to_hsl(c);
    r[i] = c.c[0];
    g[i] = c.c[1];
    b[i] = c.c[2];
}
__global__ void k_farbe_zusammen(int n, const float* r, const float* g, const float* b, int modus, float* aus)
{
    HB_FADEN(n)
    v3 c = V3(r[i], g[i], b[i]);
    if (modus == 1)
        c = hsv_to_rgb(c);
    else if (modus == 2)
        c = hsl_to_rgb(c);
    schreib3(aus, i, c);
}
__global__ void k_trennen_xyz(int n, const float* v, float* x, float* y, float* z)
{
    HB_FADEN(n)
    x[i] = v[3 * i];
    y[i] = v[3 * i + 1];
    z[i] = v[3 * i + 2];
}
__global__ void k_zusammen_xyz(int n, const float* x, const float* y, const float* z, float* aus)
{
    HB_FADEN(n)
    schreib3(aus, i, V3(x[i], y[i], z[i]));
}

}  // namespace hb
