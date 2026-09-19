# -*- coding: utf-8 -*-
"""Fototextur über das Modell selbst (20.09.2026): Kamera, Gesichtstabelle, Mischung, Kameravorgabe.

Edgar: „das ist doch reinstes Chaos!" — die Projektion lief über das SMPL-X-Netz
des Schätzers, jedes Bild lag anders daneben. Jetzt projiziert das Genesis-Modell
selbst; hier die Bausteine ohne Daz-Bibliothek:

1. `G9bildkamera.aus_browser`: eine three.js-Kamera (Weltmatrix, fov) wird zur
   OpenCV-Kamera — ein Punkt vor der Kamera landet in der Bildmitte, ein Punkt
   rechts davon rechts (x wächst), ein höherer Punkt weiter OBEN (v sinkt);
   der Zuschnitt verschiebt nur den Hauptpunkt; `strahlen` ↔ `projizieren`
   sind Umkehrungen.
2. `G9gesichtslandmarken.bauen`: Strahlen durch 68 Bildpunkte gegen ein Kunstnetz
   (Kugel) — die Positionen liegen auf dem Netz und projizieren auf die
   Bildpunkte zurück; zu wenige Treffer → None.
3. `Texturmischung.gewinne`: zwei Bilder, das zweite auf der Überlappung um den
   Faktor 1,5 heller → die Gewinne heben den Unterschied auf (Verhältnis ≈ 1);
   ohne Überlappung Faktor 1. `mischen`: zwei Bilder mit verschiedenen Farben
   und weichem Gewichtswechsel — kein Texel fällt aus dem Farbbereich, die
   Herkunft folgt dem größeren Gewicht, ungedeckte Texel bleiben leer.
   Sabotage: ohne Normalisierung über die Deckung zöge die Kachelkante Schwarz
   hinein — das Mittel im Innern eines Bilds bleibt hier auf ±2 %.
4. `Bildmodellbildtypen.kamera_pruefen`: nur vollständige Zahlen; die
   Vorgabe `kamera` läuft durch `vorgaben_pruefen`.
"""

import unittest

import numpy as np
from Genesis9.bildkamera import G9bildkamera
from Genesis9.gesichtslandmarken import G9gesichtslandmarken

from core.dienste.bildmodellbildtypen import Bildmodellbildtypen
from core.tests.unit._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from texturmischung import Texturmischung  # noqa: E402


def _browserkamera(z=3.0, y=0.9, fov=30.0, breite=1200, hoehe=1600):
    # three.js: Kamera bei (0, y, z), schaut entlang −z (Einheitsdrehung), Spaltenordnung.
    m = np.eye(4)
    m[:3, 3] = [0.0, y, z]
    return {'matrix': m.ravel(order='F').tolist(), 'fov': fov, 'breite': breite, 'hoehe': hoehe}


class BildkameraTest(unittest.TestCase):
    def test_1_kamera(self):
        k = G9bildkamera.aus_browser(_browserkamera())
        u, v, tiefe = G9bildkamera.projizieren(k, [[0.0, 0.9, 0.0], [0.3, 0.9, 0.0], [0.0, 1.4, 0.0]])
        self.assertAlmostEqual(u[0], 600.0, places=6)
        self.assertAlmostEqual(v[0], 800.0, places=6)
        self.assertAlmostEqual(tiefe[0], 3.0, places=6)
        self.assertGreater(u[1], u[0], 'rechts vom Blick: u wächst')
        self.assertLess(v[2], v[0], 'höher: v sinkt (y nach unten)')
        f = (1600 / 2.0) / np.tan(np.radians(15.0))
        self.assertAlmostEqual(k['fx'], f, places=6)
        self.assertAlmostEqual(u[1] - 600.0, f * 0.3 / 3.0, places=6)
        # Zuschnitt: nur der Hauptpunkt wandert.
        z = G9bildkamera.aus_browser(_browserkamera(), kasten=[100, 50, 700, 1650])
        uz, vz, _ = G9bildkamera.projizieren(z, [[0.0, 0.9, 0.0]])
        self.assertAlmostEqual(uz[0], 500.0, places=6)
        self.assertAlmostEqual(vz[0], 750.0, places=6)
        self.assertEqual((z['breite'], z['hoehe']), (600, 1600))
        # Strahlen sind die Umkehrung der Projektion.
        ursprung, richtungen = G9bildkamera.strahlen(k, [u[1]], [v[1]])
        np.testing.assert_allclose(ursprung, [0.0, 0.9, 3.0], atol=1e-9)
        treffer = ursprung + richtungen[0] * (3.0 / -richtungen[0][2])
        np.testing.assert_allclose(treffer, [0.3, 0.9, 0.0], atol=1e-6)
        self.assertIsNone(G9bildkamera.aus_browser(None))

    def test_2_gesichtstabelle(self):
        import trimesh

        kugel = trimesh.creation.icosphere(subdivisions=3, radius=0.1)
        punkte = np.asarray(kugel.vertices) + np.array([0.0, 0.9, 0.0])
        k = G9bildkamera.aus_browser(_browserkamera(z=1.0))
        rng = np.random.default_rng(5)
        richtung = rng.normal(size=(68, 3))
        richtung[:, 2] = np.abs(richtung[:, 2]) + 0.3                            # der Kamera zugewandt
        richtung /= np.linalg.norm(richtung, axis=1, keepdims=True)
        ziel = np.array([0.0, 0.9, 0.0]) + 0.1 * richtung                        # auf der Kugel
        u, v, _ = G9bildkamera.projizieren(k, ziel)
        g68 = [[float(a / 1200), float(b / 1600), 1.0] for a, b in zip(u, v, strict=True)]
        tabelle = G9gesichtslandmarken.bauen(punkte, kugel.faces, k, g68, quelle='kugel')
        self.assertIsNotNone(tabelle)
        lagen = tabelle.positionen(punkte, kugel.faces)
        da = np.isfinite(lagen).all(1)
        self.assertGreaterEqual(int(da.sum()), 60)
        radius = np.linalg.norm(lagen[da] - [0.0, 0.9, 0.0], axis=1)
        self.assertLess(float(np.abs(radius - 0.1).max()), 0.002, 'auf dem Netz (Ikosaeder-Sehnen)')
        u2, v2, _ = G9bildkamera.projizieren(k, lagen[da])
        self.assertLess(float(np.hypot(u2 - u[da], v2 - v[da]).max()), 0.5,
                        'projiziert auf die Bildpunkte zurück')
        self.assertIsNone(G9gesichtslandmarken.bauen(punkte, kugel.faces, k, g68[:10]))
        weg = [[2.0, 2.0, 1.0]] * 68        # alle Strahlen gehen ins Leere
        self.assertIsNone(G9gesichtslandmarken.bauen(punkte, kugel.faces, k, weg))


class TexturmischungTest(unittest.TestCase):
    S = 128

    def _drin(self):
        drin = np.zeros((self.S, self.S), dtype=bool)
        drin[8:120, 8:120] = True
        return drin

    def test_3_gewinne(self):
        rng = np.random.default_rng(1)
        n = 5000
        idx_a = np.arange(0, n, dtype=np.int32)
        idx_b = np.arange(n // 2, n + n // 2, dtype=np.int32)
        grund = rng.uniform(0.3, 0.6, size=(n + n // 2, 3))
        fa = (grund[idx_a] * 255).astype(np.uint8)
        fb = (np.clip(grund[idx_b] * 1.5, 0, 1) * 255).astype(np.uint8)
        g = Texturmischung.gewinne({0: (idx_a, fa, np.ones(n, np.float32)),
                                    1: (idx_b, fb, np.ones(n, np.float32))})
        verhaeltnis = g[1] / g[0]
        np.testing.assert_allclose(verhaeltnis, 1 / 1.5, rtol=0.06)
        self.assertLess(abs(float(np.log(g[0]).mean() + np.log(g[1]).mean())), 0.15, 'Gesamtton bleibt')
        ohne = Texturmischung.gewinne({0: (idx_a, fa, np.ones(n, np.float32)),
                                       1: (idx_a + 100000, fb, np.ones(n, np.float32))})
        np.testing.assert_allclose(ohne[0], 1.0)
        np.testing.assert_allclose(ohne[1], 1.0)

    def test_4_mischen(self):
        drin = self._drin()
        m = Texturmischung(drin)
        zeilen, spalten = np.nonzero(drin)
        n = len(zeilen)
        # Bild 0 links (rot), Bild 1 rechts (blau), Gewichte wechseln weich um Spalte 64.
        links = spalten < 80
        rechts = spalten > 48
        wa = np.clip((80 - spalten[links]) / 32.0, 0, 1).astype(np.float32) + 1e-3
        wb = np.clip((spalten[rechts] - 48) / 32.0, 0, 1).astype(np.float32) + 1e-3
        fa = np.tile(np.array([[200, 60, 60]], np.uint8), (int(links.sum()), 1))
        fb = np.tile(np.array([[60, 60, 200]], np.uint8), (int(rechts.sum()), 1))
        proben = {0: (np.flatnonzero(links).astype(np.int32), fa, wa),
                  1: (np.flatnonzero(rechts).astype(np.int32), fb, wb)}
        farbe, gewicht, herkunft = m.mischen(proben)
        self.assertEqual(farbe.shape, (n, 3))
        self.assertTrue(((farbe >= 0) & (farbe <= 1)).all())
        self.assertTrue((gewicht > 0).all(), 'jedes Inseltexel ist gedeckt')
        self.assertTrue((herkunft[spalten < 50] == 0).all())
        self.assertTrue((herkunft[spalten > 78] == 1).all())
        innen_links = (spalten < 30) & (zeilen > 20) & (zeilen < 100)
        innen_rechts = (spalten > 100) & (zeilen > 20) & (zeilen < 100)
        np.testing.assert_allclose(farbe[innen_links].mean(0), [200 / 255, 60 / 255, 60 / 255], atol=0.02)
        np.testing.assert_allclose(farbe[innen_rechts].mean(0), [60 / 255, 60 / 255, 200 / 255], atol=0.02)
        # In der Mitte eine Mischung, kein Sprung: Rotanteil fällt monoton von links nach rechts.
        mitte = zeilen == 64
        rot = farbe[mitte][np.argsort(spalten[mitte]), 0]
        self.assertLess(float(np.abs(np.diff(rot)).max()), 0.12, 'weicher Übergang')
        # Kante der Insel: kein Schwarz hineingezogen (Sabotage der Normalisierung würde hier abfallen).
        kante = (spalten == 8) & (zeilen > 20) & (zeilen < 100)
        self.assertGreater(float(farbe[kante, 0].mean()), 0.7)
        # Ungedeckt: leer.
        nichts = (np.zeros(0, np.int32), np.zeros((0, 3), np.uint8), np.zeros(0, np.float32))
        leer, g2, h2 = m.mischen({0: nichts})
        self.assertEqual(int((g2 > 0).sum()), 0)
        self.assertTrue((h2 == -1).all())


class KameravorgabeTest(unittest.TestCase):
    def test_5_kamera_pruefen(self):
        gut = _browserkamera()
        k = Bildmodellbildtypen.kamera_pruefen(gut)
        self.assertEqual((k['breite'], k['hoehe'], k['fov']), (1200, 1600, 30.0))
        self.assertEqual(len(k['matrix']), 16)
        self.assertEqual(k['figur'][0], 1.0)
        self.assertIsNone(Bildmodellbildtypen.kamera_pruefen({**gut, 'matrix': gut['matrix'][:15]}))
        self.assertIsNone(Bildmodellbildtypen.kamera_pruefen({**gut, 'fov': 'breit'}))
        self.assertIsNone(Bildmodellbildtypen.kamera_pruefen({**gut, 'breite': 0}))
        self.assertIsNone(Bildmodellbildtypen.kamera_pruefen('nein'))
        aus = Bildmodellbildtypen.vorgaben_pruefen({'a.jpg': {'neben': 'neben/gesicht', 'kamera': gut}},
                                                   ['a.jpg'])
        self.assertEqual(aus['a.jpg']['neben'], 'neben/gesicht')
        self.assertEqual(aus['a.jpg']['kamera']['hoehe'], 1600)
