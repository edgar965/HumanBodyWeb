# -*- coding: utf-8 -*-
"""Hautbackenretri — die Dreiecke des Körpers in der Ruhelage so, wie Blender sie dort bildet.

Blender zerlegt ein Viereck beim Backen nach den Punkten, die der Körper DANN hat (`corner_tris_calc`, `mesh_tessellate.cc`, Blender v5.2.2, gelesen 11.10.2026): zuerst (0, 1, 2) und
(0, 2, 3); liegen die Ecken so, dass die Diagonale 0–2 aus dem Viereck herausfällt (`is_quad_flip_v3_first_third_fast`: `dot(cross(p1−p0, p2−p0), cross(p3−p0, p2−p0)) > 0`), gilt die andere
Diagonale (0, 1, 3) und (1, 2, 3). `blendbacken.py` setzt dem Körper die Punkte der Ruhelage und holt dann die Dreiecke neu — die `.npz` des Exports hat die Zerlegung der Pose, in der er
exportiert wurde. Gemessen am 11.10.2026 (Ruhelage gegen Exportlage): hinako 1.328 von 41.112 Vierecken wechseln die Diagonale, seori 242, Asian Female 153, Rainy 5, Rosemary 1, Fallout
ranger 0; nur Dreiecksnetze (cute girl, BP3D Mann) nie. Bei hinako lagen die Abweichungen gegen Blenders Bild (6 % der Texel, auch gegen Blender auf der CPU) an Hals und Händen.

    npz, bericht = Hautbackenretri.neu(npz, punkte_ruhe)        # `bericht`: {'vierecke', 'gewechselt', 'ngone'}

Gelesen wird die Zerlegung des Exports (`dreieck_poly`, `poly_start`, `poly_punkte`); neu geschrieben werden die Arrays je Dreiecksecke (`dreiecke`, `uv_*`, `farbe_*`, `uv_ecken`,
`dreieck_ecken`) der gewechselten Vierecke — Glatt-Flag, Material und Polygon sind je Polygon und bleiben. Polygone mit mehr als vier Ecken zerlegt Blender mit `BLI_polyfill_calc` (Ohrenschnitt
in der Projektion): das ist NICHT nachgebaut, ihre Zahl steht im Bericht (`ngone`) — dort bleibt die Zerlegung des Exports.
"""

import torch
from KoerperKI_alle.torchfeld import Torchfeld

__all__ = ['Hautbackenretri']

#: Je Zerlegung (0 = (0,1,2)+(0,2,3), 1 = (0,1,3)+(1,2,3)) die Ecken (Schleifen 0…3 des Vierecks) der beiden Dreiecke.
DREIECKE = (((0, 1, 2), (0, 2, 3)), ((0, 1, 3), (1, 2, 3)))
#: Je Zerlegung für jede Schleife 0…3: (Dreieck a/b, Ecke im Dreieck).
ORT = (((0, 0), (0, 1), (0, 2), (1, 2)), ((0, 0), (1, 0), (1, 1), (0, 2)))
#: Arrays je Dreiecksecke `(T, 3, …)`, die mit den Ecken wandern.
ECKEN_ARRAYS = ('dreiecke', 'uv_ecken', 'dreieck_ecken')


class Hautbackenretri:
    @staticmethod
    def wechselt(v1, v2, v3, v4):
        """`is_quad_flip_v3_first_third_fast` (`math_geom.cc`) in float32: gilt für die Ecken (v1…v4) die Zerlegung (0,1,3)+(1,2,3)?"""
        v1, v2, v3, v4 = (Torchfeld.feld(v, dtype=torch.float32) for v in (v1, v2, v3, v4))
        a = Torchfeld.cross(v2 - v1, v3 - v1)
        b = Torchfeld.cross(v4 - v1, v3 - v1)
        return (a * b).sum(axis=1, dtype=torch.float32) > Torchfeld.f32(0.0)

    @classmethod
    def neu(cls, npz, punkte):
        """`(neue Arrays, Bericht)`: `npz` bleibt unverändert; `punkte` (N, 3) sind die Punkte der Ruhelage (Blender-Achsen, wie `blendbacken.py` sie dem Körper setzt)."""
        ps, pp, dp = Torchfeld.feld(npz['poly_start']), Torchfeld.feld(npz['poly_punkte']), Torchfeld.feld(npz['dreieck_poly'])
        groesse = Torchfeld.diff(ps)
        bericht = {'vierecke': int((groesse == 4).sum()), 'gewechselt': 0, 'ngone': int((groesse > 4).sum())}
        viereck = torch.flatten(groesse == 4).nonzero()[:, 0]
        if not len(viereck):
            return npz, bericht
        if (Torchfeld.diff(dp) < 0).any():
            raise ValueError('dreieck_poly ist nicht nach Polygonen geordnet — die Zerlegung des Exports lässt sich nicht lesen')
        ta = Torchfeld.searchsorted(dp, viereck)
        tb = ta + 1
        if not ((dp[ta] == viereck).all() and (dp[tb] == viereck).all()):
            raise ValueError('ein Viereck des Exports hat nicht genau zwei Dreiecke')
        ecken = [pp[ps[viereck] + k] for k in range(4)]
        alt = Torchfeld.astype((Torchfeld.feld(npz['dreiecke'])[ta] == ecken[3][:, None]).any(axis=1), torch.int64)
        neu = Torchfeld.astype(cls.wechselt(*(Torchfeld.feld(punkte)[e] for e in ecken)), torch.int64)
        aendern = torch.flatten(alt != neu).nonzero()[:, 0]
        bericht['gewechselt'] = int(len(aendern))
        if not len(aendern):
            return npz, bericht
        a, b, von, nach = ta[aendern], tb[aendern], alt[aendern], neu[aendern]
        aus = dict(npz)
        for name in [k for k in npz if k in ECKEN_ARRAYS or k.startswith('uv_') or k.startswith('farbe_')]:
            quelle = Torchfeld.feld(npz[name])
            if quelle.ndim < 2 or quelle.shape[:2] != (len(dp), 3):
                continue
            ziel = Torchfeld.kopie(quelle)
            for slot, ziel_tri in enumerate((a, b)):
                for j in range(3):
                    schleife = Torchfeld.feld([DREIECKE[n][slot][j] for n in nach], copy=True)
                    src_dreieck = Torchfeld.feld([[ORT[v][s][0] for s in range(4)] for v in von], copy=True)[Torchfeld.arange(len(von)), schleife]
                    src_ecke = Torchfeld.feld([[ORT[v][s][1] for s in range(4)] for v in von], copy=True)[Torchfeld.arange(len(von)), schleife]
                    ziel[ziel_tri, j] = quelle[torch.where(src_dreieck == 0, a, b), src_ecke]
            aus[name] = ziel
        return aus, bericht
