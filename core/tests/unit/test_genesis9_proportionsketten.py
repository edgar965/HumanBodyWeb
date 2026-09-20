# -*- coding: utf-8 -*-
"""G9proportionsketten — die Fenster der Proportionsformung als Hüte zwischen den Maßstellen.

Edgar (20.09.2026, Ursula von hinten): „erkläre mir diese Welle zwischen Hüftbreite und
Oberschenkeldicke. Warum ist das eine Welle? warum interpolierst du nicht???" Bis dahin
lief jedes Maß über einen festen Rand auf 1 zurück (Hüfte 8 cm, eine Dicke 35 % der
Knochenlänge als Dreieck um die Knochenmitte) — zwischen zwei Maßstellen blieb die Figur
ungeformt, und die Oberschenkeldicke setzte einen Buckel mitten auf den Knochen.

1. `hut`: 1 im Kern, linear auf 0 an den Nachbarstellen, am Kettenende über den Rand.
2. Nachbarn in der Kette (Brust, Taille, Hüfte): die Taille hat beide, die Hüfte nur oben.
3. Zwischen Taille und Hüfte ergänzen sich die Hüte zu 1 — das ist die Interpolation.
   Sabotage: das alte Fenster (halb + Rand) ist dort 0 für beide Maße.
4. Glieder: der Oberschenkel-Hut läuft vom Hüftgelenk (0) über die Mitte (1) bis zur Wadenmitte
   (0) — über das Knie hinweg, kein Dreieck um die Knochenmitte.

Kunstdaten, keine Bibliothek.
"""

import numpy as np
from django.test import SimpleTestCase

from core.daten.wrapperpfad import Wrapperpfad


def _ketten():
    with Wrapperpfad():
        from Genesis9.proportionsketten import G9proportionsketten
    return G9proportionsketten


def _band(y, halb, rand):
    return {'m': 0.3, 'lage': {'art': 'band', 'y': y, 'halb': halb, 'rand': rand, 'achse': [1, 0, 0]}}


BEFUND = {'brust_breite': _band(1.2, 0.02, 0.05), 'taille_breite': _band(1.05, 0.01, 0.05),
          'huefte_breite': _band(0.8, 0.02, 0.08)}


class KettenTest(SimpleTestCase):
    def test_1_hut(self):
        K = _ketten()
        w = K.hut(np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.0]), 0.7, 0.05, 0.5, 1.0, 0.1)
        self.assertTrue(np.allclose(w, [0.0, 2.0 / 3.0, 1.0, 0.8, 0.4, 0.0]), w)  # linear vom Kernrand
        # Kettenende: über den Rand statt zur Nachbarstelle.
        w = K.hut(np.array([0.55, 0.6, 0.65, 0.7]), 0.7, 0.0, None, None, 0.1)
        self.assertTrue(np.allclose(w, [0.0, 0.0, 0.5, 1.0]), w)

    def test_2_nachbarn(self):
        K = _ketten()
        self.assertEqual(K.band_nachbarn(BEFUND, 'taille_breite'), (0.8, 1.2))
        self.assertEqual(K.band_nachbarn(BEFUND, 'huefte_breite'), (None, 1.05))
        self.assertEqual(K.band_nachbarn(BEFUND, 'brust_breite'), (1.05, None))

    def test_3_zwischen_zwei_massen_wird_interpoliert(self):
        K = _ketten()
        y = np.array([0.925])  # Mitte zwischen Taille (1,05) und Hüfte (0,8)
        w_t = float(K.band_fenster(y, BEFUND, 'taille_breite')[0])
        w_h = float(K.band_fenster(y, BEFUND, 'huefte_breite')[0])
        self.assertAlmostEqual(w_t, 0.5, delta=0.05)
        self.assertAlmostEqual(w_h, 0.5, delta=0.05)
        self.assertAlmostEqual(w_t + w_h, 1.0, delta=0.08)  # die Kerne (halb) verschieben die Mitte etwas
        # Sabotage: das alte Fenster (1 im Band, linear auf 0 über den festen Rand).
        alt_t = np.clip(1.0 - (abs(0.925 - 1.05) - 0.01) / 0.05, 0.0, 1.0)
        alt_h = np.clip(1.0 - (abs(0.925 - 0.8) - 0.02) / 0.08, 0.0, 1.0)
        self.assertEqual((alt_t, alt_h), (0.0, 0.0), 'die alte Fassung ließ die Mitte ungeformt (Welle)')

    def test_4_glieder_ueber_das_knie_hinweg(self):
        K = _ketten()
        g = {'l_thigh': np.array([0.1, 0.9, 0.0]), 'l_shin': np.array([0.1, 0.5, 0.0]),
             'l_foot': np.array([0.1, 0.1, 0.0])}
        befund = {'oberschenkel_dicke': {'lage': {'art': 'knochen', 't': 0.5, 'halb': 0.01}},
                  'wade_dicke': {'lage': {'art': 'knochen', 't': 0.3, 'halb': 0.01}}}
        _, glieder = K.kette('oberschenkel_dicke')
        weg = K.gliedweg(g, glieder, 'l_')
        self.assertEqual([round(w[4], 3) for w in weg], [0.0, 0.4])
        u = np.array([0.0, 0.1, 0.2, 0.36, 0.52, 0.8])
        w = K.glied_fenster(u, 'oberschenkel_dicke', weg, befund)
        self.assertTrue(np.allclose(w, [0.0, 0.5, 1.0, 0.5, 0.0, 0.0], atol=0.06), w)
        w = K.glied_fenster(u, 'wade_dicke', weg, befund)
        self.assertTrue(np.allclose(w, [0.0, 0.0, 0.0, 0.5, 1.0, 0.0], atol=0.06), w)
        # Ohne gemessene Wade läuft der Oberschenkel-Hut bis zum Knöchel aus.
        w = K.glied_fenster(np.array([0.8]), 'oberschenkel_dicke', weg,
                            {'oberschenkel_dicke': befund['oberschenkel_dicke']})
        self.assertEqual(float(w[0]), 0.0)
        w = K.glied_fenster(np.array([0.5]), 'oberschenkel_dicke', weg,
                            {'oberschenkel_dicke': befund['oberschenkel_dicke']})
        self.assertAlmostEqual(float(w[0]), 0.5, delta=0.02)
