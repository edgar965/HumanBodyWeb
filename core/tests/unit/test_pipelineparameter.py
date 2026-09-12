# -*- coding: utf-8 -*-
u"""GVHMR-Formular: die vier Schalter, die nie ankamen (12.09.2026).

`upload_v4.html` zeigte seit dem Formularbau DPVO, Verbose, Glättung und
Gelenkgrenzen für GVHMR; `Pipelineparameter._gvhmr` las nur Kamera,
Brennweite und Gerät. `Smplbefehl` kannte `use_dpvo` und die Glättung
längst — es fehlte das Stück dazwischen. Aufgefallen, als DPVO unter
Windows endlich lief und das Häkchen nichts tat.
"""
from types import SimpleNamespace

from django.test import SimpleTestCase, override_settings

from core.api.pipelineparameter import Pipelineparameter
from core.pipelines.smplbefehl import Smplbefehl


class Einstellungen(SimpleNamespace):
    u"""Nur, was `Smplbefehl` für GVHMR liest."""

    def __init__(self):
        super().__init__(smpl_device='cuda', gvhmr_static_cam=True,
                         gvhmr_focal_length_mm=0, gvhmr_smooth_sigma=2.0,
                         gvhmr_joint_limits=True, gvhmr_use_dpvo=False,
                         gvhmr_verbose=False, gvhmr_render=True)


class GvhmrFormularTest(SimpleTestCase):

    databases = set()

    def test_die_vier_schalter_kommen_im_auftrag_an(self):
        p = Pipelineparameter.lesen(
            {'gvhmr_use_dpvo': 'on', 'gvhmr_verbose': 'on',
             'gvhmr_smooth_sigma': '1.5'}, 'gvhmr')
        self.assertTrue(p['use_dpvo'])
        self.assertTrue(p['verbose'])
        self.assertEqual(p['smooth_sigma'], 1.5)
        # Kein `on` vom Kästchen heisst: Gelenkgrenzen aus.
        self.assertFalse(p['joint_limits'])

    def test_ohne_haekchen_bleibt_dpvo_aus(self):
        p = Pipelineparameter.lesen({}, 'gvhmr')
        self.assertFalse(p['use_dpvo'])
        self.assertFalse(p['verbose'])
        self.assertEqual(p['smooth_sigma'], 2.0)

    def test_duomo_liest_seine_vier_felder(self):
        p = Pipelineparameter.lesen(
            {'duomo_static_cam': 'on', 'duomo_smooth_sigma': '3',
             'duomo_joint_limits': 'on', 'duomo_device': 'cpu'}, 'duomo')
        self.assertEqual(p, {'static_cam': True, 'smooth_sigma': 3.0,
                             'joint_limits': True, 'device': 'cpu'})
        self.assertFalse(Pipelineparameter.lesen({}, 'duomo')['static_cam'])

    def test_gemx_liest_seine_drei_felder(self):
        p = Pipelineparameter.lesen(
            {'gemx_static_cam': 'on', 'gemx_smooth_sigma': '1'}, 'gemx')
        self.assertEqual(p, {'static_cam': True, 'smooth_sigma': 1.0, 'device': 'cuda'})

    def test_der_befehl_traegt_die_schalter_weiter(self):
        p = Pipelineparameter.lesen(
            {'gvhmr_use_dpvo': 'on', 'gvhmr_smooth_sigma': '1.5',
             'gvhmr_joint_limits': 'on'}, 'gvhmr')
        job = SimpleNamespace(pipeline='gvhmr', pipeline_params=p)
        with override_settings(PIPELINE_PYTHON='py.exe'):
            teile = Smplbefehl(job, Einstellungen()).bauen('w.py', 'v.mp4', 'z.bvh')
        self.assertIn('--use_dpvo', teile)
        self.assertNotIn('--verbose', teile)
        self.assertNotIn('--no_joint_limits', teile)
        self.assertEqual(teile[teile.index('--smooth_sigma') + 1], '1.5')
