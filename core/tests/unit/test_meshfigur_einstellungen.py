"""Auftragsseite „Mesh to 3D": jede Eingabe sofort speichern, Kopfnetz abschaltbar (29.09.2026).

Edgar: „bei eingabe in irgend ein feld soll das automatisch gespeichert werden" und „mach mir bei den Jobs
Mesh to 3D die auswahl des Kopfes optional". `POST …/einstellungen/` speichert Optionen und Pfade ohne Lauf;
ein neu eingelesenes Netz lässt den nächsten Start bei der Erkennung beginnen. Ordner in `ProjektTemp`
(`Pruefablage`), kein Arbeitsprozess.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.test import Client, TransactionTestCase, override_settings

from core.dienste.meshfigurarbeiter import Meshfigurarbeiter
from core.dienste.meshfiguroptionen import Meshfiguroptionen
from core.models import Meshfigurauftrag

from ._pruefablage import Pruefablage
from .test_meshfigur_endpunkte import OBJ


class MeshfigureinstellungenTest(TransactionTestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='meshfigur_', dir=Pruefablage.wurzel()))
        self.client = Client(HTTP_HOST='127.0.0.1')
        self.referenzen = mock.patch.object(Meshfiguroptionen, '_referenzen', return_value=[('', '—')])
        self.referenzen.start()
        self.quelle = self.tmp / 'quelle'
        self.quelle.mkdir()
        (self.quelle / 'koerper.obj').write_bytes(OBJ)
        (self.quelle / 'edgar.obj').write_bytes(OBJ + b'\n# edgar')
        (self.quelle / 'kopf.glb').write_bytes(b'glTF')
        self.umlenkung = override_settings(OBJECTS_ROOT=self.tmp)
        self.umlenkung.enable()
        antwort = self.client.post('/api/meshfigur/anlegen/', {
            'name': 'ZZ Einstellungen', 'starten': '0', 'pfad_koerper': str(self.quelle / 'koerper.obj'),
            'pfad_kopf': str(self.quelle / 'kopf.glb')})
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        self.job = Meshfigurauftrag.objects.get(pk=antwort.json()['id'])

    def tearDown(self):
        self.umlenkung.disable()
        self.referenzen.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _speichern(self, **daten):
        return self.client.post('/api/meshfigur/%s/einstellungen/' % self.job.id, json.dumps(daten),
                                content_type='application/json')

    def _pfade(self, koerper='koerper.obj', kopf='kopf.glb'):
        return {'koerper': str(self.quelle / koerper), 'kopf': str(self.quelle / kopf) if kopf else ''}

    def test_optionen_ohne_lauf_gespeichert(self):
        with mock.patch.object(Meshfigurarbeiter, 'starten') as starten:
            antwort = self._speichern(optionen={'basis': 'masculine', 'frisur': 'eigen'})
        self.assertEqual(antwort.status_code, 200)
        starten.assert_not_called()
        self.job.refresh_from_db()
        self.assertEqual((self.job.optionen['basis'], self.job.optionen['frisur']), ('masculine', 'eigen'))
        self.assertEqual(self.job.status, 'angelegt')

    def test_kopfnetz_aus_nimmt_es_heraus_und_merkt_den_pfad(self):
        antwort = self._speichern(pfade=self._pfade(), kopf_an=False)
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        self.job.refresh_from_db()
        self.assertNotIn('kopf', self.job.eingang)
        self.assertEqual(self.job.eingang['kopf_gemerkt'], str(self.quelle / 'kopf.glb'))
        kopfordner = self.tmp / 'meshfigurauftraege' / self.job.kennung / 'eingang_kopf'
        self.assertEqual(list(kopfordner.iterdir()) if kopfordner.exists() else [], [])
        self._speichern(pfade=self._pfade(), kopf_an=True)
        self.job.refresh_from_db()
        self.assertEqual(self.job.eingang['kopf']['datei'], 'kopf.glb', 'wieder an = wieder da')
        self.assertNotIn('kopf_gemerkt', self.job.eingang)

    def test_neues_koerpernetz_laesst_den_naechsten_start_bei_der_erkennung_beginnen(self):
        antwort = self._speichern(pfade=self._pfade('edgar.obj'), kopf_an=True)
        self.assertTrue(antwort.json()['neu_eingelesen'])
        self.job.refresh_from_db()
        self.assertEqual(self.job.eingang['ursprung'], str(self.quelle / 'edgar.obj'))
        with mock.patch.object(Meshfigurarbeiter, 'starten', return_value=1) as starten:
            antwort = self.client.post('/api/meshfigur/%s/starten/' % self.job.id,
                                       json.dumps({'ab': 'gesicht'}), content_type='application/json')
        self.assertTrue(antwort.json()['neu_eingelesen'])
        self.assertIsNone(starten.call_args.kwargs['ab'],
                          'anderes Netz = ab der Erkennung, nicht ab „gesicht“')
        self.job.refresh_from_db()
        self.assertNotIn('neu_eingelesen', self.job.eingang, 'die Marke gilt nur für EINEN Start')

    def test_falscher_pfad_meldet_und_speichert_die_optionen_trotzdem(self):
        antwort = self._speichern(optionen={'basis': 'neutral'}, pfade=self._pfade('fehlt.obj'))
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('fehlt.obj', antwort.json()['error'])
        self.job.refresh_from_db()
        self.assertEqual(self.job.optionen['basis'], 'neutral')
        self.assertEqual(self.job.eingang['ursprung'], str(self.quelle / 'koerper.obj'))

    def test_waehrend_eines_laufs_gesperrt(self):
        Meshfigurauftrag.objects.filter(pk=self.job.pk).update(status='laeuft')
        with mock.patch.object(Meshfigurarbeiter, 'lebt', return_value=True):
            self.assertEqual(self._speichern(optionen={'basis': 'neutral'}).status_code, 409)
