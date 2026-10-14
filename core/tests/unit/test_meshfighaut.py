# -*- coding: utf-8 -*-
"""Hautgewichte der Netz-Objekte (13.10.2026): `Hautdatei`, `Kleidunghautgewichte`, `Kleidungsobjekt.schreiben(haut=…)`.

Anlass (Edgar, Zauberer in Mesh-3D): „Warum animieren die Kleider nicht?" — Kleidung, Haar und Bestandteile waren starre GLB in der Gruppe der Figur. Jetzt liegt neben jeder GLB eine Hautdatei (Knochen und Gewicht
je GLB-Punkt), die die Bühne an das Skelett bindet (`static/viewer/meshfigur/meshfighaut.js`).

Fälle: (1) Quantisierung auf Summe 255, (2) Schreiben und Lesen sind Umkehrungen, (3) ein Punkt erbt die Gewichte seiner Käfig-Nachbarn und sieht mit Körperteilen nur die des eigenen und der angrenzenden Teile,
(4) `Kleidungsobjekt.schreiben` legt die Beidatei mit einer Zeile je GLB-Punkt an — auch wenn ein Punkt wegen zweier UV doppelt in der GLB steht.
Sabotage-Gegenprobe: in `quantisieren` den Rest nicht verteilen → Fall 1 rot; in `Kleidunghautgewichte._block` `nummern` ignorieren (`i = nummern[i]` streichen) → Fall 3b rot; in `Kleidungsobjekt.schreiben`
`[ursprung]` weglassen → Fall 4 rot (Längen passen nicht).

Ohne Datenbank. Geschrieben am 13.10.2026, nicht gelaufen — läuft nur auf Ansage.
"""

import tempfile
import unittest
from pathlib import Path

import numpy as np

from Kleidung.hautdatei import Hautdatei
from Kleidung.kleidunghautgewichte import Kleidunghautgewichte
from Kleidung.kleidungsentposen import Kleidungsentposen
from Kleidung.kleidungsobjekt import Kleidungsobjekt


class HautdateiTest(unittest.TestCase):

    def test_1_quantisieren_summiert_auf_255(self):
        rng = np.random.default_rng(5)
        g = rng.random((500, 4))
        g[7] = 0.0                                                   # ein Punkt ohne Gewicht bleibt leer
        q = Hautdatei.quantisieren(g)
        summen = q.sum(axis=1)
        self.assertTrue(np.all(np.delete(summen, 7) == 255))
        self.assertEqual(int(summen[7]), 0)
        self.assertEqual(q.dtype, np.uint8)

    def test_2_schreiben_und_lesen_sind_umkehrungen(self):
        index = np.array([[3, 1, 0, 0], [137, 5, 6, 7], [2, 2, 2, 2]], dtype=np.int64)
        gewicht = np.array([[0.7, 0.3, 0, 0], [0.25, 0.25, 0.25, 0.25], [1.0, 0, 0, 0]])
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as ordner:
            glb = Path(ordner) / 'x.glb'
            brief = Hautdatei.schreiben(glb, index, gewicht, ['k%d' % i for i in range(138)])
            gelesen_index, gelesen_gewicht = Hautdatei.lesen(Hautdatei.pfad(glb))
        self.assertEqual(brief['punkte'], 3)
        self.assertEqual(brief['datei'], 'x.haut')
        self.assertEqual(len(brief['knochen']), 138)
        np.testing.assert_array_equal(gelesen_index, index.astype(np.uint8))
        np.testing.assert_array_equal(gelesen_gewicht, Hautdatei.quantisieren(gewicht))


class KaefigGewichteTest(unittest.TestCase):
    """Zwei Käfigwolken A (links, Knochen 0) und B (rechts, Knochen 1); Punkte dazwischen erben nach Nähe."""

    @staticmethod
    def _kaefig():
        a = np.c_[np.linspace(-0.30, -0.10, 40), np.zeros(40), np.zeros(40)]
        b = np.c_[np.linspace(0.10, 0.30, 40), np.zeros(40), np.zeros(40)]
        punkte = np.r_[a, b]
        index = np.zeros((80, 4), dtype=np.int64)
        index[40:, 0] = 1
        gewicht = np.zeros((80, 4))
        gewicht[:, 0] = 1.0
        teil = np.r_[np.zeros(40), np.ones(40)].astype(np.int64)
        return punkte, index, gewicht, teil

    def test_3a_ein_punkt_erbt_die_gewichte_der_naechsten_nachbarn(self):
        punkte, index, gewicht, _ = self._kaefig()
        e = Kleidungsentposen(punkte, punkte)
        h = Kleidunghautgewichte(e)
        i, g = h.berechnen(np.array([[-0.20, 0.01, 0.0], [0.20, 0.01, 0.0]]), index, gewicht, 2)
        self.assertEqual(int(i[0, 0]), 0)
        self.assertEqual(int(i[1, 0]), 1)
        self.assertGreater(float(g[0, 0]), 0.99)
        self.assertGreater(float(g[1, 0]), 0.99)
        np.testing.assert_allclose(g.sum(axis=1), 1.0)

    def test_3b_mit_teilen_zaehlt_nur_das_eigene_teil(self):
        punkte, index, gewicht, teil = self._kaefig()
        e = Kleidungsentposen(punkte, punkte, teil, {0: {0}, 1: {1}})            # keine Nachbarschaft zwischen A und B
        h = Kleidunghautgewichte(e)
        p = np.array([[0.05, 0.0, 0.0]])                                          # liegt näher an B (0,10) als an A (−0,10)
        i_a, _ = h.berechnen(p, index, gewicht, 2, teile=np.array([0]))           # aber das Teil ist A
        i_b, _ = h.berechnen(p, index, gewicht, 2, teile=np.array([1]))
        self.assertEqual(int(i_a[0, 0]), 0)
        self.assertEqual(int(i_b[0, 0]), 1)

    def test_3c_die_vier_staerksten_knochen_sortiert(self):
        punkte, index, gewicht, _ = self._kaefig()
        index = index.copy()
        gewicht = gewicht.copy()
        index[:, 1] = 2
        gewicht[:, 0], gewicht[:, 1] = 0.6, 0.4                                   # jeder Käfigpunkt: 60 % eigener Knochen, 40 % Knochen 2
        e = Kleidungsentposen(punkte, punkte)
        i, g = Kleidunghautgewichte(e).berechnen(np.array([[-0.2, 0.0, 0.0]]), index, gewicht, 3)
        self.assertEqual(int(i[0, 0]), 0)
        self.assertEqual(int(i[0, 1]), 2)
        self.assertAlmostEqual(float(g[0, 0]), 0.6, places=3)
        self.assertAlmostEqual(float(g[0, 1]), 0.4, places=3)


class ObjektTest(unittest.TestCase):

    def test_4_die_beidatei_hat_eine_zeile_je_glb_punkt(self):
        import trimesh

        punkte = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=np.float64)
        flaechen = np.array([[0, 1, 2], [0, 2, 3]])
        # Punkt 0 und 2 stehen in beiden Dreiecken mit verschiedenen UV (Naht) → zwei GLB-Punkte je Punkt
        uv_ecken = np.array([[0, 0], [1, 0], [1, 1], [0.5, 0.5], [1, 0.9], [0, 1]], dtype=np.float64)
        index = np.array([[0, 0, 0, 0], [1, 0, 0, 0], [2, 0, 0, 0], [3, 0, 0, 0]], dtype=np.int64)
        gewicht = np.zeros((4, 4))
        gewicht[:, 0] = 1.0
        textur = np.full((8, 8, 3), 200, dtype=np.uint8)
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as ordner:
            glb = Path(ordner) / 'objekt.glb'
            brief = Kleidungsobjekt.schreiben(glb, punkte, flaechen, uv_ecken, textur,
                                              haut={'index': index, 'gewicht': gewicht, 'knochen': ['a', 'b', 'c', 'd']})
            self.assertEqual(brief['haut']['punkte'], brief['punkte'])
            self.assertGreater(brief['punkte'], 4)                                 # die Naht verdoppelt Punkte
            gelesen_index, _ = Hautdatei.lesen(Hautdatei.pfad(glb))
            szene = trimesh.load(str(glb), force='scene')
            netz = list(szene.geometry.values())[0]
        self.assertEqual(len(gelesen_index), len(netz.vertices))
        # Jeder GLB-Punkt trägt den Knochen seines Ausgangspunkts (Knochennummer = Punktnummer).
        for knochen, lage in zip(gelesen_index[:, 0], netz.vertices):
            ausgang = int(np.argmin(np.linalg.norm(punkte - lage, axis=1)))
            self.assertEqual(int(knochen), ausgang)


if __name__ == '__main__':
    unittest.main()
