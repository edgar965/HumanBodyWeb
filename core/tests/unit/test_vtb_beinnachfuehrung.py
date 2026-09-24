# -*- coding: utf-8 -*-
"""Beinnachfuehrung: Huefte und Knie an ViTPose-Punkte, ohne durch die Arme.

Befund Edgar (24.09.2026, Dance1 Bild 49): „der Arm kommt viel zu nahe zum
Bein". GEM legte das gehobene Bein 390 px unter die ViTPose-Punkte.

EICHFALL MIT BEKANNTER WAHRHEIT: ein Kunstskelett (22 Gelenke, Arme waagrecht
— haengende Arme laegen dem seitlich gehobenen Bein im Weg, und der Armterm
wuerde den Fall verfaelschen),
die Wahrheit hebt das rechte Bein um 70 Grad zur Seite, die Bahn steht in
Ruhe. Die ViTPose-Punkte sind die Projektion der Wahrheit.

1. Das rechte Bein trifft danach die Punkte (Fehler < 20 % von vorher).
2. Das linke Bein (Punkte passen) bleibt Zahl fuer Zahl, wie es war.
3. Unsichere Punkte (Sicherheit 0,3) aendern nichts.
4. `durchdringung` meldet einen Armpunkt an der Oberschenkelachse, einen
   fernen nicht.

Fall 1 fand beim ersten Lauf (24.09.2026) einen echten Fehler: Die
Tausch-Pruefung verglich nur das eigene Modellbein mit den Punkten des
anderen Beins — bei einem gehobenen Bein gleicht das ruhende Modellbein dem
ruhenden anderen, und alle 5 Bilder galten als vertauscht. Jetzt muessen
beide Beine ueber Kreuz besser passen.

Sabotage-Gegenproben (gelaufen 24.09.2026, `ProjektTemp/armbein/sabotage.py`):
`SCHWELLE` auf 99 -> Fall 1 rot; `MINDESTSICHERHEIT` auf 0 -> Fall 3 rot; in
`durchdringung` `np.maximum` durch `np.minimum` -> Fall 4 rot (und Fall 1).
"""

import unittest

import numpy as np
from scipy.spatial.transform import Rotation

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from beinnachfuehrung import Beinnachfuehrung  # noqa: E402
from smplxbahn import Smplxbahn  # noqa: E402

#: Ruhegelenke (m, y oben) — Becken, Hueften, Wirbel, Knie, Knoechel, Fuesse,
#: Hals, Schluesselbeine, Kopf, Schultern, Ellbogen, Handgelenke.
J = np.array([
    [0, 0, 0], [0.1, -0.1, 0], [-0.1, -0.1, 0], [0, 0.1, 0],
    [0.1, -0.5, 0], [-0.1, -0.5, 0], [0, 0.2, 0], [0.1, -0.9, 0],
    [-0.1, -0.9, 0], [0, 0.3, 0], [0.1, -0.95, 0.1], [-0.1, -0.95, 0.1],
    [0, 0.5, 0], [0.05, 0.45, 0], [-0.05, 0.45, 0], [0, 0.6, 0],
    [0.18, 0.45, 0], [-0.18, 0.45, 0], [0.45, 0.45, 0], [-0.45, 0.45, 0],
    [0.7, 0.45, 0], [-0.7, 0.45, 0]], dtype=np.float64)
BILDER = 5
RECHTS = Beinnachfuehrung.BEINE[1]


class Testnachfuehrung(Beinnachfuehrung):
    """Ohne SMPL-X-Modell: die Ruhegelenke des Kunstskeletts."""

    def ruhegelenke(self):
        return J.copy()


class TestBeinnachfuehrung(unittest.TestCase):
    """Eichfall: rechtes Bein zur Seite gehoben, Bahn in Ruhe."""

    @staticmethod
    def bahn():
        bahn = Smplxbahn(BILDER, 30.0, np)
        bahn.global_orient[:] = Rotation.from_euler('x', 180, degrees=True).as_rotvec()
        bahn.transl[:] = [0.0, 0.0, 3.0]
        bahn.K = np.array([[1000, 0, 500], [0, 1000, 500], [0, 0, 1]], dtype=np.float32)
        return bahn

    def punkte(self, sicherheit=0.9):
        """COCO-17 aus der Wahrheit: rechte Huefte 70 Grad zur Seite."""
        wahr = self.bahn()
        wahr.body_pose[:, 1] = [0.0, 0.0, np.radians(-70)]
        nf = Testnachfuehrung(wahr, np)
        nf.K, nf.J = np.asarray(wahr.K, dtype=np.float64), J
        punkte = np.zeros((BILDER, 17, 3))
        for bild in range(BILDER):
            for _, gelenke, posen, coco in Beinnachfuehrung.BEINE:
                p = nf.bein(bild, gelenke, *(wahr.body_pose[bild, i].astype(float) for i in posen))
                punkte[bild, list(coco), :2] = nf.projizieren(p)
                punkte[bild, list(coco), 2] = sicherheit
        return punkte

    def test_rechtes_bein_trifft_die_punkte(self):
        bahn = self.bahn()
        bilanz = Testnachfuehrung(bahn, np).anwenden(self.punkte())
        vorher, nachher = bilanz['rechts']['fehler_px']
        self.assertEqual(bilanz['rechts']['bilder'], BILDER)
        self.assertLess(nachher, 0.2 * vorher)

    def test_linkes_bein_bleibt(self):
        bahn = self.bahn()
        Testnachfuehrung(bahn, np).anwenden(self.punkte())
        np.testing.assert_array_equal(bahn.body_pose[:, 0], 0.0)
        np.testing.assert_array_equal(bahn.body_pose[:, 3], 0.0)

    def test_unsichere_punkte_aendern_nichts(self):
        bahn = self.bahn()
        bilanz = Testnachfuehrung(bahn, np).anwenden(self.punkte(sicherheit=0.3))
        self.assertEqual(bilanz['rechts']['bilder'], 0)
        np.testing.assert_array_equal(bahn.body_pose, 0.0)

    def test_durchdringung_nah_und_fern(self):
        nf = Testnachfuehrung(self.bahn(), np)
        bein = np.array([[0.0, 0, 0], [0, -0.4, 0], [0, -0.8, 0]])
        arm = np.array([[0.05, -0.2, 0], [0.5, -0.2, 0]])
        fehl = nf.durchdringung(bein, arm)
        self.assertAlmostEqual(fehl[0], Beinnachfuehrung.ARMABSTAND_M - 0.05)
        self.assertEqual(fehl[1], 0.0)
