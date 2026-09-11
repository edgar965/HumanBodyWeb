# -*- coding: utf-8 -*-
u"""`POST /api/animation/video/` nimmt den Auftrag als Formular entgegen.

Seit dem 11.09.2026 kommen die Kleidungsstuecke als Binaerdateien neben
dem Auftrag (`scene/figurvideo_stuecke.js`). Der Endpunkt muss beides
durchreichen: das JSON aus dem Feld `auftrag` und `request.FILES`. Der
Lauf selbst (Unterprozess, Minuten) wird hier durch eine Attrappe ersetzt,
die festhaelt, was bei ihr ankam — ein Endpunkt, der die Dateien vergisst,
faellt so auf, ohne dass ein Video entsteht.
"""
import json
from unittest import mock

from django.test import SimpleTestCase
from django.urls import reverse

from core.api import figurvideo as endpunkt


class FigurvideoEndpunktTest(SimpleTestCase):

    databases = []

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
        from django.core.files.uploadedfile import SimpleUploadedFile
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
        antwort, attrappe = self._starten(auftrag='{nicht json')
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
