# -*- coding: utf-8 -*-
u"""HS Viola Hair (20.09.2026): Strangverdichtung, OmniHair-Farben, unsichtbare
Knoten — Kunstdaten, keine Bibliothek.

Sabotage-Gegenproben:
- `G9strangverdichtung.__init__`: `genannt.all()` immer True → `test_1` rot
  (Punkte bleiben 12 statt 4).
- `morphe_anwenden`: `umnummer` nicht angewandt → `test_2` rot (Delta landet
  auf Punkt 9 statt auf dem umnummerierten Punkt 3).
- `G9haarfarben.farbe`: `lerp` ohne `√m` (Tint allein) → `test_3` rot (Amber
  [0,549 …] statt [0,5405 …]).
- `G9knotensicht.sichtbar`: `KANAL = 'Renderable'` → `test_4` rot (die Kappe
  mit `Visible: false` gilt als sichtbar).
"""
import numpy as np
from django.test import SimpleTestCase
from Genesis9.haarfarben import G9haarfarben
from Genesis9.knotensicht import G9knotensicht
from Genesis9.strangverdichtung import G9strangverdichtung


class Attrappenmorphe:
    u"""Wie `G9anhangmorphe`: `deltas[name] = (nummern, deltas)`, `eigene`."""

    def __init__(self, deltas):
        self.deltas = deltas

    def eigene(self, werte):
        return {k: v for k, v in werte.items() if k in self.deltas}

    def anwenden(self, punkte, werte):
        aus = np.array(punkte, dtype=np.float64, copy=True)
        for name, wert in self.eigene(werte).items():
            nummern, deltas = self.deltas[name]
            np.add.at(aus, nummern, deltas * float(wert))
        return aus


class StrangUndHaarfarben(SimpleTestCase):
    databases = set()

    def test_1_verdichtung_behaelt_nur_genannte_punkte(self):
        # Zwei Straehnen zu je 2 Punkten aus 12 gespeicherten (wie Viola: 8 von 60).
        zeilen = [[0, 0, 0, 9], [0, 0, 3, 11]]
        v = G9strangverdichtung(zeilen, 12)
        self.assertTrue(v.noetig)
        self.assertEqual(v.behalten.tolist(), [0, 3, 9, 11])
        punkte = np.arange(36, dtype=np.float64).reshape(12, 3)
        self.assertEqual(v.punkte(punkte).shape, (4, 3))
        self.assertEqual(v.punkte(punkte)[1].tolist(), punkte[3].tolist())
        self.assertEqual(v.zeilen(zeilen), [[0, 0, 0, 2], [0, 0, 1, 3]])
        # Nennt die Linie jeden Punkt (Pixie), aendert sich nichts.
        alle = G9strangverdichtung([[0, 0, 0, 1], [0, 0, 2, 3]], 4)
        self.assertFalse(alle.noetig)
        self.assertIs(alle.punkte(punkte), punkte)
        self.assertEqual(alle.zeilen(zeilen), zeilen)

    def test_2_morphe_in_neuer_nummerierung(self):
        v = G9strangverdichtung([[0, 0, 0, 9], [0, 0, 3, 11]], 12)
        morphe = Attrappenmorphe({'Move Front': (np.array([9, 5]),
                                                  np.array([[0.0, 0.0, 1.0],
                                                            [0.0, 5.0, 0.0]]))})
        punkte = np.zeros((4, 3))
        aus = v.morphe_anwenden(punkte, morphe, {'Move Front': 0.5})
        # Alter Punkt 9 ist neuer Punkt 2; Punkt 5 ist weggefallen.
        self.assertEqual(aus.tolist(), [[0, 0, 0], [0, 0, 0], [0, 0, 0.5], [0, 0, 0]])
        # Ohne Verdichtung laeuft das Original.
        alle = G9strangverdichtung([[0, 0, 0, 1]], 2)
        aus = alle.morphe_anwenden(np.zeros((2, 3)),
                                   Attrappenmorphe({'x': (np.array([1]),
                                                          np.array([[1.0, 0, 0]]))}),
                                   {'x': 2.0})
        self.assertEqual(aus.tolist(), [[0, 0, 0], [2.0, 0, 0]])

    def test_3_omnihair_rechnung(self):
        f = G9haarfarben.farbe
        # Weisser Tint: Melanin allein — Preset 6 (black) schwarz, 0 (white) hell.
        schwarz = f({'Melanin Presets': 6, 'Hair Root Color': [1, 1, 1]}, 'Hair Root Color')
        self.assertEqual(schwarz, [0.0314, 0.0036, 0.0001])
        weiss = f({'Melanin Presets': 0, 'Hair Root Color': [1, 1, 1]}, 'Hair Root Color')
        self.assertEqual(weiss, [1.0, 1.0, 1.0])
        # Custom 0,25 (Viola Light Blonde): Daz' Formel gibt ein goldenes Blond.
        blond = f({'Melanin Presets': 7, 'Melanin': 0.25, 'Hair Root Color': [1, 1, 1]},
                  'Hair Root Color')
        self.assertEqual(blond, [0.5085, 0.3941, 0.2362])
        # Tint ueber dark blonde (Viola Amber) — Wurzel und Spitze getrennt.
        w = {'Melanin Presets': 4, 'Hair Root Color': [0.5490196, 0.2352941, 0.2196078],
             'Hair Tip Color': [0.3490196, 0.1490196, 0.1411765]}
        self.assertEqual(f(w, 'Hair Root Color'), [0.5405, 0.3405, 0.2268])
        self.assertEqual(f(w, 'Hair Tip Color'), [0.4764, 0.2803, 0.1934])
        self.assertIsNone(f({'Melanin Presets': 4}, 'Hair Root Color'))
        # Mehr Melanin: dunkler — in jedem Kanal.
        hell = f({'Melanin Presets': 2, 'Hair Root Color': [0.5, 0.5, 0.5]}, 'Hair Root Color')
        dunkel = f({'Melanin Presets': 5, 'Hair Root Color': [0.5, 0.5, 0.5]}, 'Hair Root Color')
        self.assertTrue(all(a > b for a, b in zip(hell, dunkel)), (hell, dunkel))
        # `diffuse` auf der Kanalvorgabe ist nicht gestellt.
        self.assertFalse(G9haarfarben._gesetzt([0.5019608, 0.5019608, 0.5019608]))
        self.assertTrue(G9haarfarben._gesetzt([0.09, 0.15, 0.2]))
        self.assertFalse(G9haarfarben._gesetzt(None))
        treffer = G9haarfarben._ANIMATION.search(
            'x#materials/Hair:?extra/studio_material_channels/channels/Hair Tip Color/value')
        self.assertEqual((treffer.group(1), treffer.group(3)), ('Hair', 'Hair Tip Color'))
        self.assertEqual(G9haarfarben._ANIMATION.search('x#materials/Hair:?diffuse/value')
                         .group(2), 'diffuse')
        bilder = {'Hair': {'farbe': [0.5, 0.5, 0.5]}}
        # `ergaenzen` mit einer Datei, die es nicht gibt: nichts passiert.
        self.assertEqual(G9haarfarben.ergaenzen(bilder, 'gibt/es/nicht.duf'), bilder)

    def test_4_knotensicht(self):
        def knoten(wert, schluessel='current_value', kanal='Visible'):
            return {'extra': [{'type': 'studio_node_channels',
                               'channels': [{'channel': {'id': kanal, 'type': 'bool',
                                                         schluessel: wert}}]}]}
        self.assertFalse(G9knotensicht.sichtbar(knoten(False)))
        self.assertTrue(G9knotensicht.sichtbar(knoten(True)))
        self.assertFalse(G9knotensicht.sichtbar(knoten(False, 'value')))
        self.assertTrue(G9knotensicht.sichtbar(knoten(False, kanal='Renderable')))
        self.assertTrue(G9knotensicht.sichtbar({}))
        self.assertTrue(G9knotensicht.sichtbar(None))
        self.assertTrue(G9knotensicht.sichtbar({'extra': [{'type': 'anderes'}]}))
