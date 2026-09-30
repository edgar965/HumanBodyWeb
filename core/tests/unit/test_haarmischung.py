# -*- coding: utf-8 -*-
u"""Die Haarmischung ueber die Straehnendichte (`Genesis9/haarmischung.py`, 30.09.2026).

Kunstnetze aus getrennten Inseln (je Insel ein Dreieckspaar) — so, wie eine Frisur aus
Straehnen und Haarkarten besteht (gemessen: Kin Hair 4.225 Inseln, Toulouse 236).
Geprueft wird, was im Browser sonst still falsch waere: ganze Inseln statt zerschnittener
Straehnen, Nahtkopien, die zusammenbleiben, die `-1`-Ecke, Gruppen und Haut, die
mitschrumpfen, und dass derselbe Anteil dieselben Straehnen ergibt.
"""
import numpy as np
from django.test import SimpleTestCase
from Genesis9.haarmischung import G9haarmischung


def inselnetz(anzahl, gruppen=False):
    u"""`anzahl` getrennte Quadrate (je 4 Punkte, 2 Dreiecke) nebeneinander."""
    punkte, dreiecke = [], []
    for i in range(anzahl):
        b = len(punkte)
        punkte += [[i, 0, 0], [i + 0.5, 0, 0], [i + 0.5, 1, 0], [i, 1, 0]]
        dreiecke += [[b, b + 1, b + 2], [b, b + 2, b + 3]]
    teil = {'punkte': np.array(punkte, dtype=np.float64),
            'dreiecke': np.array(dreiecke, dtype=np.int64),
            'normalen': np.tile([0.0, 0.0, 1.0], (len(punkte), 1)),
            'uv': np.zeros((len(punkte), 2)),
            'haut': {'knochen': ['head'],
                     'index': np.zeros((len(punkte), 4), dtype=np.int64),
                     'gewicht': np.tile([1.0, 0, 0, 0], (len(punkte), 1))},
            'stoff': {'frei': np.zeros(len(punkte))},
            'art': None, 'name': 'probe', 'stufen': 0}
    if gruppen:
        halb = len(dreiecke) // 2
        teil['gruppen'] = [
            {'name': 'A', 'index_ab': 0, 'index_anzahl': halb * 3, 'kachel': 1001},
            {'name': 'B', 'index_ab': halb * 3, 'index_anzahl': (len(dreiecke) - halb) * 3,
             'kachel': 1001}]
    return teil


class InselnTest(SimpleTestCase):

    def test_1_getrennte_quadrate_sind_getrennte_inseln(self):
        teil = inselnetz(5)
        _, zahl = G9haarmischung.inseln(teil['dreiecke'], len(teil['punkte']))
        self.assertEqual(zahl, 5)

    def test_2_nahtkopien_halten_eine_insel_zusammen(self):
        u"""An einer UV-Naht liegen zwei Punkte an derselben Stelle, ohne gemeinsame
        Flaeche. Ohne die Lage zerfiele die Straehne in zwei Inseln."""
        punkte = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0],        # Haelfte 1
                           [1, 0, 0], [2, 0, 0], [1, 1, 0]],       # Haelfte 2, Nahtkopien
                          dtype=np.float64)
        dreiecke = np.array([[0, 1, 2], [3, 4, 5]])
        _, ohne = G9haarmischung.inseln(dreiecke, 6)
        _, mit = G9haarmischung.inseln(dreiecke, 6, punkte)
        self.assertEqual(ohne, 2)
        self.assertEqual(mit, 1)


class AusduennenTest(SimpleTestCase):

    def test_1_ganze_inseln_bleiben_ganz(self):
        u"""Jede behaltene Insel hat alle 4 Punkte und beide Dreiecke — keine Fetzen."""
        aus = G9haarmischung.ausduennen(inselnetz(100), 0.3, 'probe')
        self.assertEqual(len(aus['punkte']) % 4, 0)
        self.assertEqual(len(aus['dreiecke']), len(aus['punkte']) // 2)
        self.assertEqual(len(aus['punkte']) // 4, 30)

    def test_2_indizes_zeigen_auf_die_neuen_punkte(self):
        aus = G9haarmischung.ausduennen(inselnetz(50), 0.4, 'probe')
        self.assertLess(int(aus['dreiecke'].max()), len(aus['punkte']))
        self.assertGreaterEqual(int(aus['dreiecke'].min()), 0)

    def test_3_felder_je_punkt_und_haut_ziehen_mit(self):
        aus = G9haarmischung.ausduennen(inselnetz(50), 0.5, 'probe')
        n = len(aus['punkte'])
        self.assertEqual(len(aus['normalen']), n)
        self.assertEqual(len(aus['uv']), n)
        self.assertEqual(len(aus['haut']['index']), n)
        self.assertEqual(len(aus['haut']['gewicht']), n)

    def test_4_der_stoffschwung_faellt_weg(self):
        u"""dForce rechnet auf den Kaefigpunkten des GANZEN Netzes — die gibt es nicht mehr."""
        aus = G9haarmischung.ausduennen(inselnetz(50), 0.5, 'probe')
        self.assertNotIn('stoff', aus)

    def test_5_gruppen_schrumpfen_und_bleiben_lueckenlos(self):
        aus = G9haarmischung.ausduennen(inselnetz(40, gruppen=True), 0.5, 'probe')
        gezaehlt = 0
        for g in aus['gruppen']:
            self.assertEqual(g['index_ab'], gezaehlt)
            gezaehlt += g['index_anzahl']
        self.assertEqual(gezaehlt, len(aus['dreiecke']) * 3)
        self.assertEqual({g['name'] for g in aus['gruppen']}, {'A', 'B'})

    def test_6_derselbe_anteil_ergibt_dieselben_straehnen(self):
        u"""Sonst saehe die Figur nach jedem Reglerzug anders aus — und der Antwortvorrat
        lieferte zu einem Schluessel wechselnde Netze."""
        a = G9haarmischung.ausduennen(inselnetz(80), 0.35, 'kin_hair/0')
        b = G9haarmischung.ausduennen(inselnetz(80), 0.35, 'kin_hair/0')
        np.testing.assert_array_equal(a['punkte'], b['punkte'])

    def test_7_nicht_die_ersten_inseln(self):
        u"""Daz speichert Straehnen von einer Kopfseite zur anderen — ein Praefix waere
        ein halb kahles Haar. Die behaltenen Inseln streuen ueber das ganze Netz."""
        aus = G9haarmischung.ausduennen(inselnetz(100), 0.3, 'probe')
        x = aus['punkte'][:, 0]
        self.assertLess(x.min(), 20)
        self.assertGreater(x.max(), 80)

    def test_8_voll_und_leer(self):
        teil = inselnetz(10)
        self.assertIs(G9haarmischung.ausduennen(teil, 1.0, 'probe'), teil)
        self.assertIsNone(G9haarmischung.ausduennen(teil, 0.0, 'probe'))

    def test_9_die_hauptsorte_behaelt_ihre_groesste_insel(self):
        u"""Bei Flaechenhaar ist das meist die Kappe — ohne sie schiene die Kopfhaut durch."""
        teil = inselnetz(30)
        # Insel 0 zur groessten machen: ein drittes Dreieck dazu.
        teil['dreiecke'] = np.vstack([teil['dreiecke'], [[0, 1, 3]]])
        for saat in ('a', 'b', 'c', 'd'):
            aus = G9haarmischung.ausduennen(teil, 0.1, saat, groesste_behalten=True)
            self.assertTrue(np.any(np.all(aus['punkte'] == [0, 0, 0], axis=1)), saat)

    def test_10_die_fehlende_vierte_ecke_liest_keinen_fremden_punkt(self):
        u"""`[a, b, c, -1]` — `behalten[-1]` laese still den LETZTEN Punkt."""
        teil = inselnetz(20)
        teil['dreiecke'] = np.hstack([teil['dreiecke'],
                                      np.full((len(teil['dreiecke']), 1), -1)])
        aus = G9haarmischung.ausduennen(teil, 0.5, 'probe')
        self.assertTrue(np.all(aus['dreiecke'][:, 3] == -1))
        self.assertLess(int(aus['dreiecke'][:, :3].max()), len(aus['punkte']))
