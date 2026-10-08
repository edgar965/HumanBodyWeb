# -*- coding: utf-8 -*-
"""Haarfarbwahl (08.10.2026, N1: das Rückfoto mit Blaustich machte das Haar grau): ein Foto mit Blaustich im Haarton zählt nicht, solange ein anderes einen Ton ohne hat.

Zahlen aus `segmentierung.json` von N1 (`2026.10.07.22.53.48`): vorne (147, 107, 75) mit 22.958 Haarpixeln, hinten (176, 171, 193) mit 34.321. Keine Datenbank, keine Dateien.
Geschrieben, nicht als Suite gelaufen (`testsuite-nur-auf-ansage`).

Sabotage: in `Haarfarbwahl.waehlen` `gut or mit` durch `mit` ersetzen → Fall 1 rot (das alte Mittel (164, 145, 146)).
"""

from django.test import SimpleTestCase

from core.dienste.haarfarbwahl import Haarfarbwahl

VORNE = {'rolle': 'vorne', 'haarfarbe': [147, 107, 75], 'haar_pixel': 22958}
HINTEN = {'rolle': 'hinten', 'haarfarbe': [176, 171, 193], 'haar_pixel': 34321}


class DieHaarfarbwahl(SimpleTestCase):
    databases = set()

    def test_1_das_foto_mit_blaustich_zaehlt_nicht(self):
        rgb, ausgelassen = Haarfarbwahl.waehlen([VORNE, HINTEN])
        self.assertEqual(rgb, [147, 107, 75])                  # nicht das Mittel (164, 145, 146)
        self.assertEqual(ausgelassen, {'hinten': [176, 171, 193]})

    def test_2_ohne_blaustich_gilt_das_mittel_nach_haarpixeln(self):
        zwei = {'rolle': 'hinten', 'haarfarbe': [100, 80, 60], 'haar_pixel': 22958}
        rgb, ausgelassen = Haarfarbwahl.waehlen([VORNE, zwei])
        self.assertEqual(rgb, [124, 94, 68])                   # (147 + 100) / 2 usw. — gleiche Pixelzahl
        self.assertEqual(ausgelassen, {})

    def test_3_zeigen_alle_blaustich_oder_gibt_es_nur_eines_gilt_wie_bisher(self):
        blau = {'rolle': 'seite', 'haarfarbe': [150, 160, 190], 'haar_pixel': 10000}
        rgb, ausgelassen = Haarfarbwahl.waehlen([HINTEN, blau])
        self.assertEqual(ausgelassen, {})
        self.assertEqual([int(c) for c in rgb], [int(round((176 * 34321 + 150 * 10000) / 44321)), int(round((171 * 34321 + 160 * 10000) / 44321)), int(round((193 * 34321 + 190 * 10000) / 44321))])
        self.assertEqual(Haarfarbwahl.waehlen([HINTEN])[0], [176, 171, 193])

    def test_4_fotos_ohne_haar_und_ohne_eintraege(self):
        self.assertEqual(Haarfarbwahl.waehlen(None), (None, {}))
        self.assertEqual(Haarfarbwahl.waehlen([{'rolle': 'vorne', 'haarfarbe': None, 'haar_pixel': 0}]), (None, {}))
        self.assertEqual(Haarfarbwahl.waehlen([{'rolle': 'vorne', 'haarfarbe': None, 'haar_pixel': 0}, VORNE])[0], [147, 107, 75])

    def test_5_die_schwelle_liegt_bei_acht(self):
        self.assertFalse(Haarfarbwahl.blaustich([100, 100, 108]))      # genau 8: noch kein Blaustich
        self.assertTrue(Haarfarbwahl.blaustich([100, 100, 109]))
        self.assertFalse(Haarfarbwahl.blaustich([147, 107, 75]))
