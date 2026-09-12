# -*- coding: utf-8 -*-
u"""GEM-X im VideoToBVH-Baum — der Teil ohne Grafikkarte (12.09.2026).

* **Der Befehl** an `gemx_vorhersage.py` (die Kommandozeile von
  `demo_soma.py`), mit GEM-X VORN im `PYTHONPATH`: `gem` ist in python10
  GEM-SMPL, im Unterprozess muss es GEM-X sein.
* **Das BVH** (`Somabvh`): Mixamo-Namen, die HumanBodys Retarget als
  MIXAMO erkennt und deren Finger es auf die DEF-Knochen legt; die
  Vorwaertskinematik der Gegenprobe; die Hochachse auf +y.
* **Die Verteiler stimmen ueberein** wie bei GEM und DuoMo.
"""
import os
import re
import shutil
import unittest

import numpy as np
from django.conf import settings

from ._humanbodypfad import Humanbodypfad
from ._wrappersuchpfad import Wrappersuchpfad, WRAPPERS

Wrappersuchpfad.setzen()
Humanbodypfad.setzen()

from gemxlauf import Gemxlauf                               # noqa: E402
from gvhmrlauf import Gvhmrlauf                             # noqa: E402
from lifterwahl import Lifterwahl                           # noqa: E402
from somabvh import Somabvh                                 # noqa: E402

#: SOMAs 77 Gelenke (ohne Root), wie `SOMA_neutral.npz` sie nennt.
SOMA_NAMEN = (
    'Hips', 'Spine1', 'Spine2', 'Chest', 'Neck1', 'Neck2', 'Head', 'HeadEnd',
    'Jaw', 'LeftEye', 'RightEye', 'LeftShoulder', 'LeftArm', 'LeftForeArm',
    'LeftHand', 'LeftHandThumb1', 'LeftHandThumb2', 'LeftHandThumb3',
    'LeftHandThumbEnd', 'LeftHandIndex1', 'LeftHandIndex2', 'LeftHandIndex3',
    'LeftHandIndex4', 'LeftHandIndexEnd', 'LeftHandMiddle1', 'LeftHandMiddle2',
    'LeftHandMiddle3', 'LeftHandMiddle4', 'LeftHandMiddleEnd', 'LeftHandRing1',
    'LeftHandRing2', 'LeftHandRing3', 'LeftHandRing4', 'LeftHandRingEnd',
    'LeftHandPinky1', 'LeftHandPinky2', 'LeftHandPinky3', 'LeftHandPinky4',
    'LeftHandPinkyEnd', 'RightShoulder', 'RightArm', 'RightForeArm', 'RightHand',
    'RightHandThumb1', 'RightHandThumb2', 'RightHandThumb3', 'RightHandThumbEnd',
    'RightHandIndex1', 'RightHandIndex2', 'RightHandIndex3', 'RightHandIndex4',
    'RightHandIndexEnd', 'RightHandMiddle1', 'RightHandMiddle2', 'RightHandMiddle3',
    'RightHandMiddle4', 'RightHandMiddleEnd', 'RightHandRing1', 'RightHandRing2',
    'RightHandRing3', 'RightHandRing4', 'RightHandRingEnd', 'RightHandPinky1',
    'RightHandPinky2', 'RightHandPinky3', 'RightHandPinky4', 'RightHandPinkyEnd',
    'LeftLeg', 'LeftShin', 'LeftFoot', 'LeftToeBase', 'LeftToeEnd', 'RightLeg',
    'RightShin', 'RightFoot', 'RightToeBase', 'RightToeEnd')


class DerGemxBefehl(unittest.TestCase):

    def _lauf(self, **zusatz):
        return Gemxlauf('tanz.mp4', os.path.join('aus', 'tanz.bvh'), **zusatz)

    def test_befehl_wie_das_demo(self):
        befehl = self._lauf().befehl('aus')
        self.assertTrue(befehl[1].endswith('gemx_vorhersage.py'))
        self.assertEqual(befehl[2:8], ['--video', 'tanz.mp4', '--output_root', 'aus',
                                       '--ckpt', Gemxlauf.CHECKPOINT])
        self.assertIn('--static_cam', befehl)
        self.assertNotIn('--static_cam', self._lauf(static_cam=False).befehl('aus'))

    def test_gemx_steht_vorn_im_suchpfad(self):
        u = self._lauf().umgebung()
        self.assertEqual(u['PYTHONPATH'].split(os.pathsep)[0], Gemxlauf.WURZEL)
        self.assertTrue(u['HF_HOME'].lower().endswith('hf_home'))
        self.assertIn('TORCH_HOME', u)

    def test_ergebnisse_liegen_unter_dem_videonamen(self):
        lauf = self._lauf()
        self.assertEqual(lauf.ergebnisdatei('aus'), os.path.join('aus', 'tanz', 'hpe_results.pt'))
        self.assertEqual(lauf.parameterdatei('aus'), os.path.join('aus', 'tanz', 'soma_params.npz'))

    def test_lifterwahl_kennt_gemx_mit_den_schaltern_von_smplbefehl(self):
        from core.pipelines.smplbefehl import Smplbefehl
        modul, erlaubt = Lifterwahl.LIFTER['gemx']
        self.assertEqual(modul, 'gemx_lift')
        for schluessel, _feld, _argument in Smplbefehl.SCHALTER['gemx']:
            self.assertIn(schluessel, erlaubt)
        self.assertIn('smooth_sigma', erlaubt)
        self.assertIn('gemx', Smplbefehl.MIT_GLAETTUNG)

    def test_lift_3d_parst_jeden_gesendeten_schalter(self):
        from core.pipelines.smplbefehl import Smplbefehl
        quelle = (WRAPPERS / 'lift_3d.py').read_text(encoding='utf-8')
        argumente = set(re.findall(r"add_argument\('(--[a-z_]+)'", quelle))
        for _schluessel, _feld, argument in Smplbefehl.SCHALTER['gemx']:
            self.assertIn(argument, argumente)


class DasSomaBvh(unittest.TestCase):
    u"""Vier Gelenke reichen: Hips -> Spine1 -> Head, Hips -> LeftLeg."""

    NAMEN = ('Hips', 'Spine1', 'Head', 'LeftLeg')
    ELTERN = (-1, 0, 1, 0)

    def setUp(self):
        self.ordner = os.path.join(settings.BASE_DIR, '_wegwerf', 'test_vtb_gemx')
        shutil.rmtree(self.ordner, ignore_errors=True)
        os.makedirs(self.ordner)
        Gvhmrlauf.hilfsmodule_bereitstellen()

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)

    def _params(self, tpose, bilder=3):
        # Dictionary gewollt: dieselben Schluessel wie SOMAs `smpl_params.pt`.
        return {
            'names': np.asarray(self.NAMEN), 'parents': np.asarray(self.ELTERN),
            'tpose': np.asarray(tpose, dtype=np.float32),
            'global_orient': np.zeros((bilder, 3), np.float32),
            'body_pose': np.zeros((bilder, 3, 3), np.float32),
            'transl': np.tile(np.asarray(tpose[0], np.float32), (bilder, 1)),
        }

    def test_mixamo_namen_werden_als_mixamo_erkannt_mit_fingern(self):
        from humanbody_core.skeleton.formats.mixamo import SkeletonMixamo
        namen = Somabvh.mixamo_namen(SOMA_NAMEN)
        self.assertEqual(len(namen), 77)
        self.assertTrue(SkeletonMixamo.detect(namen))
        karte = SkeletonMixamo.BONE_MAP_TO_RIGIFY
        for name, knochen in (('LeftHandIndex1', 'DEF-f_index.01.L'),
                              ('RightHandThumb3', 'DEF-thumb.03.R'),
                              ('LeftUpLeg', 'DEF-thigh.L'), ('Spine2', 'DEF-spine.003')):
            self.assertIn(name, namen)
            self.assertEqual(karte[name], knochen)

    def test_vorwaertskinematik_trifft_die_tpose_ohne_drehung(self):
        tpose = np.array([[0, 1.0, 0], [0, 1.3, 0], [0, 1.6, 0], [0.1, 0.9, 0]])
        offsets = Somabvh.offsets(tpose * 100, self.ELTERN, np)
        pos = Somabvh.positionen(np.zeros((2, 4, 3)), offsets, self.ELTERN,
                                 np.tile(tpose[0] * 100, (2, 1)), np)
        np.testing.assert_allclose(pos[1], tpose * 100, atol=1e-6)

    def test_eine_drehung_der_wurzel_dreht_alles(self):
        tpose = np.array([[0, 1.0, 0], [0, 1.3, 0], [0, 1.6, 0], [0.1, 0.9, 0]])
        offsets = Somabvh.offsets(tpose * 100, self.ELTERN, np)
        rot = np.zeros((1, 4, 3))
        rot[0, 0] = [0, 0, np.pi / 2]      # 90 Grad um z: +y wird -x
        pos = Somabvh.positionen(rot, offsets, self.ELTERN, tpose[:1] * 100, np)
        np.testing.assert_allclose(pos[0, 2], [-60, 100, 0], atol=1e-6)

    def test_bvh_mit_umbenannten_gelenken_und_hochachse_y(self):
        tpose = [[0, 1.0, 0], [0, 1.3, 0], [0, 1.6, 0], [0.1, 0.9, 0]]
        ziel = os.path.join(self.ordner, 'probe.bvh')
        Somabvh(bilder=25.0, sigma=0).bauen(self._params(tpose), ziel)
        text = open(ziel, encoding='utf-8').read()
        self.assertIn('ROOT Hips', text)
        self.assertIn('JOINT Spine\n', text)          # Spine1 -> Spine
        self.assertIn('JOINT LeftUpLeg', text)
        self.assertNotIn('Spine1', text)
        self.assertIn('Frames: 3', text)
        self.assertIn('End Site', text)

    def test_kameraraum_wird_wie_bei_bvhbau_nach_y_oben_gedreht(self):
        # GEM-X liefert im Kameraraum (y unten, z nach vorn): eine stehende
        # Person traegt dort global_orient = pi um x, die Huefte liegt bei
        # y < 0. Nach der Drehung steht sie aufrecht bei y > 0, wie bei
        # GVHMR/DuoMo ueber `Bvhbau` (Vergleich 12.09.2026: 180 Grad verdreht).
        import bvh as bvh_util
        import quat
        tpose = [[0, 1.0, 0], [0, 1.3, 0], [0, 1.6, 0], [0.1, 0.9, 0]]
        params = self._params(tpose)
        params['raum'] = np.asarray('incam')
        params['global_orient'][:] = [np.pi, 0, 0]
        params['transl'][:] = [0.2, -1.0, 5.0]
        ziel = os.path.join(self.ordner, 'probe_incam.bvh')
        Somabvh(bilder=25.0, sigma=0).bauen(params, ziel)
        daten = bvh_util.load(ziel)
        rot = quat.from_euler(np.radians(daten['rotations']), order=daten['order'])
        _, pos = quat.fk(rot, daten['positions'], daten['parents'])
        np.testing.assert_allclose(pos[0, 0], [20, 100, -500], atol=1e-3)   # Huefte
        np.testing.assert_allclose(pos[0, 2], [20, 160, -500], atol=1e-3)   # Kopf oben

    def test_hochachse_z_wird_auf_y_gedreht(self):
        tpose = [[0, 0, 1.0], [0, 0, 1.3], [0, 0, 1.6], [0.1, 0, 0.9]]   # Kopf in +z
        ziel = os.path.join(self.ordner, 'probe_z.bvh')
        Somabvh(bilder=25.0, sigma=0).bauen(self._params(tpose), ziel)
        text = open(ziel, encoding='utf-8').read()
        # Der Kopf-Offset (30 cm) liegt nach der Drehung auf +y.
        self.assertRegex(text, r'JOINT Head\s*\{\s*OFFSET 0\.0+ 30\.0+ ')
