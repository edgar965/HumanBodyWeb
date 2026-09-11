# -*- coding: utf-8 -*-
u"""DuoMo im VideoToBVH-Baum — der Teil ohne Grafikkarte (12.09.2026).

Der Lauf selbst braucht 2,6 GB Checkpoints, die PromptHMR-Bildmerkmale
und CUDA; was sich hier pruefen laesst, ist alles davor und danach:

* **Der Befehl** an DuoMos `scripts/inference.py`: eigener Interpreter
  (`python10duomo`), relativer Skriptpfad (Arbeitsverzeichnis ist DuoMos
  Wurzel, dort liegt `configs/inference.yaml`), `--camera_param` nur mit
  Kamerabahn UND bewegter Kamera.
* **Die Ablagen**: DuoMo schreibt nach `results/<videoname>/motion.pt`
  unter seiner Wurzel; die SMPL-X-Parameter landen beim Auftrag.
* **Die Gewichtsliste** nennt, was fehlt — der erste Lauf scheiterte an
  `phmr/checkpoint.ckpt` (Google-Drive-Quota), und ohne Liste stand nur
  ein Traceback aus der Tiefe von DuoMo da.
* **Die Verteiler stimmen ueberein**: Was `Lifterwahl` fuer `duomo`
  annimmt, muss `Smplbefehl` senden koennen — und `lift_3d.py` parsen.
"""
import os
import re
import unittest
from unittest.mock import patch

from ._wrappersuchpfad import Wrappersuchpfad, WRAPPERS

Wrappersuchpfad.setzen()

from duomolauf import Duomolauf                             # noqa: E402
from lifterwahl import Lifterwahl                           # noqa: E402


class DerDuomoBefehl(unittest.TestCase):

    def _lauf(self, **zusatz):
        return Duomolauf('tanz.mp4', os.path.join('aus', 'tanz.bvh'), **zusatz)

    def test_eigener_interpreter_und_relatives_skript(self):
        befehl = self._lauf().befehl()
        self.assertTrue(befehl[0].lower().endswith(
            os.path.join('python10duomo', 'scripts', 'python.exe')))
        self.assertEqual(befehl[1], os.path.join('scripts', 'inference.py'))
        self.assertEqual(befehl[2:4], ['--video_path', 'tanz.mp4'])
        self.assertNotIn('--camera_param', befehl)

    def test_kamerabahn_nur_bei_bewegter_kamera(self):
        mit = self._lauf(static_cam=False, kamera_pt='kamera.pt').befehl()
        self.assertEqual(mit[-2:], ['--camera_param', 'kamera.pt'])
        # Feste Kamera angekreuzt: die Bahn bleibt liegen.
        fest = self._lauf(static_cam=True, kamera_pt='kamera.pt').befehl()
        self.assertNotIn('--camera_param', fest)

    def test_ergebnis_liegt_unter_duomos_wurzel(self):
        ergebnis = self._lauf().ergebnisdatei()
        self.assertEqual(os.path.normcase(ergebnis), os.path.normcase(
            os.path.join(Duomolauf.WURZEL, 'results', 'tanz', 'motion.pt')))
        parameter = self._lauf().parameterdatei('aus')
        self.assertEqual(parameter, os.path.join('aus', 'tanz', 'smplx_params.pt'))

    def test_fehlende_gewichte_werden_genannt(self):
        lauf = self._lauf()
        with patch.object(Duomolauf, 'WURZEL', os.path.join('aus', 'nirgends')):
            fehlt = lauf.fehlende_gewichte()
        self.assertEqual(len(fehlt), len(Duomolauf.GEWICHTE))
        self.assertTrue(any('phmr' in p for p in fehlt))
        with patch.object(Duomolauf, 'WURZEL', os.path.join('aus', 'nirgends')):
            with self.assertRaises(SystemExit):
                lauf.gewichte_pruefen()

    def test_lifterwahl_kennt_duomo_mit_den_schaltern_von_smplbefehl(self):
        from core.pipelines.smplbefehl import Smplbefehl
        modul, erlaubt = Lifterwahl.LIFTER['duomo']
        self.assertEqual(modul, 'duomo_lift')
        for schluessel, _feld, _argument in Smplbefehl.SCHALTER['duomo']:
            self.assertIn(schluessel, erlaubt)
        for name in ('smooth_sigma', 'joint_limits'):
            self.assertIn(name, erlaubt, '%s kommt ueber _glaettung mit' % name)
        self.assertIn('duomo', Smplbefehl.MIT_GLAETTUNG)

    def test_lift_3d_parst_jeden_gesendeten_schalter(self):
        from core.pipelines.smplbefehl import Smplbefehl
        quelle = (WRAPPERS / 'lift_3d.py').read_text(encoding='utf-8')
        argumente = set(re.findall(r"add_argument\('(--[a-z_]+)'", quelle))
        argumente |= set(re.findall(r"'(--no_[a-z_]+)'", quelle))
        for _schluessel, _feld, argument in Smplbefehl.SCHALTER['duomo']:
            self.assertIn(argument, argumente)

    def test_umrechner_liegt_neben_dem_lauf(self):
        self.assertTrue(os.path.isfile(Duomolauf.UMRECHNER))
        self.assertEqual(os.path.basename(Duomolauf.UMRECHNER), 'duomo_smplx.py')
