# -*- coding: utf-8 -*-
u"""Hilfe → Kleidung → Neu: die Seite steht, und ihre Zahlen kommen aus Python.

WARUM (Edgar, 08.09.2026: „schreibe … in eine neue Seite hilfe - kleidung -
Neu"): Die Analyse zu „wie holt man das Beste aus MakeHuman, GarmentCode und
UMA" gehört ins Projekt, neben die Seiten, deren Zahlen sie benutzt.

Geprüft wird dreierlei, und der dritte Punkt ist der, den man vergisst:

1. Die Seite antwortet und trägt ihre Kernzahlen.
2. Die Daten kommen aus `kleidung.vergleich.Vergleich`, nicht aus der
   Vorlage — sonst rechnet sie niemand mehr nach.
3. Die MITGELIEFERTEN djangoBase-Hilfeseiten bleiben erreichbar. Ein zu
   weit gefasster eigener Präfix schluckt sie, und das fällt erst auf,
   wenn jemand Hilfe → Logs aufruft (Befund vom 07.09.2026).
"""
import sys
import unittest
from pathlib import Path

from django.conf import settings
from django.test import Client, SimpleTestCase
from django.urls import reverse

sys.path.insert(0, str(Path(settings.ASSETS_ROOT)))

from kleidung.vergleich import Vergleich                     # noqa: E402


class SeiteNeu(SimpleTestCase):

    databases = set()

    def setUp(self):
        self.antwort = Client().get(reverse('hilfe_kleidung_neu'))
        self.inhalt = self.antwort.content.decode('utf-8')

    def test_die_seite_antwortet(self):
        self.assertEqual(self.antwort.status_code, 200)

    def test_die_adresse_ist_die_erwartete(self):
        self.assertEqual(reverse('hilfe_kleidung_neu'),
                         '/hilfe/kleidung/neu/')

    def test_die_kernzahlen_stehen_darin(self):
        u"""Nicht der Fließtext, sondern die Zahlen: Sie sind der Grund,
        warum es die Seite gibt."""
        for probe in ('16.277', '18.210', '6.890', '347', '274',
                      u'Konformer', u'GarmentCode', u'Fünf Welten'):
            self.assertIn(probe, self.inhalt, probe)

    def test_alle_fuenf_welten_und_sieben_wege(self):
        for welt in Vergleich.welten():
            self.assertIn(welt['name'], self.inhalt, welt['name'])
        for weg in Vergleich.wege():
            self.assertIn(weg['bindung'], self.inhalt, weg['name'])

    def test_der_balken_ist_zur_skala_gezeichnet(self):
        u"""Die Breite MUSS die Zahl sein, nicht nur neben ihr stehen.
        95 % und 31 % kommen beide vor."""
        self.assertIn('width: 95%', self.inhalt)
        self.assertIn('width: 31%', self.inhalt)

    def test_das_menue_fuehrt_den_punkt(self):
        u"""Eine Seite ohne Menüpunkt findet niemand."""
        gruppen = settings.DJANGOBASE.get('hilfe_extra') or []
        eintraege = [e for gruppe in gruppen
                     for e in gruppe.get('untermenu', [])]
        adressen = [e['url'] for e in eintraege]
        self.assertIn('/hilfe/kleidung/neu/', adressen)

    def test_die_mitgelieferten_hilfeseiten_bleiben(self):
        u"""Der eigene Präfix darf djangoBases Seiten nicht schlucken."""
        for pfad in ('/hilfe/versionen/', '/hilfe/logs/', '/hilfe/tests/',
                     '/hilfe/kleidung/', '/hilfe/kleidung/garmentcode/'):
            self.assertEqual(Client().get(pfad).status_code, 200, pfad)


class DatenStehenInPython(unittest.TestCase):
    u"""Die Stammdaten — geprüft ohne Django, weil sie ohne auskommen."""

    databases = set()

    def test_jede_welt_ist_vollstaendig(self):
        felder = ('kuerzel', 'name', 'formt', 'regler', 'netz', 'kleidung',
                  'bestand')
        welten = Vergleich.welten()
        self.assertEqual(len(welten), 5)
        for welt in welten:
            for feld in felder:
                self.assertTrue(welt.get(feld), '%s: %s' % (welt, feld))
            self.assertIn(welt['kuerzel'], Vergleich.FARBEN)

    def test_die_sieben_wege_sind_sieben(self):
        wege = Vergleich.wege()
        self.assertEqual(len(wege), 7)
        stark = [w for w in wege if w.get('stark')]
        self.assertEqual([w['name'] for w in stark],
                         ['UMA-Konformer', 'GarmentCode'],
                         u'Die beiden Wege, die auf JEDEN Körper gehen')

    def test_die_anteile_sind_prozentwerte(self):
        for zeile in Vergleich.knochen_gegen_morph():
            self.assertGreaterEqual(zeile['anteil'], 0)
            self.assertLessEqual(zeile['anteil'], 100)

    def test_es_gibt_drei_stufen_mit_aufwand(self):
        stufen = Vergleich.stufen()
        self.assertEqual(len(stufen), 3)
        for stufe in stufen:
            self.assertTrue(stufe['titel'])
            self.assertTrue(stufe['aufwand'],
                            u'Eine Stufe ohne Aufwandsangabe ist ein Wunsch')

    def test_abgrenzung_und_unsicherheit_sind_benannt(self):
        u"""Ein Vorschlag ohne „was ich NICHT vorschlage" und ohne „was
        daran unsicher ist" liest sich wie eine Zusage."""
        self.assertGreaterEqual(len(Vergleich.nicht()), 3)
        self.assertGreaterEqual(len(Vergleich.unsicher()), 3)
