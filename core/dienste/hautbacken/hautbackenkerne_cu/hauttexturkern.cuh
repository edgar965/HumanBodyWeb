// hauttexturkern.cuh — ein Bild abtasten wie Cycles (bis 21.11.2026 Warp-Kern `abtasten` in `graph/hauttexturkernel.py`; Quellen kernel/util/image.h,
// kernel/svm/image.h): Wiederholen/Erweitern/Klemmen/Spiegeln, nächster Nachbar, bilinear, kubisch (B-Spline); Bild unten-zuerst als RGBA mit 16 Bit je Kanal.
#pragma once
#include "hautfunktionen.cuh"

namespace hb {

__device__ __forceinline__ int frac_i(float x)
{
    int r = (int)x;
    if (x < 0.0f)
        r = r - 1;
    return r;
}
__device__ __forceinline__ int wrap_periodic(int x_in, int breite)
{
    int x = x_in % breite;
    if (x < 0)
        x = x + breite;
    return x;
}
__device__ __forceinline__ int wrap_mirror(int x, int breite)
{
    int xx = x;
    if (x < 0)
        xx = x + 1;
    const int m = abs(xx) % (2 * breite);
    if (m >= breite)
        return 2 * breite - m - 1;
    return m;
}
__device__ __forceinline__ v4 lies_bild(const u16* daten, int x, int y, int breite, int hoehe)
{
    if (x < 0 || x >= breite || y < 0 || y >= hoehe)
        return V4(0.0f, 0.0f, 0.0f, 0.0f);
    const long long k = ((long long)y * breite + x) * 4;
    const float s = 1.0f / 65535.0f;
    return V4((float)daten[k] * s, (float)daten[k + 1] * s, (float)daten[k + 2] * s, (float)daten[k + 3] * s);
}
__device__ __forceinline__ float spline_gewicht(float t, int k)
{
    if (k == 0)
        return (((-1.0f / 6.0f) * t + 0.5f) * t - 0.5f) * t + (1.0f / 6.0f);
    if (k == 1)
        return ((0.5f * t - 1.0f) * t) * t + (2.0f / 3.0f);
    if (k == 2)
        return ((-0.5f * t + 0.5f) * t + 0.5f) * t + (1.0f / 6.0f);
    return (1.0f / 6.0f) * t * t * t;
}
__device__ v4 bild_naechster(const u16* d, int breite, int hoehe, float x, float y, int erw)
{
    int ix = frac_i(x), iy = frac_i(y);
    if (erw == 0) {
        ix = wrap_periodic(ix, breite);
        iy = wrap_periodic(iy, hoehe);
    } else if (erw == 2) {
        if (ix < 0 || ix >= breite || iy < 0 || iy >= hoehe)
            return V4(0.0f, 0.0f, 0.0f, 0.0f);
    } else if (erw == 1) {
        ix = iclamp(ix, 0, breite - 1);
        iy = iclamp(iy, 0, hoehe - 1);
    } else {
        ix = wrap_mirror(ix, breite);
        iy = wrap_mirror(iy, hoehe);
    }
    return lies_bild(d, ix, iy, breite, hoehe);
}
__device__ v4 bild_linear(const u16* d, int breite, int hoehe, float x, float y, int erw)
{
    int ix = frac_i(x - 0.5f), iy = frac_i(y - 0.5f);
    const float tx = (x - 0.5f) - (float)ix, ty = (y - 0.5f) - (float)iy;
    int nix = ix + 1, niy = iy + 1;
    if (erw == 0) {
        ix = wrap_periodic(ix, breite);
        nix = wrap_periodic(ix + 1, breite);
        iy = wrap_periodic(iy, hoehe);
        niy = wrap_periodic(iy + 1, hoehe);
    } else if (erw == 2) {
        if (ix < -1 || ix >= breite || iy < -1 || iy >= hoehe)
            return V4(0.0f, 0.0f, 0.0f, 0.0f);
    } else if (erw == 1) {
        nix = iclamp(ix + 1, 0, breite - 1);
        ix = iclamp(ix, 0, breite - 1);
        niy = iclamp(iy + 1, 0, hoehe - 1);
        iy = iclamp(iy, 0, hoehe - 1);
    } else {
        nix = wrap_mirror(ix + 1, breite);
        ix = wrap_mirror(ix, breite);
        niy = wrap_mirror(iy + 1, hoehe);
        iy = wrap_mirror(iy, hoehe);
    }
    return add(add(add(mul((1.0f - ty) * (1.0f - tx), lies_bild(d, ix, iy, breite, hoehe)), mul((1.0f - ty) * tx, lies_bild(d, nix, iy, breite, hoehe))),
                   mul(ty * (1.0f - tx), lies_bild(d, ix, niy, breite, hoehe))),
               mul(ty * tx, lies_bild(d, nix, niy, breite, hoehe)));
}
__device__ v4 bild_kubisch(const u16* d, int breite, int hoehe, float x, float y, int erw)
{
    int ix = frac_i(x - 0.5f), iy = frac_i(y - 0.5f);
    const float tx = (x - 0.5f) - (float)ix, ty = (y - 0.5f) - (float)iy;
    int pix = ix - 1, nix = ix + 1, nnix = ix + 2, piy = iy - 1, niy = iy + 1, nniy = iy + 2;
    if (erw == 0) {
        ix = wrap_periodic(ix, breite);
        pix = wrap_periodic(ix - 1, breite);
        nix = wrap_periodic(ix + 1, breite);
        nnix = wrap_periodic(ix + 2, breite);
        iy = wrap_periodic(iy, hoehe);
        piy = wrap_periodic(iy - 1, hoehe);
        niy = wrap_periodic(iy + 1, hoehe);
        nniy = wrap_periodic(iy + 2, hoehe);
    } else if (erw == 2) {
        if (ix < -2 || ix > breite || iy < -2 || iy > hoehe)
            return V4(0.0f, 0.0f, 0.0f, 0.0f);
    } else if (erw == 1) {
        pix = iclamp(ix - 1, 0, breite - 1);
        nix = iclamp(ix + 1, 0, breite - 1);
        nnix = iclamp(ix + 2, 0, breite - 1);
        ix = iclamp(ix, 0, breite - 1);
        piy = iclamp(iy - 1, 0, hoehe - 1);
        niy = iclamp(iy + 1, 0, hoehe - 1);
        nniy = iclamp(iy + 2, 0, hoehe - 1);
        iy = iclamp(iy, 0, hoehe - 1);
    } else {
        pix = wrap_mirror(ix - 1, breite);
        nix = wrap_mirror(ix + 1, breite);
        nnix = wrap_mirror(ix + 2, breite);
        ix = wrap_mirror(ix, breite);
        piy = wrap_mirror(iy - 1, hoehe);
        niy = wrap_mirror(iy + 1, hoehe);
        nniy = wrap_mirror(iy + 2, hoehe);
        iy = wrap_mirror(iy, hoehe);
    }
    v4 s = V4(0.0f, 0.0f, 0.0f, 0.0f);
    for (int j = 0; j < 4; ++j) {
        int yy = piy;
        if (j == 1)
            yy = iy;
        else if (j == 2)
            yy = niy;
        else if (j == 3)
            yy = nniy;
        const v4 zeile = mul(spline_gewicht(ty, j),
                             add(add(add(mul(spline_gewicht(tx, 0), lies_bild(d, pix, yy, breite, hoehe)), mul(spline_gewicht(tx, 1), lies_bild(d, ix, yy, breite, hoehe))),
                                     mul(spline_gewicht(tx, 2), lies_bild(d, nix, yy, breite, hoehe))),
                                 mul(spline_gewicht(tx, 3), lies_bild(d, nnix, yy, breite, hoehe))));
        s = add(s, zeile);
    }
    return s;
}

// `svm_node_tex_image` (FLAT) + `svm_image_texture`: Pixelkoordinate (u · Breite, v · Höhe), abtasten, Alpha ent-assoziieren, sRGB nach der Interpolation
__global__ void k_abtasten(int n, const u16* daten, int breite, int hoehe, const float* koordinate, int interpolation, int erweiterung, int srgb,
                           int entassoziieren, float* aus)
{
    HB_FADEN(n)
    const float x = koordinate[3 * i] * (float)breite;
    const float y = koordinate[3 * i + 1] * (float)hoehe;
    v4 r;
    if (interpolation == 1)
        r = bild_naechster(daten, breite, hoehe, x, y, erweiterung);
    else if (interpolation == 0)
        r = bild_linear(daten, breite, hoehe, x, y, erweiterung);
    else
        r = bild_kubisch(daten, breite, hoehe, x, y, erweiterung);
    const float alpha = r.c[3];
    if (entassoziieren > 0 && alpha != 1.0f && alpha != 0.0f) {
        r = div(r, alpha);
        r = V4(r.c[0], r.c[1], r.c[2], alpha);
    }
    if (srgb > 0)
        r = V4(color_srgb_to_linear(r.c[0]), color_srgb_to_linear(r.c[1]), color_srgb_to_linear(r.c[2]), r.c[3]);
    schreib4(aus, i, r);
}

HB_EXPORT hb_abtasten(void* s, int n, const u16* daten, int breite, int hoehe, const float* koordinate, int interpolation, int erweiterung, int srgb,
                      int entassoziieren, float* aus)
{
    if (n > 0)
        k_abtasten<<<HB_GITTER(n)>>>(n, daten, breite, hoehe, koordinate, interpolation, erweiterung, srgb, entassoziieren, aus);
    HB_ENDE;
}

}  // namespace hb
