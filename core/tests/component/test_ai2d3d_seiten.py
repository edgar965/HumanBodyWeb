# -*- coding: utf-8 -*-
"""Dashboard → 2d-3d-AI und Hilfe → Architektur → 2d-3d-AI (24.10.2026).

WARUM: Edgar, 24.10.2026: „Ich sagte eine Kopie der Mesh3d-Ai jobs, http://127.0.0.1:8081/2d-3d-AI/ hat schon mal keine Gerechnet Spalten, keine Jobauswahl zum Löschen usw“ — die erste
Fassung hatte eigene Spalten. Diese Tests halten fest: dieselben Spalten wie Mesh3D-AI, Auswahl und Löschen in Jobs und Test, Neuanlage aus Fotos, Exporte als Jobs und echte Fotos als Tests,
Löschen verschiebt bzw. blendet aus (nie ein Exportordner), und die Architekturseite mit der Netzgrafik. Alle Daten in einer eigenen Ablage unter `ProjektTemp/_wegwerf/` (nie Edgars 3DObjects).
"""

import json
import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, SimpleTestCase, override_settings

from core.dienste.architekturai2d3dnetz import Architekturai2d3dnetz
from core.dienste.mesh3daitabelle import Mesh3daitabelle
from core.dienste.mesh3daitesttabelle import Mesh3daitesttabelle


class Ai2d3dAblageMixin:
    """Eine Ablage wie `3DObjects`: ein Export `Probe` (JSON + vier Fotos) und ein Test `Fototest` (job.json mit zwei Fotos)."""

    def setUp(self):
        wurzel = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / '_wegwerf' / 'tests'
        wurzel.mkdir(parents=True, exist_ok=True)
        self.objekte = Path(tempfile.mkdtemp(prefix='ai2d3d_', dir=wurzel))
        export = self.objekte / 'modelsExport' / 'Probe'
        export.mkdir(parents=True)
        (export / 'Probe.json').write_text(json.dumps({'name': 'Probe', 'figur': {'figur': 'probefigur'}}), encoding='utf-8')
        for a in ('vorne', 'links', 'rechts', 'hinten'):
            (export / ('Probe_%s.jpg' % a)).write_bytes(b'\xff\xd8\xff\xd9')
        test = self.objekte / 'ai2d3d' / 'Fototest'
        test.mkdir(parents=True)
        fotos = []
        for i in range(2):
            (test / ('%d.png' % i)).write_bytes(b'\x89PNG\r\n')
            fotos.append({'datei': str(test / ('%d.png' % i)), 'winkel': 90 * i})
        (test / 'job.json').write_text(json.dumps({'name': 'Fototest', 'fotos': fotos, 'netze': [], 'mesh3dai_test': None}), encoding='utf-8')
        self.einstellung = override_settings(OBJECTS_ROOT=self.objekte)
        self.einstellung.enable()
        self.client = Client()

    def tearDown(self):
        self.einstellung.disable()
        shutil.rmtree(self.objekte, ignore_errors=True)


class Ai2d3dListeWieMesh3dai(Ai2d3dAblageMixin, SimpleTestCase):
    databases = set()

    def test_jobs_und_test_tragen_die_spalten_von_mesh3dai(self):
        text = self.client.get('/2d-3d-AI/').content.decode('utf-8')
        for spalte in list(Mesh3daitabelle.SPALTEN) + list(Mesh3daitesttabelle.SPALTEN):
            self.assertIn(spalte['label'], text, spalte['key'])

    def test_auswahl_loeschen_und_neuanlage_sind_da(self):
        text = self.client.get('/2d-3d-AI/').content.decode('utf-8')
        self.assertIn('data-loeschen="jobs"', text)
        self.assertIn('data-loeschen="tests"', text)
        self.assertIn('class="mesh3dai-wahl" data-id="probe"', text)
        self.assertIn('class="mesh3dai-wahl" data-id="fototest"', text)
        self.assertIn('id="ai2d3d-testneu"', text)

    def test_export_ist_ein_job_und_fotos_sind_ein_test(self):
        self.assertEqual(self.client.get('/2d-3d-AI/probe/').status_code, 200)
        self.assertEqual(self.client.get('/2d-3d-AI/test/fototest/').status_code, 200)
        self.assertRedirects(self.client.get('/2d-3d-AI/fototest/'), '/2d-3d-AI/test/fototest/', fetch_redirect_response=False)
        self.assertRedirects(self.client.get('/2d-3d-AI/Probe/'), '/2d-3d-AI/probe/', fetch_redirect_response=False)
        self.assertEqual(self.client.get('/2d-3d-AI/gibtsnicht/').status_code, 404)

    def test_fotos_kommen_nur_aus_dem_job(self):
        self.assertEqual(self.client.get('/api/2d3dai/probe/foto/0/').status_code, 200)
        self.assertEqual(self.client.get('/api/2d3dai/probe/foto/4/').status_code, 404)
        self.assertEqual(self.client.get('/api/2d3dai/probe/netz/tripo3d/').status_code, 404)


class Ai2d3dLoeschenUndNeu(Ai2d3dAblageMixin, SimpleTestCase):
    databases = set()

    def _loeschen(self, art, ids):
        return self.client.post('/api/2d3dai/loeschen/', json.dumps({'art': art, 'ids': ids}), content_type='application/json').json()

    def test_ein_test_wird_verschoben_nicht_geloescht(self):
        self.assertTrue(self._loeschen('tests', ['fototest'])['ok'])
        self.assertFalse((self.objekte / 'ai2d3d' / 'Fototest').exists())
        self.assertEqual(len(list((self.objekte / 'ai2d3d' / '_beiseite').glob('*_geloescht/Fototest/job.json'))), 1)

    def test_ein_export_wird_nur_ausgeblendet(self):
        self.assertTrue(self._loeschen('jobs', ['probe'])['ok'])
        self.assertTrue((self.objekte / 'modelsExport' / 'Probe' / 'Probe.json').is_file())
        self.assertEqual(self.client.get('/2d-3d-AI/probe/').status_code, 404)

    def test_unbekanntes_wird_gemeldet_und_nichts_angelegt(self):
        antwort = self._loeschen('tests', ['gibtsnicht'])
        self.assertFalse(antwort['ok'])
        self.assertFalse((self.objekte / 'ai2d3d' / '_beiseite').exists())

    def test_neuer_test_aus_fotos_legt_job_json_an_und_ueberschreibt_nie(self):
        fotos = [SimpleUploadedFile('a.jpg', b'\xff\xd8\xff\xd9'), SimpleUploadedFile('b.jpg', b'\xff\xd8\xff\xd9')]
        antwort = self.client.post('/api/2d3dai/test-neu/', {'name': 'Neu Test', 'fotos': fotos})
        self.assertEqual(antwort.status_code, 200)
        info = json.loads((self.objekte / 'ai2d3d' / 'Neu_Test' / 'job.json').read_text(encoding='utf-8'))
        self.assertEqual([f['winkel'] for f in info['fotos']], [None, None])
        noch = self.client.post('/api/2d3dai/test-neu/', {'name': 'Neu Test', 'fotos': [SimpleUploadedFile('c.jpg', b'\xff\xd8')]})
        self.assertEqual(noch.status_code, 400)

    def test_nur_fotos_werden_angenommen(self):
        antwort = self.client.post('/api/2d3dai/test-neu/', {'name': 'Falsch', 'fotos': [SimpleUploadedFile('x.exe', b'MZ')]})
        self.assertEqual(antwort.status_code, 400)
        self.assertFalse((self.objekte / 'ai2d3d' / 'Falsch').exists())


class Ai2d3dArchitekturseite(SimpleTestCase):
    databases = set()

    def test_seite_mit_netzgrafik_und_im_menue(self):
        antwort = Client().get('/hilfe/architektur/2d-3d-ai/')
        self.assertEqual(antwort.status_code, 200)
        text = antwort.content.decode('utf-8')
        self.assertIn('aria-label="Neuronales Netz von 2d-3d-AI', text)
        self.assertIn('href="/hilfe/architektur/2d-3d-ai/"', text)
        self.assertIn(f'{Architekturai2d3dnetz.summe():,}'.replace(',', '.'), text)

    def test_gewichte_nach_der_formel(self):
        """Gegenprobe der Rechnung: Linear 2 → 3 = 9; eine Transformer-Schicht mit d = 1, m = 1 = 4 + 4 + 2 + 1 + 1 + 4 = 16."""
        self.assertEqual(Architekturai2d3dnetz.linear(2, 3), 9)
        self.assertEqual(Architekturai2d3dnetz.block(1, 1), 16)
        self.assertEqual(Architekturai2d3dnetz.tokens(), (512 // 16) * (384 // 16))
