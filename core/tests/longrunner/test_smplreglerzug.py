# -*- coding: utf-8 -*-
"""Der Reglerzug einer SMPL-X-Figur ohne Maße und Ablage (25.11.2026, Edgar: „alle regler unter 0,2 s“; bis dahin 13,5 s je Zug).

1. `nur: 'form'` gibt dieselben Punkte, dasselbe Skelett und denselben Namen wie die volle Antwort; gemessen und abgelegt wird nichts, nur die Betas liegen da.
2. `Smplvarianten.sicherstellen` baut daraus OBJ und YAML nach; danach trägt die volle Antwort die Maße.
3. Das OBJ ist zeilengleich mit einer Ausgabe je Zahl (`Koerperablage` schreibt seit 25.11.2026 aus Listen).
4. Der Maße-Endpunkt: gemessen 200, unbekannt 404.

Die Ablage ist auf einen Wegwerfordner umgebogen. Langläufer: eine Messung dauert rund 5 s. Sabotage-Gegenprobe (nicht gefahren): in `form` die Betas nicht schreiben → Fall 2 rot;
in `_netz_schreiben` `%.5f` → Fall 3 rot. Geschrieben, nicht gelaufen (nur auf Ansage).
"""
import base64
import json
import os
import shutil
import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import torch
from django.conf import settings
from django.test import RequestFactory, SimpleTestCase

from ...dienste.smplvarianten import Smplvarianten
from ...dienste.smplxrig import Smplxrig


@unittest.skipUnless(torch.cuda.is_available() and Smplxrig.vorhanden('female'), 'braucht die Grafikkarte und die SMPL-X-Modelle')
class SmplreglerzugTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = tempfile.mkdtemp(prefix='smplzug_', dir=str(Path(settings.BASE_DIR).parent / 'ProjektTemp'))
        self.addCleanup(shutil.rmtree, self.ordner, True)
        for name, ersatz in (('ordner', staticmethod(lambda: self.ordner)), ('_erzeugt', {}), ('_segmentierung', None)):
            flicken = mock.patch.object(Smplvarianten, name, ersatz)
            flicken.start()
            self.addCleanup(flicken.stop)

    @staticmethod
    def zug(**werte):
        from ...api.smplform import Smplformung

        anfrage = RequestFactory().post('/', json.dumps({'geschlecht': 'female', **werte}), content_type='application/json')
        antwort = Smplformung._formen(anfrage)
        return json.loads(antwort.content)

    def test_1_nur_form(self):
        kurz, voll = self.zug(groesse=30, armlaenge=20, nur='form'), self.zug(groesse=30, armlaenge=20)
        soll = struct.pack('<%df' % (3 * len(voll['punkte'])), *[x for p in voll['punkte'] for x in p])
        self.assertEqual(base64.b64decode(kurz['punkte']), soll)
        for feld in ('name', 'betas', 'regler', 'hoehe', 'skelett'):
            self.assertEqual(kurz[feld], voll[feld], feld)
        self.assertNotIn('dreiecke', kurz)
        self.assertEqual(voll['masse'], {})
        self.assertEqual(sorted(d for d in os.listdir(self.ordner) if d.startswith(kurz['name'])), [kurz['name'] + Smplvarianten.BETAS])
        self.assertTrue(Smplvarianten.vorhanden(kurz['name']))

    def test_2_bis_4_nachholen(self):
        from ...api.smplfigur import Smplfigur

        name = self.zug(fuelle=40, nur='form')['name']
        self.assertEqual(Smplfigur._masse(None, 'smplx_f_gibtesnicht').status_code, 404)
        masse = json.loads(Smplfigur._masse(None, name).content)['masse']
        self.assertGreater(masse['waist'], 0)
        for endung in ('.obj', '.yaml'):
            self.assertTrue(os.path.isfile(os.path.join(self.ordner, name + endung)), endung)
        voll = self.zug(fuelle=40)
        self.assertEqual(voll['masse'], masse)
        punkte = [z.split()[1:] for z in Path(self.ordner, name + '.obj').read_text(encoding='utf-8').splitlines() if z.startswith('v ')]
        self.assertEqual(punkte, [['%.6f' % x for x in p] for p in voll['punkte']])
