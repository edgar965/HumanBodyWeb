# -*- coding: utf-8 -*-
u"""Hilfe → Kleidung → Kleiderphysik: die Seite steht, ihre Zahlen kommen aus Python.

WARUM (Edgar, 10.09.2026: „Kleiderphysik - schreib das rein in eine neuen
Seite Hilfe - Kleider - Kleiderphysik"): Die Bestandsaufnahme zur
Stoffdynamik gehört ins Projekt, neben die Seiten, deren Kette sie benutzt.

Geprüft wird dreierlei, wie bei der Seite „Neu":

1. Die Seite antwortet und trägt ihre Kernzahlen und -namen.
2. Die Daten kommen aus `kleidung.physik.Kleiderphysik`, nicht aus der
   Vorlage — und sie sind vollständig (ein Kandidat ohne Urteil, eine
   Messung ohne Ergebnis wäre eine halbe Tabelle).
3. Die MITGELIEFERTEN djangoBase-Hilfeseiten bleiben erreichbar.
"""
import sys
import unittest
from pathlib import Path

from django.conf import settings
from django.test import Client, SimpleTestCase
from django.urls import reverse
from django.utils.html import escape

sys.path.insert(0, str(Path(settings.ASSETS_ROOT)))

from kleidung.physik import Kleiderphysik                    # noqa: E402


class SeitePhysik(SimpleTestCase):

    databases = []

    def setUp(self):
        self.antwort = Client().get(reverse('hilfe_kleidung_physik'))
        self.inhalt = self.antwort.content.decode('utf-8')

    def test_die_seite_antwortet(self):
        self.assertEqual(self.antwort.status_code, 200)

    def test_die_adresse_ist_die_erwartete(self):
        self.assertEqual(reverse('hilfe_kleidung_physik'),
                         '/hilfe/kleidung/physik/')

    def test_die_kernaussagen_stehen_darin(self):
        u"""Die Zahlen und Namen, um die es geht — nicht der Fließtext."""
        for probe in ('Style3D', 'Newton', 'GarmentCode', '10.201',
                      str(Kleiderphysik.KERNELBAU_S),
                      str(Kleiderphysik.STYLE3D_MS_JE_BILD),
                      u'blenderCloth nutze ich nicht'):
            self.assertIn(probe, self.inhalt, probe)

    def test_jeder_kandidat_und_jede_messung_steht_auf_der_seite(self):
        # `escape`, weil die Vorlage Anführungszeichen als `&quot;` schreibt —
        # ein Urteil mit Zitat stünde sonst nie „auf der Seite".
        for kandidat in Kleiderphysik.kandidaten():
            self.assertIn(escape(kandidat['urteil']), self.inhalt, kandidat['name'])
        for messung in Kleiderphysik.messung():
            self.assertIn(escape(messung['ergebnis']), self.inhalt, messung['motor'])

    def test_das_menue_fuehrt_den_punkt(self):
        gruppen = settings.DJANGOBASE.get('hilfe_extra') or []
        eintraege = [e for gruppe in gruppen
                     for e in gruppe.get('untermenu', [])]
        adressen = [e['url'] for e in eintraege]
        self.assertIn('/hilfe/kleidung/physik/', adressen)

    def test_die_mitgelieferten_hilfeseiten_bleiben(self):
        for pfad in ('/hilfe/versionen/', '/hilfe/logs/', '/hilfe/tests/',
                     '/hilfe/kleidung/', '/hilfe/kleidung/garmentcode/',
                     '/hilfe/kleidung/neu/'):
            self.assertEqual(Client().get(pfad).status_code, 200, pfad)


class DatenStehenInPython(unittest.TestCase):

    databases = []

    def test_jeder_kandidat_ist_vollstaendig(self):
        felder = ('name', 'lizenz', 'laeuft', 'koerper', 'stand', 'urteil')
        kandidaten = Kleiderphysik.kandidaten()
        self.assertGreaterEqual(len(kandidaten), 6)
        for kandidat in kandidaten:
            for feld in felder:
                self.assertTrue(kandidat.get(feld), '%s: %s' % (kandidat, feld))

    def test_die_messung_hat_gute_und_schlechte_zeilen(self):
        u"""Eine Messtabelle, in der alles hält, hat nichts gemessen."""
        messung = Kleiderphysik.messung()
        self.assertTrue(any(m['gut'] for m in messung))
        self.assertTrue(any(not m['gut'] for m in messung))
        for m in messung:
            self.assertTrue(m['ergebnis'], m['motor'])

    def test_blender_ist_messzeile_aber_keine_empfehlung(self):
        u"""Edgar: „blenderCloth nutze ich nicht" — die Zeile bleibt, das
        Urteil sagt nein."""
        blender = [k for k in Kleiderphysik.kandidaten()
                   if k['name'].startswith('Blender')]
        self.assertEqual(len(blender), 1)
        self.assertTrue(blender[0]['urteil'].startswith('nicht'))
        self.assertTrue(any('Blender' in titel for titel, _ in Kleiderphysik.nicht()))

    def test_abgrenzung_offenes_und_quellen_sind_benannt(self):
        self.assertGreaterEqual(len(Kleiderphysik.nicht()), 3)
        self.assertGreaterEqual(len(Kleiderphysik.offen()), 3)
        for name, adresse, was in Kleiderphysik.quellen():
            self.assertTrue(name and adresse and was, name)

    def test_die_zehn_sekunden_rechnung_folgt_den_konstanten(self):
        erwartet = 10 * 60 * Kleiderphysik.STYLE3D_MS_JE_BILD / 1000 / 60
        self.assertAlmostEqual(Kleiderphysik.minuten_je_10s(), erwartet, places=1)
