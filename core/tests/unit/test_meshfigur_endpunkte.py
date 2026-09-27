# -*- coding: utf-8 -*-
"""Reiter „Mesh to 3D" — Anlegen (genau ein Netz, OBJ-Beilagen dazu), Zustand, Pfadschutz, Seite;
Körper- und Kopfnetz als Pfad, Neuberechnen mit geänderten Pfaden, „Als Genesis-Figur speichern".

Die Auftragsordner liegen während der Prüfung in `ProjektTemp/pruefungen` (`Pruefablage`), nie
unter `3DObjects` — `OBJECTS_ROOT` wird umgelenkt, `HUMANBODY_MODELS_DIR` ebenso. Gestartet wird
nichts (`starten=0`, `Meshfigurarbeiter.starten` ersetzt): kein Arbeitsprozess, keine Grafikkarte.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, TransactionTestCase, override_settings

from core.daten.meshfigurablage import Meshfigurablage
from core.dienste.meshfiguroptionen import Meshfiguroptionen
from core.models import Meshfigurauftrag

from ._pruefablage import Pruefablage

OBJ = b'v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n'


class MeshfigurablageTest(TestCase):
    def test_netzendungen_und_beilagen(self):
        self.assertTrue(Meshfigurablage.ist_netz('Damira.GLB'))
        self.assertTrue(Meshfigurablage.ist_netz('x.obj'))
        self.assertFalse(Meshfigurablage.ist_netz('x.mtl'))
        self.assertTrue(Meshfigurablage.ist_beilage('x.mtl'))
        self.assertTrue(Meshfigurablage.ist_beilage('textur.PNG'))
        self.assertEqual(Meshfigurablage.sauber('..\\böse Datei:1.GLB'), 'b_se_Datei_1.glb')

    def test_datei_nur_in_lesbaren_ordnern_und_ohne_pfad(self):
        ablage = Meshfigurablage('2026.09.27.00.00.00')
        for ordner, name in (
            ('arbeit', 'auftrag.json'),
            ('eingang', '../auftrag.log'),
            ('ergebnis', '..'),
            ('ergebnis', 'a/b.png'),
            ('ergebnis', ''),
        ):
            with self.assertRaises(ValueError, msg='%s/%s' % (ordner, name)):
                ablage.datei(ordner, name)
        self.assertTrue(str(ablage.datei('ergebnis', 'icon.png')).endswith('icon.png'))


class MeshfigurendpunkteTest(TransactionTestCase):
    """`TransactionTestCase`, nicht `TestCase`: `zustand` ist async und liest die Datenbank in einem
    eigenen Faden (`thread_sensitive=False`). Unter der offenen Transaktion von `TestCase` sperrt
    SQLite dort die Tabelle — „database table is locked: core_meshfigurauftrag" (27.09.2026)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='meshfigur_', dir=Pruefablage.wurzel()))
        self.client = Client(HTTP_HOST='127.0.0.1')
        self.referenzen = mock.patch.object(Meshfiguroptionen, '_referenzen', return_value=[('', '—')])
        self.referenzen.start()

    def tearDown(self):
        self.referenzen.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _anlegen(self, dateien, name='ZZ Test'):
        return self.client.post(
            '/api/meshfigur/anlegen/',
            {
                'name': name,
                'netz': dateien,
                'starten': '0',
                'optionen': '{"runden": "3", "basis": "gibtsnicht"}',
            },
        )

    def test_genau_ein_netz(self):
        with override_settings(OBJECTS_ROOT=self.tmp):
            antwort = self._anlegen([SimpleUploadedFile('a.mtl', b'x')])
            self.assertEqual(antwort.status_code, 400)
            antwort = self._anlegen([SimpleUploadedFile('a.obj', OBJ), SimpleUploadedFile('b.glb', b'glTF')])
            self.assertEqual(antwort.status_code, 400)
            self.assertEqual(self._anlegen([SimpleUploadedFile('a.obj', OBJ)], name='').status_code, 400)
            self.assertEqual(Meshfigurauftrag.objects.count(), 0)

    def test_anlegen_zustand_datei_loeschen(self):
        with override_settings(OBJECTS_ROOT=self.tmp):
            antwort = self._anlegen(
                [
                    SimpleUploadedFile('Damira Netz.obj', OBJ),
                    SimpleUploadedFile('Damira Netz.mtl', b'newmtl a\n'),
                    SimpleUploadedFile('haut.png', b'\x89PNG'),
                ]
            )
            self.assertEqual(antwort.status_code, 200, antwort.content[:200])
            job = Meshfigurauftrag.objects.get(pk=antwort.json()['id'])
            self.assertEqual(job.status, 'angelegt', 'starten=0 startet keinen Arbeitsprozess')
            self.assertEqual(job.eingang['datei'], 'Damira_Netz.obj')
            self.assertEqual(sorted(job.eingang['beilagen']), ['Damira_Netz.mtl', 'haut.png'])
            self.assertEqual((job.optionen['runden'], job.optionen['basis']), ('3', 'feminine'))
            ordner = self.tmp / 'meshfigurauftraege' / job.kennung / 'eingang'
            self.assertTrue((ordner / 'Damira_Netz.obj').is_file())
            zustand = self.client.get('/api/meshfigur/%s/zustand/' % job.id).json()
            self.assertEqual(zustand['status'], 'angelegt')
            self.assertEqual(zustand['schritte'][0], 'erkennung')
            self.assertEqual(zustand['stellung'], {})
            self.assertIn('MeshTo3D', zustand['exportordner'])
            self.assertIn('ZZ Test_', zustand['exportordner'], 'Ordner = Name + Anlagezeit')
            netz = self.client.get('/api/meshfigur/%s/datei/eingang/Damira_Netz.obj' % job.id)
            self.assertEqual(netz.status_code, 200)
            self.assertEqual(b''.join(netz.streaming_content), OBJ)
            self.assertEqual(
                self.client.get('/api/meshfigur/%s/datei/arbeit/auftrag.json' % job.id).status_code,
                404,
                'arbeit/ ist nicht lesbar',
            )
            self.assertEqual(
                self.client.get('/modell-aus-dateien/meshfigur/%s/' % job.kennung).status_code, 200
            )
            antwort = self.client.post('/api/meshfigur/%s/loeschen/' % job.id)
            self.assertEqual(antwort.status_code, 200)
            self.assertFalse(Meshfigurauftrag.objects.filter(pk=job.pk).exists())
            self.assertFalse((self.tmp / 'meshfigurauftraege' / job.kennung).exists())

    def test_dashboard_zeigt_den_reiter(self):
        with override_settings(OBJECTS_ROOT=self.tmp):
            seite = self.client.get('/modell-aus-dateien/')
            self.assertEqual(seite.status_code, 200)
            self.assertContains(seite, 'data-reiter="meshto3d"')
            self.assertContains(seite, 'id="meshfigur-form"')
            self.assertContains(seite, 'id="meshfigur-pfad-kopf"')


class MeshfigurpfadeTest(TransactionTestCase):
    """Körper- und Kopfnetz als Pfad (Edgar: „zwei Textboxen … auch beim Job, falls ich neu berechnen
    will"), „Als Genesis-Figur speichern" (Edgar: „… damit die bei den gespeicherten Genesis-Figuren
    vorkommt")."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='meshfigur_', dir=Pruefablage.wurzel()))
        self.client = Client(HTTP_HOST='127.0.0.1')
        self.referenzen = mock.patch.object(Meshfiguroptionen, '_referenzen', return_value=[('', '—')])
        self.referenzen.start()
        self.quelle = self.tmp / 'quelle'
        self.quelle.mkdir()
        (self.quelle / 'koerper.obj').write_bytes(b'mtllib koerper.mtl\n' + OBJ)
        (self.quelle / 'koerper.mtl').write_text('newmtl a\nmap_Kd -bm 1.0 haut.png\n', encoding='utf-8')
        (self.quelle / 'haut.png').write_bytes(b'\x89PNG')
        (self.quelle / 'kopf.glb').write_bytes(b'glTF')

    def tearDown(self):
        self.referenzen.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _anlegen(self, **daten):
        return self.client.post('/api/meshfigur/anlegen/', dict({'name': 'ZZ Pfad', 'starten': '0'}, **daten))

    def _post(self, adresse, daten):
        return self.client.post(adresse, json.dumps(daten), content_type='application/json')

    def test_anlegen_kopiert_netz_beilagen_und_kopfnetz(self):
        with override_settings(OBJECTS_ROOT=self.tmp):
            antwort = self._anlegen(
                pfad_koerper='"%s"' % (self.quelle / 'koerper.obj'), pfad_kopf=str(self.quelle / 'kopf.glb')
            )
            self.assertEqual(antwort.status_code, 200, antwort.content[:300])
            job = Meshfigurauftrag.objects.get(pk=antwort.json()['id'])
            self.assertEqual(
                job.eingang['ursprung'], str(self.quelle / 'koerper.obj'), 'ohne Anführungszeichen'
            )
            self.assertEqual(
                sorted(job.eingang['beilagen']), ['haut.png', 'koerper.mtl'], 'MTL und ihre Textur'
            )
            self.assertEqual(job.eingang['kopf']['datei'], 'kopf.glb')
            ordner = self.tmp / 'meshfigurauftraege' / job.kennung
            self.assertTrue((ordner / 'eingang' / 'haut.png').is_file())
            kopf = self.client.get('/api/meshfigur/%s/datei/eingang_kopf/kopf.glb' % job.id)
            self.assertEqual(kopf.status_code, 200)

    def test_falsche_pfade_hinterlassen_nichts(self):
        with override_settings(OBJECTS_ROOT=self.tmp):
            for daten in (
                {'pfad_koerper': str(self.quelle / 'fehlt.glb')},
                {'pfad_koerper': str(self.quelle / 'haut.png')},
                {
                    'pfad_koerper': str(self.quelle / 'koerper.obj'),
                    'pfad_kopf': str(self.quelle / 'fehlt.obj'),
                },
                {
                    'pfad_koerper': str(self.quelle / 'koerper.obj'),
                    'netz': [SimpleUploadedFile('a.obj', OBJ)],
                },
            ):
                self.assertEqual(self._anlegen(**daten).status_code, 400, daten)
            self.assertEqual(Meshfigurauftrag.objects.count(), 0)
            wurzel = self.tmp / 'meshfigurauftraege'
            self.assertFalse(wurzel.exists() and any(wurzel.iterdir()), 'kein halber Auftragsordner')

    def test_neu_berechnen_liest_geaenderte_pfade_ab_der_erkennung(self):
        with override_settings(OBJECTS_ROOT=self.tmp):
            job_id = self._anlegen(pfad_koerper=str(self.quelle / 'koerper.obj')).json()['id']
            adresse = '/api/meshfigur/%s/starten/' % job_id
            koerper = str(self.quelle / 'koerper.obj')
            with mock.patch('core.api.meshfigur.Meshfigurarbeiter.starten', return_value=4711) as start:
                gleich = self._post(
                    adresse, {'ab': 'textur', 'pfade': {'koerper': koerper, 'kopf': ''}}
                ).json()
                self.assertFalse(gleich['neu_eingelesen'])
                self.assertEqual(
                    start.call_args.kwargs['ab'], 'textur', 'unverändert: ab dem gewählten Schritt'
                )
                kopf = str(self.quelle / 'kopf.glb')
                neu = self._post(
                    adresse, {'ab': 'textur', 'pfade': {'koerper': koerper, 'kopf': kopf}}
                ).json()
                self.assertTrue(neu['neu_eingelesen'])
                self.assertIsNone(start.call_args.kwargs['ab'], 'neues Netz: alles ab der Erkennung')
                self.assertEqual(
                    Meshfigurauftrag.objects.get(pk=job_id).eingang['kopf']['original'], 'kopf.glb'
                )
                weg = self._post(adresse, {'pfade': {'koerper': '', 'kopf': ''}}).json()
                self.assertTrue(weg['neu_eingelesen'], 'leeres Kopffeld nimmt das Kopfnetz heraus')
                eingang = Meshfigurauftrag.objects.get(pk=job_id).eingang
                self.assertNotIn('kopf', eingang)
                self.assertEqual(
                    eingang['ursprung'], koerper, 'leeres Körperfeld lässt das Körpernetz stehen'
                )

    def test_als_genesis_figur_speichern_ohne_fremde_zu_ueberschreiben(self):
        modelle = self.tmp / 'modelle'
        modelle.mkdir()
        (modelle / 'Fremd.json').write_text(
            '{"name": "Fremd", "quelle": "genesis9", "figur": {}}', encoding='utf-8'
        )
        with override_settings(OBJECTS_ROOT=self.tmp, HUMANBODY_MODELS_DIR=modelle):
            job = Meshfigurauftrag.objects.create(
                kennung='2026.09.27.00.00.01',
                name='ZZ',
                eingang={},
                optionen={},
                status='fertig',
                ergebnis={'regler': {'stellung': {'body_bs_BodyMass': 0.3}}},
            )
            adresse = '/api/meshfigur/%s/modell/' % job.id
            self.assertEqual(self._post(adresse, {'name': 'Fremd'}).status_code, 400)
            self.assertEqual(self._post(adresse, {'name': 'ZZ Damira'}).json()['modell'], 'ZZ Damira')
            daten = json.loads((modelle / 'ZZ Damira.json').read_text(encoding='utf-8'))
            self.assertEqual(
                (daten['quelle'], daten['figur']['regler']), ('genesis9', {'body_bs_BodyMass': 0.3})
            )
            self.assertEqual(
                self._post(adresse, {'name': 'ZZ Damira'}).status_code, 200, 'eigene Figur: neu schreiben'
            )
            self.assertEqual(json.loads((modelle / 'Fremd.json').read_text(encoding='utf-8'))['figur'], {})
