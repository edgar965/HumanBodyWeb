# -*- coding: utf-8 -*-
"""Hilfe -> Recherche -> Human 3D (04.10.2026): die Datei der Projekte und die Tabelle daraus.

Zwei Dinge sind hier festgehalten, beide aus der Art, wie die Seite entsteht:
* Die Datei `core/daten/recherche_human3d.json` stammt aus fremden READMEs — Pflichtfelder, https-Adressen, eindeutige Kennungen und ein Repo-Name, der zur Adresse passt, werden
  gegen die ECHTE Datei geprüft (kein Muster, das nur gegen Kunstdaten grün ist).
* `Recherchetabelle` darf aus fremdem Text nie HTML oder eine `javascript:`-Adresse machen — mit Kunstprojekten, deren Felder genau das versuchen.
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from core.dienste.rechercheprio import Rechercheprio
from core.dienste.rechercheprojekte import Rechercheprojekte
from core.dienste.recherchetabelle import Recherchetabelle

from ._pruefablage import Pruefablage


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

    def test_jedes_bild_ist_eine_vorhandene_lokale_vorschau_oder_eine_https_adresse(self):
        static = Path(settings.BASE_DIR) / 'static'
        for p in Rechercheprojekte.projekte():
            for adresse in [p['bild'], *p['bilder']]:
                if not adresse:
                    continue
                if adresse.startswith('https://'):
                    continue
                self.assertRegex(adresse, Recherchetabelle.LOKAL, f'{p["repo"]}: {adresse}')
                self.assertTrue((static / adresse).is_file(), f'{p["repo"]}: {adresse} fehlt auf der Platte')

    def test_die_quellen_der_bilder_sind_https(self):
        for p in Rechercheprojekte.projekte():
            for quelle in [p.get('bild_quelle'), *(p.get('bilder_quellen') or [])]:
                if quelle:
                    self.assertTrue(quelle.startswith('https://'), f'{p["repo"]}: {quelle}')

    def test_ein_fork_nennt_sein_original_und_was_er_besser_macht(self):
        for p in Rechercheprojekte.projekte():
            if p.get('fork_von'):
                self.assertRegex(p['fork_von'], r'^[^/\s]+/[^/\s]+$', p['repo'])
                self.assertTrue((p.get('fork_grund') or '').strip(), f'{p["repo"]}: Fork ohne Grund')

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
        sterne, datum = zellen[6], zellen[7]
        self.assertEqual(sterne['sort'], 12345)
        self.assertEqual(sterne['html'], '12.345')
        self.assertEqual(datum['sort'], '2026-09-01')
        self.assertEqual(datum['html'], '01.09.2026')

    def test_die_zeile_traegt_die_kennung_und_die_todozelle_ihre_klasse(self):
        zeile = Recherchetabelle.bauen([_projekt()])['zeilen'][0]
        self.assertEqual(zeile['id'], 'a--b')
        self.assertEqual(zeile['zellen'][10]['klasse'], 'rc-todozelle')
        self.assertIn('data-id="a--b"', zeile['zellen'][10]['html'])

    def test_elf_spalten_in_der_verlangten_reihenfolge(self):
        kopf = [s['label'] for s in Recherchetabelle.bauen([])['spalten']]
        self.assertEqual(kopf, ['Name', 'Prio', 'Kurzbeschreibung', 'GitHub', 'Hugging Face', 'Hauptbild', 'Sterne bei GitHub', 'Letzte Aktualisierung', 'Beschreibung', 'Details', 'ToDo'])

    def test_die_prio_zelle_traegt_zahl_und_sortierwert(self):
        zellen = Recherchetabelle.bauen([_projekt(), _projekt(id='c--d', name='D', repo='c/d')], {'a--b': 3})['zeilen']
        mit, ohne = zellen[0]['zellen'][1], zellen[1]['zellen'][1]
        self.assertEqual(mit['sort'], 3)
        self.assertIn('value="3"', mit['html'])
        self.assertIn('data-id="a--b"', mit['html'])
        self.assertEqual(ohne['sort'], Rechercheprio.SORT_OHNE_PRIO)
        self.assertIn('value=""', ohne['html'])
        self.assertEqual(mit['klasse'], 'rc-priozelle')

    def test_die_hf_spalte_baut_die_adresse_aus_der_kennung_und_verwirft_fremdes(self):
        hf = [{'typ': 'space', 'id': 'o/demo', 'likes': 12}, {'typ': 'model', 'id': 'o/gewichte', 'likes': 3}, {'typ': 'dataset', 'id': 'o/daten', 'likes': 0},
              {'typ': 'model', 'id': 'javascript:1', 'likes': 1}, {'typ': 'unbekannt', 'id': 'o/x', 'likes': 1}, {'typ': 'space', 'id': 'o/../x', 'likes': 1}]
        zelle = Recherchetabelle.bauen([_projekt(hf=hf)])['zeilen'][0]['zellen'][4]
        self.assertEqual(zelle['sort'], 7)
        self.assertIn('href="https://huggingface.co/spaces/o/demo"', zelle['html'])
        self.assertIn('href="https://huggingface.co/o/gewichte"', zelle['html'])
        self.assertIn('href="https://huggingface.co/datasets/o/daten"', zelle['html'])
        self.assertNotIn('javascript:', zelle['html'])
        self.assertEqual(len(Recherchetabelle.hf_liste(_projekt(hf=hf))), 3)

    def test_ohne_hf_eintrag_steht_ein_strich_und_der_sortierwert_null(self):
        zelle = Recherchetabelle.bauen([_projekt()])['zeilen'][0]['zellen'][4]
        self.assertEqual(zelle['sort'], 0)
        self.assertIn('rc-fehlt', zelle['html'])

    def test_mehrere_gleicher_art_werden_nummeriert_und_das_fenster_bekommt_alle(self):
        hf = [{'typ': 'model', 'id': 'o/a', 'likes': 5}, {'typ': 'model', 'id': 'o/b', 'likes': 2}]
        html = Recherchetabelle.bauen([_projekt(hf=hf)])['zeilen'][0]['zellen'][4]['html']
        self.assertIn('Modell 1', html)
        self.assertIn('Modell 2', html)
        self.assertEqual([h['url'] for h in Recherchetabelle.popup([_projekt(hf=hf)])['a--b']['hf']], ['https://huggingface.co/o/a', 'https://huggingface.co/o/b'])

    def test_eine_lokale_vorschau_wird_zur_statikadresse_und_ein_fremder_pfad_nie(self):
        self.assertEqual(Recherchetabelle.bildadresse('recherche/human3d/a--b.webp'), '/static/recherche/human3d/a--b.webp')
        for falsch in ('recherche/human3d/../../x.webp', '/etc/passwd', 'recherche/human3d/a b.webp', 'recherche/andere/x.webp', 'http://x/y.png', 'javascript:1', None):
            self.assertEqual(Recherchetabelle.bildadresse(falsch), '', repr(falsch))

    def test_ein_fork_traegt_seine_zeile_unter_dem_namen(self):
        html = Recherchetabelle.bauen([_projekt(fork_von='x/orig', fork_grund='<b>mehr</b> Sterne')])['zeilen'][0]['zellen'][0]['html']
        self.assertIn('Fork von x/orig', html)
        self.assertNotIn('<b>mehr', html)
        self.assertNotIn('Fork von', Recherchetabelle.bauen([_projekt()])['zeilen'][0]['zellen'][0]['html'])

    def test_das_fenster_bekommt_nur_https_bilder(self):
        daten = Recherchetabelle.popup([_projekt(bilder=['https://x/y.png', 'http://x/z.png', 'javascript:1'])])['a--b']
        self.assertEqual(daten['bilder'], ['https://x/y.png'])


class DiePrio(SimpleTestCase):
    """Die Spalte „Prio" (Edgar: keine zwei gleichen, eine vergebene Zahl schiebt die anderen dazwischen)."""

    def test_eine_freie_zahl_wird_einfach_vergeben(self):
        self.assertEqual(Rechercheprio.verteilen({'a': 1, 'b': 5}, 'c', 3), {'a': 1, 'b': 5, 'c': 3})

    def test_eine_belegte_zahl_schiebt_den_bisherigen_nach_hinten(self):
        self.assertEqual(Rechercheprio.verteilen({'a': 1, 'b': 2}, 'c', 1), {'a': 2, 'b': 3, 'c': 1})

    def test_die_verschiebung_endet_beim_ersten_freien_platz(self):
        self.assertEqual(Rechercheprio.verteilen({'a': 1, 'b': 2, 'c': 5}, 'd', 1), {'a': 2, 'b': 3, 'c': 5, 'd': 1})

    def test_die_eingegebene_zahl_bleibt_wie_sie_ist(self):
        self.assertEqual(Rechercheprio.verteilen({'a': 1}, 'b', 10), {'a': 1, 'b': 10})

    def test_ein_projekt_das_umzieht_gibt_seinen_alten_platz_frei(self):
        self.assertEqual(Rechercheprio.verteilen({'a': 1, 'b': 2, 'c': 3}, 'a', 3), {'a': 3, 'b': 2, 'c': 4})
        self.assertEqual(Rechercheprio.verteilen({'a': 1, 'b': 2, 'c': 3}, 'c', 1), {'a': 2, 'b': 3, 'c': 1})

    def test_leer_nimmt_das_projekt_heraus_und_laesst_die_anderen_stehen(self):
        self.assertEqual(Rechercheprio.verteilen({'a': 1, 'b': 2}, 'a', None), {'b': 2})

    def test_keine_zwei_projekte_tragen_dieselbe_zahl(self):
        prios = {}
        for kennung, wert in [('a', 2), ('b', 2), ('c', 1), ('d', 2), ('a', 1), ('e', 3), ('b', None), ('f', 1)]:
            prios = Rechercheprio.verteilen(prios, kennung, wert)
            self.assertEqual(len(set(prios.values())), len(prios), prios)

    def test_die_eingabe_wird_geprueft_statt_gerundet(self):
        self.assertIsNone(Rechercheprio.normieren(None))
        self.assertIsNone(Rechercheprio.normieren('  '))
        self.assertEqual(Rechercheprio.normieren('4'), 4)
        self.assertEqual(Rechercheprio.normieren(4.0), 4)
        for falsch in ('abc', 2.5, 0, -1, Rechercheprio.HOECHSTENS + 1, True):
            with self.assertRaises(ValueError, msg=repr(falsch)):
                Rechercheprio.normieren(falsch)

    def test_gespeichert_wird_unter_objects_root_und_ueberlebt_das_neu_laden(self):
        with Pruefablage.ordner('recherche_prio_') as ordner, override_settings(OBJECTS_ROOT=ordner):
            self.assertEqual(Rechercheprio.laden(), {})
            Rechercheprio.setzen('a--b', 1)
            Rechercheprio.setzen('c--d', 1)
            self.assertEqual(Rechercheprio.laden(), {'c--d': 1, 'a--b': 2})
            self.assertTrue((Path(ordner) / 'recherche' / 'human3d_prio.json').is_file())
            Rechercheprio.setzen('c--d', None)
            self.assertEqual(Rechercheprio.laden(), {'a--b': 2})
