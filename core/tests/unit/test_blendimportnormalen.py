# -*- coding: utf-8 -*-
"""`Blendimportnormalen`: falsch getroffene Stellen der gebackenen Normalenkarte werden flach (08.10.2026).

Edgar: „was ist das Pflaster zwischen den Brüsten von cute girl?" — gemessen (`normalen_kippung.py`, Import
2026.10.08.11.28.06): Im Dekolleté sind die Normalen im Mittel 26–38° gekippt, bis 168°; die Strahlen trafen die andere Brust.

1. Ein Texel weit schief zur flachen Normale (90°, auch umgedreht 180°) wird flach, samt seinem Rand (`RAND_PX`).
2. Eine leichte Neigung (Poren, Formunterschied) und ein weit entferntes Texel bleiben unberührt.
3. Das leere Gebiet (`leer`) wird nicht angefasst, die Eingabe nicht verändert, der Anteil stimmt.

Sabotage-Gegenprobe: `GRENZE_GRAD = 120` → Fall 1 rot; `RAND_PX = 0` → der Nachbar in Fall 1 bleibt schief.
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportnormalen import Blendimportnormalen


class BlendimportnormalenTest(SimpleTestCase):
    databases = set()

    FLACH = Blendimportnormalen.FLACH

    def _karte(self, groesse=64):
        karte = np.zeros((groesse, groesse, 3), dtype=np.uint8)
        karte[:, :] = self.FLACH
        return karte

    def test_1_schiefe_und_umgedrehte_normalen_werden_flach_samt_rand(self):
        karte = self._karte()
        karte[20, 20] = (255, 128, 128)     # n = (1, 0, 0): 90° zur flachen
        karte[40, 40] = (128, 128, 0)       # n = (0, 0, -1): umgedreht, 180°
        neu, anteil = Blendimportnormalen.saeubern(karte)
        self.assertEqual(tuple(neu[20, 20]), self.FLACH)
        self.assertEqual(tuple(neu[40, 40]), self.FLACH)
        karte[21, 20] = (200, 128, 200)     # Nachbar: bleibt in der Eingabe schief ...
        neu, _ = Blendimportnormalen.saeubern(karte)
        self.assertEqual(tuple(neu[21, 20]), self.FLACH, 'der Rand wird mit flachgelegt')
        self.assertGreater(anteil, 0.0)

    def test_2_leichte_neigung_und_ferne_texel_bleiben(self):
        karte = self._karte()
        karte[10, 10] = (160, 128, 250)     # etwa 14° geneigt: eine Pore
        karte[20, 20] = (255, 128, 128)
        neu, _ = Blendimportnormalen.saeubern(karte)
        self.assertEqual(tuple(neu[10, 10]), (160, 128, 250))
        self.assertEqual(tuple(neu[50, 50]), self.FLACH)

    def test_3_leer_bleibt_und_die_eingabe_wird_nicht_veraendert(self):
        karte = self._karte()
        karte[30, 30] = (255, 128, 128)
        kopie = karte.copy()
        leer = np.zeros(karte.shape[:2], dtype=bool)
        leer[30, 30] = True
        neu, anteil = Blendimportnormalen.saeubern(karte, leer)
        self.assertEqual(tuple(neu[30, 30]), (255, 128, 128), 'ein leeres Texel gehört dem Aufrufer')
        self.assertTrue(np.array_equal(neu, kopie), 'nichts geändert: das einzige schiefe Texel ist leer')
        self.assertEqual(anteil, 0.0)
        schief = self._karte()
        schief[5, 5] = (255, 128, 128)
        Blendimportnormalen.saeubern(schief)
        self.assertEqual(tuple(schief[5, 5]), (255, 128, 128), 'die Eingabe bleibt unverändert')

    def test_4_anteil_ist_der_prozentsatz_der_geaenderten_texel(self):
        # Eine leichte Neigung ringsum (nicht FLACH): nur dann ändert sich der Rand des schiefen Texels wirklich —
        # auf einer flachen Karte würde „flachlegen" am Nachbarn nichts ändern und der Anteil (25 Texel) wäre zu groß.
        karte = self._karte(100)
        karte[:, :] = (140, 128, 250)
        karte[50, 50] = (255, 128, 128)
        neu, anteil = Blendimportnormalen.saeubern(karte)
        geaendert = int(np.any(neu != karte, axis=2).sum())
        self.assertEqual(anteil, round(100.0 * geaendert / (100 * 100), 3))
        self.assertGreater(geaendert, 1, 'mehr als das eine Texel: der Rand')
