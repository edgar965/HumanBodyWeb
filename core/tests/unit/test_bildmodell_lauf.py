# -*- coding: utf-8 -*-
"""Bildmodelllauf.relativ — Fortschritt ab dem Startschritt (Balken unter „Neu berechnen").

Ein Start ab Zielnetz beginnt im Gesamtbalken bei 60 %; der Balken am
Personenformular soll dort bei 0 stehen und bei 100 enden.
"""

import unittest
from types import SimpleNamespace

from core.dienste.bildmodelllauf import Bildmodelllauf


class RelativTest(unittest.TestCase):
    def test_ab_zielnetz_zaehlt_von_null(self):
        von = Bildmodelllauf.BAENDER['ziel'][0]
        job = SimpleNamespace(optionen={'ab': 'ziel'}, progress=von)
        self.assertEqual(Bildmodelllauf.relativ(job), {'ab': 'ziel', 'prozent': 0})
        job.progress = 100
        self.assertEqual(Bildmodelllauf.relativ(job)['prozent'], 100)
        job.progress = von + (100 - von) // 2
        self.assertEqual(Bildmodelllauf.relativ(job)['prozent'], 50)

    def test_vor_dem_startschritt_bleibt_null(self):
        job = SimpleNamespace(optionen={'ab': 'anpassung'}, progress=0)
        self.assertEqual(Bildmodelllauf.relativ(job)['prozent'], 0)

    def test_ohne_oder_mit_unbekanntem_startschritt_ganzer_lauf(self):
        self.assertEqual(Bildmodelllauf.relativ(SimpleNamespace(optionen={}, progress=50))['ab'], 'sichtung')
        job = SimpleNamespace(optionen={'ab': 'quatsch'}, progress=50)
        self.assertEqual(Bildmodelllauf.relativ(job), {'ab': 'sichtung', 'prozent': 50})
        self.assertEqual(Bildmodelllauf.relativ(SimpleNamespace(optionen=None, progress=None))['prozent'], 0)
