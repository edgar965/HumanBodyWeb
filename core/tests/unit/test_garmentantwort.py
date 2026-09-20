# -*- coding: utf-8 -*-
"""`Garmentantwort`: die Antwort eines langen Laufs überlebt den Server.

Edgar, 20.09.2026: „Stoff drapieren — Failed to fetch". Der Dev-Server
lud während der Drapierung neu (109-mal an dem Abend); der alte Prozess
rechnete fertig, die Antwort kam nie an.

Sabotage-Gegenprobe: `ablegen` ohne `os.replace` (direkt schreiben) lässt
`test_eine_halbe_datei_wird_nie_gelesen` grün bleiben — deshalb prüft der
Test die `.neu`-Datei nicht, sondern dass `lesen` erst nach dem Ablegen
etwas liefert; `KENNUNG` auf `.*` macht `test_nur_eine_saubere_kennung`
rot; die drei Endpunkte ohne `Garmentantwort.ablegen` machen
`test_die_drei_langen_endpunkte_legen_ab` rot.
"""

import os
import shutil
import time
from unittest import mock

from django.conf import settings
from django.test import Client, SimpleTestCase

from core.api.garmentantwort import Garmentantwort

WEGWERF = settings.BASE_DIR / '_wegwerf' / 'test_garmentantwort'


class GarmentantwortTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        if WEGWERF.is_dir():
            shutil.rmtree(WEGWERF)
        self.ordner = mock.patch.object(Garmentantwort, 'ORDNER', str(WEGWERF))
        self.ordner.start()

    def tearDown(self):
        self.ordner.stop()
        if WEGWERF.is_dir():
            shutil.rmtree(WEGWERF)

    def test_abgelegt_wird_gelesen_und_ueber_den_endpunkt_geholt(self):
        kennung = 'abcd1234-efgh-5678'
        self.assertIsNone(Garmentantwort.lesen(kennung))
        self.assertEqual(Client().get('/api/garmentcode/antwort/%s/' % kennung).status_code, 404)
        pfad = Garmentantwort.ablegen(kennung, {'punkte': 3, 'rig_url': '/x/'})
        self.assertTrue(pfad and os.path.isfile(pfad))
        self.assertEqual(Garmentantwort.lesen(kennung), {'punkte': 3, 'rig_url': '/x/'})
        antwort = Client().get('/api/garmentcode/antwort/%s/' % kennung)
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.json()['punkte'], 3)
        self.assertFalse(os.path.exists(pfad + '.neu'))            # fertig umbenannt

    def test_nur_eine_saubere_kennung(self):
        for schlecht in (None, '', 'kurz', '../etc', 'a b c d e f g h', 'x' * 65):
            self.assertIsNone(Garmentantwort.ablegen(schlecht, {'a': 1}), schlecht)
            self.assertIsNone(Garmentantwort.lesen(schlecht), schlecht)
        self.assertEqual(Client().get('/api/garmentcode/antwort/kurz/').status_code, 400)
        self.assertFalse(WEGWERF.is_dir() and os.listdir(WEGWERF))

    def test_alte_antworten_werden_geraeumt(self):
        alt = Garmentantwort.ablegen('alte-antwort-0001', {'a': 1})
        neu = Garmentantwort.ablegen('neue-antwort-0001', {'a': 2})
        vor = time.time() - Garmentantwort.HALTEN_S - 60
        os.utime(alt, (vor, vor))
        self.assertEqual(Garmentantwort.aufraeumen(), 1)
        self.assertFalse(os.path.exists(alt))
        self.assertTrue(os.path.exists(neu))

    def test_die_drei_langen_endpunkte_legen_ab(self):
        wurzel = settings.BASE_DIR / 'core' / 'api'
        for datei, wieoft in (('garmentcode.py', 2), ('garmentgemeinsam.py', 1)):
            quelle = open(wurzel / datei, encoding='utf-8').read()
            self.assertEqual(quelle.count("Garmentantwort.ablegen(request.POST.get('anfrage')"), wieoft, datei)
        for modul in ('scene/garmentcode_drapieren.js', 'scene/garmentcode_schnitt.js',
                      'scene/garmentcode_gemeinsam.js'):
            quelle = open(settings.BASE_DIR / 'static' / 'viewer' / modul, encoding='utf-8').read()
            self.assertIn('Antwortnachholen.formular(', quelle, modul)
            self.assertNotIn('Fristabruf.formular(', quelle, modul)
