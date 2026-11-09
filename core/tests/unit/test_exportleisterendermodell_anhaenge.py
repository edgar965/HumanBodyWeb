# -*- coding: utf-8 -*-
"""`Exportleisterendermodell._anhaenge`: Eigene Hautkacheln tragen Brauen und Wimpern schon, die Daz-Anhänge fallen weg; Augen und Mund bleiben (05.11.2026). Geschrieben, nicht gelaufen."""
import unittest

from core.dienste.exportleisterendermodell import Exportleisterendermodell


class AnhaengeTest(unittest.TestCase):
    databases = []

    NETZ = {'punkte': [], 'anhaenge': [{'schluessel': s} for s in ('augen', 'mund', 'wimpern', 'brauen')]}

    def test_eigene_kacheln_ohne_brauen_und_wimpern(self):
        aus = Exportleisterendermodell({1001: 'a.jpg'})._anhaenge(self.NETZ)
        self.assertEqual([a['schluessel'] for a in aus['anhaenge']], ['augen', 'mund'])

    def test_daz_haut_behaelt_alle(self):
        self.assertIs(Exportleisterendermodell()._anhaenge(self.NETZ), self.NETZ)

    def test_das_netz_bleibt_unveraendert(self):
        Exportleisterendermodell({1001: 'a.jpg'})._anhaenge(self.NETZ)
        self.assertEqual(len(self.NETZ['anhaenge']), 4)
