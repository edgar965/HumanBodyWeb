# -*- coding: utf-8 -*-
"""`Fotohautregler`: Eigene Haut bekommt keine Bräune und kein Öl, verstellte Regler und Daz-Haut bleiben (05.11.2026). Geschrieben, nicht gelaufen."""
import unittest

from core.dienste.fotohautregler import Fotohautregler


class FotohautreglerTest(unittest.TestCase):
    databases = []

    KATALOG = {'material.haut.toenung': '#f7c487', 'material.arme.toenung': '#ffd196', 'material.haut.glanzlack': 0.3, 'material.haut.rauheit': 0.38, 'material.arme.rauheit': 0.55}

    def test_eigene_haut_ohne_braeune_und_oel(self):
        aus = Fotohautregler.einsetzen({'renderhaut': dict(self.KATALOG)}, {1001: 'a.jpg'})['renderhaut']
        self.assertEqual(aus, Fotohautregler.WERTE)

    def test_daz_haut_bleibt(self):
        ein = {'renderhaut': dict(self.KATALOG)}
        self.assertIs(Fotohautregler.einsetzen(ein, {}), ein)

    def test_verstellter_regler_bleibt(self):
        aus = Fotohautregler.einsetzen({'renderhaut': dict(self.KATALOG, **{'material.haut.glanzlack': 0.1})}, {1001: 'a.jpg'})['renderhaut']
        self.assertEqual(aus['material.haut.glanzlack'], 0.1)
        self.assertEqual(aus['material.haut.toenung'], '#ffffff')

    def test_eingabe_bleibt_unveraendert(self):
        ein = {'renderhaut': dict(self.KATALOG), 'renderlicht': {'x': 1}}
        aus = Fotohautregler.einsetzen(ein, {1001: 'a.jpg'})
        self.assertEqual(ein['renderhaut'], self.KATALOG)
        self.assertEqual(aus['renderlicht'], {'x': 1})
