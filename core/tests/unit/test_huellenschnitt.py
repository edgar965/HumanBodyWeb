# -*- coding: utf-8 -*-
u"""Huellenschnitt (02.10.2026 nachts, Befund Edgar „Ausschnitt, Ärmel- und Hosensaum gezackt") — Kunstnetze, keine
Grafikkarte.

1. `schneiden`: ein Dreieck mit einer Ecke innen wird an der Linie 0,5 geteilt — die neuen Punkte liegen genau dort.
2. `feld` + `schneiden` auf einem Zylinder mit gezackter Wahl (Treppe aus Flächen, ±3 Ringe): der Saum liegt danach in
   einer Ebene (Höhenspanne < 5 mm).
3. `halsgewichte`: Gewicht von `neck1` und seinen Kindern je Punkt, andere Knochen zählen nicht.

Sabotage: in `schneiden` `t` fest auf 0,5 → Fall 1 rot; `halsgewichte` ohne Kinder → Fall 3 rot.
"""
import numpy as np
from django.test import SimpleTestCase

from core.dienste.huellenschnitt import Huellenschnitt


def zylinder(ringe=40, um=32, hoehe=0.8, radius=0.08):
    w = np.linspace(0, 2 * np.pi, um, endpoint=False)
    y = np.linspace(0, hoehe, ringe)
    punkte = np.array([[radius * np.cos(a), h, radius * np.sin(a)] for h in y for a in w])
    flaechen = []
    for r in range(ringe - 1):
        for i in range(um):
            a, b = r * um + i, r * um + (i + 1) % um
            c, d = a + um, b + um
            flaechen += [[a, b, d], [a, d, c]]
    return punkte, np.array(flaechen)


class _Datei:
    def __init__(self, **werte):
        self.werte = werte
        self.files = list(werte)

    def __getitem__(self, k):
        return self.werte[k]


class HuellenschnittTest(SimpleTestCase):
    databases = set()

    def test_1_schneiden_teilt_an_der_linie(self):
        lagen = np.array([[0.0, 0.0, 0.0, 1.0], [1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]])
        neu, flaechen = Huellenschnitt(np.zeros((1, 3)), np.zeros((0, 3), int)).schneiden(lagen, np.array([[0, 1, 2]]),
                                                                                           3)
        self.assertEqual(len(flaechen), 1)
        self.assertTrue(np.allclose(sorted(neu[:, 0].round(3)), [0.0, 0.0, 0.5]))
        self.assertTrue(np.allclose(neu[:, 3][neu[:, 3] < 1.0], 0.5))

    def _saum(self, eben_rms):
        punkte, flaechen = zylinder()
        um = 32
        ring = np.arange(len(flaechen)) // (2 * um)
        spalte = (np.arange(len(flaechen)) // 2) % um
        grenze = 20 + np.where(spalte % 4 < 2, 3, -3)                    # gezackt: ±3 Ringe je zwei Spalten
        wahl = ring >= grenze
        s = Huellenschnitt(punkte, flaechen)
        s.EBEN_RMS = eben_rms
        feld = s.feld(wahl)
        lagen = np.hstack([punkte, feld[:, None]])
        nah = (feld[flaechen] >= s.SCHNITT).any(axis=1)
        neu, f = s.schneiden(lagen, flaechen[nah], 3)
        rand = np.abs(neu[:, 3] - s.SCHNITT) < 1e-6
        return np.ptp(neu[rand, 1])

    def test_2_saum_wird_eben(self):
        self.assertLess(self._saum(Huellenschnitt.EBEN_RMS), 0.005)

    def test_3_halsgewichte_nur_hals_und_kinder(self):
        datei = _Datei(knochen=np.array(['hip', 'spine4', 'neck1', 'neck2', 'head', 'l_shoulder']),
                       eltern=np.array([-1, 0, 1, 2, 3, 1]),
                       haut_index=np.array([[2, 1, -1, -1], [4, 5, -1, -1], [0, -1, -1, -1]]),
                       haut_gewicht=np.array([[0.3, 0.7, 0, 0], [0.6, 0.4, 0, 0], [1.0, 0, 0, 0]]))
        self.assertTrue(np.allclose(Huellenschnitt.halsgewichte(datei), [0.3, 0.6, 0.0]))
        self.assertIsNone(Huellenschnitt.halsgewichte(_Datei(punkte=np.zeros((1, 3)))))
