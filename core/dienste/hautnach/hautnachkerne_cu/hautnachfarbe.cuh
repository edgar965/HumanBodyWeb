// Farbangleich (`Hautnachfarbe`) — bis 21.11.2026 Warp-Kerne `_bloecke`, `_ueberblenden`, `_anwenden` in `hautnachfarbe.py`.

// je grobem Pixel: Anteil gültig und Mittel der gültigen gebackenen Farbe, daraus Gewicht und gewichteter Unterschied Gebackenes − Ersatz
// farbe (H, W, 3), gueltig (H, W) — W wie farbe.shape[1] —, ersatz (h, w, 3)
__global__ void k_bloecke(int h, int w, const u8* __restrict__ farbe, const u8* __restrict__ gueltig, int W, int faktor, const u8* __restrict__ ersatz,
                          int weiss, float* __restrict__ gewicht, float* __restrict__ uf0, float* __restrict__ uf1, float* __restrict__ uf2)
{
    FADEN2(h, w)
    const float n = (float)(faktor * faktor);
    float anteil = 0.0f, s0 = 0.0f, s1 = 0.0f, s2 = 0.0f;
    for (int j = 0; j < faktor; ++j)
        for (int i = 0; i < faktor; ++i) {
            const long long p = (long long)(y * faktor + j) * W + (x * faktor + i);
            if (gueltig[p] != 0) {
                anteil += 1.0f;
                s0 += (float)farbe[3 * p];
                s1 += (float)farbe[3 * p + 1];
                s2 += (float)farbe[3 * p + 2];
            }
        }
    anteil = anteil / n;
    const long long e = 3 * ((long long)y * w + x);
    const long long q = (long long)y * w + x;
    const int helligkeit = imin((int)ersatz[e], imin((int)ersatz[e + 1], (int)ersatz[e + 2]));
    if (helligkeit < weiss && anteil > 0.0f) {
        gewicht[q] = anteil;
        const float m = 1.0f / fmaxf(anteil * n, 1.0e-6f);
        uf0[q] = (s0 * m - (float)ersatz[e]) * anteil;
        uf1[q] = (s1 * m - (float)ersatz[e + 1]) * anteil;
        uf2[q] = (s2 * m - (float)ersatz[e + 2]) * anteil;
    } else {
        gewicht[q] = 0.0f;
        uf0[q] = 0.0f;
        uf1[q] = 0.0f;
        uf2[q] = 0.0f;
    }
}

// ein Maßstab: wo er genug Fläche sieht (g / MIN_GEWICHT, bis 1), gilt sein Versatz, sonst der gröbere
__global__ void k_ueberblenden(int h, int w, const float* __restrict__ g, const float* __restrict__ d0, const float* __restrict__ d1,
                               const float* __restrict__ d2, float min_gewicht, float* __restrict__ e0, float* __restrict__ e1, float* __restrict__ e2)
{
    FADEN2(h, w)
    const long long q = (long long)y * w + x;
    const float a = klemmen(g[q] / min_gewicht, 0.0f, 1.0f);
    const float n = fmaxf(g[q], 1.0e-6f);
    e0[q] = e0[q] * (1.0f - a) + (d0[q] / n) * a;
    e1[q] = e1[q] * (1.0f - a) + (d1[q] / n) * a;
    e2[q] = e2[q] * (1.0f - a) + (d2[q] / n) * a;
}

// Position im groben Raster zu Pixel i des feinen (Mitte auf Mitte, geklemmt)
static __device__ __forceinline__ float zeiger(int i, int faktor, int n)
{
    return klemmen(((float)i + 0.5f) / (float)faktor - 0.5f, 0.0f, (float)(n - 1));
}

// auf den Fehlstellen der vollen Kachel (nicht weiß) den bilinear hochgerechneten Versatz addieren, auf 0 … 255 klemmen; voll (H, W, 3), e* (h, w)
__global__ void k_anwenden(int H, int W, u8* __restrict__ voll, const u8* __restrict__ ungueltig, const float* __restrict__ e0, const float* __restrict__ e1,
                           const float* __restrict__ e2, int h, int w, int faktor, int weiss)
{
    FADEN2(H, W)
    const long long p = (long long)y * W + x;
    if (ungueltig[p] == 0)
        return;
    if (imin((int)voll[3 * p], imin((int)voll[3 * p + 1], (int)voll[3 * p + 2])) >= weiss)
        return;
    const float fy = zeiger(y, faktor, h), fx = zeiger(x, faktor, w);
    const int y0 = (int)floorf(fy), x0 = (int)floorf(fx);
    const int y1 = imin(y0 + 1, h - 1), x1 = imin(x0 + 1, w - 1);
    const float wy = fy - (float)y0, wx = fx - (float)x0;
    const long long a = (long long)y0 * w, b = (long long)y1 * w;
    const float d0 = (e0[a + x0] * (1.0f - wx) + e0[a + x1] * wx) * (1.0f - wy) + (e0[b + x0] * (1.0f - wx) + e0[b + x1] * wx) * wy;
    const float d1 = (e1[a + x0] * (1.0f - wx) + e1[a + x1] * wx) * (1.0f - wy) + (e1[b + x0] * (1.0f - wx) + e1[b + x1] * wx) * wy;
    const float d2 = (e2[a + x0] * (1.0f - wx) + e2[a + x1] * wx) * (1.0f - wy) + (e2[b + x0] * (1.0f - wx) + e2[b + x1] * wx) * wy;
    voll[3 * p] = (u8)klemmen((float)voll[3 * p] + d0, 0.0f, 255.0f);
    voll[3 * p + 1] = (u8)klemmen((float)voll[3 * p + 1] + d1, 0.0f, 255.0f);
    voll[3 * p + 2] = (u8)klemmen((float)voll[3 * p + 2] + d2, 0.0f, 255.0f);
}

extern "C" __declspec(dllexport) int hn_bloecke(cudaStream_t s, int h, int w, const u8* farbe, const u8* gueltig, int W, int faktor, const u8* ersatz,
                                                int weiss, float* gewicht, float* uf0, float* uf1, float* uf2)
{
    if ((long long)h * w > 0)
        k_bloecke<<<bloecke((long long)h * w), 256, 0, s>>>(h, w, farbe, gueltig, W, faktor, ersatz, weiss, gewicht, uf0, uf1, uf2);
    return (int)cudaGetLastError();
}

extern "C" __declspec(dllexport) int hn_ueberblenden(cudaStream_t s, int h, int w, const float* g, const float* d0, const float* d1, const float* d2,
                                                     float min_gewicht, float* e0, float* e1, float* e2)
{
    if ((long long)h * w > 0)
        k_ueberblenden<<<bloecke((long long)h * w), 256, 0, s>>>(h, w, g, d0, d1, d2, min_gewicht, e0, e1, e2);
    return (int)cudaGetLastError();
}

extern "C" __declspec(dllexport) int hn_anwenden(cudaStream_t s, int H, int W, u8* voll, const u8* ungueltig, const float* e0, const float* e1,
                                                 const float* e2, int h, int w, int faktor, int weiss)
{
    if ((long long)H * W > 0)
        k_anwenden<<<bloecke((long long)H * W), 256, 0, s>>>(H, W, voll, ungueltig, e0, e1, e2, h, w, faktor, weiss);
    return (int)cudaGetLastError();
}
