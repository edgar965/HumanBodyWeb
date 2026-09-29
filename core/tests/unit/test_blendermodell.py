# -*- coding: utf-8 -*-
"""Bereich „BlenderModel" (29.09.2026) — Optionen, Lauf und Ablage. Rein rechnend: keine Datenbank, keine
Dateien, keine Grafikkarte. Die Endpunkte samt gemeinsamer Register: `test_blendermodell_endpunkte.py`.
"""

import inspect
from unittest import mock

from django.test import SimpleTestCase

from core.daten.blendermodellablage import Blendermodellablage
from core.dienste.blendermodelllauf import Blendermodelllauf
from core.dienste.blendermodelloptionen import Blendermodelloptionen
from core.dienste.meshfiguroptionen import Meshfiguroptionen
from core.dienste.ollamamodelle import Ollamamodelle


class BlendermodelloptionenTest(SimpleTestCase):
    def setUp(self):
        # Die Testfiguren stehen in der Daz-Bibliothek, die Prüf-KIs in Ollama — hier geht es nur um die
        # Kataloge.
        for ziel, name, wert in (
            (Meshfiguroptionen, '_referenzen', [('', '—')]),
            (Ollamamodelle, 'mit_bildern', [('qwen3.8:27b', 'qwen3.8:27b (Q4_K_M)')]),
        ):
            patcher = mock.patch.object(ziel, name, return_value=wert)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_katalog_hat_drei_gruppen_die_rollen_und_kein_netz(self):
        katalog = Blendermodelloptionen.katalog()
        self.assertEqual(set(katalog), {'figur', 'kostuem', 'blender', 'rollen'})
        figur = [f['schluessel'] for f in katalog['figur']['optionen']]
        self.assertEqual(sorted(figur), ['basis', 'modell'], 'die Kette Netz → Figur ist ausgebaut')
        kostuem = {f['schluessel']: f for f in katalog['kostuem']['optionen']}
        self.assertIn('qwen3.8:27b', [w['wert'] for w in kostuem['pruefki']['werte']])
        self.assertIn('aus', [w['wert'] for w in kostuem['pruefki']['werte']])

    def test_das_modell_wird_nicht_ungefragt_in_die_bibliothek_geschrieben(self):
        katalog = Blendermodelloptionen.katalog()
        modell = next(f for f in katalog['figur']['optionen'] if f['schluessel'] == 'modell')
        self.assertEqual(modell['vorgabe'], 'aus')
        self.assertEqual(Blendermodelloptionen.pruefen({})['figur']['modell'], 'aus')
        self.assertEqual(Blendermodelloptionen.pruefen({'figur': {'modell': 'an'}})['figur']['modell'], 'an')

    def test_alte_netzgruppe_faellt_weg(self):
        # Aufträge von vor dem Umbau tragen `netz: {formmodell: trellis2}` — das darf nirgends mehr ankommen.
        optionen = Blendermodelloptionen.pruefen(
            {'netz': {'formmodell': 'trellis2'}, 'figur': 'kein dict', 'x': 1}
        )
        self.assertEqual(set(optionen), {'figur', 'kostuem', 'blender'})
        self.assertEqual(optionen['figur']['basis'], 'feminine')
        self.assertEqual(Blendermodelloptionen.pruefen(None), Blendermodelloptionen.pruefen({}))

    def test_mischen_aendert_nur_die_geschickte_gruppe(self):
        alt = Blendermodelloptionen.pruefen({'kostuem': {'runden': 55}, 'figur': {'basis': 'masculine'}})
        neu = Blendermodelloptionen.mischen(alt, {'kostuem': {'pruefki': 'aus'}})
        self.assertEqual((neu['kostuem']['runden'], neu['kostuem']['pruefki']), (55, 'aus'))
        self.assertEqual(neu['figur']['basis'], 'masculine')


class BlendermodelllaufTest(SimpleTestCase):
    def test_jeder_schritt_hat_sein_band_und_die_baender_schliessen_lueckenlos_an(self):
        self.assertEqual(set(Blendermodelllauf.BAENDER), set(Blendermodelllauf.SCHRITTE))
        ende = 0
        for name in Blendermodelllauf.SCHRITTE:
            von, bis = Blendermodelllauf.BAENDER[name]
            self.assertEqual(von, ende, 'Lücke oder Überlappung vor „%s"' % name)
            self.assertGreater(bis, von, name)
            ende = bis
        self.assertEqual(ende, 100)

    def test_jeder_schritt_steht_in_der_schrittfolge(self):
        # Die Folge baut Lambdas mit späten Importen der schweren Schrittklassen — hier nur der Quelltext.
        quelle = inspect.getsource(Blendermodelllauf.schrittfolge)
        for name in Blendermodelllauf.SCHRITTE:
            self.assertIn("'%s':" % name, quelle, 'Schritt „%s" fehlt in schrittfolge()' % name)

    def test_die_grundfigur_kommt_zuerst_und_trellis_laeuft_nicht(self):
        # Edgar, 29.09.2026: „trellis soll nicht laufen" — kein Schritt baut ein Netz aus den Fotos.
        self.assertEqual(Blendermodelllauf.SCHRITTE[0], 'grundfigur')
        self.assertNotIn('netz', Blendermodelllauf.SCHRITTE)
        quelle = inspect.getsource(Blendermodelllauf.schrittfolge).lower()
        for verboten in ('blendermodellnetz', '_run_mesh', 'trellis', 'hunyuan'):
            self.assertNotIn(verboten, quelle, verboten)


class BlendermodellablageTest(SimpleTestCase):
    def test_lesbar_sind_fotos_netz_und_ergebnis_nicht_die_arbeit(self):
        ablage = Blendermodellablage('2026.09.29.00.00.00')
        for ordner in ('eingang', 'vorbereitet', 'netz', 'ergebnis'):
            self.assertTrue(str(ablage.datei(ordner, 'x.png')).endswith('x.png'), ordner)
        for ordner, name in (
            ('arbeit', 'auftrag.json'),
            ('netz_arbeit', 'auftrag.json'),
            ('netz', '../a'),
            ('ergebnis', '..'),
            ('eingang', 'a/b.png'),
        ):
            with self.assertRaises(ValueError, msg='%s/%s' % (ordner, name)):
                ablage.datei(ordner, name)

    def test_ein_kopfnetz_gibt_es_nicht(self):
        self.assertIsNone(Blendermodellablage('2026.09.29.00.00.00').netzdatei('kopf'))
