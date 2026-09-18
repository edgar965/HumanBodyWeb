# -*- coding: utf-8 -*-
"""Koerperfeinheit: Corrective Smooth → Unterteilung → Hautverschiebung im Film.

An einem Wuerfel mit echtem Unterteiler (eine Stufe, mit UV-Naehten):

1. Kopfmaske: Gesichts- und Kopfknochen zaehlen, `forearm` nicht (das
   `ear` darin war die Falle beim Bestimmen der Liste).
2. Ohne Textur und ohne Korrektur ist `punkte()` genau `subdivide()`.
3. Textur 0,5 ueberall verschiebt nichts; Textur 1,0 schiebt jeden Punkt um
   +5 mm nach aussen (Radius des Wuerfels waechst).
4. Mit Korrektur kommt die Ruhelage unveraendert heraus.
5. `Feinkoerper` rechnet ueber die Feinheit und haelt nur SPEICHER Bilder.
"""

import numpy as np
from django.test import SimpleTestCase
from humanbody_core.catmull_clark import CatmullClarkSubdivider

from ._modelphysik import Modelphysik


def _wuerfel():
    punkte = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], dtype=np.float64) * 0.1
    quads = np.array([[0, 2, 3, 1], [4, 5, 7, 6], [0, 1, 5, 4], [2, 6, 7, 3], [0, 4, 6, 2], [1, 3, 7, 5]])
    ecke = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float64)
    uv_loops = np.stack([ecke * 0.3 + [0.35 * (i % 3), 0.5 * (i // 3)] for i in range(6)])
    return punkte, quads, uv_loops


class KoerperfeinheitTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kf = Modelphysik.modul('koerperfeinheit')
        cls.fk = Modelphysik.modul('feinkoerper')
        cls.punkte, cls.quads, uv_loops = _wuerfel()
        cls.cc = CatmullClarkSubdivider(cls.quads, levels=1, uv_loops=uv_loops)
        cls.dreiecke = np.vstack([cls.quads[:, [0, 1, 2]], cls.quads[:, [0, 2, 3]]])

    def test_kopfmaske_nimmt_kopf_und_gesicht_nicht_den_unterarm(self):
        namen = [
            'DEF-forearm.L',
            'DEF-spine.006',
            'DEF-nose',
            'MCH-eye.L',
            'DEF-spine.005',
            'ORG-teeth.T',
            'DEF-ear.L.002',
        ]
        gewichte = np.eye(len(namen))
        maske = self.kf.Koerperfeinheit.kopfmaske(gewichte, namen)
        self.assertEqual(list(maske), [0, 1, 1, 1, 0, 1, 1])

    def test_ohne_textur_und_korrektur_ist_es_die_unterteilung(self):
        f = self.kf.Koerperfeinheit(self.cc, self.quads, korrektur=False)
        np.testing.assert_allclose(
            f.punkte(self.punkte, self.dreiecke), self.cc.subdivide(self.punkte), atol=1e-12
        )

    def test_textur_mitte_schiebt_nichts_textur_eins_schiebt_fuenf_millimeter(self):
        mitte = np.full((4, 4), 0.5, dtype=np.float32)
        f = self.kf.Koerperfeinheit(self.cc, self.quads, mitte, korrektur=False)
        np.testing.assert_allclose(
            f.punkte(self.punkte, self.dreiecke), self.cc.subdivide(self.punkte), atol=1e-6
        )
        voll = np.ones((4, 4), dtype=np.float32)
        f = self.kf.Koerperfeinheit(self.cc, self.quads, voll, korrektur=False)
        fein = self.cc.subdivide(self.punkte)
        verschoben = f.punkte(self.punkte, self.dreiecke)
        r0 = np.linalg.norm(fein[: self.cc.geo_vertex_count], axis=1)
        r1 = np.linalg.norm(verschoben[: self.cc.geo_vertex_count], axis=1)
        self.assertTrue(np.all(r1 > r0))
        np.testing.assert_allclose(r1 - r0, 0.005, atol=5e-4)
        # Die Textur-Kopien liegen auf ihren Geometriepunkten.
        kopien = verschoben[self.cc.geo_vertex_count :]
        np.testing.assert_allclose(kopien, verschoben[self.cc.kopien_eltern], atol=1e-9)

    def test_korrektur_laesst_die_ruhelage_in_ruhe(self):
        namen = ['DEF-spine', 'DEF-spine.006']
        gewichte = np.zeros((8, 2))
        gewichte[:, 0] = 1.0
        f = self.kf.Koerperfeinheit(self.cc, self.quads).anlegen(self.punkte, gewichte, namen)
        self.assertIsNotNone(f.korrektur)
        np.testing.assert_allclose(
            f.punkte(self.punkte, self.dreiecke), self.cc.subdivide(self.punkte), atol=1e-9
        )
        self.assertIn('Korrekturglaettung an', f.beschreibung())

    def test_feinkoerper_rechnet_ueber_die_feinheit_und_haelt_wenige_bilder(self):
        F = self.fk.Feinkoerper
        voll = np.ones((4, 4), dtype=np.float32)
        f = self.kf.Koerperfeinheit(self.cc, self.quads, voll, korrektur=False)

        class Haut:
            punkte = self.punkte
            folge = np.stack([self.punkte + [0, 0.01 * i, 0] for i in range(6)])

        teil = {
            'haut': Haut(),
            'dreiecke': self.dreiecke,
            'feinheit': f,
            'unterteiler': self.cc,
            'fein_dreiecke': f.dreiecke,
        }
        np.testing.assert_allclose(F.ruhe(teil), f.punkte(self.punkte, self.dreiecke))
        for nummer in range(6):
            F.bild(teil, nummer)
        self.assertLessEqual(len(teil['fein_folge']), F.SPEICHER)
        np.testing.assert_allclose(F.bild(teil, 5), f.punkte(Haut.folge[5], self.dreiecke))
