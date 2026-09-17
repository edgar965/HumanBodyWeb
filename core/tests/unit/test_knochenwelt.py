# -*- coding: utf-8 -*-
u"""`Knochenwelt` — die EINE Vorwärtskinematik des Rigs.

Vier Kopien derselben Rekursion (`Animumsetzung._rig_punkte`,
`Codyfigur._welt`, `Skelettbahn._welt`, `Stofframpe.lage`) wurden am
17.09.2026 auf diese Klasse gezogen; die Gegenprobe gegen die alten
Fassungen am echten DEF-Rig (176 Knochen, drei Zufallsbilder) war bitgleich
(`ProjektTemp/knochenwelt_gegenprobe.py`). Hier die Wahrheit an einer
Kette aus drei Knochen, von Hand gerechnet.
"""
import numpy as np
from django.test import SimpleTestCase

from ._modelphysik import Modelphysik

EINHEIT = [0.0, 0.0, 0.0, 1.0]
#: 90° um Z als [x, y, z, w]
UM_Z_90 = [0.0, 0.0, np.sqrt(0.5), np.sqrt(0.5)]
KETTE = {
    'wurzel': {'local_position': [0.0, 0.0, 0.8], 'local_quaternion': EINHEIT,
               'parent': None},
    'arm': {'local_position': [0.0, 1.0, 0.0], 'local_quaternion': EINHEIT,
            'parent': 'wurzel'},
    'hand': {'local_position': [0.0, 1.0, 0.0], 'local_quaternion': EINHEIT,
             'parent': 'arm'},
    'waise': {'local_position': [5.0, 0.0, 0.0], 'local_quaternion': EINHEIT,
              'parent': 'gibtesnicht'},
}


class DieVorwaertskinematik(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Knochenwelt = Modelphysik.modul('knochenwelt').Knochenwelt

    def welt(self, lokal, namen=('hand',), ort=None):
        return self.Knochenwelt.loesen(KETTE, list(namen), lokal, ort)

    def test_in_ruhe_addieren_sich_die_versaetze_die_kette_hinauf(self):
        welt = self.welt(lambda name: np.array(EINHEIT))
        np.testing.assert_allclose(welt['hand'][0], [0.0, 2.0, 0.8])
        np.testing.assert_allclose(welt['hand'][1], EINHEIT)

    def test_eltern_werden_mitgeloest_auch_wenn_sie_nicht_verlangt_sind(self):
        welt = self.welt(lambda name: np.array(EINHEIT))
        self.assertEqual(set(welt), {'wurzel', 'arm', 'hand'})

    def test_eine_drehung_des_arms_schwenkt_die_hand_um_den_arm(self):
        u"""Arm 90° um Z: die Hand liegt 1 m in −X neben dem Armansatz."""
        welt = self.welt(lambda n: np.array(UM_Z_90 if n == 'arm' else EINHEIT))
        np.testing.assert_allclose(welt['arm'][0], [0.0, 1.0, 0.8], atol=1e-12)
        np.testing.assert_allclose(welt['hand'][0], [-1.0, 1.0, 0.8], atol=1e-12)
        np.testing.assert_allclose(welt['hand'][1], UM_Z_90, atol=1e-12)

    def test_der_ort_verschiebt_die_wurzel_und_damit_alles(self):
        welt = self.welt(lambda name: np.array(EINHEIT), ort=[1.0, 2.0, 3.0])
        np.testing.assert_allclose(welt['wurzel'][0], [1.0, 2.0, 3.8])
        np.testing.assert_allclose(welt['hand'][0], [1.0, 4.0, 3.8])

    def test_ein_unbekannter_elternteil_macht_den_knochen_zur_wurzel(self):
        welt = self.welt(lambda name: np.array(EINHEIT), namen=('waise',),
                         ort=[0.0, 0.0, 1.0])
        np.testing.assert_allclose(welt['waise'][0], [5.0, 0.0, 1.0])

    def test_die_lokale_drehung_wird_je_knochen_genau_einmal_erfragt(self):
        gefragt = []

        def lokal(name):
            gefragt.append(name)
            return np.array(EINHEIT)

        self.welt(lokal, namen=('hand', 'arm', 'hand'))
        self.assertEqual(sorted(gefragt), ['arm', 'hand', 'wurzel'])
