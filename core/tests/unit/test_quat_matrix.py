# -*- coding: utf-8 -*-
u"""`Quat.matrix` und `Quat.from_matrix` — hin und zurueck, alle vier Zweige.

WARUM (05.09.2026): Beide sind neu, fuer den GLB-Leser (Bindmatrizen) und
die Wurzelspur. `from_matrix` hat vier Zweige (Shepperd); der erste greift
bei kleinen Drehungen, die anderen drei erst bei halben Drehungen um je
eine Achse — genau die Faelle, die ein Test mit nur einer Drehung nie sieht.

Aufruf:  python manage.py test core.tests.unit.test_quat_matrix
"""
import math

import numpy as np
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.quaternion import Quat  # noqa: E402


class QuatMatrixTest(SimpleTestCase):

    @staticmethod
    def _um(achse, grad):
        a = np.array(achse, dtype=float) / np.linalg.norm(achse)
        h = math.radians(grad) / 2
        return np.array([*(a * math.sin(h)), math.cos(h)])

    def test_matrix_dreht_wie_rotate(self):
        q = self._um((1, 2, 3), 37)
        v = np.array([0.3, -0.7, 1.1])
        self.assertTrue(np.allclose(Quat.matrix(q) @ v, Quat.rotate(q, v)))

    def test_vierteldrehung_um_y_legt_x_auf_minus_z(self):
        self.assertTrue(np.allclose(Quat.matrix(self._um((0, 1, 0), 90)) @ [1, 0, 0],
                                    [0, 0, -1]))

    def test_hin_und_zurueck_alle_vier_zweige(self):
        u"""Kleine Drehung (Spur > 0) und die drei halben Drehungen (Spur -1)."""
        for q in (self._um((1, 2, 3), 37), self._um((1, 0, 0), 180),
                  self._um((0, 1, 0), 180), self._um((0, 0, 1), 180),
                  self._um((1, 1, 0), 180)):
            m = Quat.matrix(q)
            zurueck = Quat.from_matrix(m)
            self.assertTrue(np.allclose(Quat.matrix(zurueck), m, atol=1e-9), q)

    def test_die_einheitsmatrix_ergibt_die_einheitsdrehung(self):
        self.assertTrue(np.allclose(Quat.from_matrix(np.eye(3)), Quat.ID))

    def test_zeilenweise_fuer_ein_ganzes_feld(self):
        u"""``reihe @ M.T`` — so nutzt es die Wurzelspur."""
        q = self._um((0, 1, 0), 180)
        reihe = np.array([[0, 0, 10.0], [1, 0, 0.0]])
        erwartet = np.array([Quat.rotate(q, r) for r in reihe])
        self.assertTrue(np.allclose(reihe @ Quat.matrix(q).T, erwartet))
