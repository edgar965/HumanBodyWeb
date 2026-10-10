# -*- coding: utf-8 -*-
"""Hautbackenblendernormalen — die Normalen eines Netzes so, wie Blender sie aus denselben Rohdaten und denselben Punkten rechnet.

Blender v5.2.2 (`blenkernel/intern/mesh_normals.cc`, gelesen 10.10.2026), eins zu eins nachgebaut — Cycles liest die Shading-Normalen von dort
(`intern/cycles/blender/mesh.cpp`: `vert_normals()` bei Domain Punkt/Fläche, `corner_normals()` bei Domain Ecke):
  * `Mesh::normals_domain`: eigene Normalen → Ecke; alle Polygone scharf oder alle Kanten scharf → Fläche; weder scharfe Kanten noch scharfe Polygone → Punkt; sonst Ecke.
  * `face_normals_true` (Newell, `Hautbackenblenderflaechen`), `vert_normals_true` (winkelgewichtet), `corner_normals` (Fächer, `Hautbackenblenderfaecher`/`…ecken`).
  * Mit eigenen Normalen (`custom_normal`, INT16_2D auf der Ecke): `Mesh::face_normals`/`vert_normals` mischen die Eckennormalen (wie `polygon_normals`/`vertex_normals`).
Nicht gebaut: `custom_normal` als Float3 (freie Normalen aus Geometry Nodes) und auf Punkt/Fläche — dort fehlt jede Messung; solche Netze werfen einen Fehler.
Faustregel für die Anbindung: bei Domain 'CORNER' liest Cycles `ecken`, sonst `punkte` (und `smooth = False` je Dreieck bei Domain 'FACE' bzw. `sharp_face`).
Die Punkte sind die des Objektraums, in dem Blender rechnet; werden sie in den Weltraum gebracht (blendexport), gilt das nur für Drehung und gleichmäßigen Maßstab.
"""

import numpy as np

from .hautbackenblendereintraege import Hautbackenblendereintraege
from .hautbackenblenderecken import Hautbackenblenderecken
from .hautbackenblenderfaecher import Hautbackenblenderfaecher
from .hautbackenblenderflaechen import Hautbackenblenderflaechen as Flaechen

__all__ = ['Hautbackenblendernormalen']


class Hautbackenblendernormalen:
    @staticmethod
    def domain(anzahl_polygone, scharf_kante=None, scharf_flaeche=None, eigene_normale=None):
        """`Mesh::normals_domain`: 'POINT', 'FACE' oder 'CORNER'."""
        if anzahl_polygone == 0:
            return 'POINT'
        if eigene_normale is not None:
            return 'CORNER'
        flaeche = None if scharf_flaeche is None else np.asarray(scharf_flaeche, dtype=bool)
        kante = None if scharf_kante is None else np.asarray(scharf_kante, dtype=bool)
        if flaeche is not None and flaeche.all():
            return 'FACE'
        if kante is not None and len(kante) and kante.all():
            return 'FACE'
        if (kante is None or not kante.any()) and (flaeche is None or not flaeche.any()):
            return 'POINT'
        return 'CORNER'

    @staticmethod
    def berechnen(punkte, poly_start, poly_punkte, kanten=None, ecke_kante=None, scharf_kante=None, scharf_flaeche=None, eigene_normale=None, ecken_immer=False):
        """Blenders `polygon_normals`, `vertex_normals` und `corner_normals` für die gegebenen Punkte.

        Eingaben wie Blender sie hält: `punkte` (N,3) float; `poly_start` (P+1) Offsets in die Ecken (letzter = L); `poly_punkte` (L) = `.corner_vert`;
        `kanten` (E,2) = `.edge_verts` (Blender 5.2 liest sie für die Normalen nicht — nur der Vollständigkeit halber); `ecke_kante` (L) = `.corner_edge`;
        `scharf_kante` (E) bool = `sharp_edge`; `scharf_flaeche` (P) bool = `sharp_face`; `eigene_normale` (L,2) int16 = `custom_normal`.
        Fehlendes Attribut = None.
        Rückgabe (float32): `flaechen` (P,3) = `polygon_normals`, `punkte` (N,3) = `vertex_normals`, `ecken` (L,3) = `corner_normals` (nur bei Domain 'CORNER', sonst
        None — mit `ecken_immer=True` immer), `domain` ('POINT'|'FACE'|'CORNER'), außerdem `flaechen_wahr` / `punkte_wahr`: die Normalen ohne Einfluss eigener Normalen
        (`face_normals_true` / `vert_normals_true`).
        """
        p = np.ascontiguousarray(punkte, dtype=np.float32).reshape(-1, 3)
        ps = np.asarray(poly_start, dtype=np.int64)
        pp = np.asarray(poly_punkte, dtype=np.int64)
        flaechen = len(ps) - 1
        domain = Hautbackenblendernormalen.domain(flaechen, scharf_kante, scharf_flaeche, eigene_normale)
        sk = None if scharf_kante is None else np.asarray(scharf_kante, dtype=bool)
        sf = None if scharf_flaeche is None else np.asarray(scharf_flaeche, dtype=bool)
        eigene = None if eigene_normale is None else np.asarray(eigene_normale, dtype=np.int16).reshape(-1, 2)
        if len(pp) != int(ps[-1]) or (sf is not None and len(sf) != flaechen):
            raise ValueError('poly_start/poly_punkte/scharf_flaeche passen nicht zusammen')
        if eigene is not None and len(eigene) != len(pp):
            raise ValueError('eigene_normale braucht eine Zeile je Ecke')
        if domain == 'CORNER' and (sk is not None) and ecke_kante is None:
            raise ValueError('scharf_kante braucht ecke_kante (.corner_edge)')
        fn = Flaechen.flaechennormalen(p, ps, pp)
        e = Hautbackenblendereintraege(ps, pp, len(p))
        pn = Flaechen.punktnormalen(p, e, fn)
        aus = {'domain': domain, 'flaechen': fn, 'punkte': pn, 'flaechen_wahr': fn, 'punkte_wahr': pn, 'ecken': None}
        if flaechen == 0:
            return aus
        if domain == 'CORNER':
            ek = None if ecke_kante is None else np.asarray(ecke_kante, dtype=np.int64)
            faecher = Hautbackenblenderfaecher(e, ek, sk, sf)
            ecken = Hautbackenblenderecken.berechnen(p, e, faecher, fn, eigene)
            aus['ecken'] = ecken
            if eigene is not None:
                aus['punkte'] = Flaechen.ecken_zu_punkten(p, e, ecken)
                aus['flaechen'] = Flaechen.ecken_zu_flaechen(ps, ecken)
        elif ecken_immer:
            aus['ecken'] = pn[pp] if domain == 'POINT' else np.repeat(fn, np.diff(ps), axis=0)
        return aus
