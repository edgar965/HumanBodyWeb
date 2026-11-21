// hautnachkerne — die Kerne der Nacharbeit einer Haut-Kachel (21.11.2026, Edgar: „Warp überall raus“; bis dahin Warp-Kerne in `hautnachfilter.py`,
// `hautnachfarbe.py`, `hautnachnormalen.py`, `hautnachumfeld.py`). Zeile für Zeile übertragen, float32 wie dort (die Schwerpunktkoordinaten float64);
// übersetzt mit -fmad=true (Warps Vorgabe `fuse_fp`), min/max/clamp auf Gleitkomma über fminf/fmaxf wie Warp (builtin.h), round = roundf.
// Zähler (vorher `atomic_add`) rechnet der Aufrufer mit torch; der nächste Punkt auf dem Original kommt aus `fl_abfrage` (GarmentCode `Dreiecksbaum`).
#include <cuda_runtime.h>
#include <math.h>

typedef unsigned char u8;

static __device__ __forceinline__ int imin(int a, int b) { return a < b ? a : b; }
static __device__ __forceinline__ int imax(int a, int b) { return a > b ? a : b; }
static __device__ __forceinline__ float klemmen(float x, float a, float b) { return fminf(fmaxf(a, x), b); }
static int bloecke(long long n) { return (int)((n + 255) / 256); }

#define FADEN2(H, W)                                                    \
    const long long _t = (long long)blockIdx.x * blockDim.x + threadIdx.x; \
    if (_t >= (long long)(H) * (W))                                     \
        return;                                                         \
    const int y = (int)(_t / (W)), x = (int)(_t % (W));

// ------------------------------------------------------------------ Filter (`Hautnachfilter`)

// Index außerhalb 0 … n−1 gespiegelt (scipy `reflect`: der Randwert wird wiederholt)
static __device__ __forceinline__ int spiegel(int i, int n)
{
    int r = i;
    while (r < 0 || r >= n) {
        if (r < 0)
            r = -r - 1;
        if (r >= n)
            r = 2 * n - r - 1;
    }
    return r;
}

__global__ void k_gauss_zeilen(int h, int w, const float* __restrict__ quelle, const float* __restrict__ kern, int radius, float* __restrict__ aus)
{
    FADEN2(h, w)
    float s = 0.0f;
    for (int k = -radius; k < radius + 1; ++k)
        s += kern[k + radius] * quelle[(long long)y * w + spiegel(x + k, w)];
    aus[(long long)y * w + x] = s;
}

__global__ void k_gauss_spalten(int h, int w, const float* __restrict__ quelle, const float* __restrict__ kern, int radius, float* __restrict__ aus)
{
    FADEN2(h, w)
    float s = 0.0f;
    for (int k = -radius; k < radius + 1; ++k)
        s += kern[k + radius] * quelle[(long long)spiegel(y + k, h) * w + x];
    aus[(long long)y * w + x] = s;
}

// eine Raute vom Radius `schritte` (L1-Abstand): so weit reicht `schritte`-mal die Dilatation mit dem Kreuz
__global__ void k_dilatieren(int h, int w, const u8* __restrict__ quelle, int schritte, u8* __restrict__ aus)
{
    FADEN2(h, w)
    int gesetzt = 0;
    for (int dy = -schritte; dy < schritte + 1; ++dy) {
        const int yy = y + dy;
        if (yy >= 0 && yy < h) {
            const int rest = schritte - abs(dy);
            for (int dx = -rest; dx < rest + 1; ++dx) {
                const int xx = x + dx;
                if (xx >= 0 && xx < w)
                    if (quelle[(long long)yy * w + xx] != 0)
                        gesetzt = 1;
            }
        }
    }
    aus[(long long)y * w + x] = (u8)gesetzt;
}

#include "hautnachfarbe.cuh"
#include "hautnachnormalen.cuh"
#include "hautnachumfeld.cuh"

extern "C" __declspec(dllexport) int hn_gauss_zeilen(cudaStream_t s, int h, int w, const float* q, const float* k, int r, float* a)
{
    if ((long long)h * w > 0)
        k_gauss_zeilen<<<bloecke((long long)h * w), 256, 0, s>>>(h, w, q, k, r, a);
    return (int)cudaGetLastError();
}

extern "C" __declspec(dllexport) int hn_gauss_spalten(cudaStream_t s, int h, int w, const float* q, const float* k, int r, float* a)
{
    if ((long long)h * w > 0)
        k_gauss_spalten<<<bloecke((long long)h * w), 256, 0, s>>>(h, w, q, k, r, a);
    return (int)cudaGetLastError();
}

extern "C" __declspec(dllexport) int hn_dilatieren(cudaStream_t s, int h, int w, const u8* q, int schritte, u8* a)
{
    if ((long long)h * w > 0)
        k_dilatieren<<<bloecke((long long)h * w), 256, 0, s>>>(h, w, q, schritte, a);
    return (int)cudaGetLastError();
}
