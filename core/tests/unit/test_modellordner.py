# -*- coding: utf-8 -*-
"""Modellordner — Ordner umbenennen und löschen (Kontextmenü im Dialog „Charakter hinzufügen“, 18.10.2026).

Edgar: „Kontextmenü für die Ordner fehlt noch, die sollen löschen, umbenennen enthalten“. Ein Ordner ist eine Zuordnung, kein Verzeichnis:
1. Umbenennen nimmt die Modelle des Ordners mit; die anderen Ordner und Reiter bleiben, wie sie sind.
2. Umbenennen auf einen vorhandenen Namen (ohne Groß-/Kleinschreibung) wird abgelehnt; nur die Schreibweise ändern geht.
3. Löschen nimmt NUR den Ordner weg: seine Modelle stehen danach ohne Ordner (Eintrag weg), gezählt wird, wie viele.
4. Ein unbekannter Ordner wird gemeldet, nicht still übergangen.

Die Zuordnung liegt in einer Prüfablage (`OBJECTS_ROOT` umgeleitet, Regel `test-isolation`), nie in `3DObjects/models/modellordner.json`.
Sabotage: in `ordner_umbenennen` die Zeile `q['modelle'] = …` streichen → Fall 1 rot; in `ordner_loeschen` `del q['modelle'][m]` streichen → Fall 3 rot.
Aufruf: python manage.py test core.tests.unit.test_modellordner
"""

from pathlib import Path

from django.test import SimpleTestCase, override_settings

from core.dienste.modellordner import Modellordner

from ._pruefablage import Pruefablage


class ModellordnerTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        ablage = Pruefablage.ordner('modellordner_')
        self.wurzel = Path(ablage.__enter__())
        self.addCleanup(ablage.__exit__, None, None, None)
        umschaltung = override_settings(OBJECTS_ROOT=str(self.wurzel))
        umschaltung.enable()
        self.addCleanup(umschaltung.disable)
        Modellordner.anlegen('genesis9', 'Edgar')
        Modellordner.anlegen('genesis9', 'Tests')
        Modellordner.anlegen('modell', 'Edgar')
        Modellordner.verschieben('genesis9', ['Edgar Mesh 2', 'Edgar Mesh 3'], 'Edgar')
        Modellordner.verschieben('genesis9', ['Probe'], 'Tests')
        Modellordner.verschieben('modell', ['Female1'], 'Edgar')

    def test_die_umleitung_greift(self):
        self.assertEqual(Modellordner.datei(), self.wurzel / 'models' / 'modellordner.json')
        self.assertTrue(Modellordner.datei().is_file())

    def test_1_umbenennen_nimmt_die_modelle_mit(self):
        self.assertEqual(Modellordner.ordner_umbenennen('genesis9', 'Edgar', 'Edgars Figuren'), 'Edgars Figuren')
        daten = Modellordner.lesen()
        self.assertEqual(daten['genesis9']['ordner'], ['Edgars Figuren', 'Tests'])
        self.assertEqual(daten['genesis9']['modelle'], {'Edgar Mesh 2': 'Edgars Figuren', 'Edgar Mesh 3': 'Edgars Figuren', 'Probe': 'Tests'})
        self.assertEqual(daten['modell'], {'ordner': ['Edgar'], 'modelle': {'Female1': 'Edgar'}})

    def test_2_umbenennen_auf_einen_vorhandenen_namen_wird_abgelehnt(self):
        with self.assertRaisesMessage(ValueError, 'gibt es schon'):
            Modellordner.ordner_umbenennen('genesis9', 'Edgar', 'tests')
        self.assertEqual(Modellordner.ordner_umbenennen('genesis9', 'Edgar', 'EDGAR'), 'EDGAR')
        self.assertEqual(Modellordner.lesen()['genesis9']['modelle']['Edgar Mesh 2'], 'EDGAR')

    def test_3_loeschen_laesst_die_modelle_ohne_ordner_stehen(self):
        self.assertEqual(Modellordner.ordner_loeschen('genesis9', 'Edgar'), 2)
        daten = Modellordner.lesen()
        self.assertEqual(daten['genesis9']['ordner'], ['Tests'])
        self.assertEqual(daten['genesis9']['modelle'], {'Probe': 'Tests'})
        self.assertEqual(daten['modell']['modelle'], {'Female1': 'Edgar'})

    def test_4_unbekannter_ordner_wird_gemeldet(self):
        with self.assertRaisesMessage(ValueError, 'gibt es nicht'):
            Modellordner.ordner_umbenennen('genesis9', 'Fehlt', 'Neu')
        with self.assertRaisesMessage(ValueError, 'gibt es nicht'):
            Modellordner.ordner_loeschen('genesis9', 'Fehlt')
