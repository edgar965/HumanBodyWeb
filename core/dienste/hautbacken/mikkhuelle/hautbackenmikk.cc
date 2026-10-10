/* Hülle um MikkTSpace aus Blender 5.2.2: die Header unter ../mikktspace/ sind unverändert; hier steht nur, was Cycles darum herum tut.
 *
 * Gegenstück zu `MikkMeshWrapper` und `mikk_compute_tangents` in intern/cycles/scene/mesh.cpp (Blender v5.2.2, Zeilen 29–178):
 *   GetNumFaces              = Anzahl der Dreiecke            GetNumVerticesOfFace = 3
 *   GetPosition(f, v)        = Position des Punktes, auf den Ecke v des Dreiecks f zeigt
 *   GetTexCoord(f, v)        = (u, v, 1.0) der Ecke            has_uv() = wahr
 *   GetNormal(f, v)          = glattes Dreieck: Punktnormale, DURCH Cycles' packed_normal (Oktaeder, 2 × 16 Bit) GESCHICKT und decode() zurück;
 *                              flaches Dreieck: Mesh::Triangle::compute_normal (Kreuzprodukt, mit Cycles' float3-Rechnung)
 *   SetTangentSpace(f, v, T, orientation) = Tangente T, Vorzeichen orientation ? +1 : -1
 *
 * Zweiter Modus (`modus` = 1) ist `calc_tangents` aus Blenders Python-Schnittstelle (BKE mesh_tangent.cc, MeshToTangentQuadsTris): Normale
 * als float, ungepackt; flache Dreiecke mit der Newell-Flächennormale (normals_calc_faces). Er dient nur dem Vergleich mit Blender.
 *
 * Gebaut wird ohne WITH_TBB: seriell (Blender rechnet ab 10.000 Dreiecken parallel; die Summen der Tangenten je Gruppe werden dort atomar
 * in wechselnder Reihenfolge addiert, die letzte Stelle kann dort von Lauf zu Lauf schwanken — hier nicht). */

#include <array>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <exception>
#include <unordered_map>
#include <vector>

/* Cycles setzt den Namensraum über die Befehlszeile des Builds (CMake: -DCCL_NAMESPACE_BEGIN=...); hier vor dem ersten Cycles-Header. */
#define CCL_NAMESPACE_BEGIN namespace ccl {
#define CCL_NAMESPACE_END }

#include "util/types_normal.h" /* Cycles: packed_normal, float3-Rechnung (SSE, wie im Cycles-Build für x86-64) */

/* mikktspace.hh setzt `uint` (und LIKELY, aus Cycles' defines.h) aus Blenders Umgebung voraus — hier, ohne die Datei anzufassen. */
typedef unsigned int uint;

#include "mikktspace.hh"

#include "hautbackenblender.hh"

#define HB_API extern "C" __declspec(dllexport)

namespace {

struct Huelle {
  int anzahl_dreiecke;
  const float *punkte;
  const int32_t *dreiecke;
  const float *uv;
  /* Normale je Punkt (bereits decodiert bzw. float) und je Dreieck (flach); beides vorab gerechnet — dieselben Werte, die Cycles bei jedem Aufruf neu rechnet. */
  std::vector<mikk::float3> punktnormale;
  std::vector<mikk::float3> flaechennormale;
  std::vector<mikk::float3> eckennormale; /* leer = keine Eckennormalen (Cycles: attr_cN == nullptr) */
  bool eckennormalen_fuer_alle;           /* Modus „Blender“: Eckennormale gilt für jede Ecke, glatt oder flach (calc_tangents liest corner_normals()) */
  const uint8_t *glatt;
  float *tangente;
  float *vorzeichen;

  int GetNumFaces()
  {
    return anzahl_dreiecke;
  }
  int GetNumVerticesOfFace(const int)
  {
    return 3;
  }
  mikk::float3 GetPosition(const int f, const int v)
  {
    const float *p = punkte + 3 * size_t(dreiecke[3 * size_t(f) + size_t(v)]);
    return mikk::float3(p[0], p[1], p[2]);
  }
  mikk::float3 GetTexCoord(const int f, const int v)
  {
    const float *t = uv + 2 * (3 * size_t(f) + size_t(v));
    return mikk::float3(t[0], t[1], 1.0f);
  }
  mikk::float3 GetNormal(const int f, const int v)
  {
    if (eckennormalen_fuer_alle) {
      return eckennormale[3 * size_t(f) + size_t(v)];
    }
    if (glatt[f]) {
      /* Cycles: ((corner_normal) ? corner_normal[CornerIndex] : vertex_normal[VertexIndex]).decode() */
      return eckennormale.empty() ? punktnormale[size_t(dreiecke[3 * size_t(f) + size_t(v)])] : eckennormale[3 * size_t(f) + size_t(v)];
    }
    return flaechennormale[size_t(f)];
  }
  void SetTangentSpace(const int f, const int v, mikk::float3 T, bool orientation)
  {
    const size_t ecke = 3 * size_t(f) + size_t(v);
    tangente[3 * ecke + 0] = T.x;
    tangente[3 * ecke + 1] = T.y;
    tangente[3 * ecke + 2] = T.z;
    vorzeichen[ecke] = orientation ? 1.0f : -1.0f;
  }
  bool has_uv() const
  {
    return true;
  }
};

/* Mesh::Triangle::compute_normal (scene/mesh.cpp, v5.2.2 Z. 220), Zeile für Zeile. */
ccl::float3 cycles_flaechennormale(const ccl::float3 v0, const ccl::float3 v1, const ccl::float3 v2)
{
  const ccl::float3 norm = ccl::cross(v1 - v0, v2 - v0);
  const float normlen = ccl::len(norm);
  if (normlen == 0.0f) {
    return ccl::make_float3(1.0f, 0.0f, 0.0f);
  }
  return norm / normlen;
}

}  // namespace

/* Fassung der Hülle — wächst mit jeder Änderung an der Schnittstelle. */
HB_API int hb_fassung(void)
{
  return 2;
}

/* Punktnormalen wie Blender (mesh.vertex_normals). 0 = gut, -1 = Ausnahme, -2 = Punktindex außerhalb. */
HB_API int hb_punktnormalen(int n_punkte, int n_dreiecke, const float *punkte, const int32_t *dreiecke, float *normalen_aus)
{
  try {
    std::vector<hb::V3> flaechen, punkt_normalen;
    const int rc = hb::punktnormalen_blender(n_punkte, n_dreiecke, punkte, dreiecke, flaechen, punkt_normalen);
    if (rc != 0) {
      return rc;
    }
    std::memcpy(normalen_aus, punkt_normalen.data(), sizeof(float) * 3 * size_t(n_punkte));
    return 0;
  }
  catch (const std::exception &) {
    return -1;
  }
}

/* Tangenten und Vorzeichen je Dreiecksecke (Index dreieck * 3 + ecke).
 * modus 0 = Cycles: glatte Dreiecke: Punkt- bzw. Eckennormale durch packed_normal und decode(); flache Dreiecke: compute_normal.
 *        1 = Blenders calc_tangents: float-Normalen; mit Eckennormalen gilt für JEDE Ecke die Eckennormale (corner_normals()), ohne sie Punktnormale (glatt) bzw. Newell-Flächennormale (flach).
 * normalen: (n_punkte, 3) Punktnormalen — darf nullptr sein, wenn ecken_normalen gesetzt ist.
 * ecken_normalen: (n_dreiecke, 3, 3) oder nullptr; gesetzt, ersetzt es die Punktnormalen (Cycles: corner_normal ? corner_normal[Ecke] : vertex_normal[Punkt]).
 * glatt: (n_dreiecke) 0/1 — das Glatt-Flag des Netzes (Mesh::get_smooth), NICHT das in pack_shaders überschriebene.
 * 0 = gut, -1 = Ausnahme, -2 = Punktindex außerhalb, -3 = unbekannter Modus, -4 = weder Punkt- noch Eckennormalen. */
HB_API int hb_tangenten(int n_punkte, int n_dreiecke, const float *punkte, const int32_t *dreiecke, const float *uv_ecken, const float *normalen,
                        const float *ecken_normalen, const uint8_t *glatt, int modus, float *tangenten_aus, float *vorzeichen_aus)
{
  try {
    if (modus != 0 && modus != 1) {
      return -3;
    }
    if (normalen == nullptr && ecken_normalen == nullptr) {
      return -4;
    }
    for (int i = 0; i < n_dreiecke * 3; i++) {
      if (dreiecke[i] < 0 || dreiecke[i] >= n_punkte) {
        return -2;
      }
    }
    Huelle h;
    h.anzahl_dreiecke = n_dreiecke;
    h.punkte = punkte;
    h.dreiecke = dreiecke;
    h.uv = uv_ecken;
    h.glatt = glatt;
    h.tangente = tangenten_aus;
    h.vorzeichen = vorzeichen_aus;
    h.eckennormalen_fuer_alle = (modus == 1 && ecken_normalen != nullptr);
    h.flaechennormale.resize(size_t(n_dreiecke));
    const bool ecken = ecken_normalen != nullptr;

    if (modus == 0) {
      auto entpackt = [](const float *n) {
        const ccl::packed_normal gepackt(ccl::make_float3(n[0], n[1], n[2]));
        const ccl::float3 d = gepackt.decode();
        return mikk::float3(d.x, d.y, d.z);
      };
      if (ecken) {
        h.eckennormale.resize(size_t(n_dreiecke) * 3);
        for (size_t i = 0; i < size_t(n_dreiecke) * 3; i++) {
          h.eckennormale[i] = entpackt(ecken_normalen + 3 * i);
        }
      }
      else {
        h.punktnormale.resize(size_t(n_punkte));
        for (int p = 0; p < n_punkte; p++) {
          h.punktnormale[size_t(p)] = entpackt(normalen + 3 * size_t(p));
        }
      }
      for (int t = 0; t < n_dreiecke; t++) {
        const int32_t *d = dreiecke + 3 * size_t(t);
        const float *a = punkte + 3 * size_t(d[0]), *b = punkte + 3 * size_t(d[1]), *c = punkte + 3 * size_t(d[2]);
        const ccl::float3 vN = cycles_flaechennormale(ccl::make_float3(a[0], a[1], a[2]), ccl::make_float3(b[0], b[1], b[2]), ccl::make_float3(c[0], c[1], c[2]));
        h.flaechennormale[size_t(t)] = mikk::float3(vN.x, vN.y, vN.z);
      }
    }
    else {
      if (ecken) {
        h.eckennormale.resize(size_t(n_dreiecke) * 3);
        for (size_t i = 0; i < size_t(n_dreiecke) * 3; i++) {
          h.eckennormale[i] = mikk::float3(ecken_normalen + 3 * i);
        }
      }
      else {
        h.punktnormale.resize(size_t(n_punkte));
        for (int p = 0; p < n_punkte; p++) {
          h.punktnormale[size_t(p)] = mikk::float3(normalen + 3 * size_t(p));
        }
      }
      for (int t = 0; t < n_dreiecke; t++) {
        const int32_t *d = dreiecke + 3 * size_t(t);
        const hb::V3 n = hb::flaechennormale_blender(punkte + 3 * size_t(d[0]), punkte + 3 * size_t(d[1]), punkte + 3 * size_t(d[2]));
        h.flaechennormale[size_t(t)] = mikk::float3(n.x, n.y, n.z);
      }
    }

    mikk::Mikktspace<Huelle>(h).genTangSpace();
    return 0;
  }
  catch (const std::exception &) {
    return -1;
  }
}

