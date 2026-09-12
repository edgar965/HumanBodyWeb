# -*- coding: utf-8 -*-
u"""Der portierte UMA-Konformer gegen UMAs eigene Testfälle.

Die ersten vier Fälle sind Zeile für Zeile aus
`UMA/UMAProject/Assets/UMA/Core/Editor/Tests/UMAClothingConformerTests.cs`
übernommen — dieselben Zahlen, dieselben Erwartungen. Sie sind die Probe
darauf, dass die VEKTORISIERUNG nichts verschoben hat: Der Port rechnet
nicht Punkt für Punkt wie das Original, sondern über ganze Felder.

Danach folgen die Gegenproben, die UMA nicht hat und die hier nötig sind:
die zweite, unabhängige Ericson-Fassung des Projekts, die relative
Entartungsschwelle und die Ruhe-Probe.
"""
import sys
import unittest
from pathlib import Path

import numpy as np

from django.conf import settings

sys.path.insert(0, str(Path(settings.TOOLS_ROOT)))

from UMA_Python.netzgeometrie import Netzgeometrie          # noqa: E402
from UMA_Python.nahtgruppen import Nahtgruppen              # noqa: E402
from UMA_Python.glaettung import Glaettung                  # noqa: E402


class UmaOriginalfaelle(unittest.TestCase):
    u"""Die vier Fälle aus UMAs eigener NUnit-Suite."""

    databases = set()

    def test_mapping_haelt_den_normalabstand_nach_einer_koerperaenderung(self):
        u"""`MappingRoundTripPreservesSurfaceNormalOffsetAfterBodyDelta`."""
        a, b, c = (np.array([0., 0, 0]), np.array([1., 0, 0]),
                   np.array([0., 1, 0]))
        kleid = np.array([0.2, 0.3, 0.05])
        ecken = np.array([[a, b, c]])
        fuss = Netzgeometrie.naechster_punkt_im_dreieck(kleid[None], ecken)[0]
        bary = Netzgeometrie.baryzentrisch(fuss[None], ecken)[0]
        abstand = np.dot(kleid - fuss, np.array([0., 0, 1]))

        delta = np.array([0., 0, 0.1])          # der Körper wandert 10 cm vor
        flaeche = (bary[0] * (a + delta) + bary[1] * (b + delta)
                   + bary[2] * (c + delta))
        konform = flaeche + abstand * np.array([0., 0, 1])

        self.assertAlmostEqual(konform[0], 0.2, places=5)
        self.assertAlmostEqual(konform[1], 0.3, places=5)
        self.assertAlmostEqual(konform[2], 0.15, places=5)

    def test_fusspunkt_liegt_auf_der_kante_wenn_der_punkt_draussen_ist(self):
        u"""`ClosestPointReturnsTriangleEdgeForOutsidePoint`."""
        ecken = np.array([[[0., 0, 0], [1., 0, 0], [0., 1, 0]]])
        p = Netzgeometrie.naechster_punkt_im_dreieck(
            np.array([[1.5, 0.5, 0.]]), ecken)[0]
        self.assertAlmostEqual(p[0] + p[1], 1.0, places=5)
        self.assertAlmostEqual(p[2], 0.0, places=5)

    def test_nahtgruppen_fassen_uv_kopien_aber_keine_kantennachbarn(self):
        u"""`WeldGroupsJoinUvSplitCopiesButNotConnectedMeshEdges`."""
        punkte = np.array([[0., 0, 0], [1., 0, 0], [0., 1, 0],
                           [0.00001, 0, 0], [-1., 0, 0], [0., -1, 0]])
        dreiecke = np.array([[0, 1, 2], [3, 4, 5]])
        gruppen = Nahtgruppen.bauen(punkte, dreiecke, 0.0001)

        self.assertGreaterEqual(gruppen[0], 0)
        self.assertEqual(gruppen[3], gruppen[0])
        self.assertEqual(gruppen[1], -1)      # durch eine Kante verbunden

    def test_seite_folgt_der_bindezeit_auch_bei_nach_innen_zeigender_normale(self):
        u"""`CollisionSideFollowsTheOriginalClothingSideOfAnInwardNormal`."""
        flaechennormale = np.array([[0., 0, -1]])
        stoffnormale = np.array([[0., 0, 1]])
        seite = Netzgeometrie.seite(np.array([-0.01]), stoffnormale,
                                    flaechennormale)
        nach_aussen = flaechennormale[0] * seite[0]

        self.assertAlmostEqual(seite[0], -1.0, places=5)
        self.assertGreater(np.dot(nach_aussen, stoffnormale[0]), 0.999)


class ZweiteFassungDesselbenAlgorithmus(unittest.TestCase):
    u"""Gegen `GarmentFitter/dreiecksprojektion.py` — dieselbe Buchstelle
    (Ericson 5.1.5), unabhängig geschrieben. Weichen sie ab, hat eine der
    beiden einen Fehler."""

    databases = set()

    def test_beide_ericson_fassungen_liefern_denselben_fusspunkt(self):
        from assetCreator.GarmentFitter.dreiecksprojektion import DreiecksProjektion

        zufall = np.random.default_rng(20260908)
        ecken = zufall.normal(size=(400, 3, 3))
        punkte = zufall.normal(size=(400, 3)) * 2.0

        meins = Netzgeometrie.naechster_punkt_im_dreieck(punkte, ecken)
        seins, _ = DreiecksProjektion._naechster_punkt_im_dreieck(punkte, ecken)

        abweichung = np.linalg.norm(meins - seins, axis=1)
        self.assertLess(abweichung.max(), 1e-9,
                        'Die beiden Ericson-Fassungen weichen ab: max %.3e'
                        % abweichung.max())


class RelativeEntartungsschwelle(unittest.TestCase):
    u"""Die Abweichung vom Original, die am meisten bewirkt hat."""

    databases = set()

    @staticmethod
    def _feines_dreieck(kante_m):
        u"""Ein gesundes, gleichseitiges Dreieck der gegebenen Kantenlänge."""
        return np.array([[[0., 0, 0], [kante_m, 0, 0],
                          [kante_m / 2, kante_m * 0.866, 0]]])

    def test_ein_zentimeter_dreieck_gilt_nicht_als_entartet(self):
        u"""Mit UMAs fester Schwelle 1e-8 fielen an `mean_all` 67,4 % der
        Dreiecke durch — der Punkt landete auf Ecke A."""
        ecken = self._feines_dreieck(0.0113)      # Median von `mean_all`
        mitte = ecken[0].mean(axis=0)[None]
        bary = Netzgeometrie.baryzentrisch(mitte, ecken)[0]

        # Der Schwerpunkt hat (1/3, 1/3, 1/3) — der Ersatzwert wäre (1, 0, 0).
        for gewicht in bary:
            self.assertAlmostEqual(gewicht, 1.0 / 3.0, places=6)

    def test_ein_wirklich_entartetes_dreieck_faellt_durch(self):
        u"""Gegenprobe: drei Punkte auf einer Geraden."""
        ecken = np.array([[[0., 0, 0], [1., 0, 0], [2., 0, 0]]])
        bary = Netzgeometrie.baryzentrisch(np.array([[0.5, 0., 0.]]), ecken)[0]
        np.testing.assert_allclose(bary, [1.0, 0.0, 0.0])

    def test_die_schwelle_haengt_nicht_an_der_einheit(self):
        u"""Dasselbe Dreieck in Metern und in Zentimetern muss dieselben
        Gewichte ergeben — genau das leistet eine feste Schwelle nicht."""
        for kante in (0.01, 1.0, 100.0):
            ecken = self._feines_dreieck(kante)
            bary = Netzgeometrie.baryzentrisch(ecken[0].mean(axis=0)[None],
                                               ecken)[0]
            self.assertAlmostEqual(bary[0], 1.0 / 3.0, places=6,
                                   msg='Kantenlänge %g' % kante)


class GlaettungHaeltDieGroesse(unittest.TestCase):
    u"""Laplace schrumpft, Taubin und HC nicht — der Grund, warum es drei
    Verfahren gibt."""

    databases = set()

    @staticmethod
    def _kugel(n=200):
        zufall = np.random.default_rng(7)
        richtung = zufall.normal(size=(n, 3))
        richtung /= np.linalg.norm(richtung, axis=1, keepdims=True)
        from scipy.spatial import ConvexHull
        huelle = ConvexHull(richtung)
        return richtung, huelle.simplices.astype(np.int64)

    def _radius(self, punkte):
        return float(np.linalg.norm(punkte, axis=1).mean())

    def test_laplace_schrumpft_und_hc_haelt(self):
        punkte, dreiecke = self._kugel()
        nachbarn = Netzgeometrie.nachbarschaft(len(punkte), dreiecke)
        vorher = self._radius(punkte)

        laplace = Glaettung.glaetten(punkte, nachbarn, 'laplace',
                                     durchgaenge=20, staerke=0.5)
        hc = Glaettung.glaetten(punkte, nachbarn, 'hc',
                                durchgaenge=20, staerke=0.5)

        self.assertLess(self._radius(laplace), vorher * 0.97,
                        'Laplace müsste sichtbar schrumpfen')
        self.assertGreater(self._radius(hc), self._radius(laplace),
                           'HC muss weniger schrumpfen als Laplace')

    def test_gesperrte_punkte_bleiben_liegen(self):
        punkte, dreiecke = self._kugel()
        nachbarn = Netzgeometrie.nachbarschaft(len(punkte), dreiecke)
        darf = np.zeros(len(punkte), dtype=bool)
        darf[:50] = True

        raus = Glaettung.glaetten(punkte, nachbarn, 'hc', durchgaenge=5,
                                  betroffen=darf)
        np.testing.assert_allclose(raus[50:], punkte[50:], atol=1e-12)
        self.assertGreater(np.abs(raus[:50] - punkte[:50]).max(), 0.0)

    def test_unbekanntes_verfahren_wird_gemeldet(self):
        punkte, dreiecke = self._kugel()
        nachbarn = Netzgeometrie.nachbarschaft(len(punkte), dreiecke)
        with self.assertRaises(ValueError):
            Glaettung.glaetten(punkte, nachbarn, 'kaputt')
