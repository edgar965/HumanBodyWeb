# -*- coding: utf-8 -*-
"""Hautbackenblendereintraege — Blenders `vert_to_face_map` samt `VertCornerInfo`: zu jedem Punkt die Polygone, die ihn benutzen, mit der Ecke und ihren Nachbarn.

Nach `build_vert_to_face_map` (`mesh_mapping.cc`) und `collect_corner_info` (`mesh_normals.cc`, Blender v5.2.2): die Einträge stehen nach Punkt, innerhalb des Punkts nach
aufsteigender Polygonnummer (Blender sortiert die Gruppen); ein Polygon, das den Punkt mehrfach benutzt, steht mehrfach darin. `corner` ist immer die ERSTE Ecke des Polygons mit
diesem Punkt (`face_find_corner_from_vert`), `corner_prev`/`corner_next` die Nachbarn mit Umlauf (`face_corner_prev`/`face_corner_next`).
Dazu die Richtungen zu den Nachbarpunkten und der Winkelfaktor `safe_acos_approx(dot(dir_prev, dir_next))`, den Punktnormalen, Fächer und Mischung teilen.

Felder (alle (E,), E = Anzahl der Ecken):
  punkt, flaeche, ecke, ecke_vor, ecke_nach, punkt_vor, punkt_nach;  `anfang` (N+1) Offsets je Punkt, `anzahl` (N,)
"""

import torch
from KoerperKI_alle.torchfeld import Torchfeld

from .hautbackenblendermathe import Hautbackenblendermathe as M

__all__ = ['Hautbackenblendereintraege']


class Hautbackenblendereintraege:
    def __init__(self, poly_start, poly_punkte, n_punkte):
        ps = Torchfeld.feld(poly_start, dtype=torch.int64)
        pp = Torchfeld.feld(poly_punkte, dtype=torch.int64)
        flaechen = len(ps) - 1
        ecken = len(pp)
        groesse = Torchfeld.diff(ps)
        je_ecke = Torchfeld.repeat_interleave(torch.arange(flaechen, dtype=torch.int64, device='cuda'), groesse)
        ordnung = torch.argsort(pp, stable=True)           # (Punkt, Ecke) == (Punkt, Polygon, Ecke im Polygon)
        punkt = pp[ordnung]
        flaeche = je_ecke[ordnung]
        ecke = ordnung
        # Ein Polygon mit demselben Punkt mehrfach: alle Einträge nehmen die erste Ecke (face_find_corner_from_vert).
        neu = torch.ones(ecken, dtype=torch.bool, device='cuda')
        neu[1:] = (punkt[1:] != punkt[:-1]) | (flaeche[1:] != flaeche[:-1])
        if not neu.all():
            ecke = ecke[Torchfeld.maximum_accumulate(torch.where(neu, Torchfeld.arange(ecken), 0))]
        start, anz = ps[flaeche], groesse[flaeche]
        self.punkt, self.flaeche, self.ecke = punkt, flaeche, ecke
        self.ecke_vor = ecke - 1 + (ecke == start) * anz
        self.ecke_nach = torch.where(ecke == start + anz - 1, start, ecke + 1)
        self.punkt_vor = pp[self.ecke_vor]
        self.punkt_nach = pp[self.ecke_nach]
        self.anzahl = Torchfeld.astype(Torchfeld.bincount(pp, minlength=n_punkte), torch.int64)
        self.anfang = Torchfeld.cat([[0], Torchfeld.cumsum(self.anzahl)])
        self.doppelt = not neu.all()

    def richtungen(self, p):
        """`(dir_prev, dir_next, faktor)`: Einheitsrichtungen vom Punkt zu seinen Nachbarn im Polygon (`math::normalize`) und `safe_acos_approx(dot)`."""
        mitte = p[self.punkt]
        vor = M.normalisieren(p[self.punkt_vor] - mitte)
        nach = M.normalisieren(p[self.punkt_nach] - mitte)
        return vor, nach, M.acos_naeherung(M.punkt(vor, nach))
