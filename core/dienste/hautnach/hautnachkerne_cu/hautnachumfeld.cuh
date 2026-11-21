// Umfeld des Scham-Stücks (`Hautnachumfeld`) — bis 21.11.2026 Warp-Kerne `_rastern`, `_sammeln`, `_naechster` in `hautnachumfeld.py`.
// `_zaehlen` und die Sammelreihenfolge (vorher `atomic_add` + lexsort) macht torch (`nonzero` zeilenweise = dieselbe Ordnung); der nächste Punkt auf dem
// Original kommt aus `fl_abfrage` (`Dreiecksbaum`, Warps `mesh_query_point_no_sign`), hier nur UV und Farbe daran.

// Schwerpunktkoordinaten (l1, l2, l3) des Punkts (x, y) im UV-Dreieck t (Pixel; px je Dreieck a0 a1 b0 b1 c0 c1) — bei entartetem Dreieck (−1, −1, −1)
static __device__ __forceinline__ void bary(const double* px, int t, double x, double y, double& l1, double& l2, double& l3)
{
    const double a0 = px[6 * t], a1 = px[6 * t + 1], b0 = px[6 * t + 2], b1 = px[6 * t + 3], c0 = px[6 * t + 4], c1 = px[6 * t + 5];
    const double det = (b1 - c1) * (a0 - c0) + (c0 - b0) * (a1 - c1);
    if (fabs(det) < 1.0e-9) {
        l1 = -1.0;
        l2 = -1.0;
        l3 = -1.0;
        return;
    }
    l1 = ((b1 - c1) * (x - c0) + (c0 - b0) * (y - c1)) / det;
    l2 = ((c1 - a1) * (x - c0) + (a0 - c0) * (y - c1)) / det;
    l3 = 1.0 - l1 - l2;
}

// je Dreieck die Texel seines Rechtecks: im Dreieck → atomicMax(innen, t), in der Zugabe `rand` → atomicMin(zugabe, t)
__global__ void k_rastern(int nt, const double* __restrict__ px, double rand, int hoehe, int breite, int* __restrict__ innen, int* __restrict__ zugabe)
{
    const int t = blockIdx.x * blockDim.x + threadIdx.x;
    if (t >= nt)
        return;
    const double xs0 = fmin(px[6 * t], fmin(px[6 * t + 2], px[6 * t + 4]));
    const double xs1 = fmax(px[6 * t], fmax(px[6 * t + 2], px[6 * t + 4]));
    const double ys0 = fmin(px[6 * t + 1], fmin(px[6 * t + 3], px[6 * t + 5]));
    const double ys1 = fmax(px[6 * t + 1], fmax(px[6 * t + 3], px[6 * t + 5]));
    const int x0 = imax((int)floor(xs0) - 1, 0), x1 = imin((int)ceil(xs1) + 2, breite);
    const int y0 = imax((int)floor(ys0) - 1, 0), y1 = imin((int)ceil(ys1) + 2, hoehe);
    for (int gy = y0; gy < y1; ++gy)
        for (int gx = x0; gx < x1; ++gx) {
            double l1, l2, l3;
            bary(px, t, (double)gx + 0.5, (double)gy + 0.5, l1, l2, l3);
            const double kleinste = fmin(l1, fmin(l2, l3));
            if (kleinste >= 0.0)
                atomicMax(&innen[(long long)gy * breite + gx], t);
            else if (kleinste >= -rand)
                atomicMin(&zugabe[(long long)gy * breite + gx], t);
        }
}

// die Schwerpunktkoordinaten der gesammelten Texel (Zeile, Spalte, Dreieck) — wie in `_sammeln`
__global__ void k_bary(int n, const double* __restrict__ px, const int* __restrict__ eigner, const long long* __restrict__ zeile,
                       const long long* __restrict__ spalte, double* __restrict__ lam)
{
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n)
        return;
    double l1, l2, l3;
    bary(px, eigner[i], (double)spalte[i] + 0.5, (double)zeile[i] + 0.5, l1, l2, l3);
    lam[3 * i] = l1;
    lam[3 * i + 1] = l2;
    lam[3 * i + 2] = l3;
}

// UV am nächsten Punkt (Fläche, u, v aus `fl_abfrage`) und die Farbe daran (bilinear, Texelmitten bei ganzen Zahlen, außen geklemmt); bild (H, W, 3)
__global__ void k_abtasten(int n, const int* __restrict__ treffer, const int* __restrict__ flaeche, const float* __restrict__ u_feld,
                           const float* __restrict__ v_feld, const float* __restrict__ uv_ecken, const u8* __restrict__ bild, int hoehe, int breite,
                           float* __restrict__ farbe, int* __restrict__ gefunden)
{
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n)
        return;
    if (!treffer[i]) {
        gefunden[i] = 0;
        return;
    }
    gefunden[i] = 1;
    const long long f = flaeche[i];
    const float u = u_feld[i], v = v_feld[i], w = 1.0f - u - v;
    const float* a = uv_ecken + 6 * f;
    const float uvx = a[0] * u + a[2] * v + a[4] * w;
    const float uvy = a[1] * u + a[3] * v + a[5] * w;
    const float x = klemmen(uvx * (float)breite - 0.5f, 0.0f, (float)breite - 1.0001f);
    const float y = klemmen((1.0f - uvy) * (float)hoehe - 0.5f, 0.0f, (float)hoehe - 1.0001f);
    const int x0 = (int)floorf(x), y0 = (int)floorf(y);
    const float fx = x - (float)x0, fy = y - (float)y0;
    const long long o = ((long long)y0 * breite + x0) * 3, un = ((long long)(y0 + 1) * breite + x0) * 3;
    for (int k = 0; k < 3; ++k) {
        const float oben = (float)bild[o + k] * (1.0f - fx) + (float)bild[o + 3 + k] * fx;
        const float unten = (float)bild[un + k] * (1.0f - fx) + (float)bild[un + 3 + k] * fx;
        farbe[3 * (long long)i + k] = oben * (1.0f - fy) + unten * fy;
    }
}

extern "C" __declspec(dllexport) int hn_rastern(cudaStream_t s, int nt, const double* px, double rand, int hoehe, int breite, int* innen, int* zugabe)
{
    if (nt > 0)
        k_rastern<<<bloecke(nt), 256, 0, s>>>(nt, px, rand, hoehe, breite, innen, zugabe);
    return (int)cudaGetLastError();
}

extern "C" __declspec(dllexport) int hn_bary(cudaStream_t s, int n, const double* px, const int* eigner, const long long* zeile, const long long* spalte,
                                             double* lam)
{
    if (n > 0)
        k_bary<<<bloecke(n), 256, 0, s>>>(n, px, eigner, zeile, spalte, lam);
    return (int)cudaGetLastError();
}

extern "C" __declspec(dllexport) int hn_abtasten(cudaStream_t s, int n, const int* treffer, const int* flaeche, const float* u, const float* v,
                                                 const float* uv_ecken, const u8* bild, int hoehe, int breite, float* farbe, int* gefunden)
{
    if (n > 0)
        k_abtasten<<<bloecke(n), 256, 0, s>>>(n, treffer, flaeche, u, v, uv_ecken, bild, hoehe, breite, farbe, gefunden);
    return (int)cudaGetLastError();
}
