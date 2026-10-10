/* Punktnormalen und Flächennormalen so, wie Blender 5.2.2 sie rechnet — Zeile für Zeile übernommen, ohne Blenders Containertypen.
 *
 * Quellen (Blender v5.2.2, Commit d13f752e3b9c, gelesen am 10.10.2026; Kopien liegen unter ProjektTemp/_wegwerf/hautbacken_tangenten/blender_v522/):
 *   source/blender/blenkernel/intern/mesh_normals.cc   normals_calc_faces (Z. 180), normal_calc_ngon (Z. 123), normals_calc_verts (Z. 194)
 *   source/blender/blenlib/intern/math_vector_inline.cc add_newell_cross_v3_v3v3 (Z. 700), normalize_v3 (Z. 868), dot_v3v3 (Z. 640)
 *   source/blender/blenlib/BLI_math_vector.hh           math::normalize (Z. 521), math::dot (Z. 425)
 *   source/blender/blenlib/BLI_math_base.hh             math::safe_acos_approx (Z. 236)
 *
 * Gleiche Rechenreihenfolge in float; der Übersetzer darf nicht zu FMA zusammenziehen (Blender: -ffp-contract=off; hier: MSVC ohne /arch:AVX2).
 * Ein Dreieck ist für Blender eine Fläche mit drei Ecken; die Fläche wird nach Newell berechnet (nicht über die Kreuzprodukt-Kante). */

#pragma once

#include <cmath>
#include <cstdint>
#include <vector>

namespace hb {

struct V3 {
  float x, y, z;
};

static inline V3 sub(const V3 &a, const V3 &b)
{
  return {a.x - b.x, a.y - b.y, a.z - b.z};
}

/* math::dot: a[0]*b[0], dann += a[1]*b[1], dann += a[2]*b[2] */
static inline float dot3(const V3 &a, const V3 &b)
{
  float r = a.x * b.x;
  r += a.y * b.y;
  r += a.z * b.z;
  return r;
}

/* math::normalize (BLI_math_vector.hh): Länge² über Schwelle 1e-35f, dann v / sqrt(Länge²), sonst Nullvektor. */
static inline V3 normalize_math(const V3 &v)
{
  float l2 = dot3(v, v);
  if (l2 > 1.0e-35f) {
    const float l = std::sqrt(l2);
    return {v.x / l, v.y / l, v.z / l};
  }
  return {0.0f, 0.0f, 0.0f};
}

/* normalize_v3 (math_vector_inline.cc): d = a0*a0 + a1*a1 + a2*a2 (in einem Ausdruck), Faktor 1.0f / d, dann je Achse multiplizieren. Gibt die Länge zurück (0 = entartet). */
static inline float normalize_v3(float n[3])
{
  float d = n[0] * n[0] + n[1] * n[1] + n[2] * n[2];
  if (d > 1.0e-35f) {
    d = std::sqrt(d);
    const float f = 1.0f / d;
    n[0] = n[0] * f;
    n[1] = n[1] * f;
    n[2] = n[2] * f;
  }
  else {
    n[0] = n[1] = n[2] = 0.0f;
    d = 0.0f;
  }
  return d;
}

static inline void add_newell_cross(float n[3], const float v_prev[3], const float v_curr[3])
{
  n[0] += (v_prev[1] - v_curr[1]) * (v_prev[2] + v_curr[2]);
  n[1] += (v_prev[2] - v_curr[2]) * (v_prev[0] + v_curr[0]);
  n[2] += (v_prev[0] - v_curr[0]) * (v_prev[1] + v_curr[1]);
}

/* normal_calc_ngon für drei Ecken: v_prev = letzte Ecke, dann jede Ecke der Reihe nach. */
static inline V3 flaechennormale_blender(const float *p0, const float *p1, const float *p2)
{
  float n[3] = {0.0f, 0.0f, 0.0f};
  const float *ecken[3] = {p0, p1, p2};
  const float *v_prev = ecken[2];
  for (int i = 0; i < 3; i++) {
    const float *v_curr = ecken[i];
    add_newell_cross(n, v_prev, v_curr);
    v_prev = v_curr;
  }
  if (normalize_v3(n) == 0.0f) {
    n[2] = 1.0f; /* die anderen Achsen sind schon 0 */
  }
  return {n[0], n[1], n[2]};
}

/* math::safe_acos_approx (BLI_math_base.hh). std::numbers::pi ist double, die Rechnung `pi - a` also in double, dann auf float gekürzt — wie dort. */
static inline float safe_acos_approx(float x)
{
  const float f = std::abs(x);
  const float m = (f < 1.0f) ? 1.0f - (1.0f - f) : 1.0f;
  const float a = std::sqrt(1.0f - m) *
                  (1.5707963267f + m * (-0.213300989f + m * (0.077980478f + m * -0.02164095f)));
  return x < 0.0f ? float(3.14159265358979323846) - a : a;
}

/* Alle Flächennormalen (normals_calc_faces) und Punktnormalen (normals_calc_verts). `dreiecke` ist (T,3). Die Flächen eines Punktes laufen in
 * aufsteigender Reihenfolge (so baut vert_to_face_map sie), ein Punkt ohne Fläche bekommt normalize(Position). Gibt 0 zurück, sonst -2 bei einem Index außerhalb. */
static inline int punktnormalen_blender(int n_punkte, int n_dreiecke, const float *punkte, const int32_t *dreiecke,
                                        std::vector<V3> &flaechen, std::vector<V3> &punkt_normalen)
{
  for (int i = 0; i < n_dreiecke * 3; i++) {
    if (dreiecke[i] < 0 || dreiecke[i] >= n_punkte) {
      return -2;
    }
  }
  const V3 *P = reinterpret_cast<const V3 *>(punkte);
  flaechen.resize(size_t(n_dreiecke));
  for (int t = 0; t < n_dreiecke; t++) {
    const int32_t *d = dreiecke + 3 * t;
    flaechen[size_t(t)] = flaechennormale_blender(punkte + 3 * d[0], punkte + 3 * d[1], punkte + 3 * d[2]);
  }
  /* Flächen je Punkt in aufsteigender Reihenfolge: Zählen, dann füllen (die Ecke einer Fläche wird mit gemerkt). */
  std::vector<int> start(size_t(n_punkte) + 1, 0);
  for (int i = 0; i < n_dreiecke * 3; i++) {
    start[size_t(dreiecke[i]) + 1]++;
  }
  for (int v = 0; v < n_punkte; v++) {
    start[size_t(v) + 1] += start[size_t(v)];
  }
  std::vector<int> ecke_der_flaeche(size_t(n_dreiecke) * 3);
  std::vector<int> belegt(size_t(n_punkte), 0);
  for (int i = 0; i < n_dreiecke * 3; i++) {
    const int v = dreiecke[i];
    ecke_der_flaeche[size_t(start[size_t(v)] + belegt[size_t(v)])] = i;
    belegt[size_t(v)]++;
  }
  punkt_normalen.resize(size_t(n_punkte));
  for (int v = 0; v < n_punkte; v++) {
    if (start[size_t(v)] == start[size_t(v) + 1]) {
      punkt_normalen[size_t(v)] = normalize_math(P[v]);
      continue;
    }
    V3 summe = {0.0f, 0.0f, 0.0f};
    for (int k = start[size_t(v)]; k < start[size_t(v) + 1]; k++) {
      const int i = ecke_der_flaeche[size_t(k)];
      const int t = i / 3;
      const int32_t *d = dreiecke + 3 * t;
      /* face_find_corner_from_vert: die ERSTE Ecke mit diesem Punkt (nur bei entarteten Dreiecken mit doppeltem Punkt von i % 3 verschieden). */
      const int c = (d[0] == v) ? 0 : (d[1] == v) ? 1 : 2;
      const int vor = d[(c + 2) % 3], nach = d[(c + 1) % 3]; /* face_corner_prev / face_corner_next */
      const V3 dir_prev = normalize_math(sub(P[vor], P[v]));
      const V3 dir_next = normalize_math(sub(P[nach], P[v]));
      const float faktor = safe_acos_approx(dot3(dir_prev, dir_next));
      summe.x += flaechen[size_t(t)].x * faktor;
      summe.y += flaechen[size_t(t)].y * faktor;
      summe.z += flaechen[size_t(t)].z * faktor;
    }
    punkt_normalen[size_t(v)] = normalize_math(summe);
  }
  return 0;
}

}  // namespace hb
