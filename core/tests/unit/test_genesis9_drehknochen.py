# -*- coding: utf-8 -*-
u"""Daz' Twist-Knochen folgen ihrem Glied per Formel (`G9drehknochen`,
20.09.2026 nachts; Edgar mit Bild: „der Arm bei der Dance1_smplx ist kaputt",
Bild 95 — SMPL-X dreht den Unterarm dort 118 Grad um seine Achse, und auf
Genesis 9 sass die ganze Verdrehung am Ellbogen).

1. `lesen`: aus den Knotenformeln `push url, push val, mult` je Twist-Knochen
   `{von, quelle, achse, faktor}`; die Achsen koennen sich unterscheiden
   (Mittelfuss z an Fuss z, Oberschenkel y), Praefix `name:#` und `#` egal.
2. Nicht gelesen: Formeln auf den eigenen Knochen, andere Operationen,
   Ausgaben, die keine Drehung sind, Eingaben ohne Knochen.
3. `G9felderapi.achsen` haengt `dreh` nur an die Knochen mit Formel.

Sabotage: `KANAL` ohne das optionale Praefix -> Fall 1 rot (Daz schreibt
`l_forearm:#l_forearm?rotation/x`).
"""
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.drehknochen import G9drehknochen
from Genesis9.skelett import G9skelett

from core.api.g9felder import G9felderapi


def _formel(ziel, von, faktor, achse='x', quelle='x'):
    return {'output': '%s:#%s?rotation/%s' % (ziel, ziel, achse),
            'operations': [{'op': 'push', 'url': '%s:#%s?rotation/%s' % (von, von, quelle)},
                           {'op': 'push', 'val': faktor}, {'op': 'mult'}]}


KNOCHEN = [
    {'id': 'l_forearm'},
    {'id': 'l_forearmtwist1', 'formulas': [_formel('l_forearmtwist1', 'l_forearm', -0.8333333)]},
    {'id': 'l_thightwist1', 'formulas': [_formel('l_thightwist1', 'l_thigh', -0.7, 'y', 'y')]},
    {'id': 'l_metatarsal', 'formulas': [{'output': '#l_metatarsal?rotation/z', 'operations': [
        {'op': 'push', 'url': '#l_foot?rotation/z'}, {'op': 'push', 'val': -0.4444444}, {'op': 'mult'}]}]},
]


class Drehknochen(SimpleTestCase):

    databases = set()

    def test_1_formeln_lesen(self):
        aus = G9drehknochen.lesen(KNOCHEN)
        self.assertEqual(aus, {
            'l_forearmtwist1': {'von': 'l_forearm', 'quelle': 'x', 'achse': 'x', 'faktor': -0.8333333},
            'l_thightwist1': {'von': 'l_thigh', 'quelle': 'y', 'achse': 'y', 'faktor': -0.7},
            'l_metatarsal': {'von': 'l_foot', 'quelle': 'z', 'achse': 'z', 'faktor': -0.4444444},
        })

    def test_2_was_keine_drehformel_ist(self):
        eigene = {'id': 'k', 'formulas': [_formel('k', 'k', 0.5)]}                 # auf sich selbst
        summe = {'id': 'k2', 'formulas': [{'output': 'k2:#k2?rotation/x', 'operations': [
            {'op': 'push', 'url': 'a:#a?rotation/x'}, {'op': 'push', 'url': 'b:#b?rotation/x'},
            {'op': 'add'}]}]}
        skalierung = {'id': 'k3', 'formulas': [{'output': 'k3:#k3?scale/x', 'operations': [
            {'op': 'push', 'url': 'a:#a?rotation/x'}, {'op': 'push', 'val': 2.0}, {'op': 'mult'}]}]}
        regler = {'id': 'k4', 'formulas': [{'output': 'k4:#k4?rotation/x', 'operations': [
            {'op': 'push', 'url': 'Genesis9:/data/x.dsf#CTRLArmsUp?value'},
            {'op': 'push', 'val': 2.0}, {'op': 'mult'}]}]}
        self.assertEqual(G9drehknochen.lesen([eigene, summe, skalierung, regler]), {})

    def test_3_achsen_tragen_dreh(self):
        roh = [{'name': 'l_forearm', 'orientation': np.array([1.0, -13.9, -42.2]), 'reihenfolge': 'XZY'},
               {'name': 'l_forearmtwist1', 'orientation': np.array([1.0, -13.9, -42.2]),
                'reihenfolge': 'XZY'}]
        with mock.patch.object(G9skelett, 'roh', classmethod(lambda cls: roh)), \
                mock.patch.object(G9drehknochen, 'tabelle',
                                  classmethod(lambda cls: G9drehknochen.lesen(KNOCHEN))):
            achsen = G9felderapi.achsen()
        self.assertNotIn('dreh', achsen['l_forearm'])
        self.assertEqual(achsen['l_forearmtwist1']['dreh']['von'], 'l_forearm')
        self.assertEqual(achsen['l_forearmtwist1']['r'], 'XZY')
