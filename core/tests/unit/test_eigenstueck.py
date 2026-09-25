# -*- coding: utf-8 -*-
u"""Eigenes Stück: OBJ-Leser und grobe Platzierung (Kunstdaten, keine Bibliothek).

Sabotagen, die rot werden müssen: in `G9objleser._ecke` die negative Nummer
nicht vom Ende rechnen (Fall 2); in `G9eigenstueck.platzieren` Z-oben nicht
drehen (Fall 4); in `G9eigenstueck.einheit` die cm-Stufe streichen (Fall 3).
"""
import tempfile
import unittest
from pathlib import Path

import numpy as np
from Genesis9.eigenstueck import G9eigenstueck
from Genesis9.objleser import G9objleser

ORDNER = Path(__file__).resolve().parent


class ObjleserTest(unittest.TestCase):
    databases = []

    def _obj(self, text, mtl=None):
        ordner = tempfile.mkdtemp(dir=ORDNER)
        self.addCleanup(lambda: __import__('shutil').rmtree(ordner, ignore_errors=True))
        pfad = Path(ordner) / 'stueck.obj'
        pfad.write_text(text, encoding='utf-8')
        if mtl:
            (Path(ordner) / 'stueck.mtl').write_text(mtl, encoding='utf-8')
        return pfad

    def test_1_fuenfeck_wird_faecher_uv_je_ecke(self):
        netz = G9objleser.lesen(self._obj(
            'v 0 0 0\nv 1 0 0\nv 1 1 0\nv 0.5 1.5 0\nv 0 1 0\n'
            'vt 0 0\nvt 1 0\nvt 1 1\nvt .5 1\nvt 0 1\nf 1/1 2/2 3/3 4/4 5/5\n'))
        self.assertEqual(netz['flaechen'], [[0, 1, 2], [0, 2, 3], [0, 3, 4]])
        self.assertEqual(netz['flaechen_uv'], [[0, 1, 2], [0, 2, 3], [0, 3, 4]])

    def test_2_negative_nummern_zaehlen_vom_ende(self):
        netz = G9objleser.lesen(self._obj('v 0 0 0\nv 1 0 0\nv 0 1 0\nf -3 -2 -1\n'))
        self.assertEqual(netz['flaechen'], [[0, 1, 2]])
        # Ohne UV: eine Koordinate für alle Ecken, der Schreiber braucht einen Satz.
        self.assertEqual(netz['flaechen_uv'], [[0, 0, 0]])

    def test_5_mtl_farbe_des_ersten_materials(self):
        netz = G9objleser.lesen(self._obj(
            'mtllib stueck.mtl\nv 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n',
            mtl='newmtl a\nKd 0.2 0.4 0.6\nnewmtl b\nKd 1 1 1\n'))
        self.assertEqual(netz['farbe'], (0.2, 0.4, 0.6))


class PlatzierenTest(unittest.TestCase):
    databases = []

    def test_3_einheit_aus_der_hoehe(self):
        kleid_cm = np.array([[0, 0, 0], [0, 120, 0]], dtype=float)
        self.assertEqual(G9eigenstueck.einheit(kleid_cm), 'cm')
        self.assertEqual(G9eigenstueck.einheit(kleid_cm / 100), 'm')
        self.assertEqual(G9eigenstueck.einheit(kleid_cm * 10), 'mm')

    def test_4_z_oben_wird_y_oben(self):
        p, einheit = G9eigenstueck.platzieren(np.array([[0.0, 0.0, 0.0], [0.1, 0.2, 1.3]]),
                                              einheit='m', oben='z', zentrieren=False)
        self.assertEqual(einheit, 'm')
        np.testing.assert_allclose(p[1], [0.1, 1.3, -0.2])

    def test_6_massstab_und_versatz(self):
        p, _ = G9eigenstueck.platzieren(np.array([[0.0, 100.0, 0.0]]), einheit='cm',
                                        zentrieren=False, massstab=2.0, versatz_cm=-10.0)
        np.testing.assert_allclose(p[0], [0.0, 1.9, 0.0])

    def test_7_kennung_ohne_sonderzeichen(self):
        kennung, name = G9eigenstueck.kennung_und_name('Kleid: blau/Größe 38')
        self.assertEqual(name, 'Kleid blauGröße 38')
        self.assertRegex(kennung, r'^EIGEN_[A-Za-z0-9_]+$')


if __name__ == '__main__':
    unittest.main()
