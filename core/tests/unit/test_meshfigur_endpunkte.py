# -*- coding: utf-8 -*-
"""Reiter „Mesh to 3D" — Anlegen (genau ein Netz, OBJ-Beilagen dazu), Zustand, Pfadschutz, Seite.

Die Auftragsordner liegen während der Prüfung in `ProjektTemp/pruefungen` (`Pruefablage`), nie
unter `3DObjects` — `OBJECTS_ROOT` wird umgelenkt. Gestartet wird nichts (`starten=0`): kein
Arbeitsprozess, keine Grafikkarte.
"""

import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

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


class MeshfigurendpunkteTest(TestCase):
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
