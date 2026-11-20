# -*- coding: utf-8 -*-
"""Ausreißer-Filter des Video-BVH: Sprünge der Wurzel werden vor dem Glätten herausgenommen (`Bvhausreisser`).

DER ANLASS (20.11.2026, Edgar „mach alles, auch video-BVH“): `A_Results/DanceKurz.bvh` springt in Bild 272 mit der Hüfte
34 cm in einem Bild und dreht sie in 727–729 je Bild um 33–40° — die Seite zeigte den Sprung, Stoff und Haar der Kette
flogen davon. Der Erkenner rechnet mit 30 fps, die Bahn steht bei 60 fps paarweise; echte Bewegung in jedem zweiten Bild ist
KEIN Sprung (mit dem Median der Einzelschritte nahm der Filter 52 echte Schritte heraus).

BDD - GEGEBEN / DANN
====================
    EinSprung           ... im Ort wird erkannt und entfernt, alles danach rückt um den Sprung zurück, davor bitgleich
    EineDrehkippe       ... (drei Bilder je 40°) wird erkannt; danach dreht die Wurzel weiter wie vorher
    PaarweiseBilder     ... (30 fps auf 60 fps verdoppelt) und eine anhaltende Pirouette bleiben unangetastet

Läuft nur auf Ansage (Regel „Tests nur auf Ansage“). Nicht gelaufen beim Schreiben (20.11.2026).
"""

import math
import unittest

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import torch  # noqa: E402
from bvhausreisser import Bvhausreisser  # noqa: E402

KARTE = 'cuda' if torch.cuda.is_available() else 'cpu'  # cpu gewollt: Test auch ohne Karte lesbar


def _um_y(grad):
    """(N,) Winkel in Grad → (N, 4) Quaternionen [w,x,y,z] um die Hochachse."""
    h = torch.as_tensor(grad, dtype=torch.float64, device=KARTE) * (math.pi / 360.0)
    null = torch.zeros_like(h)
    return torch.stack([torch.cos(h), null, torch.sin(h), null], -1)


def _gehen(n=120, fps=60.0, m_s=1.0):
    """Hüfte geht gleichmäßig in x (Meter), Drehung 90°/s um y."""
    t = torch.arange(n, dtype=torch.float64, device=KARTE) / fps
    p = torch.stack([t * m_s, torch.full_like(t, 0.9), torch.zeros_like(t)], -1)
    return _um_y(t * 90.0), p


class EinSprung(unittest.TestCase):
    def test_sprung_im_ort_entfernt(self):
        q, p = _gehen()
        p[60:, 0] += 0.34                                                  # 34 cm in einem Bild wie DanceKurz 272
        q2, p2, schritte = Bvhausreisser(60.0).anwenden(q, p, 1.0)
        self.assertEqual(schritte, [60])
        self.assertTrue(torch.equal(p2[:60], p[:60]))
        weg = (p2[1:] - p2[:-1]).norm(dim=-1) * 60.0
        self.assertLess(float(weg.max()), 1.01)
        self.assertAlmostEqual(float(p2[-1, 0] - p[-1, 0]), -0.34, places=6)  # der Schritt wird zum Nachbarschritt (1/60 m), der Sprung fällt weg

    def test_sabotage_ohne_sprung_nichts(self):
        q, p = _gehen()
        _, _, schritte = Bvhausreisser(60.0).anwenden(q, p, 1.0)
        self.assertEqual(schritte, [])


class EineDrehkippe(unittest.TestCase):
    def test_drei_bilder_je_40_grad(self):
        q, p = _gehen()
        grad = torch.arange(120, dtype=torch.float64, device=KARTE) * 1.5
        grad[70:] += 40.0
        grad[71:] += 40.0
        grad[72:] += 40.0
        q = _um_y(grad)
        q2, _, schritte = Bvhausreisser(60.0).anwenden(q, p, 1.0)
        self.assertEqual(schritte, [70, 71, 72])
        f = Bvhausreisser(60.0)
        sprung, _, grad_s, _ = f.spruenge(q2, p, 1.0)
        self.assertFalse(bool(sprung.any()))
        self.assertLess(float(grad_s.max()), 91.0)


class PaarweiseBilder(unittest.TestCase):
    def test_30fps_verdoppelt_bleibt(self):
        q, p = _gehen(m_s=3.0)
        p[1::2] = p[0::2][:p[1::2].shape[0]]                                # jedes Bild doppelt: 6 m/s in jedem zweiten Schritt
        _, _, schritte = Bvhausreisser(60.0).anwenden(q, p, 1.0)
        self.assertEqual(schritte, [])

    def test_pirouette_bleibt(self):
        t = torch.arange(240, dtype=torch.float64, device=KARTE) / 60.0
        grad = torch.where(t < 1.0, t * 90.0, 90.0 + (t - 1.0) * 1500.0)  # ab 1 s anhaltend 1.500°/s
        q = _um_y(grad)
        _, p = _gehen(240)
        _, _, schritte = Bvhausreisser(60.0).anwenden(q, p, 1.0)
        self.assertEqual(schritte, [])


if __name__ == '__main__':
    unittest.main()
