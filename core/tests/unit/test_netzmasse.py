# -*- coding: utf-8 -*-
u"""Netzmasse: Punkte, Vierecke, Dreiecke und Unterteilungen auf eine
Vergleichszahl — und der Rang folgt ihr.

Edgar (17.09.2026): „einmal Punkte, einmal Vierecke, einmal Dreiecke? Mach
irgendetwas, mit dem man alles vergleichen kann". Die Regeln: ein Viereck
sind zwei Dreiecke, ein Vierecknetz hat etwa so viele Flächen wie Punkte,
jede Unterteilung vervierfacht. Abgeleitetes traegt „≈".
"""
from unittest import TestCase

from core.dienste.netzmasse import Netzmasse


class Ableitung(TestCase):

    def test_gegebene_dreiecke_bleiben_exakt(self):
        z = Netzmasse.ergaenzen({'dreiecke': 13_776, 'punkte': 6_890})
        self.assertEqual(z['basis_dreiecke'], 13_776)
        self.assertEqual(z['basis_dreiecke_text'], '13.776')
        self.assertEqual(z['basis_punkte_text'], '6.890')
        self.assertEqual(z['hoechst_dreiecke'], 13_776)
        self.assertEqual(z['stufen_text'], 'keine')

    def test_vierecke_werden_verdoppelt_und_markiert(self):
        z = Netzmasse.ergaenzen({'vierecke': 32_976})
        self.assertEqual(z['basis_dreiecke'], 65_952)
        self.assertEqual(z['basis_dreiecke_text'], '≈ 65.952')
        self.assertEqual(z['basis_punkte_text'], '≈ 32.976')
        self.assertEqual(z['basis_vierecke_text'], '32.976')

    def test_punkte_allein_ergeben_vierecke_und_dreiecke(self):
        z = Netzmasse.ergaenzen({'punkte': 10_582, 'stufen': 3})
        self.assertEqual(z['basis_vierecke_text'], '≈ 10.582')
        self.assertEqual(z['basis_dreiecke'], 21_164)
        self.assertEqual(z['hoechst_dreiecke'], 21_164 * 64)
        self.assertEqual(z['stufen_text'], '3 Unterteilungen')

    def test_bezifferte_hoechste_stufe_schlaegt_die_rechnung(self):
        z = Netzmasse.ergaenzen({'stufen': 7, 'hoechste': 69_000_000,
                                 'hoechste_einheit': 'punkte'})
        self.assertEqual(z['hoechst_dreiecke'], 138_000_000)
        self.assertEqual(z['hoechst_text'], '≈ 138.000.000')
        self.assertEqual(z['basis_punkte_text'], '–')

    def test_ohne_zahl_bleibt_alles_strich(self):
        z = Netzmasse.ergaenzen({'stufen': 3})
        self.assertIsNone(z['hoechst_dreiecke'])
        self.assertEqual(z['hoechst_text'], '–')


class Rangfolge(TestCase):

    def test_rang_folgt_der_dichte_und_ohne_zahl_gibt_es_keinen(self):
        zeilen = [{'name': 'klein', 'dreiecke': 100},
                  {'name': 'leer'},
                  {'name': 'gross', 'vierecke': 100, 'stufen': 1},
                  {'name': 'forschung', 'dreiecke': 10 ** 9,
                   'ohne_rang': 'nur Forschung'}]
        aus = Netzmasse.rangfolge(zeilen)
        self.assertEqual([(z['name'], z['rang']) for z in aus],
                         [('gross', 1), ('klein', 2), ('leer', None),
                          ('forschung', None)])

    def test_gleiche_dichte_behaelt_die_reihenfolge(self):
        aus = Netzmasse.rangfolge([{'name': 'a', 'dreiecke': 5},
                                   {'name': 'b', 'dreiecke': 5}])
        self.assertEqual([z['name'] for z in aus], ['a', 'b'])
