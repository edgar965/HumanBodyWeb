# -*- coding: utf-8 -*-
"""Scham-Stück ohne gesägte Zipfel (Edgar, 09.10.2026: „Scham-Stück: keine helle, gesägte Zipfel an den Rändern!!"):
`Blendimportschamschnitt` schneidet ein Dreiecksnetz exakt an einer Kontur ab — ohne Django, Genesis und trimesh.

Gesehen im Chrome („cute girl", Stück allein): Der Rand folgte den GANZEN Dreiecken des Originals (4–8 mm) und lief in Spitzen aus;
die weiche Deckkraft am Rand (`stueckrand.js`) folgt dem Netzrand und versteckt Zacken dieser Größe nicht.

Kunstwelt: Quadrat [0, 1]² bei z = 0 in 3 × 3 Zellen (je zwei Dreiecke, Drehrichtung +z), UV je Ecke = (x, y), Schnittwert x − 0,3.

1. Die Fläche innen ist genau 0,3 (ein linear gerechneter Schnitt an einer Geraden ist exakt) und kein Punkt liegt rechts davon.
2. Die neuen Punkte liegen auf x = 0,3, und jeder steht nur EINMAL da (Kante zwischen zwei Dreiecken → ein Punkt): das Netz bleibt dicht —
   die offenen Kanten des Ergebnisses sind nur der Außenrand des Quadrats und der Schnitt.
3. Die Drehrichtung bleibt (alle Dreiecke zeigen nach +z), auch bei Dreiecken mit einer und mit zwei Ecken innen.
4. UV je Ecke bleibt die Lage: (x, y) jeder Ecke des Ergebnisses = UV dort — die neuen Ecken sind in der UV genauso geschnitten.
5. Alles innen → unverändert; alles außen → leer, ohne Fehler.

Sabotage-Gegenprobe: den Schlüssel `lage` je Dreieck statt je Kante (`schluessel = (k, a, b)`) macht Fall 2 rot; in Fall `zahl == 2` die
Dreiecke `[a, b, cb]`/`[a, cb, ca]` zu `[b, a, cb]`/`[cb, a, ca]` macht Fall 3 rot; `uv_punkt` mit `t = 0.5` macht Fall 4 rot;
`werte[dreiecke] < 0.0` → `<= 1e9` macht Fall 5 rot (alles innen, auch das Außen).
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportschamschnitt import Blendimportschamschnitt


class SchamschnittTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _quadrat(zellen=3):
        n = zellen + 1
        punkte = np.array([[x / zellen, y / zellen, 0.0] for y in range(n) for x in range(n)])
        dreiecke = []
        for y in range(zellen):
            for x in range(zellen):
                a = y * n + x
                dreiecke += [[a, a + 1, a + n], [a + 1, a + n + 1, a + n]]
        dreiecke = np.array(dreiecke)
        uv = punkte[dreiecke][:, :, :2]
        return punkte, dreiecke, uv

    @staticmethod
    def _flaeche(punkte, dreiecke):
        a, b, c = (punkte[dreiecke[:, i]] for i in range(3))
        return np.cross(b - a, c - a)[:, 2] / 2.0

    def test_1_die_flaeche_innen_ist_exakt_und_nichts_liegt_rechts(self):
        punkte, dreiecke, uv = self._quadrat()
        p, d, _ = Blendimportschamschnitt.schneiden(punkte, dreiecke, uv, punkte[:, 0] - 0.3)
        self.assertAlmostEqual(float(self._flaeche(p, d).sum()), 0.3, places=12)
        self.assertLessEqual(float(p[np.unique(d)][:, 0].max()), 0.3 + 1e-12)

    def test_2_jeder_neue_punkt_steht_einmal_da_das_netz_bleibt_dicht(self):
        punkte, dreiecke, uv = self._quadrat()
        p, d, _ = Blendimportschamschnitt.schneiden(punkte, dreiecke, uv, punkte[:, 0] - 0.3)
        neu = p[len(punkte):]
        self.assertGreater(len(neu), 0)
        self.assertTrue(np.allclose(neu[:, 0], 0.3))
        self.assertEqual(len(np.unique(np.round(neu, 9), axis=0)), len(neu), 'ein Schnittpunkt doppelt')
        kanten = np.sort(np.concatenate([d[:, [0, 1]], d[:, [1, 2]], d[:, [2, 0]]]), axis=1)
        roh, zaehl = np.unique(kanten, axis=0, return_counts=True)
        offen = roh[zaehl == 1]
        for a, b in offen:
            ort = (p[a] + p[b]) / 2.0
            am_rand = (min(ort[0], ort[1], 1 - ort[1]) < 1e-9) or abs(ort[0] - 0.3) < 1e-9
            self.assertTrue(am_rand, 'offene Kante mitten in der Fläche: %s' % ort)

    def test_3_die_drehrichtung_bleibt(self):
        punkte, dreiecke, uv = self._quadrat()
        p, d, _ = Blendimportschamschnitt.schneiden(punkte, dreiecke, uv, punkte[:, 0] - 0.3)
        flaechen = self._flaeche(p, d)
        self.assertTrue((flaechen > 0).all(), 'umgedrehte oder entartete Dreiecke: %s' % flaechen[flaechen <= 0])
        # Sowohl Dreiecke mit einer als auch mit zwei Ecken innen kommen vor (Schnitt x = 0,3 quer zur Diagonale).
        innen = (punkte[dreiecke][:, :, 0] < 0.3).sum(axis=1)
        self.assertTrue({1, 2} <= set(innen.tolist()))

    def test_4_uv_je_ecke_ist_die_lage(self):
        punkte, dreiecke, uv = self._quadrat()
        p, d, u = Blendimportschamschnitt.schneiden(punkte, dreiecke, uv, punkte[:, 0] - 0.3)
        self.assertTrue(np.allclose(u, p[d][:, :, :2]), 'UV der neuen Ecken weicht von ihrer Lage ab')

    def test_5_alles_innen_bleibt_alles_aussen_ist_leer(self):
        punkte, dreiecke, uv = self._quadrat()
        p, d, u = Blendimportschamschnitt.schneiden(punkte, dreiecke, uv, np.full(len(punkte), -1.0))
        self.assertEqual(len(d), len(dreiecke))
        self.assertEqual(len(p), len(punkte))
        p, d, u = Blendimportschamschnitt.schneiden(punkte, dreiecke, uv, np.full(len(punkte), 1.0))
        self.assertEqual(len(d), 0)
        self.assertEqual(u.shape, (0, 3, 2))
