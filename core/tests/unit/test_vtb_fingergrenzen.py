# -*- coding: utf-8 -*-
u"""Fingergrenzen des SMPL-X-BVH: unmoegliche Fingerdrehungen werden geklemmt.

DER ANLASS (12.09.2026, Edgar an `0001_Dance`: „manchmal gehen die Finger
nach oben, also brechen durch"): GEM-X lieferte das linke Zeigefinger-
Grundgelenk mit 106 Grad Beugung — der Finger klappte durch die Handflaeche.
Der Retarget war exakt (0,0 Grad Abweichung je Fingerknochen), die Quelle
nicht. Seither klemmt `Fingergrenzen` die 30 Finger beim Schreiben
(`Smplxbvh`) und nachtraeglich (`FingergrenzenBvh`).

BDD - GEGEBEN / DANN
====================
    DerGelenkrahmen     ... beugt jeden Finger zur Flaeche, auch den schraegen kleinen
    DieFingergrenzen    ... fangen 120 Grad Grundgelenk und Seitbewegung im Mittelgelenk
    DasWerkzeug         ... laesst Koerper und Wurzelbahn einer BVH unangetastet

Sabotage-Gegenprobe (12.09.2026): `_spreizfaktor` auf 1 -> „gebeugt spreizt
nicht" rot; `np.cross(n, t)` zu `np.cross(t, n)` -> „zur Flaeche" rot.
"""
import os
import tempfile
import unittest

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np                                          # noqa: E402
from scipy.spatial.transform import Rotation                # noqa: E402

from fingergrenzen import Fingergrenzen                     # noqa: E402
from SMPL.finger import Smplxfinger                         # noqa: E402


def _wxyz(rot):
    x, y, z, w = rot.as_quat()
    return np.array([w, x, y, z])


def _im_rahmen(wxyz, B):
    u"""(Beugung, Spreizung, Verdrehung) einer Drehung im Gelenkrahmen."""
    rot = Rotation.from_quat([wxyz[1], wxyz[2], wxyz[3], wxyz[0]])
    f, t, n = Rotation.from_matrix(B.T @ rot.as_matrix() @ B).as_euler('ZYX', degrees=True)
    return f, n, t


class DerGelenkrahmen(unittest.TestCase):

    def test_beugung_fuehrt_zur_handflaeche(self):
        u"""+60 Grad um f bringt den Knochen nach -y — links, rechts, schraeger Kleinfinger."""
        for name in ('left_index1', 'left_pinky1', 'right_index1', 'right_pinky1', 'right_ring2'):
            with self.subTest(gelenk=name):
                B = Fingergrenzen.rahmen(Smplxfinger.NAMEN.index(name), np)
                n, t, f = B.T
                self.assertAlmostEqual(np.linalg.det(B), 1.0, places=9)
                gedreht = Rotation.from_rotvec(np.radians(60) * f).apply(t)
                self.assertLess(gedreht[1], -0.8)
                self.assertGreater(np.dot(gedreht, t), 0.45)

    def test_endglied_nimmt_die_richtung_des_mittelglieds(self):
        B2 = Fingergrenzen.rahmen(Smplxfinger.NAMEN.index('left_middle2'), np)
        B3 = Fingergrenzen.rahmen(Smplxfinger.NAMEN.index('left_middle3'), np)
        np.testing.assert_allclose(B2, B3)


class DieFingergrenzen(unittest.TestCase):

    def _feld(self):
        return np.tile(np.array([1.0, 0.0, 0.0, 0.0]), (2, len(Smplxfinger.NAMEN), 1))

    def test_grundgelenk_120_grad_wird_90_und_spreizt_gebeugt_nicht(self):
        gelenk = Smplxfinger.NAMEN.index('left_pinky1')
        B = Fingergrenzen.rahmen(gelenk, np)
        n, t, f = B.T
        feld = self._feld()
        feld[0, gelenk] = _wxyz(Rotation.from_rotvec(np.radians(120) * f)
                                * Rotation.from_rotvec(np.radians(20) * n))
        # Gestreckt darf der Finger 20 Grad spreizen.
        feld[1, gelenk] = _wxyz(Rotation.from_rotvec(np.radians(20) * n))
        self.assertEqual(Fingergrenzen.anwenden(feld, np), 1)
        beugung, spreizung, _ = _im_rahmen(feld[0, gelenk], B)
        self.assertAlmostEqual(beugung, 90.0, places=3)
        self.assertAlmostEqual(spreizung, 0.0, places=3)
        _, spreizung, _ = _im_rahmen(feld[1, gelenk], B)
        self.assertAlmostEqual(spreizung, 20.0, places=3)

    def test_mittelgelenk_ist_ein_scharnier(self):
        gelenk = Smplxfinger.NAMEN.index('right_middle2')
        B = Fingergrenzen.rahmen(gelenk, np)
        n, t, f = B.T
        feld = self._feld()
        feld[0, gelenk] = _wxyz(Rotation.from_rotvec(np.radians(25) * n))     # seitlich
        feld[1, gelenk] = _wxyz(Rotation.from_rotvec(np.radians(60) * f))     # gebeugt: erlaubt
        self.assertEqual(Fingergrenzen.anwenden(feld, np), 1)
        _, spreizung, _ = _im_rahmen(feld[0, gelenk], B)
        self.assertAlmostEqual(spreizung, Fingergrenzen.GRENZEN[2][3], places=3)
        beugung, _, _ = _im_rahmen(feld[1, gelenk], B)
        self.assertAlmostEqual(beugung, 60.0, places=3)

    def test_daumen_wird_nur_im_gesamtwinkel_gekappt(self):
        gelenk = Smplxfinger.NAMEN.index('left_thumb1')
        achse = np.array([0.3, 0.9, 0.3]) / np.linalg.norm([0.3, 0.9, 0.3])
        feld = self._feld()
        feld[0, gelenk] = _wxyz(Rotation.from_rotvec(np.radians(130) * achse))
        feld[1, gelenk] = _wxyz(Rotation.from_rotvec(np.radians(80) * achse))
        self.assertEqual(Fingergrenzen.anwenden(feld, np), 1)
        w = feld[0, gelenk]
        vektor = Rotation.from_quat([w[1], w[2], w[3], w[0]]).as_rotvec()
        self.assertAlmostEqual(np.degrees(np.linalg.norm(vektor)), Fingergrenzen.DAUMEN_MAX, places=3)
        np.testing.assert_allclose(vektor / np.linalg.norm(vektor), achse, atol=1e-6)

    def test_ohne_verstoss_bleibt_alles_wie_es_war(self):
        feld = self._feld()
        vorher = feld.copy()
        self.assertEqual(Fingergrenzen.anwenden(feld, np), 0)
        np.testing.assert_array_equal(feld, vorher)


class DasWerkzeug(unittest.TestCase):
    u"""`FingergrenzenBvh` auf einem kleinen SMPL-X-BVH mit einem Ausreisser."""

    def _bvh_schreiben(self, pfad):
        from gvhmrlauf import Gvhmrlauf
        from smplxbvh import Smplxbvh
        Gvhmrlauf.hilfsmodule_bereitstellen()
        import bvh as bvh_util
        namen = Smplxbvh.namen()
        offsets = Smplxbvh.offsets(np)
        eltern = Smplxbvh.eltern(np)
        anzahl = 3
        rot = np.zeros((anzahl, len(namen), 3))
        gelenk = namen.index('left_index1')
        B = Fingergrenzen.rahmen(Smplxfinger.NAMEN.index('left_index1'), np)
        f = B[:, 2]
        # Bild 1: 120 Grad Beugung als Euler — der Ausreisser. BVH-Kanaele
        # Z Y X wirken nacheinander (R = Rz Ry Rx), bei scipy „ZYX" intrinsisch.
        rot[1, gelenk] = Rotation.from_rotvec(np.radians(120) * f).as_euler('ZYX', degrees=True)
        rot[:, 1] = [10.0, 0.0, 0.0]                      # Left_hip: Koerper, bleibt
        pos = np.tile(offsets, (anzahl, 1, 1))
        pos[:, 0] = [[5.0, 90.0, -3.0]] * anzahl          # Wurzelbahn, bleibt
        bvh_util.save(pfad, {'rotations': rot, 'positions': pos, 'offsets': offsets,
                             'parents': eltern, 'names': namen, 'order': 'zyx',
                             'frametime': 1.0 / 30.0})
        return bvh_util

    def test_koerper_und_wurzel_bleiben_nur_der_finger_wird_geklemmt(self):
        from fingergrenzen_bvh import FingergrenzenBvh
        ordner = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(__file__)))
        try:
            quelle = os.path.join(ordner, 'probe.bvh')
            bvh_util = self._bvh_schreiben(quelle)
            vorher = bvh_util.load(quelle)
            self.assertEqual(FingergrenzenBvh(quelle).anwenden(), 1)
            nachher = bvh_util.load(quelle)
            np.testing.assert_allclose(nachher['positions'][:, 0], vorher['positions'][:, 0], atol=1e-5)
            np.testing.assert_allclose(nachher['rotations'][:, 1], vorher['rotations'][:, 1], atol=1e-5)
            np.testing.assert_allclose(nachher['offsets'], vorher['offsets'], atol=1e-5)
            gelenk = vorher['names'].index('left_index1')
            neu = Rotation.from_euler('ZYX', nachher['rotations'][1, gelenk], degrees=True)
            B = Fingergrenzen.rahmen(Smplxfinger.NAMEN.index('left_index1'), np)
            beugung, _, _ = _im_rahmen(_wxyz(neu), B)
            self.assertAlmostEqual(beugung, 90.0, places=3)
        finally:
            for name in os.listdir(ordner):
                os.remove(os.path.join(ordner, name))
            os.rmdir(ordner)
