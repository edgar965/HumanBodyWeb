# -*- coding: utf-8 -*-
u"""Gesichtsspuren: die SMPLest-X-Ausdrücke eines Hybrids kommen aufs Rig.

Der Hybrid hatte vom 05.04. bis zum 12.09.2026 kein Gesicht — die Datei
`<gesicht>_blendshapes.json` wurde geschrieben, aber nirgends gelesen. Hier
steht, was die Zusammenführung seither verspricht: Liegt die Datei neben
der v4-BVH, stellen die Ausdrücke die Gesichtsknochen; der gemessene
Kiefer ersetzt den geratenen; die Körper- und Fingerspuren bleiben
unberührt; ohne Datei ändert sich nichts.

UND SEIT DEM ABEND DES 12.09.2026 (Edgar: „das Gesicht ist zermatscht"):
Die Ausdrücke sind Deltas zur Ruhelage, der Player setzt Spuren absolut.
`mischen` legt sie deshalb auf die Ruhelage des Zielskeletts — `ruhe · delta`,
dieselbe Reihenfolge wie `facial_expression.js`. Ein neutrales Gesicht
steht danach in seiner Ruhelage, nicht auf der Einheitsdrehung.
Sabotage-Gegenprobe: `auf_ruhelage` weglassen → `DasMischen` rot.
"""
import json
import math
import os

import numpy as np
from django.test import SimpleTestCase

from core.dienste.gesichtsspuren import Gesichtsspuren
from humanbody_core.quaternion import Quat
from humanbody_core.skeleton.bewegungsspuren import Bewegungsspuren
from humanbody_core.skeleton.face_blendshapes import Gesichtsformen
from humanbody_core.skeleton.kieferspuren import Kieferspuren
from humanbody_core.skeleton.skeleton_geometry import SkeletonGeometry
from ._pruefablage import Pruefablage

#: Ruhelage des Kiefers in der Skelettattrappe: 90° um Y — weit weg von der
#: Einheitsdrehung, damit ein vergessenes `auf_ruhelage` sofort auffällt.
KIEFER_RUHE = [0.0, math.sin(math.pi / 4), 0.0, math.cos(math.pi / 4)]


def skelett():
    u"""Ein DEF-Skelett mit den Knochen, die die Tests anfassen."""
    ruhe = [0.0, 0.0, 0.0, 1.0]
    knochen = [{'name': 'DEF-spine', 'parent': None,
                'local_position': [0, 0, 0], 'local_quaternion': ruhe},
               {'name': 'DEF-jaw', 'parent': 'DEF-spine',
                'local_position': [0, 1, 0], 'local_quaternion': KIEFER_RUHE},
               {'name': 'DEF-chin', 'parent': 'DEF-jaw',
                'local_position': [0, 0.1, 0], 'local_quaternion': ruhe},
               {'name': 'DEF-f_index.01.L', 'parent': 'DEF-spine',
                'local_position': [1, 0, 0], 'local_quaternion': ruhe}]
    return SkeletonGeometry.from_three(knochen)


def delta_x(spuren, knochen, ruhe, bild=0):
    u"""Die X-Drehung eines Bildes RELATIV zur Ruhelage (Bogenmaß)."""
    q = np.asarray(spuren.tracks[knochen][bild * 4:bild * 4 + 4])
    delta = Quat.mul(Quat.inv(np.asarray(ruhe, dtype=float)), q)
    return 2.0 * math.asin(delta[0])


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

    def mischen(self, gemischt, ausdruecke):
        return Gesichtsspuren.mischen(gemischt, ausdruecke, geometrie=skelett())

    def test_das_gesicht_kommt_aus_den_ausdruecken(self):
        with Pruefablage.ordner() as ordner:
            ausdruecke = Gesichtsspuren.laden(ausdrucksdatei(ordner, kiefer=0.4))
        gemischt = self.mischen(gemisch(), ausdruecke)
        self.assertAlmostEqual(delta_x(gemischt, 'DEF-jaw', KIEFER_RUHE), 0.4, places=3)
        self.assertIn('DEF-lip.T.L', gemischt.tracks)

    def test_die_spur_liegt_auf_der_ruhelage_nicht_auf_der_einheitsdrehung(self):
        u"""Der Befund vom 12.09.2026: Ruhelage 89°, Spur 2° — das Gesicht
        sprang auf die Einheitslage. Neutral heißt jetzt: in Ruhe."""
        with Pruefablage.ordner() as ordner:
            bvh = ausdrucksdatei(ordner, kiefer=0.0)
            with open(Gesichtsspuren.datei(bvh)) as f:
                daten = json.load(f)
            daten['expression_frames'] = [[0.0] * 10] * 3
            with open(Gesichtsspuren.datei(bvh), 'w') as f:
                json.dump(daten, f)
            ausdruecke = Gesichtsspuren.laden(bvh)
        gemischt = self.mischen(gemisch(), ausdruecke)
        np.testing.assert_allclose(gemischt.tracks['DEF-jaw'][:4], KIEFER_RUHE, atol=1e-6)
        np.testing.assert_allclose(gemischt.tracks['DEF-chin'][:4], [0, 0, 0, 1], atol=1e-6)

    def test_reihenfolge_wie_im_javascript_ruhe_mal_delta(self):
        u"""`facial_expression.js`: `knochen.quaternion.copy(ruhe).multiply(drehung)`."""
        with Pruefablage.ordner() as ordner:
            ausdruecke = Gesichtsspuren.laden(ausdrucksdatei(ordner, kiefer=0.4))
        delta = np.asarray(ausdruecke.tracks['DEF-jaw'][:4], dtype=float)
        gemischt = self.mischen(gemisch(), ausdruecke)
        soll = Quat.mul(np.asarray(KIEFER_RUHE), delta)
        np.testing.assert_allclose(gemischt.tracks['DEF-jaw'][:4], soll, atol=1e-9)
        # die andere Reihenfolge wäre bei dieser Ruhelage eine andere Lage
        falsch = Quat.mul(delta, np.asarray(KIEFER_RUHE))
        self.assertGreater(np.abs(soll - falsch).max(), 1e-3)

    def test_koerper_und_finger_bleiben(self):
        with Pruefablage.ordner() as ordner:
            ausdruecke = Gesichtsspuren.laden(ausdrucksdatei(ordner))
        gemischt = self.mischen(gemisch(), ausdruecke)
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
        gemischt = self.mischen(gemisch(bilder=3), ausdruecke)
        self.assertEqual(len(gemischt.tracks['DEF-jaw']), 3 * 4)


class DasEchteSkelett(SimpleTestCase):
    u"""Gegen `def_skeleton.json`: der Kiefer ruht dort weit weg von der
    Einheitsdrehung (gemessen 89°) — genau deshalb fiel der Fehler auf."""

    databases = set()

    def test_die_ruhelage_des_kiefers_ist_keine_einheitsdrehung(self):
        from core.dienste.skelettgeometrie import Skelettgeometrie
        ruhe = Skelettgeometrie.holen().bones['DEF-jaw'].rest_local_quat
        grad = 2.0 * math.degrees(math.acos(min(1.0, abs(ruhe[3]))))
        self.assertGreater(grad, 45.0, 'sonst wäre der Fehler nie sichtbar gewesen')

    def test_ohne_geometrie_nimmt_mischen_das_def_skelett(self):
        from core.dienste.skelettgeometrie import Skelettgeometrie
        ruhe = Skelettgeometrie.holen().bones['DEF-jaw'].rest_local_quat
        with Pruefablage.ordner() as ordner:
            ausdruecke = Gesichtsspuren.laden(ausdrucksdatei(ordner, kiefer=0.4))
        gemischt = Gesichtsspuren.mischen(gemisch(), ausdruecke)
        self.assertAlmostEqual(delta_x(gemischt, 'DEF-jaw', ruhe), 0.4, places=3)
