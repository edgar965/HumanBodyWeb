# -*- coding: utf-8 -*-
u"""Der Schnitt eines Stuecks (Laenge < 0) ist ein RAND des Netzes
(`G9passformschnitt`, 20.09.2026 nachts; Edgar mit Bild: „t-shirt besser,
aber noch immer fehler bei der Animation" — ein Zackensaum auf Stufe 1).

Ein Streifen 3 × 5 Punkte (8 Vierecke, Hoehe 4), Schnittlinie bei 1,5:

1. `flaechen`: die zwei Vierecke ganz unter der Linie fallen weg, die zwei,
   die sie kreuzen, bleiben; `ueber` traegt die neuen Flaechennummern;
   ohne Kuerzung (hub 0) None.
2. `kuerzen` legt die Reihe unter der Linie auf ihre Kante genau auf 1,5,
   und mit den geschnittenen Flaechen halten die Catmull-Clark-Punkte des
   Saums (alte Punkte und Kantenpunkte) die Hoehe 1,5 — der Saum ist Rand.
3. Gegenprobe: mit ALLEN Flaechen (Nullflaechen unter der Linie, die erste
   Fassung) rueckt der mittlere Saumpunkt ueber die Linie — das war der
   Zackensaum.
4. `G9passformhaut.netzstufe`: ohne Schnitt die Stufe des Stuecks, mit
   Schnitt eine eigene mit weniger Flaechen (Stufe 0 ohne Ablage).

Sabotage: `flaechen` behaelt alle Flaechen -> Fall 1 und 2 rot.
"""
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.passform import G9passform
from Genesis9.passformhaut import G9passformhaut
from Genesis9.passformschnitt import G9passformschnitt
from Genesis9.unterteilung import G9unterteilung
from humanbody_core.unterteilungsstufe import Unterteilungsstufe

LINIE = 1.5


def _streifen():
    u"""3 Spalten (x), 5 Reihen (y = 0..4); Punkt = reihe * 3 + spalte."""
    punkte = np.array([[x, y, 0.0] for y in range(5) for x in range(3)], dtype=np.float64)
    polys = []
    for y in range(4):
        for x in range(2):
            a = y * 3 + x
            polys.append([0, 0, a, a + 1, a + 4, a + 3])
    uvs = punkte[:, :2] / 4.0
    ueber = {(7, 14): 3, (0, 0): 4}       # zwei Naehte: Flaeche 7 und Flaeche 0
    return SimpleNamespace(punkte=punkte, polys=polys, _uvsatz=(uvs, ueber),
                           materialnamen=['stoff'], unterteilbar=True,
                           _stufenname=lambda: 'streifen', netzstufe=lambda s: 'eigene')


class Passformschnitt(SimpleTestCase):

    databases = set()

    def test_1_flaechen_unter_der_linie_fallen_weg(self):
        f = _streifen()
        polys, ueber = G9passformschnitt.flaechen(f, LINIE)
        self.assertEqual(len(polys), 6)
        self.assertEqual([p[2] for p in polys], [3, 4, 6, 7, 9, 10])   # ab Reihe 1
        self.assertEqual(ueber, {(5, 14): 3})       # Flaeche 7 heisst jetzt 5, Flaeche 0 ist weg
        self.assertIsNone(G9passformschnitt.flaechen(f, 0.0))
        self.assertIsNone(G9passformschnitt.flaechen(f, -1.0))

    def _saum_auf_stufe_1(self, polys):
        f = _streifen()
        aus = G9passform.kuerzen(f, f.punkte.copy(), LINIE)
        np.testing.assert_allclose(aus[3:6, 1], LINIE)       # Reihe 1 auf der Linie
        np.testing.assert_allclose(aus[0:3, 1], LINIE)       # Reihe 0 auf den Saum gerueckt
        np.testing.assert_allclose(aus[6:, 1], f.punkte[6:, 1])   # darueber unveraendert
        stufe = Unterteilungsstufe(G9unterteilung.flaechen(polys), len(aus))
        gewichte, _neu, _n = stufe.bauen()
        fein = gewichte @ aus
        kanten = [stufe.N_v + stufe.N_f + stufe.edge_map[(3, 4)],
                  stufe.N_v + stufe.N_f + stufe.edge_map[(4, 5)]]
        # Der mittlere Saumpunkt (4) und die beiden Saumkanten; die Ecken 3 und 5
        # sind Streifen-Ecken (ein Randnachbar liegt hoeher) — am Hemd ist der
        # Saum ein geschlossener Ring ohne Ecken.
        return fein[4, 1], fein[kanten, 1]

    def test_2_geschnitten_bleibt_der_saum_auf_der_linie(self):
        f = _streifen()
        polys, _ueber = G9passformschnitt.flaechen(f, LINIE)
        punkt, kanten = self._saum_auf_stufe_1(polys)
        self.assertAlmostEqual(punkt, LINIE)
        np.testing.assert_allclose(kanten, LINIE)

    def test_3_gegenprobe_mit_nullflaechen_zieht_es_den_saum_hoch(self):
        f = _streifen()
        punkt, _kanten = self._saum_auf_stufe_1(f.polys)
        self.assertGreater(punkt, LINIE + 0.03)     # (F + 2R + P) / 4 = 1,5625

    def test_4_stand_mit_schnitt_hat_eigene_stufe(self):
        f = _streifen()
        stand = G9passformhaut.__new__(G9passformhaut)
        stand.folger, stand.laenge, stand.schluessel = f, -150.0, 'l-150_w0'
        stand._netzstufen = {}
        stand.schnitt = None
        self.assertEqual(stand.netzstufe(1), 'eigene')
        stand.schnitt = G9passformschnitt.flaechen(f, LINIE)
        with mock.patch('Genesis9.netzstufe.G9netzstufe._teilungabgelegt',
                        side_effect=lambda name, polys, mn, uvs, ueber: (
                            np.arange(15), np.zeros((15, 2)), np.zeros((0, 3), dtype=np.int64), [])):
            stufe = stand.netzstufe(0)
        self.assertEqual(len(stufe.polys), 6)
        self.assertEqual(stufe.name, 'streifen_l-150_w0')
        self.assertIs(stand.netzstufe(0), stufe)
