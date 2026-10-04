# -*- coding: utf-8 -*-
"""Die Gruppen „Stoffsolver“ und „Blender“ des Reiters „Tools“ der Seite Hilfe → Architektur → 2D3D (03.10.2026).

WARUM: Andere Sessions nehmen die Zeilen als Anleitung — eine Klasse, die es nicht gibt, ein Rezeptname ohne `def` oder eine Methode, die der Aufruf erfindet, wäre der Fehler,
den die Seite verhindern soll. Deshalb prüfen diese Tests gegen den Code: jede genannte Klasse (Datei und Klasse über `Architektur2d3dklassen.zeile`), jeder Rezeptname, jede
`Klasse.methode(` im Aufruf, jede Beziehung zwischen Klassen derselben Gruppe. Dazu die Regeln des Reiters: Zeilen des Stoffsolvers nennen ihren Stand, Zeilen der Blender-Schleifen
sagen „nur nach Ansage von Edgar“, die Texte haben echte Umlaute. Gruppen und Zeilen werden hier nur gelesen — nichts davon startet Blender, den Solver oder einen Lauf."""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.architektur2d3dklassen import Architektur2d3dklassen
from core.dienste.architektur2d3dwerkzeuge import Architektur2d3dwerkzeuge
from core.dienste.werkzeugblenderschleife import Werkzeugblenderschleife
from core.dienste.werkzeugblenderweitere import Werkzeugblenderweitere
from core.dienste.werkzeugstofffedern import Werkzeugstofffedern
from core.dienste.werkzeugstofffelder import Werkzeugstofffelder
from core.dienste.werkzeugstoffhaar import Werkzeugstoffhaar
from core.dienste.werkzeugstoffsolver import Werkzeugstoffsolver
from core.dienste.werkzeugstoffuv import Werkzeugstoffuv
from core.dienste.werkzeugstoffvergleich import Werkzeugstoffvergleich

STOFFSOLVER = (Werkzeugstoffsolver, Werkzeugstofffedern, Werkzeugstofffelder, Werkzeugstoffhaar, Werkzeugstoffuv)
GRUPPEN = STOFFSOLVER + (Werkzeugstoffvergleich, Werkzeugblenderschleife, Werkzeugblenderweitere)
UMSCHREIBUNG = re.compile(r'\b(fuer|ueber|Ueber[a-z]*|Faelle|Koerper|Staerke|Ruecken|moeglich|koennen|muessen|waehrend|Groesse|Loesung|Aenderung|Aufloesung|Laenge|Hoehe|'
                          r'Praefix|natuerlich|gueltig|aehnlich|spaeter|ausser|waere|duerfen|Wuerfel|Fuesse|erklaert|Verhaeltnis|Zaehl[a-z]*)\b')


def zeilen():
    """(Gruppe, Zeile als Wörterbuch) über alle Zeilen aller Gruppen."""
    for g in GRUPPEN:
        for werkzeug, wofuer, art, aufruf, klassen, hinweis in g.ZEILEN:
            yield g, {'werkzeug': werkzeug, 'wofuer': wofuer, 'art': art, 'aufruf': aufruf, 'klassen': klassen, 'hinweis': hinweis}


class WerkzeugeStoffblenderAufbauTest(SimpleTestCase):
    def test_jede_gruppe_hat_eine_eindeutige_ascii_kennung_titel_einleitung_und_zeilen(self):
        kennungen = [g.KENNUNG for g in GRUPPEN]
        self.assertEqual(len(kennungen), len(set(kennungen)), 'die Kennung ist der Anker der Seite')
        for g in GRUPPEN:
            self.assertRegex(g.KENNUNG, r'^[a-z0-9]+$', g.__name__)
            self.assertTrue(g.TITEL.strip() and g.EINLEITUNG.strip() and g.ZEILEN, g.__name__)

    def test_die_gruppen_stehen_in_dateien_werkzeug_name_mit_einer_klasse_gleichen_namens(self):
        for g in GRUPPEN:
            self.assertEqual(g.__name__, g.__module__.rsplit('.', 1)[1].capitalize(), g.__module__)

    def test_jede_art_ist_bekannt(self):
        for g, z in zeilen():
            self.assertIn(z['art'], Architektur2d3dwerkzeuge.ARTEN, '%s / %s' % (g.KENNUNG, z['werkzeug']))

    def test_jede_zeile_ist_vollstaendig_und_hat_eine_klasse_ausser_bei_regel_und_seite(self):
        for g, z in zeilen():
            stelle = '%s / %s' % (g.KENNUNG, z['werkzeug'])
            for feld in ('werkzeug', 'wofuer', 'aufruf', 'hinweis'):
                self.assertTrue(isinstance(z[feld], str) and z[feld].strip(), '%s: %s' % (stelle, feld))
            self.assertTrue(z['klassen'] or z['art'] in ('regel', 'seite'), stelle + ': ohne Klasse')

    def test_ein_werkzeug_steht_nur_einmal(self):
        namen = [z['werkzeug'] for _g, z in zeilen()]
        self.assertEqual(len(namen), len(set(namen)))

    def test_die_texte_enthalten_keine_umschreibung_von_umlauten(self):
        for g in GRUPPEN:
            self.assertIsNone(UMSCHREIBUNG.search(g.TITEL + ' ' + g.EINLEITUNG), g.KENNUNG)
            for _von, _wie, _nach, womit in g.BEZIEHUNGEN:
                self.assertIsNone(UMSCHREIBUNG.search(womit), '%s: %s' % (g.KENNUNG, womit))
        for g, z in zeilen():
            self.assertIsNone(UMSCHREIBUNG.search(z['werkzeug'] + ' ' + z['wofuer'] + ' ' + z['hinweis']), '%s / %s' % (g.KENNUNG, z['werkzeug']))

    def test_keine_datei_ist_laenger_als_300_zeilen(self):
        for g in GRUPPEN:
            pfad = Path(settings.TOOLS_ROOT) / 'HumanBodyWeb' / 'core' / 'dienste' / (g.__module__.rsplit('.', 1)[1] + '.py')
            zahl = pfad.read_text(encoding='utf-8').count('\n') + 1
            self.assertLessEqual(zahl, 300, '%s hat %d Zeilen' % (pfad.name, zahl))


class WerkzeugeStoffblenderGegenCodeTest(SimpleTestCase):
    def test_jede_klasse_der_zeilen_gibt_es_im_code(self):
        fehlend = []
        for g, z in zeilen():
            for datei, klasse in z['klassen']:
                info = Architektur2d3dklassen.zeile(datei, klasse)
                if info['fehlt']:
                    fehlend.append((g.KENNUNG, z['werkzeug'], klasse, info['fehlt']))
        self.assertEqual(fehlend, [])

    def test_jede_beziehung_nennt_zwei_klassen_der_gruppe_und_ihre_zahl_liegt_zwischen_3_und_25(self):
        for g in GRUPPEN:
            klassen = {klasse for _w, _wo, _a, _au, ks, _h in g.ZEILEN for _datei, klasse in ks}
            self.assertTrue(3 <= len(g.BEZIEHUNGEN) <= 25, '%s: %d Beziehungen' % (g.KENNUNG, len(g.BEZIEHUNGEN)))
            for von, wie, nach, womit in g.BEZIEHUNGEN:
                self.assertEqual(wie, 'ruft')
                self.assertIn(von, klassen, '%s: %s' % (g.KENNUNG, von))
                self.assertIn(nach, klassen, '%s: %s' % (g.KENNUNG, nach))
                self.assertTrue(womit.strip(), '%s: %s → %s' % (g.KENNUNG, von, nach))

    def test_beginnt_womit_mit_einer_methode_dann_hat_die_zielklasse_sie(self):
        """„drapierung(motor): …“ heißt: die Zielklasse hat die Methode `drapierung`. Steht die Methode einer anderen Klasse vorn, beginnt der Text mit dem Klassennamen."""
        for g in GRUPPEN:
            datei_von = {klasse: datei for _w, _wo, _a, _au, ks, _h in g.ZEILEN for datei, klasse in ks}
            for von, _wie, nach, womit in g.BEZIEHUNGEN:
                treffer = re.match(r'([a-z_][a-z0-9_]*)\(', womit)
                if treffer:
                    methoden = Architektur2d3dklassen.zeile(datei_von[nach], nach)['methoden']
                    self.assertIn(treffer.group(1), methoden, '%s: %s → %s nennt %s()' % (g.KENNUNG, von, nach, treffer.group(1)))

    def test_jede_rezeptzeile_nennt_eine_methode_die_es_im_code_gibt(self):
        wurzel = Path(settings.TOOLS_ROOT)
        quellen = ''
        for ordner in ('Genesis9', '2d3DIterationen', 'HumanBodyWeb/core/dienste'):
            for datei in (wurzel / ordner).rglob('*.py'):
                quellen += datei.read_text(encoding='utf-8', errors='replace')
        for g, z in zeilen():
            if z['art'] != 'rezept':
                continue
            namen = re.findall(r'\bm\.([a-z_0-9]+)\(', z['aufruf'])
            self.assertTrue(namen, '%s / %s: eine Rezeptzeile ohne m.<name>(' % (g.KENNUNG, z['werkzeug']))
            for name in namen:
                self.assertIn('def %s(' % name, quellen, '%s / %s: m.%s gibt es nicht' % (g.KENNUNG, z['werkzeug'], name))

    def test_klasse_punkt_methode_im_aufruf_gibt_es_in_der_klasse(self):
        for g, z in zeilen():
            bekannt = {klasse: Architektur2d3dklassen.zeile(datei, klasse)['methoden'] for datei, klasse in z['klassen']}
            for klasse, methode in re.findall(r'\b([A-Z][A-Za-z0-9]+)\.([a-z][a-z0-9_]*)\(', z['aufruf']):
                if klasse in bekannt:
                    self.assertIn(methode, bekannt[klasse], '%s / %s: %s.%s(' % (g.KENNUNG, z['werkzeug'], klasse, methode))


class WerkzeugeStoffblenderRegelnTest(SimpleTestCase):
    def test_jede_zeile_des_stoffsolvers_nennt_ihren_stand(self):
        for g in STOFFSOLVER:
            for werkzeug, _wo, _art, _auf, _klassen, hinweis in g.ZEILEN:
                self.assertIn('Stand:', hinweis, '%s / %s' % (g.KENNUNG, werkzeug))

    def test_jede_zeile_der_blender_schleifen_sagt_nur_nach_ansage_von_edgar(self):
        self.assertIn('NUR NACH ANSAGE VON EDGAR', Werkzeugblenderschleife.EINLEITUNG)
        for werkzeug, _wo, _art, _auf, _klassen, hinweis in Werkzeugblenderschleife.ZEILEN:
            self.assertIn('NUR NACH ANSAGE VON EDGAR', hinweis, werkzeug)

    def test_die_vergleichswerkzeuge_und_der_effekte_weg_sagen_dass_blender_gestartet_wird(self):
        self.assertIn('nur nach Ansage von Edgar', Werkzeugstoffvergleich.EINLEITUNG)
        effekte = [z for z in Werkzeugblenderweitere.ZEILEN if z[0].startswith('Kleid + Wind')]
        self.assertEqual(len(effekte), 1)
        self.assertIn('NUR NACH ANSAGE VON EDGAR', effekte[0][5])
