# -*- coding: utf-8 -*-
u"""Modelle und UMA-Figuren aus dem Dialog umbenennen und löschen.

WARUM (06.09.2026, Edgar): „Mach auch Möglichkeiten zum Umbenennen und
Löschen der Modelle aus dem Dialog." Beides fasst Dateien auf der Platte an,
deshalb wird hier genau geprüft, WAS passiert:

1. Eine UMA-Figur ist ein Paar aus GLB und Beipackzettel — beide wandern mit.
2. Zeigt `aktuell.json` auf sie, wird der Zeiger nachgeführt. Sonst zeigte er
   ins Leere, Roomguest nähme die jüngste Datei und warnte nur im Log
   (`Figuren/VERTRAG.md`).
3. Zeigt der Zeiger auf eine ANDERE Figur, bleibt er unangetastet.
4. Ein Name, der aus dem Ordner ausbrechen will, wird abgewiesen.
5. Gelöscht wird genau die eine Figur, nichts daneben.

Gearbeitet wird auf einem Wegwerf-Katalog unter `ProjektTemp/`; weder
`Figuren/` noch `HumanBody/data/` werden angefasst.

Aufruf: python manage.py test core.tests.component.test_katalogverwaltung
"""
import json
import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse


class KatalogverwaltungTest(TestCase):

    def setUp(self):
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        self.wurzel = Path(tempfile.mkdtemp(prefix='katalogpflege_', dir=str(basis)))
        self.addCleanup(shutil.rmtree, self.wurzel, True)
        self.katalog = self.wurzel / 'figuren'
        (self.katalog / 'uma').mkdir(parents=True)
        self.modelle = self.wurzel / 'models'
        self.modelle.mkdir()
        umschaltung = override_settings(FIGUREN_KATALOG=self.katalog,
                                        HUMANBODY_MODELS_DIR=self.modelle)
        umschaltung.enable()
        self.addCleanup(umschaltung.disable)

    # -- Hilfen ---------------------------------------------------------------

    def _figur(self, name, mit_zettel=True):
        (self.katalog / 'uma' / ('%s.glb' % name)).write_bytes(b'glTF-Attrappe')
        if mit_zettel:
            (self.katalog / 'uma' / ('%s.json' % name)).write_text(
                json.dumps({'name': name, 'hoehe_m': 1.7}), encoding='utf-8')

    def _zeiger(self, inhalt):
        (self.katalog / 'aktuell.json').write_text(
            json.dumps(inhalt), encoding='utf-8')

    def _zeiger_lesen(self):
        pfad = self.katalog / 'aktuell.json'
        return json.loads(pfad.read_text(encoding='utf-8')) if pfad.exists() else {}

    def _modell(self, name):
        (self.modelle / ('%s.json' % name)).write_text(
            json.dumps({'body_type': 'Female_Caucasian'}), encoding='utf-8')

    def _post(self, route, daten):
        return self.client.post(reverse(route), data=json.dumps(daten),
                                content_type='application/json')

    def _da(self, *namen):
        return sorted(p.name for p in (self.katalog / 'uma').iterdir()
                      if p.name in namen or True)

    # -- UMA umbenennen -------------------------------------------------------

    def test_umbenennen_nimmt_den_zettel_mit(self):
        self._figur('Alt')
        antwort = self._post('katalog_uma_umbenennen',
                             {'alt': 'Alt.glb', 'neu': 'Neu.glb'})
        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertEqual(antwort.json()['name'], 'Neu.glb')
        self.assertEqual(self._da(), ['Neu.glb', 'Neu.json'])
        # Der Zettel nennt danach den neuen Namen.
        zettel = json.loads((self.katalog / 'uma' / 'Neu.json').read_text(encoding='utf-8'))
        self.assertEqual(zettel['name'], 'Neu')
        self.assertEqual(zettel['hoehe_m'], 1.7)      # der Rest bleibt

    def test_umbenennen_zieht_den_zeiger_nach(self):
        self._figur('Alt')
        self._zeiger({'uma': 'Alt.glb', 'humanbody': 'Rig2.glb'})
        self._post('katalog_uma_umbenennen', {'alt': 'Alt.glb', 'neu': 'Neu.glb'})
        self.assertEqual(self._zeiger_lesen(),
                         {'uma': 'Neu.glb', 'humanbody': 'Rig2.glb'})

    def test_zeiger_auf_eine_andere_figur_bleibt_unberuehrt(self):
        self._figur('Alt')
        self._figur('Andere')
        self._zeiger({'uma': 'Andere.glb'})
        self._post('katalog_uma_umbenennen', {'alt': 'Alt.glb', 'neu': 'Neu.glb'})
        self.assertEqual(self._zeiger_lesen(), {'uma': 'Andere.glb'})

    def test_umbenennen_ueberschreibt_keine_vorhandene_figur(self):
        self._figur('Alt')
        self._figur('Belegt')
        antwort = self._post('katalog_uma_umbenennen',
                             {'alt': 'Alt.glb', 'neu': 'Belegt.glb'})
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('Belegt', antwort.json()['error'])
        self.assertTrue((self.katalog / 'uma' / 'Alt.glb').exists())

    def test_ausbruch_aus_dem_ordner_wird_abgewiesen(self):
        self._figur('Alt')
        for neu in ('../weg.glb', 'unter/weg.glb', '..\\weg.glb'):
            antwort = self._post('katalog_uma_umbenennen',
                                 {'alt': 'Alt.glb', 'neu': neu})
            self.assertEqual(antwort.status_code, 400, neu)
        self.assertTrue((self.katalog / 'uma' / 'Alt.glb').exists())

    def test_nur_glb_dateien(self):
        antwort = self._post('katalog_uma_umbenennen',
                             {'alt': 'Alt.txt', 'neu': 'Neu.txt'})
        self.assertEqual(antwort.status_code, 400)

    # -- UMA löschen ----------------------------------------------------------

    def test_loeschen_entfernt_glb_und_zettel_und_sonst_nichts(self):
        self._figur('Weg')
        self._figur('Bleibt')
        antwort = self._post('katalog_uma_loeschen', {'name': 'Weg.glb'})
        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertEqual(self._da(), ['Bleibt.glb', 'Bleibt.json'])

    def test_loeschen_raeumt_den_zeiger_ab(self):
        self._figur('Weg')
        self._zeiger({'uma': 'Weg.glb', 'humanbody': 'Rig2.glb'})
        self._post('katalog_uma_loeschen', {'name': 'Weg.glb'})
        self.assertEqual(self._zeiger_lesen(), {'humanbody': 'Rig2.glb'})

    def test_loeschen_einer_figur_ohne_zettel_geht_auch(self):
        self._figur('Nackt', mit_zettel=False)
        antwort = self._post('katalog_uma_loeschen', {'name': 'Nackt.glb'})
        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertEqual(self._da(), [])

    def test_unbekannte_figur_meldet_sich(self):
        antwort = self._post('katalog_uma_loeschen', {'name': 'GibtEsNicht.glb'})
        self.assertEqual(antwort.status_code, 400)

    # -- HumanBody-Modelle ----------------------------------------------------

    def test_modell_umbenennen_und_loeschen(self):
        self._modell('Alt')
        antwort = self._post('katalog_modell_umbenennen',
                             {'alt': 'Alt', 'neu': 'Neu'})
        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertTrue((self.modelle / 'Neu.json').exists())
        self.assertFalse((self.modelle / 'Alt.json').exists())
        antwort = self._post('katalog_modell_loeschen', {'name': 'Neu'})
        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertEqual(list(self.modelle.iterdir()), [])

    def test_die_szenendatei_daneben_bleibt_liegen(self):
        u"""`<name>.scene.json` ist eine Szene, kein Modell."""
        self._modell('Figur')
        (self.modelle / 'Figur.scene.json').write_text('{}', encoding='utf-8')
        self._post('katalog_modell_loeschen', {'name': 'Figur'})
        self.assertEqual([p.name for p in self.modelle.iterdir()],
                         ['Figur.scene.json'])

    def test_modell_ausbruch_wird_abgewiesen(self):
        self._modell('Alt')
        antwort = self._post('katalog_modell_loeschen', {'name': '../../geheim'})
        self.assertEqual(antwort.status_code, 400)
        self.assertTrue((self.modelle / 'Alt.json').exists())

    # -- Eingaben -------------------------------------------------------------

    def test_ohne_namen_kein_vorgang(self):
        self.assertEqual(self._post('katalog_uma_loeschen', {}).status_code, 400)
        self.assertEqual(self._post('katalog_uma_umbenennen',
                                    {'alt': 'X.glb'}).status_code, 400)

    def test_gleicher_name_ist_kein_fehler(self):
        self._figur('Gleich')
        antwort = self._post('katalog_uma_umbenennen',
                             {'alt': 'Gleich.glb', 'neu': 'Gleich.glb'})
        self.assertEqual(antwort.status_code, 200)
        self.assertTrue(antwort.json()['unveraendert'])

    def test_nur_post(self):
        self.assertEqual(self.client.get(reverse('katalog_uma_loeschen')).status_code, 405)
