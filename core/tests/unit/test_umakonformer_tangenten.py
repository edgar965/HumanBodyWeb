# -*- coding: utf-8 -*-
u"""Tangenten aus UV und Normalen — wie UMAs `CalculateTangents`.

Probe aus der Abdeckungstabelle (`UMA_Python/abdeckung.py`); die
Tabelle nennt jede Testmethode hier beim Namen, `test_umaabdeckung_
tabelle` haelt das. Herausgeloest aus `test_umaabdeckung` (12.09.2026).
"""
import unittest

import numpy as np

from ._umaabdeckung import Einstellungen, Kleidungskonformer, Netzgeometrie
from .test_umakonformer import zylinder


class Tangenten(unittest.TestCase):
    u"""`CalculateTangents` — am 08.09.2026 nachportiert."""

    databases = set()

    def setUp(self):
        # Ein Quadrat in der XY-Ebene mit der üblichen UV-Belegung.
        self.punkte = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0],
                                [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]])
        self.uv = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
        self.dreiecke = np.array([[0, 1, 2], [0, 2, 3]])
        self.normalen = np.tile([0.0, 0.0, 1.0], (4, 1))

    def test_standard_uv_ergibt_die_x_achse(self):
        u"""u wächst mit x — die Tangente MUSS +X sein, Händigkeit +1."""
        t = Netzgeometrie.tangenten(self.punkte, self.normalen, self.uv,
                                    self.dreiecke)
        self.assertEqual(t.shape, (4, 4))
        for zeile in t:
            np.testing.assert_allclose(zeile, [1, 0, 0, 1], atol=1e-12)

    def test_gespiegeltes_u_dreht_tangente_und_haendigkeit(self):
        u"""Die Händigkeit ist die Spalte, die man beim Portieren vergisst
        — und ohne sie steht eine Normal-Map seitenverkehrt."""
        uv = np.array([[1.0, 0.0], [0.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        t = Netzgeometrie.tangenten(self.punkte, self.normalen, uv,
                                    self.dreiecke)
        np.testing.assert_allclose(t[0], [-1, 0, 0, -1], atol=1e-12)

    def test_tangente_steht_senkrecht_auf_der_normale(self):
        u"""Gram-Schmidt: Das Skalarprodukt muss null sein, sonst ist die
        Orthogonalisierung nicht gelaufen."""
        gedreht = np.tile([0.0, 0.6, 0.8], (4, 1))
        t = Netzgeometrie.tangenten(self.punkte, gedreht, self.uv,
                                    self.dreiecke)
        np.testing.assert_allclose((t[:, :3] * gedreht).sum(axis=1), 0.0,
                                   atol=1e-12)
        np.testing.assert_allclose(np.linalg.norm(t[:, :3], axis=1), 1.0,
                                   atol=1e-12)

    def test_ohne_uv_kommen_einheitstangenten(self):
        u"""Wie im Original: `(1,0,0,1)`, keine Ausnahme. GarmentCode-Netze
        haben keine UV — eine Ausnahme mitten im Anwenden wäre hier der
        schlechtere Weg."""
        for uv in (None, self.uv[:2]):
            t = Netzgeometrie.tangenten(self.punkte, self.normalen, uv,
                                        self.dreiecke)
            self.assertEqual(t.shape, (4, 4))
            np.testing.assert_allclose(t[0], [1, 0, 0, 1])

    def test_entartete_uv_wird_uebergangen(self):
        u"""Ein Dreieck ohne UV-Fläche (alle drei Punkte auf demselben
        UV-Wert) darf nicht durch null teilen."""
        uv = np.zeros((4, 2))
        t = Netzgeometrie.tangenten(self.punkte, self.normalen, uv,
                                    self.dreiecke)
        self.assertTrue(np.isfinite(t).all())
        np.testing.assert_allclose(t[0], [1, 0, 0, 1])

    def test_tangenten_werden_nach_dem_anwenden_neu_gerechnet(self):
        u"""Der Unterschied zu UMA: Die Tangente wird nicht mitgeführt,
        sondern aus dem VERFORMTEN Netz gerechnet. Die Probe darauf ist,
        dass sie sich mit der Verformung ändert."""
        koerper, k_tri = zylinder(0.20)
        stoff, s_tri = zylinder(0.21, ringe=18, stufen=12)
        # UV: Winkel und Höhe des Zylinders.
        winkel = np.arctan2(stoff[:, 2], stoff[:, 0])
        uv = np.column_stack([(winkel + np.pi) / (2 * np.pi), stoff[:, 1]])

        k = Kleidungskonformer(koerper, k_tri)
        b = k.binden('huelle', stoff, s_tri)
        vorher = Netzgeometrie.tangenten(stoff, None, uv, s_tri)

        # Zylinder oben aufweiten -> die Fläche kippt, die Tangente auch.
        weit = koerper.copy()
        weit[:, [0, 2]] *= 1.0 + 0.5 * weit[:, 1:2]
        gelegt = k.anwenden(b, weit)
        nachher = Netzgeometrie.tangenten(gelegt, None, uv, s_tri)

        wanderung = np.linalg.norm(nachher[:, :3] - vorher[:, :3], axis=1)
        # Gemessen 0,028 bei dieser Verformung; die Schwelle liegt
        # darunter, aber deutlich über dem Rauschen (1e-9 bei
        # unverändertem Körper — die Gegenprobe steht darunter).
        self.assertGreater(float(wanderung.max()), 0.01,
                           u'Die Tangenten haben sich nicht bewegt — dann '
                           u'beschreiben sie die alte Oberfläche')
        # GEGENPROBE: Ohne Verformung dürfen sie sich NICHT bewegen.
        # Dazu muss die Glättung aus sein — sie ist in `Einstellungen`
        # VORGABE und verändert das Netz auch bei unverändertem Körper.
        still = Kleidungskonformer(
            koerper, k_tri,
            Einstellungen(glaetten=False, tangential_halten=True))
        b2 = still.binden('huelle', stoff, s_tri)
        ruhe = Netzgeometrie.tangenten(still.anwenden(b2), None, uv,
                                       s_tri)
        self.assertLess(
            float(np.linalg.norm(ruhe[:, :3] - vorher[:, :3],
                                 axis=1).max()), 1e-6)
