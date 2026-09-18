# -*- coding: utf-8 -*-
"""Unterteilungsbau: gebaut, abgelegt, geladen — und der Unterteiler
rechnet mit geladenen Teilen dasselbe wie mit gebauten.

An einem Würfel (6 Vierecke, 8 Punkte, mit UV-Nähten), zwei Stufen. Der
Schlüssel ändert sich mit jeder Eingabe und mit `FASSUNG`; eine fremde
Datei greift nicht.
"""

from pathlib import Path
from unittest import TestCase

import numpy as np
from humanbody_core.catmull_clark import CatmullClarkSubdivider
from humanbody_core.unterteilungsbau import Unterteilungsbau

from core.tests.unit._pruefablage import Pruefablage


def _wuerfel():
    punkte = np.array([[x, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)], dtype=np.float64)
    quads = np.array([[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]])
    # Jede Fläche mit eigenem UV-Feld — alle Kanten sind Nähte.
    ecke = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float64)
    uv_loops = np.stack([ecke * 0.3 + [0.35 * (i % 3), 0.5 * (i // 3)] for i in range(6)])
    materialien = np.array([0, 0, 1, 1, 2, 2], dtype=np.uint8)
    return punkte, quads, uv_loops, materialien


class BauUndAblage(TestCase):
    def test_geladen_rechnet_wie_gebaut(self):
        punkte, quads, uv_loops, mat = _wuerfel()
        gebaut = CatmullClarkSubdivider(quads, face_materials=mat, levels=2, uv_loops=uv_loops)
        with Pruefablage.ordner('unterteilung_') as ordner:
            pfad = Path(ordner) / 'wuerfel.npz'
            Unterteilungsbau.speichern(pfad, gebaut.teile)
            teile = Unterteilungsbau.laden(pfad)
        geladen = CatmullClarkSubdivider(quads, teile=teile)
        np.testing.assert_array_equal(geladen.subdivide(punkte), gebaut.subdivide(punkte))
        np.testing.assert_array_equal(geladen.triangles, gebaut.triangles)
        np.testing.assert_array_equal(geladen.triangle_materials, gebaut.triangle_materials)
        self.assertEqual(geladen.groups, gebaut.groups)
        np.testing.assert_array_equal(geladen.uvs, gebaut.uvs)
        self.assertEqual(geladen.sub_vertex_count, gebaut.sub_vertex_count)
        self.assertEqual(geladen.naht_kopien, gebaut.naht_kopien)
        self.assertEqual(geladen.levels, 2)
        np.testing.assert_array_equal(
            geladen.compute_quad_normals(geladen.subdivide(punkte)),
            gebaut.compute_quad_normals(gebaut.subdivide(punkte)),
        )

    def test_zwei_stufen_vervierfachen_die_flaechen(self):
        punkte, quads, uv_loops, mat = _wuerfel()
        cc = CatmullClarkSubdivider(quads, face_materials=mat, levels=2, uv_loops=uv_loops)
        self.assertEqual(len(cc.triangles), 6 * 16 * 2)
        self.assertGreater(cc.naht_kopien, 0)
        self.assertEqual(cc.sub_vertex_count, cc.geo_vertex_count + len(cc.kopien_eltern))

    def test_schluessel_haengt_an_jeder_eingabe(self):
        _p, quads, uv_loops, mat = _wuerfel()
        a = Unterteilungsbau.schluessel(quads, mat, None, 2, uv_loops)
        self.assertEqual(len(a), 16)
        S = Unterteilungsbau.schluessel
        self.assertEqual(a, S(quads, mat, None, 2, uv_loops))
        self.assertNotEqual(a, S(quads, mat, None, 3, uv_loops))
        self.assertNotEqual(a, S(quads, mat, None, 2, None))
        andere = quads.copy()
        andere[0] = andere[0][[1, 2, 3, 0]]
        self.assertNotEqual(a, S(andere, mat, None, 2, uv_loops))
        alt = Unterteilungsbau.FASSUNG
        try:
            Unterteilungsbau.FASSUNG = alt + 1
            self.assertNotEqual(a, S(quads, mat, None, 2, uv_loops))
        finally:
            Unterteilungsbau.FASSUNG = alt
