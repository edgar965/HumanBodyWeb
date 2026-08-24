# -*- coding: utf-8 -*-
"""Smplbefehl — welche Schalter bei welcher Pipeline mitgehen.

WARUM (17.08.2026)
=================
`_run_smpl_pipeline` war 95 Zeilen, davon die Hälfte Befehlsaufbau für drei
Pipelines — ungedeckt, weil der Lauf eine Grafikkarte braucht. Die Falle ist die
Vorrang-Regel: Der Auftrag schlägt die Einstellung. Wer im Formular „feste
Kamera: nein" wählt, während in den Einstellungen „ja" steht, muss `--static_cam`
NICHT bekommen. Ein `or` an dieser Stelle (statt `get` mit Vorgabe) würde die
Abwahl verschlucken — und die Pipeline rechnet etwas anderes, als auf dem
Bildschirm stand.

Dazu der eine umgekehrte Schalter: Gelenkgrenzen sind AN; `--no_joint_limits`
erscheint nur, wenn sie ausdrücklich abgewählt sind.
"""

from django.test import SimpleTestCase, override_settings

from core.pipelines.smplbefehl import Smplbefehl
from core.tests.attrappen import AuftragsAttrappe


class EinstellungenAttrappe:
    smpl_device = 'cuda'
    gvhmr_static_cam = True
    gvhmr_focal_length_mm = 35.0
    wham_estimate_local_only = True
    wham_run_smplify = False
    prompthmr_static_camera = True


class SmplbefehlTest(SimpleTestCase):

    def befehl(self, pipeline, **params):
        auftrag = AuftragsAttrappe(pipeline, params)
        with override_settings(PIPELINE_PYTHON='py.exe'):
            return Smplbefehl(auftrag, EinstellungenAttrappe()).bauen(
                'lift_3d.py', 'tanz.mp4', 'out.bvh')

    # ------------------------------------------------------------- Grundgerüst

    def test_grundargumente_stehen_immer(self):
        befehl = self.befehl('gvhmr')
        for erwartet in ('--pipeline', 'gvhmr', '--video', 'tanz.mp4',
                         '--output', 'out.bvh', '--device', 'cuda'):
            self.assertIn(erwartet, befehl)

    def test_geraet_kommt_aus_dem_auftrag(self):
        self.assertIn('cpu', self.befehl('gvhmr', device='cpu'))

    # --------------------------------------------------------------- Vorrang

    def test_einstellung_gilt_ohne_auftragswert(self):
        self.assertIn('--static_cam', self.befehl('gvhmr'))

    def test_auftrag_schlaegt_die_einstellung(self):
        """Der Fall, der ohne Test durchfällt: ausdrücklich ABGEWÄHLT."""
        self.assertNotIn('--static_cam', self.befehl('gvhmr', static_cam=False))

    def test_schalter_ohne_einstellung_sind_aus(self):
        befehl = self.befehl('gvhmr')
        self.assertNotIn('--use_dpvo', befehl)
        self.assertNotIn('--verbose', befehl)
        self.assertIn('--use_dpvo', self.befehl('gvhmr', use_dpvo=True))

    # ---------------------------------------------------------- Je Pipeline

    def test_gvhmr_werte(self):
        befehl = self.befehl('gvhmr', focal_length_mm=50.0, smooth_sigma=1.5)
        self.assertEqual(befehl[befehl.index('--focal_length_mm') + 1], '50.0')
        self.assertEqual(befehl[befehl.index('--smooth_sigma') + 1], '1.5')

    def test_gelenkgrenzen_sind_umgekehrt(self):
        self.assertNotIn('--no_joint_limits', self.befehl('gvhmr'))
        self.assertIn('--no_joint_limits',
                      self.befehl('gvhmr', joint_limits=False))

    def test_wham_hat_eigene_schalter(self):
        befehl = self.befehl('wham')
        self.assertIn('--estimate_local_only', befehl)
        self.assertNotIn('--run_smplify', befehl)
        self.assertNotIn('--static_cam', befehl, 'gvhmr-Schalter gehören nicht dazu')

    def test_prompthmr_hat_eigenen_kameraschalter(self):
        befehl = self.befehl('prompthmr')
        self.assertIn('--static_camera', befehl)
        self.assertNotIn('--static_cam', befehl)

    def test_unbekannte_pipeline_bekommt_nur_das_grundgeruest(self):
        befehl = self.befehl('smplest_x')
        self.assertEqual([a for a in befehl if a.startswith('--')],
                         ['--pipeline', '--video', '--output', '--device'])
