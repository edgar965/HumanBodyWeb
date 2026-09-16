# -*- coding: utf-8 -*-
u"""Hautbild — die Hauttextur des Films mit gezeichneter Braue.

WARUM (Edgar, 17.09.2026: „baue: der pyrender-Film (er hat weder Textur
noch Augen/Wimpern)"): Der Film bekommt die Braue nicht über einen Shader,
sondern als Bild — dasselbe Fenster, dieselbe Mischung wie im Browser.
Hier ohne die MB-Lab-Texturen (Kunstbogen, Fläche statt Albedo):

1. Die Reglertabelle ist die des Browsers (`Brauenhaut.FELDER`), Meter
   werden Millimeter.
2. Ohne eigene Hautfarbe gilt die der Körperart (linear, mit 1/2,2
   angehoben wie `hautfarbe.js`); eine gesetzte Farbe gewinnt.
3. Die Braue liegt im Fenster des Bogens — außerhalb bleibt der Grund
   Pixel für Pixel, innerhalb wird es dunkler.
4. Verdrahtung: Szene → Auftrag → `Filmlauf` → `Hbfilm` → `Filmrender`.

Sabotage-Gegenprobe: in `Hautbild.mit_brauen` `(1 - v1)` durch `v0`
ersetzen → Fall 3 rot (Braue außerhalb des Fensters).
"""
import re
from unittest import mock

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.brauenbogen import Brauenbogen
from core.dienste.brauendecal import Brauendecal
from core.dienste.hautbild import Hautbild
from core.tests.unit._pruefablage import Pruefablage

VIEWER = settings.BASE_DIR / 'static' / 'viewer'
MODELPHYSIK = settings.BASE_DIR / 'TheatreJS' / 'ModelPhysik'


class HautbildTest(SimpleTestCase):

    databases = set()

    @staticmethod
    def kunstbogen():
        t = np.linspace(0, 1, 20)
        return {'fassung': Brauenbogen.FASSUNG, 'fenster': [0.375, 0.125, 0.625, 0.25],
                'mm_je_uv': 800.0, 'form': [2048, 2048],
                'links': [[float(0.48 - 0.06 * x), float(0.19 + 0.02 * x)] for x in t],
                'rechts': [[float(0.52 + 0.06 * x), float(0.19 + 0.02 * x)] for x in t]}

    def test_reglertabelle_wie_im_browser(self):
        quelle = (VIEWER / 'gemeinsam' / 'brauenhaut.js').read_text(encoding='utf-8')
        block = quelle[quelle.index('static FELDER = {'):]
        block = block[:block.index('};')]
        js = {feld: (name, int(faktor)) for feld, name, faktor
              in re.findall(r"(brauen\w*): \['(\w+)', (\d+)\]", block)}
        self.assertEqual(js, Hautbild.BRAUENFELDER)
        regler = Hautbild.regler({'brauen': '#102030', 'brauen_lage': 0.0125,
                                  'brauen_staerke': 0.64, 'haut': '#ffffff'})
        self.assertEqual((regler['farbe'], regler['lage'], regler['haar_laenge']),
                         ('#102030', 12.5, 0.64))
        self.assertEqual(Hautbild.regler({})['dichte'], Brauendecal.VORGABE['dichte'])

    def test_hautfarbe_der_koerperart_und_eigene(self):
        from humanbody_core import MorphData
        asiatisch = MorphData.SKIN_COLORS['Asian']
        erwartet = tuple(int(round(255 * c ** (1 / 2.2))) for c in asiatisch)
        self.assertEqual(Hautbild.hautfarbe({}, 'Female_Asian'), erwartet)
        self.assertEqual(Hautbild.hautfarbe({'haut': ''}, 'Male_Asian'), erwartet)
        self.assertEqual(Hautbild.hautfarbe({'haut': '#102030'}, 'Female_Asian'),
                         (16, 32, 48))
        self.assertEqual(Hautbild.hautfarbe({}, 'Quatsch'),
                         Hautbild.hautfarbe({}, 'Female_Caucasian'))
        self.assertEqual(Hautbild.geschlecht('Male_Latin'), 'male')
        self.assertIsNone(Hautbild.albedo({'haut_textur': '../etc'}))
        with mock.patch.object(Hautbild, 'GROESSE', 8):
            grund = Hautbild.grund({}, 'Female_Caucasian')
        self.assertEqual(grund.shape, (8, 8, 3))
        self.assertEqual(tuple(grund[3, 3]), Hautbild.hautfarbe({}, 'Female_Caucasian'))
        getoent = Hautbild.toenen(np.full((2, 2, 3), 200, dtype=np.uint8), (255, 0, 0))
        self.assertEqual(int(getoent[0, 0, 0]), 200)
        self.assertEqual(int(getoent[0, 0, 1]), 0)

    def test_braue_liegt_im_fenster(self):
        ablage = Pruefablage.ordner('hautbild_')
        ordner = ablage.__enter__()
        self.addCleanup(ablage.__exit__, None, None, None)
        laden = mock.patch.object(Brauenbogen, 'laden', return_value=self.kunstbogen())
        breite = mock.patch.object(Brauendecal, 'BREITE', 512)
        ort = mock.patch.object(Brauendecal, 'ORDNER',
                                Brauenbogen.ORDNER.__class__(ordner))
        for patch in (laden, breite, ort):
            patch.start()
            self.addCleanup(patch.stop)
        grund = np.full((1024, 1024, 3), 200, dtype=np.uint8)
        bild = Hautbild.mit_brauen(grund, 'female',
                                   Brauendecal.regler({'farbe': '#000000'}))
        u0, v0, u1, v1 = self.kunstbogen()['fenster']
        x0, x1 = int(u0 * 1024), int(u1 * 1024)
        y0, y1 = int((1 - v1) * 1024), int((1 - v0) * 1024)
        aussen = np.ones((1024, 1024), dtype=bool)
        aussen[y0:y1, x0:x1] = False
        self.assertTrue(np.array_equal(bild[aussen], grund[aussen]), 'außen gleich')
        innen = bild[y0:y1, x0:x1]
        dunkel = int((innen.min(axis=2) < 120).sum())
        self.assertGreater(dunkel, 50, 'Härchen im Fenster')
        self.assertLess(dunkel, innen.shape[0] * innen.shape[1] // 2)

    def test_verdrahtung(self):
        szene = (VIEWER / 'scene' / 'figurvideo.js').read_text(encoding='utf-8')
        self.assertIn('details: inst.details || {}', szene)
        dienst = (settings.BASE_DIR / 'core' / 'dienste' / 'figurvideo.py'
                  ).read_text(encoding='utf-8')
        self.assertIn("'details': dict(daten.get('details') or {})", dienst)
        lauf = (MODELPHYSIK / 'filmlauf.py').read_text(encoding='utf-8')
        self.assertIn("details=self.auftrag.get('details') or {}", lauf)
        film = (MODELPHYSIK / 'hbfilm.py').read_text(encoding='utf-8')
        self.assertIn('Filmhaut.anlegen(self.teile[0], details, geschlecht, body_type)',
                      film)
        render = (MODELPHYSIK / 'filmrender.py').read_text(encoding='utf-8')
        self.assertIn('haut.netze(ecken, senkrechten, dreiecke)', render)
