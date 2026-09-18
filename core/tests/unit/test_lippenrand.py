# -*- coding: utf-8 -*-
"""`Lippenrand`: der Lippenrand als Kantenschleife eines Kunstmundes.

Der Kunstmund: konzentrische Ellipsenringe um eine Öffnung (24 Ecken je
Ring), Tiefe je Ring — ein Innenring hinter der Öffnung (Mundhöhle), der
Saum, drei Lippenringe, die nach vorn wölben, dann knickt die Fläche am
Ring 3 zurück (der Lippenrand), und drei Hautringe. Die Lipmap deckt die
Lippen (255), läuft am Ring 4 aus (40) und ist dahinter leer.

1. `vorn`: Lippenringe vorn, der Innenring nicht.
2. Die Mundöffnung ist genau der Saumring (Ring 0), die Schleifen zählen
   von dort nach außen.
3. Randschleife = Ring 3 auf beiden Seiten (größter Knickabfall, wo die
   Lipmap noch malt — Ring 5 und 6 knicken nicht, Ring 1 zählt nicht).
4. Das Feld: Ring 3 = 0, innen positiv (Ring 2 ≈ 2 mm), außen negativ,
   der Innenring als Mundhöhle INNEN, der letzte Hautring weit außen.
5. Durch den Unterteiler: das Feld geht als Spalte durch `subdivide`.

Sabotage-Gegenprobe: `range(2, …)` in `randschleifen` auf `range(1, …)` →
Fall 3 rot (Ring 1 mit dem Knick der Mundlinie gewänne).
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.lippenrand import Lippenrand


class Kunstmund:
    """Ringe um eine Öffnung: (Ring, Ecke) → Punkt; Vierecke zwischen Ringen."""

    ECKEN = 24
    #: Ring → (halbe Breite mm, halbe Höhe mm, Tiefe mm nach hinten, Lipmap)
    RINGE = {
        -1: (11.5, 2.0, 6.0, 255),
        0: (10.0, 1.0, 0.0, 255),
        1: (12.5, 3.0, -1.0, 255),
        2: (15.0, 5.0, -1.6, 255),
        3: (17.5, 7.0, -1.8, 255),
        4: (20.0, 9.0, -0.6, 40),
        5: (22.5, 11.0, 0.0, 2),
        6: (25.0, 13.0, 0.3, 0),
    }
    HOEHE = 1.5

    @classmethod
    def bauen(cls):
        ringe = sorted(cls.RINGE)
        punkte, maske, nummer = [], [], {}
        winkel = np.linspace(0, 2 * np.pi, cls.ECKEN, endpoint=False)
        for r in ringe:
            a, b, tiefe, wert = cls.RINGE[r]
            for j, w in enumerate(winkel):
                nummer[(r, j)] = len(punkte)
                punkte.append([a * np.cos(w) / 1000, tiefe / 1000, cls.HOEHE + b * np.sin(w) / 1000])
                maske.append(wert)
        quads = []
        for r0, r1 in zip(ringe, ringe[1:]):
            for j in range(cls.ECKEN):
                k = (j + 1) % cls.ECKEN
                quads.append([nummer[(r0, j)], nummer[(r1, j)], nummer[(r1, k)], nummer[(r0, k)]])
        return np.array(punkte), np.array(quads), np.array(maske), nummer


class LippenrandTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.punkte, cls.quads, cls.maske, cls.nummer = Kunstmund.bauen()
        cls.feld = Lippenrand.feld(cls.punkte, cls.quads, cls.maske)

    def ring(self, r):
        return np.array([self.nummer[(r, j)] for j in range(Kunstmund.ECKEN)])

    def test_vorn_sind_die_lippen_nicht_die_innenseite(self):
        normalen = Lippenrand.flaechennormalen(self.punkte, self.quads)
        vorn = Lippenrand.vorn(len(self.punkte), self.quads, normalen)
        self.assertTrue(vorn[self.ring(1)].all())
        self.assertTrue(vorn[self.ring(3)].all())
        self.assertFalse(vorn[self.ring(-1)].any())

    def test_mundoeffnung_ist_der_saumring(self):
        normalen = Lippenrand.flaechennormalen(self.punkte, self.quads)
        kanten = Lippenrand.kanten(self.quads)
        vorn = Lippenrand.vorn(len(self.punkte), self.quads, normalen)
        nachbarn = Lippenrand.nachbarn(len(self.punkte), kanten)
        mund = Lippenrand.mundoeffnung(nachbarn, vorn, self.maske >= Lippenrand.UMRISS)
        self.assertEqual(sorted(mund), sorted(self.ring(0).tolist()))
        stufe = Lippenrand.ringe(nachbarn, mund, vorn)
        for r in range(0, 7):
            self.assertTrue((stufe[self.ring(r)] == r).all(), 'Ring %d' % r)
        self.assertTrue((stufe[self.ring(-1)] == -1).all())

    def test_randschleife_ist_ring_drei_auf_beiden_seiten(self):
        normalen = Lippenrand.flaechennormalen(self.punkte, self.quads)
        kanten = Lippenrand.kanten(self.quads)
        knick = Lippenrand.knick(kanten, normalen)
        vorn = Lippenrand.vorn(len(self.punkte), self.quads, normalen)
        nachbarn = Lippenrand.nachbarn(len(self.punkte), kanten)
        mund = Lippenrand.mundoeffnung(nachbarn, vorn, self.maske >= Lippenrand.UMRISS)
        stufe = Lippenrand.ringe(nachbarn, mund, vorn)
        schleifen = Lippenrand.schleifen(kanten, stufe)
        self.assertEqual(
            Lippenrand.randschleifen(schleifen, self.punkte, knick, self.maske, Kunstmund.HOEHE), (3, 3)
        )

    def test_feld_null_am_rand_innen_positiv_aussen_negativ(self):
        feld = self.feld
        self.assertIsNotNone(feld)
        self.assertTrue((feld[self.ring(3)] == 0).all())
        self.assertTrue((feld[self.ring(1)] > 0).all())
        self.assertTrue((feld[self.ring(2)] > 0).all())
        self.assertTrue((feld[self.ring(4)] < 0).all())
        self.assertTrue((feld[self.ring(5)] < 0).all())
        # Ring 2 liegt 2,5 mm (breit) bis 2 mm (hoch) vor dem Rand — gemessen
        # zum Streckenzug der Randschleife, der innerhalb der Ellipse liegt.
        self.assertAlmostEqual(feld[self.nummer[(2, 0)]], 2.4, delta=0.3)
        self.assertAlmostEqual(feld[self.nummer[(2, 6)]], 1.9, delta=0.3)
        self.assertTrue((feld[self.ring(-1)] == Lippenrand.INNEN).all(), 'Mundhöhle innen')
        self.assertTrue((feld[self.ring(6)] <= -6).all())

    def test_durch_den_unterteiler_als_spalte(self):
        class Attrappe:
            def subdivide(self, basis):
                return np.repeat(np.asarray(basis, dtype=float), 2, axis=0)

        Lippenrand._basis['kunst'] = self.feld
        try:
            fein = Lippenrand.abstand('kunst', Attrappe())
        finally:
            Lippenrand._basis.pop('kunst', None)
        self.assertEqual(len(fein), 2 * len(self.feld))
        self.assertEqual(fein[2 * self.nummer[(3, 0)]], 0.0)
        self.assertEqual(fein[2 * self.nummer[(1, 0)] + 1], self.feld[self.nummer[(1, 0)]])
