# -*- coding: utf-8 -*-
"""`Hautohneki.gewuenscht`: Ein ausdrückliches `"haut_ki"` entscheidet (05.11.2026); ohne Wahl ist die Haut-KI bei einem Netz aus einem Foto aus (06.11.2026), sonst an. Geschrieben, nicht gelaufen."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, r'A:\3DTools\mesh3dai')

from mesh3dai_haut_ohneki import Hautohneki  # noqa: E402


class HautohnekiTest(unittest.TestCase):
    databases = []

    def _mit(self, inhalt):
        ordner = Path(tempfile.mkdtemp(dir=r'A:\3DTools\ProjektTemp\_wegwerf'))
        if inhalt is not None:
            (ordner / 'einstellung.json').write_text(inhalt, encoding='utf-8')
        return ordner

    def test_nur_false_schaltet_ab(self):
        self.assertTrue(Hautohneki.gewuenscht(self._mit(json.dumps({'haut_ki': False}))))
        self.assertFalse(Hautohneki.gewuenscht(self._mit(json.dumps({'haut_ki': True}))))
        self.assertFalse(Hautohneki.gewuenscht(self._mit(json.dumps({'geschlecht': 'maennlich'}))))

    def _mit_foto(self, inhalt):
        ordner = self._mit(inhalt)
        (ordner / 'foto').mkdir()
        for name in ('foto.png', 'maske.png'):
            (ordner / 'foto' / name).write_bytes(b'x')
        return ordner

    def test_netz_aus_einem_foto_kommt_ohne_ki(self):
        self.assertTrue(Hautohneki.gewuenscht(self._mit_foto(None)))

    def test_ausdrueckliches_an_gilt_auch_beim_foto(self):
        self.assertFalse(Hautohneki.gewuenscht(self._mit_foto(json.dumps({'haut_ki': True}))))

    def test_ohne_lesbare_datei_bleibt_die_ki(self):
        self.assertFalse(Hautohneki.gewuenscht(self._mit(None)))
        self.assertFalse(Hautohneki.gewuenscht(self._mit('kein json')))
        self.assertFalse(Hautohneki.gewuenscht(self._mit('[]')))

    def _job(self, info, einstellung=None, anlage=None):
        """Ablage wie `3DObjects`: Test `t` unter `mesh3dai/_test/`, Job `J` unter `ai2d3d/`."""
        wurzel = Path(tempfile.mkdtemp(dir=r'A:\3DTools\ProjektTemp\_wegwerf'))
        test = wurzel / 'mesh3dai' / '_test' / 't'
        test.mkdir(parents=True)
        (wurzel / 'ai2d3d' / 'J').mkdir(parents=True)
        (wurzel / 'ai2d3d' / 'J' / 'job.json').write_text(json.dumps(info), encoding='utf-8')
        if einstellung is not None:
            (test / 'einstellung.json').write_text(json.dumps(einstellung), encoding='utf-8')
        if anlage is not None:
            (test / 'anlage.json').write_text(json.dumps(anlage), encoding='utf-8')
        return test

    def test_das_haekchen_des_jobs_entscheidet(self):
        self.assertTrue(Hautohneki.gewuenscht(self._job({'mesh3dai_test': 't', 'pshuman': {'haut_ki': False}})))
        self.assertFalse(Hautohneki.gewuenscht(self._job({'mesh3dai_test': 't', 'pshuman': {'haut_ki': True}}, {'haut_ki': False})))

    def test_beim_ersten_lauf_ueber_den_namen(self):
        self.assertTrue(Hautohneki.gewuenscht(self._job({'pshuman': {'haut_ki': False}}, anlage={'name': 'J-mesh3d-AI'})))
        self.assertFalse(Hautohneki.gewuenscht(self._job({'pshuman': {'haut_ki': False}}, anlage={'name': 'Anderer-mesh3d-AI'})))

    def test_job_ohne_wahl_laesst_die_einstellung_gelten(self):
        self.assertTrue(Hautohneki.gewuenscht(self._job({'mesh3dai_test': 't'}, {'haut_ki': False})))
        self.assertFalse(Hautohneki.gewuenscht(self._job({'mesh3dai_test': 't'})))
