# -*- coding: utf-8 -*-
u"""Slamstatus: Dateiprüfung statt Import (12.09.2026)."""
import os
import shutil
from unittest.mock import MagicMock

from django.conf import settings
from django.test import SimpleTestCase

from core.pipelines.slamstatus import Slamstatus


class SlamstatusTest(SimpleTestCase):

    databases = []

    def setUp(self):
        self.ordner = os.path.join(settings.BASE_DIR, '_wegwerf', 'test_slamstatus')
        shutil.rmtree(self.ordner, ignore_errors=True)
        self.sp = os.path.join(self.ordner, 'venv', 'Lib', 'site-packages')
        self.python = os.path.join(self.ordner, 'venv', 'Scripts', 'python.exe')
        self.gvhmr = os.path.join(self.ordner, 'GVHMR')
        self.prompthmr = os.path.join(self.ordner, 'PromptHMR')
        for modul in Slamstatus.MODULE:
            self._datei(self.sp, modul + '.cp310-win_amd64.pyd')
        for paket, datei in Slamstatus.PAKETE:
            self._datei(os.path.join(self.sp, paket), datei)
        self._datei(os.path.join(self.gvhmr, 'inputs', 'checkpoints', 'dpvo'), 'dpvo.pth')
        self._datei(os.path.join(self.prompthmr, 'data', 'pretrain'), 'droidcalib.pth')

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)

    @staticmethod
    def _datei(ordner, name):
        os.makedirs(ordner, exist_ok=True)
        with open(os.path.join(ordner, name), 'w') as f:
            f.write('x')

    def test_alles_da(self):
        self.assertTrue(Slamstatus.verfuegbar(self.python, self.gvhmr, self.prompthmr))

    def test_ein_fehlendes_rad_wird_genannt(self):
        os.remove(os.path.join(self.sp, 'cuda_ba.cp310-win_amd64.pyd'))
        fehlt = Slamstatus.fehlend(self.python, self.gvhmr, self.prompthmr)
        self.assertEqual(len(fehlt), 1)
        self.assertIn('cuda_ba', fehlt[0])

    def test_fehlende_gewichte_zaehlen_auch(self):
        os.remove(os.path.join(self.prompthmr, 'data', 'pretrain', 'droidcalib.pth'))
        self.assertFalse(Slamstatus.verfuegbar(self.python, self.gvhmr, self.prompthmr))

    def test_unsinnige_einstellung_ist_nur_nicht_verfuegbar(self):
        u"""Die Uploadseite patcht `settings` in Tests mit einem MagicMock."""
        self.assertFalse(Slamstatus.verfuegbar(MagicMock(), MagicMock(), MagicMock()))
