# -*- coding: utf-8 -*-
u"""`POST /api/animation/video/` nimmt den Auftrag als Formular entgegen.

Seit dem 11.09.2026 kommen die Kleidungsstuecke als Binaerdateien neben
dem Auftrag (`scene/figurvideo_stuecke.js`). Der Endpunkt muss beides
durchreichen: das JSON aus dem Feld `auftrag` und `request.FILES`. Der
Lauf selbst (Unterprozess, Minuten) wird hier durch eine Attrappe ersetzt,
die festhaelt, was bei ihr ankam — ein Endpunkt, der die Dateien vergisst,
faellt so auf, ohne dass ein Video entsteht.

Dazu der Browser-Weg (`aufnahme`): Ablageordner, Dateiname, Figur und
Animation muessen bei `aus_bildfolge` ankommen und der Pfad der Kopie in
der Antwort stehen.
"""
import json
import os
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from django.urls import reverse

from core.api import figurvideo as endpunkt

ORDNER = 'A:' + os.sep + 'v'
PFAD = os.path.join(ORDNER, 'a.mp4')
PNG = b'\x89PNG'


class FigurvideoEndpunktTest(SimpleTestCase):

    databases = set()

    def _starten(self, **felder):
        with mock.patch.object(endpunkt.Figurvideo, 'starten',
                               return_value='abc123') as attrappe:
            antwort = self.client.post(reverse('figurvideo_starten'), felder)
        return antwort, attrappe

    def test_formular_mit_stueck(self):
        auftrag = {'bvh_url': '/api/character/bvh/Walk/136_28/',
                   'stuecke': [{'name': 'Hose', 'datei': 'stueck_0',
                                'punkte': 3, 'dreiecke': 1}],
                   'knochen': ['DEF-spine']}
        antwort, attrappe = self._starten(
            auftrag=json.dumps(auftrag),
            stueck_0=SimpleUploadedFile('stueck_0.bin', b'\x00' * 12))
        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertEqual(antwort.json()['kennung'], 'abc123')
        daten, dateien = attrappe.call_args.args
        self.assertEqual(daten['stuecke'][0]['datei'], 'stueck_0')
        self.assertEqual(daten['knochen'], ['DEF-spine'])
        self.assertIn('stueck_0', dateien)

    def test_json_rumpf_geht_weiter(self):
        with mock.patch.object(endpunkt.Figurvideo, 'starten',
                               return_value='def456') as attrappe:
            antwort = self.client.post(
                reverse('figurvideo_starten'),
                json.dumps({'bvh_url': '/api/character/bvh/Walk/136_28/'}),
                content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content)
        daten, dateien = attrappe.call_args.args
        self.assertEqual(daten['bvh_url'], '/api/character/bvh/Walk/136_28/')
        self.assertEqual(len(dateien), 0)

    def test_ohne_animation_400(self):
        antwort, attrappe = self._starten(auftrag=json.dumps({'sekunden': 3}))
        self.assertEqual(antwort.status_code, 400)
        self.assertFalse(attrappe.called)

    def test_kaputtes_json_400(self):
        antwort, _attrappe = self._starten(auftrag='{nicht json')
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('JSON', antwort.json()['fehler'])

    def test_wertfehler_wird_400(self):
        with mock.patch.object(endpunkt.Figurvideo, 'starten',
                               side_effect=ValueError('Stueck ohne Daten')):
            antwort = self.client.post(
                reverse('figurvideo_starten'),
                {'auftrag': json.dumps({'bvh_url': '/x/y/'})})
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('ohne Daten', antwort.json()['fehler'])

    # ------------------------------------------------------ Browser-Weg

    def test_aufnahme_reicht_ablage_durch(self):
        with mock.patch.object(endpunkt.Figurvideo, 'aus_bildfolge',
                               return_value=('k1', '/media/x.mp4',
                                             PFAD)) as attrappe:
            antwort = self.client.post(
                reverse('figurvideo_aufnahme'),
                {'frames': SimpleUploadedFile('000000.png', PNG),
                 'fps': '24', 'physik_mm': '25', 'ablage': ORDNER,
                 'dateiname': 'a', 'figur': 'F', 'animation': 'Walk_1'})
        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertEqual(antwort.json()['pfad'], PFAD)
        self.assertEqual(attrappe.call_args.kwargs['ablage'],
                         {'ordner': ORDNER, 'name': 'a', 'figur': 'F',
                          'animation': 'Walk_1'})

    def test_aufnahme_falsche_ablage_400(self):
        with mock.patch.object(endpunkt.Figurvideo, 'aus_bildfolge',
                               side_effect=ValueError('vollständiger Pfad')):
            antwort = self.client.post(
                reverse('figurvideo_aufnahme'),
                {'frames': SimpleUploadedFile('000000.png', PNG),
                 'ablage': 'relativ'})
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('Pfad', antwort.json()['fehler'])

    def test_ablage_vorgabe(self):
        antwort = self.client.get(reverse('figurvideo_ablage'))
        self.assertEqual(antwort.status_code, 200)
        self.assertTrue(antwort.json()['ordner'].endswith('figurvideos'))
