// Einzug (`Hauteinzugrechnung`, `Hautkarteeinzug`) — bis 21.11.2026 `hautkartewarpeinzug.py`. Je verdecktem Punkt ein Faden wie in JS; float32 wie die
// Felder dort (`Float32Array`): gespeichert wird gerundet, verglichen in double.

// `Hautdicke._dicke` (Gitter 25 mm, Schritte entlang −N)
__global__ void k_dicke(int n, const double* __restrict__ P, const double* __restrict__ N, const i64* __restrict__ schl, i64 nschl,
                        const i64* __restrict__ folge, double h, const u8* __restrict__ auswahl, const double* __restrict__ weite, double quer_m,
                        double quer_max, float* __restrict__ aus)
{
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n || auswahl[i] == 0)
        return;
    const double weit = weite[i];
    const double px = P[3 * i], py = P[3 * i + 1], pz = P[3 * i + 2];
    const double nx = N[3 * i], ny = N[3 * i + 1], nz = N[3 * i + 2];
    int schritte = (int)ceil(weit / h) - 1;
    if (schritte < 0)
        schritte = 0;
    double best = INFINITY;
    int s = 0;
    while (s <= schritte) {
        if (best < (double)(s - 1) * h)
            break;
        const double sh = (double)s * h;
        const i64 ci = zellnummer(px - sh * nx, h), cj = zellnummer(py - sh * ny, h), ck = zellnummer(pz - sh * nz, h);
        for (int a = -1; a < 2; ++a)
            for (int b = -1; b < 2; ++b)
                for (int c = -1; c < 2; ++c) {
                    const i64 sk = zellschluessel(ci + (i64)a, cj + (i64)b, ck + (i64)c);
                    int p = untergrenze(schl, nschl, sk);
                    while (p < nschl && schl[p] == sk) {
                        const int j = (int)folge[p];
                        p = p + 1;
                        if (N[3 * j] * nx + N[3 * j + 1] * ny + N[3 * j + 2] * nz >= 0.0)
                            continue;
                        const double dx = px - P[3 * j], dy = py - P[3 * j + 1], dz = pz - P[3 * j + 2];
                        const double tiefe = dx * nx + dy * ny + dz * nz;
                        if (tiefe <= 0.0 || tiefe >= best || tiefe > weit)
                            continue;
                        const double qx = dx - tiefe * nx, qy = dy - tiefe * ny, qz = dz - tiefe * nz;
                        const double quer = fmax(quer_m, fmin(0.5 * tiefe, quer_max));
                        if (qx * qx + qy * qy + qz * qz <= quer * quer)
                            best = tiefe;
                    }
                }
        s = s + 1;
    }
    const float gerundet = (float)best;
    if ((double)gerundet <= weit)
        aus[i] = gerundet;
    else
        aus[i] = INFINITY;
}

// je verdecktem Punkt die Verschiebung — an einer Randecke unter die nächste Stoffkante (`Saumschnitt.verschiebung`), sonst entlang −N
__global__ void k_einzug(int n, const double* __restrict__ P, const double* __restrict__ N, const u8* __restrict__ maske, const u8* __restrict__ ecken,
                         const double* __restrict__ kanten, const i64* __restrict__ mschl, i64 nmschl, const i64* __restrict__ mfolge, double kh,
                         int mit_kanten, double schnapp2, double unterkante, const double* __restrict__ abstaende, const float* __restrict__ nachgeben,
                         double tiefe_m, double steigung, const float* __restrict__ dicken, const double* __restrict__ anteil, float* __restrict__ werte,
                         u8* __restrict__ geschnappt)
{
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n || maske[i] == 0)
        return;
    const double px = P[3 * i], py = P[3 * i + 1], pz = P[3 * i + 2];
    const double nx = N[3 * i], ny = N[3 * i + 1], nz = N[3 * i + 2];
    if (mit_kanten != 0 && ecken[i] != 0) {
        // `Saumschnitt.naechsterKantenpunkt`: Streckenmitten im Gitter, 27 Zellen, bester binnen SCHNAPP
        const i64 ci = zellnummer(px, kh), cj = zellnummer(py, kh), ck = zellnummer(pz, kh);
        double best = schnapp2;
        int da = 0;
        double tx = 0.0, ty = 0.0, tz = 0.0;
        for (int a = -1; a < 2; ++a)
            for (int b = -1; b < 2; ++b)
                for (int c = -1; c < 2; ++c) {
                    const i64 sk = zellschluessel(ci + (i64)a, cj + (i64)b, ck + (i64)c);
                    int p = untergrenze(mschl, nmschl, sk);
                    while (p < nmschl && mschl[p] == sk) {
                        const int k = (int)mfolge[p];
                        p = p + 1;
                        const double ax = kanten[6 * k], ay = kanten[6 * k + 1], az = kanten[6 * k + 2];
                        const double ex = kanten[6 * k + 3] - ax, ey = kanten[6 * k + 4] - ay, ez = kanten[6 * k + 5] - az;
                        const double e2 = ex * ex + ey * ey + ez * ez;
                        double t = 0.0;
                        if (e2 > 0.0)
                            t = ((px - ax) * ex + (py - ay) * ey + (pz - az) * ez) / e2;
                        if (t < 0.0)
                            t = 0.0;
                        else if (t > 1.0)
                            t = 1.0;
                        const double qx = ax + t * ex, qy = ay + t * ey, qz = az + t * ez;
                        const double d2 = (qx - px) * (qx - px) + (qy - py) * (qy - py) + (qz - pz) * (qz - pz);
                        if (d2 < best) {
                            best = d2;
                            da = 1;
                            tx = qx;
                            ty = qy;
                            tz = qz;
                        }
                    }
                }
        if (da != 0) {
            double dx = tx - px, dy = ty - py, dz = tz - pz;
            const double entlang = dx * nx + dy * ny + dz * nz;
            dx = dx - entlang * nx;
            dy = dy - entlang * ny;
            dz = dz - entlang * nz;
            werte[3 * i] = (float)(dx - unterkante * nx);
            werte[3 * i + 1] = (float)(dy - unterkante * ny);
            werte[3 * i + 2] = (float)(dz - unterkante * nz);
            geschnappt[i] = 1;
            return;
        }
    }
    double bis = tiefe_m;
    if (nachgeben[i] > 0.0f)
        bis = (double)nachgeben[i];
    double tiefe = fmin(bis, unterkante + steigung * abstaende[i]);
    if (anteil[0] > 0.0)
        tiefe = fmin(tiefe, anteil[0] * (double)dicken[i]);
    werte[3 * i] = (float)(-tiefe * nx);
    werte[3 * i + 1] = (float)(-tiefe * ny);
    werte[3 * i + 2] = (float)(-tiefe * nz);
}

static int hk_bloecke(long long n) { return (int)((n + 255) / 256); }

extern "C" __declspec(dllexport) int hk_dicke(cudaStream_t strom, int n, const double* P, const double* N, const i64* schl, i64 nschl, const i64* folge,
                                              double h, const u8* auswahl, const double* weite, double quer_m, double quer_max, float* aus)
{
    if (n > 0)
        k_dicke<<<hk_bloecke(n), 256, 0, strom>>>(n, P, N, schl, nschl, folge, h, auswahl, weite, quer_m, quer_max, aus);
    return (int)cudaGetLastError();
}

extern "C" __declspec(dllexport) int hk_einzug(cudaStream_t strom, int n, const double* P, const double* N, const u8* maske, const u8* ecken,
                                               const double* kanten, const i64* mschl, i64 nmschl, const i64* mfolge, double kh, int mit_kanten,
                                               double schnapp2, double unterkante, const double* abstaende, const float* nachgeben, double tiefe_m,
                                               double steigung, const float* dicken, const double* anteil, float* werte, u8* geschnappt)
{
    if (n > 0)
        k_einzug<<<hk_bloecke(n), 256, 0, strom>>>(n, P, N, maske, ecken, kanten, mschl, nmschl, mfolge, kh, mit_kanten, schnapp2, unterkante, abstaende,
                                                   nachgeben, tiefe_m, steigung, dicken, anteil, werte, geschnappt);
    return (int)cudaGetLastError();
}
