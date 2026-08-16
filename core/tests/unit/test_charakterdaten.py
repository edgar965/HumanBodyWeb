# -*- coding: utf-8 -*-
"""Charakterdaten: die Zwischenspeicher muessen erst nach dem Laden sichtbar sein.

Anlass (16.08.2026): `morphdaten()` setzte `cls._morph_data` VOR dem `load()`.
Daphne beantwortet Anfragen parallel; eine zweite Anfrage sah das Attribut schon
gesetzt und arbeitete mit leeren Morph-Packs weiter. `MorphData` merkt sich das
Ergebnis in seinem `_l2_cache` — die leere Liste blieb bis zum Prozessende
stehen, `/api/character/morphs/` lieferte dauerhaft `morphs: []`.
"""
import threading
import unittest
from unittest import mock

from core.dienste.charakterdaten import Charakterdaten


class LangsamLadendeDaten:
    """Steht fuer MorphData: `load()` braucht Zeit, vorher ist nichts drin."""

    def __init__(self, *args, **kwargs):
        self.geladen = False
        self.packs = []

    def load(self):
        # Lang genug, dass ein zweiter Thread sicher dazwischenkommt.
        threading.Event().wait(0.05)
        self.packs = ['pack']
        self.geladen = True


class CharakterdatenNebenlaeufigTest(unittest.TestCase):

    def setUp(self):
        self._vorher = Charakterdaten._morph_data
        Charakterdaten._morph_data = None

    def tearDown(self):
        Charakterdaten._morph_data = self._vorher

    def test_paralleler_zugriff_sieht_nur_geladene_daten(self):
        """Kein Aufrufer darf ein halb gebautes MorphData bekommen."""
        gesehen = []

        def holen():
            daten = Charakterdaten.morphdaten()
            gesehen.append((daten.geladen, list(daten.packs)))

        with mock.patch('core.dienste.charakterdaten.MorphData',
                        LangsamLadendeDaten):
            threads = [threading.Thread(target=holen) for _ in range(8)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        self.assertEqual(len(gesehen), 8)
        for geladen, packs in gesehen:
            self.assertTrue(geladen, 'ungeladene Daten waren sichtbar')
            self.assertEqual(packs, ['pack'])

    def test_nur_einmal_geladen(self):
        """Acht gleichzeitige Aufrufe duerfen die Daten nicht achtmal laden."""
        anzahl = []

        class Zaehlend(LangsamLadendeDaten):
            def load(self):
                anzahl.append(1)
                super().load()

        with mock.patch('core.dienste.charakterdaten.MorphData', Zaehlend):
            threads = [threading.Thread(target=Charakterdaten.morphdaten)
                       for _ in range(8)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        self.assertEqual(sum(anzahl), 1)

    def test_zweiter_aufruf_liefert_dasselbe_objekt(self):
        with mock.patch('core.dienste.charakterdaten.MorphData',
                        LangsamLadendeDaten):
            erst = Charakterdaten.morphdaten()
            zweit = Charakterdaten.morphdaten()
        self.assertIs(erst, zweit)


if __name__ == '__main__':
    unittest.main()
