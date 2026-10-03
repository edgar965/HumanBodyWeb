# -*- coding: utf-8 -*-
"""Der Reiter „Tools" der Seite Hilfe → Architektur → 2D3D (03.10.2026): die Sammlung der Werkzeuggruppen und ihr Klassenmodell.

WARUM: Die Seite soll anderen Sessions sagen, welches Werkzeug sie wie aufrufen. Eine Zeile mit einer Klasse, die es nicht gibt, wäre der Fehler,
den die Seite verhindern soll — deshalb prüft `Architektur2d3dwerkzeuge` jede Klasse gegen den Code und meldet Fehlendes als Befund. Diese Tests halten fest,
dass das Schema gelesen wird (Zeilen, Klassenmodell, Beziehungen in beide Richtungen), dass Fehlendes als Befund erscheint, und dass die echten Gruppen keinen Befund haben."""

import re
from unittest import mock

from django.test import SimpleTestCase

from core.dienste.architektur2d3dwerkzeuge import Architektur2d3dwerkzeuge

KLASSEN = 'HumanBodyWeb/core/dienste/architektur2d3dklassen.py'
WERKZEUG = 'HumanBodyWeb/core/dienste/architektur2d3dwerkzeuge.py'


class Probe:
    KENNUNG = 'probe'
    TITEL = 'Probegruppe'
    EINLEITUNG = 'Zuerst die Klassenkarten, dann die Werkzeuge.'
    ZEILEN = [
        ('Klassenkarte lesen', 'Liest eine Klasse aus dem Code.', 'python',
         "Architektur2d3dklassen.zeile(modul, klasse)",
         [(KLASSEN, 'Architektur2d3dklassen'), (WERKZEUG, 'Architektur2d3dwerkzeuge')], 'Nur lesen.'),
        ('Gruppen sammeln', 'Findet die Gruppen.', 'python', 'Architektur2d3dwerkzeuge.kontext()',
         [(WERKZEUG, 'Architektur2d3dwerkzeuge')], ''),
    ]
    BEZIEHUNGEN = [('Architektur2d3dwerkzeuge', 'ruft', 'Architektur2d3dklassen', 'zeile(): liest Docstring und Methoden')]


class ProbeMitFehlern:
    KENNUNG = 'fehler'
    TITEL = 'Fehler'
    EINLEITUNG = 'Mit Fehlern.'
    ZEILEN = [
        ('Gibt es nicht', 'Klasse fehlt.', 'api', 'GET /gibt/es/nicht/', [(KLASSEN, 'KlasseDieEsNichtGibt')], ''),
        ('Unbekannte Art', 'Art ist neu.', 'zauber', 'abrakadabra', [(KLASSEN, 'Architektur2d3dklassen')], ''),
    ]
    BEZIEHUNGEN = [('Architektur2d3dklassen', 'ruft', 'KlasseOhneZeile', 'nirgends')]


def kontext_mit(*gruppen):
    gefunden = [('werkzeug' + g.KENNUNG, g, '') for g in gruppen]
    with mock.patch.object(Architektur2d3dwerkzeuge, 'gruppenklassen', return_value=gefunden):
        return Architektur2d3dwerkzeuge.kontext()


class WerkzeugeKontextTest(SimpleTestCase):
    def test_die_zeilen_der_gruppe_tragen_art_aufruf_und_geprueft_vorhandene_klassen(self):
        gruppe = kontext_mit(Probe)['gruppen'][0]
        z = gruppe['zeilen'][0]
        self.assertEqual((z['art'], z['art_text']), ('python', 'Python'))
        self.assertEqual([k['klasse'] for k in z['klassen']], ['Architektur2d3dklassen', 'Architektur2d3dwerkzeuge'])
        self.assertEqual([k['fehlt'] for k in z['klassen']], ['', ''])
        self.assertEqual(z['klassen'][0]['anker'], 't-probe-Architektur2d3dklassen')

    def test_das_klassenmodell_zeigt_methoden_aufrufe_und_beziehungen_in_beide_richtungen(self):
        modell = {k['klasse']: k for k in kontext_mit(Probe)['gruppen'][0]['modell']}
        self.assertEqual(set(modell), {'Architektur2d3dklassen', 'Architektur2d3dwerkzeuge'})
        self.assertIn('zeile', modell['Architektur2d3dklassen']['methoden'])
        self.assertGreater(modell['Architektur2d3dklassen']['zeilen'], 100)
        ruft = modell['Architektur2d3dwerkzeuge']['ruft']
        self.assertEqual([(r['klasse'], r['womit']) for r in ruft], [('Architektur2d3dklassen', 'zeile(): liest Docstring und Methoden')])
        self.assertEqual([g['klasse'] for g in modell['Architektur2d3dklassen']['gerufen_von']], ['Architektur2d3dwerkzeuge'])
        self.assertEqual(ruft[0]['anker'], modell['Architektur2d3dklassen']['anker'])

    def test_einstieg_ist_die_erste_klasse_der_zeile_die_anderen_sind_beteiligt(self):
        modell = {k['klasse']: k for k in kontext_mit(Probe)['gruppen'][0]['modell']}
        einstieg = {a['werkzeug']: a['einstieg'] for a in modell['Architektur2d3dwerkzeuge']['aufrufe']}
        self.assertEqual(einstieg, {'Klassenkarte lesen': False, 'Gruppen sammeln': True})
        self.assertEqual([a['einstieg'] for a in modell['Architektur2d3dklassen']['aufrufe']], [True])

    def test_die_zaehlung_stimmt_mit_den_gruppen_ueberein(self):
        z = kontext_mit(Probe)['zaehlung']
        self.assertEqual(z, {'gruppen': 1, 'werkzeuge': 2, 'klassen': 2, 'beziehungen': 1})


class WerkzeugeBefundTest(SimpleTestCase):
    def test_eine_klasse_die_es_nicht_gibt_steht_als_befund_und_rot_in_der_zeile(self):
        kontext = kontext_mit(ProbeMitFehlern)
        zeile = kontext['gruppen'][0]['zeilen'][0]
        self.assertIn('nicht in der Datei', zeile['klassen'][0]['fehlt'])
        self.assertTrue(any('KlasseDieEsNichtGibt' in b for b in kontext['befunde']))

    def test_eine_unbekannte_art_steht_als_befund(self):
        kontext = kontext_mit(ProbeMitFehlern)
        self.assertTrue(any('unbekannte Art' in b and 'zauber' in b for b in kontext['befunde']))

    def test_eine_beziehung_zu_einer_klasse_ausserhalb_der_zeilen_steht_als_befund(self):
        kontext = kontext_mit(ProbeMitFehlern)
        self.assertTrue(any('KlasseOhneZeile' in b for b in kontext['befunde']))

    def test_eine_gruppe_ohne_klasse_wird_ein_befund_und_bricht_die_seite_nicht(self):
        with mock.patch.object(Architektur2d3dwerkzeuge, 'gruppenklassen', return_value=[('werkzeugkaputt', None, 'Import schlug fehl')]):
            kontext = Architektur2d3dwerkzeuge.kontext()
        self.assertEqual(kontext['befunde'], ['werkzeugkaputt: Import schlug fehl'])
        self.assertEqual(kontext['gruppen'][0]['zeilen'], [])


class WerkzeugeEchteGruppenTest(SimpleTestCase):
    def test_jede_echte_gruppe_hat_kennung_titel_und_zeilen_und_keinen_befund(self):
        kontext = Architektur2d3dwerkzeuge.kontext()
        self.assertEqual(kontext['befunde'], [])
        kennungen = [g['kennung'] for g in kontext['gruppen']]
        self.assertEqual(len(kennungen), len(set(kennungen)), 'Kennungen müssen eindeutig sein (sie sind die Anker der Seite)')
        for g in kontext['gruppen']:
            self.assertTrue(g['titel'].strip() and g['einleitung'].strip(), g['kennung'])
            self.assertGreater(len(g['zeilen']), 0, g['kennung'])

    def test_jede_zeile_der_echten_gruppen_ist_vollstaendig_und_ohne_umschreibung(self):
        for g in Architektur2d3dwerkzeuge.kontext()['gruppen']:
            for z in g['zeilen']:
                stelle = '%s / %s' % (g['kennung'], z['werkzeug'])
                self.assertTrue(z['werkzeug'].strip() and z['wofuer'].strip() and z['aufruf'].strip(), stelle)
                self.assertIn(z['art'], Architektur2d3dwerkzeuge.ARTEN, stelle)
                self.assertTrue(z['klassen'] or z['art'] in ('regel', 'seite'), stelle + ': ohne Klasse')
                self.assertIsNone(re.search(r'\b(fuer|ueber|Faelle|Koerper|Staerke|Ruecken|moeglich)\b', z['wofuer'] + ' ' + z['hinweis']), stelle)

    def test_jede_rezeptzeile_nennt_eine_methode_die_es_im_code_gibt(self):
        from pathlib import Path

        from django.conf import settings
        wurzel = Path(settings.TOOLS_ROOT)
        quellen = ''
        for ordner in ('Genesis9', '2d3DIterationen', 'HumanBodyWeb/core/dienste'):
            for datei in (wurzel / ordner).rglob('*.py'):
                quellen += datei.read_text(encoding='utf-8', errors='replace')
        for g in Architektur2d3dwerkzeuge.kontext()['gruppen']:
            for z in g['zeilen']:
                if z['art'] != 'rezept':
                    continue
                for name in re.findall(r'\bm\.([a-z_0-9]+)\(', z['aufruf']):
                    self.assertIn('def %s(' % name, quellen, '%s / %s: m.%s gibt es nicht' % (g['kennung'], z['werkzeug'], name))
