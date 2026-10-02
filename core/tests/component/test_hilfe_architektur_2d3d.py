# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> 2D3D: die Seite steht, und jede genannte Klasse gibt es.

WARUM (Edgar, 02.10.2026: „Schreibe alles über die Implementierung der 2D3D Iterationen in eine neue Seite Hilfe -
Architektur 2D3D"): Eine Architekturseite, die Klassen nennt, die es nicht mehr gibt, ist schlimmer als keine. Die
Seite liest Docstring und Zeilenzahl aus dem Code; dieser Test hält fest, dass jede Zeile eine Datei und eine Klasse
findet und dass die Frage „wo schaut die KI auf das Ergebnis?" auf der Seite beantwortet bleibt.
"""

from django.test import Client, SimpleTestCase
from django.urls import reverse
from django.utils.html import escape

from core.dienste.architektur2d3d import Architektur2d3d
from core.dienste.architektur2d3dklassen import Architektur2d3dklassen


class SeiteArchitektur2d3d(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.antwort = Client().get(reverse('hilfe_architektur_2d3d'))
        cls.text = cls.antwort.content.decode('utf-8')

    def test_antwortet_und_haengt_im_menue(self):
        self.assertEqual(self.antwort.status_code, 200)
        self.assertEqual(reverse('hilfe_architektur_2d3d'), '/hilfe/architektur/2d3d/')
        self.assertIn('href="/hilfe/architektur/2d3d/"', self.text)

    def test_jede_klasse_gibt_es_im_code(self):
        for modul, klasse in Architektur2d3dklassen.alle():
            zeile = Architektur2d3dklassen.zeile(modul, klasse)
            self.assertEqual(zeile['fehlt'], '', '%s in %s' % (klasse, modul))
            self.assertTrue(zeile['satz'], '%s ohne Docstring' % modul)
            self.assertNotIn('`', zeile['satz'])
            self.assertIn(escape(klasse), self.text)

    def test_die_klassen_der_ablaufschritte_stehen_im_katalog(self):
        katalog = {k for _m, k in Architektur2d3dklassen.alle()}
        for _nr, _wann, _was, klassen, _takt in Architektur2d3d.RUNDE:
            for k in klassen.split(', '):
                self.assertIn(k, katalog, k)

    def test_die_vorgabe_steht_vorn_und_die_wege_dahinter(self):
        """Edgar, 02.10.2026: „Vorgabe ist, du überprüfst und optimierst den Code … warum steht das da nicht???\""""
        self.assertIn(escape(Architektur2d3d.VORGABE), self.text)
        self.assertLess(self.text.index('Die Prüfung nach jeder Runde'), self.text.index('Wer schreibt das Rezept'))
        for schritt, _was in Architektur2d3d.PRUEFSCHLEIFE:
            self.assertIn(escape(schritt), self.text)
        for weg, _wann, _wer, _klassen in Architektur2d3d.WEGE:
            self.assertIn(escape(weg), self.text)

    def test_ein_fehlender_eintrag_wird_gezeigt_nicht_verschluckt(self):
        """Gegenprobe: eine erfundene Klasse muss als `fehlt` erscheinen."""
        zeile = Architektur2d3dklassen.zeile(Architektur2d3dklassen.D + 'teilevorrat.py', 'GibtEsNicht')
        self.assertIn('nicht in der Datei', zeile['fehlt'])
        self.assertIn('nicht lesbar', Architektur2d3dklassen.zeile('gibt/es/nicht.py', 'X')['fehlt'])
