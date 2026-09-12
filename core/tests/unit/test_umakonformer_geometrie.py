# -*- coding: utf-8 -*-
u"""Die vier Geometriebausteine des Konformers, einzeln geprueft.

Probe aus der Abdeckungstabelle (`UMA_Python/abdeckung.py`); die
Tabelle nennt jede Testmethode hier beim Namen, `test_umaabdeckung_
tabelle` haelt das. Herausgeloest aus `test_umaabdeckung` (12.09.2026).
"""
import unittest

import numpy as np

from ._umaabdeckung import Netzgeometrie
from .test_umakonformer import zylinder


class Geometriebausteine(unittest.TestCase):
    u"""Die vier Bausteine, die bisher nur mittelbar geprüft waren."""

    databases = set()

    def setUp(self):
        self.ecken = np.array([[[0.0, 0.0, 0.0],
                                [1.0, 0.0, 0.0],
                                [0.0, 1.0, 0.0]]])

    def test_baryzentrisch_trifft_die_ecken_und_die_mitte(self):
        u"""`CalculateBarycentric`. Die drei Ecken müssen (1,0,0), (0,1,0)
        und (0,0,1) ergeben, der Schwerpunkt dreimal ein Drittel."""
        ecken = np.repeat(self.ecken, 4, axis=0)
        punkte = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0],
                           [0.0, 1.0, 0.0], [1 / 3, 1 / 3, 0.0]])
        bary = Netzgeometrie.baryzentrisch(punkte, ecken)
        np.testing.assert_allclose(bary[0], [1, 0, 0], atol=1e-12)
        np.testing.assert_allclose(bary[1], [0, 1, 0], atol=1e-12)
        np.testing.assert_allclose(bary[2], [0, 0, 1], atol=1e-12)
        np.testing.assert_allclose(bary[3], [1 / 3, 1 / 3, 1 / 3], atol=1e-12)
        # Die Summe ist immer 1 — das ist die Probe, die bei einem
        # Vorzeichenfehler fällt.
        np.testing.assert_allclose(bary.sum(axis=1), 1.0, atol=1e-12)

    def test_normale_wird_zur_bezugsrichtung_gedreht(self):
        u"""`OrientNormalToReference`: Eine Normale, die dem Bezug den
        Rücken kehrt, wird umgedreht — die andere bleibt.

        Ohne das kippt der ganze Stoff auf die Innenseite, sobald ein
        Körperdreieck falsch herum gewickelt ist."""
        normalen = np.array([[0.0, 1.0, 0.0], [0.0, -1.0, 0.0]])
        bezug = np.array([[0.0, 1.0, 0.0], [0.0, 1.0, 0.0]])
        gedreht = Netzgeometrie.normalen_ausrichten(normalen, bezug)
        np.testing.assert_allclose(gedreht[0], [0, 1, 0])
        np.testing.assert_allclose(gedreht[1], [0, 1, 0])

    def test_punktnormalen_sind_radial_und_normiert(self):
        u"""`CalculateNormals` auf einem Zylinder: Jede Punktnormale muss
        RADIAL stehen und die Länge 1 haben.

        Radial, nicht „nach aussen": Wohin sie zeigen, entscheidet die
        Wickelrichtung des Netzes, und die ist eine Eigenschaft der
        EINGABE. UMA sichert hier nichts zu — es dreht die Normalen erst
        in `OrientNormalToReference` auf eine Bezugsrichtung. Wer hier
        „nach aussen" prüft, prüft seine eigene Vorrichtung: Dieser
        Zylinder wickelt nach innen (gemessen Median −1,0).
        """
        punkte, dreiecke = zylinder(0.2)
        n = Netzgeometrie.punktnormalen(punkte, dreiecke)
        np.testing.assert_allclose(np.linalg.norm(n, axis=1), 1.0,
                                   atol=1e-9)
        radial = punkte.copy()
        radial[:, 1] = 0.0
        radial /= np.linalg.norm(radial, axis=1, keepdims=True)
        richtung = (n * radial).sum(axis=1)
        # Deckel und Boden fehlen, deshalb der Median statt des Minimums.
        self.assertGreater(abs(float(np.median(richtung))), 0.99)
        # Und alle in DERSELBEN Richtung — eine gemischte Wickelung
        # wäre ein echter Befund.
        self.assertGreater(abs(float(np.sign(richtung).mean())), 0.9)

    def test_nachbarschaft_ist_symmetrisch_und_ohne_selbstbezug(self):
        u"""`BuildAdjacency`. Zwei Eigenschaften, die eine Glättung
        stillschweigend verfälschen, wenn sie fehlen: Ein Punkt darf nicht
        sein eigener Nachbar sein (er zöge sich selbst an), und die
        Beziehung muss in beide Richtungen stehen."""
        punkte, dreiecke = zylinder(0.2, ringe=8, stufen=4)
        starts, nachbarn = Netzgeometrie.nachbarschaft(len(punkte), dreiecke)
        self.assertEqual(len(starts), len(punkte) + 1)
        paare = set()
        for i in range(len(punkte)):
            for j in nachbarn[starts[i]:starts[i + 1]]:
                self.assertNotEqual(i, int(j), u'Punkt %d ist sein eigener '
                                               u'Nachbar' % i)
                paare.add((i, int(j)))
        fehlend = [(a, b) for a, b in paare if (b, a) not in paare]
        self.assertEqual(fehlend, [], u'Nachbarschaft nicht symmetrisch')

    def test_interpolierte_normale_liegt_zwischen_den_ecken(self):
        u"""`InterpolateNormal`: In der Mitte eines Dreiecks das Mittel der
        drei Eckennormalen, an einer Ecke genau deren Normale."""
        pn = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        dreiecke = np.array([[0, 1, 2]])
        bary = np.array([[1.0, 0.0, 0.0], [1 / 3, 1 / 3, 1 / 3]])
        n = Netzgeometrie.normale_interpolieren(pn, dreiecke,
                                                np.array([0, 0]), bary)
        np.testing.assert_allclose(n[0], [1, 0, 0], atol=1e-12)
        np.testing.assert_allclose(n[1], np.ones(3) / np.sqrt(3), atol=1e-12)
