# -*- coding: utf-8 -*-
"""Gerätewahl und Detektorschwelle der Foto-Runner (19.09.2026).

Zwei Befunde derselben Nacht, beide ohne Fehlermeldung:

1. Die RTX PRO 4500 Blackwell (sm_120) ist für python8ENVs torch 1.13.1
   (Kerne bis sm_86) unbekannt — PyMAF-X hing 15 Minuten in
   `load_state_dict`, 0 % GPU, nur eine UserWarning auf stderr.
   `Pymafxstart.geraet()` weicht auf die CPU aus, wenn `karte_passt`
   nein sagt, und `detektor()` stellt den openpifpaf-`Predictor` mit um
   (dessen `device` ist ein Klassenattribut, das sich beim Import selbst
   auf `cuda` stellt).
2. SMPLest-X verwarf Damiras Vorderansicht: YOLOv8x 0,38 bei Schwelle
   0,5 — auf einem Rendering, in dem die Sichtung schon 33 Landmarken
   gefunden hatte. `_run_smplest_x_bilder.py --zuversicht 0.2` senkt die
   Schwelle; das Bildmodell gibt sie mit.

Sabotage: `karte_passt` immer wahr → Fall `blackwell_auf_torch_1_13` rot;
`--zuversicht` nicht geparst → Fall `zuversicht_ist_kein_pfad` rot.
"""

import os
import sys
import types
import unittest

from ._pruefablage import Pruefablage
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from pymafxstart import Pymafxstart  # noqa: E402


class Torchattrappe:
    """So viel `torch`, wie `Pymafxstart.geraet` anfasst."""

    def __init__(self, karte, kerne, verfuegbar=True):
        self.cuda = types.SimpleNamespace(
            is_available=lambda: verfuegbar,
            get_device_capability=lambda: karte,
            get_arch_list=lambda: kerne,
        )

    @staticmethod
    def device(name):
        return name


class DieKartenpruefung(unittest.TestCase):
    KERNE_1_13 = ['sm_37', 'sm_50', 'sm_60', 'sm_61', 'sm_70', 'sm_75', 'sm_80', 'sm_86', 'compute_37']

    def _start(self, torch):
        start = Pymafxstart('/egal', None)
        # `geraet()` importiert torch selbst — die Attrappe steht dafür bereit.
        sys.modules['torch'] = torch
        self.addCleanup(sys.modules.pop, 'torch', None)
        return start

    def test_blackwell_auf_torch_1_13_rechnet_auf_der_cpu(self):
        torch = Torchattrappe((12, 0), self.KERNE_1_13)
        self.assertFalse(Pymafxstart.karte_passt(torch))
        self.assertEqual(self._start(torch).geraet(), 'cpu')

    def test_ampere_auf_torch_1_13_bleibt_auf_der_karte(self):
        torch = Torchattrappe((8, 6), self.KERNE_1_13)
        self.assertTrue(Pymafxstart.karte_passt(torch))
        self.assertEqual(self._start(torch).geraet(), 'cuda')

    def test_ohne_karte_cpu_ohne_kartenpruefung(self):
        torch = Torchattrappe((0, 0), [], verfuegbar=False)
        self.assertEqual(self._start(torch).geraet(), 'cpu')


class DieDetektorschwelle(unittest.TestCase):
    """`_run_smplest_x_bilder._argumente`: Option und Pfade auseinanderhalten."""

    @staticmethod
    def _argumente(argv):
        import _run_smplest_x_bilder

        return _run_smplest_x_bilder._argumente(argv)

    def test_zuversicht_ist_kein_pfad(self):
        with Pruefablage.datei('x', endung='.jpg') as pfad:
            zuversicht, pfade = self._argumente(['--zuversicht', '0.2', pfad])
            self.assertEqual(zuversicht, 0.2)
            self.assertEqual([os.path.basename(p) for p in pfade], [os.path.basename(pfad)])

    def test_ohne_option_bleibt_die_schwelle_des_modells(self):
        with Pruefablage.datei('x', endung='.jpg') as pfad:
            zuversicht, pfade = self._argumente([pfad, '/gibt/es/nicht.jpg'])
            self.assertIsNone(zuversicht)
            self.assertEqual(len(pfade), 1, 'nur vorhandene Dateien')

    def test_das_bildmodell_gibt_die_schwelle_mit(self):
        from core.dienste.bildmodellschaetzung import Bildmodellschaetzung

        self.assertGreater(Bildmodellschaetzung.ZUVERSICHT, 0.0)
        self.assertLess(Bildmodellschaetzung.ZUVERSICHT, 0.38, 'Damiras Vorderansicht muss durch')
