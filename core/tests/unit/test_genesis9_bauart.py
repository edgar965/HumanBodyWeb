# -*- coding: utf-8 -*-
"""Bauart am Eintrag der Garderobe (`Genesis9/bauart.py`, 12.11.2026).

Edgar, 12.11.2026: „mach alles, mit deinen Empfehlungen“ — Entscheidung 3 des Konzepts „Genesis zuerst“: Starr wird ein Stück über die Bauart am
Eintrag der Garderobe, nicht über neue Gewichte in der Stückdatei. Geprüft ohne Daz-Bibliothek, die Ablage liegt in einem eigenen Ordner unter
`ProjektTemp/_wegwerf/tests/` (nie in `3DObjects/models/Genesis9/`):

1. Setzen, Lesen, Zurücknehmen (None) und untaugliche Werte (unbekannte Bauart, Tiefe außerhalb 0–50 mm → ValueError, Datei unverändert).
2. `fuer`: am Stück gesetzt schlägt den Vorschlag; Requisit → starr; ein Kleidungsstück ohne Kategorie- oder Namensregel → None (dann entscheidet
   `G9stoff.entscheiden` wie bisher).
3. `stand` (Schlüssel des Antwortvorrats): None ohne Angabe — der Schlüssel aller Stücke ohne Angabe bleibt damit bitgleich —, sonst die Angabe.
4. `antwort`: ohne Vorschlag lose, wenn ein Teil im Stoffschwung läuft, sonst anliegend; die gesetzte Tiefe geht mit.

Sabotage: in `G9bauart.setzen` die Prüfung der Grenzen streichen → Fall 1 rot; in `fuer` die gesetzte Bauart nach dem Vorschlag fragen → Fall 2 rot;
`stand` immer eine Liste geben → Fall 3 rot.

Geschrieben am 12.11.2026, nicht gelaufen (Tests nur auf Ansage).
"""
import shutil
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase
from Genesis9.bauart import G9bauart


class G9bauartTest(SimpleTestCase):

    ORDNER = Path(settings.BASE_DIR).parent / 'ProjektTemp' / '_wegwerf' / 'tests' / 'g9bauart'

    def setUp(self):
        shutil.rmtree(self.ORDNER, ignore_errors=True)
        self.ORDNER.mkdir(parents=True, exist_ok=True)
        umleitung = mock.patch.object(G9bauart, 'datei', classmethod(lambda cls: self.ORDNER / G9bauart.DATEI))
        umleitung.start()
        self.addCleanup(umleitung.stop)
        self.addCleanup(shutil.rmtree, self.ORDNER, True)
        # Kein Zugriff auf die echte Einteilung der Garderobe: die Kategorie ist hier immer „Oberteile“.
        kategorie = mock.patch('Genesis9.garderobekategorien.G9garderobekategorien.kategorie', return_value='Oberteile')
        kategorie.start()
        self.addCleanup(kategorie.stop)

    def test_1_setzen_lesen_zuruecknehmen(self):
        self.assertEqual(G9bauart.gesetzt('laserwaffe'), (None, None))
        G9bauart.setzen('laserwaffe', 'starr', 25)
        self.assertEqual(G9bauart.gesetzt('laserwaffe'), ('starr', 25.0))
        G9bauart.setzen('laserwaffe', None, 25)
        self.assertEqual(G9bauart.gesetzt('laserwaffe'), (None, 25.0))
        vorher = G9bauart.datei().read_bytes()
        for falsch in (('laserwaffe', 'weich', None), ('laserwaffe', None, 51), ('laserwaffe', None, -1), ('laserwaffe', None, 'tief'), ('', 'starr', None)):
            with self.assertRaises(ValueError, msg=repr(falsch)):
                G9bauart.setzen(*falsch)
        self.assertEqual(G9bauart.datei().read_bytes(), vorher)

    def test_2_gesetzt_schlaegt_vorschlag(self):
        hemd = {'id': 'hemd', 'art': 'kleidung'}
        stab = {'id': 'stab', 'art': 'requisit'}
        self.assertIsNone(G9bauart.fuer(hemd))
        self.assertEqual(G9bauart.fuer(stab), 'starr')
        G9bauart.setzen('stab', 'anliegend')
        G9bauart.setzen('hemd', 'lose')
        self.assertEqual((G9bauart.fuer(stab), G9bauart.fuer(hemd)), ('anliegend', 'lose'))

    def test_3_stand_fuer_den_schluessel(self):
        self.assertIsNone(G9bauart.stand({'id': 'hemd', 'art': 'kleidung'}))
        self.assertIsNone(G9bauart.stand(None))
        G9bauart.setzen('hemd', None, 4)
        self.assertEqual(G9bauart.stand({'id': 'hemd'}), [None, 4.0])

    def test_4_antwort(self):
        hemd = {'id': 'hemd', 'art': 'kleidung'}
        self.assertEqual(G9bauart.antwort(hemd, False)['bauart'], 'anliegend')
        self.assertEqual(G9bauart.antwort(hemd, True)['bauart'], 'lose')
        G9bauart.setzen('hemd', 'starr', 30)
        self.assertEqual(G9bauart.antwort(hemd, True), {'bauart': 'starr', 'schuh': False, 'nachgeben_mm': 30.0})
