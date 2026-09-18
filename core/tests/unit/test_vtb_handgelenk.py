# -*- coding: utf-8 -*-
"""Das Handgelenk aus der Handquelle gilt nur, wo es anatomisch moeglich bleibt.

DER ANLASS (13.09.2026, Edgar an `005 DanceLang`: „die Finger bewegen sich
nach oben, also brechen sie" / „die Handgelenkwinkel sind auch kaputt"):
Kein Fingergelenk war ueberstreckt — die HAND war zum Unterarm bis 179 Grad
geklappt, in 26 % der Bilder ueber 80 Grad. `Smplxmischung.handgelenk()`
schreibt die Weltdrehung der Handquelle (SMPLest-X) unter GEMs Unterarm;
wo beide Koerper am Arm uneins sind, landete der ganze Unterschied im
Handgelenk. Jetzt bleibt in solchen Bildern GEMs eigenes Handgelenk, und
`Gelenkgrenzen` kappt jedes Handgelenk auf 80 Grad Schwenk / 90 Grad
Verdrehung.

BDD - GEGEBEN / DANN
====================
    DieHandgelenkmischung     ... uebernimmt ein moegliches Handgelenk (30 Grad) aus der Handquelle
                    ... verwirft ein unmoegliches (150 Grad) und behaelt GEMs eigenes
                    ... zaehlt die verworfenen Bilder in der Bilanz
    DieGelenkgrenzen ... kappen ein Handgelenk ueber 80 Grad Schwenk

Sabotage-Gegenprobe (13.09.2026): `HANDGELENK_MOEGLICH = (180, 180)` ->
„verwirft" und „zaehlt" rot; Handgelenke aus SCHWENKGRENZEN entfernt ->
„kappen" rot.
"""

import unittest

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np  # noqa: E402
from gelenkgrenzen import Gelenkgrenzen  # noqa: E402
from scipy.spatial.transform import Rotation  # noqa: E402
from smplskelett import Smplskelett  # noqa: E402
from smplxbahn import Smplxbahn  # noqa: E402
from smplxmischung import Smplxmischung  # noqa: E402
from smplxreihe import Smplxreihe  # noqa: E402

LINKS = Smplskelett.NAMEN.index('Left_wrist')  # 20
#: Beugung des linken Handgelenks nach vorn (Arm entlang +x): um -y.
BEUGEACHSE = np.array([0.0, -1.0, 0.0])


def _reihe(n, handgelenk_grad):
    """SMPLest-X-Reihe: Koerper in Ruhe, nur das linke Handgelenk gedreht."""
    reihe = Smplxreihe(30.0, np)
    koerper = np.zeros((21, 3))
    koerper[LINKS - 1] = np.radians(handgelenk_grad) * BEUGEACHSE
    for _ in range(n):
        reihe.dazu(
            {
                'smplx_root_pose': np.zeros(3),
                'smplx_body_pose': koerper.ravel(),
                'smplx_lhand_pose': np.zeros(45),
                'smplx_rhand_pose': np.zeros(45),
                'smplx_jaw_pose': np.zeros(3),
                'smplx_expr': np.zeros(10),
                'smplx_shape': np.zeros(10),
                'cam_trans': np.zeros(3),
            },
            (1, 2, 3, 4),
            [(1.0, 2.0)] * 72,
        )
    return reihe.als_felder()


def _winkel(bahn, gelenk):
    return np.degrees(np.linalg.norm(bahn.body_pose[:, gelenk - 1], axis=1))


class DieHandgelenkmischung(unittest.TestCase):
    N = 12

    def _bahn(self, eigen_grad=10.0):
        bahn = Smplxbahn(self.N, 30.0, np)
        bahn.body_pose[:, LINKS - 1] = np.radians(eigen_grad) * BEUGEACHSE
        return bahn

    def test_ein_moegliches_handgelenk_kommt_aus_der_handquelle(self):
        bahn = self._bahn()
        mischung = Smplxmischung(bahn, _reihe(self.N, 30.0), np)
        mischung.handgelenk(0.0)
        np.testing.assert_allclose(_winkel(bahn, LINKS), 30.0, atol=1e-3)
        self.assertEqual(mischung.bilanz['handgelenk_verworfen'], 0)

    def test_ein_unmoegliches_handgelenk_bleibt_gems_eigenes(self):
        bahn = self._bahn()
        mischung = Smplxmischung(bahn, _reihe(self.N, 150.0), np)
        mischung.handgelenk(0.0)
        np.testing.assert_allclose(_winkel(bahn, LINKS), 10.0, atol=1e-3)
        self.assertEqual(mischung.bilanz['handgelenk_verworfen'], self.N)

    def test_die_grenze_ist_die_der_gelenkgrenzen(self):
        _, schwenk_max = Gelenkgrenzen.SCHWENKGRENZEN[LINKS][1:]
        self.assertEqual(Smplxmischung.HANDGELENK_MOEGLICH[0], schwenk_max)


class DieGelenkgrenzen(unittest.TestCase):
    def test_ein_handgelenk_ueber_80_grad_wird_gekappt(self):
        feld = np.tile(np.array([[1.0, 0.0, 0.0, 0.0]]), (2, len(Smplskelett.NAMEN), 1))
        x, y, z, w = Rotation.from_rotvec(np.radians(170) * BEUGEACHSE).as_quat()
        feld[0, LINKS] = [w, x, y, z]
        self.assertEqual(Gelenkgrenzen.anwenden(feld, np), 1)
        w, x, y, z = feld[0, LINKS]
        achse = Gelenkgrenzen.knochenachse(Smplskelett.NAMEN.index('Left_palm'), np)
        gedreht = Rotation.from_quat([x, y, z, w]).apply(achse)
        self.assertAlmostEqual(np.degrees(np.arccos(np.clip(np.dot(gedreht, achse), -1, 1))), 80.0, places=1)
