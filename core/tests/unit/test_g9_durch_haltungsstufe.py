"""„Hand in der eigenen Figur“ ist aus und wirkt mit Gewicht nur auf die Armhaltung, die Hülle nur in `pose_only`, Gelenke unter 0,75 sind rot (`ballerina_bunt`, 06./07.11.2026). Ohne Datenbank, ohne Karte."""
import sys
import unittest
from pathlib import Path

import torch

from Genesis9.meshipnet import G9meshipnet

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'meshgenesis'))
from meshgenesis_meshglieder import Meshgenesismeshglieder  # noqa: E402
from meshgenesis_meshpruefung import Meshgenesismeshpruefung  # noqa: E402


class EinpassungOhneStrafeTest(unittest.TestCase):
    databases = []

    def test_offsets_kennen_keine_strafe(self):
        self.assertNotIn('durch', G9meshipnet.get_loss_weights_d())

    def test_summe_ist_die_von_ipnet(self):
        w = {'a': lambda cst, it: 2.0 * cst, 'b': lambda cst, it: 3.0 * cst}
        self.assertEqual(float(G9meshipnet.backward_step({'a': torch.tensor(1.0), 'b': torch.tensor(2.0)}, w, 0)), 8.0)


class HuelleNurBeiDerHaltungTest(unittest.TestCase):
    databases = []

    def setUp(self):
        g = object.__new__(G9meshipnet)
        g.teile = []
        self.w = g._gewichte_pose_shape()
        self.roh = G9meshipnet.get_loss_weights()
        self.wert = torch.tensor(7.0)

    def test_pose_shape_ohne_huelle(self):
        self.assertEqual(float(self.w['huelle'](self.wert, 0)), 0.0)

    def test_pose_only_mit_huelle(self):
        self.assertEqual(float(self.roh['huelle'](self.wert, 0)), 7.0 * G9meshipnet.HUELLE_GEWICHT)

    def test_ohne_teile_gibt_es_kein_pose_only_und_die_huelle_zaehlt(self):
        g = object.__new__(G9meshipnet)
        g.teile = None
        self.assertEqual(float(g._gewichte_pose_shape()['huelle'](self.wert, 0)), 7.0 * G9meshipnet.HUELLE_GEWICHT)

    def test_die_uebrigen_gewichte_bleiben(self):
        self.assertEqual(float(self.w['s2m'](self.wert, 0)), float(self.roh['s2m'](self.wert, 0)))


class StrafeNurAufDerHaltungTest(unittest.TestCase):
    databases = []

    def glieder(self):
        g = object.__new__(Meshgenesismeshglieder)
        g.k = lambda x, haltung, trans: (x.sum() * torch.ones(2, 3) + haltung.sum() + trans.sum(),)
        g.ipnet = type('Ipnet', (), {'_durchdringung': staticmethod(lambda v: (v ** 2).sum())})()
        return g

    def test_regler_bekommen_keinen_gradienten(self):
        g = self.glieder()
        x, h, t = (torch.ones(2, requires_grad=True), torch.ones(4, 3, requires_grad=True), torch.zeros(3))
        g._stand = x, h, t
        g._dazu(None, 0, {'durch': lambda cst, it: 100.0 * cst}).backward()
        self.assertIsNone(x.grad)
        self.assertGreater(float(h.grad.abs().sum()), 0.0)

    def test_ohne_ipnet_keine_strafe(self):
        g = self.glieder()
        g.ipnet = None
        self.assertIsNone(g._dazu(None, 0, {}))


class GelenkdickeTest(unittest.TestCase):
    databases = []

    def test_keilarm_ist_rot(self):
        zeilen = Meshgenesismeshpruefung.dicke_zeilen({'Handgelenk l': 0.57, 'Ellbogen l': 0.9})
        self.assertEqual(len(zeilen), 1)
        self.assertIn('Handgelenk l', zeilen[0])

    def test_gesunde_figur_ist_nicht_rot(self):
        self.assertEqual(Meshgenesismeshpruefung.dicke_zeilen({'Ellbogen l': 0.768, 'Handgelenk l': 0.78}), [])

    def test_ohne_abnahme_nichts(self):
        self.assertEqual(Meshgenesismeshpruefung.dicke_zeilen(None), [])
