# -*- coding: utf-8 -*-
"""Proportionen-Eingaben: Prüfung, Endpunkt, Start behält sie (19.09.2026).

1. `Bildmodelloptionen.proportionen_pruefen`: nur formbare Maße im Bereich,
   Augenabstand (nicht formbar) und Unbekanntes fallen weg; `pruefen` trägt sie.
2. POST `proportionen/` legt sie in `job.optionen` ab; ein Start ohne eigene
   Angabe behält sie, einer mit leerem Wörterbuch löscht sie.
"""

import json
import unittest
from unittest import mock

from django.test import Client, TestCase

from core.dienste.bildmodelloptionen import Bildmodelloptionen
from core.models import Bildmodellauftrag


class PruefungTest(unittest.TestCase):
    def test_nur_formbare_im_bereich(self):
        roh = {'huefte_breite': '38.26', 'augen_abstand': 7, 'quatsch': 3, 'nase_breite': 0.1,
               'kopf_hoehe': None, 'wade_dicke': 'abc', 'brust_tiefe': 500}
        self.assertEqual(Bildmodelloptionen.proportionen_pruefen(roh), {'huefte_breite': 38.3})
        self.assertEqual(Bildmodelloptionen.proportionen_pruefen(None), {})
        aus = Bildmodelloptionen.pruefen({'proportionen': {'mund_breite': 6}})
        self.assertEqual(aus['proportionen'], {'mund_breite': 6.0})
        self.assertEqual(Bildmodelloptionen.vorgaben()['proportionen'], {})
        katalog = Bildmodelloptionen.katalog()
        self.assertEqual(len(katalog['proportionen']), 18)
        augen = [m for m in katalog['proportionen'] if m['schluessel'] == 'augen_abstand'][0]
        self.assertFalse(augen['formbar'])


class EndpunktTest(TestCase):
    def setUp(self):
        self.client = Client(HTTP_HOST='127.0.0.1')
        self.job = Bildmodellauftrag.objects.create(kennung='2026.01.01.00.00.01', name='ZZ')

    def test_stellen_und_start_behaelt(self):
        antwort = self.client.post(
            '/api/bildmodell/%s/proportionen/' % self.job.id,
            data=json.dumps({'proportionen': {'huefte_breite': 38, 'augen_abstand': 7}}),
            content_type='application/json',
        )
        self.assertEqual(antwort.json()['proportionen'], {'huefte_breite': 38.0})
        self.job.refresh_from_db()
        self.assertEqual(self.job.optionen['proportionen'], {'huefte_breite': 38.0})
        with mock.patch('core.api.bildmodell.Bildmodellarbeiter.starten', return_value=4711):
            self.client.post('/api/bildmodell/%s/starten/' % self.job.id,
                             data=json.dumps({'ab': 'anpassung', 'optionen': {'reglersatz': 'alle'}}),
                             content_type='application/json')
            self.job.refresh_from_db()
            self.assertEqual(self.job.optionen['proportionen'], {'huefte_breite': 38.0})
            self.client.post('/api/bildmodell/%s/starten/' % self.job.id,
                             data=json.dumps({'ab': 'anpassung', 'optionen': {'proportionen': {}}}),
                             content_type='application/json')
            self.job.refresh_from_db()
            self.assertEqual(self.job.optionen['proportionen'], {})
