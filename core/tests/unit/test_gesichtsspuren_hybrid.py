# -*- coding: utf-8 -*-
u"""Gesichtsspuren: die SMPLest-X-Ausdrücke eines Hybrids kommen aufs Rig.

Der Hybrid hatte vom 05.04. bis zum 12.09.2026 kein Gesicht — die Datei
`<gesicht>_blendshapes.json` wurde geschrieben, aber nirgends gelesen. Hier
steht, was die Zusammenführung seither verspricht: Liegt die Datei neben
der v4-BVH, stellen die Ausdrücke die Gesichtsknochen; der gemessene
Kiefer ersetzt den geratenen; die Körper- und Fingerspuren bleiben
unberührt; ohne Datei ändert sich nichts.
"""
import json
import os

from django.test import SimpleTestCase

from core.dienste.gesichtsspuren import Gesichtsspuren
from humanbody_core.skeleton.bewegungsspuren import Bewegungsspuren
from humanbody_core.skeleton.face_blendshapes import Gesichtsformen
from humanbody_core.skeleton.kieferspuren import Kieferspuren
from ._pruefablage import Pruefablage


def gemisch(bilder=3):
    q = [0.0, 0.0, 0.0, 1.0]
    tracks = {'DEF-spine': q * bilder, 'DEF-f_index.01.L': q * bilder,
              'DEF-jaw': q * bilder}
    return Bewegungsspuren(duration=bilder / 30.0, times=[i / 30.0 for i in range(bilder)],
                           tracks=tracks, frame_count=bilder, mapped_bones=sorted(tracks))


def ausdrucksdatei(ordner, bilder=3, kiefer=0.4):
    u"""Die Datei, wie `Ausdrucksreihe.schreiben` sie ablegt."""
    bvh = os.path.join(ordner, 'v4_probe.bvh')
    open(bvh, 'w').close()
    daten = {'fps': 30.0, 'frame_count': bilder,
             'expression_frames': [[0.5] + [0.0] * 9] * bilder,
             'jaw_frames': [[kiefer, 0.0, 0.0]] * bilder,
             'face_points': [[[1.0, 2.0]] * 72] * bilder,
             'detected_count': bilder}
    with open(Gesichtsspuren.datei(bvh), 'w') as f:
        json.dump(daten, f)
    return bvh


def winkel_x(spuren, knochen, bild=0):
    u"""Die X-Drehung eines Bildes in Bogenmaß (kleine Winkel: 2·asin(x))."""
    import math
    x = spuren.tracks[knochen][bild * 4]
    return 2.0 * math.asin(x)


class DieDatei(SimpleTestCase):

    databases = set()

    def test_ohne_datei_kommt_none(self):
        with Pruefablage.ordner() as ordner:
            bvh = os.path.join(ordner, 'v4_leer.bvh')
            self.assertIsNone(Gesichtsspuren.laden(bvh))

    def test_die_datei_liegt_neben_der_bvh(self):
        self.assertEqual(Gesichtsspuren.datei('a/b/v4_x.bvh'), 'a/b/v4_x_blendshapes.json')

    def test_geladen_kommen_gesichtsknochen(self):
        with Pruefablage.ordner() as ordner:
            spuren = Gesichtsspuren.laden(ausdrucksdatei(ordner))
        self.assertEqual(spuren.frame_count, 3)
        for knochen in ('DEF-jaw', 'DEF-lip.T.L', 'DEF-brow.T.L'):
            self.assertIn(knochen, spuren.tracks)


class DerKiefer(SimpleTestCase):
    u"""Der gemessene Kiefer ersetzt den geratenen aus dem Ausdruckswert."""

    databases = set()

    def test_der_gemessene_winkel_steht_auf_dem_kiefer(self):
        with Pruefablage.ordner() as ordner:
            spuren = Gesichtsspuren.laden(ausdrucksdatei(ordner, kiefer=0.4))
        self.assertAlmostEqual(winkel_x(spuren, 'DEF-jaw'), 0.4, places=3)
        self.assertAlmostEqual(winkel_x(spuren, 'DEF-chin'), 0.12, places=3)

    def test_ohne_kiefer_bleibt_der_geratene(self):
        u"""Alte Dateien (vor dem 12.09.2026) haben kein `jaw_frames`."""
        spuren = Gesichtsformen.blendshapes_to_bone_tracks(
            {'fps': 30.0, 'expression_frames': [[1.0] + [0.0] * 9]})
        self.assertAlmostEqual(winkel_x(spuren, 'DEF-jaw'), 0.015, places=4)

    def test_der_kiefer_oeffnet_nie_negativ_und_nie_zu_weit(self):
        self.assertEqual(Kieferspuren.winkel([-0.3, 0, 0]), 0.0)
        self.assertEqual(Kieferspuren.winkel([2.0, 0, 0]), Kieferspuren.HOECHSTENS)
        self.assertEqual(Kieferspuren.winkel([]), 0.0)

    def test_ein_kurzer_kiefer_laesst_die_letzten_bilder_geschlossen(self):
        spuren = Gesichtsformen.blendshapes_to_bone_tracks(
            {'fps': 30.0, 'expression_frames': [[0.0] * 10] * 3,
             'jaw_frames': [[0.3, 0, 0]]})
        self.assertAlmostEqual(winkel_x(spuren, 'DEF-jaw', 0), 0.3, places=3)
        self.assertAlmostEqual(winkel_x(spuren, 'DEF-jaw', 2), 0.0, places=6)


class DasMischen(SimpleTestCase):

    databases = set()

    def test_das_gesicht_kommt_aus_den_ausdruecken(self):
        with Pruefablage.ordner() as ordner:
            ausdruecke = Gesichtsspuren.laden(ausdrucksdatei(ordner, kiefer=0.4))
        gemischt = Gesichtsspuren.mischen(gemisch(), ausdruecke)
        self.assertAlmostEqual(winkel_x(gemischt, 'DEF-jaw'), 0.4, places=3)
        self.assertIn('DEF-lip.T.L', gemischt.tracks)

    def test_koerper_und_finger_bleiben(self):
        with Pruefablage.ordner() as ordner:
            ausdruecke = Gesichtsspuren.laden(ausdrucksdatei(ordner))
        gemischt = Gesichtsspuren.mischen(gemisch(), ausdruecke)
        self.assertEqual(gemischt.tracks['DEF-spine'], [0.0, 0.0, 0.0, 1.0] * 3)
        self.assertEqual(gemischt.tracks['DEF-f_index.01.L'], [0.0, 0.0, 0.0, 1.0] * 3)
        self.assertEqual(gemischt.frame_count, 3)

    def test_ohne_ausdruecke_bleibt_das_gemisch(self):
        vorher = gemisch()
        self.assertIs(Gesichtsspuren.mischen(vorher, None), vorher)
        self.assertIs(Gesichtsspuren.mischen(vorher, Bewegungsspuren.leer()), vorher)

    def test_ein_laengeres_gesicht_wird_auf_den_koerper_gekuerzt(self):
        with Pruefablage.ordner() as ordner:
            ausdruecke = Gesichtsspuren.laden(ausdrucksdatei(ordner, bilder=7))
        gemischt = Gesichtsspuren.mischen(gemisch(bilder=3), ausdruecke)
        self.assertEqual(len(gemischt.tracks['DEF-jaw']), 3 * 4)
