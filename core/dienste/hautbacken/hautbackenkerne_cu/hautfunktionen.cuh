// hautfunktionen.cuh — die kleinen Rechenfunktionen von Cycles (bis 21.11.2026 Warp-Funktionen in `hautfunktionen.py` und `hautfarbfunktionen.py`), Zeile für
// Zeile übertragen; dort stehen die Blender-Quellen je Funktion (math_base.h, math_float3.h, color.h, color_util.h, map_range.h, math_util.h).
#pragma once
#include "wp17.cuh"

namespace hb {

#define PI_F 3.1415926535897932f

// ------------------------------------------------------------ util/math_base.h
__device__ __forceinline__ float saturatef(float a) { return wclamp(a, 0.0f, 1.0f); }
__device__ __forceinline__ float fractf(float x) { return x - floorf(x); }
__device__ __forceinline__ float safe_divide(float a, float b) { return b != 0.0f ? a / b : 0.0f; }
__device__ __forceinline__ float safe_sqrtf(float f) { return sqrtf(fmaxf(f, 0.0f)); }
__device__ __forceinline__ float inversesqrtf(float f) { return f > 0.0f ? 1.0f / sqrtf(f) : 0.0f; }
__device__ __forceinline__ float safe_asinf(float a) { return wasin(wclamp(a, -1.0f, 1.0f)); }
__device__ __forceinline__ float safe_acosf(float a) { return wacos(wclamp(a, -1.0f, 1.0f)); }

__device__ __forceinline__ float compatible_powf(float x, float y)
{
    if (y == 0.0f)
        return 1.0f;
    if (x == 0.0f)
        return 0.0f;
    if (x < 0.0f) {
        if (fmodf(wneg(y), 2.0f) == 0.0f)
            return powf(wneg(x), y);
        return wneg(powf(wneg(x), y));
    }
    return powf(x, y);
}
__device__ __forceinline__ float safe_powf(float a, float b)
{
    if (a < 0.0f && b != (float)(int)b)
        return 0.0f;
    return compatible_powf(a, b);
}
__device__ __forceinline__ float safe_logf(float a, float b)
{
    if (a <= 0.0f || b <= 0.0f)
        return 0.0f;
    return safe_divide(logf(a), logf(b));
}
__device__ __forceinline__ float safe_modulo(float a, float b) { return b != 0.0f ? fmodf(a, b) : 0.0f; }
__device__ __forceinline__ float safe_floored_modulo(float a, float b) { return b != 0.0f ? a - floorf(a / b) * b : 0.0f; }
__device__ __forceinline__ float wrapf(float value, float maxv, float minv)
{
    const float rng = maxv - minv;
    if (rng != 0.0f)
        return value - (rng * floorf((value - minv) / rng));
    return minv;
}
__device__ __forceinline__ float pingpongf(float a, float b)
{
    if (b != 0.0f)
        return fabsf(fractf((a - b) / (b * 2.0f)) * b * 2.0f - b);
    return 0.0f;
}
__device__ __forceinline__ float smoothminf(float a, float b, float k)
{
    if (k != 0.0f) {
        const float h = fmaxf(k - fabsf(a - b), 0.0f) / k;
        return fminf(a, b) - h * h * h * k * (1.0f / 6.0f);
    }
    return fminf(a, b);
}
__device__ __forceinline__ float signf(float f) { return f < 0.0f ? -1.0f : 1.0f; }
__device__ __forceinline__ float compatible_signf(float f) { return f == 0.0f ? 0.0f : signf(f); }
__device__ __forceinline__ float compatible_atan2(float y, float x) { return (x == 0.0f && y == 0.0f) ? 0.0f : atan2f(y, x); }
__device__ __forceinline__ float smoothstep_cycles(float edge0, float edge1, float x)
{
    if (x < edge0)
        return 0.0f;
    if (x >= edge1)
        return 1.0f;
    const float t = (x - edge0) / (edge1 - edge0);
    return (3.0f - 2.0f * t) * (t * t);
}
__device__ __forceinline__ float smootherstep(float edge0, float edge1, float x)
{
    const float xx = wclamp(safe_divide(x - edge0, edge1 - edge0), 0.0f, 1.0f);
    return xx * xx * xx * (xx * (xx * 6.0f - 15.0f) + 10.0f);
}

// --------------------------------------------------------- util/math_float3.h
__device__ __forceinline__ v3 safe_normalize3(v3 a)
{
    const float t = length(a);
    if (t != 0.0f)
        return mul(a, 1.0f / t);
    return a;
}
__device__ __forceinline__ float average3(v3 a) { return (a.c[0] + a.c[1] + a.c[2]) * (1.0f / 3.0f); }
__device__ __forceinline__ v3 safe_divide3(v3 a, v3 b) { return V3(safe_divide(a.c[0], b.c[0]), safe_divide(a.c[1], b.c[1]), safe_divide(a.c[2], b.c[2])); }
__device__ __forceinline__ v3 safe_pow3(v3 a, v3 b) { return V3(safe_powf(a.c[0], b.c[0]), safe_powf(a.c[1], b.c[1]), safe_powf(a.c[2], b.c[2])); }
__device__ __forceinline__ v3 project3(v3 v, v3 v_proj)
{
    const float len_squared = dot(v_proj, v_proj);
    if (len_squared != 0.0f)
        return mul(dot(v, v_proj) / len_squared, v_proj);
    return null3();
}
__device__ __forceinline__ v3 reflect3(v3 incident, v3 unit_normal) { return sub(incident, mul(mul(2.0f, unit_normal), dot(incident, unit_normal))); }
__device__ __forceinline__ v3 refract3(v3 incident, v3 normal, float eta)
{
    const float k = 1.0f - eta * eta * (1.0f - dot(normal, incident) * dot(normal, incident));
    if (k < 0.0f)
        return null3();
    return sub(mul(eta, incident), mul(eta * dot(normal, incident) + sqrtf(k), normal));
}
__device__ __forceinline__ v3 faceforward3(v3 vector, v3 incident, v3 reference) { return dot(reference, incident) < 0.0f ? vector : neg(vector); }
__device__ __forceinline__ v3 safe_floored_fmod3(v3 a, v3 b)
{
    v3 r = null3();
    for (int i = 0; i < 3; ++i)
        if (b.c[i] != 0.0f)
            r.c[i] = a.c[i] - floorf(a.c[i] / b.c[i]) * b.c[i];
    return r;
}
__device__ __forceinline__ v3 wrap3(v3 value, v3 maxv, v3 minv) { return add(safe_floored_fmod3(sub(value, minv), sub(maxv, minv)), minv); }
__device__ __forceinline__ v3 safe_fmod3(v3 a, v3 b)
{
    v3 r = null3();
    for (int i = 0; i < 3; ++i)
        if (b.c[i] != 0.0f)
            r.c[i] = fmodf(a.c[i], b.c[i]);
    return r;
}
__device__ __forceinline__ v3 make_orthonormals_a(v3 n)
{
    v3 a;
    if (n.c[0] != n.c[1] || n.c[0] != n.c[2])
        a = V3(n.c[2] - n.c[1], n.c[0] - n.c[2], n.c[1] - n.c[0]);
    else
        a = V3(n.c[2] - n.c[1], n.c[0] + n.c[2], wneg(n.c[1]) - n.c[0]);
    return normalize(a);
}

// ------------------------------------------------------------- util/color.h, svm/color_util.h
__device__ __forceinline__ float color_srgb_to_linear(float c)
{
    if (c < 0.04045f) {
        if (c < 0.0f)
            return 0.0f;
        return c * (1.0f / 12.92f);
    }
    return powf((c + 0.055f) * (1.0f / 1.055f), 2.4f);
}
__device__ __forceinline__ float color_linear_to_srgb(float c)
{
    if (c < 0.0031308f) {
        if (c < 0.0f)
            return 0.0f;
        return c * 12.92f;
    }
    return 1.055f * powf(c, 1.0f / 2.4f) - 0.055f;
}
__device__ __forceinline__ v3 rgb_to_hsv(v3 rgb)
{
    const float cmax = fmaxf(rgb.c[0], fmaxf(rgb.c[1], rgb.c[2]));
    const float cmin = fminf(rgb.c[0], fminf(rgb.c[1], rgb.c[2]));
    const float cdelta = cmax - cmin;
    const float v = cmax;
    float s = 0.0f, h = 0.0f;
    if (cmax != 0.0f)
        s = cdelta / cmax;
    if (s != 0.0f) {
        const float c0 = (cmax - rgb.c[0]) / cdelta, c1 = (cmax - rgb.c[1]) / cdelta, c2 = (cmax - rgb.c[2]) / cdelta;
        if (rgb.c[0] == cmax)
            h = c2 - c1;
        else if (rgb.c[1] == cmax)
            h = 2.0f + c0 - c2;
        else
            h = 4.0f + c1 - c0;
        h = h / 6.0f;
        if (h < 0.0f)
            h = h + 1.0f;
    } else {
        h = 0.0f;
    }
    return V3(h, s, v);
}
__device__ __forceinline__ v3 hsv_to_rgb(v3 hsv)
{
    float h = hsv.c[0];
    const float s = hsv.c[1], v = hsv.c[2];
    v3 rgb = V3(v, v, v);
    if (s != 0.0f) {
        if (h == 1.0f)
            h = 0.0f;
        h = h * 6.0f;
        const float i = floorf(h);
        const float f = h - i;
        const float p = v * (1.0f - s);
        const float q = v * (1.0f - (s * f));
        const float t = v * (1.0f - (s * (1.0f - f)));
        if (i == 0.0f)
            rgb = V3(v, t, p);
        else if (i == 1.0f)
            rgb = V3(q, v, p);
        else if (i == 2.0f)
            rgb = V3(p, v, t);
        else if (i == 3.0f)
            rgb = V3(p, q, v);
        else if (i == 4.0f)
            rgb = V3(t, p, v);
        else
            rgb = V3(v, p, q);
    }
    return rgb;
}
__device__ __forceinline__ v3 rgb_to_hsl(v3 rgb)
{
    const float cmax = fmaxf(rgb.c[0], fmaxf(rgb.c[1], rgb.c[2]));
    const float cmin = fminf(rgb.c[0], fminf(rgb.c[1], rgb.c[2]));
    const float l = fminf(1.0f, (cmax + cmin) / 2.0f);
    float h = 0.0f, s = 0.0f;
    if (cmax == cmin) {
        h = 0.0f;
        s = 0.0f;
    } else {
        const float cdelta = cmax - cmin;
        if (l > 0.5f)
            s = cdelta / (2.0f - cmax - cmin);
        else
            s = cdelta / (cmax + cmin);
        if (cmax == rgb.c[0]) {
            if (rgb.c[1] < rgb.c[2])
                h = (rgb.c[1] - rgb.c[2]) / cdelta + 6.0f;
            else
                h = (rgb.c[1] - rgb.c[2]) / cdelta + 0.0f;
        } else if (cmax == rgb.c[1]) {
            h = (rgb.c[2] - rgb.c[0]) / cdelta + 2.0f;
        } else {
            h = (rgb.c[0] - rgb.c[1]) / cdelta + 4.0f;
        }
    }
    h = h / 6.0f;
    return V3(h, s, l);
}
__device__ __forceinline__ v3 hsl_to_rgb(v3 hsl)
{
    const float h = hsl.c[0], s = hsl.c[1], l = hsl.c[2];
    float nr = fabsf(h * 6.0f - 3.0f) - 1.0f;
    float ng = 2.0f - fabsf(h * 6.0f - 2.0f);
    float nb = 2.0f - fabsf(h * 6.0f - 4.0f);
    nr = wclamp(nr, 0.0f, 1.0f);
    nb = wclamp(nb, 0.0f, 1.0f);
    ng = wclamp(ng, 0.0f, 1.0f);
    const float chroma = (1.0f - fabsf(2.0f * l - 1.0f)) * s;
    return V3((nr - 0.5f) * chroma + l, (ng - 0.5f) * chroma + l, (nb - 0.5f) * chroma + l);
}
__device__ __forceinline__ v3 saturate3(v3 c) { return V3(wclamp(c.c[0], 0.0f, 1.0f), wclamp(c.c[1], 0.0f, 1.0f), wclamp(c.c[2], 0.0f, 1.0f)); }

}  // namespace hb
