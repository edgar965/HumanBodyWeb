// hautkartekerne — die Kerne der Haut-Maske auf der Karte (21.11.2026, Edgar: „Warp überall raus“; bis dahin Warp: `hautkartewarphilfe.py`,
// `hautkartewarpeinzug.py`, `hautkartewarpmaske.py`, Kerne in `hautkartenormalen.py`, 18.11.2026). Zeile für Zeile übertragen.
// Die Kerne bilden `gemeinsam/hautmaske*.js` nach: JS rechnet in double ohne FMA — übersetzt mit -fmad=false (wie Warps `fuse_fp: False`), dieselbe
// Reihenfolge der Rechenschritte. min/max auf double über fmin/fmax wie Warp (builtin.h `_wp_native_fmin`). Gitter wie `Hautmaskegeometrie.punktgitter`:
// Zelle floor(p / h), Schlüssel `zelle(i, j, k)`, je Zelle die Punkte aufsteigend (`Hautkartegitter`).
#include <cuda_runtime.h>
#include <math.h>

typedef long long i64;
typedef unsigned char u8;

static __device__ __forceinline__ i64 zellschluessel(i64 i, i64 j, i64 k)
{
    return ((i + (i64)1024) * (i64)2048 + (j + (i64)1024)) * (i64)2048 + (k + (i64)1024);
}

static __device__ __forceinline__ i64 zellnummer(double x, double h) { return (i64)floor(x / h); }

static __device__ __forceinline__ int untergrenze(const i64* schl, i64 n, i64 wert)
{
    int lo = 0, hi = (int)n;
    while (lo < hi) {
        const int mitte = (lo + hi) / 2;
        if (schl[mitte] < wert)
            lo = mitte + 1;
        else
            hi = mitte;
    }
    return lo;
}

// V8s `Math.hypot` (src/builtins/math.tq): größter Betrag, Quotienten mit Kahan summiert, Wurzel mal Größtem
static __device__ double hypot3(double x, double y, double z)
{
    const double ax = fabs(x), ay = fabs(y), az = fabs(z);
    double m = ax;
    if (ay > m)
        m = ay;
    if (az > m)
        m = az;
    if (m == 0.0)
        return 0.0;
    double s = 0.0, c = 0.0, n, summand, vorl;
    n = ax / m;
    summand = n * n - c;
    vorl = s + summand;
    c = (vorl - s) - summand;
    s = vorl;
    n = ay / m;
    summand = n * n - c;
    vorl = s + summand;
    c = (vorl - s) - summand;
    s = vorl;
    n = az / m;
    summand = n * n - c;
    vorl = s + summand;
    c = (vorl - s) - summand;
    s = vorl;
    return sqrt(s) * m;
}

// `Hautmaskegeometrie.strahlDreieck` (Möller–Trumbore, beidseitig); kein Treffer: NaN
static __device__ double strahl_dreieck(const double* P, int a, int b, int c, double px, double py, double pz, double rx, double ry, double rz)
{
    const double ax = P[3 * a], ay = P[3 * a + 1], az = P[3 * a + 2];
    const double e1x = P[3 * b] - ax, e1y = P[3 * b + 1] - ay, e1z = P[3 * b + 2] - az;
    const double e2x = P[3 * c] - ax, e2y = P[3 * c + 1] - ay, e2z = P[3 * c + 2] - az;
    const double hx = ry * e2z - rz * e2y, hy = rz * e2x - rx * e2z, hz = rx * e2y - ry * e2x;
    const double det = e1x * hx + e1y * hy + e1z * hz;
    const double keins = nan("");
    if (det > -1e-12 && det < 1e-12)
        return keins;
    const double f = 1.0 / det;
    const double sx = px - ax, sy = py - ay, sz = pz - az;
    const double u = f * (sx * hx + sy * hy + sz * hz);
    if (u < 0.0 || u > 1.0)
        return keins;
    const double qx = sy * e1z - sz * e1y, qy = sz * e1x - sx * e1z, qz = sx * e1y - sy * e1x;
    const double v = f * (rx * qx + ry * qy + rz * qz);
    if (v < 0.0 || u + v > 1.0)
        return keins;
    return f * (e2x * qx + e2y * qy + e2z * qz);
}

// `Hautmaskegeometrie.naechsterPunkt`: nächster Punkt in den 27 Zellen — bj = −1 ohne Punkt
static __device__ void naechster(const double* P, const i64* schl, i64 nschl, const i64* folge, double h, double px, double py, double pz, double& bj,
                                 double& best)
{
    const i64 ci = zellnummer(px, h), cj = zellnummer(py, h), ck = zellnummer(pz, h);
    best = INFINITY;
    bj = -1.0;
    for (int a = -1; a < 2; ++a)
        for (int b = -1; b < 2; ++b)
            for (int c = -1; c < 2; ++c) {
                const i64 s = zellschluessel(ci + (i64)a, cj + (i64)b, ck + (i64)c);
                int p = untergrenze(schl, nschl, s);
                while (p < nschl && schl[p] == s) {
                    const int j = (int)folge[p];
                    const double dx = P[3 * j] - px, dy = P[3 * j + 1] - py, dz = P[3 * j + 2] - pz;
                    const double d2 = dx * dx + dy * dy + dz * dz;
                    if (d2 < best) {
                        best = d2;
                        bj = (double)j;
                    }
                    p = p + 1;
                }
            }
}

#include "hautkarteeinzug.cuh"
#include "hautkartemaske.cuh"
#include "hautkartenormalen.cuh"
