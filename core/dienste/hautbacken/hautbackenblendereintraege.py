# -*- coding: utf-8 -*-
"""Hautbackenblendereintraege — Blenders `vert_to_face_map` samt `VertCornerInfo`: zu jedem Punkt die Polygone, die ihn benutzen, mit der Ecke und ihren Nachbarn.

Nach `build_vert_to_face_map` (`mesh_mapping.cc`) und `collect_corner_info` (`mesh_normals.cc`, Blender v5.2.2): die Einträge stehen nach Punkt, innerhalb des Punkts nach
aufsteigender Polygonnummer (Blender sortiert die Gruppen); ein Polygon, das den Punkt mehrfach benutzt, steht mehrfach darin. `corner` ist immer die ERSTE Ecke des Polygons mit
diesem Punkt (`face_find_corner_from_vert`), `corner_prev`/`corner_next` die Nachbarn mit Umlauf (`face_corner_prev`/`face_corner_next`).
Dazu die Richtungen zu den Nachbarpunkten und der Winkelfaktor `safe_acos_approx(dot(dir_prev, dir_next))`, den Punktnormalen, Fächer und Mischung teilen.

Felder (alle (E,), E = Anzahl der Ecken):
  punkt, flaeche, ecke, ecke_vor, ecke_nach, punkt_vor, punkt_nach;  `anfang` (N+1) Offsets je Punkt, `anzahl` (N,)
"""

import numpy as np

from .hautbackenblendermathe import Hautbackenblendermathe as M

__all__ = ['Hautbackenblendereintraege']


class Hautbackenblendereintraege:
    def __init__(self, poly_start, poly_punkte, n_punkte):
        ps = np.asarray(poly_start, dtype=np.int64)
        pp = np.asarray(poly_punkte, dtype=np.int64)
        flaechen = len(ps) - 1
        ecken = len(pp)
        groesse = np.diff(ps)
        je_ecke = np.repeat(np.arange(flaechen, dtype=np.int64), groesse)
        ordnung = np.argsort(pp, kind='stable')           # (Punkt, Ecke) == (Punkt, Polygon, Ecke im Polygon)
        punkt = pp[ordnung]
        flaeche = je_ecke[ordnung]
        ecke = ordnung
        # Ein Polygon mit demselben Punkt mehrfach: alle Einträge nehmen die erste Ecke (face_find_corner_from_vert).
        neu = np.ones(ecken, dtype=bool)
        neu[1:] = (punkt[1:] != punkt[:-1]) | (flaeche[1:] != flaeche[:-1])
        if not neu.all():
            ecke = ecke[np.maximum.accumulate(np.where(neu, np.arange(ecken), 0))]
        start, anz = ps[flaeche], groesse[flaeche]
        self.punkt, self.flaeche, self.ecke = punkt, flaeche, ecke
        self.ecke_vor = ecke - 1 + (ecke == start) * anz
        self.ecke_nach = np.where(ecke == start + anz - 1, start, ecke + 1)
        self.punkt_vor = pp[self.ecke_vor]
        self.punkt_nach = pp[self.ecke_nach]
        self.anzahl = np.bincount(pp, minlength=n_punkte).astype(np.int64)
        self.anfang = np.concatenate([[0], np.cumsum(self.anzahl)])
        self.doppelt = not neu.all()

    def richtungen(self, p):
        """`(dir_prev, dir_next, faktor)`: Einheitsrichtungen vom Punkt zu seinen Nachbarn im Polygon (`math::normalize`) und `safe_acos_approx(dot)`."""
        mitte = p[self.punkt]
        vor = M.normalisieren(p[self.punkt_vor] - mitte)
        nach = M.normalisieren(p[self.punkt_nach] - mitte)
        return vor, nach, M.acos_naeherung(M.punkt(vor, nach))
