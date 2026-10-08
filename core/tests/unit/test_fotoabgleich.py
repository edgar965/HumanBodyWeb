# -*- coding: utf-8 -*-
"""Fotoabgleich (08.10.2026, Fotohaut der Beine): `Fotoabgleich.abgleichen` zieht das Foto per optischem Fluss der Silhouetten in den Rahmen des Modells.

Kunstdaten: Modell = zwei Rechtecke (Beine) auf einer 256 × 256-Fläche, Foto = dieselben um 24 px nach rechts versetzt, die Farbe ein waagerechter Verlauf (x/255). Keine Datenbank, keine Dateien.
Geschrieben, nicht als Suite gelaufen (`testsuite-nur-auf-ansage`).

Sabotage: in `Fotoabgleich.abgleichen` `mx, my = gx + f[..., 0], gy + f[..., 1]` durch `gx, gy` ersetzen → Fall 1 rot (die Maske bleibt versetzt).
"""

import numpy as np
from core.dienste.fotoabgleich import Fotoabgleich
from django.test import SimpleTestCase


def _flaeche(versatz):
    m = np.zeros((256, 256), dtype=bool)
    m[60:230, 70 + versatz:100 + versatz] = True
    m[60:230, 140 + versatz:170 + versatz] = True
    return m


def _verlauf():
    return np.repeat(np.linspace(0.0, 1.0, 256, dtype=np.float32)[None, :, None], 256, axis=0).repeat(3, axis=2)


class DerFotoabgleich(SimpleTestCase):
    def test_1_ein_versetztes_foto_liegt_danach_auf_dem_modell(self):
        modell, foto = _flaeche(0), _flaeche(24)
        self.assertLess(Fotoabgleich.iou(foto, modell), 0.5)
        farbe, maske, bericht = Fotoabgleich.abgleichen(_verlauf(), foto, modell)
        self.assertTrue(bericht['abgeglichen'])
        self.assertGreater(Fotoabgleich.iou(maske, modell), 0.9)
        self.assertGreater(bericht['iou_nachher'], 0.9)
        self.assertGreater(bericht['fluss_median_px'], 10.0)                        # gemessen wurde der Versatz, nicht Null

    def test_2_die_farbe_folgt_dem_koerper_nicht_dem_pixel(self):
        modell, foto = _flaeche(0), _flaeche(24)
        farbe, maske, _bericht = Fotoabgleich.abgleichen(_verlauf(), foto, modell)
        # Im Modell steht das linke Bein bei x = 85 (Mitte); im Foto steht es bei 109 — dort hat der Verlauf 109/255. Nach dem Abgleich liegt diese Farbe an der Stelle des Modells.
        wert = float(farbe[150, 85, 0])
        self.assertAlmostEqual(wert, 109.0 / 255.0, delta=0.04)
        self.assertGreater(wert, 0.36)                                              # nicht die Farbe des Pixels am alten Ort (85/255 = 0,333)

    def test_3_deckungsgleiche_oder_leere_silhouetten_bleiben_wie_sie_sind(self):
        modell = _flaeche(0)
        farbe = _verlauf()
        f2, m2, bericht = Fotoabgleich.abgleichen(farbe, modell.copy(), modell)
        self.assertIs(f2, farbe)
        self.assertFalse(bericht['abgeglichen'])
        leer = np.zeros_like(modell)
        f3, m3, bericht3 = Fotoabgleich.abgleichen(farbe, leer, modell)
        self.assertIs(f3, farbe)
        self.assertFalse(bericht3['abgeglichen'])
        self.assertFalse(Fotoabgleich.abgleichen(farbe, modell, leer)[2]['abgeglichen'])
