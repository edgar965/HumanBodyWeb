# -*- coding: utf-8 -*-
u"""Hilfe → Kleidung → Körperphysik: die Seite steht, ihre Zahlen kommen aus Python.

WARUM (Edgar, 10.09.2026: „schreibe alle Erkenntnisse und das ganze Know how
der Körperphysik auf in Hilfe - Kleidung - Körperphysik"): Was an dieser
Baustelle gemessen wurde, gehört ins Projekt — sonst steht es nur in einer
Sitzung.

Geprüft wird viererlei:

1. Die Seite antwortet und trägt ihre Kernzahlen und -namen.
2. Die Daten kommen aus `koerper.physik` / `koerper.fpskette`, nicht aus der
   Vorlage — und sie sind vollständig.
3. **Der Stand bleibt ehrlich.** Eine Seite, auf der alles „läuft", während
   die Arme zerreißen, ist schlimmer als keine. Der Test verlangt deshalb
   mindestens eine Zeile mit `FEHLER` und mindestens eine mit `offen`.
4. Jede Prüfung führt ihre Gegenprobe mit — eine Probe ohne Gegenprobe kann
   blind sein, ohne dass es jemand merkt.
"""
import sys
import unittest
from pathlib import Path

from django.conf import settings
from django.test import Client, SimpleTestCase
from django.urls import reverse
from django.utils.html import escape

sys.path.insert(0, str(Path(settings.ASSETS_ROOT)))

from koerper.fpskette import Fpskette                        # noqa: E402
from koerper.physik import Koerperphysik                     # noqa: E402


class SeiteKoerperphysik(SimpleTestCase):

    databases = []

    def setUp(self):
        self.antwort = Client().get(reverse('hilfe_koerper_physik'))
        self.inhalt = self.antwort.content.decode('utf-8')

    def test_die_seite_antwortet(self):
        self.assertEqual(self.antwort.status_code, 200)

    def test_die_adresse_ist_die_erwartete(self):
        self.assertEqual(reverse('hilfe_koerper_physik'),
                         '/hilfe/kleidung/koerperphysik/')

    def test_die_kernaussagen_stehen_darin(self):
        u"""Die Namen und Zahlen, um die es geht — nicht der Fließtext."""
        for probe in ('FastProjectiveSkinning', 'Spring Decomposed Skinning',
                      'vertices_tpose.npy', '--vorlauf',
                      str(Fpskette.PUNKTE), str(Fpskette.GELENKE),
                      str(Fpskette.SEKUNDEN_60_BILDER),
                      # Ohne Vorzeichen: Django lokalisiert und schreibt
                      # ein typografisches Minus (U+2212), nicht den
                      # ASCII-Bindestrich der Konstanten.
                      str(abs(Koerperphysik.LBS_ARMVERLUST_PROZENT))
                      .replace('.', ',')):
            self.assertIn(probe, self.inhalt, probe)

    def test_jeder_kandidat_und_jede_falle_steht_auf_der_seite(self):
        # `escape`, weil die Vorlage Anführungszeichen als `&quot;` schreibt.
        for kandidat in Koerperphysik.kandidaten():
            self.assertIn(escape(kandidat['urteil']), self.inhalt, kandidat['name'])
        for falle in Fpskette.fallen():
            self.assertIn(escape(falle['titel']), self.inhalt, falle['titel'])

    def test_das_menue_fuehrt_den_punkt(self):
        gruppen = settings.DJANGOBASE.get('hilfe_extra') or []
        adressen = [e['url'] for gruppe in gruppen
                    for e in gruppe.get('untermenu', [])]
        self.assertIn('/hilfe/kleidung/koerperphysik/', adressen)

    def test_die_nachbarseiten_bleiben_erreichbar(self):
        for pfad in ('/hilfe/versionen/', '/hilfe/logs/', '/hilfe/tests/',
                     '/hilfe/kleidung/', '/hilfe/kleidung/garmentcode/',
                     '/hilfe/kleidung/neu/', '/hilfe/kleidung/physik/'):
            self.assertEqual(Client().get(pfad).status_code, 200, pfad)


class DatenStehenInPython(unittest.TestCase):

    databases = []

    def test_die_drei_baustellen_sind_getrennt(self):
        u"""A, B und C brauchen verschiedene Lösungen — deshalb stehen sie
        einzeln da, jede mit Ist-Zustand und Löser."""
        baustellen = Koerperphysik.baustellen()
        self.assertEqual(len(baustellen), 3)
        for b in baustellen:
            for feld in ('name', 'was', 'ist', 'loeser'):
                self.assertTrue(b.get(feld), '%s: %s' % (b['name'], feld))

    def test_jeder_kandidat_ist_vollstaendig(self):
        felder = ('name', 'lizenz', 'laeuft', 'braucht', 'kann', 'urteil')
        kandidaten = Koerperphysik.kandidaten()
        self.assertGreaterEqual(len(kandidaten), 5)
        for kandidat in kandidaten:
            for feld in felder:
                self.assertTrue(kandidat.get(feld), '%s: %s' % (kandidat, feld))

    def test_genau_ein_kandidat_ist_gewaehlt(self):
        gewaehlt = [k for k in Koerperphysik.kandidaten()
                    if k['urteil'] == 'gewaehlt']
        self.assertEqual(len(gewaehlt), 1)
        self.assertTrue(gewaehlt[0]['name'].startswith('FastProjectiveSkinning'))

    def test_der_stand_bleibt_ehrlich(self):
        u"""DIE SCHARFE PRÜFUNG. Eine Bestandsseite, auf der alles läuft,
        während die Arme zerreißen, führt in die Irre. Sobald der Armfehler
        behoben ist, wird dieser Fall rot — und dann gehört der Stand
        angefasst, nicht der Test."""
        stand = Fpskette.stand()
        wie = [w for _teil, w, _beleg in stand]
        self.assertIn('FEHLER', wie, u'kein einziger Fehler — wirklich?')
        self.assertIn('offen', wie)
        self.assertIn('laeuft', wie)
        for teil, _w, beleg in stand:
            self.assertTrue(beleg, teil)

    def test_jede_pruefung_fuehrt_ihre_gegenprobe(self):
        u"""Eine Probe ohne Gegenprobe kann blind sein. Genau das ist hier
        passiert: Die Positionsprobe meldet 0,00 mm, während der Oberarm
        161 Grad bekommt."""
        pruefungen = Fpskette.pruefen()
        self.assertGreaterEqual(len(pruefungen), 4)
        for p in pruefungen:
            for feld in ('was', 'wie', 'soll', 'ist', 'gegenprobe'):
                self.assertTrue(p.get(feld), '%s: %s' % (p['was'], feld))

    def test_jede_falle_nennt_zahl_und_lehre(self):
        u"""Eine Falle ohne Messung ist eine Behauptung, eine ohne Lehre
        eine Anekdote."""
        fallen = Fpskette.fallen()
        self.assertGreaterEqual(len(fallen), 9)
        for f in fallen:
            for feld in ('titel', 'was', 'zahl', 'warum_still', 'lehre'):
                self.assertTrue(f.get(feld), '%s: %s' % (f['titel'], feld))

    def test_die_vier_schritte_sind_bedienbar_beschrieben(self):
        schritte = Fpskette.schritte()
        self.assertEqual(len(schritte), 5)
        self.assertEqual(sorted(s['nr'] for s in schritte),
                         [1, 2, 3, 4, 5])
        for s in schritte:
            for feld in ('titel', 'befehl', 'macht', 'ergibt', 'dauer'):
                self.assertTrue(s.get(feld), '%s: %s' % (s['titel'], feld))

    def test_die_aenderungen_am_fremden_code_sind_benannt(self):
        u"""GPL-Code: Was geändert wurde, muss nachlesbar sein."""
        aenderungen = Fpskette.aenderungen()
        self.assertGreaterEqual(len(aenderungen), 3)
        for a in aenderungen:
            for feld in ('wo', 'was', 'warum'):
                self.assertTrue(a.get(feld), '%s: %s' % (a['wo'], feld))

    def test_abgrenzung_offenes_und_quellen_sind_benannt(self):
        self.assertGreaterEqual(len(Koerperphysik.nicht()), 3)
        self.assertGreaterEqual(len(Fpskette.offen()), 3)
        for name, adresse in Koerperphysik.quellen():
            self.assertTrue(name and adresse.startswith('http'), name)

    def test_die_zehn_sekunden_rechnung_folgt_den_konstanten(self):
        erwartet = 10 * 60 * (Fpskette.SEKUNDEN_60_BILDER / 60.0) / 60.0
        self.assertAlmostEqual(Fpskette.minuten_je_10s(), erwartet, places=0)
