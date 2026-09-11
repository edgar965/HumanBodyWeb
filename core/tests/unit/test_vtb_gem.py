# -*- coding: utf-8 -*-
u"""GEM-SMPL im VideoToBVH-Baum — der Teil ohne Grafikkarte (11.09.2026).

Der Lauf selbst braucht den 5,5-GB-Checkpoint und CUDA; was sich hier
pruefen laesst, ist alles davor und danach:

* **Der Befehl** an `demo_smpl_hpe.py`: fester Checkpoint-Pfad, `--static_cam`
  nur auf Wunsch, `--no_render` als Vorgabe (das Rendern braucht Open3D und
  beendet den Prozess mit `os._exit`).
* **Die Ergebnisumformung**: `smpl_params.pt` traegt `body_params_incam`,
  `Bvhbau` und `Bildpunkte` erwarten `smpl_params_incam`. Ein Schluessel
  daneben, und der Lauf bricht NACH zwei Minuten Rechnen ab.
* **Die Verteiler stimmen ueberein**: Was `Lifterwahl` fuer `gem` annimmt,
  muss `Smplbefehl` auch senden koennen — und `lift_3d.py` parsen.
* **`bvh`/`quat` liegen im Baum**: Bis zum 11.09.2026 zeigte `Gvhmrlauf` auf
  `3DObjects/smpl2bvh`, das seit dem 08.05. im Archiv lag; jeder GVHMR-Lauf
  brach beim BVH-Schreiben ab (Auftrag e1d2333f).
"""
import os
import re
import sys
import unittest

from ._wrappersuchpfad import Wrappersuchpfad, WRAPPERS

Wrappersuchpfad.setzen()

from gemlauf import Gemlauf                                 # noqa: E402
from gvhmrlauf import Gvhmrlauf                             # noqa: E402
from lifterwahl import Lifterwahl                           # noqa: E402


class DerGemBefehl(unittest.TestCase):

    def _lauf(self, **zusatz):
        return Gemlauf('tanz.mp4', os.path.join('aus', 'tanz.bvh'), **zusatz)

    def test_vorgabe_feste_kamera_ohne_rendern(self):
        befehl = self._lauf().befehl('aus')
        self.assertEqual(befehl[0], sys.executable)
        self.assertTrue(befehl[1].endswith('demo_smpl_hpe.py'))
        self.assertIn('--static_cam', befehl)
        self.assertIn('--no_render', befehl)
        self.assertEqual(befehl[befehl.index('--ckpt_path') + 1], Gemlauf.CHECKPOINT)
        self.assertEqual(befehl[befehl.index('--output_root') + 1], 'aus')

    def test_bewegte_kamera_und_rendern_auf_wunsch(self):
        befehl = self._lauf(static_cam=False, rendern=True).befehl('aus')
        self.assertNotIn('--static_cam', befehl)
        self.assertNotIn('--no_render', befehl)

    def test_ergebnis_liegt_unter_dem_videonamen(self):
        self.assertEqual(self._lauf().ergebnisdatei('aus'),
                         os.path.join('aus', 'tanz', 'smpl_params.pt'))


class DieErgebnisumformung(unittest.TestCase):
    u"""Ohne torch: der Leser wird hereingereicht."""

    def test_body_params_incam_wird_smpl_params_incam(self):
        daten = {'body_params_incam': {'transl': [[0, 0, 0]]},
                 'body_params_global': {'transl': [[1, 1, 1]]},
                 'K_fullimg': 'K'}
        v = Gemlauf.vorhersage_laden('smpl_params.pt', laden=lambda _pfad: daten)
        self.assertEqual(v, {'smpl_params_incam': daten['body_params_incam'],
                             'smpl_params_global': daten['body_params_global'],
                             'K_fullimg': 'K'})

    def test_ohne_incam_bricht_der_lauf_ab(self):
        with self.assertRaises(SystemExit):
            Gemlauf.vorhersage_laden('x.pt', laden=lambda _pfad: {'body_params_global': {}})


class DieVerteilerPassenZusammen(unittest.TestCase):

    def test_lifterwahl_kennt_gem_mit_den_schaltern_von_smplbefehl(self):
        from core.pipelines.smplbefehl import Smplbefehl
        modul, erlaubt = Lifterwahl.LIFTER['gem']
        self.assertEqual(modul, 'gem_lift')
        for schluessel, _feld, _argument in Smplbefehl.SCHALTER['gem']:
            self.assertIn(schluessel, erlaubt)
        for name in ('smooth_sigma', 'joint_limits'):
            self.assertIn(name, erlaubt, '%s kommt ueber _glaettung mit' % name)

    def test_lift_3d_parst_jeden_gesendeten_schalter(self):
        from core.pipelines.smplbefehl import Smplbefehl
        quelle = (WRAPPERS / 'lift_3d.py').read_text(encoding='utf-8')
        argumente = set(re.findall(r"add_argument\('(--[a-z_]+)'", quelle))
        argumente |= set(re.findall(r"'(--no_[a-z_]+)'", quelle))
        for _schluessel, _feld, argument in Smplbefehl.SCHALTER['gem']:
            self.assertIn(argument, argumente)
        for argument in ('--smooth_sigma', '--no_joint_limits'):
            self.assertIn(argument, argumente)

    def test_jede_smpl_pipeline_steht_in_allen_listen(self):
        """Sechs Listen nennen die Pipelines; fehlt eine, antwortet der Start
        mit 400 (`Invalid pipeline`) — so ging der erste GEM-Start (12.09.2026,
        00:06) an `PIPELINES_3D` vorbei, obwohl Karte und Lauf fertig waren."""
        from core.api.auftraege import PIPELINES_3D
        from core.dienste.auftragssteuerung import Auftragssteuerung
        from core.dienste.gelenkquelle import Gelenkquelle
        from core.pipelines.auftragslauf import Auftragslauf
        from core.pipelines.smplbefehl import Smplbefehl
        from core.models.auftrag import BVHJob
        for name in Auftragslauf.SMPL_PIPELINES:
            with self.subTest(pipeline=name):
                self.assertIn(name, dict(BVHJob.PIPELINE_CHOICES))
                self.assertIn(name, PIPELINES_3D)
                self.assertIn(name, Gelenkquelle.SMPL)
                self.assertIn(name, Smplbefehl.SCHALTER)
                self.assertIn(name, Lifterwahl.LIFTER)
                self.assertEqual(Auftragssteuerung._anfangszustand(name), 'processing')


class DieBvhHilfsmodule(unittest.TestCase):

    def test_bvh_und_quat_liegen_im_wrapperbaum(self):
        ordner = Gvhmrlauf.hilfsmodule_bereitstellen()
        self.assertEqual(os.path.normcase(ordner),
                         os.path.normcase(str(WRAPPERS / 'smpl2bvh')))
        self.assertIn(ordner, sys.path)
        import bvh
        import quat
        self.assertTrue(callable(bvh.save))
        self.assertTrue(callable(quat.from_angle_axis))
