# -*- coding: utf-8 -*-
u"""`Skelettausrichtung` — die Figur blickt danach nach +Z, wie DEF.

WARUM (05.09.2026): Die UMA-GLB steht um 180 Grad gedreht. Der Retarget
korrigiert die Wurzel nicht; ungedreht liefe die UMA-Figur bei derselben
Aufnahme rueckwaerts. Die Blickrichtung wird aus zwei Knochen gemessen,
deren Seite feststeht — deshalb prueft dieser Test auch, dass ein Skelett,
das schon richtig steht, unangetastet bleibt.

Aufruf:  python manage.py test core.tests.unit.test_skelettausrichtung
"""
import numpy as np
from django.test import SimpleTestCase

from ._umaattrappe import Umaattrappe
from humanbody_core.skeleton import (  # noqa: E402
    SkeletonGeometry, Skelettausrichtung)


class SkelettausrichtungTest(SimpleTestCase):

    @staticmethod
    def _welt(knochen, name):
        welt = SkeletonGeometry.from_three(knochen).compute_world_transforms()
        return welt[name]['world_pos']

    @staticmethod
    def _ausrichtung(knochen):
        return Skelettausrichtung(knochen, 'LeftUpLeg', 'RightUpLeg')

    def test_die_gedrehte_attrappe_blickt_nach_minus_z(self):
        richtung = self._ausrichtung(Umaattrappe.gedreht()).blickrichtung()
        self.assertTrue(np.allclose(richtung, [0, 0, -1], atol=1e-6), richtung)

    def test_danach_blickt_sie_nach_plus_z(self):
        ausgerichtet = self._ausrichtung(Umaattrappe.gedreht()).ausgerichtet()
        richtung = self._ausrichtung(ausgerichtet).blickrichtung()
        self.assertTrue(np.allclose(richtung, [0, 0, 1], atol=1e-6), richtung)
        self.assertGreater(self._welt(ausgerichtet, 'LeftUpLeg')[0], 0.05)

    def test_nur_die_wurzel_wird_angefasst(self):
        vorher = Umaattrappe.gedreht()
        nachher = self._ausrichtung(vorher).ausgerichtet()
        for a, b in zip(vorher, nachher):
            if a['parent']:
                self.assertEqual(a, b)
            else:
                self.assertNotEqual(a['local_quaternion'], b['local_quaternion'])

    def test_eine_richtig_stehende_figur_bleibt(self):
        nachher = self._ausrichtung(Umaattrappe.uma_knochen()).ausgerichtet()
        wurzel = [k for k in nachher if not k['parent']][0]
        self.assertTrue(np.allclose(wurzel['local_quaternion'], [0, 0, 0, 1],
                                    atol=1e-9))

    def test_eine_vierteldrehung_wird_erkannt(self):
        s = np.sqrt(0.5)
        winkel = self._ausrichtung(Umaattrappe.gedreht(quat=(0, s, 0, s))).drehwinkel()
        self.assertAlmostEqual(abs(winkel), np.pi / 2, places=6)

    def test_fehlender_knochen_wirft(self):
        with self.assertRaises(ValueError):
            Skelettausrichtung(Umaattrappe.uma_knochen(), 'LeftUpLeg',
                               'Gibtesnicht').blickrichtung()

    def test_die_eingabe_bleibt_unveraendert(self):
        vorher = Umaattrappe.gedreht()
        kopie = [dict(k) for k in vorher]
        self._ausrichtung(vorher).ausgerichtet()
        self.assertEqual(vorher, kopie)
