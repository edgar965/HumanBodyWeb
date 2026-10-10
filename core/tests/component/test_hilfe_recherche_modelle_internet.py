# -*- coding: utf-8 -*-
"""Hilfe -> Recherche -> Modelle Internet (10.10.2026): die Seite steht, hängt im Menü und zeigt jede Zeile der Datei.

Edgar: „baue dafür eine neue Seite Hilfe - Recherche - Modelle Internet" — „schreibe die Links, Vorschau (Icon), Auflösung, Größe, Dateityp, Download-Link in eine neue
Django-Base-Tabelle". Geprüft: die Seite antwortet; sie ist eine djangoBase-Tabelle (`db-tabelle sortable`, `data-sort-key`); jedes Modell, jeder Download und jede Vorschau der
echten Datei steht darauf; das Bildfenster und das Modul sind eingebunden; der Menüpunkt zeigt auf die Adresse.

Geschrieben, nicht gelaufen (Tests laufen nur auf Ansage).
"""

from django.test import Client, SimpleTestCase
from django.urls import resolve, reverse
from django.utils.html import escape

from core.dienste.recherchemodelleinternet import Recherchemodelleinternet
from ui.settings.djangobase_menue import HILFE_EXTRA


class SeiteModelleInternet(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.antwort = Client().get(reverse('hilfe_recherche_modelle_internet'))
        cls.html = cls.antwort.content.decode('utf-8')

    def test_die_adresse_ist_die_verlangte(self):
        self.assertEqual(reverse('hilfe_recherche_modelle_internet'), '/hilfe/recherche/modelle-internet/')
        self.assertEqual(resolve('/hilfe/recherche/modelle-internet/').url_name, 'hilfe_recherche_modelle_internet')

    def test_die_seite_antwortet(self):
        self.assertEqual(self.antwort.status_code, 200)

    def test_die_tabelle_ist_eine_djangobase_tabelle(self):
        self.assertIn('class="db-tabelle sortable mi-tabelle"', self.html)
        self.assertIn('data-sort-key="hilfe-recherche-modelle-internet"', self.html)

    def test_jedes_modell_jeder_download_und_jede_vorschau_steht_auf_der_seite(self):
        for m in Recherchemodelleinternet.modelle():
            self.assertIn(f'data-id="{m["id"]}"', self.html)
            self.assertIn(escape(m['name']), self.html)
            self.assertIn('/static/' + m['bild'], self.html)
            for d in m['downloads']:
                self.assertIn(escape(d['url']), self.html, f'{m["id"]}: {d["label"]}')

    def test_alle_neun_spalten_stehen_im_kopf(self):
        for kopf in ('Vorschau', 'Modell', 'Bewertung', 'Quelle', 'Auflösung', 'Größe', 'Dateityp', 'Download', 'Lizenz'):
            self.assertIn(kopf, self.html)

    def test_jede_bewertung_steht_mit_urteil_und_rang_auf_der_seite(self):
        for m in Recherchemodelleinternet.modelle():
            b = m['bewertung']
            self.assertIn(f'mi-urteil-{b["urteil"]}', self.html)
            self.assertIn(f'Rang {b["rang"]}', self.html)
            self.assertIn(escape(b['naechster_schritt']), self.html)

    def test_der_massstab_der_bewertung_steht_unter_der_tabelle(self):
        self.assertIn('id="mi-bewertung"', self.html)
        for k in Recherchemodelleinternet.meta()['bewertung']['massstab']:
            self.assertIn(escape(k), self.html)

    def test_das_bildfenster_und_das_modul_sind_eingebunden(self):
        self.assertIn('id="mi-bildfenster"', self.html)
        self.assertIn('recherchemodelleinternet.js', self.html)
        self.assertIn('hilfe_recherche_modelle_internet.css', self.html)

    def test_die_nicht_aufgenommenen_stehen_mit_grund_darunter(self):
        for n in Recherchemodelleinternet.meta()['nicht_aufgenommen']:
            self.assertIn(escape(n['grund']), self.html)


class MenuModelleInternet(SimpleTestCase):

    def test_der_punkt_haengt_unter_recherche_und_zeigt_auf_die_seite(self):
        recherche = next(g for g in HILFE_EXTRA if g['label'] == 'Recherche')
        punkt = next(p for p in recherche['untermenu'] if p['label'] == 'Modelle Internet')
        self.assertEqual(punkt['url'], reverse('hilfe_recherche_modelle_internet'))
        self.assertEqual(punkt['aktiv'], 'hilfe_recherche_modelle_internet')
