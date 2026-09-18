# -*- coding: utf-8 -*-
u"""Dreiecke in der Catmull-Clark-Unterteilung (17.09.2026).

Anlass: die Daz-Garderobe von Genesis 9 — das Basishemd hat 132 Dreiecke
unter 7.878 Vierecken, der Helm 125, der Reißverschluss-Schieber nur
Dreiecke. Ein Dreieck steht im (F, 4)-Feld mit -1 an vierter Stelle und
wird in der ersten Stufe zu DREI Vierecken.

Geprüft an einer Pyramide (4 Dreiecke auf einem Viereck): Gewichte je Zeile
summieren zu 1, die Flächenzahl stimmt, der Flächenpunkt eines Dreiecks ist
das Mittel seiner drei Ecken, die Naht-UVs tragen kein -1 mehr weiter, und
ein reines Vierecknetz rechnet Bit für Bit wie vor dem Umbau (Würfel gegen
die alte Formel 1/16 je Ecke am Kantenpunkt).
"""
from unittest import TestCase

import numpy as np

from humanbody_core.catmull_clark import CatmullClarkSubdivider
from humanbody_core.nahtteilung import Nahtteilung
from humanbody_core.unterteilungsstufe import Unterteilungsstufe


def _pyramide():
    punkte = np.array([[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1],
                       [0.5, 1, 0.5]], dtype=np.float64)
    flaechen = np.array([[0, 1, 2, 3],
                         [0, 4, 1, -1], [1, 4, 2, -1],
                         [2, 4, 3, -1], [3, 4, 0, -1]])
    ecke = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float64)
    uv_loops = np.stack([ecke * 0.2 + [0.25 * i, 0.0] for i in range(5)])
    return punkte, flaechen, uv_loops


class DreieckeInDerStufe(TestCase):

    def test_ein_dreieck_wird_drei_vierecke(self):
        _, flaechen, _ = _pyramide()
        stufe = Unterteilungsstufe(flaechen, 5)
        gewichte, neue, gesamt = stufe.bauen()
        self.assertEqual(len(neue), 4 + 4 * 3)
        self.assertEqual(stufe.N_e, 8)                 # 4 Grund- + 4 Seitenkanten
        self.assertEqual(gesamt, 5 + 5 + 8)
        self.assertTrue((neue >= 0).all())
        np.testing.assert_allclose(np.asarray(gewichte.sum(axis=1)).ravel(), 1.0)

    def test_flaechenpunkt_eines_dreiecks_ist_das_mittel_der_drei_ecken(self):
        punkte, flaechen, _ = _pyramide()
        stufe = Unterteilungsstufe(flaechen, 5)
        gewichte, _, _ = stufe.bauen()
        fein = gewichte @ punkte
        # Flaeche 1 = Dreieck [0, 4, 1]; ihr Punkt steht in Zeile N_v + 1.
        np.testing.assert_allclose(fein[5 + 1], punkte[[0, 4, 1]].mean(axis=0))
        # Flaeche 0 = das Viereck: Mittel der vier.
        np.testing.assert_allclose(fein[5 + 0], punkte[[0, 1, 2, 3]].mean(axis=0))

    def test_sabotage_einheitsgewicht_wuerde_auffallen(self):
        u"""Wer beim Dreieck weiter 0,25 je Ecke nimmt, summiert auf 0,75."""
        _, flaechen, _ = _pyramide()
        stufe = Unterteilungsstufe(flaechen, 5)
        stufe._kantentopologie()
        stufe._nachbarschaft()
        for fi in range(stufe.N_f):
            for v in stufe.quads[fi][:stufe.ecken[fi]]:
                stufe._gewicht(stufe.N_v + fi, int(v), 0.25)
        summen = np.bincount(stufe.rows, weights=stufe.vals)
        self.assertAlmostEqual(summen[5 + 1], 0.75)

    def test_naht_ohne_minus_eins(self):
        punkte, flaechen, uv_loops = _pyramide()
        naht = Nahtteilung(flaechen, uv_loops)
        self.assertEqual(naht.anzahl, 4 + 3 * 4)        # jede Flaeche eigene Insel
        self.assertTrue((naht.quads[1:, 3] == -1).all())
        stufe = Unterteilungsstufe(flaechen, 5)
        stufe.bauen()
        naht.stufe(stufe)
        self.assertTrue((naht.quads >= 0).all())
        self.assertEqual(len(naht.quads), 4 + 4 * 3)

    def test_ganzer_unterteiler_mit_material_und_naehten(self):
        punkte, flaechen, uv_loops = _pyramide()
        material = np.array([0, 1, 1, 1, 1], dtype=np.uint8)
        cc = CatmullClarkSubdivider(flaechen, face_materials=material, levels=1,
                                    uv_loops=uv_loops)
        fein = cc.subdivide(punkte)
        self.assertEqual(len(cc.triangles), 2 * (4 + 12))
        # Material 0 = das Viereck (4 Vierecke = 8 Dreiecke), Material 1 = 12 Vierecke.
        self.assertEqual([g['count'] // 3 for g in cc.groups], [8, 24])
        self.assertTrue(np.isfinite(fein).all())
        self.assertEqual(len(cc.uvs), cc.sub_vertex_count)
        normalen = cc.compute_quad_normals(fein)
        self.assertEqual(normalen.shape, (cc.sub_vertex_count, 3))

    def test_reines_vierecknetz_bleibt_bitgleich(self):
        u"""Kantenpunkt im Vierecknetz: 1/4 + 2/16 je Ende, 1/16 je andere Ecke."""
        quads = np.array([[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1],
                          [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]])
        stufe = Unterteilungsstufe(quads, 8)
        gewichte, neue, _ = stufe.bauen()
        self.assertEqual(len(neue), 24)
        zeile = gewichte.tocsr()[8 + 6]                 # erster Kantenpunkt
        werte = sorted(np.round(zeile.data, 12))
        self.assertEqual(werte, [0.0625] * 4 + [0.375] * 2)
