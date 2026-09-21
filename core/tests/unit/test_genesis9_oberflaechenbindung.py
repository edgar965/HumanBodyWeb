# -*- coding: utf-8 -*-
u"""`G9oberflaechenbindung` (Konzept Fitting, Schicht 2, 21.09.2026) — an Kunstdaten.

Eine Ebene z = 0 aus 3 × 3 Punkten (8 Dreiecke, Normalen +z), Stoffpunkte
darueber und darunter:

1. Ein Punkt ueber dem Inneren eines Dreiecks bekommt DIESES Dreieck, die
   Baryzentrik trifft seinen Fusspunkt, der Abstand ist sein Hoehenversatz —
   mit Vorzeichen (5 mm unter der Ebene: −0,005).
2. `mischung`: 1 bis `NAH_M`, dazwischen linear, 0 ab `FERN_M`; ein Punkt
   jenseits `FERN_M` traegt Dreieck −1.
3. Die Formel des Shaders (q = Σ bary·Ecke + d·n) stellt den Ruhepunkt exakt
   wieder her — sonst spraenge der Stoff beim Einschalten der Bindung.
4. Ein Punkt seitlich neben der Flaeche (kein Dreieck darunter) haengt an
   der naechsten Kante, nicht an einem falschen Inneren.

Sabotage-Gegenprobe: in `_naechster_punkt` die Zuweisung von Bereich 1
(Ecke A) streichen → Fall 4 rot (Baryzentrik liegt ausserhalb).
"""
import numpy as np
from django.test import SimpleTestCase
from scipy.spatial import cKDTree

from Genesis9.oberflaechenbindung import G9oberflaechenbindung


def _ebene():
    xs, ys = np.meshgrid([0, 1, 2], [0, 1, 2])
    P = np.stack([xs.ravel(), ys.ravel(), np.zeros(9)], axis=1).astype(float)
    N = np.tile([0, 0, 1.0], (9, 1))
    D = []
    for j in range(2):
        for i in range(2):
            a = j * 3 + i
            D += [[a, a + 1, a + 4], [a, a + 4, a + 3]]
    return G9oberflaechenbindung(P, N, np.array(D), cKDTree(P.astype(np.float32)), stufen=1), P, N


class OberflaechenbindungTest(SimpleTestCase):
    databases = set()

    def test_1_dreieck_baryzentrik_abstand(self):
        ob, P, _N = _ebene()
        b = ob.fuer(np.array([[0.3, 0.2, 0.01], [1.5, 1.5, -0.005]]))
        self.assertEqual(list(b['dreieck'][0]), [0, 1, 4])
        q = (b['bary'][0][:, None] * P[b['dreieck'][0]]).sum(0)
        np.testing.assert_allclose(q, [0.3, 0.2, 0.0], atol=1e-6)
        self.assertAlmostEqual(float(b['abstand'][0]), 0.01, places=6)
        self.assertAlmostEqual(float(b['abstand'][1]), -0.005, places=6)
        self.assertEqual(b['stufen'], 1)

    def test_2_mischung_nah_fern(self):
        ob, _P, _N = _ebene()
        b = ob.fuer(np.array([[1.0, 1.0, 0.01], [1.0, 1.0, 0.05], [1.0, 1.0, 0.2]]))
        self.assertEqual(float(b['mischung'][0]), 1.0)
        erwartet = (ob.FERN_M - 0.05) / (ob.FERN_M - ob.NAH_M)
        self.assertAlmostEqual(float(b['mischung'][1]), erwartet, places=5)
        self.assertEqual(float(b['mischung'][2]), 0.0)
        self.assertEqual(list(b['dreieck'][2]), [-1, -1, -1])

    def test_3_formel_stellt_die_ruhe_wieder_her(self):
        ob, P, N = _ebene()
        rng = np.random.default_rng(3)
        S = np.column_stack([rng.uniform(0.05, 1.95, 50), rng.uniform(0.05, 1.95, 50),
                             rng.uniform(-0.01, 0.02, 50)])
        b = ob.fuer(S)
        e = b['dreieck'].astype(int)
        q = np.einsum('kc,kcj->kj', b['bary'], P[e]) + b['abstand'][:, None] * N[e[:, 0]]
        np.testing.assert_allclose(q, S, atol=1e-5)

    def test_4_neben_der_flaeche_haengt_der_punkt_an_der_kante(self):
        ob, P, _N = _ebene()
        b = ob.fuer(np.array([[2.02, 1.0, 0.0]]))       # 2 cm neben der Kante x = 2
        self.assertTrue(np.all(b['bary'][0] >= -1e-6) and np.all(b['bary'][0] <= 1 + 1e-6))
        q = (b['bary'][0][:, None] * P[b['dreieck'][0]]).sum(0)
        np.testing.assert_allclose(q, [2.0, 1.0, 0.0], atol=1e-6)
