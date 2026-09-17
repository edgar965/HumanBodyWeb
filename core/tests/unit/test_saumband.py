# -*- coding: utf-8 -*-
u"""`saumband.py` — der Film hält hinter der Maskengrenze dasselbe Band
versenkter Haut wie der Browser (`test_js_saumband.py`, gleiche Zahlen).

Ein Streifen aus Dreiecken, gezeichnet bei x=0, verdeckt bei 2, 5, 9, 15,
45 und 400 mm: Wege 2/5/9/15/45, der ferne `inf`; Versenkung 3/6/10/10 mm;
`weg` nur die fernen. Dazu `Filmmasken` am Kunstkörper (Rohr von 0,30 bis
0,70 auf einem Zylinder mit Ringen alle 20 mm): Der Index behält die
Dreiecke bis `BAND_M` (15 cm) hinter der Rohrkante — die Mitte bei 0,50
liegt 22 cm von beiden Kanten und fällt weg, 0,42 bleibt — und versenkt
die Punkte im Band bis 10 mm.

Dazu `Geometrie.normalen`: deckungsgleiche Punkte (Naht) teilen sich eine
Normale, wie `hautmaskegeometrie.js` (Spalt über dem Bund an der Rückenmitte).

Sabotage-Gegenproben: in `abstaende` das `limit` weglassen → der ferne
Punkt bekommt 400 mm statt `inf`, `weg` leer → rot; `_naehte_vereinen`
nicht aufrufen → Nahttest rot.
"""
import numpy as np
from django.test import SimpleTestCase

from ._kunstkoerper import Kunstkoerper
from ._modelphysik import Modelphysik


class _Haut:
    def __init__(self, punkte):
        self.punkte = np.asarray(punkte, dtype=np.float64)
        self.folge = np.array([self.punkte, self.punkte + np.array([0.0, 0.001, 0.0])])


class SaumbandTest(SimpleTestCase):

    databases = set()

    def setUp(self):
        self.S = SaumbandTest._modul('saumband').Saumband

    def test_weg_tiefe_und_index(self):
        u"""Derselbe Streifen wie in `test_js_saumband`: Wege 2/5/9/15 mm,
        fern `inf`; Punkt 14 liegt im Raum 2 mm neben der Quelle, auf der
        Haut aber über 40 mm; Punkt 15 ist ein Zwilling von Punkt 1 (Naht)."""
        xs = [0, 0.002, 0.005, 0.009, 0.015, 0.045, 0.4]
        P = np.zeros((16, 3))
        P[:7, 0] = xs
        P[7:14, 0] = xs
        P[7:14, 1] = 0.01
        P[14] = [0.002, -0.04, 0]
        P[15] = [0.002, 0, 0]
        T = [[i, i + 1, i + 7] for i in range(6)] + [[i + 1, i + 8, i + 7] for i in range(6)]
        T.append([5, 12, 14])
        maske = np.ones(16, bool)
        maske[[0, 7]] = False
        d = self.S.abstaende(P, maske, T)
        self.assertTrue(np.allclose(d[:5], [0, 0.002, 0.005, 0.009, 0.015]), d)
        self.assertTrue(np.isinf(d[6]))
        self.assertGreater(d[14], 0.04)
        self.assertAlmostEqual(d[15], 0.002, places=6)
        self.assertTrue(np.allclose(self.S.tiefe(d)[1:5], [0.003, 0.006, 0.010, 0.010]))
        self.assertEqual(list(np.flatnonzero(self.S.weg(maske, d))), [6, 13])
        self.assertEqual(list(self.S.abstaende(P, np.zeros(16, bool), T)), [0.0] * 16)
        self.assertTrue(np.all(np.isinf(self.S.abstaende(P, np.ones(16, bool), T))))

    def test_film_behaelt_das_band_hinter_der_rohrkante(self):
        fm = SaumbandTest._modul('filmmasken')
        kp, kt = Kunstkoerper.zylinder(0.10, 0.0, 1.0, 51, 36)
        sp, st = Kunstkoerper.zylinder(0.102, 0.30, 0.70, 41, 36)
        koerper = {'name': u'Koerper', 'haut': _Haut(kp), 'dreiecke': kt}
        rohr = {'name': u'rohr', 'haut': _Haut(sp), 'dreiecke': st}
        fm.Filmmasken.anwenden([koerper, rohr])
        maske = koerper['maske']
        y_ruhe = kp[:, 1]
        # Verdeckt ab der Rohrkante — im Band (bis 15 cm auf der Haut hinter
        # der gezeichneten bei y<0,30 bzw. y>=0,70) liegt alles bis 0,42 und
        # ab 0,56; die Mitte (0,44–0,54) fällt weg.
        band = maske & (koerper['abstand_haut'] <= self.S.BAND_M)
        yb = y_ruhe[band]
        self.assertTrue(np.all((yb < 0.43) | (yb > 0.55)), sorted(set(np.round(yb, 2))))
        self.assertTrue(np.any(np.isclose(yb, 0.30)) and np.any(np.isclose(yb, 0.42)))
        T = np.asarray(koerper['dreiecke_sichtbar'])
        ymax = y_ruhe[T].max(axis=1)
        ymin = y_ruhe[T].min(axis=1)
        self.assertTrue(np.any(np.isclose(ymin, 0.30) & np.isclose(ymax, 0.32)), u'Bandring fehlt')
        self.assertTrue(np.any(np.isclose(ymin, 0.40) & np.isclose(ymax, 0.42)), u'Bandende fehlt')
        self.assertFalse(np.any((ymin > 0.43) & (ymax < 0.55)), u'Dreieck jenseits des Bands')
        punkte, _dreiecke, _normalen = fm.Filmmasken.gerendert(koerper, 0)
        r = np.linalg.norm(punkte[:, [0, 2]], axis=1)
        innen = band & (y_ruhe > 0.33) & (y_ruhe < 0.67)
        self.assertTrue(np.allclose(r[innen], 0.10 - 0.010, atol=1e-6))

    def test_naht_teilt_sich_eine_normale(self):
        G = SaumbandTest._modul('maskengeometrie').Geometrie
        naht = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 0, 0], [1, 1, 0.5], [0, 1, 0]], float)
        N = G.normalen(naht, [[0, 1, 2], [3, 4, 5]])
        self.assertTrue(np.allclose(N[1], N[3]) and np.allclose(N[2], N[5]), N)
        self.assertLess(abs(N[1, 2]), 1 - 1e-6, u'Zwilling sieht nur seinen halben Fächer')
        # Mit vorgerechneter Naht (der Film je Bild) dasselbe Ergebnis.
        self.assertTrue(np.allclose(G.normalen(naht, [[0, 1, 2], [3, 4, 5]], G.naht(naht)), N))
        gruppe = G.naht(naht)
        self.assertTrue(gruppe[1] == gruppe[3] and gruppe[2] == gruppe[5], gruppe)
        self.assertEqual(len(set(gruppe.tolist())), 4)

    @staticmethod
    def _modul(name):
        return Modelphysik.modul(name)
