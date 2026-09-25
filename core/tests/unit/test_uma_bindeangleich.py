# -*- coding: utf-8 -*-
u"""UMA_Python.Bindeangleich — ein Slot mit eigenem Netzraum (25.09.2026).

Anlass: `M_Wrapped Pants_slot` lag im Browser flach vor der Figur, weil
`Verschmelzen._posen` die Bindeposen des Koerpers fuer alle Slots setzt und
die gedrehten der Hose verwarf. Kunstslots, kein UMA-Projekt:

1. Ein Slot mit derselben Bindepose wie der Koerper kommt unveraendert
   durch (dasselbe Objekt).
2. Ein Slot mit um 90 Grad um X gedrehter Bindepose: seine Punkte werden
   so umgerechnet, dass Haeuten mit der KOERPER-Bindepose dieselbe Weltlage
   ergibt wie mit seiner eigenen — `R · v' == B · v`.
3. Gemischte Gewichte mischen die Wandel je Knochen.

Sabotage: `_wandel` immer `None` -> Fall 2 rot (die Hose laege wieder flach).
"""
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from UMA_Python.bindeangleich import Bindeangleich

DREH_X = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=float)


class _Slot:
    def __init__(self, punkte, posen, gewichte=None, index=None):
        self.punkte = np.asarray(punkte, dtype=float)
        self.normalen = np.tile([0.0, 0.0, 1.0], (len(self.punkte), 1))
        self.bindeposen = [np.asarray(p, dtype=float) for p in posen]
        self.hautknochen = list(range(1, len(posen) + 1))
        n = len(self.punkte)
        self.gewichte = np.ones((n, 1)) if gewichte is None else np.asarray(gewichte, dtype=float)
        self.knochenindex = np.zeros((n, 1), dtype=int) if index is None else np.asarray(index)
        self.formen = {'F': np.tile([0.0, 0.0, 0.1], (n, 1))}
        self.formnormalen = {}


NACH_HASH = {1: 0, 2: 1}


class Bindeangleichfaelle(SimpleTestCase):

    def test_1_gleiche_bindepose_bleibt(self):
        koerper = _Slot([[0, 0, 1]], [np.eye(4)])
        kleid = _Slot([[0, 0, 2]], [np.eye(4)])
        aus = Bindeangleich.slots([koerper, kleid], NACH_HASH)
        self.assertIs(aus[1], kleid)

    def test_2_gedrehte_bindepose_wird_umgerechnet(self):
        koerper = _Slot([[0, 0, 1]], [np.eye(4)])
        kleid = _Slot([[0.1, 0.2, 0.3]], [DREH_X])
        aus = Bindeangleich.slots([koerper, kleid], NACH_HASH)[1]
        erwartet = (DREH_X @ [0.1, 0.2, 0.3, 1])[:3]
        np.testing.assert_allclose(aus.punkte[0], erwartet, atol=1e-9)
        np.testing.assert_allclose(aus.normalen[0], DREH_X[:3, :3] @ [0, 0, 1], atol=1e-9)
        np.testing.assert_allclose(aus.formen['F'][0], DREH_X[:3, :3] @ [0, 0, 0.1], atol=1e-9)
        self.assertEqual(aus.hautknochen, kleid.hautknochen)   # der Rest kommt vom Slot

    def test_2b_sabotage_ohne_wandel(self):
        koerper = _Slot([[0, 0, 1]], [np.eye(4)])
        kleid = _Slot([[0.1, 0.2, 0.3]], [DREH_X])
        with mock.patch.object(Bindeangleich, '_wandel', return_value=None):
            aus = Bindeangleich.slots([koerper, kleid], NACH_HASH)[1]
        erwartet = (DREH_X @ [0.1, 0.2, 0.3, 1])[:3]
        self.assertFalse(np.allclose(aus.punkte[0], erwartet))

    def test_3_gewichte_mischen(self):
        koerper = _Slot([[0, 0, 1]], [np.eye(4), np.eye(4)])
        verschoben = np.eye(4)
        verschoben[:3, 3] = [0.0, 0.0, 1.0]
        kleid = _Slot([[0, 0, 0]], [np.eye(4), verschoben],
                      gewichte=[[0.5, 0.5]], index=[[0, 1]])
        aus = Bindeangleich.slots([koerper, kleid], NACH_HASH)[1]
        np.testing.assert_allclose(aus.punkte[0], [0, 0, 0.5], atol=1e-9)
