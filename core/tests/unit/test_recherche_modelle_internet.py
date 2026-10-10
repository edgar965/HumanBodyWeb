# -*- coding: utf-8 -*-
"""Hilfe -> Recherche -> Modelle Internet (10.10.2026): die Datei der Modelle und die Tabelle daraus.

Zwei Dinge sind hier festgehalten, beide aus der Art, wie die Seite entsteht:
* Die Datei `core/daten/recherche_modelle_internet.json` enthält Zahlen aus Messungen und Angaben fremder Seiten — Pflichtfelder, https-Adressen, eindeutige Kennungen,
  die Untergrenze von 200 MB und vorhandene Vorschaubilder werden gegen die ECHTE Datei geprüft (kein Muster, das nur gegen Kunstdaten grün ist).
* `Recherchemodelletabelle` darf aus fremdem Text nie HTML oder eine `javascript:`-Adresse machen — mit Kunstmodellen, deren Felder genau das versuchen.

Geschrieben, nicht gelaufen (Tests laufen nur auf Ansage). Gegenprobe vor dem ersten Lauf: die Untergrenze in der Datei auf 100 setzen → `test_jedes_modell_ist_mindestens_200_mb_gross`
muss rot werden; ein Bild umbenennen → `test_jedes_bild_ist_eine_vorhandene_lokale_vorschau` rot.
"""

import copy
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.recherchemodelleinternet import Recherchemodelleinternet
from core.dienste.recherchemodelletabelle import Recherchemodelletabelle


def _zellen(tabelle, nr=0):
    """Die Zellen einer Zeile nach Spaltenschlüssel — Zahlen als Index wären brüchig, sobald eine Spalte dazukommt."""
    return dict(zip([s['key'] for s in tabelle['spalten']], tabelle['zeilen'][nr]['zellen'], strict=True))


def _modell(**ueber):
    m = {
        'id': 'a', 'name': 'A', 'kurz': 'kurz', 'quellen': [{'label': 'quelle', 'url': 'https://example.org/a'}],
        'bild': 'recherche/modelle_internet/a.webp', 'bild_herkunft': 'irgendwo',
        'aufloesung': {'sort': 1000, 'zeilen': [{'text': '1.000 Dreiecke', 'beleg': 'gemessen'}]},
        'groesse': {'sort_mb': 250.5, 'zeilen': [{'text': '250,5 MB', 'beleg': 'angabe'}]},
        'dateityp': 'OBJ', 'downloads': [{'label': 'Paket', 'url': 'https://example.org/a.zip', 'groesse': '250,5 MB'}],
        'lizenz': 'CC0', 'lizenz_url': 'https://creativecommons.org/publicdomain/zero/1.0/', 'hinweis': 'Hinweis',
        'bewertung': {'urteil': 'bedingt', 'rang': 2, 'zeilen': [{'text': 'Grund', 'beleg': 'vermutung'}], 'naechster_schritt': 'Ansehen'},
    }
    m.update(ueber)
    return m


class DieDatei(SimpleTestCase):
    """Die echte Datei, wie sie ausgeliefert wird."""

    def test_sie_ist_da_und_hat_modelle(self):
        self.assertTrue(Recherchemodelleinternet.pfad().is_file())
        self.assertGreater(len(Recherchemodelleinternet.modelle()), 0)

    def test_jedes_modell_fuehrt_alle_pflichtfelder(self):
        for m in Recherchemodelleinternet.modelle():
            for feld in Recherchemodelleinternet.PFLICHT:
                self.assertIn(feld, m, f'{m.get("id")}: Feld {feld} fehlt')
            self.assertTrue(m['aufloesung']['zeilen'], f'{m["id"]}: Auflösung ohne Zeilen')
            self.assertTrue(m['groesse']['zeilen'], f'{m["id"]}: Größe ohne Zeilen')
            self.assertTrue(m['downloads'], f'{m["id"]}: kein Download-Link')
            self.assertTrue(m['quellen'], f'{m["id"]}: keine Quelle')

    def test_jede_zeile_traegt_einen_bekannten_beleg(self):
        for m in Recherchemodelleinternet.modelle():
            for block in ('aufloesung', 'groesse'):
                for zeile in m[block]['zeilen']:
                    self.assertIn(zeile['beleg'], Recherchemodelletabelle.BELEGE, f'{m["id"]}: {zeile["text"]}')

    def test_jede_bewertung_hat_ein_bekanntes_urteil_gruende_mit_beleg_und_einen_rang(self):
        for m in Recherchemodelleinternet.modelle():
            b = m['bewertung']
            self.assertIn(b['urteil'], Recherchemodelletabelle.URTEILE, m['id'])
            self.assertTrue(b['zeilen'], f'{m["id"]}: Bewertung ohne Gründe')
            for zeile in b['zeilen']:
                self.assertIn(zeile['beleg'], Recherchemodelletabelle.BELEGE, f'{m["id"]}: {zeile["text"]}')
            self.assertTrue(b['naechster_schritt'], f'{m["id"]}: kein nächster Schritt')

    def test_die_raenge_sind_eins_bis_n_und_folgen_den_urteilen(self):
        modelle = sorted(Recherchemodelleinternet.modelle(), key=lambda m: m['bewertung']['rang'])
        self.assertEqual([m['bewertung']['rang'] for m in modelle], list(range(1, len(modelle) + 1)))
        stufen = list(Recherchemodelletabelle.URTEILE)
        folge = [stufen.index(m['bewertung']['urteil']) for m in modelle]
        self.assertEqual(folge, sorted(folge), 'ein schlechteres Urteil steht vor einem besseren')

    def test_kennungen_sind_eindeutig(self):
        kennungen = [m['id'] for m in Recherchemodelleinternet.modelle()]
        self.assertEqual(len(kennungen), len(set(kennungen)))

    def test_jedes_modell_ist_mindestens_200_mb_gross(self):
        for m in Recherchemodelleinternet.modelle():
            self.assertGreaterEqual(m['groesse']['sort_mb'], Recherchemodelleinternet.MINDESTGROESSE_MB, m['id'])

    def test_jeder_dateityp_nennt_obj_fbx_oder_blender(self):
        for m in Recherchemodelleinternet.modelle():
            self.assertRegex(m['dateityp'], re.compile(r'\b(OBJ|FBX|\.?blend|Blender)\b', re.IGNORECASE), m['id'])

    def test_alle_adressen_sind_https(self):
        daten = Recherchemodelleinternet.laden()
        adressen = [n['url'] for n in daten['meta']['nicht_aufgenommen']]
        for m in daten['modelle']:
            adressen += [q['url'] for q in m['quellen']] + [d['url'] for d in m['downloads']] + [m['lizenz_url']]
        for adresse in adressen:
            self.assertTrue(adresse.startswith('https://'), adresse)

    def test_jedes_bild_ist_eine_vorhandene_lokale_vorschau(self):
        static = Path(settings.BASE_DIR) / 'static'
        for m in Recherchemodelleinternet.modelle():
            self.assertRegex(m['bild'], Recherchemodelletabelle.LOKAL, m['id'])
            self.assertTrue((static / m['bild']).is_file(), f'{m["id"]}: {m["bild"]} fehlt auf der Platte')

    def test_die_modelle_stehen_nach_den_dreiecken_absteigend(self):
        werte = [int(m['aufloesung']['sort']) for m in Recherchemodelleinternet.modelle()]
        self.assertEqual(werte, sorted(werte, reverse=True))


class DieTabelle(SimpleTestCase):
    """`Recherchemodelletabelle.bauen` — Spalten, Sortierwerte und der Umgang mit fremdem Text."""

    def test_die_spalten_sind_die_verlangten(self):
        tabelle = Recherchemodelletabelle.bauen([_modell()])
        self.assertEqual([s['key'] for s in tabelle['spalten']],
                         ['bild', 'name', 'bewertung', 'quelle', 'aufloesung', 'groesse', 'dateityp', 'download', 'lizenz'])

    def test_jede_zeile_hat_so_viele_zellen_wie_die_tabelle_spalten(self):
        tabelle = Recherchemodelletabelle.bauen(Recherchemodelleinternet.modelle())
        for zeile in tabelle['zeilen']:
            self.assertEqual(len(zeile['zellen']), len(tabelle['spalten']))
        self.assertEqual(len(tabelle['zeilen']), len(Recherchemodelleinternet.modelle()))

    def test_aufloesung_und_groesse_sortieren_nach_dem_rohwert(self):
        z = _zellen(Recherchemodelletabelle.bauen([_modell()]))
        self.assertEqual(z['aufloesung']['sort'], 1000)
        self.assertEqual(z['groesse']['sort'], 250.5)
        self.assertNotIsInstance(z['groesse']['sort'], str)

    def test_die_vorschau_hat_keine_sortierung_und_der_download_auch_nicht(self):
        kopf = {s['key']: s for s in Recherchemodelletabelle.kopf()}
        self.assertTrue(kopf['bild']['sortAus'])
        self.assertTrue(kopf['download']['sortAus'])
        self.assertFalse(kopf['groesse']['sortAus'])

    def test_fremder_text_wird_maskiert(self):
        boese = '<script>alert(1)</script>'
        m = _modell(name=boese, kurz=boese, hinweis=boese, dateityp=boese, lizenz=boese)
        m['aufloesung'] = {'sort': 1, 'zeilen': [{'text': boese, 'beleg': 'gemessen'}]}
        m['bewertung'] = {'urteil': 'bedingt', 'rang': 1, 'zeilen': [{'text': boese, 'beleg': 'vermutung'}], 'naechster_schritt': boese}
        z = _zellen(Recherchemodelletabelle.bauen([m]))
        for schluessel, zelle in z.items():
            self.assertNotIn('<script>', zelle['html'], schluessel)
        self.assertIn('&lt;script&gt;', z['name']['html'])

    def test_eine_adresse_ohne_https_wird_kein_link(self):
        m = _modell(downloads=[{'label': 'Paket', 'url': 'javascript:alert(1)', 'groesse': '1 MB'}],
                    quellen=[{'label': 'Q', 'url': 'http://example.org/a'}], lizenz_url='ftp://example.org/l')
        z = _zellen(Recherchemodelletabelle.bauen([m]))
        for schluessel in ('download', 'quelle', 'lizenz'):
            self.assertNotIn('href=', z[schluessel]['html'], schluessel)

    def test_ein_bild_ausserhalb_der_ablage_ist_kein_bild(self):
        for adresse in ('../../static/x.webp', 'recherche/human3d/x.webp', 'https://example.org/x.png', '/etc/passwd'):
            z = _zellen(Recherchemodelletabelle.bauen([_modell(bild=adresse)]))
            self.assertNotIn('<img', z['bild']['html'], adresse)

    def test_ein_bild_der_ablage_wird_unter_static_ausgeliefert(self):
        z = _zellen(Recherchemodelletabelle.bauen([_modell()]))
        self.assertIn('src="/static/recherche/modelle_internet/a.webp"', z['bild']['html'])

    def test_der_beleg_steht_an_jeder_zeile(self):
        m = copy.deepcopy(_modell())
        z = _zellen(Recherchemodelletabelle.bauen([m]))
        self.assertIn('mi-beleg-gemessen', z['aufloesung']['html'])
        self.assertIn('mi-beleg-angabe', z['groesse']['html'])

    def test_die_bewertung_zeigt_urteil_rang_grund_und_schritt_und_sortiert_nach_dem_rang(self):
        z = _zellen(Recherchemodelletabelle.bauen([_modell()]))
        self.assertIn('mi-urteil-bedingt', z['bewertung']['html'])
        self.assertIn('Rang 2', z['bewertung']['html'])
        self.assertIn('Grund', z['bewertung']['html'])
        self.assertIn('mi-beleg-vermutung', z['bewertung']['html'])
        self.assertIn('Nächster Schritt', z['bewertung']['html'])
        self.assertEqual(z['bewertung']['sort'], 2)

    def test_ein_unbekanntes_urteil_wird_maskiert_statt_ausgegeben(self):
        m = _modell()
        m['bewertung']['urteil'] = '"><script>x</script>'
        z = _zellen(Recherchemodelletabelle.bauen([m]))
        self.assertNotIn('<script>', z['bewertung']['html'])

    def test_ohne_modelle_steht_der_leer_text(self):
        tabelle = Recherchemodelletabelle.bauen([])
        self.assertEqual(tabelle['zeilen'], [])
        self.assertIn('recherche_modelle_internet.json', tabelle['leer'])
