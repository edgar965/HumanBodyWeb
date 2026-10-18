# -*- coding: utf-8 -*-
"""Der Schieber läuft nur in Richtungen, die etwas bewegen (`G9morphfamilie._weg`, 17.10.2026).

WARUM (Edgar, 17.10.2026: „Teste alle Morphs, mach dir UI testcases"): Der Lauf über alle 597 Schieber im Browser fand drei, deren Anschlag nichts bewegte, und der Server-Gegencheck (`einseitige_regler.py`)
neun mit einer toten Seite: `hb:Torso_BreastNipple` (nur minus), `hb:Fantasy_EarsPointedUp` (nur plus 59 mm), `uma:Face_EyePosition` (minus 39 mm, plus 0). Der Schieber lief von −1 bis 1, die halbe
Bahn tat nichts. Zusagen (Kunstdaten in einem Wegwerf-Ordner, `G9hbmorphe`):

1. Beide Richtungen wirken (≥ `WIRKUNG_MM`): −1 … 1.
2. Wirkt nur plus: 0 … 1. Wirkt nur minus: −1 … 0.
3. Sind beide Richtungen tot, bleiben die Grenzen (der Bau übergeht solche Regler; hier ändert die Liste nichts).
4. Eine Seite genau an der Schwelle zählt als wirksam.

FEHLERBILD OHNE DIESEN TEST: ein Schieber, den man zur Hälfte bewegen kann, ohne dass etwas geschieht — kein Fehler, kein Log.
Gefahren am 17.10.2026 (auf Ansage „Teste alle Morphs"). Sabotage-Gegenprobe nicht gefahren: `_weg` gibt immer (lo, hi) zurück → Fall 2 müsste rot werden.
"""
import shutil
from pathlib import Path

from django.test import SimpleTestCase
from Genesis9.hbmorphe import G9hbmorphe

MM = 0.001


class _Ordner:
    def __init__(self):
        self.pfad = Path(__file__).parent / 'tmp_schieberbahn'
        self.alt = G9hbmorphe.ordner

    def __enter__(self):
        shutil.rmtree(self.pfad, ignore_errors=True)
        G9hbmorphe.ordner = classmethod(lambda cls: self.pfad)
        G9hbmorphe.vergessen()

    def __exit__(self, *_):
        G9hbmorphe.ordner = self.alt
        G9hbmorphe.vergessen()
        shutil.rmtree(self.pfad, ignore_errors=True)


def grenzen(plus_mm, minus_mm):
    G9hbmorphe.ablegen('Nose_Test', [1], [[plus_mm * MM, 0, 0]], [[-minus_mm * MM, 0, 0]])
    return G9hbmorphe.grenzen('hb:Nose_Test')


class SchieberbahnTest(SimpleTestCase):
    databases = set()

    def test_1_beide_richtungen_wirken(self):
        with _Ordner():
            self.assertEqual(grenzen(5.0, 3.0), (-1.0, 1.0))

    def test_2_nur_eine_richtung_wirkt(self):
        with _Ordner():
            self.assertEqual(grenzen(5.0, 0.04), (0.0, 1.0), 'minus ist tot: der Schieber läuft von 0 bis 1')
            self.assertEqual(grenzen(0.0, 5.0), (-1.0, 0.0), 'plus ist tot: der Schieber läuft von −1 bis 0')

    def test_3_sind_beide_tot_bleiben_die_grenzen(self):
        with _Ordner():
            self.assertEqual(grenzen(0.05, 0.04), (-1.0, 1.0))

    def test_4_die_schwelle_selbst_zaehlt_als_wirksam(self):
        with _Ordner():
            self.assertEqual(grenzen(G9hbmorphe.WIRKUNG_MM, 5.0), (-1.0, 1.0))
