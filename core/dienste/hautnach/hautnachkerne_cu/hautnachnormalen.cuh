// Normalen säubern und Feindetail (`Hautnachnormalen`) — bis 21.11.2026 Warp-Kerne in `hautnachnormalen.py` (`_zaehlen` rechnet jetzt torch).

// Kippung über der Grenze (z < cos(Grad)·|n|), ohne Fehlstellen
__global__ void k_falsche(int h, int w, const u8* __restrict__ normal, const u8* __restrict__ leer, float grenze, u8* __restrict__ aus)
{
    FADEN2(h, w)
    const long long p = (long long)y * w + x;
    const float a = (float)normal[3 * p] / 127.5f - 1.0f;
    const float b = (float)normal[3 * p + 1] / 127.5f - 1.0f;
    const float c = (float)normal[3 * p + 2] / 127.5f - 1.0f;
    const float laenge = sqrtf(a * a + b * b + c * c);
    if (c < grenze * fmaxf(laenge, 1.0e-6f) && leer[p] == 0)
        aus[p] = 1;
    else
        aus[p] = 0;
}

// falsche Treffer (samt Rand, ohne Fehlstellen) werden flach; sonst bleibt der Wert
__global__ void k_flachlegen(int h, int w, const u8* __restrict__ normal, const u8* __restrict__ schlecht, const u8* __restrict__ leer, u8* __restrict__ aus)
{
    FADEN2(h, w)
    const long long p = (long long)y * w + x;
    const bool flach = schlecht[p] != 0 && leer[p] == 0;
    for (int k = 0; k < 3; ++k) {
        if (flach)
            aus[3 * p + k] = (k == 2) ? (u8)255 : (u8)128;
        else
            aus[3 * p + k] = normal[3 * p + k];
    }
}

// Neigung x/z, y/z (z nach unten auf 0,05 begrenzt) und das Gültigkeitsfeld (1 = getroffen)
__global__ void k_neigung(int h, int w, const u8* __restrict__ normal, const u8* __restrict__ leer, float* __restrict__ tx, float* __restrict__ ty,
                          float* __restrict__ gueltig)
{
    FADEN2(h, w)
    const long long p = (long long)y * w + x;
    const float a = (float)normal[3 * p] / 127.5f - 1.0f;
    const float b = (float)normal[3 * p + 1] / 127.5f - 1.0f;
    const float c = fmaxf((float)normal[3 * p + 2] / 127.5f - 1.0f, 0.05f);
    tx[p] = a / c;
    ty[p] = b / c;
    float g = 1.0f;
    if (leer[p] != 0)
        g = 0.0f;
    gueltig[p] = g;
}

// Mittel von feld·gültig und von gültig je t × t-Block; feld/gueltig (hk·t, w), klein/gewicht (hk, wk)
__global__ void k_verkleinern(int hk, int wk, const float* __restrict__ feld, const float* __restrict__ gueltig, int w, int t, float* __restrict__ klein,
                              float* __restrict__ gewicht)
{
    FADEN2(hk, wk)
    float s = 0.0f, g = 0.0f;
    for (int j = 0; j < t; ++j)
        for (int i = 0; i < t; ++i) {
            const long long p = (long long)(y * t + j) * w + (x * t + i);
            const float wert = gueltig[p];
            s += feld[p] * wert;
            g += wert;
        }
    klein[(long long)y * wk + x] = s / (float)(t * t);
    gewicht[(long long)y * wk + x] = g / (float)(t * t);
}

__global__ void k_teilen(long long n, const float* __restrict__ zaehler, const float* __restrict__ nenner, float* __restrict__ aus)
{
    const long long i = (long long)blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n)
        return;
    aus[i] = zaehler[i] / fmaxf(nenner[i], 1.0e-3f);
}

// scipy.ndimage.zoom(…, order=1): die Ränder fallen aufeinander (in = out · (n_in − 1)/(n_out − 1)), dazwischen bilinear
__global__ void k_hochskalieren(int h, int w, const float* __restrict__ klein, int hk, int wk, float* __restrict__ aus)
{
    FADEN2(h, w)
    float fy = 0.0f, fx = 0.0f;
    if (h > 1)
        fy = (float)y * (float)(hk - 1) / (float)(h - 1);
    if (w > 1)
        fx = (float)x * (float)(wk - 1) / (float)(w - 1);
    const int y0 = imin((int)floorf(fy), hk - 1), x0 = imin((int)floorf(fx), wk - 1);
    const int y1 = imin(y0 + 1, hk - 1), x1 = imin(x0 + 1, wk - 1);
    const float wy = fy - (float)y0, wx = fx - (float)x0;
    const float oben = klein[(long long)y0 * wk + x0] * (1.0f - wx) + klein[(long long)y0 * wk + x1] * wx;
    const float unten = klein[(long long)y1 * wk + x0] * (1.0f - wx) + klein[(long long)y1 * wk + x1] * wx;
    aus[(long long)y * w + x] = oben * (1.0f - wy) + unten * wy;
}

// Feindetail = Neigung minus großflächige Neigung; zurück in eine Normale, auf Bytes (round), Fehlstellen flach
__global__ void k_kodieren(int h, int w, const float* __restrict__ tx, const float* __restrict__ ty, const float* __restrict__ tx_tief,
                           const float* __restrict__ ty_tief, const float* __restrict__ gueltig, const u8* __restrict__ leer, u8* __restrict__ aus)
{
    FADEN2(h, w)
    const long long p = (long long)y * w + x;
    const float hx = (tx[p] - tx_tief[p]) * gueltig[p];
    const float hy = (ty[p] - ty_tief[p]) * gueltig[p];
    const float laenge = sqrtf(hx * hx + hy * hy + 1.0f);
    const float w0 = hx / laenge, w1 = hy / laenge, w2 = 1.0f / laenge;
    if (leer[p] != 0) {
        aus[3 * p] = 128;
        aus[3 * p + 1] = 128;
        aus[3 * p + 2] = 255;
    } else {
        aus[3 * p] = (u8)klemmen(roundf((w0 + 1.0f) * 127.5f), 0.0f, 255.0f);
        aus[3 * p + 1] = (u8)klemmen(roundf((w1 + 1.0f) * 127.5f), 0.0f, 255.0f);
        aus[3 * p + 2] = (u8)klemmen(roundf((w2 + 1.0f) * 127.5f), 0.0f, 255.0f);
    }
}

#define HN_GITTER(h, w) bloecke((long long)(h) * (w)), 256, 0, s
#define HN_ENDE return (int)cudaGetLastError()

extern "C" __declspec(dllexport) int hn_falsche(cudaStream_t s, int h, int w, const u8* n, const u8* l, float g, u8* a)
{
    if ((long long)h * w > 0)
        k_falsche<<<HN_GITTER(h, w)>>>(h, w, n, l, g, a);
    HN_ENDE;
}

extern "C" __declspec(dllexport) int hn_flachlegen(cudaStream_t s, int h, int w, const u8* n, const u8* sc, const u8* l, u8* a)
{
    if ((long long)h * w > 0)
        k_flachlegen<<<HN_GITTER(h, w)>>>(h, w, n, sc, l, a);
    HN_ENDE;
}

extern "C" __declspec(dllexport) int hn_neigung(cudaStream_t s, int h, int w, const u8* n, const u8* l, float* tx, float* ty, float* g)
{
    if ((long long)h * w > 0)
        k_neigung<<<HN_GITTER(h, w)>>>(h, w, n, l, tx, ty, g);
    HN_ENDE;
}

// (hk, wk) = Größe des kleinen Felds; wv = Breite des vollen
extern "C" __declspec(dllexport) int hn_verkleinern(cudaStream_t s, int hk, int wk, const float* f, const float* g, int wv, int t, float* k, float* ge)
{
    if ((long long)hk * wk > 0)
        k_verkleinern<<<HN_GITTER(hk, wk)>>>(hk, wk, f, g, wv, t, k, ge);
    HN_ENDE;
}

extern "C" __declspec(dllexport) int hn_hochskalieren(cudaStream_t s, int h, int w, const float* k, int hk, int wk, float* a)
{
    if ((long long)h * w > 0)
        k_hochskalieren<<<HN_GITTER(h, w)>>>(h, w, k, hk, wk, a);
    HN_ENDE;
}

extern "C" __declspec(dllexport) int hn_kodieren(cudaStream_t s, int h, int w, const float* tx, const float* ty, const float* txt, const float* tyt,
                                                 const float* g, const u8* l, u8* a)
{
    if ((long long)h * w > 0)
        k_kodieren<<<HN_GITTER(h, w)>>>(h, w, tx, ty, txt, tyt, g, l, a);
    HN_ENDE;
}

extern "C" __declspec(dllexport) int hn_teilen(cudaStream_t s, long long n, const float* z, const float* nn, float* a)
{
    if (n > 0)
        k_teilen<<<bloecke(n), 256, 0, s>>>(n, z, nn, a);
    return (int)cudaGetLastError();
}
