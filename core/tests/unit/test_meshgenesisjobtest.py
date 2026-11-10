"""`Meshgenesisjobtest`: Tests eines Jobs erkennen, echte Mesh-Genesis-Tests unberührt lassen. Ohne Datenbank."""
import json
import tempfile
import unittest
from pathlib import Path

from django.test import override_settings

from core.dienste.meshgenesisjobtest import Meshgenesisjobtest


class MeshgenesisjobtestTest(unittest.TestCase):
    databases = []

    def _ablage(self, jobs=(), tests=()):
        """`jobs`: (Ordner, meshgenesis_test); `tests`: (Kennung, Name in anlage.json)."""
        wurzel = Path(tempfile.mkdtemp(dir=r'A:\3DTools\ProjektTemp\_wegwerf'))
        for ordner, test in jobs:
            job = wurzel / 'fotogenesis' / ordner
            job.mkdir(parents=True)
            (job / 'job.json').write_text(json.dumps({'meshgenesis_test': test}), encoding='utf-8')
        for kennung, name in tests:
            ablage = wurzel / 'meshgenesis' / '_test' / kennung
            ablage.mkdir(parents=True)
            (ablage / 'anlage.json').write_text(json.dumps({'name': name}), encoding='utf-8')
        return wurzel

    def test_genannter_test_gehoert_zum_job(self):
        wurzel = self._ablage([('Edgar_alle', 'edgar_alle')], [('edgar_alle', 'Edgar alle')])
        with override_settings(OBJECTS_ROOT=wurzel):
            self.assertEqual(Meshgenesisjobtest.kennungen(), {'edgar_alle'})

    def test_name_zaehlt_solange_die_job_json_ihn_nicht_nennt(self):
        wurzel = self._ablage([('n2', None)], [('n2_mesh_genesis_2', 'n2-mesh-genesis')])
        with override_settings(OBJECTS_ROOT=wurzel):
            self.assertEqual(Meshgenesisjobtest.kennungen(), {'n2_mesh_genesis_2'})

    def test_echter_test_bleibt_in_der_liste(self):
        wurzel = self._ablage([('n2', None)], [('edgar', 'Edgar'), ('venus', 'venus-mesh-genesis')])
        with override_settings(OBJECTS_ROOT=wurzel):
            self.assertEqual(Meshgenesisjobtest.kennungen(), set())

    def test_ohne_ablage_leer(self):
        with override_settings(OBJECTS_ROOT=self._ablage()):
            self.assertEqual(Meshgenesisjobtest.kennungen(), set())
