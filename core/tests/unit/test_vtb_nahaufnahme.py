# -*- coding: utf-8 -*-
"""Nahaufnahme: die Kamera eines Detailbilds aus dem Rig, gegen das Ganzkörpernetz (19.09.2026).

Edgar: „mach ca. 10 Nahaufnahmen von Ursula mit HD aus unterschiedlichen
Winkeln". SMPLest-X schätzt auf einer Nahaufnahme einen ganzen Körper; hier
wird die Kamera per PnP aus den Rig-Punkten gefunden. Kunstdaten: Zielfelder
(COCO 17, Füße 6, Hände, Gesicht 68 — seit dem 20.09. ein Wörterbuch, das
`G9texturmodell` aus dem Genesis-Modell liefert; hier zufällige Punkte, das
Kinn NaN wie beim SMPL-X-Feld), eine bekannte Kamera (f = 1,9 × Kante,
gedreht, verschoben) projiziert Gelenke, Gesicht und Füße ins Bild.

1. `paare`: COCO-17 + Füße + 51 Gesichtspunkte → 74 Paare; unsichere Punkte
   (Güte < 0,3) fallen weg; ohne Rig keine Paare.
2. `registrieren` findet R, t und f wieder (goldener Schnitt um die beste
   Brennweite): Reprojektion unter 1 px, Lage im Kameraraum auf 1 % der
   Entfernung, Brennweite auf 1 %.
3. Sabotage: vertauschte Bildpunkte (links ↔ rechts, alle) → keine Kamera oder
   ein Fehler, der die Schwelle reißt — in keinem Fall die richtige Kamera.
"""

import unittest

import numpy as np

from core.tests.unit._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from nahaufnahme import Nahaufnahme  # noqa: E402

N = 10475


def _modell(rng):
    punkte = rng.normal(size=(N, 3)) * 0.3
    punkte[:, 1] = rng.uniform(0.0, 1.7, N)

    def feld(n):
        return punkte[rng.integers(0, N, size=n)]

    gesicht = feld(68)
    gesicht[:17] = np.nan                       # Kinnbogen unbekannt (wie beim SMPL-X-Feld)
    ziele = {'coco': feld(17), 'fuesse': feld(6), 'hand_l': feld(21), 'hand_r': feld(21), 'gesicht': gesicht}
    return Nahaufnahme(ziele), punkte


def _kamera(breite, hoehe, f):
    w = np.radians(25.0)
    rot = np.array([[np.cos(w), 0, np.sin(w)], [0, 1, 0], [-np.sin(w), 0, np.cos(w)]])
    t = np.array([0.1, -0.85, 3.0])
    k = np.array([[f, 0, breite / 2], [0, f, hoehe / 2], [0, 0, 1.0]])
    return rot, t, k


def _rig(nah, punkte, rot, t, k, breite, hoehe, rng):
    welt = np.concatenate([nah.ziele['coco'], nah.ziele['fuesse'], nah.ziele['gesicht'][17:]])
    cam = welt @ rot.T + t
    px = cam @ k.T
    px = px[:, :2] / px[:, 2:3]
    px += rng.normal(scale=0.3, size=px.shape)
    norm = [[float(x / breite), float(y / hoehe), 0.95] for x, y in px]
    ganz = norm[:17] + norm[17:23] + [[0.0, 0.0, 0.0]] * 17 + norm[23:74] + [[0.0, 0.0, 0.0]] * 42
    return {'openpifpaf': {'punkte': ganz}}, cam


class NahaufnahmeTest(unittest.TestCase):
    def setUp(self):
        import cv2

        cv2.setRNGSeed(7)
        self.rng = np.random.default_rng(3)
        self.nah, self.punkte = _modell(self.rng)
        self.breite, self.hoehe = 2400, 2400
        self.f = 1.9 * 2400
        self.rot, self.t, self.k = _kamera(self.breite, self.hoehe, self.f)
        self.rigs, self.cam = _rig(self.nah, self.punkte, self.rot, self.t, self.k, self.breite, self.hoehe,
                                   self.rng)

    def test_1_paare(self):
        bild, welt = self.nah.paare(self.rigs, self.breite, self.hoehe)
        self.assertEqual(len(bild), 17 + 6 + 51)
        self.assertEqual(welt.shape, (74, 3))
        unsicher = {'openpifpaf': {'punkte': [[p[0], p[1], 0.1] for p in self.rigs['openpifpaf']['punkte']]}}
        self.assertEqual(len(self.nah.paare(unsicher, self.breite, self.hoehe)[0]), 0)
        self.assertEqual(len(self.nah.paare({}, self.breite, self.hoehe)[0]), 0)
        # Unbekannte Ziele (NaN) bilden kein Paar: ohne Gesichtsfeld nur Körper und Füße.
        ohne = Nahaufnahme({k: v for k, v in self.nah.ziele.items() if k != 'gesicht'})
        self.assertEqual(len(ohne.paare(self.rigs, self.breite, self.hoehe)[0]), 23)

    def test_2_registrieren(self):
        reg = self.nah.registrieren(self.rigs, self.breite, self.hoehe)
        self.assertIsNotNone(reg)
        self.assertGreaterEqual(reg['punkte'], 70)
        self.assertLess(reg['fehler_px'], 1.5)
        self.assertAlmostEqual(reg['fx'] / self.f, 1.0, delta=0.01)
        lage = Nahaufnahme.anwenden(reg, self.punkte)
        abstand = np.linalg.norm(lage - (self.punkte @ self.rot.T + self.t), axis=1)
        self.assertLess(float(np.median(abstand)), 0.01 * 3.0, 'Lage im Kameraraum auf 1 % der Entfernung')

    def test_3_sabotage_gespiegelt(self):
        p = [[1.0 - x, y, g] for x, y, g in self.rigs['openpifpaf']['punkte']]
        reg = self.nah.registrieren({'openpifpaf': {'punkte': p}}, self.breite, self.hoehe)
        if reg is not None:
            lage = Nahaufnahme.anwenden(reg, self.punkte)
            abstand = np.linalg.norm(lage - (self.punkte @ self.rot.T + self.t), axis=1)
            self.assertGreater(float(np.median(abstand)), 0.2, 'gespiegeltes Rig: nicht die richtige Kamera')
