# -*- coding: utf-8 -*-
"""Hautbackenblenderflaechen — Flächen- und Punktnormalen wie `Mesh::face_normals_true` / `vert_normals_true` und die Mischungen aus Eckennormalen.

Blender v5.2.2, `blenkernel/intern/mesh_normals.cc` (gelesen 10.10.2026):
  * `normals_calc_faces`: für JEDES Polygon `normal_calc_ngon` — Newell (`add_newell_cross_v3_v3v3`, Start mit dem letzten Punkt als `v_prev`), dann `normalize_v3`;
    zu kleiner Vektor: (0, 0, 1). Dreiecke und Vierecke gehen NICHT über `normal_tri`/`normal_quad_v3` (die gelten nur für das einzelne `face_normal_calc`).
  * `normals_calc_verts`: je Punkt die Summe `Flächennormale × safe_acos_approx(dot(dir_prev, dir_next))` über die Polygone des Punkts (in der Reihenfolge der
    `vert_to_face_map`), `math::normalize`; ein Punkt ohne Polygon: `normalize(position)`.
  * `mix_normals_corner_to_vert`: dasselbe mit der Eckennormale statt der Flächennormale (eigene Normalen auf der Ecke → `Mesh::vert_normals`).
  * `mix_normals_corner_to_face`: Summe der Eckennormalen des Polygons (`std::accumulate` ab 0), `math::normalize` (→ `Mesh::face_normals`).
"""

import numpy as np

from .hautbackenblendermathe import Hautbackenblendermathe as M

__all__ = ['Hautbackenblenderflaechen']


class Hautbackenblenderflaechen:
    @staticmethod
    def flaechennormalen(p, poly_start, poly_punkte):
        """`normals_calc_faces` — (P,3) float32."""
        ps = np.asarray(poly_start, dtype=np.int64)
        pp = np.asarray(poly_punkte, dtype=np.int64)
        start, groesse = ps[:-1], np.diff(ps)
        n = np.zeros((len(start), 3), dtype=np.float32)
        for k in range(int(groesse.max()) if len(groesse) else 0):
            aktiv = np.flatnonzero(groesse > k)
            vor = p[pp[start[aktiv] + (groesse[aktiv] - 1 if k == 0 else k - 1)]]
            aktuell = p[pp[start[aktiv] + k]]
            n[aktiv, 0] += (vor[:, 1] - aktuell[:, 1]) * (vor[:, 2] + aktuell[:, 2])
            n[aktiv, 1] += (vor[:, 2] - aktuell[:, 2]) * (vor[:, 0] + aktuell[:, 0])
            n[aktiv, 2] += (vor[:, 0] - aktuell[:, 0]) * (vor[:, 1] + aktuell[:, 1])
        n, laenge = M.normalisieren_c(n)
        n[laenge == 0.0, 2] = 1.0       # „Other axis are already set to zero"
        return n

    @staticmethod
    def punktnormalen(p, e, flaechen_normalen):
        """`normals_calc_verts` mit den Einträgen `e` (`Hautbackenblendereintraege`) — (N,3) float32."""
        _, _, faktor = e.richtungen(p)
        summe = M.gruppensumme(flaechen_normalen[e.flaeche] * faktor[:, None], e.anfang)
        return Hautbackenblenderflaechen._abschluss(p, e, summe)

    @staticmethod
    def ecken_zu_punkten(p, e, ecken_normalen):
        """`mix_normals_corner_to_vert` — (N,3) float32."""
        _, _, faktor = e.richtungen(p)
        summe = M.gruppensumme(ecken_normalen[e.ecke] * faktor[:, None], e.anfang)
        return Hautbackenblenderflaechen._abschluss(p, e, summe)

    @staticmethod
    def _abschluss(p, e, summe):
        aus = M.normalisieren(summe)
        lose = e.anzahl == 0
        if lose.any():                  # Punkt ohne Polygon: normalize(position)
            aus[lose] = M.normalisieren(p[lose])
        return aus

    @staticmethod
    def ecken_zu_flaechen(poly_start, ecken_normalen):
        """`mix_normals_corner_to_face` — (P,3) float32."""
        ps = np.asarray(poly_start, dtype=np.int64)
        start, groesse = ps[:-1], np.diff(ps)
        summe = np.zeros((len(start), 3), dtype=np.float32)
        for k in range(int(groesse.max()) if len(groesse) else 0):
            aktiv = np.flatnonzero(groesse > k)
            summe[aktiv] += ecken_normalen[start[aktiv] + k]
        return M.normalisieren(summe)
