# -*- coding: utf-8 -*-
u"""`Wurzelspur` legt den Weg der Figur in den Rahmen des Elternknochens.

WARUM (05.09.2026): Der Weg aus der BVH ist in Weltkoordinaten, die Spur
wird aber als LOKALE Lage des Wurzelknochens gelesen. Bei DEF ist die Wurzel
elternlos — beides dasselbe. Bei UMA haengt `Hips` unter `Position` unter
`Global`, und `Global` traegt eine Drehung: Ohne Umrechnung liefe die Figur
in die falsche Richtung, mit korrekten Drehungen — die Sorte Fehler, die
niemand an einer einzelnen Zahl sieht.

Aufruf:  python manage.py test core.tests.unit.test_wurzelspur_elternrahmen
"""
import numpy as np
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.quaternion import Quat  # noqa: E402
from humanbody_core.skeleton.retarget.wurzelspur import Wurzelspur  # noqa: E402


class _Knochen:
    def __init__(self, local_pos, eltern_rot):
        self.local_pos = np.array(local_pos, dtype=float)
        self.parent_world_rest_quat = eltern_rot


class _Skelett:
    def __init__(self, eltern_rot):
        self.bones = {'Hips': _Knochen((0, 1, 0), eltern_rot)}


class _Bvh:
    names = ['Hips']
    children = {}
    #: Zwei Bilder: die Wurzel wandert um 10 Einheiten nach +Z.
    positions = np.array([[[0.0, 0.0, 0.0]], [[0.0, 0.0, 10.0]]])


class WurzelspurElternrahmenTest(SimpleTestCase):

    @staticmethod
    def _spur(skelett):
        return Wurzelspur(_Bvh(), skelett, {'Hips': 'Hips'}, 0.01, 2).spur()['values']

    def test_ohne_drehung_bleibt_der_weg_wie_er_ist(self):
        self.assertTrue(np.allclose(self._spur(_Skelett(Quat.ID.copy())),
                                    [0, 1, 0, 0, 1, 0.1]))

    def test_mit_halber_drehung_kehrt_sich_der_weg_um(self):
        u"""Elternteil um 180 Grad um Y: +Z in Welt ist -Z im Rahmen."""
        self.assertTrue(np.allclose(self._spur(_Skelett(np.array([0.0, 1.0, 0.0, 0.0]))),
                                    [0, 1, 0, 0, 1, -0.1]))

    def test_ohne_elternangabe_wie_frueher(self):
        u"""Attrappen ohne das Feld (aeltere Tests) laufen weiter."""
        skelett = _Skelett(None)
        del skelett.bones['Hips'].parent_world_rest_quat
        self.assertTrue(np.allclose(self._spur(skelett), [0, 1, 0, 0, 1, 0.1]))
