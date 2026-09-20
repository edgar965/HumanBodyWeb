# -*- coding: utf-8 -*-
u"""Der Aermel muss ueber den Arm passen — `armumfang`, `aermelweite`, `armloch`.

Edgar, 20.09.2026, mit Bildern: „Hemd tailliert an den Armen auch kaputt" (die
Aermel klafften an der Unterseite auf), davor ein abstehender Lappen am
kurzen T-Shirt-Aermel. Gemessen an Olesia1 (Genesis 9): Armloch 8,0 cm, weil
das Umfangsmaximum des Rumpfs auf Achselhoehe lag; Aermel oben 25 cm Umfang
an einem Arm mit 30, Aermelende 16,2 cm am Ellbogen mit 23.

Kunstfiguren, kein Netz von der Platte:

1. `Armumfang`: ein Kegelarm (Radius 5 -> 3 cm) an einem Rumpfwuerfel; das
   Profil misst 2·pi·r auf 5 %; `bei` interpoliert; die Hand (Buckel hinter
   der engsten Stelle) wird abgeschnitten.
2. `Aermelweite.weiten`: zu enges Ende wird auf Arm + Luft gehoben, ein
   ausreichendes bleibt; Vorder- und Rueckenhaelfte geben EINEN Hinweis.
3. `Armloch`: aus der Achsel (tiefster Rumpfpunkt am Arm), mit Zugabe
   hoechstens `ANTEIL_MAX` der Brustlinie; ohne Segmente das Verhaeltnis der
   Vorlage; `rueckenbreite` haelt das Armloch der Rueckenhaelfte offen (Kin1,
   17:44: „Schnitt konstruieren — Fehler").

Sabotage-Gegenprobe: in `Aermelweite.weiten` `bisher >= noetig` durch
`bisher > 0` ersetzen -> Fall 2 rot.
"""

import sys

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

if str(settings.ASSETS_ROOT) not in sys.path:  # pragma: no cover
    sys.path.insert(0, str(settings.ASSETS_ROOT))

from GarmentCode.aermelweite import Aermelweite  # noqa: E402
from GarmentCode.armloch import Armloch  # noqa: E402
from GarmentCode.armumfang import Armumfang  # noqa: E402


def kunstfigur(hand=False):
    u"""Rumpfwuerfel (0,4 m Kante, Oberkante z=1,4) und ein Kegelarm nach
    rechts oben (Z oben): Radius 5 cm an der Schulter, 3 cm an der Hand,
    50 cm lang, um 45 Grad gesenkt. Mit `hand`: ein dicker Knubbel dahinter."""
    zs, ys, xs = np.meshgrid(np.linspace(1.0, 1.4, 21), np.linspace(-0.2, 0.2, 21),
                             np.linspace(-0.2, 0.2, 21), indexing='ij')
    rumpf = np.c_[xs.ravel(), ys.ravel(), zs.ravel()]
    achse = np.array([np.cos(np.radians(45)), 0.0, -np.sin(np.radians(45))])
    quer1 = np.array([0.0, 1.0, 0.0])
    quer2 = np.cross(achse, quer1)
    start = np.array([0.2, 0.0, 1.35])
    arm = []
    for t in np.linspace(0.0, 0.5, 51):
        r = 0.05 - 0.02 * (t / 0.5)
        if hand and t > 0.42:
            r = 0.06
        for w in np.linspace(0, 2 * np.pi, 24, endpoint=False):
            arm.append(start + achse * t + (np.cos(w) * quer1 + np.sin(w) * quer2) * r)
    arm = np.array(arm)
    v = np.vstack([rumpf, arm])
    seg = {'body': list(range(len(rumpf))),
           'left_arm': list(range(len(rumpf), len(v))), 'right_arm': []}
    return v, seg


class Umfang(SimpleTestCase):
    databases = set()

    def test_profil_misst_den_kegel(self):
        v, seg = kunstfigur()
        profil = Armumfang(v, seg, oben=2).profil()
        self.assertIsNotNone(profil)
        self.assertGreaterEqual(len(profil), 10)
        # 6 cm ab Schulter: Radius ~4,8 cm -> 30 cm Umfang; 40 cm: ~3,4 -> 21 cm.
        self.assertAlmostEqual(Armumfang.bei(profil, 6.0), 2 * np.pi * 4.8, delta=1.5)
        self.assertAlmostEqual(Armumfang.bei(profil, 40.0), 2 * np.pi * 3.4, delta=1.5)
        # Ausserhalb festgehalten, dazwischen linear.
        self.assertEqual(Armumfang.bei(profil, -3), profil[0][1])
        self.assertEqual(Armumfang.bei(profil, 999), profil[-1][1])
        self.assertAlmostEqual(Armumfang.bei([[0, 10], [10, 20]], 2.5), 12.5)

    def test_die_hand_wird_abgeschnitten(self):
        v, seg = kunstfigur(hand=True)
        profil = Armumfang(v, seg, oben=2).profil()
        self.assertLess(profil[-1][0], 44.0)                  # vor dem Knubbel
        self.assertLess(profil[-1][1], 2 * np.pi * 3.6)       # das Handgelenk, nicht die Hand

    def test_ohne_arm_kein_profil(self):
        v, seg = kunstfigur()
        self.assertIsNone(Armumfang(v, {'body': seg['body']}, oben=2).profil())
        self.assertIsNone(Armumfang.bei(None, 5))


class Kante:
    def __init__(self, start, end):
        self.start, self.end = start, end


def oeffnung(breite, hoehe):
    u"""Eine Armlochkante wie `open_shape`: von (0,0) nach (-breite, -hoehe)."""
    return [Kante((0.0, 0.0), (-breite, -hoehe))]


class Weiten(SimpleTestCase):
    databases = set()

    #: Arm: 30 cm oben, 24 am Ellbogen, 16 am Handgelenk.
    PROFIL = [[2, 30], [20, 26], [28, 24], [50, 16]]

    def setUp(self):
        Aermelweite.profil = list(self.PROFIL)
        Aermelweite.hinweise = []

    def tearDown(self):
        Aermelweite.profil = None
        Aermelweite.hinweise = []

    def _design(self, laenge, ende):
        return {'length': {'v': laenge}, 'end_width': {'v': ende}}

    def test_zu_enges_ende_wird_auf_den_arm_gehoben(self):
        body = {'arm_length': 52.0, 'wrist': 16.0}
        design = self._design(0.5, 0.4)
        # Armloch 2 breit, 14 hoch: Ende 0,4 * 14 = 5,6, wrist/2 = 8 -> 16 cm Umfang
        # am Ellbogen (2 + 25 = 27 cm ab Schulter, Arm ~24): zu eng.
        neu = Aermelweite.weiten(body, design, oeffnung(2.0, 14.0))
        self.assertAlmostEqual(neu, 24.25 + Aermelweite.LUFT_CM, delta=0.05)
        self.assertAlmostEqual(design['end_width']['v'] * 14.0 * 2, neu, places=6)
        self.assertEqual(len(Aermelweite.hinweise), 1)
        # Die Rueckenhaelfte (gleiche Oeffnung) meldet nichts Neues.
        self.assertIsNone(Aermelweite.weiten(body, design, oeffnung(2.0, 14.0)))
        self.assertEqual(len(Aermelweite.hinweise), 1)

    def test_weites_ende_bleibt(self):
        body = {'arm_length': 52.0, 'wrist': 16.0}
        design = self._design(0.5, 1.2)                      # 1,2 * 14 = 16,8 -> 33,6 cm
        self.assertIsNone(Aermelweite.weiten(body, design, oeffnung(2.0, 14.0)))
        self.assertEqual(design['end_width']['v'], 1.2)
        self.assertEqual(Aermelweite.hinweise, [])

    def test_ohne_profil_passiert_nichts(self):
        Aermelweite.profil = None
        design = self._design(0.5, 0.4)
        self.assertIsNone(Aermelweite.weiten({'arm_length': 52.0, 'wrist': 16.0}, design,
                                             oeffnung(2.0, 14.0)))
        self.assertEqual(design['end_width']['v'], 0.4)


class Tiefe(SimpleTestCase):
    databases = set()

    VORLAGE = {'armscye_depth': 12.6, 'vert_bust_line': 20.8, 'bust_line': 25.6}

    def test_aus_der_achsel_und_begrenzt(self):
        v, seg = kunstfigur()
        loch = Armloch(v, seg, self.VORLAGE)
        # Der Arm setzt bei z 1,35 mit Radius 5 cm an: die Achsel liegt darunter.
        achsel = loch.achsel_z()
        self.assertTrue(1.27 <= achsel <= 1.35, achsel)
        self.assertAlmostEqual(loch.aus_achsel(1.44), (1.44 - achsel) * 100, places=6)
        self.assertAlmostEqual(loch.tiefe(1.44, 30.0), loch.aus_achsel(1.44), places=6)
        # Brustlinie 14 cm: Tiefe plus 2,5 cm Zugabe hoechstens 80 % davon.
        self.assertAlmostEqual(loch.tiefe(1.44, 14.0), 0.8 * 14.0 - 2.5, places=6)
        self.assertAlmostEqual(Armloch.grenze(14.0), 8.7, places=6)
        self.assertIsNone(Armloch.grenze(0))

    def test_der_ruecken_laesst_dem_armloch_platz(self):
        """Kin1: back_width 31,3 bei shoulder_w 33,95 -> Armloch der Rueckenhaelfte
        -0,3 cm, `cut_corner` bricht ab. Mindestens shoulder_w - 2 + 2 * 3 cm."""
        self.assertEqual(Armloch.rueckenbreite(31.33, 33.95), (33.95 - 2.0 + 6.0, True))
        self.assertEqual(Armloch.rueckenbreite(39.1, 34.5), (39.1, False))
        self.assertEqual(Armloch.rueckenbreite(None, 34.5), (None, False))

    def test_ohne_segmente_das_verhaeltnis_der_vorlage(self):
        v, _ = kunstfigur()
        loch = Armloch(v, {}, self.VORLAGE)
        misch = 2.0 / 3.0 * 20.8 + 1.0 / 3.0 * 25.6
        self.assertAlmostEqual(loch.tiefe(1.44, 22.4), 12.6 * 22.4 / misch, places=6)
        self.assertIsNone(Armloch(v, {}, {}).tiefe(1.44, 22.4))
