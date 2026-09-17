# -*- coding: utf-8 -*-
u"""`Nahtteilung`: Nahtpunkte bekommen für die Textur Kopien, die Geometrie bleibt.

WARUM (Edgar, 13.09.2026, Bild vom Nacken: „Textur des Körpers hat bugs …
Nähte zwischen Körperteilen"): `uvs.npy` mittelt an einer Naht die Inseln,
jedes Viereck an der Naht spannte quer über die Textur. Mit den UVs je
Flächenecke (`uv_loops`) trennt der Unterteiler die Nahtpunkte nur für die
Textur.

Kunstnetz: ein 3×3-Gitter (9 Punkte, 4 Vierecke) mit einer Naht in der
mittleren Spalte — links liegen die UVs bei u ≤ 0,4, rechts bei u ≥ 0,6.

1. Die drei Nahtpunkte bekommen je eine Kopie, hinten angehängt.
2. Lage, Normale und Gewichte der ersten Punkte sind wie ohne Naht; die
   Kopien tragen die ihres Elternpunkts.
3. Kein Dreieck spannt mehr über die Naht.
4. Ohne Naht (alle Ecken-UVs stimmen mit den Punkt-UVs überein) kommt
   dasselbe heraus wie über den alten Weg.

Sabotage-Gegenprobe: in `anordnung` `zuordnung[doppelte] = eltern` → Fall 3 rot.
"""
from collections import namedtuple

import numpy as np
from django.test import SimpleTestCase
from humanbody_core.catmull_clark import CatmullClarkSubdivider
from humanbody_core.nahtteilung import Nahtteilung
from ._sicher import Sicher


#: Das Kunstgitter: Punkte (9, 3), Vierecke (4, 4), UVs je Punkt (9, 2), je Ecke (4, 4, 2).
Gitter = namedtuple('Gitter', 'punkte quads uvs ecken')


class NahtteilungTest(SimpleTestCase):

    def setUp(self):
        self.punkte, self.quads, self.uvs, self.ecken = NahtteilungTest.gitter()
        material = np.zeros(4, dtype=np.uint8)
        self.ohne = CatmullClarkSubdivider(self.quads, face_materials=material, uvs=self.uvs)
        self.mit = CatmullClarkSubdivider(self.quads, face_materials=material, uvs=self.uvs,
                                          uv_loops=self.ecken)

    def test_nahtpunkte_bekommen_kopien_hinten(self):
        self.assertEqual(Nahtteilung(self.quads, self.ecken).kopien, 3)
        self.assertEqual(self.ohne.naht_kopien, 0)
        self.assertGreater(self.mit.naht_kopien, 3)         # dazu die Kantenpunkte der Naht
        self.assertEqual(self.mit.sub_vertex_count, self.ohne.sub_vertex_count + self.mit.naht_kopien)

    def test_geometrie_wie_ohne_naht_und_kopien_auf_den_eltern(self):
        g = self.ohne.sub_vertex_count
        fein_ohne, fein_mit = self.ohne.subdivide(self.punkte), self.mit.subdivide(self.punkte)
        self.assertEqual(fein_ohne.tolist(), fein_mit[:g].tolist())
        eltern = self.mit._kopien_eltern
        self.assertEqual(fein_mit[g:].tolist(), fein_mit[eltern].tolist())
        n_ohne, n_mit = self.ohne.compute_quad_normals(fein_ohne), self.mit.compute_quad_normals(fein_mit)
        self.assertEqual(n_ohne.tolist(), n_mit[:g].tolist())
        self.assertEqual(n_mit[g:].tolist(), n_mit[eltern].tolist())
        gewichte = self.mit.propagate_skin_weights([[[0, 1.0]]] * 9, ['DEF-a'])
        self.assertEqual(gewichte['vertex_count'], self.mit.sub_vertex_count)
        self.assertEqual(gewichte['weights'][g], gewichte['weights'][eltern[0]])

    def test_kein_dreieck_spannt_ueber_die_naht(self):
        # Zwischen den Inseln (0,4 < u < 0,6) liegt keine Ecke — der alte Weg
        # setzt die Nahtpunkte gemittelt auf u = 0,5.
        for cc, dazwischen in ((self.ohne, True), (self.mit, False)):
            u = Sicher.wert(cc.uvs, 'UVs')[cc.triangles][:, :, 0]
            self.assertEqual(bool(((u > 0.4) & (u < 0.6)).any()), dazwischen)
        self.assertEqual(len(self.mit.triangles), len(self.ohne.triangles))
        self.assertLess(int(self.mit.triangles.max()), self.mit.sub_vertex_count)

    def test_ohne_naht_wie_der_alte_weg(self):
        glatt = CatmullClarkSubdivider(self.quads, uvs=self.uvs, uv_loops=self.uvs[self.quads])
        self.assertEqual(glatt.naht_kopien, 0)
        np.testing.assert_allclose(Sicher.wert(glatt.uvs, 'UVs'), Sicher.wert(self.ohne.uvs, 'UVs'),
                                   atol=1e-6)
        self.assertEqual(glatt.triangles.tolist(), self.ohne.triangles.tolist())

    @staticmethod
    def gitter():
        """Punkte (9, 3), Vierecke (4, 4), UVs je Punkt (9, 2) und je Ecke (4, 4, 2)."""
        xs, ys = np.meshgrid([0.0, 1.0, 2.0], [0.0, 1.0, 2.0])
        punkte = np.column_stack([xs.ravel(), ys.ravel(), np.zeros(9)])
        quads = np.array([[0, 1, 4, 3], [1, 2, 5, 4], [3, 4, 7, 6], [4, 5, 8, 7]])
        uvs = punkte[:, :2] / 2.0
        ecken = uvs[quads].copy()                      # (4, 4, 2)
        for fi, q in enumerate(quads):
            links = fi in (0, 2)
            for k, v in enumerate(q):
                if v in (1, 4, 7):                     # die mittlere Spalte: die Naht
                    ecken[fi, k, 0] = 0.4 if links else 0.6
        return Gitter(punkte, quads, uvs, ecken)
