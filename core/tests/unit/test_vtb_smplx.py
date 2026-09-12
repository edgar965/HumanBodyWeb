# -*- coding: utf-8 -*-
u"""Die eigene SMPL-X-Pipeline im VideoToBVH-Baum — der Teil ohne Grafikkarte (12.09.2026).

Der Lauf braucht GEM (5,5 GB) und SMPLest-X; pruefbar ist alles davor und
danach: das kanonische Format (`Smplxbahn`), die Mischung (`Smplxmischung`
mit Luecken, Handmittel, Gegenprobe), das Skelett des BVH (`Smplxbvh`,
54 Gelenke, Finger am Handgelenk), das Retarget-Format (`SkeletonSMPLX`
gegen AIST) und die Verteiler (`Lifterwahl`, `Smplbefehl`, `lift_3d.py`).

Sabotagen, die diese Faelle rot machen (gemacht): Handmittel nicht addiert
-> `test_handmittel`; AIST-Erkennung ohne den Fingerausschluss ->
`test_bvh_mit_fingern_ist_smplx_nicht_aist`; Fingereltern auf das falsche
Handgelenk -> `test_finger_haengen_am_handgelenk`.
"""
import os
import re
import unittest

import numpy as np

from ._wrappersuchpfad import Wrappersuchpfad, WRAPPERS
from ._pruefablage import Pruefablage

Wrappersuchpfad.setzen()

from lifterwahl import Lifterwahl                            # noqa: E402
from smplxbahn import Smplxbahn                              # noqa: E402
from smplxbvh import Smplxbvh                                # noqa: E402
from smplxmischung import Smplxmischung                      # noqa: E402
from smplxreihe import Smplxreihe                            # noqa: E402
from SMPL.finger import Smplxfinger                          # noqa: E402


class DasKanonischeFormat(unittest.TestCase):

    N = 12

    def _smpl(self):
        rng = np.random.default_rng(3)
        return {'body_pose': rng.normal(0, 0.1, (self.N, 69)).astype(np.float32),
                'global_orient': np.zeros((self.N, 3), np.float32),
                'transl': np.tile([0.0, 0.3, 3.0], (self.N, 1)).astype(np.float32),
                'betas': np.zeros((self.N, 10), np.float32)}

    def test_aus_smpl_nimmt_21_koerpergelenke_und_laesst_die_handflaechen(self):
        smpl = self._smpl()
        bahn = Smplxbahn.aus_smpl(smpl, 30.0, np)
        self.assertEqual(bahn.body_pose.shape, (self.N, 21, 3))
        np.testing.assert_allclose(bahn.body_pose.reshape(self.N, 63),
                                   smpl['body_pose'][:, :63])
        self.assertEqual(bahn.anzahl, self.N)
        self.assertFalse(bahn.haende_gueltig.any())

    def test_speichern_und_laden_sind_verlustfrei(self):
        bahn = Smplxbahn.aus_smpl(self._smpl(), 60.0, np)
        bahn.left_hand_pose[:] = 0.25
        bahn.K = np.eye(3)
        with Pruefablage.ordner('smplx_bahn') as ordner:
            pfad = os.path.join(ordner, 'probe' + Smplxbahn.ENDUNG)
            zurueck = Smplxbahn.laden(bahn.speichern(pfad), np)
        self.assertEqual(zurueck.fps, 60.0)
        np.testing.assert_allclose(zurueck.left_hand_pose, bahn.left_hand_pose)
        np.testing.assert_allclose(zurueck.body_pose, bahn.body_pose)
        self.assertIsNotNone(zurueck.K)


class DieMischung(unittest.TestCase):

    N = 20

    def _reihe(self, luecke=range(5, 9), mittel=0.1):
        reihe = Smplxreihe(30.0, np)
        reihe.handmittel(np.full(45, mittel), np.full(45, -mittel))
        for i in range(self.N):
            if i in luecke:
                reihe.leer()
                continue
            reihe.dazu({'smplx_root_pose': np.zeros(3), 'smplx_body_pose': np.zeros(63),
                        'smplx_lhand_pose': np.full(45, 0.5), 'smplx_rhand_pose': np.full(45, -0.5),
                        'smplx_jaw_pose': np.array([0.2, 0.0, 0.0]),
                        'smplx_expr': np.arange(10) / 10.0, 'smplx_shape': np.zeros(10),
                        'cam_trans': np.zeros(3)}, (1, 2, 3, 4), [(1.0, 2.0)] * 72)
        return reihe.als_felder()

    def _bahn(self):
        return Smplxbahn(self.N, 30.0, np)

    def test_handmittel_wird_addiert(self):
        u"""SMPLest-X liefert relativ zur gekruemmten Mittelhand; gegen die
        gestreckte Hand des BVH fehlt sonst die Kruemmung in jedem Bild."""
        bahn = self._bahn()
        Smplxmischung(bahn, self._reihe(luecke=()), np).mischen(0.0, 0.0)
        self.assertAlmostEqual(float(bahn.left_hand_pose[0, 0, 0]), 0.6, places=5)
        self.assertAlmostEqual(float(bahn.right_hand_pose[0, 0, 0]), -0.6, places=5)

    def test_luecken_bekommen_den_letzten_gueltigen_wert_und_bleiben_markiert(self):
        bahn = self._bahn()
        mischung = Smplxmischung(bahn, self._reihe(), np)
        mischung.mischen(0.0, 0.0)
        self.assertFalse(bahn.haende_gueltig[6])
        self.assertTrue(bahn.haende_gueltig[4])
        np.testing.assert_allclose(bahn.left_hand_pose[6], bahn.left_hand_pose[4])
        self.assertAlmostEqual(float(bahn.expression[6, 5]), 0.5, places=5)
        self.assertEqual(mischung.bilanz['haende_bilder'], self.N - 4)

    def test_ohne_eine_einzige_erkennung_bleibt_alles_null(self):
        bahn = self._bahn()
        Smplxmischung(bahn, self._reihe(luecke=range(self.N)), np).mischen(2.0, 2.0)
        self.assertFalse(bahn.left_hand_pose.any())
        self.assertFalse(bahn.haende_gueltig.any())

    def test_gegenprobe_misst_den_winkel_zwischen_den_koerpern(self):
        bahn = self._bahn()
        felder = self._reihe(luecke=())
        mischung = Smplxmischung(bahn, felder, np)
        mischung.gegenprobe()
        self.assertEqual(mischung.bilanz['koerper_abweichung_grad'], 0.0)
        bahn.body_pose[:, 3, 0] = np.pi / 2          # ein Gelenk um 90 Grad
        mischung.gegenprobe()
        self.assertAlmostEqual(mischung.bilanz['koerper_abweichung_grad'], 90.0 / 21, places=1)

    def test_glaettung_nimmt_das_zittern_aus_den_fingern(self):
        bahn = self._bahn()
        felder = self._reihe(luecke=(), mittel=0.0)
        felder['lhand_pose'][::2] = 0.5 + 0.2         # jedes zweite Bild anders
        roh = felder['lhand_pose'][:, 0].copy()
        Smplxmischung(bahn, felder, np).mischen(2.0, 0.0)
        geglaettet = bahn.left_hand_pose[:, 0, 0]
        self.assertLess(np.abs(np.diff(geglaettet)).mean(), np.abs(np.diff(roh)).mean() / 3)


class DasSkelettDesBvh(unittest.TestCase):

    def test_54_gelenke_koerper_dann_finger(self):
        namen = Smplxbvh.namen()
        self.assertEqual(len(namen), 54)
        self.assertEqual(namen[:24][0], 'Pelvis')
        self.assertEqual(namen[24], 'left_index1')
        self.assertEqual(namen[-1], 'right_thumb3')
        self.assertEqual(Smplxbvh.offsets(np).shape, (54, 3))
        self.assertEqual(len(Smplxfinger.OFFSETS), 30)

    def test_finger_haengen_am_handgelenk(self):
        eltern = Smplxbvh.eltern(np)
        namen = Smplxbvh.namen()
        links, rechts = namen.index('Left_wrist'), namen.index('Right_wrist')
        for finger in ('index', 'middle', 'pinky', 'ring', 'thumb'):
            self.assertEqual(eltern[namen.index('left_%s1' % finger)], links)
            self.assertEqual(eltern[namen.index('right_%s1' % finger)], rechts)
            self.assertEqual(eltern[namen.index('left_%s2' % finger)],
                             namen.index('left_%s1' % finger))
        # Fingerwurzeln links zeigen nach +x, rechts nach -x (wie die Arme)
        offsets = Smplxbvh.offsets(np)
        self.assertGreater(offsets[namen.index('left_index1')][0], 0)
        self.assertLess(offsets[namen.index('right_index1')][0], 0)

    def test_drehungen_setzen_haende_an_die_richtige_stelle(self):
        bahn = Smplxbahn(3, 30.0, np)
        bahn.left_hand_pose[:, 2, 1] = 0.7
        feld = Smplxbvh.drehungen(bahn, np)
        self.assertEqual(feld.shape, (3, 54, 3))
        self.assertAlmostEqual(float(feld[0, 24 + 2, 1]), 0.7, places=6)
        self.assertFalse(feld[:, 22:24].any(), 'die Handflaechen bleiben ungedreht')


class DasRetargetFormat(unittest.TestCase):

    def test_bvh_mit_fingern_ist_smplx_nicht_aist(self):
        from humanbody_core.skeleton import Skeleton
        mit = Skeleton.detect_format(Smplxbvh.namen())
        ohne = Skeleton.detect_format(Smplxbvh.namen()[:24])
        self.assertEqual(mit.FORMAT, 'SMPLX')
        self.assertEqual(ohne.FORMAT, 'AIST')

    def test_jeder_finger_und_jeder_koerperknochen_ist_zugeordnet(self):
        from humanbody_core.skeleton.formats import SkeletonSMPLX, SkeletonAIST_SMPL
        tabelle = SkeletonSMPLX.BONE_MAP_TO_RIGIFY
        for name in Smplxfinger.NAMEN:
            self.assertIn(name, tabelle)
            self.assertTrue(tabelle[name].startswith('DEF-'), name)
        for name, ziel in SkeletonAIST_SMPL.BONE_MAP_TO_RIGIFY.items():
            self.assertEqual(tabelle[name], ziel)
        self.assertEqual(tabelle['left_thumb1'], 'DEF-thumb.01.L')
        self.assertEqual(tabelle['right_pinky3'], 'DEF-f_pinky.03.R')


class DieVerteilerPassenZusammen(unittest.TestCase):

    def test_lifterwahl_kennt_smplx_mit_den_schaltern_von_smplbefehl(self):
        from core.pipelines.smplbefehl import Smplbefehl
        modul, erlaubt = Lifterwahl.LIFTER['smplx']
        self.assertEqual(modul, 'smplx_lift')
        for schluessel, _feld, _argument in Smplbefehl.SCHALTER['smplx']:
            self.assertIn(schluessel, erlaubt)
        for name in ('smooth_sigma', 'joint_limits', 'hand_sigma', 'face_sigma'):
            self.assertIn(name, erlaubt)

    def test_lift_3d_parst_die_beiden_neuen_schalter(self):
        quelle = (WRAPPERS / 'lift_3d.py').read_text(encoding='utf-8')
        argumente = set(re.findall(r"add_argument\('(--[a-z_]+)'", quelle))
        self.assertIn('--hand_sigma', argumente)
        self.assertIn('--face_sigma', argumente)
        self.assertIn('hand_sigma=a.hand_sigma', quelle)

    def test_die_karte_und_die_hilfe_kennen_die_pipeline(self):
        from core.dienste.pipelinekarten import Pipelinekarten
        from core.dienste.pipelinevergleich import Pipelinevergleich
        self.assertIn('smplx', Pipelinekarten.dreid())
        self.assertIn('_pipeline_smplx.html', Pipelinekarten.vorlagen())
        self.assertIn('smplx', Pipelinevergleich.schluessel())
