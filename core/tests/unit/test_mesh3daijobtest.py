"""`Mesh3daijobtest`: Tests eines Jobs erkennen, echte Mesh3D-AI-Tests unberührt lassen. Ohne Datenbank."""
import json
import tempfile
import unittest
from pathlib import Path

from django.test import override_settings

from core.dienste.mesh3daijobtest import Mesh3daijobtest


class Mesh3daijobtestTest(unittest.TestCase):
    databases = []

    def _ablage(self, jobs=(), tests=()):
        """`jobs`: (Ordner, mesh3dai_test); `tests`: (Kennung, Name in anlage.json)."""
        wurzel = Path(tempfile.mkdtemp(dir=r'A:\3DTools\ProjektTemp\_wegwerf'))
        for ordner, test in jobs:
            job = wurzel / 'ai2d3d' / ordner
            job.mkdir(parents=True)
            (job / 'job.json').write_text(json.dumps({'mesh3dai_test': test}), encoding='utf-8')
        for kennung, name in tests:
            ablage = wurzel / 'mesh3dai' / '_test' / kennung
            ablage.mkdir(parents=True)
            (ablage / 'anlage.json').write_text(json.dumps({'name': name}), encoding='utf-8')
        return wurzel

    def test_genannter_test_gehoert_zum_job(self):
        wurzel = self._ablage([('Edgar_alle', 'edgar_alle')], [('edgar_alle', 'Edgar alle')])
        with override_settings(OBJECTS_ROOT=wurzel):
            self.assertEqual(Mesh3daijobtest.kennungen(), {'edgar_alle'})

    def test_name_zaehlt_solange_die_job_json_ihn_nicht_nennt(self):
        wurzel = self._ablage([('n2', None)], [('n2_mesh3d_ai_2', 'n2-mesh3d-AI')])
        with override_settings(OBJECTS_ROOT=wurzel):
            self.assertEqual(Mesh3daijobtest.kennungen(), {'n2_mesh3d_ai_2'})

    def test_echter_test_bleibt_in_der_liste(self):
        wurzel = self._ablage([('n2', None)], [('edgar', 'Edgar'), ('venus', 'venus-mesh3d-AI')])
        with override_settings(OBJECTS_ROOT=wurzel):
            self.assertEqual(Mesh3daijobtest.kennungen(), set())

    def test_ohne_ablage_leer(self):
        with override_settings(OBJECTS_ROOT=self._ablage()):
            self.assertEqual(Mesh3daijobtest.kennungen(), set())
