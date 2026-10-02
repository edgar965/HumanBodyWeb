# -*- coding: utf-8 -*-
"""Die Umfangstabelle des Stoffsolvers auf der Seite Hilfe → Architektur → 2D3D (02.10.2026).

WARUM: Die Tabelle sagt je Blender-Funktion, welche Klasse sie trägt und ob sie gegen einen Blender-Lauf gemessen ist. Eine
Behauptung über eine Klasse, die es nicht gibt, wäre der Fehler, den die Seite verhindern soll — deshalb sucht `zeilen()` jede Klasse
im Code, und diese Tests halten fest, dass keine fehlt, jeder Stand zu den vier bekannten gehört und die Zählung zu den Zeilen passt."""

from django.test import SimpleTestCase

from core.dienste.stoffsolverumfang import Stoffsolverumfang


class StoffsolverumfangTest(SimpleTestCase):
    def test_jede_genannte_klasse_gibt_es_im_code(self):
        fehlend = [(z['blender'], k['klasse'], k['fehlt']) for z in Stoffsolverumfang.zeilen() for k in z['klassen'] if k['fehlt']]
        self.assertEqual(fehlend, [])

    def test_jeder_stand_ist_bekannt_und_jede_zeile_hat_eine_anmerkung(self):
        for zeile in Stoffsolverumfang.zeilen():
            self.assertIn(zeile['stand'], Stoffsolverumfang.STAENDE)
            self.assertTrue(zeile['hinweis'].strip(), zeile['blender'])

    def test_nur_der_kern_ist_gegen_blender_gemessen(self):
        """Der Ausbau vom 02.10.2026 ist nicht gegen Blender gelaufen: nur die Zeilen des Kerns tragen den Stand `blender`."""
        for neu in ('Schrumpfen', 'Nähte', 'Innenfedern', 'Wind', 'Haar-Kontinuum', 'UV'):
            for zeile in Stoffsolverumfang.ZEILEN:
                if neu in zeile[1]:
                    self.assertNotEqual(zeile[3], 'blender', zeile[1])

    def test_nicht_gebaute_zeilen_nennen_keine_klasse(self):
        for bereich, blender, klassen, stand, _hinweis in Stoffsolverumfang.ZEILEN:
            if stand == 'nein':
                self.assertEqual(klassen, [], blender)
            else:
                self.assertTrue(klassen, blender)

    def test_die_zaehlung_stimmt_mit_den_zeilen_ueberein(self):
        zaehlung = Stoffsolverumfang.zaehlung()
        self.assertEqual(sum(z['anzahl'] for z in zaehlung), len(Stoffsolverumfang.ZEILEN))
        self.assertEqual([z['stand'] for z in zaehlung], list(Stoffsolverumfang.STAENDE))
