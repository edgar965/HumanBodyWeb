# -*- coding: utf-8 -*-
"""Tests fuer Bvhbibliothek — Suche, Filter, Seitenaufteilung.

Der Anlass ist der Performance-Durchgang (16.08.2026): `/library/` rendete alle
7.110 Eintraege in einer Antwort. Zwei Dinge sollen die Tests festhalten —
erstens dass nicht mehr als JE_SEITE Karten auf eine Seite kommen, zweitens der
`distinct()`-Fehlgriff aus dem ersten Bauversuch: mit Modell-Standardsortierung
liefert `values_list('source').distinct()` eine Zeile je Datei, nicht je Quelle.
"""

from django.test import TestCase

from core.dienste.bvhbibliothek import Bvhbibliothek
from core.models import BVHFile


class BvhbibliothekTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        for i in range(75):
            BVHFile.objects.create(
                name='walk_%03d' % i, path='/x/walk_%03d.bvh' % i, source='cmu')
        for i in range(5):
            BVHFile.objects.create(
                name='jump_%03d' % i, path='/x/jump_%03d.bvh' % i, source='gvhmr')

    def test_erste_seite_hat_hoechstens_je_seite_eintraege(self):
        inhalt = Bvhbibliothek().seiteninhalt()
        self.assertEqual(len(inhalt.object_list), Bvhbibliothek.JE_SEITE)
        self.assertEqual(inhalt.paginator.count, 80)

    def test_letzte_seite_hat_den_rest(self):
        inhalt = Bvhbibliothek(seite=2).seiteninhalt()
        self.assertEqual(len(inhalt.object_list), 20)
        self.assertFalse(inhalt.has_next())

    def test_suche_filtert_nach_name(self):
        inhalt = Bvhbibliothek(suche='jump').seiteninhalt()
        self.assertEqual(inhalt.paginator.count, 5)
        self.assertTrue(all('jump' in f.name for f in inhalt.object_list))

    def test_suche_ist_gross_klein_unabhaengig(self):
        self.assertEqual(Bvhbibliothek(suche='JUMP').seiteninhalt().paginator.count, 5)

    def test_quellfilter(self):
        self.assertEqual(Bvhbibliothek(quelle='gvhmr').seiteninhalt().paginator.count, 5)

    def test_suche_und_quelle_wirken_zusammen(self):
        # 'walk' gibt es nur mit Quelle cmu — die Kombination muss leer bleiben.
        self.assertEqual(
            Bvhbibliothek(suche='walk', quelle='gvhmr').seiteninhalt().paginator.count, 0)

    def test_quellen_sind_eindeutig(self):
        """Der distinct()-Fehlgriff: vorher kam eine Zeile je DATEI zurueck."""
        self.assertEqual(Bvhbibliothek().quellen(), ['cmu', 'gvhmr'])

    def test_leere_quelle_faellt_aus_der_liste(self):
        BVHFile.objects.create(name='ohne', path='/x/ohne.bvh', source='')
        self.assertNotIn('', Bvhbibliothek().quellen())

    def test_zusatzfrage_erhaelt_filter_in_seitenlinks(self):
        self.assertEqual(Bvhbibliothek(suche='a', quelle='b').zusatzfrage(),
                         '&q=a&source=b')
        self.assertEqual(Bvhbibliothek().zusatzfrage(), '')

    def test_unsinnige_seitenzahl_liefert_erste_seite(self):
        """get_page() faengt ab — sonst waere jeder falsche Link ein Fehler 500."""
        self.assertEqual(Bvhbibliothek(seite='abc').seiteninhalt().number, 1)
        self.assertEqual(Bvhbibliothek(seite=9999).seiteninhalt().number, 2)

    def test_reihenfolge_ist_stabil(self):
        eins = [f.pk for f in Bvhbibliothek(seite=1).seiteninhalt()]
        zwei = [f.pk for f in Bvhbibliothek(seite=2).seiteninhalt()]
        self.assertEqual(len(set(eins) & set(zwei)), 0)

    def test_aus_anfrage_liest_die_parameter(self):
        antwort = self.client.get('/library/?q=jump&source=gvhmr')
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.context['gesamt'], 5)
        self.assertEqual(antwort.context['suche'], 'jump')

    def test_seite_bleibt_klein(self):
        """Kern des Befunds: die Antwort darf nicht mit der Tabelle wachsen."""
        antwort = self.client.get('/library/')
        self.assertLess(len(antwort.content), 200_000)
        self.assertEqual(antwort.content.count(b'class="bvh-card"'),
                         Bvhbibliothek.JE_SEITE)
