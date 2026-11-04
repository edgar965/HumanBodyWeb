# -*- coding: utf-8 -*-
"""PSHuman-Eingabe auf der Testseite von 2d-3d-AI (03.11.2026, `Ai2d3dpshumaneingabe`,
`Ai2d3dpshumanendpunkte`).

WARUM: Edgar, 03.11.2026: „mach im job ein UI das entweder eines oder mehrere Bilder nimmt … mit Upload
möglichkeit für alle. Wenn ein Bild als Input, dann zeige die erzeugten bilder von pshuman“. Diese Tests
halten fest: sechs Plätze in PSHumans Reihenfolge, „vorn“ kommt ohne Upload aus dem Foto des Jobs; ein
Upload landet im Jobordner und in der job.json und ersetzt nie still ein älteres Bild (es bleibt umbenannt
liegen); falsche Plätze und Endungen werden abgelehnt; Bilder gibt es nur über den Platz, nie über einen
Pfad; „Übernehmen“ im Formular lässt die Plätze stehen; erzeugte Ansichten werden gefunden. Ablage wie
`test_ai2d3d_seiten` (nie Edgars 3DObjects).
"""

import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from core.dienste.ai2d3dpshuman import Ai2d3dpshuman
from core.dienste.ai2d3dpshumaneingabe import Ai2d3dpshumaneingabe
from core.tests.component.test_ai2d3d_seiten import Ai2d3dAblageMixin

PNG = b'\x89PNG\r\n\x1a\n'


class Ai2d3dPshumanEingabe(Ai2d3dAblageMixin, SimpleTestCase):
    databases = set()
    BASIS = '/api/2d3dai/fototest/pshuman'

    def _info(self):
        return json.loads((self.objekte / 'ai2d3d' / 'Fototest' / 'job.json').read_text(encoding='utf-8'))

    def _hoch(self, winkel, name='bild.png', inhalt=PNG):
        datei = SimpleUploadedFile(name, inhalt)
        return self.client.post('%s/eingabe/%d/' % (self.BASIS, winkel), {'datei': datei})

    def test_sechs_plaetze_vorn_und_linke_seite_aus_den_fotos_des_jobs(self):
        info = self._info()
        fotos = [{'winkel': f['winkel'], 'pfad': f['datei']} for f in info['fotos']]
        plaetze = Ai2d3dpshumaneingabe.lesen(self.objekte / 'ai2d3d' / 'Fototest', info, fotos)
        self.assertEqual([p['winkel'] for p in plaetze], [0, 45, 90, 180, 270, 315])
        self.assertEqual([p['quelle'] for p in plaetze], ['job', None, 'job', None, None, None])
        self.assertFalse(any(p['erzeugt'] for p in plaetze))
        text = self.client.get('/2d-3d-AI/test/fototest/').content.decode('utf-8')
        self.assertIn('id="ai2d3d-pshumaneingabe"', text)
        self.assertEqual(text.count('class="ai2d3d-pshumanplatz"'), 6)

    def test_upload_landet_im_jobordner_und_ersetzt_nichts_still(self):
        antwort = self._hoch(180)
        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertEqual(antwort.json()['platz']['quelle'], 'upload')
        ziel = self.objekte / 'ai2d3d' / 'Fototest' / 'pshuman' / 'eingabe' / 'w180.png'
        self.assertEqual(ziel.read_bytes(), PNG)
        self.assertEqual(self._info()['pshuman']['eingabe'], {'180': str(ziel)})
        self.assertEqual(self._hoch(180, inhalt=PNG + b'zwei').status_code, 200)
        self.assertEqual(ziel.read_bytes(), PNG + b'zwei')
        alte = list(ziel.parent.glob('w180.vor_*.png'))
        self.assertEqual(len(alte), 1)
        self.assertEqual(alte[0].read_bytes(), PNG)
        bild = self.client.get('%s/bild/180/eingabe/' % self.BASIS)
        self.assertEqual(bild.status_code, 200)
        self.assertEqual(b''.join(bild.streaming_content), PNG + b'zwei')

    def test_entfernen_nimmt_aus_der_eingabe_und_behaelt_die_datei(self):
        self._hoch(270)
        antwort = self.client.post('%s/eingabe/270/entfernen/' % self.BASIS)
        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertIsNone(antwort.json()['platz']['quelle'])
        self.assertEqual(self._info()['pshuman']['eingabe'], {})
        eingabe = self.objekte / 'ai2d3d' / 'Fototest' / 'pshuman' / 'eingabe'
        self.assertEqual(len(list(eingabe.glob('w270.vor_*.png'))), 1)
        self.assertEqual(self.client.post('%s/eingabe/270/entfernen/' % self.BASIS).status_code, 400)

    def test_falscher_platz_falsche_endung_und_pfade_werden_abgelehnt(self):
        self.assertEqual(self._hoch(30).status_code, 400)
        self.assertEqual(self._hoch(0, name='bild.exe').status_code, 400)
        self.assertNotIn('pshuman', self._info())
        for adresse in ('bild/30/eingabe/', 'bild/0/zauber/', 'bild/45/eingabe/', 'bild/90/farbe/'):
            self.assertEqual(self.client.get('%s/%s' % (self.BASIS, adresse)).status_code, 404, adresse)

    def test_formular_uebernehmen_laesst_die_plaetze_stehen(self):
        self._hoch(90)
        rumpf = json.dumps({'zeile1': True, 'anzahl': 4, 'vae_bildweise': True})
        antwort = self.client.post(self.BASIS + '/', rumpf, content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content)
        p = self._info()['pshuman']
        self.assertEqual((p['anzahl'], p['vae_bildweise'], list(p['eingabe'])), (4, True, ['90']))
        for wert in (0, 7, True, 'viele'):
            falsch = self.client.post(self.BASIS + '/', json.dumps({'anzahl': wert}),
                                      content_type='application/json')
            self.assertEqual(falsch.status_code, 400, wert)
        self.assertEqual(Ai2d3dpshuman.lesen({})['anzahl'], 1)
        self.assertEqual(Ai2d3dpshuman.lesen({})['dichte'], 480)
        self.assertFalse(Ai2d3dpshuman.lesen({})['fototextur'])
        self.assertFalse(Ai2d3dpshuman.lesen({})['genesis_aus_foto'])
        for rumpf in ({'dichte': 960}, {'fototextur': True}):
            self.assertEqual(self.client.post(self.BASIS + '/', json.dumps(rumpf), content_type='application/json').status_code, 200)
        p = self._info()['pshuman']
        self.assertEqual((p['dichte'], p['fototextur'], p['anzahl']), (960, True, 4))
        self.assertEqual(self.client.post(self.BASIS + '/', json.dumps({'dichte': 700}), content_type='application/json').status_code, 400)

    def test_geschlecht_steht_in_der_jobjson(self):
        # 04.11.2026, Edgar: „Auswahl ob Genesis Männlich, weiblich“
        adresse = self.BASIS.rsplit('/', 1)[0] + '/geschlecht/'
        antwort = self.client.post(adresse, json.dumps({'geschlecht': 'weiblich'}), content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertEqual(self._info()['geschlecht'], 'weiblich')
        falsch = self.client.post(adresse, json.dumps({'geschlecht': 'zauber'}), content_type='application/json')
        self.assertEqual(falsch.status_code, 400)

    def test_erzeugte_ansichten_von_pshuman_werden_gefunden(self):
        rembg = self.objekte / 'ai2d3d' / 'Fototest' / 'pshuman' / 'rekon' / 'rembg'
        rembg.mkdir(parents=True)
        for art in ('farbe', 'normale'):
            (rembg / ('%s_3_back.png' % art)).write_bytes(PNG)
        info = self._info()
        plaetze = Ai2d3dpshumaneingabe.lesen(self.objekte / 'ai2d3d' / 'Fototest', info, [])
        platz = next(p for p in plaetze if p['winkel'] == 180)
        self.assertTrue(platz['erzeugt'])
        self.assertEqual(self.client.get('%s/bild/180/normale/' % self.BASIS).status_code, 200)

    def test_ein_job_liest_nie_aus_einem_anderen_job(self):
        # 04.11.2026, Edgar: „die jobs sollen immer unabhängig sein, was soll der schwachsinn mit Basisjobs???“ — auch ein alter Eintrag `probe.basis` wirkt nicht mehr
        fremd = self.objekte / 'ai2d3d' / 'Fototest'
        rembg = fremd / 'pshuman' / 'rekon' / 'rembg'
        rembg.mkdir(parents=True)
        for art in ('farbe', 'normale'):
            (rembg / ('%s_3_back.png' % art)).write_bytes(PNG)
        job = self.objekte / 'ai2d3d' / 'Fototest--probe'
        job.mkdir()
        platz = next(p for p in Ai2d3dpshumaneingabe.lesen(job, {'probe': {'basis': 'Fototest'}}, []) if p['winkel'] == 180)
        self.assertFalse(platz['erzeugt'])
