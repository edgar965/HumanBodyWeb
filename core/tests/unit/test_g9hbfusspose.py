# -*- coding: utf-8 -*-
u"""Die Fusspose eines Daz-Schuhs auf HumanBody (`core/dienste/g9hbfusspose.py`).

WARUM (19.09.2026, Edgar mit Bild: „Die Sandalen fitten nicht"): Die Bardot
Sandals sind fuer den gebeugten Fuss modelliert; auf HumanBody stand der
flache Fuss vor und ueber der Sandale. Jetzt bekommt die Figur den Absatz aus
der Daz-Fusspose, und das Stueck geht vor dem Haeuten in die Ruhelage.

Kunstdaten, keine Bibliothek:

1. `absatz`: aus `l_foot` x 25,7 / `l_toes` x -34,4 werden Winkel 25,7,
   Sprengung 8,7; der Hub ist der tiefste Punkt der Teile (5 cm unter dem
   Boden -> 5,0 cm); ohne Fusspose None.
2. `gebeugt`: ein Punkt vor dem Knoechel geht bei positivem Winkel nach UNTEN
   (die Ferse steigt); ein Punkt an einem fremden Knochen bleibt.
3. `ruhelage` ist die Umkehrung von `gebeugt` — auch bei gemischten Gewichten
   (Fuss 0,6 / Zehen 0,4), auf 0,01 mm.
"""
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.g9hbfusspose import G9hbfusspose

KOEPFE = {'DEF-foot.L': np.array([0.20, 0.09, 0.02]), 'DEF-toe.L': np.array([0.21, 0.02, 0.15]),
          'DEF-foot.R': np.array([-0.20, 0.09, 0.02]), 'DEF-toe.R': np.array([-0.21, 0.02, 0.15])}
ABSATZ = {'winkel_grad': 25.7, 'sprengung_grad': 8.7, 'hebung_cm': 5.0, 'plateau_cm': 0.0}


def haut(index, gewicht):
    return {'knochen': ['DEF-shin.L', 'DEF-foot.L', 'DEF-toe.L'],
            'index': np.asarray(index, dtype=np.int64), 'gewicht': np.asarray(gewicht, dtype=np.float64)}


class Absatz(SimpleTestCase):
    databases = set()

    def test_aus_der_daz_fusspose(self):
        griff = {'l_foot': {'rotation/x': 25.709, 'rotation/y': 2.58},
                 'l_toes': {'rotation/x': -34.41}}
        with mock.patch('core.dienste.g9hbfusspose.G9garderobe.griff', return_value=griff):
            aus = G9hbfusspose.absatz('bardot_sandals', [np.array([[0, -0.05, 0], [0, 0.03, 0]])])
        self.assertEqual(aus['winkel_grad'], 25.71)
        self.assertEqual(aus['sprengung_grad'], 8.7)
        self.assertEqual(aus['hebung_cm'], 5.0)
        self.assertEqual(aus['quelle'], 'schuh:bardot_sandals')

    def test_ohne_fusspose_keiner(self):
        with mock.patch('core.dienste.g9hbfusspose.G9garderobe.griff', return_value={}):
            self.assertIsNone(G9hbfusspose.absatz('angie_jeans', [np.zeros((3, 3))]))


class Beugung(SimpleTestCase):
    databases = set()

    def test_vor_dem_knoechel_geht_es_nach_unten(self):
        p = np.array([[0.20, 0.02, 0.15]])                     # Ballen, 13 cm vor dem Knoechel
        aus = G9hbfusspose.gebeugt(p, haut([[1, 0, 0, 0]], [[1, 0, 0, 0]]), ABSATZ, KOEPFE)
        self.assertLess(aus[0, 1], p[0, 1] - 0.04)              # 13 cm * sin 25,7 = 5,6, minus Hoehe
        self.assertLess(aus[0, 2], p[0, 2])                    # und ein Stueck zurueck

    def test_fremder_knochen_bleibt(self):
        p = np.array([[0.20, 0.30, 0.02]])
        aus = G9hbfusspose.gebeugt(p, haut([[0, 0, 0, 0]], [[1, 0, 0, 0]]), ABSATZ, KOEPFE)
        np.testing.assert_allclose(aus, p)


class Ruhelage(SimpleTestCase):
    databases = set()

    def test_umkehrung_der_beugung(self):
        rng = np.random.default_rng(1)
        ziel = np.array([0.20, 0.0, 0.10]) + rng.uniform(-0.05, 0.05, size=(40, 3))
        index = np.tile([1, 2, 0, 0], (40, 1))
        gewicht = np.tile([0.6, 0.4, 0.0, 0.0], (40, 1))
        gewicht[:10] = [1.0, 0.0, 0.0, 0.0]
        h = haut(index, gewicht)
        with mock.patch.object(G9hbfusspose, 'koepfe', return_value=KOEPFE):
            ruhe = G9hbfusspose.ruhelage(ziel, h, ABSATZ)
        self.assertGreater(np.abs(ruhe - ziel).max(), 0.02)  # wirklich gedreht
        np.testing.assert_allclose(G9hbfusspose.gebeugt(ruhe, h, ABSATZ, KOEPFE), ziel, atol=1e-5)
