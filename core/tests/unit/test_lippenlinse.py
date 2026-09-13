# -*- coding: utf-8 -*-
u"""`Lippenlinse`: die weiche MB-Lab-Maske auf die Lippenform beschneiden.

WARUM (Edgar, 13.09.2026, Bild aus der Szene: „die Lippen sind fehlerhaft"):
Die Maske reicht an den Mundwinkeln als Keil in die Wange, und je Dreieck
gefärbt wurde daraus ein Zickzack. Geprüft an einem Kunstgesicht — eine
Hautfläche aus Punkten im 1-mm-Raster (vorn bei 0,14 m), darin eine
Mundlinie als 1,5 mm tiefe Rinne von x = −20 bis +20 mm auf Höhe 1,500 m,
dahinter Punkte der Mundhöhle (0,12 m). Die Maske ist ein Rechteck
±32 mm × (1,490..1,510) — an der Mundlinie selbst aber nur ±20 mm breit,
wie die echte: Die Keile sitzen über und unter den Winkeln.

1. Mundwinkel ±20 mm und Mundlinie 1,500 m kommen aus dem Netz, nicht aus
   der Maske (die reicht bis ±32 mm).
2. Die Keile fallen weg: (27 mm, 1,506 m) ist nicht Lippe, obwohl die Maske
   dort weiß ist; die Mitte oben (0, 1,508 m) bleibt Lippe.
3. Der Abstand ist innen positiv, außen negativ und nimmt zum Rand hin ab.
4. Verborgene Punkte (Mundhöhle) im Umriss sind INNEN, außerhalb AUSSEN.
5. Ohne genug Maskenpunkte bleibt die Maske roh.

Sabotage-Gegenprobe: `np.abs(t) <= 1` weg in `rand` → Fall 2 rot.
"""
import numpy as np
from django.test import SimpleTestCase

from core.dienste.lippenlinse import Lippenlinse


def kunstgesicht():
    """Punkte (Blender: x, y=−vorn, z=hoch) und Maske eines Mundes."""
    xs = np.arange(-0.040, 0.0401, 0.001)
    zs = np.arange(1.480, 1.5201, 0.001)
    X, Z = np.meshgrid(xs, zs)
    x, hoch = X.ravel(), Z.ravel()
    vorn = np.full(x.shape, 0.14)
    mund = (np.abs(hoch - 1.500) < 0.0006) & (np.abs(x) <= 0.020)
    vorn[mund] = 0.1385                                  # die Rinne der Mundlinie (1,5 mm)
    # Mundhöhle: dieselben Lagen 2 cm dahinter, nur um den Mund herum
    hinten = (np.abs(x) < 0.030) & (np.abs(hoch - 1.500) < 0.012)
    px = np.concatenate([x, x[hinten]])
    ph = np.concatenate([hoch, hoch[hinten]])
    pv = np.concatenate([vorn, np.full(hinten.sum(), 0.12)])
    punkte = np.column_stack([px, -pv, ph])
    maske = (np.abs(px) <= 0.032) & (ph >= 1.490) & (ph <= 1.510)
    maske &= ~((np.abs(ph - 1.500) < 0.0025) & (np.abs(px) > 0.020))   # an der Linie nur bis zum Winkel
    return punkte, maske


class LippenlinseTest(SimpleTestCase):

    def setUp(self):
        self.punkte, self.maske = kunstgesicht()
        self.abstand = Lippenlinse.abstand(self.maske, self.punkte)

    def wo(self, x, hoch, vorn=0.14):
        d = np.abs(self.punkte[:, 0] - x) + np.abs(self.punkte[:, 2] - hoch) + np.abs(-self.punkte[:, 1] - vorn)
        return int(np.argmin(d))

    def test_mundwinkel_und_mundlinie_kommen_aus_dem_netz(self):
        x, hoch, vorn = self.punkte[:, 0], self.punkte[:, 2], -self.punkte[:, 1]
        front = Lippenlinse.vorderseite(x, hoch, vorn)
        kand = self.maske & front
        linse = Lippenlinse.linse(x[kand], hoch[kand], vorn[kand])
        self.assertAlmostEqual(linse['xc'], 0.020, delta=0.001)
        self.assertAlmostEqual(linse['ym'], 1.500, places=3)
        self.assertAlmostEqual(linse['x0'], 0.0, places=3)

    def test_die_keile_an_den_winkeln_fallen_weg(self):
        self.assertTrue(self.maske[self.wo(0.027, 1.506)])
        self.assertLess(self.abstand[self.wo(0.027, 1.506)], 0)
        self.assertLess(self.abstand[self.wo(-0.027, 1.494)], 0)
        self.assertGreater(self.abstand[self.wo(0.0, 1.508)], 0)
        self.assertGreater(self.abstand[self.wo(0.0, 1.492)], 0)
        self.assertGreater(self.abstand[self.wo(0.017, 1.500)], 0)

    def test_abstand_innen_positiv_aussen_negativ_und_stetig(self):
        innen, rand, aussen = (self.abstand[self.wo(0.0, h)] for h in (1.503, 1.508, 1.514))
        self.assertGreater(innen, rand)
        self.assertGreater(rand, 0)
        self.assertLess(aussen, 0)
        self.assertEqual(self.abstand[self.wo(0.0, 1.480)], Lippenlinse.AUSSEN)
        beschnitten = Lippenlinse.beschneiden(self.maske, self.punkte)
        self.assertEqual(beschnitten.tolist(), (self.abstand > 0).tolist())

    def test_verborgene_punkte_im_umriss_sind_innen(self):
        self.assertEqual(self.abstand[self.wo(0.0, 1.500, vorn=0.12)], Lippenlinse.INNEN)
        self.assertEqual(self.abstand[self.wo(0.028, 1.500, vorn=0.12)], Lippenlinse.AUSSEN)

    def test_ohne_genug_maske_bleibt_sie_roh(self):
        wenig = np.zeros(len(self.punkte), dtype=bool)
        wenig[:10] = True
        self.assertEqual(Lippenlinse.beschneiden(wenig, self.punkte).tolist(), wenig.tolist())
