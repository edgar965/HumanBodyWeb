# -*- coding: utf-8 -*-
u"""Hilfe -> Video to BVH: die Seite antwortet, traegt alle Pipelines und ist
eine djangoBase-Tabelle.

Wie bei Hilfe -> Kleidung gilt beides: Die eigene Seite unter `/hilfe/`
antwortet, UND die mitgelieferten djangoBase-Seiten bleiben erreichbar
(dort ist das Projekt am 27.08.2026 schon einmal hineingelaufen).

Die Tabelle muss `db-tabelle sortable` und einen `data-sort-key` tragen —
nur dann bindet `tabellen_auto.js` Sortierung und Spaltenbreiten. Und wo
ein Wert fehlt, steht „nicht gemessen", keine leere Zelle: Eine leere
Zelle saehe aus wie „alles gut".
"""
from django.test import Client, SimpleTestCase

from core.dienste.pipelinevergleich import Pipelinevergleich
from core.models import BVHJob


class DieSeite(SimpleTestCase):

    databases = set()
    ADRESSE = '/hilfe/video-to-bvh/'

    def setUp(self):
        self.client = Client()

    def _text(self):
        antwort = self.client.get(self.ADRESSE)
        self.assertEqual(antwort.status_code, 200)
        return antwort.content.decode('utf-8')

    def test_antwortet(self):
        self._text()

    def test_djangobase_seiten_bleiben_erreichbar(self):
        self.assertEqual(self.client.get('/hilfe/versionen/').status_code, 200)

    def test_nennt_jede_pipeline_mit_dem_namen_aus_dem_modell(self):
        text = self._text()
        for schluessel, name in BVHJob.PIPELINE_CHOICES:
            with self.subTest(pipeline=schluessel):
                self.assertIn(name, text)
                self.assertIn('>%s<' % schluessel, text)

    def test_die_tabelle_ist_eine_djangobase_tabelle(self):
        text = self._text()
        self.assertIn('class="db-tabelle sortable vtb-tabelle"', text)
        self.assertIn('data-sort-key="hilfe-video-to-bvh"', text)
        self.assertIn('class="db-tabelle-rahmen"', text)
        # Die Listen-Spalten sortieren nicht.
        self.assertEqual(text.count('data-sort-aus="1"'), 2)

    def test_fehlende_werte_stehen_ausgeschrieben_da(self):
        text = self._text()
        fehlt = any(e[f] is None for e in Pipelinevergleich.alle()
                    for f in ('dauer_s', 'ueberlagerung_px', 'ruhe_wurzel'))
        self.assertEqual('nicht gemessen' in text, fehlt)

    def test_jeder_rang_steht_in_der_tabelle(self):
        text = self._text()
        for e in Pipelinevergleich.alle():
            self.assertIn('data-sort="%d"' % e['rang'], text)

    def test_der_menuepunkt_zeigt_auf_die_seite(self):
        self.assertIn('href="/hilfe/video-to-bvh/"', self._text())
