# -*- coding: utf-8 -*-
"""`Figurkarte` — die Figur des Figurcache je Bild im Speicher des Render-Prozesses (01.11.2026, Edgar: „mach variante B: … alles im Speicher“).

Kunstfigur mit zwei Knochen und drei Bildern: Knochen 0 wandert je Bild um (i, 0, 0), Knochen 1 um (0, 2i, 0), die Bindung ist die Einheit. Netz A hängt mit einer Einflussspalte an
Knochen 0, Netz B halb an beiden (zwei Spalten) — `bild` häutet beide in EINEM Aufruf von `Haeutung.punkte` und füllt A dafür mit Gewicht 0 auf. Ein starres Netz folgt seiner Matrix
je Bild. Alles kommt in Z oben zurück (glTF (x, y, z) → (x, −z, y), wie `Figurcache.zup`). Gerechnet auf der CPU (Kunstfigur, Millisekunden); im Render läuft dieselbe Rechnung auf
der Karte. Die Gegenprobe gegen echte PC2-Caches ist `ProjektTemp/_wegwerf/animation_koenigin/figurkarte_gegenprobe.py` (koenigin1: alle 20 Netze bis 0,0004 mm).

Geschrieben am 01.11.2026, nicht gelaufen; keine Sabotage-Gegenprobe.
"""

from types import SimpleNamespace

import numpy as np
import scipy.sparse
from django.test import SimpleTestCase
from Figurfilm.figurkarte import Figurkarte


class FigurkarteTest(SimpleTestCase):
    databases = set()
    BILDER = 3

    @staticmethod
    def _zup(p):
        p = np.asarray(p, dtype=np.float64)
        return np.stack([p[:, 0], -p[:, 2], p[:, 1]], 1)

    @classmethod
    def _karte(cls):
        welt = np.tile(np.eye(4), (cls.BILDER, 2, 1, 1))
        for i in range(cls.BILDER):
            welt[i, 0, :3, 3] = (i, 0, 0)
            welt[i, 1, :3, 3] = (0, 2 * i, 0)
        karte = Figurkarte(welt, np.tile(np.eye(4), (2, 1, 1)), 'cpu')
        karte.haut('A', {'punkte': [[0, 0, 0], [1, 0, 0]], 'gelenke': [[0], [0]], 'gewichte': [[1.0], [1.0]]}, lambda i: None)
        karte.haut('B', {'punkte': [[0, 0, 1]], 'gelenke': [[0, 1]], 'gewichte': [[0.5, 0.5]]}, lambda i: None)
        return karte

    def _gleich(self, ist, soll):
        np.testing.assert_allclose(ist.cpu().numpy(), self._zup(soll), atol=1e-6)

    def test_haut_folgt_den_knochen_in_z_oben(self):
        karte = self._karte()
        for i in range(self.BILDER):
            bild = karte.bild(i)
            self._gleich(bild['A'], [[i, 0, 0], [1 + i, 0, 0]])
            self._gleich(bild['B'], [[i / 2, i, 1]])               # halb an beiden Knochen: (i/2, i, 0) dazu

    def test_deltas_vor_der_haeutung(self):
        karte = self._karte()
        karte.haut('C', {'punkte': [[0, 0, 0]], 'gelenke': [[1]], 'gewichte': [[1.0]]}, lambda i: np.array([[[0.0, 0.0, 0.1 * i]]]))
        karte.haut('D', {'punkte': [[0, 0, 0]], 'gelenke': [[1]], 'gewichte': [[1.0]]}, lambda i: None)
        self._gleich(karte.bild(2)['C'], [[0, 4, 0.2]])
        self._gleich(karte.bild(2)['D'], [[0, 4, 0]])               # das Delta von C geht nicht in D über
        self._gleich(karte.bild(1)['A'], [[1, 0, 0], [2, 0, 0]])     # und nicht in die Ruhe von A (geklont, nicht überschrieben)

    def test_starres_netz_folgt_seiner_matrix(self):
        karte = self._karte()
        je_bild = np.tile(np.eye(4), (self.BILDER, 1, 1))
        je_bild[:, :3, 3] = [(0, 0, i) for i in range(self.BILDER)]
        karte.starr('S', [[1, 0, 0]], je_bild)
        self._gleich(karte.bild(2)['S'], [[1, 0, 2]])

    def test_unterteilung_als_duenne_matrix(self):
        karte = self._karte()
        gewichte = scipy.sparse.csr_matrix(np.array([[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]]))
        karte.fein('A', SimpleNamespace(gewichte=gewichte, vertreter=np.array([0, 1])))
        self._gleich(karte.bild(1)['A'], [[1, 0, 0], [2, 0, 0], [1.5, 0, 0]])

    def test_merkt_zwei_bilder_und_klemmt(self):
        karte = self._karte()
        for i in range(self.BILDER):
            karte.bild(i)
        self.assertEqual(sorted(karte._merk), [1, 2])
        self.assertIs(karte.bild(99), karte.bild(2))
        self._gleich(karte.bild(-5)['A'], [[0, 0, 0], [1, 0, 0]])

    def test_mitte_je_bild(self):
        mitte = self._karte().mitte('A')
        self.assertEqual(mitte.dtype, np.float64)
        np.testing.assert_allclose(mitte, self._zup([[i + 0.5, 0, 0] for i in range(self.BILDER)]), atol=1e-6)

    def test_ohne_hautnetze(self):
        karte = Figurkarte(np.tile(np.eye(4), (2, 1, 1, 1)), np.eye(4)[None], 'cpu')
        karte.starr('S', [[0, 1, 0]], np.tile(np.eye(4), (2, 1, 1)))
        self._gleich(karte.bild(0)['S'], [[0, 1, 0]])
