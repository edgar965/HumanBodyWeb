# -*- coding: utf-8 -*-
"""`Schammessungtextur` — Farbe des Scham-Stücks gegen das Original und gegen die Haut daneben (10./11.10.2026), an Kunstbildern und der Kunsthaut `_nahtwelt.Nahtwelt`.

Edgar: „die Textur ist unterschiedlich von der Umgebung". Zwei Maße an den TEXTUREN (nicht am Bildschirm): `am_ring` (Stück am Rand gegen die Hautkachel in Bändern vom Rand) und
`gegen_original` (Farbe des Stück-Atlas an jeder Ecke gegen die des Originals an der Stelle, die nah liegt und DASSELBE ZEIGT — seit 11.10.2026 mit den Normalen der Ecken, wie der Bake).

1. `abtasten` liest den Texel unter (u, v) mit v nach oben; `leuchtdichte` nach 0,2126 R + 0,7152 G + 0,0722 B.
2. `am_ring`: Stück (196, 145, 128) gegen Haut (200, 150, 130): drei Bänder, im ersten die Leuchtdichte des Stücks 2,9 % unter der der Haut (von Hand: 154,61 gegen 159,19), Mittel der Stückfarbe am Rand
   stimmt. Ohne Farbbild oder ohne Kacheln gibt es einen Hinweis statt einer Zahl.
3. `gegen_original`: gleiche Farbe → Mittel 0, Anteil „anders" 0; entgegengesetzte Farbe → Mittel über 100, Anteil 1. `farbe_an` bekommt die Orte UND die Normalen der Ecken (Form `(N, 3)` beide).
4. Ecken weiter als `NAH_M` vom Original zählen nicht (dort mischt der Bake die Haut dazu): keine nahe Ecke → Hinweis.

Sabotage-Gegenprobe (11.10.2026 im Speicher gelaufen, `ProjektTemp/_wegwerf/sabotage.py`: mit der Sabotage rot, ohne grün — Wortlaut als Quelltext-Änderung ungelaufen): `leuchtdichte` mit 0,5/0,5/0 macht Fall 2 rot; in `gegen_original` `farbe_an(ort[nah])` ohne Normalen macht Fall 3 rot (Argumente).
"""
from pathlib import Path

import numpy as np
from django.test import SimpleTestCase
from PIL import Image

from core.dienste.schammessungrahmen import Schammessungrahmen
from core.dienste.schammessungtextur import Schammessungtextur

from ._nahtwelt import Nahtwelt
from ._pruefablage import Pruefablage


class SchammessungtexturTest(SimpleTestCase):
    databases = set()

    def test_1_abtasten_liest_den_texel_unter_u_v_und_die_leuchtdichte_stimmt(self):
        bild = np.zeros((2, 4, 3), dtype=np.uint8)
        bild[0, 3] = (10, 20, 30)                                      # oben rechts
        bild[1, 0] = (200, 100, 50)                                    # unten links
        werte = Schammessungtextur.abtasten(bild, np.array([[0.9, 0.9], [0.1, 0.1]]))
        self.assertEqual(werte.tolist(), [[10.0, 20.0, 30.0], [200.0, 100.0, 50.0]])
        self.assertAlmostEqual(float(Schammessungtextur.leuchtdichte(np.array([200.0, 150.0, 130.0]))), 159.19, places=2)

    def _am_ring(self, stueck_farbe, haut_farbe, mit_kachel=True):
        figur, loch = Nahtwelt.haut()
        punkte, dreiecke = Nahtwelt.stueck(5.0)
        sichtbar = np.ones(len(figur['dreiecke']), dtype=bool)
        sichtbar[loch['dreiecke']] = False
        figur = dict(figur, uv=np.column_stack([figur['punkte'][:, 0] * 10 + 0.5, figur['punkte'][:, 1] * 10 + 0.5]), kachel=np.zeros(len(figur['dreiecke']), dtype=np.int64))
        rand = loch['ring']
        uv_ecken = np.full((len(dreiecke), 3, 2), 0.5)
        stueck = np.tile(np.array(stueck_farbe, dtype=np.uint8), (4, 4, 1))
        with Pruefablage.ordner('textur_') as ordner:
            pfad = Path(ordner) / 'kachel.png'
            Image.fromarray(np.tile(np.array(haut_farbe, dtype=np.uint8), (4, 4, 1))).save(pfad)
            return Schammessungtextur.am_ring(rand, punkte, dreiecke, uv_ecken, stueck, figur, sichtbar, (lambda k: pfad) if mit_kachel else None)

    def test_2_die_farbe_am_ring_gegen_die_haut_daneben(self):
        m = self._am_ring((196, 145, 128), (200, 150, 130))
        self.assertEqual(m['stueck_rand']['rgb'], [196.0, 145.0, 128.0])
        self.assertEqual(len(m['baender']), 3)
        erstes = m['baender'][0]
        self.assertGreater(erstes['n'], 0)
        self.assertAlmostEqual(erstes['leuchtdichte_prozent'], -2.9, places=1)
        self.assertEqual(erstes['rgb'], [200.0, 150.0, 130.0])
        self.assertIn('hinweis', self._am_ring((196, 145, 128), (200, 150, 130), mit_kachel=False))

    def _rahmen(self):
        _figur, loch = Nahtwelt.haut()
        return Schammessungrahmen.von_ring(Nahtwelt.haut()[0]['punkte'], np.tile([0.0, 0.0, 1.0], (121, 1)), loch['ring_punkte'], Nahtwelt.stueck(5.0)[0])

    def test_3_gegen_original_gleiche_und_entgegengesetzte_farbe(self):
        punkte, dreiecke = Nahtwelt.stueck(5.0)
        uv_ecken = np.full((len(dreiecke), 3, 2), 0.5)
        farbe = np.tile(np.array([255, 0, 0], dtype=np.uint8), (4, 4, 1))
        aufrufe = []

        def original(wert):
            def farbe_an(orte, normalen):
                aufrufe.append((orte.shape, normalen.shape))
                return np.tile(np.array(wert, dtype=np.float64), (len(orte), 1))
            return farbe_an

        abstand = np.zeros(len(punkte))
        gleich = Schammessungtextur.gegen_original(self._rahmen(), punkte, dreiecke, uv_ecken, farbe, original((255, 0, 0)), abstand)
        self.assertEqual((gleich['mittel'], gleich['anteil_anders']), (0.0, 0.0))
        anders = Schammessungtextur.gegen_original(self._rahmen(), punkte, dreiecke, uv_ecken, farbe, original((0, 0, 255)), abstand)
        self.assertGreater(anders['mittel'], 100.0)
        self.assertEqual(anders['anteil_anders'], 1.0)
        self.assertEqual(aufrufe[0][0], aufrufe[0][1], 'Orte und Normalen in gleicher Form (N, 3)')
        self.assertEqual(aufrufe[0][0][1], 3)

    def test_4_ecken_weit_vom_original_zaehlen_nicht(self):
        punkte, dreiecke = Nahtwelt.stueck(5.0)
        uv_ecken = np.full((len(dreiecke), 3, 2), 0.5)
        farbe = np.tile(np.array([255, 0, 0], dtype=np.uint8), (4, 4, 1))
        weit = np.full(len(punkte), 12.0)                               # mm
        m = Schammessungtextur.gegen_original(self._rahmen(), punkte, dreiecke, uv_ecken, farbe, lambda o, n: o, weit)
        self.assertIn('hinweis', m)
        self.assertIn('hinweis', Schammessungtextur.gegen_original(self._rahmen(), punkte, dreiecke, uv_ecken, None, None, weit))
