"""Kleidungsregeln (21.11.2026): `Kleidregelnaufloesung` (Wahl der App → `einstellung.json` des Tests), `Fotogenesiskleiderregeln` (Wahl am Job) und der Katalog
`meshgenesis/kleidregeln.json` (EINE Quelle für Seite und Kette). Ohne Datenbank, ohne Karte. Noch nicht gelaufen (Tests nur auf Ansage)."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from core.dienste.fotogenesiskleiderregeln import Fotogenesiskleiderregeln
from core.dienste.kleidregelnaufloesung import Kleidregelnaufloesung
from core.dienste.kleidregelnkatalog import Kleidregelnkatalog
from core.dienste.meshgenesistest import Meshgenesistest


class KleidregelnkatalogTest(unittest.TestCase):
    databases = []

    def test_voreinstellungen_nennen_nur_bekannte_regeln(self):
        katalog = Kleidregelnkatalog._laden('kleidregeln.json')
        bekannt = {r['kennung'] for r in katalog['regeln']}
        for v in katalog['voreinstellungen']:
            self.assertLessEqual(set(v['regeln']), bekannt, v['kennung'])

    def test_wie_bisher_ohne_regeln_der_stufe(self):
        # „Wie bisher“ darf nichts anschalten, was die Stufe durchsetzt (sonst änderte die Vorgabe das Ergebnis)
        katalog = Kleidregelnkatalog._laden('kleidregeln.json')
        wie = next(v['regeln'] for v in katalog['voreinstellungen'] if v['kennung'] == 'wie_bisher')
        self.assertFalse({'oeffnungen', 'abschluss', 'fetzen', 'rand_glatt', 'rock'} & set(wie))

    def test_ohne_eintrag_gilt_die_voreinstellung(self):
        an = {r['kennung']: r['an'] for g in Kleidregelnkatalog.regeln({}) for r in g['regeln']}
        self.assertTrue(an['nachbarn'])
        self.assertFalse(an['oeffnungen'])
        self.assertFalse(an['rock'])

    def test_eintrag_der_app_gewinnt(self):
        an = {r['kennung']: r['an'] for g in Kleidregelnkatalog.regeln({'kleider_regel_rock': '1', 'kleider_regel_nachbarn': '0'}) for r in g['regeln']}
        self.assertTrue(an['rock'])
        self.assertFalse(an['nachbarn'])


class KleidregelnaufloesungTest(unittest.TestCase):
    databases = []

    def _wurzel(self, inhalt='{"geschlecht": "maennlich"}'):
        wurzel = Path(tempfile.mkdtemp(dir=r'A:\3DTools\ProjektTemp\_wegwerf'))
        (wurzel / 'k').mkdir()
        if inhalt is not None:
            (wurzel / 'k' / 'einstellung.json').write_text(inhalt, encoding='utf-8')
        return wurzel

    def test_wahl_der_app_in_die_einstellung(self):
        wurzel = self._wurzel()
        with mock.patch.object(Meshgenesistest, 'ordner', return_value=wurzel):
            wahl = Kleidregelnaufloesung.schreiben('k', {'kleider_regel_rock': '1'})
        geschrieben = json.loads((wurzel / 'k' / 'einstellung.json').read_text(encoding='utf-8'))
        self.assertEqual(geschrieben['geschlecht'], 'maennlich')                 # Bestehendes bleibt
        self.assertEqual(geschrieben[Kleidregelnaufloesung.FELD], wahl)
        self.assertTrue(wahl['rock'])
        self.assertFalse(wahl['fetzen'])

    def test_ohne_einstellung_nichts(self):
        wurzel = self._wurzel(inhalt=None)
        with mock.patch.object(Meshgenesistest, 'ordner', return_value=wurzel):
            self.assertIsNone(Kleidregelnaufloesung.schreiben('k', {}))
        self.assertFalse((wurzel / 'k' / 'einstellung.json').exists())


class FotogenesiskleiderregelnTest(unittest.TestCase):
    databases = []

    def test_mischen_setzt_und_loescht(self):
        neu = Fotogenesiskleiderregeln.mischen({'rock': True}, {'fetzen': True, 'rock': None})
        self.assertEqual(neu, {'fetzen': True})

    def test_mischen_lehnt_unbekanntes_ab(self):
        with self.assertRaises(ValueError):
            Fotogenesiskleiderregeln.mischen({}, {'gibt_es_nicht': True})
        with self.assertRaises(ValueError):
            Fotogenesiskleiderregeln.mischen({}, {'rock': 'an'})
        with self.assertRaises(ValueError):
            Fotogenesiskleiderregeln.mischen({}, ['rock'])

    def test_lesen_nur_bekannte_wahrheitswerte(self):
        info = {'pshuman': {'kleider_regeln': {'rock': True, 'fetzen': 'ja', 'unbekannt': True}}}
        self.assertEqual(Fotogenesiskleiderregeln.lesen(info), {'rock': True})
        self.assertEqual(Fotogenesiskleiderregeln.lesen({}), {})

    def test_zeilen_zeigen_job_und_app(self):
        ordner = Path(tempfile.mkdtemp(dir=r'A:\3DTools\ProjektTemp\_wegwerf'))
        (ordner / 'job.json').write_text(json.dumps({'pshuman': {'kleider_regeln': {'rock': True, 'nachbarn': False}}}), encoding='utf-8')
        zeilen = {z['kennung']: z for z in Fotogenesiskleiderregeln.zeilen({'ordner': ordner}, prefs={})}
        self.assertEqual(zeilen['rock']['wahl'], 'an')
        self.assertEqual(zeilen['nachbarn']['wahl'], 'aus')
        self.assertEqual(zeilen['fetzen']['wahl'], 'einstellung')
        self.assertTrue(zeilen['nachbarn']['app_an'])
