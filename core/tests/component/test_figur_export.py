# -*- coding: utf-8 -*-
u"""Figurexport: GLB ablegen, auflisten, ausliefern — auf einem Wegwerf-Ordner.

WARUM (05.09.2026): Roomguest holt die Figur über diese drei Routen. Ein
Endpunkt, der eine Nicht-GLB annimmt oder einen Namen aus dem Ordner
hinauslässt, fiele erst beim Laden in Unity auf — ohne brauchbare Meldung.

GESCHRIEBEN WIRD IN EIN WEGWERF-VERZEICHNIS unter `ProjektTemp/` (wie
`test_bildablage`), nie in `HumanBody/data/` und nie ins System-Temp.
"""
import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

#: Ein minimaler GLB-Kopf: Magic, Version 2, Gesamtlänge 20, dann acht Nullbytes.
GLB = b'glTF' + (2).to_bytes(4, 'little') + (20).to_bytes(4, 'little') + b'\0' * 8
TYP = 'model/gltf-binary'


class FigurexportTest(TestCase):

    def setUp(self):
        # `dir=` ist Pflicht: sonst System-Temp auf C: (Befund `lehren-treue`).
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        self.ordner = tempfile.mkdtemp(prefix='figurexport_', dir=str(basis))
        self.addCleanup(shutil.rmtree, self.ordner, True)
        umschaltung = override_settings(HUMANBODY_FIGUR_EXPORT_DIR=self.ordner)
        umschaltung.enable()
        self.addCleanup(umschaltung.disable)

    def _ablegen(self, name='Mila 2', inhalt=GLB):
        datei = SimpleUploadedFile(name + '.glb', inhalt, content_type=TYP)
        return self.client.post(reverse('figur_glb_ablegen', args=[name]), {'glb': datei})

    def test_ablegen_schreibt_die_datei_und_listet_sie(self):
        antwort = self._ablegen()
        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertEqual(antwort.json()['bytes'], len(GLB))
        self.assertTrue((Path(self.ordner) / 'Mila 2.glb').is_file())
        liste = self.client.get(reverse('figur_glb_liste')).json()
        self.assertEqual([f['name'] for f in liste['figuren']], ['Mila 2'])
        self.assertEqual(liste['figuren'][0]['bytes'], len(GLB))

    def test_datei_kommt_als_gltf_binary(self):
        self._ablegen('figur')
        antwort = self.client.get(reverse('figur_glb', args=['figur']))
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort['Content-Type'], TYP)
        self.assertEqual(b''.join(antwort.streaming_content), GLB)

    def test_ohne_glb_kopf_abgewiesen(self):
        antwort = self._ablegen('x', b'{"kein": "glb"}')
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('glTF', antwort.json()['error'])

    def test_ohne_datei_abgewiesen(self):
        antwort = self.client.post(reverse('figur_glb_ablegen', args=['x']))
        self.assertEqual(antwort.status_code, 400)

    def test_name_darf_den_ordner_nicht_verlassen(self):
        self.assertEqual(self.client.get(reverse('figur_glb', args=['..'])).status_code, 400)
        self.assertEqual(self._ablegen('..').status_code, 400)

    def test_unbekannte_figur_404(self):
        self.assertEqual(self.client.get(reverse('figur_glb', args=['nix'])).status_code, 404)

    def test_ablegen_nur_per_post(self):
        self.assertEqual(self.client.get(reverse('figur_glb_ablegen', args=['x'])).status_code, 405)
