# -*- coding: utf-8 -*-
"""`Schattenausgleich`: das breite Helligkeitsgefälle eines Fotos geht weg, Details bleiben (20.09.2026).

Edgar: „woher der schwarze Flecken aus der Textur an der Seite kommt" — dieselbe Haut war
im Foto von hinten L 70, im Foto von vorn L 134 (`ProjektTemp/flanke_messung.py`).
Kunstbild: einfarbige Haut, links halb so hell wie rechts (linear, breites Gefälle), dazu
ein kleiner dunkler Fleck (Detail) und ein grauer Hintergrund außerhalb der Maske.

1. Nach dem Ausgleich sind linkes und rechtes Drittel gleich hell (±5 %); der Fleck ist
   weiter dunkler als seine Umgebung (Detail bleibt); der Hintergrund bleibt unberührt
   (er zählt nicht als Haut), der Farbton der Haut bleibt (Cr/Cb im Hautbereich).
2. Sabotage: ohne Ausgleich ist das Verhältnis links/rechts ≈ 0,66 (Drittelmittel des
   Gefälles 0,5 → 1,0) — der Test sieht das Gefälle.
3. Ein Bild ohne Haut kommt unverändert zurück (`bereich` = (1, 1)).
"""

import unittest

import numpy as np

from core.tests.unit._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from schattenausgleich import Schattenausgleich  # noqa: E402

HAUT = np.array([0.55, 0.32, 0.22])      # linear, ein warmer Hautton


def _kunstbild(n=256):
    """(rgb uint8, maske) — Haut mit Gefälle 0,5 → 1,0, Fleck bei (n/2, n/2), grauer Rand."""
    x = np.linspace(0.0, 1.0, n)
    hell = (0.5 + 0.5 * x)[None, :, None]
    lin = np.ones((n, n, 3)) * HAUT[None, None, :] * hell
    yy, xx = np.mgrid[:n, :n]
    fleck = (yy - n // 2) ** 2 + (xx - n // 2) ** 2 < 3 ** 2
    lin[fleck] *= 0.5
    maske = np.zeros((n, n), bool)
    maske[16:-16, 16:-16] = True
    lin[~maske] = 0.6                                  # neutraler Hintergrund, keine Haut
    srgb = Schattenausgleich.srgb(lin)
    return np.clip(np.rint(srgb * 255), 0, 255).astype(np.uint8), maske


class SchattenausgleichTest(unittest.TestCase):
    def _hell(self, rgb):
        lin = Schattenausgleich.linear(rgb.astype(np.float32) / 255.0)
        return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]

    def test_1_gefaelle_weg_details_bleiben(self):
        rgb, maske = _kunstbild()
        s = Schattenausgleich()
        aus = s.anwenden(rgb, maske)
        h = self._hell(aus)
        links = h[40:216, 20:80].mean()
        rechts = h[40:216, 176:236].mean()
        self.assertAlmostEqual(links / rechts, 1.0, delta=0.05, msg='Gefälle bleibt')
        umgebung = h[118:138, 100:112].mean()
        self.assertLess(h[128, 128], 0.7 * umgebung, 'Detail (Fleck) verschwunden')
        self.assertTrue(np.array_equal(aus[:8, :8], rgb[:8, :8]), 'Hintergrund verändert')
        self.assertTrue(Schattenausgleich.haut(aus)[maske].mean() > 0.95, 'Farbton verlassen')
        lo, hi = s.bereich
        self.assertLess(lo, 0.9)
        self.assertGreater(hi, 1.1)

    def test_2_sabotage_ohne_ausgleich(self):
        rgb, _ = _kunstbild()
        h = self._hell(rgb)
        self.assertAlmostEqual(h[40:216, 20:80].mean() / h[40:216, 176:236].mean(), 0.66, delta=0.05)

    def test_3_ohne_haut_unveraendert(self):
        grau = np.full((64, 64, 3), 150, np.uint8)
        s = Schattenausgleich()
        self.assertTrue(np.array_equal(s.anwenden(grau), grau))
        self.assertEqual(s.bereich, (1.0, 1.0))
