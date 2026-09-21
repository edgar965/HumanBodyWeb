# -*- coding: utf-8 -*-
"""T1 — Käfig in der Pose des Fotos (21.09.2026): `G9netzwickel`, `Posefeinabgleich.paare`.

Konzept `Docu/konzepte/2026-09-20_modell-aus-bildern-regler-und-textur.md`: Die Fototextur
projizierte den Käfig in Ruhehaltung gegen Fotos in Pose. Jetzt wird der Käfig an das
SMPL-X in A-Pose gebunden und auf das posierte SMPL-X des Fotos übertragen. Ohne
Bibliothek, ohne Schätzer:

1. `G9netzwickel.normiert`: Füße auf 0, Höhe 1, x/z um den Schwerpunkt der Füße.
2. `binden` + `anwenden` auf dem SELBEN Netz ist die Identität (Selbstprobe wie an
   Damira: 0,0 mm); ein Punkt ÜBER einem Dreieck behält seinen Abstand entlang der
   Normale; nach einer starren Drehung des Ziels folgt er ihr (Sabotage: ohne
   Normalenanteil läge er auf der Fläche).
3. `Posefeinabgleich.paare`: openpifpaf 133 gibt Körper + Füße + Hände, Punkte unter
   der Güte fallen weg; ohne openpifpaf nur COCO-17 aus dem sichersten Rig.
"""

import unittest

import numpy as np
from Genesis9.netzwickel import G9netzwickel

from core.tests.unit._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from posefeinabgleich import Posefeinabgleich  # noqa: E402


def _kasten():
    """Ein Quader 1 × 2 × 0,5 (Füße auf 0), zwölf Dreiecke."""
    p = np.array([[0, 0, 0], [1, 0, 0], [1, 2, 0], [0, 2, 0],
                  [0, 0, .5], [1, 0, .5], [1, 2, .5], [0, 2, .5]], dtype=float)
    f = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4],
                  [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])
    return p, f


class NetzwickelTest(unittest.TestCase):
    def test_1_normiert(self):
        p, _ = _kasten()
        n, hoehe, mitte = G9netzwickel.normiert(p + [3.0, 1.0, 2.0])
        self.assertAlmostEqual(hoehe, 2.0)
        self.assertAlmostEqual(float(n[:, 1].min()), 0.0)
        self.assertAlmostEqual(float(n[:, 1].max()), 1.0)
        self.assertAlmostEqual(float(mitte[1]), 1.0)

    def test_2_selbstprobe_und_abstand(self):
        p, f = _kasten()
        w = G9netzwickel.binden(p, f, p)
        zurueck = w.anwenden(p, f, 1.0)
        self.assertLess(float(np.abs(zurueck - p).max()), 1e-9)
        # Ein Punkt 0,05 vor der Vorderseite (z = 0,5 + 0,05): Abstand entlang der Normale
        vor = np.array([[0.5, 1.0, 0.55]])
        wv = G9netzwickel.binden(p, f, vor)
        self.assertAlmostEqual(float(abs(wv.abstand[0])), 0.05, places=6)
        self.assertFalse(bool(wv.weit[0]))
        # Ziel um 90° um y gedreht: der Punkt folgt (Sabotage: ohne Normalenanteil auf der Fläche)
        R = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], dtype=float)
        ziel = p @ R.T
        mit = wv.anwenden(ziel, f, 1.0)[0]
        self.assertTrue(np.allclose(mit, vor[0] @ R.T, atol=1e-9))
        ohne = G9netzwickel(wv.dreieck, wv.bary, np.zeros(1), wv.weit).anwenden(ziel, f, 1.0)[0]
        self.assertAlmostEqual(float(np.linalg.norm(mit - ohne)), 0.05, places=6)
        # Massstab 2: der Abstand verdoppelt sich
        gross = wv.anwenden(ziel, f, 2.0)[0]
        self.assertAlmostEqual(float(np.linalg.norm(gross - ohne)), 0.1, places=6)
        # weit: ein Punkt 0,5 entfernt (> WEIT = 0,06) wird gemeldet
        self.assertTrue(bool(G9netzwickel.binden(p, f, np.array([[0.5, 1.0, 1.0]])).weit[0]))


class PaareTest(unittest.TestCase):
    def test_3_paare(self):
        ganz = [[0.1 * (i % 10), 0.05 * (i % 20), 0.9] for i in range(133)]
        ganz[3] = [0.0, 0.0, 0.1]                      # unsicheres Ohr
        rig = {'rigs': {'openpifpaf': {'punkte': ganz}, 'yolo': {'punkte': ganz[:17]}}}
        gelenke, bild, sicher = Posefeinabgleich.paare(rig, 200, 100)
        self.assertEqual(len(gelenke), 16 + 6 + 42)
        self.assertEqual(bild.shape, (64, 2))
        self.assertNotIn(Posefeinabgleich.COCO[3], gelenke.tolist())
        self.assertAlmostEqual(float(bild[0, 0]), 0.0)
        self.assertAlmostEqual(float(bild[1, 0]), 20.0)
        self.assertAlmostEqual(float(bild[1, 1]), 5.0)
        # Ohne openpifpaf: nur die 17 aus dem sichersten Rig
        g2, _, _ = Posefeinabgleich.paare({'rigs': {'yolo': {'punkte': ganz[:17]}}}, 200, 100)
        self.assertEqual(len(g2), 16)
        self.assertEqual(len(Posefeinabgleich.paare({}, 200, 100)[0]), 0)


if __name__ == '__main__':
    unittest.main()
