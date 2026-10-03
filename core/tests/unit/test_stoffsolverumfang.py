# -*- coding: utf-8 -*-
"""Die Umfangstabelle des Stoffsolvers auf der Seite Hilfe → Architektur → 2D3D (02.10.2026).

WARUM: Die Tabelle sagt je Blender-Funktion, welche Klasse sie trägt und ob sie gegen einen Blender-Lauf gemessen ist. Eine Behauptung über eine Klasse, die es nicht gibt, wäre der Fehler,
den die Seite verhindern soll — deshalb sucht `zeilen()` jede Klasse im Code, und diese Tests halten fest, dass keine fehlt, jede eine Klassenkarte hat (sonst zeigt der Anker ins Leere),
jeder Stand zu den bekannten gehört, ein „gegen Blender gemessen" ein Maß nennt und die Zählung zu den Zeilen passt."""

import re

from django.test import SimpleTestCase

from core.dienste.architektur2d3dklassen import Architektur2d3dklassen
from core.dienste.stoffsolverumfang import Stoffsolverumfang


class StoffsolverumfangTest(SimpleTestCase):
    def test_jede_genannte_klasse_gibt_es_im_code(self):
        fehlend = [(z['blender'], k['klasse'], k['fehlt']) for z in Stoffsolverumfang.zeilen() for k in z['klassen'] if k['fehlt']]
        self.assertEqual(fehlend, [])

    def test_jede_genannte_klasse_hat_eine_klassenkarte(self):
        karten = {klasse for gruppe in Architektur2d3dklassen.GRUPPEN for _datei, klasse in gruppe[2]}
        ohne = sorted({k for _b, _f, klassen, _s, _h in Stoffsolverumfang.ZEILEN for _d, k in klassen} - karten)
        self.assertEqual(ohne, [], 'der Anker k-<Klasse> der Tabelle zeigt ins Leere')

    def test_jeder_stand_ist_bekannt_und_jede_zeile_hat_eine_anmerkung(self):
        for zeile in Stoffsolverumfang.zeilen():
            self.assertIn(zeile['stand'], Stoffsolverumfang.STAENDE)
            self.assertTrue(zeile['hinweis'].strip(), zeile['blender'])

    def test_ein_gegen_blender_gemessen_nennt_ein_mass(self):
        """Wer „gegen Blender gemessen" sagt, nennt die Messung: die Anmerkung enthält mindestens eine Zahl."""
        for bereich, blender, _klassen, stand, hinweis in Stoffsolverumfang.ZEILEN:
            if stand == 'blender':
                self.assertRegex(hinweis, r'\d', '%s / %s: Stand blender ohne Zahl' % (bereich, blender))

    def test_ohne_blender_lauf_steht_der_grund_in_der_anmerkung(self):
        for _bereich, blender, _klassen, stand, hinweis in Stoffsolverumfang.ZEILEN:
            if stand == 'quelle':
                self.assertIn('Blender', hinweis, blender)

    def test_nicht_gebaute_zeilen_nennen_keine_klasse(self):
        for _bereich, blender, klassen, stand, _hinweis in Stoffsolverumfang.ZEILEN:
            if stand == 'nein':
                self.assertEqual(klassen, [], blender)
            else:
                self.assertTrue(klassen, blender)

    def test_die_anmerkungen_haben_echte_umlaute(self):
        for _bereich, blender, _klassen, _stand, hinweis in Stoffsolverumfang.ZEILEN:
            self.assertIsNone(re.search(r'\b(fuer|ueber|Faelle|Koerper|Staerke|Ruecken)\b', blender + ' ' + hinweis), blender)

    def test_die_zaehlung_stimmt_mit_den_zeilen_ueberein(self):
        zaehlung = Stoffsolverumfang.zaehlung()
        self.assertEqual(sum(z['anzahl'] for z in zaehlung), len(Stoffsolverumfang.ZEILEN))
        self.assertEqual([z['stand'] for z in zaehlung], list(Stoffsolverumfang.STAENDE))
