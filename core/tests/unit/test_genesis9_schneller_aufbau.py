# -*- coding: utf-8 -*-
"""Die schneller gemachten Teile des Genesis-9-Aufbaus (12.10.2026, `meshfigur-tempo.md`) liefern dieselben Zahlen wie die Rechnungen, die sie ersetzen — Kunstdaten, ohne Daz-Bibliothek, ohne GPU.

* `G9morphsumme.addieren` gegen `np.add.at` (eindeutige und wiederholte Indizes, Wert 0, Nummern hinter dem Netz),
* `G9bildzoom.linear` gegen `scipy.ndimage.zoom(…, order=1)`,
* `G9netzteilung._ecken`/`_uvnummern`/`teilen` gegen die Schleifen davor (Vierecke, Dreiecke, ein Fünfeck, Nähte),
* `G9hautglaettung.nachbarschaft` gegen die Schleife davor,
* `G9haut._zusammenlegen` gegen `np.unique(…, axis=0)`,
* `G9offscreenwerk.sitzung` (Zählung, ohne OpenGL).

NICHT gelaufen (Tests nur auf Ansage). Die Sabotagen stehen in den Kommentaren: Wer die Prüfung `nummern[1:] > nummern[:-1]` in `addieren` streicht, macht `test_wiederholte_indizes` rot.
"""

import numpy as np
from django.test import SimpleTestCase

from Genesis9.bildzoom import G9bildzoom
from Genesis9.haut import G9haut
from Genesis9.hautglaettung import G9hautglaettung
from Genesis9.morphsumme import G9morphsumme
from Genesis9.netzteilung import G9netzteilung
from Genesis9.offscreenwerk import G9offscreenwerk


class MorphsummeTest(SimpleTestCase):
    def _alt(self, punkte, nummern, deltas, wert):
        gueltig = nummern < len(punkte)
        np.add.at(punkte, nummern[gueltig], deltas[gueltig] * wert)
        return punkte

    def test_eindeutig_wie_add_at(self):
        z = np.random.default_rng(1)
        punkte = z.normal(size=(500, 3))
        nummern = np.sort(z.choice(500, 120, replace=False)).astype(np.int32)
        deltas = z.normal(size=(120, 3)).astype(np.float32)
        for wert in (0.7, -1.3, np.float64(0.25)):
            a = self._alt(punkte.copy(), nummern, deltas, wert)
            b = G9morphsumme.addieren(punkte.copy(), nummern, deltas, wert)
            self.assertTrue(np.array_equal(a, b))

    def test_wert_null_aendert_nichts(self):
        punkte = np.arange(30, dtype=float).reshape(10, 3)
        vorher = punkte.copy()
        G9morphsumme.addieren(punkte, np.array([1, 2, 3]), np.ones((3, 3), dtype=np.float32), 0.0)
        self.assertTrue(np.array_equal(punkte, vorher))

    def test_nummern_hinter_dem_netz_zaehlen_nicht(self):
        punkte = np.zeros((10, 3))
        nummern = np.array([2, 5, 9, 10, 40])
        deltas = np.ones((5, 3), dtype=np.float32)
        G9morphsumme.addieren(punkte, nummern, deltas, 1.0)
        self.assertEqual(float(punkte.sum()), 9.0)            # drei Punkte à drei Achsen

    def test_wiederholte_indizes(self):
        # Ein Index zweimal: `punkte[nummern] += …` würde nur einmal zählen — die Prüfung auf strenges Aufsteigen schickt den Fall an `np.add.at`.
        punkte = np.zeros((6, 3))
        nummern = np.array([1, 1, 3])
        deltas = np.ones((3, 3), dtype=np.float32)
        G9morphsumme.addieren(punkte, nummern, deltas, 1.0)
        self.assertTrue(np.array_equal(punkte[1], [2.0, 2.0, 2.0]))


class BildzoomTest(SimpleTestCase):
    def test_wie_scipy_order_1(self):
        from scipy import ndimage

        z = np.random.default_rng(2)
        for n, f, c in ((16, 4, 4), (32, 2, 3), (9, 8, 4)):
            a = z.random((n, n, c))
            self.assertLess(float(np.abs(ndimage.zoom(a, (f, f, 1), order=1) - G9bildzoom.linear(a, f)).max()), 1e-12)

    def test_ecken_bleiben_ecken(self):
        a = np.arange(16, dtype=float).reshape(4, 4)
        b = G9bildzoom.linear(a, 3)
        self.assertEqual(b.shape, (12, 12))
        self.assertEqual((b[0, 0], b[-1, -1]), (a[0, 0], a[-1, -1]))


class NetzteilungTest(SimpleTestCase):
    @staticmethod
    def _alt_ecken(polys):
        ecken, material, flaeche = [], [], []
        for nummer, p in enumerate(polys):
            m = int(p[1])
            punkte = [int(x) for x in p[2:]]
            if len(punkte) == 4:
                a, b, c, d = punkte
                ecken.extend((a, b, c, a, c, d))
                material.extend((m, m))
                flaeche.extend((nummer,) * 6)
            elif len(punkte) == 3:
                ecken.extend(punkte)
                material.append(m)
                flaeche.extend((nummer,) * 3)
            else:
                for i in range(1, len(punkte) - 1):
                    ecken.extend((punkte[0], punkte[i], punkte[i + 1]))
                    material.append(m)
                    flaeche.extend((nummer,) * 3)
        return np.asarray(ecken), np.asarray(material), np.asarray(flaeche)

    def test_ecken_wie_die_schleife(self):
        polys = [[0, 0, 0, 1, 2, 3], [0, 1, 1, 2, 4], [0, 0, 4, 5, 6, 7, 8], [0, 1, 2, 3], [0, 0, 5]]       # Viereck, Dreieck, Fünfeck, Zweieck (keine Fläche), Einzelpunkt
        a, b = self._alt_ecken(polys), G9netzteilung._ecken(polys, {})
        for x, y in zip(a, b, strict=True):
            self.assertTrue(np.array_equal(x, y))

    def test_nahtnummern_und_teilen(self):
        polys = [[0, 0, 0, 1, 2, 3], [0, 0, 2, 3, 4, 5], [0, 1, 1, 2, 6]]
        uvs = np.random.default_rng(3).random((9, 2)) + [1.0, 0.0]            # u über 1: UDIM-Kachel 1002
        ueber = {(0, 2): 7, (1, 3): 8}
        ecken, _m, flaeche = G9netzteilung._ecken(polys, ueber)
        alt = np.array([ueber.get((f, p), p) for f, p in zip(flaeche, ecken, strict=True)], dtype=np.int64)
        self.assertTrue(np.array_equal(alt, G9netzteilung._uvnummern(ecken, flaeche, ueber)))
        ursprung, uv, dreiecke, gruppen = G9netzteilung.teilen(polys, ['a', 'b'], uvs, ueber)
        self.assertEqual(len(dreiecke), 5)
        self.assertTrue((uv[:, 0] < 1.0).all())
        self.assertEqual([g['kachel'] for g in gruppen], [1002, 1002])
        # (Punkt, UV)-Paare: der Punkt 2 trägt wegen der Naht zwei UV
        # Fläche 0 liest Punkt 2 mit UV 7 (Naht), die Flächen 1 und 2 mit UV 2: zwei verschiedene Paare, also zwei Browserpunkte (gemessen 12.10.2026: ursprung = [0, 1, 2, 2, 3, 3, 4, 5, 6]).
        self.assertEqual(int((ursprung == 2).sum()), 2)


class HautglaettungTest(SimpleTestCase):
    def test_nachbarschaft_wie_die_schleife(self):
        from scipy import sparse

        polys = [[0, 0, 0, 1, 2, 3], [0, 0, 2, 3, 4], [0, 0, 4, 5, 6, 7, 8], [0, 0, 1, 2]]
        a, b = [], []
        for p in polys:
            ecken = [int(x) for x in p[2:]]
            for i, e in enumerate(ecken):
                a.append(e)
                b.append(ecken[(i + 1) % len(ecken)])
        m = sparse.coo_matrix((np.ones(2 * len(a)), (np.concatenate([a, b]), np.concatenate([b, a]))), shape=(9, 9)).tocsr()
        m.data[:] = 1.0
        grad = np.asarray(m.sum(axis=1)).ravel()
        grad[grad == 0] = 1.0
        alt = sparse.diags(1.0 / grad) @ m
        self.assertEqual((alt != G9hautglaettung.nachbarschaft(polys, 9)).nnz, 0)


class HautZusammenlegenTest(SimpleTestCase):
    def test_wie_unique_axis_0(self):
        z = np.random.default_rng(4)
        punkte, spalten = z.integers(0, 50, 400), z.integers(0, 12, 400)
        werte = z.random(400)
        paare = np.stack([punkte, spalten], axis=1)
        eindeutig, zurueck = np.unique(paare, axis=0, return_inverse=True)
        summe = np.bincount(zurueck.ravel(), weights=werte, minlength=len(eindeutig))
        p, s, w = G9haut._zusammenlegen(punkte, spalten, werte)
        self.assertTrue(np.array_equal(p, eindeutig[:, 0]) and np.array_equal(s, eindeutig[:, 1]))
        self.assertTrue(np.allclose(w, summe))


class OffscreenwerkTest(SimpleTestCase):
    def test_sitzung_zaehlt_und_verschachtelt(self):
        self.assertFalse(G9offscreenwerk.offen())
        with G9offscreenwerk.sitzung():
            self.assertTrue(G9offscreenwerk.offen())
            with G9offscreenwerk.sitzung():
                self.assertTrue(G9offscreenwerk.offen())
            self.assertTrue(G9offscreenwerk.offen())
        self.assertFalse(G9offscreenwerk.offen())
