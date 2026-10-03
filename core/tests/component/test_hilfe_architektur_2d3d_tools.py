# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> 2D3D, Reiter „Tools": die Seite zeigt die Gruppen, die Aufrufe und das Klassenmodell.

WARUM (Edgar, 03.10.2026: „schreibe alle lokalen Tools für die Anpassung des Modells auf die Hilfeseite, damit andere Sessions das lesen können … Mach auch ein Klassenmodell"):
Ein Reiter, dessen Knopf fehlt oder dessen Fläche leer bleibt, sieht auf der Seite aus wie fertig. Die Tests halten fest: der Reiter steht im HTML und lässt sich über die Adresse
(`#tools`) wählen, jede Gruppe hat ihren Anker, jede Klasse im Klassenmodell ihren, jeder Verweis der Tabelle trifft einen Anker, und die Regeln (Schleifen nur nach Ansage) stehen auf der Seite."""

import re

from django.test import Client, SimpleTestCase
from django.urls import reverse

from core.dienste.architektur2d3dwerkzeuge import Architektur2d3dwerkzeuge


class SeiteTools(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.text = Client().get(reverse('hilfe_architektur_2d3d')).content.decode('utf-8')
        cls.kontext = Architektur2d3dwerkzeuge.kontext()

    def test_der_reiter_tools_steht_im_html_mit_knopf_und_flaeche(self):
        self.assertIn('data-ziel="tools"', self.text)
        self.assertIn('data-reiter="tools"', self.text)
        self.assertIn('Die Tools zur Anpassung des Modells', self.text)

    def test_die_regeln_nur_nach_ansage_stehen_auf_der_seite(self):
        for regel in self.kontext['regeln']:
            self.assertIn(regel['regel'], self.text)
        self.assertIn('Schleifen über Blender nur nach Ansage', self.text)

    def test_jede_gruppe_hat_einen_anker_und_ein_klassenmodell(self):
        for g in self.kontext['gruppen']:
            self.assertIn('id="t-%s"' % g['kennung'], self.text)
            self.assertIn('id="tm-%s"' % g['kennung'], self.text)
            for k in g['modell']:
                self.assertIn('id="%s"' % k['anker'], self.text)

    def test_jeder_verweis_der_tools_tabellen_trifft_einen_anker(self):
        flaeche = self.text.split('data-reiter="tools"', 1)[1]
        ids = set(re.findall(r'\bid="([^"]+)"', self.text))
        ziele = set(re.findall(r'href="#(t[m]?-[^"]+)"', flaeche))
        self.assertEqual(sorted(ziele - ids), [])

    def test_ohne_befund_steht_kein_befundkasten_auf_der_seite(self):
        self.assertEqual(self.kontext['befunde'], [])
        self.assertNotIn('tw-befunde', self.text)
