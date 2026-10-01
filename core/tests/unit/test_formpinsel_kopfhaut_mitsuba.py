# -*- coding: utf-8 -*-
"""Form-Pinsel (`G9formpinsel`), Kopfhaut (`G9kopfhaut`), Dichte der Haarknoten (`Haarknotenauftrag`), Farben und
Normalen für Mitsuba (`Mitsubamaterial`), der Szenenschlüssel von `Genesishaarrender` (01.10.2026).

Kunstdaten, keine Grafikkarte, keine Bibliothek — der Abgleich Mitsuba gegen pyrender steht im LongRunner
`test_mitsuba_abgleich`.
"""
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase

import numpy as np
from Genesis9.formpinsel import G9formpinsel
from Genesis9.kopfhaut import G9kopfhaut

from core.dienste.genesishaarrender import Genesishaarrender
from core.dienste.haarknotenauftrag import Haarknotenauftrag
from core.dienste.mitsubamaterial import Mitsubamaterial


def _gitter(n=21, kante=0.2):
    """Ebene z = 0, n × n Punkte über `kante` m, mit Dreiecken."""
    a = np.linspace(-kante / 2, kante / 2, n)
    x, y = np.meshgrid(a, a)
    punkte = np.column_stack([x.ravel(), y.ravel(), np.zeros(n * n)])
    d = []
    for i in range(n - 1):
        for j in range(n - 1):
            k = i * n + j
            d += [[k, k + 1, k + n + 1], [k, k + n + 1, k + n]]
    return punkte, np.asarray(d)


class FormpinselTest(TestCase):
    def setUp(self):
        self.punkte, self.dreiecke = _gitter()
        self.mitte = int(np.argmin(np.linalg.norm(self.punkte, axis=1)))

    def _striche(self, p=(0.0, 0.0, 0.0), n=(0.0, 0.0, 1.0), d=(0.0, 0.0, 0.0), anzahl=1):
        return G9formpinsel.striche_lesen([{'p': list(p), 'n': list(n), 'd': list(d)}] * anzahl)

    def test_ziehen_und_druecken(self):
        hoch = G9formpinsel.deltas(self.punkte, self._striche(), 'ziehen', 0.05, 2.0, self.dreiecke)
        tief = G9formpinsel.deltas(self.punkte, self._striche(), 'druecken', 0.05, 2.0, self.dreiecke)
        self.assertAlmostEqual(hoch[self.mitte, 2], 2 * G9formpinsel.SCHRITT_M, places=9)
        self.assertAlmostEqual(tief[self.mitte, 2], -2 * G9formpinsel.SCHRITT_M, places=9)
        fern = np.linalg.norm(self.punkte, axis=1) > 0.05
        self.assertEqual(float(np.abs(hoch[fern]).max()), 0.0)
        # Mehr Tupfer heben weiter (gewichtet mit der Lage NACH den vorigen — knapp unter n × Schritt).
        zehn = G9formpinsel.deltas(self.punkte, self._striche(anzahl=10), 'ziehen', 0.05, 1.0, self.dreiecke)
        self.assertGreater(zehn[self.mitte, 2], 9 * G9formpinsel.SCHRITT_M)
        self.assertLess(zehn[self.mitte, 2], 10 * G9formpinsel.SCHRITT_M)

    def test_glaetten_nimmt_eine_spitze_zurueck(self):
        spitze = np.zeros_like(self.punkte)
        spitze[self.mitte, 2] = 0.01
        aus = G9formpinsel.deltas(self.punkte, self._striche(anzahl=5), 'glaetten', 0.03, 1.0, self.dreiecke, start=spitze)
        self.assertLess(aus[self.mitte, 2], 0.005)

    def test_flach_zieht_auf_die_ebene(self):
        buckel = np.zeros_like(self.punkte)
        buckel[:, 2] = 0.01 * G9formpinsel.abfall(np.linalg.norm(self.punkte, axis=1), 0.08)
        aus = G9formpinsel.deltas(self.punkte, self._striche(p=(0, 0, 0.0), anzahl=8), 'flach', 0.05, 1.0, self.dreiecke,
                                  start=buckel)
        self.assertLess(abs(aus[self.mitte, 2]), 0.25 * buckel[self.mitte, 2])

    def test_greifen_folgt_dem_zug(self):
        aus = G9formpinsel.deltas(self.punkte, self._striche(d=(0.0, 0.03, 0.0)), 'greifen', 0.05, 1.0, self.dreiecke)
        np.testing.assert_allclose(aus[self.mitte], [0.0, 0.03, 0.0], atol=1e-9)

    def test_aufblasen_entlang_der_punktnormalen(self):
        aus = G9formpinsel.deltas(self.punkte, self._striche(n=(1.0, 0.0, 0.0)), 'aufblasen', 0.05, 1.0,
                                  self.dreiecke)
        # Die Normale der Ebene ist +z — die Strichnormale (x) zählt beim Aufblasen nicht.
        self.assertAlmostEqual(aus[self.mitte, 2], G9formpinsel.SCHRITT_M, places=9)
        self.assertAlmostEqual(aus[self.mitte, 0], 0.0, places=9)

    def test_striche_lesen_verwirft_unsinn(self):
        p, _n, _d = G9formpinsel.striche_lesen([{'p': [0, 0, 0], 'n': [0, 0, 2]}, {'p': [float('nan'), 0, 0]},
                                                {'q': 1}, {'p': [1, 2]}])
        self.assertEqual(len(p), 1)
        with self.assertRaises(ValueError):
            G9formpinsel.striche_lesen([{'p': 'x'}])

    def test_uebertragen_verankert_am_koerper(self):
        grund = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 0.0]])
        runde = grund + np.array([0.0, 0.1, 0.02])
        aus = G9formpinsel.uebertragen(np.array([[0.0, 1.13, 0.05]]), runde, grund)
        np.testing.assert_allclose(aus[0], [0.0, 1.03, 0.03], atol=1e-12)
        np.testing.assert_allclose(G9formpinsel.uebertragen(np.array([[1.0, 2.0, 3.0]]), None, grund)[0], [1, 2, 3])

    def test_unbekannter_modus(self):
        with self.assertRaises(ValueError):
            G9formpinsel.deltas(self.punkte, self._striche(), 'kneten', 0.05, 1.0, self.dreiecke)


class KopfhautTest(TestCase):
    def test_kappe_vor_koerper_mit_uv_je_ecke(self):
        kappe = SimpleNamespace(ART=None, kennung='Kappe', uv=np.array([[0, 0], [1, 0], [1, 1], [0, 1], [1, 1]]),
                                ursprung=np.array([0, 1, 2, 3, 2]), dreiecke=np.array([[0, 1, 4, 3]]))
        strang = SimpleNamespace(ART='strang', kennung='geometry')
        punkte = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=np.float64)
        haut = G9kopfhaut.aus_teilen([(strang, None), (kappe, None)], [np.zeros((2, 3)), punkte], 0.0)
        self.assertEqual(haut['quelle'], 'kappe:Kappe')
        self.assertEqual(haut['uv'].shape, (2, 3, 2))
        self.assertAlmostEqual(haut['flaeche_m2'], 1.0)
        np.testing.assert_array_equal(haut['dreiecke'][0], [0, 1, 2])


class HaarknotendichteTest(TestCase):
    def _auftrag(self, knoten, werte=None):
        a = Haarknotenauftrag(Path('.'), 'sorte', knoten, werte or {})
        a.kopfhaut = {'quelle': 'kappe:x', 'flaeche_m2': 0.05, 'dreiecke': 10}
        return a

    def test_dichte_aus_straehnen_und_flaeche(self):
        punkte = np.column_stack([np.zeros(40), np.linspace(0, 0.39, 40), np.zeros(40)])
        ketten = [np.arange(i * 10, i * 10 + 10) for i in range(4)]
        w = self._auftrag('interpolate')._werte(punkte, ketten)
        self.assertAlmostEqual(w['Density'], Haarknotenauftrag.DICHTE_ANTEIL * 4 / 0.05, places=1)
        g = self._auftrag('generate')._werte(punkte, ketten)
        self.assertAlmostEqual(g['Hair Length'], 0.09, places=4)
        self.assertEqual(self._auftrag('interpolate', {'Density': 7})._werte(punkte, ketten)['Density'], 7)
        self.assertNotIn('Density', self._auftrag('attach')._werte(punkte, ketten))


class MitsubamaterialTest(TestCase):
    def test_srgb_hin_und_zurueck(self):
        werte = np.linspace(0, 1, 11)
        np.testing.assert_allclose(Mitsubamaterial.srgb(Mitsubamaterial.linear(werte)), werte, atol=1e-9)

    def test_nahtkopien_bekommen_dieselbe_normale(self):
        # Zwei Dreiecke, die Kante (1, 2) als Nahtkopie (Punkte 3, 4 an derselben Lage).
        punkte = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0.5]], dtype=np.float64)
        n = Mitsubamaterial.normalen(punkte, np.array([[0, 1, 2], [3, 5, 4]]))
        np.testing.assert_allclose(n[1], n[3], atol=1e-6)
        np.testing.assert_allclose(n[2], n[4], atol=1e-6)

    def test_haarabsorption_dunkler_ist_staerker(self):
        hell, dunkel = Mitsubamaterial.haar_sigma((0.8, 0.7, 0.6)), Mitsubamaterial.haar_sigma((0.1, 0.08, 0.06))
        self.assertTrue((dunkel > hell).all())


class RenderschluesselTest(TestCase):
    def test_gleiche_felder_gleiche_szene(self):
        p, d = np.zeros((3, 3)), np.array([[0, 1, 2]])
        a = Genesishaarrender._schluessel([(p, d, (0.5, 0.5, 0.5), None)], False)
        self.assertEqual(a, Genesishaarrender._schluessel([(p, d, (0.5, 0.5, 0.5), None)], False))
        self.assertNotEqual(a, Genesishaarrender._schluessel([(p, d, (0.6, 0.5, 0.5), None)], False))
        self.assertNotEqual(a, Genesishaarrender._schluessel([(p, d, (0.5, 0.5, 0.5), None)], True))

    def test_extra_paket(self):
        self.assertIsNone(Genesishaarrender.extra({'uv': None, 'textur': []}))
        self.assertEqual(set(Genesishaarrender.extra({'uv': np.zeros((1, 2)), 'textur': [{'ab': 0}]})), {'uv', 'gruppen'})
        self.assertEqual(set(Genesishaarrender.extra({'kurven': {}})), {'kurven'})
