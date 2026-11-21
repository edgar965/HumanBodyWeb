// wp17.cuh — Vektoren und Matrizen der Hautbacken-Kerne in der Form, in der Warp 1.17 sie rechnet (warp/native/vec.h, mat.h, builtin.h; 21.11.2026, Edgar:
// „Warp überall raus“). Jede Rechnung steht in derselben Reihenfolge wie in Warps Köpfen, damit nvcc mit -fmad=true dieselben Produkte zusammenzieht:
//   dot3 = a0*b0 + a1*b1 + a2*b2, length = sqrt(x*x + y*y + z*z), normalize teilt jede Komponente durch die Länge (kEps = 0),
//   Matrix·Vektor spaltenweise (r = Spalte0·b0; r += Spalte1·b1; …), inverse(mat33) über Kofaktoren · (1/det), det = dot(Zeile0, cross(Zeile1, Zeile2)),
//   Minus vor einer Zahl = 0 − x (builtin.h `neg`), vor einem Vektor echtes −x; min/max/clamp auf Gleitkomma über fminf/fmaxf, auf Ganzzahlen a<b?a:b.
#pragma once
#include <cuda_runtime.h>
#include <math.h>

namespace hb {

typedef unsigned char u8;
typedef unsigned short u16;

struct v2 { float c[2]; };
struct v3 { float c[3]; };
struct v4 { float c[4]; };
struct m33 { float d[3][3]; };                                           // Zeilen zuerst wie wp::mat_t

__device__ __forceinline__ v2 V2(float a, float b) { v2 r; r.c[0] = a; r.c[1] = b; return r; }
__device__ __forceinline__ v3 V3(float a, float b, float c) { v3 r; r.c[0] = a; r.c[1] = b; r.c[2] = c; return r; }
__device__ __forceinline__ v4 V4(float a, float b, float c, float d) { v4 r; r.c[0] = a; r.c[1] = b; r.c[2] = c; r.c[3] = d; return r; }
__device__ __forceinline__ v3 null3() { return V3(0.0f, 0.0f, 0.0f); }

__device__ __forceinline__ float wneg(float x) { return 0.0f - x; }
__device__ __forceinline__ float wmin(float a, float b) { return fminf(a, b); }
__device__ __forceinline__ float wmax(float a, float b) { return fmaxf(a, b); }
__device__ __forceinline__ float wclamp(float x, float a, float b) { return fminf(fmaxf(a, x), b); }
__device__ __forceinline__ int imin(int a, int b) { return a < b ? a : b; }
__device__ __forceinline__ int imax(int a, int b) { return a > b ? a : b; }
__device__ __forceinline__ int iclamp(int x, int a, int b) { return imin(imax(a, x), b); }
__device__ __forceinline__ float wasin(float x) { return asinf(fminf(fmaxf(x, -1.0f), 1.0f)); }
__device__ __forceinline__ float wacos(float x) { return acosf(fminf(fmaxf(x, -1.0f), 1.0f)); }

#define HB_VOP(T, N)                                                                                                       \
    __device__ __forceinline__ T add(T a, T b) { T r; for (int i = 0; i < N; ++i) r.c[i] = a.c[i] + b.c[i]; return r; }    \
    __device__ __forceinline__ T sub(T a, T b) { T r; for (int i = 0; i < N; ++i) r.c[i] = a.c[i] - b.c[i]; return r; }    \
    __device__ __forceinline__ T mul(T a, float s) { T r; for (int i = 0; i < N; ++i) r.c[i] = a.c[i] * s; return r; }    \
    __device__ __forceinline__ T mul(float s, T a) { T r; for (int i = 0; i < N; ++i) r.c[i] = s * a.c[i]; return r; }    \
    __device__ __forceinline__ T div(T a, float s) { T r; for (int i = 0; i < N; ++i) r.c[i] = a.c[i] / s; return r; }    \
    __device__ __forceinline__ T cw_mul(T a, T b) { T r; for (int i = 0; i < N; ++i) r.c[i] = a.c[i] * b.c[i]; return r; } \
    __device__ __forceinline__ T cw_div(T a, T b) { T r; for (int i = 0; i < N; ++i) r.c[i] = a.c[i] / b.c[i]; return r; } \
    __device__ __forceinline__ T neg(T a) { T r; for (int i = 0; i < N; ++i) r.c[i] = -a.c[i]; return r; }
HB_VOP(v2, 2)
HB_VOP(v3, 3)
HB_VOP(v4, 4)
#undef HB_VOP

__device__ __forceinline__ float dot(v2 a, v2 b) { return a.c[0] * b.c[0] + a.c[1] * b.c[1]; }
__device__ __forceinline__ float dot(v3 a, v3 b) { return a.c[0] * b.c[0] + a.c[1] * b.c[1] + a.c[2] * b.c[2]; }
__device__ __forceinline__ float length(v3 a) { return sqrtf(a.c[0] * a.c[0] + a.c[1] * a.c[1] + a.c[2] * a.c[2]); }
__device__ __forceinline__ v3 normalize(v3 a)
{
    const float l = sqrtf(a.c[0] * a.c[0] + a.c[1] * a.c[1] + a.c[2] * a.c[2]);
    if (l > 0.0f)
        return V3(a.c[0] / l, a.c[1] / l, a.c[2] / l);
    return null3();
}
__device__ __forceinline__ v3 cross(v3 a, v3 b)
{
    return V3(a.c[1] * b.c[2] - a.c[2] * b.c[1], a.c[2] * b.c[0] - a.c[0] * b.c[2], a.c[0] * b.c[1] - a.c[1] * b.c[0]);
}
__device__ __forceinline__ bool null(v3 a) { return a.c[0] == 0.0f && a.c[1] == 0.0f && a.c[2] == 0.0f; }

__device__ __forceinline__ m33 M33(float a, float b, float c, float d, float e, float f, float g, float h, float i)
{
    m33 m;
    m.d[0][0] = a; m.d[0][1] = b; m.d[0][2] = c;
    m.d[1][0] = d; m.d[1][1] = e; m.d[1][2] = f;
    m.d[2][0] = g; m.d[2][1] = h; m.d[2][2] = i;
    return m;
}
__device__ __forceinline__ v3 mul(m33 m, v3 b)                          // spaltenweise wie mat.h
{
    v3 r = V3(m.d[0][0] * b.c[0], m.d[1][0] * b.c[0], m.d[2][0] * b.c[0]);
    r = add(r, V3(m.d[0][1] * b.c[1], m.d[1][1] * b.c[1], m.d[2][1] * b.c[1]));
    return add(r, V3(m.d[0][2] * b.c[2], m.d[1][2] * b.c[2], m.d[2][2] * b.c[2]));
}
__device__ __forceinline__ m33 transpose(m33 a)
{
    return M33(a.d[0][0], a.d[1][0], a.d[2][0], a.d[0][1], a.d[1][1], a.d[2][1], a.d[0][2], a.d[1][2], a.d[2][2]);
}
__device__ __forceinline__ m33 inverse(m33 m)
{
    const float det = dot(V3(m.d[0][0], m.d[0][1], m.d[0][2]), cross(V3(m.d[1][0], m.d[1][1], m.d[1][2]), V3(m.d[2][0], m.d[2][1], m.d[2][2])));
    m33 b;
    if (det == 0.0f) {
        for (int i = 0; i < 3; ++i)
            for (int j = 0; j < 3; ++j)
                b.d[i][j] = 0.0f;
        return b;
    }
    b.d[0][0] = m.d[1][1] * m.d[2][2] - m.d[1][2] * m.d[2][1];
    b.d[1][0] = m.d[1][2] * m.d[2][0] - m.d[1][0] * m.d[2][2];
    b.d[2][0] = m.d[1][0] * m.d[2][1] - m.d[1][1] * m.d[2][0];
    b.d[0][1] = m.d[0][2] * m.d[2][1] - m.d[0][1] * m.d[2][2];
    b.d[1][1] = m.d[0][0] * m.d[2][2] - m.d[0][2] * m.d[2][0];
    b.d[2][1] = m.d[0][1] * m.d[2][0] - m.d[0][0] * m.d[2][1];
    b.d[0][2] = m.d[0][1] * m.d[1][2] - m.d[0][2] * m.d[1][1];
    b.d[1][2] = m.d[0][2] * m.d[1][0] - m.d[0][0] * m.d[1][2];
    b.d[2][2] = m.d[0][0] * m.d[1][1] - m.d[0][1] * m.d[1][0];
    const float rcp = 1.0f / det;
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
            b.d[i][j] = b.d[i][j] * rcp;
    return b;
}

// Felder: vec2/vec3/vec4 hintereinander als float, vec3i als int
__device__ __forceinline__ v2 lies2(const float* a, long long i) { return V2(a[2 * i], a[2 * i + 1]); }
__device__ __forceinline__ v3 lies3(const float* a, long long i) { return V3(a[3 * i], a[3 * i + 1], a[3 * i + 2]); }
__device__ __forceinline__ v4 lies4(const float* a, long long i) { return V4(a[4 * i], a[4 * i + 1], a[4 * i + 2], a[4 * i + 3]); }
__device__ __forceinline__ void schreib2(float* a, long long i, v2 v) { a[2 * i] = v.c[0]; a[2 * i + 1] = v.c[1]; }
__device__ __forceinline__ void schreib3(float* a, long long i, v3 v) { a[3 * i] = v.c[0]; a[3 * i + 1] = v.c[1]; a[3 * i + 2] = v.c[2]; }
__device__ __forceinline__ void schreib4(float* a, long long i, v4 v) { a[4 * i] = v.c[0]; a[4 * i + 1] = v.c[1]; a[4 * i + 2] = v.c[2]; a[4 * i + 3] = v.c[3]; }

}  // namespace hb

#define HB_FADEN(N)                                                     \
    const int i = blockIdx.x * blockDim.x + threadIdx.x;                 \
    if (i >= (N))                                                       \
        return;
#define HB_GITTER(n) (int)(((long long)(n) + 255) / 256), 256, 0, (cudaStream_t)s
#define HB_EXPORT extern "C" __declspec(dllexport) int
#define HB_ENDE return (int)cudaGetLastError()
