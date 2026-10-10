# -*- coding: utf-8 -*-
"""Hautbackentangenten — die Tangenten und Bitangenten-Vorzeichen, die Blender/Cycles für eine Normalenkarte benutzt: MikkTSpace aus Blender 5.2.2, unverändert.

    tangenten, vorzeichen = Hautbackentangenten.berechnen(punkte, dreiecke, uv_ecken, normalen=None, glatt=None, ecken_normalen=None)

* `punkte` (N,3), `dreiecke` (T,3) Punktindizes, `uv_ecken` (T,3,2) UV je Dreiecksecke.
* `normalen` (N,3): die Punktnormalen, die Cycles als `vertex_normal` bekommt (Blenders `mesh.vertex_normals`). Ohne Angabe rechnet die Hülle sie wie Blender
  (`normals_calc_faces` nach Newell, `normals_calc_verts` nach dem Winkel an der Ecke gewichtet, `safe_acos_approx`).
* `glatt` (T,) bool: Dreieck glatt schattiert — dann zählt die Punktnormale, sonst die Flächennormale. Ohne Angabe sind alle glatt. Es ist das Glatt-Flag des Netzes
  (`Mesh::get_smooth`, aus `sharp_face`), das `MikkMeshWrapper::GetNormal` liest — NICHT das Flag, das `Mesh::pack_shaders` bei Eckennormalen auf „glatt" überschreibt (das gilt
  nur für den Shader, nicht für die Tangenten).
* `ecken_normalen` (T,3,3), optional: Normalen je Dreiecksecke (Blenders `corner_normals`, Bereich CORNER — scharfe Kanten, eigene Normalen). Gesetzt, ersetzt es die
  Punktnormalen (`corner_normal ? corner_normal[Ecke] : vertex_normal[Punkt]` in Cycles); `normalen` wird dann nicht gebraucht. Flache Dreiecke bleiben im Modus `'cycles'`
  bei der Flächennormale (`compute_normal`); im Modus `'blender'` gilt die Eckennormale für jede Ecke (so liest `calc_tangents` die `corner_normals()`).
* Rückgabe je Dreiecksecke (Index `dreieck * 3 + ecke`): Tangente (xyz) und Vorzeichen der Bitangente (+1.0, wenn `orientation` wahr, sonst -1.0), wie
  `MikkMeshWrapper::SetTangentSpace` in Cycles (`intern/cycles/scene/mesh.cpp`).

`modus='cycles'` (Vorgabe) ist Cycles: glatte Normalen gehen durch `packed_normal` (Oktaeder, 2 × 16 Bit) und zurück, flache Dreiecke bekommen `Mesh::Triangle::compute_normal`.
`modus='blender'` ist Blenders Python-Aufruf `mesh.calc_tangents()` (float-Normalen, Newell-Flächennormale) — nur zum Vergleich mit Blender gedacht.

Die Rechnung steckt in einer kleinen DLL (`mikkhuelle/`), die beim ersten Aufruf mit MSVC gebaut wird (`Hautbackenmikkbau`); ohne Compiler gibt es einen Fehler mit der Ursache,
keine Näherung. Quelle der Algorithmen: `mikktspace/HERKUNFT.txt`.

Anbindung an `Hautbackenflaeche` (nicht geändert): `Hautbackentangenten.berechnen(f.punkte, f.dreiecke, f.uv_ecken, f.normalen())` liefert `(T,3,3)` und `(T,3)`; `tangenten()` dort
ist `(T,3,4)` mit dem Vorzeichen in `w` — `np.concatenate([t, v[..., None]], axis=2)`.
"""

import numpy as np

from .hautbackenmikkdll import Hautbackenmikkdll

__all__ = ['Hautbackentangenten']

MODI = {'cycles': 0, 'blender': 1}


class Hautbackentangenten:
    @staticmethod
    def _felder(punkte, dreiecke):
        p = np.ascontiguousarray(punkte, dtype=np.float32)
        d = np.ascontiguousarray(dreiecke, dtype=np.int32)
        if p.ndim != 2 or p.shape[1] != 3:
            raise ValueError('punkte muss (N,3) sein, ist %s' % (p.shape,))
        if d.ndim != 2 or d.shape[1] != 3:
            raise ValueError('dreiecke muss (T,3) sein, ist %s' % (d.shape,))
        return p, d

    @classmethod
    def punktnormalen(cls, punkte, dreiecke):
        """`(N,3)` float32: Punktnormalen wie Blenders `mesh.vertex_normals` (Dreiecksnetz)."""
        p, d = cls._felder(punkte, dreiecke)
        return Hautbackenmikkdll.punktnormalen(p, d)

    @classmethod
    def berechnen(cls, punkte, dreiecke, uv_ecken, normalen=None, glatt=None, ecken_normalen=None, modus='cycles'):
        if modus not in MODI:
            raise ValueError('modus muss einer von %s sein, ist %r' % (sorted(MODI), modus))
        p, d = cls._felder(punkte, dreiecke)
        uv = np.ascontiguousarray(uv_ecken, dtype=np.float32)
        if uv.shape != (len(d), 3, 2):
            raise ValueError('uv_ecken muss (%d,3,2) sein, ist %s' % (len(d), uv.shape))
        if len(d) == 0:
            return np.zeros((0, 3, 3), dtype=np.float32), np.zeros((0, 3), dtype=np.float32)
        e = None
        n = None
        if ecken_normalen is not None:
            e = np.ascontiguousarray(ecken_normalen, dtype=np.float32)
            if e.shape != (len(d), 3, 3):
                raise ValueError('ecken_normalen muss (%d,3,3) sein, ist %s' % (len(d), e.shape))
        elif normalen is None:
            n = Hautbackenmikkdll.punktnormalen(p, d)
        else:
            n = np.ascontiguousarray(normalen, dtype=np.float32)
            if n.shape != p.shape:
                raise ValueError('normalen muss %s sein, ist %s' % (p.shape, n.shape))
        g = np.ones(len(d), dtype=np.uint8) if glatt is None else np.ascontiguousarray(glatt, dtype=bool).astype(np.uint8)
        if g.shape != (len(d),):
            raise ValueError('glatt muss (%d,) sein, ist %s' % (len(d), g.shape))
        return Hautbackenmikkdll.tangenten(p, d, uv, n, e, g, MODI[modus])
