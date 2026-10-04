# -*- coding: utf-8 -*-
"""Hilfe -> Recherche -> Human 3D (04.10.2026): die Datei der Projekte und die Tabelle daraus.

Zwei Dinge sind hier festgehalten, beide aus der Art, wie die Seite entsteht:
* Die Datei `core/daten/recherche_human3d.json` stammt aus fremden READMEs — Pflichtfelder, https-Adressen, eindeutige Kennungen und ein Repo-Name, der zur Adresse passt, werden
  gegen die ECHTE Datei geprüft (kein Muster, das nur gegen Kunstdaten grün ist).
* `Recherchetabelle` darf aus fremdem Text nie HTML oder eine `javascript:`-Adresse machen — mit Kunstprojekten, deren Felder genau das versuchen.
"""

import re

from django.test import SimpleTestCase

from core.dienste.rechercheprojekte import Rechercheprojekte
from core.dienste.recherchetabelle import Recherchetabelle


def _projekt(**ueber):
    p = {
        'id': 'a--b', 'name': 'B', 'repo': 'a/b', 'url': 'https://github.com/a/b', 'kategorie': 'Körper aus Foto', 'kurz': 'kurz', 'beschreibung': 'lang',
        'details': ['Eingabe: Foto'], 'bild': 'https://raw.githubusercontent.com/a/b/main/t.png', 'bilder': ['https://raw.githubusercontent.com/a/b/main/u.png'],
        'sterne': 12345, 'angelegt': '2025-01-02', 'aktualisiert': '2026-09-01', 'todo_kurz': 'fehlt', 'todo': ['Eins', 'Zwei'], 'sprache': 'Python', 'lizenz': 'MIT',
    }
    p.update(ueber)
    return p


class DieDatei(SimpleTestCase):
    """Die echte Datei, wie sie ausgeliefert wird."""

    def test_sie_ist_da_und_hat_projekte(self):
        self.assertTrue(Rechercheprojekte.pfad().is_file())
        self.assertGreater(len(Rechercheprojekte.projekte()), 0)

    def test_jedes_projekt_fuehrt_alle_pflichtfelder(self):
        for p in Rechercheprojekte.projekte():
            for feld in Rechercheprojekte.PFLICHT:
                self.assertIn(feld, p, f'{p.get("repo")}: Feld {feld} fehlt')
            self.assertTrue(p['todo'] and isinstance(p['todo'], list), f'{p["repo"]}: ToDo leer')
            self.assertTrue(p['details'] and isinstance(p['details'], list), f'{p["repo"]}: Details leer')

    def test_kennungen_sind_eindeutig_und_die_adresse_passt_zum_repo(self):
        gesehen = set()
        for p in Rechercheprojekte.projekte():
            self.assertNotIn(p['id'], gesehen)
            gesehen.add(p['id'])
            self.assertEqual(p['url'], f'https://github.com/{p["repo"]}')

    def test_alle_bildadressen_sind_https(self):
        for p in Rechercheprojekte.projekte():
            for adresse in [p['bild'], *p['bilder']]:
                if adresse:
                    self.assertTrue(adresse.startswith('https://'), f'{p["repo"]}: {adresse}')

    def test_die_kategorie_steht_in_der_liste(self):
        erlaubt = set(Rechercheprojekte.kategorien())
        for p in Rechercheprojekte.projekte():
            self.assertIn(p['kategorie'], erlaubt, p['repo'])

    def test_der_zeitraum_gilt_fuer_alle(self):
        ab = Rechercheprojekte.meta().get('zeitraum_ab')
        self.assertTrue(re.fullmatch(r'\d{4}-\d{2}-\d{2}', ab or ''))
        for p in Rechercheprojekte.projekte():
            self.assertGreaterEqual(p['angelegt'][:10], ab, p['repo'])

    def test_die_sterne_sind_zahlen_und_nach_sternen_sortiert(self):
        sterne = [p['sterne'] for p in Rechercheprojekte.projekte()]
        self.assertTrue(all(isinstance(s, int) for s in sterne))
        self.assertEqual(sterne, sorted(sterne, reverse=True))


class DieTabelle(SimpleTestCase):
    def test_fremder_text_wird_maskiert(self):
        zeile = Recherchetabelle.bauen([_projekt(name='<script>x</script>', kurz='<img src=x onerror=y>', todo_kurz='"><b>')])['zeilen'][0]
        html = ''.join(z['html'] for z in zeile['zellen'])
        self.assertNotIn('<script>', html)
        self.assertNotIn('<img src=x', html)
        self.assertNotIn('"><b>', html)

    def test_eine_fremde_adresse_wird_kein_link_und_kein_bild(self):
        zeile = Recherchetabelle.bauen([_projekt(url='javascript:alert(1)', bild='javascript:alert(2)')])['zeilen'][0]
        html = ''.join(z['html'] for z in zeile['zellen'])
        self.assertNotIn('javascript:', html)
        self.assertNotIn('<img', html)

    def test_sterne_und_datum_tragen_den_rohwert_zum_sortieren(self):
        zellen = Recherchetabelle.bauen([_projekt()])['zeilen'][0]['zellen']
        sterne, datum = zellen[4], zellen[5]
        self.assertEqual(sterne['sort'], 12345)
        self.assertEqual(sterne['html'], '12.345')
        self.assertEqual(datum['sort'], '2026-09-01')
        self.assertEqual(datum['html'], '01.09.2026')

    def test_die_zeile_traegt_die_kennung_und_die_todozelle_ihre_klasse(self):
        zeile = Recherchetabelle.bauen([_projekt()])['zeilen'][0]
        self.assertEqual(zeile['id'], 'a--b')
        self.assertEqual(zeile['zellen'][8]['klasse'], 'rc-todozelle')
        self.assertIn('data-id="a--b"', zeile['zellen'][8]['html'])

    def test_neun_spalten_in_der_verlangten_reihenfolge(self):
        kopf = [s['label'] for s in Recherchetabelle.bauen([])['spalten']]
        self.assertEqual(kopf, ['Name', 'Kurzbeschreibung', 'GitHub', 'Hauptbild', 'Sterne bei GitHub', 'Letzte Aktualisierung', 'Beschreibung', 'Details', 'ToDo'])

    def test_das_fenster_bekommt_nur_https_bilder(self):
        daten = Recherchetabelle.popup([_projekt(bilder=['https://x/y.png', 'http://x/z.png', 'javascript:1'])])['a--b']
        self.assertEqual(daten['bilder'], ['https://x/y.png'])
