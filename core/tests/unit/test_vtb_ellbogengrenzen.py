# -*- coding: utf-8 -*-
"""Der Ellbogen ist kein Knie: seine Grenze klemmt Verdrehung und Schwenkung.

DER ANLASS (12.09.2026, Edgar an `0001_Dance`: „die Ellbogen sind auch
seltsam verdreht"): Seit dem 31.03.2026 trugen die Ellbogen die Grenzen des
Knies (X -5..150, Y/Z +-15). Das Knie beugt sich um X, der Ellbogen um Y —
die Grenze klemmte die Beugung auf 15 Grad und liess die Verdrehung um die
Armachse bis 150 Grad frei. Jedes BVH aus der Pipeline hatte Ellbogen, die
sich nie ueber 22,6 Grad beugten (roh: 142). Gemessen in
`HumanBodyWeb/ProjektTemp/retarget/` an der rohen Bahn gegen das BVH.

BDD - GEGEBEN / DANN
====================
    DerEllbogen  ... beugt sich um y bis 140 Grad ungehindert
                 ... wird ueber 150 Grad Schwenkung auf 150 gekappt
                 ... wird ueber 90 Grad Verdrehung um die Armachse auf 90 gekappt
                 ... steht nicht mehr in den Eulergrenzen

Sabotage-Gegenprobe (12.09.2026): die alte Zeile `18: (-5, 150, -15, 15,
-15, 15)` wieder in GRENZEN -> „beugt sich ungehindert" rot.
"""

import unittest

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np  # noqa: E402
from scipy.spatial.transform import Rotation  # noqa: E402

from gelenkgrenzen import Gelenkgrenzen  # noqa: E402
from smplskelett import Smplskelett  # noqa: E402

LINKS, RECHTS = 18, 19


class Arm:
    """Der Kunstarm im SMPL-Skelett: Achsen und Winkel je Ellbogen (18/19)."""

    @staticmethod
    def achse(gelenk):
        kind = 20 if gelenk == LINKS else 21
        achse = np.asarray(Smplskelett.OFFSETS[kind], dtype=float)
        return achse / np.linalg.norm(achse)

    @staticmethod
    def beugeachse(gelenk):
        """Beugung nach vorn: um y (links -y, rechts +y), senkrecht zur Armachse
        gestellt — der Ruheversatz zum Handgelenk liegt nicht exakt auf x."""
        y = np.array([0.0, -1.0 if gelenk == LINKS else 1.0, 0.0])
        achse = Arm.achse(gelenk)
        y = y - np.dot(y, achse) * achse
        return y / np.linalg.norm(y)

    @staticmethod
    def feld(gelenk, rot):
        feld = np.tile(np.array([[1.0, 0.0, 0.0, 0.0]]), (2, len(Smplskelett.NAMEN), 1))
        x, y, z, w = rot.as_quat()
        feld[0, gelenk] = [w, x, y, z]
        return feld

    @staticmethod
    def beugung(feld, gelenk):
        """Winkel zwischen Oberarm- und Unterarmrichtung nach der Drehung des Gelenks."""
        w, x, y, z = feld[0, gelenk]
        achse = Arm.achse(gelenk)
        gedreht = Rotation.from_quat([x, y, z, w]).apply(achse)
        return np.degrees(np.arccos(np.clip(np.dot(gedreht, achse), -1.0, 1.0)))


BEUGEACHSE = {LINKS: Arm.beugeachse(LINKS), RECHTS: Arm.beugeachse(RECHTS)}


class DerEllbogen(unittest.TestCase):
    def test_steht_nicht_mehr_in_den_eulergrenzen(self):
        self.assertNotIn(LINKS, Gelenkgrenzen.GRENZEN)
        self.assertNotIn(RECHTS, Gelenkgrenzen.GRENZEN)
        self.assertIn(LINKS, Gelenkgrenzen.SCHWENKGRENZEN)
        self.assertIn(RECHTS, Gelenkgrenzen.SCHWENKGRENZEN)

    def test_beugt_sich_bis_140_grad_ungehindert(self):
        for gelenk in (LINKS, RECHTS):
            with self.subTest(gelenk=Smplskelett.NAMEN[gelenk]):
                feld = Arm.feld(gelenk, Rotation.from_rotvec(np.radians(140) * BEUGEACHSE[gelenk]))
                vorher = feld.copy()
                self.assertEqual(Gelenkgrenzen.anwenden(feld, np), 0)
                np.testing.assert_allclose(feld, vorher)
                self.assertAlmostEqual(Arm.beugung(feld, gelenk), 140.0, places=3)

    def test_schwenkung_ueber_150_grad_wird_gekappt(self):
        feld = Arm.feld(LINKS, Rotation.from_rotvec(np.radians(170) * BEUGEACHSE[LINKS]))
        self.assertEqual(Gelenkgrenzen.anwenden(feld, np), 1)
        self.assertAlmostEqual(Arm.beugung(feld, LINKS), 150.0, places=3)

    def test_verdrehung_um_die_armachse_wird_auf_90_gekappt(self):
        achse = Arm.achse(LINKS)
        beugung = Rotation.from_rotvec(np.radians(60) * BEUGEACHSE[LINKS])
        feld = Arm.feld(LINKS, beugung * Rotation.from_rotvec(np.radians(130) * achse))
        self.assertEqual(Gelenkgrenzen.anwenden(feld, np), 1)
        w, x, y, z = feld[0, LINKS]
        neu = Rotation.from_quat([x, y, z, w])
        # Der Anteil um die Achse ist jetzt 90 Grad, die Beugung unveraendert 60.
        q = neu.as_quat()
        anteil = np.dot(q[:3], achse)
        dreh = np.array([*(anteil * achse), q[3]])
        dreh /= np.linalg.norm(dreh)
        self.assertAlmostEqual(np.degrees(2 * np.arctan2(np.dot(dreh[:3], achse), dreh[3])), 90.0, places=3)
        self.assertAlmostEqual(Arm.beugung(feld, LINKS), 60.0, places=3)
