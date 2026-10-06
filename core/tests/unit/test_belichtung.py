# -*- coding: utf-8 -*-
"""`Belichtung` (06.10.2026): die Helligkeit des Renders je Ansicht an das Foto angleichen, das Mittel über alle Ansichten bleibt.

Kunstbilder, keine Datenbank; Dateien nur unter `ProjektTemp/pruefungen` (`Pruefablage`). Nicht als Suite gelaufen (`testsuite-nur-auf-ansage`); ohne Django nachgerechnet mit `ProjektTemp/_wegwerf/edgar/belichtung_test_probe.py` (5 Fälle grün).

Sabotage: in `Belichtung.faktoren` das geometrische Mittel weglassen (`mittel = 1.0`) → Fall 1 rot (das Mittel bliebe nicht 1: ein überall zu dunkles Modell sähe die Note nicht mehr); `linear` durch die rohen sRGB-Werte
ersetzen → Fall 2 rot (der Faktor stimmt nur im Licht, nicht in der Bildhelligkeit).
"""

import numpy as np
from django.test import SimpleTestCase
from iterationen2d3d.belichtung import Belichtung
from PIL import Image

from ._pruefablage import Pruefablage


class _Bild:
    """Was `Belichtung.faktoren` von einem `Iterationsbild` liest: `farbe` (H, B, 3) sRGB 0…1 und `maske` (H, B) bool."""

    def __init__(self, farbe, maske):
        self.farbe, self.maske = farbe, maske


def _bild(grau, hoehe=60, breite=40):
    """Eine Figur (Mittelstreifen) in einem Grauwert (linear), Rest leer."""
    farbe = np.zeros((hoehe, breite, 3), np.float32)
    maske = np.zeros((hoehe, breite), bool)
    maske[5:55, 10:30] = True
    farbe[maske] = float(Belichtung.srgb(grau))
    return _Bild(farbe, maske)


class DieBelichtung(SimpleTestCase):
    def test_1_die_unterschiede_gehen_das_mittel_bleibt(self):
        # Foto je Ansicht in drei Helligkeiten (linear 0,10 / 0,10 / 0,16), der Render überall 0,10: Faktoren 0,86 / 0,86 / 1,38 — nur der Unterschied zwischen den Ansichten.
        ansichten = [(_bild(g), _bild(0.10), True) for g in (0.10, 0.10, 0.16)]
        f = Belichtung.faktoren(ansichten)
        self.assertAlmostEqual(float(np.exp(np.mean(np.log(f)))), 1.0, places=6)           # das geometrische Mittel bleibt 1
        self.assertAlmostEqual(f[0], f[1], places=6)
        self.assertAlmostEqual(f[2] / f[0], 1.6, places=3)                                  # das hellere Foto bekommt das 1,6-fache
        # Ist der Render überall zu dunkel (Foto 0,2 gegen Render 0,1 in allen Ansichten), gibt es nichts abzugleichen: das Mittel bleibt, jeder Faktor ist 1.
        gleich = Belichtung.faktoren([(_bild(0.2), _bild(0.1), True)] * 3)
        for w in gleich:
            self.assertAlmostEqual(w, 1.0, places=6)

    def test_2_helligkeit_wird_im_licht_gemessen(self):
        # Das Foto 1,5-mal so hell im LICHT (0,321 gegen 0,214; als sRGB-Wert wäre das Verhältnis ein anderes) gegen ein gleich helles: im Mittel 1, also sqrt(1,5) und 1 / sqrt(1,5).
        f = Belichtung.faktoren([(_bild(0.321), _bild(0.214), True), (_bild(0.214), _bild(0.214), True)])
        self.assertAlmostEqual(f[0], 1.5 ** 0.5, places=2)
        self.assertAlmostEqual(f[1], 1.5 ** -0.5, places=2)

    def test_3_ansichten_ohne_farbe_und_einzelne_zaehlen_nicht(self):
        f = Belichtung.faktoren([(_bild(0.3), _bild(0.1), True), (_bild(0.1), _bild(0.1), True), (_bild(0.9), _bild(0.1), False)])
        self.assertEqual(f[2], 1.0)                                                         # andere Kleidung: Faktor 1
        self.assertGreater(f[0], f[1])
        # Nur eine zählende Ansicht: kein Mittel, kein Abgleich.
        self.assertEqual(Belichtung.faktoren([(_bild(0.3), _bild(0.1), True), (_bild(0.1), _bild(0.1), False)]), [1.0, 1.0])
        # Zu wenig gemeinsame Figur: nicht messbar.
        klein = _Bild(np.zeros((60, 40, 3), np.float32), np.zeros((60, 40), bool))
        self.assertEqual(Belichtung.faktoren([(klein, _bild(0.1), True), (_bild(0.1), _bild(0.1), True)]), [1.0, 1.0])

    def test_4_die_faktoren_sind_begrenzt(self):
        f = Belichtung.faktoren([(_bild(0.9), _bild(0.01), True), (_bild(0.01), _bild(0.01), True)])
        self.assertLessEqual(max(f), Belichtung.GRENZEN[1] + 1e-9)
        self.assertGreaterEqual(min(f), Belichtung.GRENZEN[0] - 1e-9)

    def test_5_anwenden_rechnet_im_licht_und_laesst_alpha(self):
        with Pruefablage.ordner() as ordner:
            pfad = ordner + '/ansicht.png'
            rgba = np.zeros((4, 4, 4), np.uint8)
            rgba[..., :3] = 128
            rgba[..., 3] = 255
            rgba[0, 0, 3] = 0
            Image.fromarray(rgba, 'RGBA').save(pfad)
            self.assertFalse(Belichtung.anwenden(pfad, 1.002))                              # unter dem Totband: Datei bleibt
            self.assertTrue(Belichtung.anwenden(pfad, 1.3))
            neu = np.asarray(Image.open(pfad).convert('RGBA'))
        erwartet = float(Belichtung.srgb(Belichtung.linear(128 / 255.0) * 1.3)) * 255.0
        self.assertAlmostEqual(float(neu[2, 2, 0]), erwartet, delta=1.0)
        self.assertEqual(int(neu[0, 0, 3]), 0)                                              # Alpha unverändert
        self.assertEqual(int(neu[2, 2, 3]), 255)
