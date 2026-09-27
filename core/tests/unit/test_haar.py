"""Paket `Haar` (Schritt „haar" von „Mesh to 3D", 27.09.2026) — Maske und Teilung an einem Kunstkopf.

Edgar: „mach dir eine Methode, mit der du das Haar extrahierst aus dem Mesh, und zeige es in dem Jobverlauf,
wie das Mesh ohne Haar ausschaut". Ohne Kopfnetz und ohne GPU: eine ebene Gitterfläche als Gesicht (Blick +Z),
Farben je Fläche, Kunstlandmarken. Die Bilder (`Haarbild`, pyrender) prüft kein Test — sie rechnen nur im
Arbeitsprozess.
"""

import unittest

import numpy as np
from Genesis9.gesichtsrahmen import G9gesichtsrahmen
from Haar.haarmaske import Haarmaske
from Haar.haarobjekt import Haarobjekt
from Haar.haarteilung import Haarteilung

HAUT = (200, 150, 120)
HAAR = (50, 35, 25)


def landmarken():
    """(478, 3): Augen auf y = 1,6 m, Kinn 1,49, Stirn 1,66; Konturen um Augen, Brauen, Nase, Mund."""
    g = np.full((478, 3), np.nan)
    g[33], g[263] = (-0.045, 1.6, 0.0), (0.045, 1.6, 0.0)
    g[133], g[362] = (-0.015, 1.6, 0.0), (0.015, 1.6, 0.0)
    g[10], g[152] = (0.0, 1.66, 0.0), (0.0, 1.49, 0.0)
    g[1] = (0.0, 1.56, 0.01)  # Nasenspitze knapp vor der Ebene: der Hautton sucht im Umkreis von 3 cm
    lagen = {'auge_rechts': (-0.03, 1.6), 'auge_links': (0.03, 1.6), 'braue_rechts': (-0.03, 1.62),
             'braue_links': (0.03, 1.62), 'nase': (0.0, 1.56), 'lippen': (0.0, 1.52), 'mund': (0.0, 1.52)}
    for name, (x, y) in lagen.items():
        idx = [i for i in G9gesichtsrahmen.KONTUREN[name] if not np.isfinite(g[i]).all()]
        w = np.linspace(0, 2 * np.pi, max(len(idx), 1), endpoint=False)
        for wi, i in zip(w, idx, strict=True):
            g[i] = (x + 0.012 * np.cos(wi), y + 0.004 * np.sin(wi), 0.0)
    winkel = np.linspace(0, 2 * np.pi, len(G9gesichtsrahmen.OVAL), endpoint=False)
    for w, i in zip(winkel, G9gesichtsrahmen.OVAL, strict=True):
        g[i] = (0.07 * np.sin(w), 1.58 + 0.09 * np.cos(w), -0.01)
    return g


def gitter(n=60):
    """Ebenes Gitter x −0,1…0,1, y 1,45…1,75, z = 0, Dreiecke nach +Z gewandt: (punkte, flaechen, mitten)."""
    xs, ys = np.linspace(-0.1, 0.1, n + 1), np.linspace(1.45, 1.75, n + 1)
    punkte = np.array([(x, y, 0.0) for y in ys for x in xs])
    flaechen = []
    for j in range(n):
        for i in range(n):
            a = j * (n + 1) + i
            flaechen += [(a, a + 1, a + n + 2), (a, a + n + 2, a + n + 1)]
    flaechen = np.array(flaechen)
    return punkte, flaechen, punkte[flaechen].mean(axis=1)


def hauttest(f):
    f = np.asarray(f, dtype=np.float64)
    return f[:, 0] > f[:, 2] + 40


class HaarmaskeTest(unittest.TestCase):
    def setUp(self):
        self.punkte, self.flaechen, self.mitte = gitter()
        farben = np.tile(HAUT, (len(self.flaechen), 1)).astype(np.float64)
        self.oben = self.mitte[:, 1] > 1.69
        farben[self.oben] = HAAR
        # dunkle Augen (geschützt) und ein einzelner dunkler Fleck auf der Wange (Sommersprosse)
        self.auge = np.linalg.norm(self.mitte[:, :2] - (-0.03, 1.6), axis=1) < 0.006
        farben[self.auge] = HAAR
        self.fleck = int(np.argmin(np.linalg.norm(self.mitte[:, :2] - (0.07, 1.53), axis=1)))
        farben[self.fleck] = HAAR
        # ein heller Fleck mitten im Haar (Licht auf Strähnen) — ohne Verbindung zur Gesichtshaut
        self.licht = np.linalg.norm(self.mitte[:, :2] - (0.0, 1.73), axis=1) < 0.008
        farben[self.licht] = HAUT
        self.farben = farben

    def test_haar_oben_gesicht_bleibt(self):
        m = Haarmaske(self.punkte, self.flaechen, self.farben, landmarken(), hauttest).rechnen()
        self.assertGreater(m['haar'][self.oben].mean(), 0.95)
        self.assertFalse(m['haar'][self.auge].any(), 'Augen sind dunkel, aber geschützt')
        self.assertFalse(m['haar'][self.fleck], 'ein einzelner dunkler Fleck wird weggeglättet')
        self.assertTrue(m['haar'][self.licht].all(), 'Haut ohne Verbindung zum Gesicht ist Haar im Licht')

    def test_hautton_um_die_nase(self):
        m = Haarmaske(self.punkte, self.flaechen, self.farben, landmarken(), hauttest)
        ton = m.hautton(m.rahmen.hinein(m.mitte))
        self.assertAlmostEqual(ton, Haarmaske.hell(np.array([HAUT]))[0], places=3)

    def test_nachbarn_symmetrisch_ueber_kanten(self):
        m = Haarmaske(self.punkte, self.flaechen, self.farben, landmarken(), hauttest)
        a = m.nachbarn()
        self.assertEqual((a - a.T).nnz, 0)
        self.assertLessEqual(int(a.sum(axis=1).max()), 3)  # ein Dreieck hat höchstens drei Kantennachbarn

    def test_unten_unter_der_ebene_nie_haar(self):
        ebene = {'punkt': (0.0, 1.5, 0.0), 'achse': (0.0, 1.0, 0.0)}
        farben = np.tile(HAAR, (len(self.flaechen), 1)).astype(np.float64)
        m = Haarmaske(self.punkte, self.flaechen, farben, landmarken(), hauttest, ebene).rechnen()
        unter = self.mitte[:, 1] < 1.5
        self.assertTrue(m['unten'][unter].all())
        self.assertFalse(m['haar'][unter].any())


class HaarteilungTest(unittest.TestCase):
    def test_teilnetze_und_kennzahlen(self):
        punkte, flaechen, mitte = gitter(20)
        haar = mitte[:, 1] > 1.69
        maske = {'haar': haar, 'unten': np.zeros(len(haar), bool), 'ton': 150.0}
        farben = np.where(haar[:, None], HAAR, HAUT).astype(np.float64)
        t = Haarteilung(punkte, flaechen, None, farben, maske, G9gesichtsrahmen(landmarken()))
        p, f, uv = t.nur_haar()
        self.assertEqual(len(f), haar.sum())
        self.assertLess(f.max(), len(p))
        self.assertIsNone(uv)
        k = t.kennzahlen()
        self.assertEqual(k['farbe']['median'], list(HAAR))
        self.assertAlmostEqual(k['anteil_prozent'], 100 * (1.75 - 1.69) / 0.30, delta=1.0)
        self.assertAlmostEqual(k['unter_kinn_mm'], (1.49 - 1.69) * 1000, delta=10)  # Haar endet über dem Kinn


class HaarobjektTest(unittest.TestCase):
    def test_je_punkt_und_uv_ein_punkt(self):
        """Zwei Dreiecke teilen eine Kante; an Punkt 2 treffen verschiedene UVs zusammen (Naht) → 5 Punkte."""
        punkte = np.array([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], dtype=float)
        flaechen = np.array([(0, 1, 2), (0, 2, 3)])
        uv = np.array([[(0, 0), (1, 0), (1, 1)], [(0, 0), (0.5, 0.5), (0, 1)]], dtype=float)
        p, u, f = Haarobjekt.punkte_mit_uv(punkte, flaechen, uv)
        self.assertEqual(len(p), 5)
        np.testing.assert_allclose(p[f], punkte[flaechen])  # dieselben Ecken wie vorher
        np.testing.assert_allclose(u[f], uv)  # und je Ecke ihr eigenes UV
