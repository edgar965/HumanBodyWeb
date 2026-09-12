# -*- coding: utf-8 -*-
u"""Einstellungen → Effekte und ihre Wirkung auf die Effekte-Seite.

WARUM (Edgar, 12.09.2026: „erstelle eine Seite Einstellungen - Effekte wo
man das Standard Modell auswählen kann mit dem die Seite geladen wird,
standard: Female2"): Die Seite speichert Vorgaben, die Effekte-Seite
liest sie — Pipeline, Modell, Animation, Windrichtung als
`data-vorgabe-*` am Formular, Bildrate/Breite/Höhe/Wind als Startwert
der Regler. Ein Modell, das es nicht gibt, darf NICHT vorgewählt werden.
"""
import json
import os

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from core.effekte.effektvorgaben import Effektvorgaben
from core.models import AppSettings
from core.tests.unit._pruefablage import Pruefablage
from effekte.figurparameter import Figurparameter


class EinstellungenEffekte(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._ablage = Pruefablage.ordner('einst_effekte_')
        cls.ordner = cls._ablage.__enter__()
        cls.modelle = os.path.join(cls.ordner, 'models')
        os.makedirs(cls.modelle)
        with open(os.path.join(cls.modelle, 'Female2.json'), 'w', encoding='utf-8') as datei:
            json.dump({'name': 'Female2', 'body_type': 'Female_Caucasian',
                       'morphs': {}, 'garmentcode': [], 'hair_style': {}}, datei)

    @classmethod
    def tearDownClass(cls):
        cls._ablage.__exit__(None, None, None)
        super().tearDownClass()

    def setUp(self):
        self.client = Client(HTTP_HOST='127.0.0.1')
        self._modelle = override_settings(HUMANBODY_MODELS_DIR=self.modelle)
        self._modelle.enable()
        self.addCleanup(self._modelle.disable)

    def test_vorgaben_des_modells(self):
        s = AppSettings.load()
        self.assertEqual((s.effekte_default_pipeline, s.effekte_default_model,
                          s.effekte_video_fps, s.effekte_video_width,
                          s.effekte_video_height, s.effekte_wind, s.effekte_windrichtung),
                         ('figur_def', 'Female2', 30, 720, 900, 4.0, 'seite'))

    def test_seite_zeigt_modelle_pipelines_und_zahlen(self):
        antwort = self.client.get(reverse('settings_effekte'))
        self.assertEqual(antwort.status_code, 200)
        text = antwort.content.decode('utf-8')
        self.assertIn('name="effekte_default_model"', text)
        self.assertIn('<option value="Female2"', text)
        self.assertIn('name="effekte_default_pipeline"', text)
        for name in ('effekte_video_fps', 'effekte_video_width',
                     'effekte_video_height', 'effekte_wind'):
            self.assertIn('name="%s"' % name, text)
        self.assertIn('id="anim-sel-effekte"', text)

    def test_speichern_haelt_die_grenzen_des_registers(self):
        antwort = self.client.post(reverse('settings_effekte'), {
            'effekte_default_pipeline': 'kleid_wind', 'effekte_default_model': 'Female2',
            'effekte_default_animation': '/api/character/bvh/Walk/02_02/',
            'effekte_windrichtung': 'vorn', 'effekte_video_fps': '24',
            'effekte_video_width': '99999', 'effekte_video_height': 'quatsch',
            'effekte_wind': '2.5'})
        self.assertEqual(antwort.status_code, 302)
        s = AppSettings.load()
        self.assertEqual((s.effekte_default_pipeline, s.effekte_windrichtung,
                          s.effekte_video_fps, s.effekte_wind),
                         ('kleid_wind', 'vorn', 24, 2.5))
        self.assertEqual(s.effekte_video_width, 3840)      # gekappt
        self.assertEqual(s.effekte_video_height, 900)      # unlesbar -> bleibt
        self.assertEqual(s.effekte_default_animation, '/api/character/bvh/Walk/02_02/')

    def test_effekteseite_traegt_die_vorgaben(self):
        s = AppSettings.load()
        s.effekte_default_animation = '/api/character/bvh/Walk/02_02/'
        s.effekte_video_fps = 24
        s.effekte_wind = 7.5
        s.save()
        antwort = self.client.get(reverse('effekte'))
        text = antwort.content.decode('utf-8')
        self.assertIn('data-vorgabe-pipeline="figur_def"', text)
        self.assertIn('data-vorgabe-modell="Female2"', text)
        self.assertIn('data-vorgabe-animation="/api/character/bvh/Walk/02_02/"', text)
        self.assertIn('id="figur_fps" name="fps"', text)
        self.assertRegex(text, r'id="figur_fps" name="fps"[^>]*value="24"')
        self.assertRegex(text, r'id="figur_wind" name="wind"[^>]*value="7.5"')
        self.assertRegex(text, r'id="effekt_fps"|id="effekt_bilder"')

    def test_unbekanntes_modell_wird_nicht_vorgewaehlt(self):
        s = AppSettings.load()
        s.effekte_default_model = 'Nirgends'
        s.effekte_default_pipeline = 'quatsch'
        s.effekte_video_width = 10   # unter der Feldgrenze
        s.save()
        v = Effektvorgaben(s)
        self.assertEqual((v.modell(), v.pipeline()), ('', 'figur_def'))
        karte = {f['name']: f for f in v.karte(Figurparameter.karte())}
        self.assertEqual(karte['breite']['vorgabe'], 320)
        self.assertEqual(karte['bilder']['vorgabe'], 120)   # unberührt
        antwort = self.client.get(reverse('effekte'))
        self.assertIn('data-vorgabe-modell=""', antwort.content.decode('utf-8'))
