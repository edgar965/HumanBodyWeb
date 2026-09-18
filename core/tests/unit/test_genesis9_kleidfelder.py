# -*- coding: utf-8 -*-
u"""Genesis 9, 18.09.2026 nachts (Edgar: „mach beide" — JCMs auf die Kleidung,
Regler fuer die Beugungen): `G9stueckfelder`, die zwei Schalter des Graphen
(`G9gelenkkorrekturen.REGLER`) und ihr Platz im Reglerplan — ohne Bibliothek.

Sabotage-Gegenproben: `_Rechner.wert` ohne den `eingaben`-Vorrang fuer
Graphkanaele -> Fall 1 rot (Schalter 0 wirkt nicht); `G9stueckfelder.folgt`
ohne die Strang-Pruefung -> Fall 3 rot (Strang bekaeme ein Feld);
`_aus_ablage` ohne Bestandsvergleich -> Fall 4 rot.
"""
import os
import tempfile
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from scipy.sparse import identity

from Genesis9 import stueckfelder
from Genesis9.gelenkkorrekturen import G9gelenkkorrekturen
from Genesis9.reglerplan import G9reglerplan
from Genesis9.stueckfelder import G9stueckfelder
from .test_genesis9_gelenke_lipsync import kunstgraph


class _Stufe:
    def matrix(self, n):
        return identity(n, format='csr')


class _Folger:
    def __init__(self, name, n, art=None):
        self.name = name
        self.punkte = np.zeros((n, 3))
        if art:
            self.ART = art

    def netzstufe(self, stufen):
        return _Stufe()


class _Formung:
    def __init__(self, regler):
        self.regler = regler
        self.formeln = self

    def wert(self, kanal):
        return {'body_basejointcorrectives': 1.0,
                'body_ctrl_FlexionAutoStrength': 0.123456}.get(kanal, 0.0)


def _delta(folger, formung, basis):
    u"""Kanal `a` bewegt Punkt 1 des Teils um 2 mm, `b` nichts."""
    if formung.regler != {'a': 1.0}:
        return None
    d = np.zeros((len(folger.punkte), 3))
    d[1] = [0.002, 0, 0]
    return d


class Kleidfelder(SimpleTestCase):

    databases = set()

    def test_1_regler_ueberschreibt_graphkanal(self):
        g = kunstgraph()
        # 35°: der JCM steht auf 1 — der Clamp greift NACH der Multiplikation.
        drehung = {'l_thigh': {'rotation/x': 35}}
        self.assertAlmostEqual(G9gelenkkorrekturen.werte(drehung, g)['cbs_x35p'], 1.0)
        self.assertEqual(G9gelenkkorrekturen.werte(drehung, g, regler={'schalter': 0}),
                         {})
        self.assertAlmostEqual(G9gelenkkorrekturen.werte(
            drehung, g, regler={'schalter': 0.5})['cbs_x35p'], 0.5)

    def test_2_regler_der_stellung_und_reglerplan(self):
        self.assertEqual(G9gelenkkorrekturen.regler(_Formung({})),
                         {'body_basejointcorrectives': 1.0,
                          'body_ctrl_FlexionAutoStrength': 0.1235})
        misc = {'gruppe': '/General/Misc', 'label': 'x'}
        for kanal in G9gelenkkorrekturen.REGLER:
            self.assertEqual(G9reglerplan.bereich(dict(misc, id=kanal)), 'koerper')
        self.assertIsNone(G9reglerplan.bereich(dict(misc, id='facs_ctrl_EyeLookAuto')))

    def test_3_teile_nur_projizierte_flaechennetze(self):
        teile = [(_Folger('Rock', 4), None), (_Folger('Haar', 3, 'strang'), None),
                 (_Folger('Dolch', 2), object())]
        basis = mock.Mock(punkte=np.zeros((5, 3)))
        with mock.patch.object(stueckfelder.G9garderobe, 'teile', return_value=teile), \
                mock.patch.object(stueckfelder.G9basisnetz, 'holen',
                                  return_value=basis), \
                mock.patch.object(stueckfelder, 'G9formung', _Formung), \
                mock.patch.object(stueckfelder.G9reglerfelder, '_anhangdelta', _delta):
            f = G9stueckfelder.rechnen('gelenke', ['a', 'b'], 'rock', 1)
        self.assertEqual([sorted(t) for t in f.teile], [['a'], [], []])
        nummern, deltas = f.teile[0]['a']
        self.assertEqual(list(nummern), [1])
        self.assertAlmostEqual(float(deltas[0, 0]), 0.002, places=6)
        self.assertEqual(f.steckbrief()['punkte'], 1)

    def test_4_ablage_rundlauf_und_bestand(self):
        n = np.array([1, 3], dtype=np.uint32)
        d = np.array([[0.001, 0, 0], [0, 0.002, 0]], dtype=np.float32)
        f = G9stueckfelder('gelenke', 'rock', 1, ['a'], [{'a': (n, d)}, {}])
        with tempfile.TemporaryDirectory(dir=os.getcwd()) as ordner:
            with mock.patch.object(stueckfelder.G9pfade, 'ablage',
                                   return_value=Path(ordner)), \
                    mock.patch.object(G9stueckfelder, 'bestand', return_value='x'):
                f._ablegen()
                wieder = G9stueckfelder._aus_ablage('gelenke', 'rock', 1, ['a'])
                self.assertEqual(len(wieder.teile), 2)
                np.testing.assert_array_equal(wieder.teile[0]['a'][0], n)
                np.testing.assert_array_equal(wieder.teile[0]['a'][1], d)
                self.assertEqual(wieder.teile[1], {})
                self.assertIsNone(
                    G9stueckfelder._aus_ablage('gelenke', 'rock', 1, ['a', 'b']))
            with mock.patch.object(stueckfelder.G9pfade, 'ablage',
                                   return_value=Path(ordner)), \
                    mock.patch.object(G9stueckfelder, 'bestand', return_value='y'):
                self.assertIsNone(
                    G9stueckfelder._aus_ablage('gelenke', 'rock', 1, ['a']))
