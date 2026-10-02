# -*- coding: utf-8 -*-
u"""Fotohülle (01.10.2026 abends) — Kunstdaten: eine ebene „Figur" (Gitter) und ein „Netz" 1 cm davor mit Stücken.

1. Die Hülle liegt um den Abstand zum Netz vor der Figur (in `ABSTAND_MIN`…`ABSTAND_MAX`), UV im Bild, Farbe des Stücks.
2. Das obere Stück schließt eine Lücke ohne Stück zum unteren, wächst aber nicht in dessen Fläche hinein.
3. Der Höhenbereich schneidet ab, was außerhalb liegt (die grauen Schienbeine der Socken).

Sabotage: `UEBER = {}` → Fall 2 rot; in `bauen` den Versatz weglassen → Fall 1 rot.
"""
import numpy as np
from django.test import SimpleTestCase

from core.dienste.fotohuelle import Fotohuelle


class _Scan:
    def __init__(self, punkte, flaechen, farbe):
        self.punkte, self.flaechen, self.farbe = punkte, flaechen, farbe

    def farben(self, flaeche, _bary):
        return np.tile(np.asarray(self.farbe, dtype=np.uint8), (len(flaeche), 1))


def _gitter(n=21, z=0.0, schritt=0.01):
    y, x = np.mgrid[0:n, 0:n] * schritt
    punkte = np.column_stack([x.ravel(), y.ravel(), np.full(n * n, z)])
    i = np.arange(n * n).reshape(n, n)
    a, b, c, d = i[:-1, :-1].ravel(), i[:-1, 1:].ravel(), i[1:, :-1].ravel(), i[1:, 1:].ravel()
    return punkte, np.vstack([np.column_stack([a, b, d]), np.column_stack([a, d, c])])


class FotohuelleTest(SimpleTestCase):
    databases = set()

    def _huelle(self, luecke=True):
        figur, dreiecke = _gitter()
        netz, flaechen = _gitter(z=0.01)
        y = netz[flaechen].mean(axis=1)[:, 1]
        stueck = np.where(y > 0.11, 1, 2)
        if luecke:
            stueck[(y > 0.09) & (y < 0.12)] = 0                # 3 cm Haut zwischen Saum und Bund
        return Fotohuelle(_Scan(netz, flaechen, (60, 70, 90)), stueck, np.zeros(len(flaechen), bool), figur, figur,
                          dreiecke), figur, dreiecke

    def test_1_versatz_uv_farbe(self):
        h, _f, _d = self._huelle(luecke=False)
        punkte, flaechen, uv, bild = h.bauen(1)
        self.assertTrue(len(flaechen))
        z = np.abs(punkte[:, 2])
        self.assertTrue(((z >= Fotohuelle.ABSTAND_MIN - 1e-6) & (z <= Fotohuelle.ABSTAND_MAX + 1e-6)).all())
        self.assertGreater(float(np.median(z)), 0.008)
        self.assertTrue(((uv >= 0) & (uv <= 1)).all())
        np.testing.assert_allclose(bild.reshape(-1, 3).mean(axis=0), [60, 70, 90], atol=1.0)

    def test_2_luecke_zum_unteren_stueck(self):
        h, figur, dreiecke = self._huelle()
        oben = h._auswahl(1)
        y = figur[dreiecke].mean(axis=1)[:, 1]
        self.assertTrue(oben[(y > 0.095) & (y < 0.115)].all())          # die Lücke gehört zum Shirt
        self.assertFalse(oben[y < 0.07].any())                          # nicht in die Hose hinein

    def test_3_hoehenbereich(self):
        h, figur, dreiecke = self._huelle(luecke=False)
        y = figur[dreiecke].mean(axis=1)[:, 1]
        wahl = h._auswahl(2, hoehen=(0.0, 0.04))
        self.assertTrue(wahl.any())
        self.assertFalse(wahl[y > 0.04 + Fotohuelle.HOEHE_RAND + 0.011].any())
