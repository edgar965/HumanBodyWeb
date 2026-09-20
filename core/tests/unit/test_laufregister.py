# -*- coding: utf-8 -*-
"""`Laufregister` (GarmentCode/laufregister.py) und der Endpunkt
`/api/garmentcode/abbrechen/`: der Abbrechen-Knopf beendet den
Simulationsprozess zur Anfrage-Kennung.

Edgar, 20.09.2026: „bei 2D+3D bauen soll es einen Abbrechen-Button geben."
Statt `drapierlauf.py` laeuft hier ein schlafender Python-Prozess, der das
Kennzeichen nur in seiner Befehlszeile traegt (letztes Argument) — so
prueft der Test die Kette PID-Datei -> psutil -> kill an einem echten
Prozess, ohne Warp. Ein Prozess OHNE Kennzeichen darf nicht beendet werden:
eine Prozessnummer wird wiederverwendet.
"""

import os
import shutil
import subprocess
import sys
from unittest import mock

from django.conf import settings
from django.test import Client, SimpleTestCase
from GarmentCode.laufregister import Laufregister

WEGWERF = settings.BASE_DIR / '_wegwerf' / 'test_laufregister'


class LaufregisterTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        if WEGWERF.is_dir():
            shutil.rmtree(WEGWERF)
        self.ordner = mock.patch.object(Laufregister, 'ORDNER', str(WEGWERF))
        self.ordner.start()
        self.prozesse = []

    def tearDown(self):
        self.ordner.stop()
        for prozess in self.prozesse:
            if prozess.poll() is None:
                prozess.kill()
                prozess.wait(timeout=5)
        if WEGWERF.is_dir():
            shutil.rmtree(WEGWERF)

    def _schlaefer(self, kennzeichen=True):
        befehl = [sys.executable, '-c', 'import time; time.sleep(60)']
        if kennzeichen:
            befehl.append(Laufregister.KENNZEICHEN)
        prozess = subprocess.Popen(befehl, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.prozesse.append(prozess)
        return prozess

    def test_angemeldeter_lauf_wird_beendet_und_als_abgebrochen_gemeldet(self):
        prozess = self._schlaefer()
        with Laufregister.lauf('abbruch-test-0001'):
            pfad = Laufregister.anmelden(prozess)
            self.assertTrue(os.path.isfile(pfad))
            self.assertEqual(open(pfad, encoding='utf-8').read(), str(prozess.pid))
            self.assertEqual(Laufregister.abbrechen('abbruch-test-0001'), 'beendet')
            self.assertIsNotNone(prozess.wait(timeout=10))
            self.assertTrue(Laufregister.abmelden())
        self.assertFalse(os.path.exists(pfad))
        self.assertEqual(os.listdir(WEGWERF), [])

    def test_ohne_abbruch_meldet_abmelden_nein(self):
        prozess = self._schlaefer()
        with Laufregister.lauf('abbruch-test-0002'):
            Laufregister.anmelden(prozess)
            self.assertFalse(Laufregister.abmelden())
        self.assertEqual(os.listdir(WEGWERF), [])

    def test_fremder_prozess_unter_der_nummer_bleibt_am_leben(self):
        prozess = self._schlaefer(kennzeichen=False)
        with Laufregister.lauf('abbruch-test-0003'):
            Laufregister.anmelden(prozess)
            self.assertEqual(Laufregister.abbrechen('abbruch-test-0003'), 'fremd')
        self.assertIsNone(prozess.poll())

    def test_ohne_kennung_oder_datei_ist_es_kein_lauf(self):
        self.assertEqual(Laufregister.abbrechen('abbruch-test-0004'), 'kein_lauf')
        self.assertEqual(Laufregister.abbrechen('kurz'), 'kein_lauf')
        with Laufregister.lauf(None):
            self.assertIsNone(Laufregister.kennung())
            self.assertIsNone(Laufregister.anmelden(mock.Mock(pid=1)))
        with Laufregister.lauf('böse/../kennung'):
            self.assertIsNone(Laufregister.kennung())

    def test_der_endpunkt_prueft_die_kennung_und_meldet_das_ergebnis(self):
        self.assertEqual(Client().post('/api/garmentcode/abbrechen/', {'anfrage': 'x'}).status_code, 400)
        antwort = Client().post('/api/garmentcode/abbrechen/', {'anfrage': 'abbruch-test-0005'})
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.json()['ergebnis'], 'kein_lauf')
        self.assertEqual(Client().get('/api/garmentcode/abbrechen/').status_code, 405)

    def test_die_beiden_langen_endpunkte_melden_die_kennung_an(self):
        wurzel = settings.BASE_DIR / 'core' / 'api'
        for datei in ('garmentcode.py', 'garmentgemeinsam.py'):
            quelle = open(wurzel / datei, encoding='utf-8').read()
            self.assertIn("with Laufregister.lauf(request.POST.get('anfrage')):", quelle, datei)
        drapierung = open(settings.ASSETS_ROOT / 'GarmentCode' / 'drapierung.py', encoding='utf-8').read()
        self.assertIn('Laufregister.anmelden(prozess)', drapierung)
        self.assertIn("raise DrapierFehler('Drapierung abgebrochen')", drapierung)
