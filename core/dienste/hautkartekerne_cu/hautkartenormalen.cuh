// Normalen (`Hautmaskegeometrie.normalen`, Aufrufer `Hautkartenormalen`) — bis 21.11.2026 Warp-Kerne in `hautkartenormalen.py`.

// je Punkt die Summe der ungeteilten Kreuzprodukte seiner Dreiecke, in der Reihenfolge der Dreiecke
__global__ void k_summen(int n, const double* __restrict__ P, const i64* __restrict__ T, const i64* __restrict__ anfang, const i64* __restrict__ eintrag,
                         double* __restrict__ N)
{
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n)
        return;
    double sx = 0.0, sy = 0.0, sz = 0.0;
    for (int e = (int)anfang[i]; e < (int)anfang[i + 1]; ++e) {
        const int k = (int)eintrag[e];
        const int a = (int)T[3 * k], b = (int)T[3 * k + 1], c = (int)T[3 * k + 2];
        const double ux = P[3 * b] - P[3 * a], uy = P[3 * b + 1] - P[3 * a + 1], uz = P[3 * b + 2] - P[3 * a + 2];
        const double vx = P[3 * c] - P[3 * a], vy = P[3 * c + 1] - P[3 * a + 1], vz = P[3 * c + 2] - P[3 * a + 2];
        sx = sx + (uy * vz - uz * vy);
        sy = sy + (uz * vx - ux * vz);
        sz = sz + (ux * vy - uy * vx);
    }
    N[3 * i] = sx;
    N[3 * i + 1] = sy;
    N[3 * i + 2] = sz;
}

// je Gruppe deckungsgleicher Punkte (erster zuerst, dann aufsteigend): N[erster] += N[i] der Reihe nach, alle übernehmen die Summe
__global__ void k_naehte(int ng, const double* __restrict__ N, const i64* __restrict__ anfang, const i64* __restrict__ glied, double* __restrict__ aus)
{
    const int g = blockIdx.x * blockDim.x + threadIdx.x;
    if (g >= ng)
        return;
    const int von = (int)anfang[g], bis = (int)anfang[g + 1];
    const int erster = (int)glied[von];
    double sx = N[3 * erster], sy = N[3 * erster + 1], sz = N[3 * erster + 2];
    for (int e = von + 1; e < bis; ++e) {
        const int i = (int)glied[e];
        sx = sx + N[3 * i];
        sy = sy + N[3 * i + 1];
        sz = sz + N[3 * i + 2];
    }
    for (int e = von; e < bis; ++e) {
        const int i = (int)glied[e];
        aus[3 * i] = sx;
        aus[3 * i + 1] = sy;
        aus[3 * i + 2] = sz;
    }
}

// vz · N / hypot3(N)
__global__ void k_normieren(int n, double* __restrict__ N, double vz)
{
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n)
        return;
    double laenge = hypot3(N[3 * i], N[3 * i + 1], N[3 * i + 2]);
    if (laenge == 0.0)
        laenge = 1.0;
    N[3 * i] = vz * N[3 * i] / laenge;
    N[3 * i + 1] = vz * N[3 * i + 1] / laenge;
    N[3 * i + 2] = vz * N[3 * i + 2] / laenge;
}

extern "C" __declspec(dllexport) int hk_summen(cudaStream_t strom, int n, const double* P, const i64* T, const i64* anfang, const i64* eintrag, double* N)
{
    if (n > 0)
        k_summen<<<hk_bloecke(n), 256, 0, strom>>>(n, P, T, anfang, eintrag, N);
    return (int)cudaGetLastError();
}

extern "C" __declspec(dllexport) int hk_naehte(cudaStream_t strom, int ng, const double* N, const i64* anfang, const i64* glied, double* aus)
{
    if (ng > 0)
        k_naehte<<<hk_bloecke(ng), 256, 0, strom>>>(ng, N, anfang, glied, aus);
    return (int)cudaGetLastError();
}

extern "C" __declspec(dllexport) int hk_normieren(cudaStream_t strom, int n, double* N, double vz)
{
    if (n > 0)
        k_normieren<<<hk_bloecke(n), 256, 0, strom>>>(n, N, vz);
    return (int)cudaGetLastError();
}
