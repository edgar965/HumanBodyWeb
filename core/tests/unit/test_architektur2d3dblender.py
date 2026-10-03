# -*- coding: utf-8 -*-
"""Die Tabelle „Wie liefe das mit Blender" im Reiter „Tools" (03.10.2026): lokales Werkzeug links, Blender-Werkzeug rechts.

WARUM (Edgar, 03.10.2026: „mach bei den Tools einen Vergleich, wie das mit Blender laufen würde. Also eine Tabelle, wo rechts die Blender-Spalte ist"): Eine Zeile, die ein lokales
Werkzeug mit einer Klasse nennt, die es nicht gibt, oder einen Stand erfindet, den die Seite nicht kennt, wäre der Fehler, den die Seite verhindern soll. Die Tests halten fest, dass das
Schema gelesen wird, die Stände gezählt werden und Fehlendes als Befund erscheint — und dass die echten Abschnitte keinen Befund haben."""

import re
from unittest import mock

from django.test import SimpleTestCase

from core.dienste.architektur2d3dblender import Architektur2d3dblender

KLASSEN = 'HumanBodyWeb/core/dienste/architektur2d3dklassen.py'


class Probe:
    KENNUNG = 'probe'
    TITEL = 'Probeabschnitt'
    EINLEITUNG = 'Zwei Aufgaben.'
    ZEILEN = [
        ('Klassen lesen', 'Klassenkarte', 'Architektur2d3dklassen.zeile(modul, klasse)', [(KLASSEN, 'Architektur2d3dklassen')],
         'ast.parse', 'ast.parse(text)', 'vorhanden', 'Beides liest Quelltext.'),
        ('Gruppen sammeln', 'Sammlung', 'Architektur2d3dblender.kontext()', [], 'Add-on X', 'bpy.ops.x()', 'addon', 'Nur als Add-on.'),
    ]


class ProbeMitFehlern:
    KENNUNG = 'fehler'
    TITEL = 'Fehler'
    EINLEITUNG = 'Mit Fehlern.'
    ZEILEN = [
        ('Klasse fehlt', 'Werkzeug', 'x()', [(KLASSEN, 'KlasseDieEsNichtGibt')], 'Blender-Werkzeug', 'bpy.x()', 'genutzt', 'Beleg fehlt.'),
        ('Stand unbekannt', 'Werkzeug', 'y()', [(KLASSEN, 'Architektur2d3dklassen')], 'Blender-Werkzeug', 'bpy.y()', 'zauberhaft', ''),
    ]


class ProbeMitZeiten:
    KENNUNG = 'zeiten'
    TITEL = 'Zeiten'
    EINLEITUNG = 'Drei Zeilen.'
    ZEILEN = [
        ('Beide gemessen', 'Lokal', 'a()', [], 'Blender', 'b()', 'genutzt', 'Beleg README.',
         '2,1 s (Szene A; Stoffsolver/README.md, 02.10.2026)', '55,0 s (Szene A; Stoffsolver/README.md, 02.10.2026)'),
        ('Nur lokal gemessen', 'Lokal', 'a()', [], 'Blender', 'b()', 'vorhanden', 'Nur lokal.',
         '0,5 s (Szene B; workflowzeiten.py)', 'nicht gemessen'),
        ('Keine Zeit', 'Lokal', 'a()', [], 'Blender', 'b()', 'keins', 'Gibt es nicht.', 'entfällt', 'entfällt'),
    ]


def kontext_mit(*klassen):
    gefunden = [('blendervergleich' + k.KENNUNG, k, '') for k in klassen]
    with mock.patch.object(Architektur2d3dblender, 'abschnittsklassen', return_value=gefunden):
        return Architektur2d3dblender.kontext()


class BlenderVergleichKontextTest(SimpleTestCase):
    def test_eine_zeile_traegt_lokal_und_blender_getrennt_und_den_stand_als_text(self):
        z = kontext_mit(Probe)['abschnitte'][0]['zeilen'][0]
        self.assertEqual((z['lokal'], z['blender'], z['stand']), ('Klassenkarte', 'ast.parse', 'vorhanden'))
        self.assertEqual(z['stand_text'], 'in Blender vorhanden, im Projekt nicht benutzt')
        self.assertEqual([(k['klasse'], k['fehlt']) for k in z['klassen']], [('Architektur2d3dklassen', '')])

    def test_die_staende_werden_gezaehlt_in_der_reihenfolge_der_seite(self):
        kontext = kontext_mit(Probe)
        zahl = {s['stand']: s['anzahl'] for s in kontext['zaehlung']}
        self.assertEqual(zahl, {'genutzt': 0, 'gemessen': 0, 'vorhanden': 1, 'addon': 1, 'keins': 0})
        self.assertEqual([s['stand'] for s in kontext['zaehlung']], list(Architektur2d3dblender.STAENDE))
        self.assertEqual(kontext['zeilen'], 2)

    def test_eine_klasse_die_es_nicht_gibt_und_ein_unbekannter_stand_stehen_als_befund(self):
        kontext = kontext_mit(ProbeMitFehlern)
        self.assertTrue(any('KlasseDieEsNichtGibt' in b for b in kontext['befunde']))
        self.assertTrue(any('unbekannter Stand' in b and 'zauberhaft' in b for b in kontext['befunde']))

    def test_ein_abschnitt_ohne_klasse_bricht_die_seite_nicht(self):
        with mock.patch.object(Architektur2d3dblender, 'abschnittsklassen', return_value=[('blendervergleichkaputt', None, 'Import schlug fehl')]):
            kontext = Architektur2d3dblender.kontext()
        self.assertEqual(kontext['befunde'], ['blendervergleichkaputt: Import schlug fehl'])


class BlenderVergleichZeitenTest(SimpleTestCase):
    def test_eine_zeit_zaehlt_als_gemessen_wenn_sie_eine_zahl_enthaelt(self):
        zeilen = kontext_mit(ProbeMitZeiten)['abschnitte'][0]['zeilen']
        gemessen = [(z['zeit_lokal']['gemessen'], z['zeit_blender']['gemessen']) for z in zeilen]
        self.assertEqual(gemessen, [(True, True), (True, False), (False, False)])
        self.assertEqual(zeilen[0]['zeit_blender']['text'], '55,0 s (Szene A; Stoffsolver/README.md, 02.10.2026)')

    def test_nur_eine_zeile_mit_zeit_auf_beiden_seiten_zaehlt_als_vergleich(self):
        self.assertEqual(kontext_mit(ProbeMitZeiten)['zeiten_beide'], 1)

    def test_eine_zeile_ohne_zeitfelder_steht_als_nicht_gemessen(self):
        z = kontext_mit(Probe)['abschnitte'][0]['zeilen'][0]
        self.assertEqual((z['zeit_lokal'], z['zeit_blender']),
                         ({'text': 'nicht gemessen', 'gemessen': False}, {'text': 'nicht gemessen', 'gemessen': False}))

    def test_eine_zeile_mit_falscher_eintragszahl_steht_als_befund(self):
        class Falsch:
            KENNUNG = 'falsch'
            TITEL = 'Falsch'
            EINLEITUNG = 'Neun Einträge.'
            ZEILEN = [('A', 'l', 'a()', [], 'B', 'b()', 'keins', 'x', 'nur eine Zeit')]
        self.assertTrue(any('9 Einträge' in b for b in kontext_mit(Falsch)['befunde']))


class BlenderVergleichEchteAbschnitteTest(SimpleTestCase):
    def test_die_echten_abschnitte_haben_keinen_befund_und_eindeutige_kennungen(self):
        kontext = Architektur2d3dblender.kontext()
        self.assertEqual(kontext['befunde'], [])
        kennungen = [a['kennung'] for a in kontext['abschnitte']]
        self.assertEqual(len(kennungen), len(set(kennungen)))
        for a in kontext['abschnitte']:
            self.assertTrue(a['titel'].strip() and a['einleitung'].strip() and a['zeilen'], a['kennung'])

    def test_jede_echte_zeile_hat_beide_seiten_und_keine_umschreibung(self):
        for a in Architektur2d3dblender.kontext()['abschnitte']:
            for z in a['zeilen']:
                stelle = '%s / %s' % (a['kennung'], z['aufgabe'])
                for feld in ('aufgabe', 'lokal', 'lokal_aufruf', 'blender', 'blender_aufruf', 'unterschied'):
                    self.assertTrue(z[feld].strip(), '%s: %s leer' % (stelle, feld))
                self.assertIn(z['stand'], Architektur2d3dblender.STAENDE, stelle)
                text = ' '.join((z['aufgabe'], z['lokal'], z['blender'], z['unterschied']))
                self.assertIsNone(re.search(r'\b(fuer|ueber|Faelle|Koerper|Staerke|Ruecken|moeglich)\b', text), stelle)

    def test_jede_echte_zeit_nennt_eine_quelle_oder_sagt_nicht_gemessen_bzw_entfaellt(self):
        quelle = re.compile(r'\.py\b|\.md\b|README|Regel|_vergleich|Protokoll|log\b')
        for a in Architektur2d3dblender.kontext()['abschnitte']:
            for z in a['zeilen']:
                for seite in ('zeit_lokal', 'zeit_blender'):
                    text = z[seite]['text']
                    stelle = '%s / %s / %s' % (a['kennung'], z['aufgabe'], seite)
                    if z[seite]['gemessen']:
                        self.assertRegex(text, quelle, stelle + ': Zeit ohne Quelle')
                    else:
                        self.assertIn(text, ('nicht gemessen', 'entfällt'), stelle)

    def test_genutzt_und_gemessen_nennen_im_unterschied_einen_beleg(self):
        beleg = re.compile(r'\.py\b|README|Regel|\.md\b|_vergleich|Messung|gemessen|Klasse|Rezept')
        for a in Architektur2d3dblender.kontext()['abschnitte']:
            for z in a['zeilen']:
                if z['stand'] in ('genutzt', 'gemessen'):
                    self.assertRegex(z['unterschied'], beleg, '%s / %s: Stand %s ohne Beleg' % (a['kennung'], z['aufgabe'], z['stand']))
