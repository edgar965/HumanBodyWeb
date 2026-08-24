# -*- coding: utf-8 -*-
"""Rockradien — die Durchdringungsrechnung an gebauten Zylindern.

WARUM DIESER TEST (17.08.2026)
=============================
Die beiden Bake-Prüfungen in `tests/cloth_engine_tests.py` suchten ihre Datei in
`C:\\Users\\…\\AppData\\Local\\Temp\\cloth_*\\bake.npz`. Dort liegt sie seit dem
15.08.2026 nicht mehr (Zwischenstände gehen nach `media/tmp/pipelines/`, harte
Projektregel wegen rund 100 GB Datenmüll auf C:). Beide haben seither IMMER
übersprungen und trotzdem grün gemeldet.

Der Fundort ist behoben. Damit die RECHNUNG nicht weiter unbelegt bleibt — sie
läuft nur, wenn jemand einen Export gefahren hat —, steht sie hier mit gebauten
Daten:

    Bein:  Zylinder um (0|0), Radius 0,10, Höhe 0 … 1
    Rock:  Zylinder um (0|0), Radius 0,15, Höhe 0 … 1   -> nichts ragt durch
    Rock:  Radius 0,05                                   -> alles ragt durch

Die Toleranz ist 5 mm: Ein Rock mit Radius 0,102 gilt noch als in Ordnung.
"""

import numpy as np
from django.test import SimpleTestCase

# `tests` ist das Paket der Oberflaechen-Tests im Projektstamm (nicht
# `core.tests`); von dort kommt die Rechenklasse.
from tests._rockradien import Rockradien


def zylinder(radius, punkte=64, hoehen=20, mitte=(0.0, 0.0), von=0.0, bis=1.0):
    """Punkte auf einem Zylindermantel — (N, 3) mit Y als Höhe."""
    winkel = np.linspace(0, 2 * np.pi, punkte, endpoint=False)
    hoehe = np.linspace(von, bis, hoehen)
    x = mitte[0] + radius * np.cos(winkel)
    z = mitte[1] + radius * np.sin(winkel)
    return np.array([[x[i], y, z[i]] for y in hoehe for i in range(punkte)])


class RockradienTest(SimpleTestCase):

    def pruefen(self, bein, rock):
        pruefung = Rockradien()
        pruefung.segment_pruefen(bein, rock, 'probe')
        return pruefung

    def test_weiter_rock_ist_in_ordnung(self):
        pruefung = self.pruefen(zylinder(0.10), zylinder(0.15))
        self.assertGreater(pruefung.geprueft, 0, 'es muss geprüft worden sein')
        self.assertEqual(pruefung.verletzt, 0)
        self.assertTrue(pruefung.bestanden)

    def test_zu_enger_rock_wird_erkannt(self):
        pruefung = self.pruefen(zylinder(0.10), zylinder(0.05))
        self.assertEqual(pruefung.verletzt, pruefung.geprueft)
        self.assertFalse(pruefung.bestanden)
        self.assertIn('worst=', pruefung.bericht())

    def test_toleranz_von_fuenf_millimetern(self):
        """Radius 0,102 gegen Bein 0,10: 2 mm Abstand — noch in Ordnung."""
        self.assertEqual(self.pruefen(zylinder(0.10), zylinder(0.102)).verletzt, 0)
        # 8 mm zu eng liegt über der Toleranz.
        self.assertGreater(self.pruefen(zylinder(0.10), zylinder(0.092)).verletzt, 0)

    def test_mitte_wandert_mit_dem_stoff(self):
        """Zur Seite gelehnt: Die Mitte ist der Stoffschwerpunkt, nicht (0|0).

        Ohne das wäre jeder seitlich verschobene Rock eine Verletzung.
        """
        pruefung = self.pruefen(zylinder(0.10, mitte=(0.5, 0.0)),
                                zylinder(0.15, mitte=(0.5, 0.0)))
        self.assertEqual(pruefung.verletzt, 0)

    def test_flacher_stoff_wird_uebersprungen(self):
        """Ein Fetzen (unter 5 cm hoch) ist Sache eines anderen Tests."""
        pruefung = self.pruefen(zylinder(0.10), zylinder(0.05, von=0.0, bis=0.02))
        self.assertEqual(pruefung.geprueft, 0)

    def test_huefte_und_saum_bleiben_aussen_vor(self):
        """Geprüft werden fünf Höhen zwischen 10 % und 90 % der Stoffhöhe."""
        pruefung = self.pruefen(zylinder(0.10), zylinder(0.15))
        self.assertEqual(pruefung.geprueft, Rockradien.HOEHEN)

    def test_beispielbilder_sind_anfang_mitte_ende(self):
        self.assertEqual(Rockradien.beispielbilder(101), [0, 50, 100])
        self.assertEqual(Rockradien.beispielbilder(2), [0, 1])

    def test_grenze_liegt_bei_zehn_prozent(self):
        """Einzelne Falten dürfen herausragen, viele nicht."""
        pruefung = Rockradien()
        pruefung.geprueft, pruefung.verletzt = 100, 9
        self.assertTrue(pruefung.bestanden)
        pruefung.verletzt = 10
        self.assertFalse(pruefung.bestanden)
