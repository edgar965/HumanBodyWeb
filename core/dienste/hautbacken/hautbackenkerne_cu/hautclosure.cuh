// hautclosure.cuh — die gebackene Normale aus den Closures des Principled BSDF (bis 21.11.2026 Warp: `closure/hautclosurefunktionen.py`, `hautclosurekernel.py`),
// Zeile für Zeile übertragen; die Blender-Quellen (bsdf_util.h, bsdf_microfacet.h, lookup_table.h, svm/closure.h) und die Begründungen stehen dort.
#pragma once
#include "hautfunktionen.cuh"

namespace hb {

#define CUTOFF 1.0e-5f
#define BSSRDF_MIN_RADIUS 1.0e-8f

__device__ __forceinline__ float lookup_table_read(const float* tab, float x_in, int offset, int size)
{
    const float x = saturatef(x_in) * (float)(size - 1);
    const int index = imin((int)x, size - 1);
    const int nindex = imin(index + 1, size - 1);
    const float t = x - (float)index;
    const float data0 = tab[index + offset];
    if (t == 0.0f)
        return data0;
    const float data1 = tab[nindex + offset];
    return (1.0f - t) * data0 + t * data1;
}
__device__ __forceinline__ float lookup_table_read_2D(const float* tab, float x, float y_in, int offset, int xsize, int ysize)
{
    const float y = saturatef(y_in) * (float)(ysize - 1);
    const int index = imin((int)y, ysize - 1);
    const int nindex = imin(index + 1, ysize - 1);
    const float t = y - (float)index;
    const float data0 = lookup_table_read(tab, x, offset + xsize * index, xsize);
    if (t == 0.0f)
        return data0;
    const float data1 = lookup_table_read(tab, x, offset + xsize * nindex, xsize);
    return (1.0f - t) * data0 + t * data1;
}
__device__ __forceinline__ float lookup_table_read_3D(const float* tab, float x, float y, float z_in, int offset, int xsize, int ysize, int zsize)
{
    const float z = saturatef(z_in) * (float)(zsize - 1);
    const int index = imin((int)z, zsize - 1);
    const int nindex = imin(index + 1, zsize - 1);
    const float t = z - (float)index;
    const float data0 = lookup_table_read_2D(tab, x, y, offset + xsize * ysize * index, xsize, ysize);
    if (t == 0.0f)
        return data0;
    const float data1 = lookup_table_read_2D(tab, x, y, offset + xsize * ysize * nindex, xsize, ysize);
    return (1.0f - t) * data0 + t * data1;
}
__device__ __forceinline__ float F0_from_ior(float ior)
{
    const float k = (ior - 1.0f) / (ior + 1.0f);
    return k * k;
}
__device__ __forceinline__ float ior_from_F0(float f0)
{
    const float sqrt_f0 = sqrtf(wclamp(f0, 0.0f, 0.99f));
    return (1.0f + sqrt_f0) / (1.0f - sqrt_f0);
}
__device__ __forceinline__ float fresnel_dielectric_Fss(float eta)
{
    if (eta < 1.0f)
        return 0.997118f + eta * (0.1014f - eta * (0.965241f + eta * 0.130607f));
    return (eta - 1.0f) / (4.08567f + 1.00071f * eta);
}
__device__ __forceinline__ v3 fresnel_f82_Fss(v3 f0, v3 b)
{
    const v3 eins = V3(1.0f, 1.0f, 1.0f);
    return sub(add(cw_mul(f0, mul(eins, 1.0f - 1.0f / 21.0f)), mul(eins, 1.0f / 21.0f)), mul(b, 1.0f / 126.0f));
}
__device__ __forceinline__ v3 fresnel_f82tint_B(v3 f0, v3 tint)
{
    const float f = 6.0f / 7.0f;
    const float f5 = f * f * f * f * f;
    const v3 f_schlick = add(mul(f0, 1.0f - f5), V3(f5, f5, f5));
    return cw_mul(mul(f_schlick, 7.0f / (f5 * f)), sub(V3(1.0f, 1.0f, 1.0f), tint));
}
__device__ __forceinline__ float inverse_lerp(float a, float b, float x) { return (x - a) / (b - a); }
__device__ __forceinline__ float reduce_max3(v3 a) { return fmaxf(a.c[0], fmaxf(a.c[1], a.c[2])); }
__device__ __forceinline__ v3 safe_divide_color(v3 a, v3 b)
{
    float x = 0.0f, y = 0.0f, z = 0.0f;
    if (b.c[0] != 0.0f)
        x = a.c[0] / b.c[0];
    if (b.c[1] != 0.0f)
        y = a.c[1] / b.c[1];
    if (b.c[2] != 0.0f)
        z = a.c[2] / b.c[2];
    return V3(x, y, z);
}
__device__ __forceinline__ v3 closure_layering_weight(v3 layer_albedo, v3 weight)
{
    return mul(weight, saturatef(1.0f - reduce_max3(safe_divide_color(layer_albedo, weight))));
}
__device__ __forceinline__ v3 hb_darkening(float e, float e_avg, v3 fss)
{
    const float missing_factor = (1.0f - e) / e;
    const float energy_scale = 1.0f + missing_factor;
    if (fss.c[0] == 1.0f && fss.c[1] == 1.0f && fss.c[2] == 1.0f)
        return V3(1.0f, 1.0f, 1.0f);
    const v3 one = V3(1.0f, 1.0f, 1.0f);
    const v3 fms = cw_div(mul(fss, e_avg), sub(one, mul(fss, 1.0f - e_avg)));
    return mul(add(one, mul(fms, missing_factor)), 1.0f / energy_scale);
}
__device__ __forceinline__ v3 ggx_darkening(const float* ggx_E, const float* ggx_Eavg, float mu, float rough, v3 fss)
{
    const float e = lookup_table_read_2D(ggx_E, rough, mu, 0, 32, 32);
    const float e_avg = lookup_table_read(ggx_Eavg, rough, 0, 32);
    return hb_darkening(e, e_avg, fss);
}
__device__ __forceinline__ v3 glass_darkening(const float* glass_E, const float* glass_Eavg, const float* glass_inv_E, const float* glass_inv_Eavg, float mu,
                                              float rough, float ior_in, v3 fss)
{
    float ior = ior_in;
    int umgekehrt = 0;
    if (ior < 1.0f) {
        ior = 1.0f / ior;
        umgekehrt = 1;
    }
    const float z = sqrtf(fabsf((ior - 1.0f) / (ior + 1.0f)));
    float e, e_avg;
    if (umgekehrt == 0) {
        e = lookup_table_read_3D(glass_E, rough, mu, z, 0, 16, 16, 16);
        e_avg = lookup_table_read_2D(glass_Eavg, rough, z, 0, 16, 16);
    } else {
        e = lookup_table_read_3D(glass_inv_E, rough, mu, z, 0, 16, 16, 16);
        e_avg = lookup_table_read_2D(glass_inv_Eavg, rough, z, 0, 16, 16);
    }
    return hb_darkening(e, e_avg, fss);
}
__device__ __forceinline__ float schlick_s_ior(const float* ggx_s_ior, float rough, float cos_ni, float ior)
{
    const float z = sqrtf(fabsf((ior - 1.0f) / (ior + 1.0f)));
    return lookup_table_read_3D(ggx_s_ior, rough, cos_ni, z, 0, 16, 16, 16);
}

__device__ __forceinline__ float mittel3(v3 a) { return (a.c[0] + a.c[1] + a.c[2]) / 3.0f; }
__device__ __forceinline__ v3 null_hoch(v3 a) { return V3(fmaxf(a.c[0], 0.0f), fmaxf(a.c[1], 0.0f), fmaxf(a.c[2], 0.0f)); }

// `maybe_ensure_valid_specular_reflection` → `ensure_valid_specular_reflection`
__device__ v3 gueltige_normale(v3 ng, v3 i, v3 n)
{
    if (n.c[0] == ng.c[0] && n.c[1] == ng.c[1] && n.c[2] == ng.c[2])
        return n;
    const v3 r = sub(mul(2.0f * dot(n, i), n), i);                    // (2·dot(n, i))·n − i
    const float iz = dot(i, ng);
    const float threshold = fminf(0.9f * iz, 0.01f);
    if (dot(ng, r) >= threshold)
        return n;
    v3 x = sub(n, mul(dot(n, ng), ng));
    const float laenge = length(x);
    if (laenge != 0.0f)
        x = mul(x, 1.0f / laenge);
    else
        x = n;
    const float ix = dot(i, x);
    const float a = ix * ix + iz * iz;
    const float b = 2.0f * (a + iz * threshold);
    const float c = (threshold + iz) * (threshold + iz);
    float nz2;
    if (ix < 0.0f)
        nz2 = 0.25f * (b + safe_sqrtf(b * b - 4.0f * a * c)) / a;
    else
        nz2 = 0.25f * (b - safe_sqrtf(b * b - 4.0f * a * c)) / a;
    return add(mul(safe_sqrtf(1.0f - nz2), x), mul(safe_sqrtf(nz2), ng));
}

}  // namespace hb
