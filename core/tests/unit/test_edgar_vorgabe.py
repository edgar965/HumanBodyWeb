# -*- coding: utf-8 -*-
"""Paket `Edgar`: `Vorgabe` — der editierbare Prompt des Rundenberaters (`vorgaben/abgleich.md`, Reiter „Bewertung").

Kunstdateien in einem Ordner unter `ProjektTemp`; die echte Vorgabe wird nicht angefasst (`Vorgabe(pfad)`). Ohne Django-Datenbank, ohne Server.
Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).
"""

import shutil
import tempfile
from pathlib import Path

from django.test import SimpleTestCase
from Edgar.vorgabe import Vorgabe

PROJEKTTEMP = Path(__file__).resolve().parents[3] / 'ProjektTemp'
TEXT = '# Titel\n\nHerkunft: nur für Menschen.\n\n## Maßstab\n\n1. Die Vorlage zählt.\n'


class DieVorgabe(SimpleTestCase):
    def setUp(self):
        self.ordner = Path(tempfile.mkdtemp(prefix='edgar_vorgabe_', dir=str(PROJEKTTEMP)))
        self.pfad = self.ordner / 'abgleich.md'
        self.pfad.write_text(TEXT, encoding='utf-8')
        self.vorgabe = Vorgabe(self.pfad)

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)

    def test_der_agent_bekommt_den_text_ab_der_ersten_ueberschrift(self):
        text = self.vorgabe.fuer_agent()
        self.assertTrue(text.startswith('## Maßstab'))
        self.assertNotIn('Herkunft', text)
        self.assertIn('Herkunft', self.vorgabe.lesen())

    def test_speichern_gilt_beim_naechsten_lesen_und_sichert_die_vorfassung(self):
        self.vorgabe.speichern('# T\n\n## Neu\n\nEin neuer Satz.\r\n')
        self.assertEqual(self.vorgabe.fuer_agent(), '## Neu\n\nEin neuer Satz.')
        self.assertEqual(self.pfad.with_name('abgleich.md.vorher').read_text(encoding='utf-8'), TEXT)
        self.assertNotIn('\r', self.pfad.read_text(encoding='utf-8'))
        self.assertFalse(self.pfad.with_name('abgleich.md.neu').exists())            # die Zwischendatei bleibt nicht liegen

    def test_ein_text_ohne_ueberschrift_wird_abgelehnt_und_die_datei_bleibt(self):
        with self.assertRaises(ValueError):
            self.vorgabe.speichern('nur ein Absatz ohne Überschrift')
        self.assertEqual(self.pfad.read_text(encoding='utf-8'), TEXT)
        self.assertFalse(self.pfad.with_name('abgleich.md.vorher').exists())

    def test_zu_langer_text_und_kein_text_werden_abgelehnt(self):
        with self.assertRaises(ValueError):
            self.vorgabe.speichern('## A\n' + 'x' * Vorgabe.HOECHSTENS)
        with self.assertRaises(ValueError):
            self.vorgabe.speichern(None)
        self.assertEqual(self.pfad.read_text(encoding='utf-8'), TEXT)

    def test_ohne_ueberschrift_in_der_datei_geht_der_ganze_text_an_den_agenten(self):
        self.pfad.write_text('Nur Text.\n', encoding='utf-8')
        self.assertEqual(self.vorgabe.fuer_agent(), 'Nur Text.')
