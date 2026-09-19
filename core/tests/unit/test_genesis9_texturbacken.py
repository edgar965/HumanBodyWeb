# -*- coding: utf-8 -*-
"""G9texturbacken und G9texturabtastung ohne Bibliothek (19.09.2026, abends erweitert).

Edgar: „warum ist das Modell noch mit dieser miserablen Textur?" — die Kacheln
werden seither je Texel abgetastet. Hier an einer Kunststufe (zwei Dreiecke in
Kachel 1001, Seite 64):

1. `G9texturabtastung.aus_stufe`: jedes Texel im Dreieck trägt seine Nummer und
   Anteile, die sich zu 1 summieren; außerhalb −1; `farben` rastert Gouraud
   (Ecke rot, Schwerpunkt Mischung) mit Deckung.
2. `rand_ziehen`: ungemalte Pixel bis `RAND_PX` bekommen die nächste gemalte Farbe.
3. `getoent`: eine graue Albedo wird auf den Fototon gezogen, Faktor begrenzt.
4. `hd_schicht`: Texelfarben in Zeilenordnung der Inseltexel, Lücken bis
   `RAND_PX` eingemalt, Rand um die Insel gezogen; Sabotage: eine Schicht
   mit falscher Texelzahl fliegt raus (ValueError).
5. `herkunftsbild`: Palette je Bildnummer, außerhalb durchsichtig.
"""

import unittest

import numpy as np
from Genesis9.texturabtastung import G9texturabtastung
from Genesis9.texturbacken import G9texturbacken


class _Stufe:
    """Zwei Dreiecke: ein Quadrat von (0,125; 0,125) bis (0,875; 0,875) in Kachel 1001."""

    def __init__(self):
        self.uv = np.array([[0.125, 0.125], [0.875, 0.125], [0.875, 0.875], [0.125, 0.875]])
        self.ursprung = np.array([0, 1, 2, 3])
        self.dreiecke = np.array([[0, 1, 2], [0, 2, 3]])
        self.gruppen = [{'name': 'Head', 'kachel': 1001, 'index_ab': 0, 'index_anzahl': 6}]


def _abtastung(seite=64):
    a = G9texturabtastung.aus_stufe(_Stufe(), seite)
    return a


class _Backen(G9texturbacken):
    """Backen mit der Kunstabtastung statt der Bibliothek; Rand 4 px (die Kachel ist klein)."""

    RAND_PX = 4

    def __init__(self, abtastung):
        super().__init__(abtastung.seite)
        self._abtastung = abtastung

    def abtastung(self):
        return self._abtastung


class TexturbackenTest(unittest.TestCase):
    def test_1_abtastung_und_gouraud(self):
        a = _abtastung()
        d = a.dreieck[1001]
        self.assertEqual(a.kacheln, [1001])
        # v nach oben: uv (0,125; 0,125) liegt bei Pixel (x 8, Zeile 56)
        self.assertGreaterEqual(int(d[55, 9]), 0, 'Ecke 0 liegt in einem Dreieck')
        self.assertEqual(int(d[5, 60]), -1, 'außerhalb kein Dreieck')
        self.assertGreater(a.texel(), 0.5 * 64 * 64 * 0.75 ** 2)
        drin, ecken, anteile = a.stellen(1001)
        self.assertTrue(np.allclose(anteile.sum(1), 1.0, atol=2e-3))
        self.assertEqual(ecken.shape, (int(drin.sum()), 3))
        farben = np.array([[1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0], [1.0, 1.0, 0]])
        rgb, alpha = a.farben(1001, farben, np.array([1.0, 1.0, 0.0, 1.0]))
        self.assertGreater(rgb[55, 9, 0], 0.8)                     # Ecke 0 rot
        self.assertGreater(alpha[55, 9], 0.9)
        mitte = rgb[32, 32]
        self.assertTrue((mitte > 0.1).sum() >= 2, mitte)          # Mischung auf der Diagonale
        self.assertEqual(float(rgb[5, 60].sum()), 0.0)
        self.assertEqual(float(alpha[5, 60]), 0.0)

    def test_2_rand_ziehen(self):
        b = G9texturbacken()
        rgb = np.zeros((40, 40, 3))
        alpha = np.zeros((40, 40))
        rgb[10:20, 10:20] = [0.2, 0.5, 0.9]
        alpha[10:20, 10:20] = 1.0
        rgb, alpha = b.rand_ziehen(rgb, alpha, alpha > 0, rand=6)
        self.assertTrue(np.allclose(rgb[25, 15], [0.2, 0.5, 0.9]))
        self.assertEqual(float(alpha[25, 15]), 1.0)
        self.assertEqual(float(rgb[28, 15].sum()), 0.0)

    def test_3_toenung(self):
        b = G9texturbacken()
        albedo = np.full((8, 8, 3), 0.5)
        aus = b.getoent(albedo, [187, 132, 103])
        self.assertTrue(np.allclose(aus.reshape(-1, 3).mean(0) * 255, [187, 132, 103], atol=1.0),
                        aus[0, 0] * 255)
        # Grenze: Schwarz kann nicht auf Hautton gehoben werden (Faktor ≤ 2,5).
        dunkel = b.getoent(np.full((4, 4, 3), 0.02), [187, 132, 103])
        self.assertLess(float(dunkel.max()), 0.2)
        self.assertIs(b.getoent(albedo, None), albedo)

    def test_4_hd_schicht_und_sabotage(self):
        a = _abtastung()
        b = _Backen(a)
        drin = a.stellen(1001)[0]
        n = int(drin.sum())
        farbe = np.tile(np.array([[200, 100, 50]], dtype=np.uint8), (n, 1))
        gewicht = np.ones(n, dtype=np.float32)
        # Ein Loch von 6 × 6 Texeln in der Mitte (kleiner als RAND_PX): wird eingemalt.
        ys, xs = np.nonzero(drin)
        loch = (ys >= 30) & (ys < 36) & (xs >= 30) & (xs < 36)
        gewicht[loch] = 0.0
        hd = {'farbe_1001': farbe, 'gewicht_1001': gewicht}
        rgb, alpha = b.hd_schicht(1001, hd)
        self.assertGreater(float(alpha[32, 32]), 0.5, 'Loch eingemalt')
        self.assertTrue(np.allclose(rgb[32, 32] * 255, [200, 100, 50], atol=3))
        self.assertEqual(float(alpha[0, 0]), 0.0, 'fern der Insel keine Deckung')
        self.assertGreater(float(alpha[6, 30]), 0.0, 'bis RAND_PX über die Insel hinaus gezogen (Filterrand)')
        with self.assertRaises(ValueError):
            b.hd_schicht(1001, {'farbe_1001': farbe[:-1], 'gewicht_1001': gewicht[:-1]})

    def test_5_herkunftsbild(self):
        a = _abtastung()
        b = _Backen(a)
        n = int(a.stellen(1001)[0].sum())
        herkunft = np.full(n, 1, dtype=np.int16)
        herkunft[:10] = -1
        bild = np.asarray(b.herkunftsbild(1001, {'herkunft_1001': herkunft}, groesse=64))
        self.assertEqual(bild.shape, (64, 64, 4))
        self.assertEqual(tuple(bild[32, 32]), (60, 140, 230, 255))
        self.assertEqual(int(bild[5, 60, 3]), 0)
