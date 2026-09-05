# -*- coding: utf-8 -*-
u"""Umabauer und die Bau-Endpunkte — mit einer Unity-Attrappe (06.09.2026).

Die Attrappe ist eine `.cmd`, die wie der Exporter die Argumente liest: bei
`-name X` legt sie `X.glb` in den Katalog, bei `-rassenliste <pfad>` schreibt
sie eine Rassenliste. Ein Lauf braucht rund zwei Sekunden (`ping` als Pause),
damit „belegt" prüfbar ist. Alles unter `ProjektTemp/`, nichts hier fasst das
echte Unity oder den echten Katalog an.
"""
import json
import os
import shutil
import tempfile
import time
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from core.dienste.umabauer import Umabauer, UmabauerBelegt, UmabauerFehlt

ATTRAPPE = u'''@echo off
setlocal
set NAME=
:schleife
if "%%~1"=="" goto fertig
if "%%~1"=="-name" set NAME=%%~2
if "%%~1"=="-rassenliste" echo %(rassen)s> "%%~2"
shift
goto schleife
:fertig
ping -n 3 127.0.0.1 > nul
if defined NAME echo glb> "%(katalog)s\\%%NAME%%.glb"
exit /b 0
'''


class UmabauerTest(SimpleTestCase):
    u"""Dienst und Endpunkte gegen die Attrappe."""

    databases = []
    WARTE_S = 15

    def setUp(self):
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        self.wurzel = Path(tempfile.mkdtemp(prefix='umabauer_', dir=str(basis)))
        self.katalog = self.wurzel / 'Figuren'
        (self.katalog / 'uma').mkdir(parents=True)
        self.projekt = self.wurzel / 'UMAProject'
        self.projekt.mkdir()
        self.unity = self.wurzel / 'unity.cmd'
        rassen = ('[{"name": "ElfFemale30", "kompatibel": ["Human Female 3.0"]}, '
                  '{"name": "Human Female 3.0", "kompatibel": []}, "HumanMale"]')
        self.unity.write_text(ATTRAPPE % {'katalog': str(self.katalog / 'uma'), 'rassen': rassen},
                              encoding='utf-8')
        Umabauer._laeufe.clear()
        Umabauer._aktiv = None
        self.umschaltung = override_settings(UNITY_EXE=self.unity, UMA_PROJEKT=self.projekt,
                                             FIGUREN_KATALOG=self.katalog, UMA_BAU_LOGS=self.wurzel / 'logs')
        self.umschaltung.enable()

    def tearDown(self):
        self._abwarten()
        self.umschaltung.disable()
        shutil.rmtree(self.wurzel, ignore_errors=True)

    def _abwarten(self, name=None):
        u"""Bis kein Lauf mehr läuft; liefert den letzten Stand des genannten Laufs."""
        stand = None
        for _ in range(self.WARTE_S * 10):
            laeuft = False
            for lauf in list(Umabauer._laeufe):
                s = Umabauer.stand(lauf)
                if s['laeuft']:
                    laeuft = True
                if lauf == name:
                    stand = s
            if not laeuft:
                return stand
            time.sleep(0.1)
        self.fail('Attrappe läuft nach %d s noch' % self.WARTE_S)

    # ---------------------------------------------------------------- Dienst

    def test_bauen_legt_die_datei_in_den_katalog(self):
        start = Umabauer.bauen('Human Female 3.0')
        self.assertEqual(start['name'], 'Uma_HumanFemale30')
        self.assertTrue(start['laeuft'])
        ende = self._abwarten('Uma_HumanFemale30')
        self.assertEqual(ende['exit'], 0)
        self.assertEqual(ende['datei'], 'Uma_HumanFemale30.glb')
        self.assertTrue((self.katalog / 'uma' / 'Uma_HumanFemale30.glb').is_file())
        self.assertTrue((self.wurzel / 'logs' / 'unity_Uma_HumanFemale30.json').is_file())
        # Ein neuer Serverprozess kennt den Lauf nur aus dieser Ablage.
        Umabauer._laeufe.clear()
        self.assertEqual(Umabauer.stand('Uma_HumanFemale30')['datei'], 'Uma_HumanFemale30.glb')

    def test_zweiter_lauf_waehrend_des_ersten_ist_belegt(self):
        Umabauer.bauen('Human Female 3.0')
        with self.assertRaises(UmabauerBelegt):
            Umabauer.bauen('Human Male 3.0')

    def test_ohne_unity_kommt_fehlt(self):
        with override_settings(UNITY_EXE=self.wurzel / 'gibtsnicht.exe'):
            with self.assertRaises(UmabauerFehlt):
                Umabauer.bauen('Human Female 3.0')

    def test_name_aus_der_rasse_und_ungueltige_namen(self):
        self.assertEqual(Umabauer.name_fuer('Anime Elf Female 3.0'), 'Uma_AnimeElfFemale30')
        with self.assertRaises(ValueError):
            Umabauer.bauen('Human Male 3.0', name='../raus')
        with self.assertRaises(ValueError):
            Umabauer.bauen('')

    def test_rassenliste_kommt_aus_unity(self):
        self.assertIsNone(Umabauer.rassen())
        Umabauer.rassen_ermitteln()
        self._abwarten(Umabauer.RASSENLAUF)
        self.assertEqual(Umabauer.rassen(), ['ElfFemale30', 'Human Female 3.0', 'HumanMale'])
        self.assertEqual(Umabauer.rassen_details()['ElfFemale30'], ['Human Female 3.0'])
        self.assertEqual(Umabauer.rassen_details()['HumanMale'], [])

    # ------------------------------------------------------------- Endpunkte

    def test_endpunkte_bauen_stand_und_rassen(self):
        antwort = self.client.get('/api/character/uma-rassen/')
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.json(), {'rassen': [], 'ermittelt': False, 'figuren': []})

        antwort = self.client.post('/api/character/uma-figur/bauen/', json.dumps({'rasse': 'Human Male 3.0'}),
                                   content_type='application/json')
        self.assertEqual(antwort.status_code, 202, antwort.content)
        name = antwort.json()['name']
        self.assertEqual(name, 'Uma_HumanMale30')

        antwort = self._bauen('Human Female 3.0')
        self.assertEqual(antwort.status_code, 409)

        self._abwarten(name)
        stand = self.client.get('/api/character/uma-figur/bauen/%s/stand/' % name).json()
        self.assertFalse(stand['laeuft'])
        self.assertEqual(stand['datei'], 'Uma_HumanMale30.glb')
        self.assertEqual(self.client.get('/api/character/uma-figur/bauen/nix/stand/').status_code, 404)

        figuren = self.client.get('/api/character/uma-rassen/').json()['figuren']
        self.assertEqual([f['name'] for f in figuren], ['Uma_HumanMale30.glb'])

    def test_endpunkt_ohne_rasse_und_ohne_unity(self):
        antwort = self.client.post('/api/character/uma-figur/bauen/', '{}', content_type='application/json')
        self.assertEqual(antwort.status_code, 400)
        with override_settings(UNITY_EXE=self.wurzel / 'gibtsnicht.exe'):
            antwort = self._bauen('Human Male 3.0')
        self.assertEqual(antwort.status_code, 503)

    def _bauen(self, rasse):
        return self.client.post('/api/character/uma-figur/bauen/', json.dumps({'rasse': rasse}),
                                content_type='application/json')
