// Maske (`Hautmaske`, `Hautmaskeersatz`, `Hautdurchsicht`; Aufrufer `Hautkartemaske`) — bis 21.11.2026 `hautkartewarpmaske.py`. Je Körperpunkt ein Faden,
// dieselben Schleifen wie JS; jeder Faden schreibt nur seinen Punkt, die Stücke laufen nacheinander.

// `Hautmaskegeometrie.punktDreieckAbstand2` (Ericson)
static __device__ double punkt_dreieck2(const double* P, int a, int b, int c, double px, double py, double pz)
{
    const double ax = P[3 * a], ay = P[3 * a + 1], az = P[3 * a + 2];
    const double bx = P[3 * b], by = P[3 * b + 1], bz = P[3 * b + 2];
    const double cx = P[3 * c], cy = P[3 * c + 1], cz = P[3 * c + 2];
    const double abx = bx - ax, aby = by - ay, abz = bz - az;
    const double acx = cx - ax, acy = cy - ay, acz = cz - az;
    const double apx = px - ax, apy = py - ay, apz = pz - az;
    const double d1 = abx * apx + aby * apy + abz * apz;
    const double d2 = acx * apx + acy * apy + acz * apz;
    if (d1 <= 0.0 && d2 <= 0.0)
        return apx * apx + apy * apy + apz * apz;
    const double bpx = px - bx, bpy = py - by, bpz = pz - bz;
    const double d3 = abx * bpx + aby * bpy + abz * bpz;
    const double d4 = acx * bpx + acy * bpy + acz * bpz;
    if (d3 >= 0.0 && d4 <= d3)
        return bpx * bpx + bpy * bpy + bpz * bpz;
    const double vc = d1 * d4 - d3 * d2;
    if (vc <= 0.0 && d1 >= 0.0 && d3 <= 0.0) {
        const double t = d1 / (d1 - d3);
        const double qx = ax + t * abx - px, qy = ay + t * aby - py, qz = az + t * abz - pz;
        return qx * qx + qy * qy + qz * qz;
    }
    const double cpx = px - cx, cpy = py - cy, cpz = pz - cz;
    const double d5 = abx * cpx + aby * cpy + abz * cpz;
    const double d6 = acx * cpx + acy * cpy + acz * cpz;
    if (d6 >= 0.0 && d5 <= d6)
        return cpx * cpx + cpy * cpy + cpz * cpz;
    const double vb = d5 * d2 - d1 * d6;
    if (vb <= 0.0 && d2 >= 0.0 && d6 <= 0.0) {
        const double t = d2 / (d2 - d6);
        const double qx = ax + t * acx - px, qy = ay + t * acy - py, qz = az + t * acz - pz;
        return qx * qx + qy * qy + qz * qz;
    }
    const double va = d3 * d6 - d5 * d4;
    if (va <= 0.0 && (d4 - d3) >= 0.0 && (d5 - d6) >= 0.0) {
        const double t = (d4 - d3) / ((d4 - d3) + (d5 - d6));
        const double qx = bx + t * (cx - bx) - px, qy = by + t * (cy - by) - py, qz = bz + t * (cz - bz) - pz;
        return qx * qx + qy * qy + qz * qz;
    }
    const double nenner = 1.0 / (va + vb + vc);
    const double v = vb * nenner, w = vc * nenner;
    const double qx = ax + abx * v + acx * w - px, qy = ay + aby * v + acy * w - py, qz = az + abz * v + acz * w - pz;
    return qx * qx + qy * qy + qz * qz;
}

static __device__ __forceinline__ bool in_huelle(double px, double py, double pz, const double* hl)
{
    return !(px < hl[0] || px > hl[3] || py < hl[1] || py > hl[4] || pz < hl[2] || pz > hl[5]);
}

// Treffer (1/0); n2 = Abstand² für den Abstandstest (inf ohne)
static __device__ double pruefe(const double* S, const i64* ST, int k, double px, double py, double pz, double nx, double ny, double nz, double tiefe,
                                double abstand, double nahe, double& n2)
{
    const int a = (int)ST[3 * k], b = (int)ST[3 * k + 1], c = (int)ST[3 * k + 2];
    const double t = strahl_dreieck(S, a, b, c, px, py, pz, nx, ny, nz);
    if (!isnan(t) && t >= -tiefe && t <= abstand)
        return 1.0;
    if (nahe > 0.0) {
        const double d2 = punkt_dreieck2(S, a, b, c, px, py, pz);
        if (d2 < n2)
            n2 = d2;
    }
    return 0.0;
}

// `Hautmaske.lockereRandpunkte` (je Randpunkt des Stoffs)
__global__ void k_locker(int nr, const double* __restrict__ S, const i64* __restrict__ rand, const double* __restrict__ K, const double* __restrict__ N,
                         const i64* __restrict__ kschl, i64 nkschl, const i64* __restrict__ kfolge, double h, double eng, u8* __restrict__ aus)
{
    const int t = blockIdx.x * blockDim.x + threadIdx.x;
    if (t >= nr)
        return;
    const int v = (int)rand[t];
    const double qx = S[3 * v], qy = S[3 * v + 1], qz = S[3 * v + 2];
    double bj, best;
    naechster(K, kschl, nkschl, kfolge, h, qx, qy, qz, bj, best);
    if (bj < 0.0) {
        aus[v] = 1;
        return;
    }
    const int i = (int)bj;
    const double d = (qx - K[3 * i]) * N[3 * i] + (qy - K[3 * i + 1]) * N[3 * i + 1] + (qz - K[3 * i + 2]) * N[3 * i + 2];
    if (fabs(d) > eng)
        aus[v] = 1;
}

// `Hautmaske._einStueck`: nächster Stoffpunkt in den 27 Zellen, dann die Dreiecke um ihn (zwei Nachbarringe, nur erlaubte), Strahl entlang der Normale,
// bei starren Stücken der Abstandstest
__global__ void k_stueck(int n, const double* __restrict__ K, const double* __restrict__ N, const double* __restrict__ S, const i64* __restrict__ ST,
                         const i64* __restrict__ sschl, i64 nsschl, const i64* __restrict__ sfolge, double h, const double* __restrict__ hl, double grenze2,
                         double tiefe, double abstand, double nahe, const i64* __restrict__ nach_a, const i64* __restrict__ nach_z,
                         const i64* __restrict__ inz_a, const i64* __restrict__ inz_z, double wert, u8* __restrict__ maske, float* __restrict__ nachgeben)
{
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n)
        return;
    if (maske[i] != 0 && !(wert > (double)nachgeben[i]))
        return;
    const double px = K[3 * i], py = K[3 * i + 1], pz = K[3 * i + 2];
    if (!in_huelle(px, py, pz, hl))
        return;
    double bj, best;
    naechster(S, sschl, nsschl, sfolge, h, px, py, pz, bj, best);
    if (bj < 0.0 || best > grenze2)
        return;
    const int j = (int)bj;
    const double nx = N[3 * i], ny = N[3 * i + 1], nz = N[3 * i + 2];
    double n2 = INFINITY;
    double hit = 0.0;
    // die Dreiecke um j: an j, an seinen Nachbarn w und an deren Nachbarn x (Doppelte schaden nicht: Treffer ODER, Abstand Minimum)
    int e = (int)inz_a[j];
    while (e < (int)inz_a[j + 1] && hit == 0.0) {
        hit = pruefe(S, ST, (int)inz_z[e], px, py, pz, nx, ny, nz, tiefe, abstand, nahe, n2);
        e = e + 1;
    }
    int m = (int)nach_a[j];
    while (m < (int)nach_a[j + 1] && hit == 0.0) {
        const int w = (int)nach_z[m];
        e = (int)inz_a[w];
        while (e < (int)inz_a[w + 1] && hit == 0.0) {
            hit = pruefe(S, ST, (int)inz_z[e], px, py, pz, nx, ny, nz, tiefe, abstand, nahe, n2);
            e = e + 1;
        }
        int o = (int)nach_a[w];
        while (o < (int)nach_a[w + 1] && hit == 0.0) {
            const int x = (int)nach_z[o];
            e = (int)inz_a[x];
            while (e < (int)inz_a[x + 1] && hit == 0.0) {
                hit = pruefe(S, ST, (int)inz_z[e], px, py, pz, nx, ny, nz, tiefe, abstand, nahe, n2);
                e = e + 1;
            }
            o = o + 1;
        }
        m = m + 1;
    }
    if (hit == 0.0 && n2 <= nahe * nahe)
        hit = 1.0;
    if (hit != 0.0) {
        maske[i] = 1;
        if (wert > (double)nachgeben[i])
            nachgeben[i] = (float)wert;
    }
}

// `Hautmaskeersatz._hoechster`: größte Höhe t im Zylinder und die Nummer des Stückpunkts — −inf / −1 ohne
static __device__ void hoechster(const double* S, const i64* sschl, i64 nsschl, const i64* sfolge, double h, double px, double py, double pz, double nx,
                                 double ny, double nz, double abstand, double tiefe, double r2, double& best, double& tj)
{
    const i64 ci = zellnummer(px, h), cj = zellnummer(py, h), ck = zellnummer(pz, h);
    best = -INFINITY;
    tj = -1.0;
    for (int a = -1; a < 2; ++a)
        for (int b = -1; b < 2; ++b)
            for (int c = -1; c < 2; ++c) {
                const i64 s = zellschluessel(ci + (i64)a, cj + (i64)b, ck + (i64)c);
                int p = untergrenze(sschl, nsschl, s);
                while (p < nsschl && sschl[p] == s) {
                    const int j = (int)sfolge[p];
                    const double vx = S[3 * j] - px, vy = S[3 * j + 1] - py, vz = S[3 * j + 2] - pz;
                    const double t = vx * nx + vy * ny + vz * nz;
                    if (t >= -tiefe && t <= abstand) {
                        if (vx * vx + vy * vy + vz * vz - t * t <= r2 && t > best) {
                            best = t;
                            tj = (double)j;
                        }
                    }
                    p = p + 1;
                }
            }
}

// `Hautmaskeersatz.maskieren`
__global__ void k_ersatz(int n, const double* __restrict__ K, const double* __restrict__ N, const double* __restrict__ S, const i64* __restrict__ sschl,
                         i64 nsschl, const i64* __restrict__ sfolge, double h, const double* __restrict__ hl, double abstand, double tiefe, double r2,
                         double r2weit, const double* __restrict__ randabstand, u8* __restrict__ maske, u8* __restrict__ ers, float* __restrict__ hoehe,
                         float* __restrict__ rand)
{
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n)
        return;
    const double px = K[3 * i], py = K[3 * i + 1], pz = K[3 * i + 2];
    if (!in_huelle(px, py, pz, hl))
        return;
    double r0, r1;
    hoechster(S, sschl, nsschl, sfolge, h, px, py, pz, N[3 * i], N[3 * i + 1], N[3 * i + 2], abstand, tiefe, r2, r0, r1);
    if (r0 != -INFINITY) {
        maske[i] = 1;
        ers[i] = 1;
        if (r0 > (double)hoehe[i])
            hoehe[i] = (float)r0;
        const double ra = randabstand[(int)r1];
        if (ra < (double)rand[i])
            rand[i] = (float)ra;
    } else {
        double w0, w1;
        hoechster(S, sschl, nsschl, sfolge, h, px, py, pz, N[3 * i], N[3 * i + 1], N[3 * i + 2], abstand, tiefe, r2weit, w0, w1);
        if (w0 > (double)hoehe[i])
            hoehe[i] = (float)w0;
    }
}

// `Hautdurchsicht.stueck`: die Tiefe, um die die Haut hinter den Stoff muss (alle Dreiecke um den nächsten Stoffpunkt); `naechste`: hinter die nächste Lage
__global__ void k_durch(int n, const double* __restrict__ K, const double* __restrict__ N, const double* __restrict__ S, const i64* __restrict__ ST,
                        const i64* __restrict__ sschl, i64 nsschl, const i64* __restrict__ sfolge, double h, const double* __restrict__ hl, double grenze2,
                        double tiefe, double luft, double grenze, const i64* __restrict__ nach_a, const i64* __restrict__ nach_z,
                        const i64* __restrict__ inz_a, const i64* __restrict__ inz_z, int naechste, float* __restrict__ aus)
{
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n)
        return;
    const double px = K[3 * i], py = K[3 * i + 1], pz = K[3 * i + 2];
    if (!in_huelle(px, py, pz, hl))
        return;
    double bj, best;
    naechster(S, sschl, nsschl, sfolge, h, px, py, pz, bj, best);
    if (bj < 0.0 || best > grenze2)
        return;
    const int j = (int)bj;
    double noetig = 0.0;
    int vorne = 0;
    int m = (int)nach_a[j] - 1;
    while (m < (int)nach_a[j + 1]) {
        int w = j;
        if (m >= (int)nach_a[j])
            w = (int)nach_z[m];
        int o = (int)nach_a[w] - 1;
        while (o < (int)nach_a[w + 1]) {
            int x = w;
            if (o >= (int)nach_a[w])
                x = (int)nach_z[o];
            for (int e = (int)inz_a[x]; e < (int)inz_a[x + 1]; ++e) {
                const int k = (int)inz_z[e];
                const double t = strahl_dreieck(S, (int)ST[3 * k], (int)ST[3 * k + 1], (int)ST[3 * k + 2], px, py, pz, N[3 * i], N[3 * i + 1], N[3 * i + 2]);
                if (!isnan(t) && t >= -tiefe && t < luft) {
                    if (naechste != 0 && noetig > 0.0)
                        noetig = fmin(noetig, luft - t);
                    else if (luft - t > noetig)
                        noetig = luft - t;
                } else if (naechste != 0 && !isnan(t) && t >= luft && t <= tiefe) {
                    vorne = 1;                                                 // Stoff auch vor der Haut: deckt von außen, kein Durchstich
                }
            }
            o = o + 1;
        }
        m = m + 1;
    }
    if (vorne != 0)
        noetig = 0.0;
    if (noetig > 0.0) {
        const double neu = fmin(noetig, grenze);
        if (neu > (double)aus[i])
            aus[i] = (float)neu;
    }
}

extern "C" __declspec(dllexport) int hk_locker(cudaStream_t strom, int nr, const double* S, const i64* rand, const double* K, const double* N,
                                               const i64* kschl, i64 nkschl, const i64* kfolge, double h, double eng, u8* aus)
{
    if (nr > 0)
        k_locker<<<hk_bloecke(nr), 256, 0, strom>>>(nr, S, rand, K, N, kschl, nkschl, kfolge, h, eng, aus);
    return (int)cudaGetLastError();
}

extern "C" __declspec(dllexport) int hk_stueck(cudaStream_t strom, int n, const double* K, const double* N, const double* S, const i64* ST, const i64* sschl,
                                               i64 nsschl, const i64* sfolge, double h, const double* hl, double grenze2, double tiefe, double abstand,
                                               double nahe, const i64* nach_a, const i64* nach_z, const i64* inz_a, const i64* inz_z, double wert, u8* maske,
                                               float* nachgeben)
{
    if (n > 0)
        k_stueck<<<hk_bloecke(n), 256, 0, strom>>>(n, K, N, S, ST, sschl, nsschl, sfolge, h, hl, grenze2, tiefe, abstand, nahe, nach_a, nach_z, inz_a,
                                                   inz_z, wert, maske, nachgeben);
    return (int)cudaGetLastError();
}

extern "C" __declspec(dllexport) int hk_ersatz(cudaStream_t strom, int n, const double* K, const double* N, const double* S, const i64* sschl, i64 nsschl,
                                               const i64* sfolge, double h, const double* hl, double abstand, double tiefe, double r2, double r2weit,
                                               const double* randabstand, u8* maske, u8* ers, float* hoehe, float* rand)
{
    if (n > 0)
        k_ersatz<<<hk_bloecke(n), 256, 0, strom>>>(n, K, N, S, sschl, nsschl, sfolge, h, hl, abstand, tiefe, r2, r2weit, randabstand, maske, ers, hoehe,
                                                   rand);
    return (int)cudaGetLastError();
}

extern "C" __declspec(dllexport) int hk_durch(cudaStream_t strom, int n, const double* K, const double* N, const double* S, const i64* ST, const i64* sschl,
                                              i64 nsschl, const i64* sfolge, double h, const double* hl, double grenze2, double tiefe, double luft,
                                              double grenze, const i64* nach_a, const i64* nach_z, const i64* inz_a, const i64* inz_z, int naechste,
                                              float* aus)
{
    if (n > 0)
        k_durch<<<hk_bloecke(n), 256, 0, strom>>>(n, K, N, S, ST, sschl, nsschl, sfolge, h, hl, grenze2, tiefe, luft, grenze, nach_a, nach_z, inz_a, inz_z,
                                                  naechste, aus);
    return (int)cudaGetLastError();
}
