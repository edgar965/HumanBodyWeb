"""`Meshgenesistestwahl`: Häkchen eines Tests ohne Job, ein Test eines Jobs bleibt zu. Ohne Datenbank."""
import json
import tempfile
import unittest
from pathlib import Path

from django.test import override_settings

from core.dienste.meshgenesistestwahl import Meshgenesistestwahl


class MeshgenesistestwahlTest(unittest.TestCase):
    databases = []

    def _ablage(self, einstellung=None, job=None):
        """Ein Test `t`, optional `einstellung.json` und ein Job, der ihn nennt."""
        wurzel = Path(tempfile.mkdtemp(dir=r'A:\3DTools\ProjektTemp\_wegwerf'))
        test = wurzel / 'meshgenesis' / '_test' / 't'
        test.mkdir(parents=True)
        (test / 'anlage.json').write_text(json.dumps({'name': 'Tanz'}), encoding='utf-8')
        if einstellung is not None:
            (test / 'einstellung.json').write_text(json.dumps(einstellung), encoding='utf-8')
        if job:
            (wurzel / 'fotogenesis' / job).mkdir(parents=True)
            text = json.dumps({'meshgenesis_test': 't'})
            (wurzel / 'fotogenesis' / job / 'job.json').write_text(text, encoding='utf-8')
        return wurzel, test

    def test_vorgaben_wie_in_der_kette(self):
        wurzel, _ = self._ablage()
        with override_settings(OBJECTS_ROOT=wurzel):
            self.assertEqual(Meshgenesistestwahl.lesen('t'), {'haut_ki': True, 'keine_kleider': False})

    def test_setzen_laesst_den_rest_stehen(self):
        wurzel, test = self._ablage({'geschlecht': 'weiblich'})
        with override_settings(OBJECTS_ROOT=wurzel):
            self.assertTrue(Meshgenesistestwahl.setzen('t', 'keine_kleider', True))
            self.assertTrue(Meshgenesistestwahl.lesen('t')['keine_kleider'])
        inhalt = json.loads((test / 'einstellung.json').read_text(encoding='utf-8'))
        self.assertEqual(inhalt, {'geschlecht': 'weiblich', 'keine_kleider': True})

    def test_fremder_name_oder_wert_wird_abgelehnt(self):
        wurzel, _ = self._ablage()
        with override_settings(OBJECTS_ROOT=wurzel):
            self.assertFalse(Meshgenesistestwahl.setzen('t', 'geschlecht', True))
            self.assertFalse(Meshgenesistestwahl.setzen('t', 'haut_ki', 'nein'))
            self.assertFalse(Meshgenesistestwahl.setzen('fehlt', 'haut_ki', True))

    def test_test_eines_jobs_hat_keine_haekchen(self):
        wurzel, test = self._ablage(job='n2')
        with override_settings(OBJECTS_ROOT=wurzel):
            self.assertIsNone(Meshgenesistestwahl.lesen('t'))
            self.assertFalse(Meshgenesistestwahl.setzen('t', 'haut_ki', False))
        self.assertFalse((test / 'einstellung.json').exists())
