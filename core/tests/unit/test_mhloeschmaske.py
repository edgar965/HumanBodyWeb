# -*- coding: utf-8 -*-
u"""Mhloeschmaske — die `delete_verts`-Liste einer `.mhclo` richtig lesen.

WORUM ES GEHT (06.09.2026): MakeHuman blendet die Haut unter einem
Kleidungsstueck aus. Ohne diese Liste steht sie durch den Stoff — gemessen
waren 23,5 % der Punkte von `female_casualsuit01` INNERHALB der Haut, bis zu
21,1 mm tief.

DIE FALLE IST DER BINDESTRICH. Er steht als EIGENES Wort zwischen den Grenzen
eines Bereichs::

    1355 - 1413 1420 - 1423 1502

Wer ihn als Vorzeichen liest, bekommt `1355, -1413, 1420, -1423, 1502` — also
lauter negative Nummern, die kein Viereck trifft. Die Maske waere dann still
viel zu klein, und das Ergebnis saehe nur „ein bisschen falsch" aus. Genau
dagegen steht dieser Test.
"""

import unittest

from MakeHuman.loeschmaske import Mhloeschmaske


class MhloeschmaskeTest(unittest.TestCase):

    databases = set()

    def test_einzelne_zahlen(self):
        self.assertEqual(Mhloeschmaske.nummern(['3', '7', '9']), {3, 7, 9})

    def test_bereich_ist_einschliesslich(self):
        self.assertEqual(Mhloeschmaske.nummern(['3', '-', '6']), {3, 4, 5, 6})

    def test_bereiche_und_einzelne_gemischt(self):
        woerter = '1355 - 1358 1420 1430 - 1432'.split()
        self.assertEqual(Mhloeschmaske.nummern(woerter),
                         {1355, 1356, 1357, 1358, 1420, 1430, 1431, 1432})

    def test_bindestrich_wird_nicht_zum_vorzeichen(self):
        u"""Kein negativer Wert — sonst trifft die Maske nichts."""
        nummern = Mhloeschmaske.nummern('10 - 12 40'.split())
        self.assertFalse([n for n in nummern if n < 0])
        self.assertEqual(nummern, {10, 11, 12, 40})

    def test_zeilenumbruch_zerreisst_keinen_bereich(self):
        u"""In der Datei stehen Bereiche ueber Zeilengrenzen hinweg."""
        erste = '1663 -'.split()
        zweite = '1686 1689'.split()
        self.assertEqual(Mhloeschmaske.nummern(erste + zweite),
                         set(range(1663, 1687)) | {1689})

    def test_muell_wird_uebergangen(self):
        self.assertEqual(Mhloeschmaske.nummern(['5', 'quatsch', '8']), {5, 8})

    def test_leer(self):
        self.assertEqual(Mhloeschmaske.nummern([]), set())


if __name__ == '__main__':
    unittest.main()
