# -*- coding: utf-8 -*-
"""Der Test eines Jobs gehört zum Job (06.11.2026, Edgar: „die jobs sollten immer unabhängig voneinander sein“). Geschrieben, nicht gelaufen.
    1  `/mesh-genesis/` lehnt einen Test ab, den eine job.json nennt, und legt einen freien weg
    2  Löschen am Job nimmt seinen Test mit
    3  Nennt ein anderer Job denselben Test, bleibt er
Sabotage (von Hand): `zum_job` leer → Fall 1 rot; `_test_mitnehmen` nicht rufen → Fall 2 rot; Prüfung auf andere Jobs weg → Fall 3 rot.
"""
import json
import unittest
from pathlib import Path

from django.test import override_settings

from core.dienste.fotogenesispapierkorb import Fotogenesispapierkorb
from core.dienste.meshgenesispapierkorb import Meshgenesispapierkorb

from ._pruefablage import Pruefablage


class JobtestPapierkorbTest(unittest.TestCase):
    databases = []

    def setUp(self):
        ablage = Pruefablage.ordner()
        self.wurzel = Path(ablage.__enter__())
        self.addCleanup(ablage.__exit__, None, None, None)
        einstellung = override_settings(OBJECTS_ROOT=self.wurzel)
        einstellung.enable()
        self.addCleanup(einstellung.disable)

    def _test(self, kennung):
        p = self.wurzel / 'meshgenesis' / '_test' / kennung
        p.mkdir(parents=True)
        (p / 'test.json').write_text('{}', encoding='utf-8')
        return p

    def _job(self, name, test):
        p = self.wurzel / 'fotogenesis' / name
        p.mkdir(parents=True)
        (p / 'job.json').write_text(json.dumps({'meshgenesis_test': test}), encoding='utf-8')
        return {'id': name.lower(), 'art': 'foto', 'ordner': p, 'test': test}

    def test_test_eines_jobs_bleibt(self):
        gebunden, frei = self._test('t_job'), self._test('t_frei')
        self._job('J', 't_job')
        ergebnis = {e['kennung']: e for e in Meshgenesispapierkorb.loeschen('tests', ['t_job', 't_frei'])['ergebnis']}
        self.assertFalse(ergebnis['t_job']['ok'])
        self.assertTrue(ergebnis['t_frei']['ok'])
        self.assertTrue(gebunden.is_dir())
        self.assertFalse(frei.is_dir())

    def test_job_nimmt_seinen_test_mit(self):
        test = self._test('t_job')
        job = self._job('J', 't_job')
        erg = Fotogenesispapierkorb.loeschen('tests', ['j'], [job])
        self.assertTrue(erg['ergebnis'][0]['ok'])
        self.assertFalse(test.is_dir())
        self.assertEqual(len(list((self.wurzel / 'meshgenesis' / '_beiseite').glob('*/tests/t_job'))), 1)

    def test_geteilter_test_bleibt(self):
        test = self._test('t_beide')
        a, b = self._job('A', 't_beide'), self._job('B', 't_beide')
        Fotogenesispapierkorb.loeschen('tests', ['a'], [a, b])
        self.assertTrue(test.is_dir())
        self.assertTrue(b['ordner'].is_dir())
