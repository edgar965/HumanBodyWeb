# -*- coding: utf-8 -*-
"""Kopf-Fit (20.09.2026, „200 Plus Genesis 9 Edition") — ohne Datenbank, ohne Genesis-Netz:

1. `G9reglerableitung.regler(teil=…)`: `koerper` lässt Kopf und Mimik weg, `kopf` nimmt nur
   den Bereich Kopf; ohne Teil alles (Sabotage: ein Kopfregler im Körpersatz fiele auf).
2. `G9reglerableitung.mit_grund`: gleiche Deltas, neuer Grund; `stellung` trägt die
   Körperregler des Grunds weiter, die keine Variable sind.
3. `Bildmodellkopfanpassung._gesamt`: RMS über ALLE gewichteten Punkte neu gemessen, Teile
   des Körpers behalten, Kopfteil ersetzt, Verlauf angehängt und als `kopf` markiert.
"""

import numpy as np
from django.test import SimpleTestCase
from Genesis9.reglerableitung import G9reglerableitung

from core.dienste.bildmodellkopfanpassung import Bildmodellkopfanpassung


def _plan():
    return [
        {'name': 'Proportion Height', 'bereich': 'koerper', 'art': 'form', 'min': -1, 'max': 1},
        {'name': '200_Nose_Width', 'bereich': 'kopf', 'art': 'form', 'min': -1, 'max': 1},
        {'name': 'Amala_head_ctrl', 'bereich': 'kopf', 'art': 'form', 'min': 0, 'max': 1},
        {'name': 'facs_jawOpen', 'bereich': 'mimik', 'art': 'pose', 'min': 0, 'max': 1},
        {'name': 'Mass Neck', 'bereich': 'hals', 'art': 'form', 'min': -1, 'max': 1},
    ]


class TeilTest(SimpleTestCase):
    databases = set()

    def test_koerper_ohne_kopf_und_mimik(self):
        namen = [r['name'] for r in G9reglerableitung.regler('charaktere', _plan(), teil='koerper')]
        self.assertEqual(namen, ['Proportion Height', 'Mass Neck'])

    def test_kopf_nur_kopf(self):
        namen = [r['name'] for r in G9reglerableitung.regler('charaktere', _plan(), teil='kopf')]
        self.assertEqual(namen, ['200_Nose_Width', 'Amala_head_ctrl'])

    def test_ohne_teil_alles_ausser_pose(self):
        namen = [r['name'] for r in G9reglerableitung.regler('charaktere', _plan())]
        self.assertEqual(len(namen), 4)

    def test_mit_grund(self):
        a = G9reglerableitung(['200_Nose_Width'], {'200_Nose_Width': ['200_Nose_Width']},
                              {'BaseFeminine': 1.0}, np.zeros((1, 2, 3)), np.zeros((1, 1, 3)),
                              ['head'], np.zeros((2, 3)), np.zeros((1, 3)), np.array([[-1.0, 1.0]]))
        b = a.mit_grund({'BaseFeminine': 1.0, 'Proportion Height': 0.4, '200_Nose_Width': 0.0})
        self.assertIs(b.punkte, a.punkte)
        self.assertEqual(b.stellung([0.25]),
                         {'BaseFeminine': 1.0, 'Proportion Height': 0.4, '200_Nose_Width': 0.25})


class GesamtTest(SimpleTestCase):
    databases = set()

    def test_rms_ueber_alle_punkte_und_teile_gemischt(self):
        koerper = {'regler': {'Proportion Height': 0.4}, 'variablen': ['Proportion Height'],
                   'verlauf': [{'durchgang': 1, 'rms_mm': 6.0}], 'teile': {'kopf': 9.0, 'rumpf': 3.0},
                   'gelenke_mm': 2.5}
        rest = np.array([[0.003, 0, 0], [0, 0.004, 0], [0, 0, 0]])   # Kopf 3 mm, Rumpf 4 mm, ungewichtet
        kopf = {'regler': {'Proportion Height': 0.4, '200_Nose_Width': 0.3}, 'x': [0.3],
                'variablen': ['200_Nose_Width'], 'verlauf': [{'durchgang': 1, 'rms_mm': 3.0}],
                'teile': {'kopf': 3.0}, 'rest': rest, 'punkte': np.zeros((3, 3))}
        g = Bildmodellkopfanpassung._gesamt(koerper, kopf, np.array([1.0, 1.0, 0.0]))
        self.assertEqual(g['teile'], {'kopf': 3.0, 'rumpf': 3.0})
        self.assertAlmostEqual(g['punkte_rms_mm'], round(np.sqrt((9 + 16) / 2), 2))  # 3,54 mm
        self.assertEqual(g['gelenke_mm'], 2.5)
        self.assertEqual([v.get('stufe') for v in g['verlauf']], [None, 'kopf'])
        self.assertEqual(g['regler']['200_Nose_Width'], 0.3)
        self.assertEqual(g['variablen'], ['Proportion Height', '200_Nose_Width'])
