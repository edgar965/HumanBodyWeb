# -*- coding: utf-8 -*-
"""`Roehrenschnitt`: der Schritt als Topologie — wo aus zwei Roehren eine wird.

Edgar, 20.09.2026, mit Bild von Kin (Genesis 9): „hose alleine funktioniert
nicht" — die Oberschenkel beruehren sich, die Luft-Regel von
`Stoffhochziehen` fand keinen Schritt, die Hose blieb 10,5 cm zu tief und
wurde zwischen die Oberschenkel gepresst.

Kunstnetz (`_gabel`): zwei Beinroehren (Radius r, Mitten x = ±a, z 0..0,80)
und eine Rumpfroehre darueber (z 0,80..1,50), als Dreiecke verbunden — die
Ringe der Beine gehen an der Vereinigung in den Ring des Rumpfs ueber.
Beruehren sich die Beine (a = r), bleiben es unter 0,80 topologisch ZWEI
Ringe, obwohl sie sich spatial beruehren.

Sabotage-Gegenprobe: `ringe` ohne die Verbindung ueber das Dreieck (jede
Kante ihr eigener Ring) macht `test_zwei_roehren_werden_eine` rot; `BREITE_M
= 10` macht `test_eine_hand_in_schritthoehe_zaehlt_nicht` rot;
`Stoffhochziehen._schritt` ohne den Topologie-Zweig macht
`test_beruehrende_oberschenkel_haben_trotzdem_einen_schritt` rot.
"""

import numpy as np
from django.test import SimpleTestCase
from GarmentCode.roehrenschnitt import Roehrenschnitt
from GarmentCode.stoffhochziehen import Stoffhochziehen

from ._sicher import Sicher

N = 24


def _ring(x0, radius, z, n=N):
    w = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.column_stack([x0 + radius * np.cos(w), radius * np.sin(w), np.full(n, z)])


def _roehre(x0, radius, hoehen, start, n=N):
    """Punkte und Dreiecke einer Roehre aus Ringen; Indizes ab `start`."""
    punkte = np.vstack([_ring(x0, radius, z, n) for z in hoehen])
    dreiecke = []
    for r in range(len(hoehen) - 1):
        a = start + r * n
        for k in range(n):
            b, c = a + k, a + (k + 1) % n
            dreiecke += [[b, c, b + n], [c, c + n, b + n]]
    return punkte, dreiecke


def _gabel(a=0.10, r=0.06, rumpf=0.22, schritt=0.80, hand_x=None):
    """Zwei Beine bis `schritt`, ein Rumpf darueber, verbunden; optional eine
    'Hand' (kleine Roehre bei x = hand_x, z 0,7..0,9), die nicht dazugehoert."""
    hoehen_bein = np.linspace(0.0, schritt, 33)      # 2,5 cm: dichter als die Luft-Probe (4 cm)
    hoehen_rumpf = np.linspace(schritt, 1.50, 8)
    links, dl = _roehre(-a, r, hoehen_bein, 0)
    rechts, dr = _roehre(+a, r, hoehen_bein, len(links))
    rumpf, dm = _roehre(0.0, rumpf, hoehen_rumpf, len(links) + len(rechts), n=2 * N)
    punkte = [links, rechts, rumpf]
    dreiecke = dl + dr + dm
    # Verbindung: unterster Rumpfring (2N) mit den obersten Beinringen (je N)
    oben_l = len(links) - N
    oben_r = len(links) + len(rechts) - N
    unten_m = len(links) + len(rechts)

    def bein(j):
        return oben_l + j if j < N else oben_r + (j - N)
    for j in range(2 * N):
        j2 = (j + 1) % (2 * N)
        dreiecke += [[unten_m + j, unten_m + j2, bein(j)], [unten_m + j2, bein(j2), bein(j)]]
    if hand_x is not None:
        start = sum(len(p) for p in punkte)
        hand, dh = _roehre(hand_x, 0.03, np.linspace(0.70, 0.90, 3), start, n=12)
        punkte.append(hand)
        dreiecke += dh
    return np.vstack(punkte), np.asarray(dreiecke)


class RoehrenschnittTest(SimpleTestCase):
    databases = set()

    def test_zwei_roehren_werden_eine(self):
        punkte, dreiecke = _gabel()
        schnitt = Roehrenschnitt(punkte, dreiecke)
        self.assertEqual(schnitt.ringe(0.40), 2)
        self.assertEqual(schnitt.ringe(1.20), 1)
        self.assertEqual(schnitt.ringe(2.00), 0)
        self.assertAlmostEqual(Sicher.wert(schnitt.vereinigung(0.3, 1.2), 'Vereinigung'), 0.80, delta=0.002)

    def test_beruehrende_beine_bleiben_zwei_ringe(self):
        punkte, dreiecke = _gabel(a=0.06, r=0.06)          # die Roehren beruehren sich bei x = 0
        schnitt = Roehrenschnitt(punkte, dreiecke)
        self.assertEqual(schnitt.ringe(0.40), 2)
        self.assertAlmostEqual(Sicher.wert(schnitt.vereinigung(0.3, 1.2), 'Vereinigung'), 0.80, delta=0.002)

    def test_eine_hand_in_schritthoehe_zaehlt_nicht(self):
        punkte, dreiecke = _gabel(hand_x=0.55)
        schnitt = Roehrenschnitt(punkte, dreiecke)
        self.assertEqual(schnitt.ringe(0.75), 2)            # Beine, nicht Beine + Hand
        self.assertEqual(schnitt.ringe(0.85), 1)

    def test_ohne_zwei_roehren_unten_oder_eine_oben_kein_schritt(self):
        punkte, dreiecke = _gabel()
        schnitt = Roehrenschnitt(punkte, dreiecke)
        self.assertIsNone(schnitt.vereinigung(0.9, 1.2))    # unten schon ein Ring
        self.assertIsNone(schnitt.vereinigung(0.3, 0.7))    # oben noch zwei
        self.assertIsNone(Roehrenschnitt(punkte, None).vereinigung(0.3, 1.2))
        self.assertIsNone(Roehrenschnitt(punkte, dreiecke[:0]).vereinigung(0.3, 1.2))

    def test_vierecke_werden_zerlegt(self):
        punkte, dreiecke = _gabel()
        vierecke = np.column_stack([dreiecke, dreiecke[:, 2]])   # entartet, aber vier Spalten
        self.assertEqual(Roehrenschnitt(punkte, vierecke).ringe(0.40), 2)

    def test_beruehrende_oberschenkel_haben_trotzdem_einen_schritt(self):
        punkte, dreiecke = _gabel(a=0.06, r=0.06)
        ohne = Stoffhochziehen(punkte)
        self.assertIsNone(ohne.schritt)                     # die Luft-Regel scheitert
        mit = Stoffhochziehen(punkte, dreiecke)
        schritt = Sicher.wert(mit.schritt, 'Schritt')
        self.assertAlmostEqual(schritt[1], 0.80, delta=0.002)
        self.assertTrue(mit.beruehrung)
        # Die Hose: dieselbe Gabel, 12 cm tiefer geschnitten, Saum bei -0,02.
        hose_p, hose_d = _gabel(a=0.06, r=0.08, rumpf=0.25, schritt=0.68)
        hose_p[:, 2] -= 0.02
        self.assertIsNone(mit.hosenschritt(hose_p))         # ohne Dreiecke nicht zu finden
        zc = Sicher.wert(mit.hosenschritt(hose_p, hose_d), 'Hosenschritt')
        self.assertAlmostEqual(zc, 0.66, delta=0.002)
        neu, bilanz = mit.anwenden(hose_p, dreiecke=hose_d)
        self.assertAlmostEqual(bilanz['hochgezogen_mm'], 140.0, delta=3)
        self.assertAlmostEqual(neu[np.isclose(hose_p[:, 2], 0.66)][:, 2].max(), 0.80, delta=0.002)

    def test_mit_luft_zwischen_den_beinen_bleibt_die_alte_regel(self):
        punkte, dreiecke = _gabel(a=0.12, r=0.06)
        punkte = np.vstack([punkte, [[0.0, 0.0, 0.80]]])   # der Schrittpunkt der Luft-Regel
        mit = Stoffhochziehen(punkte, np.asarray(dreiecke))
        self.assertFalse(mit.beruehrung)
        self.assertAlmostEqual(Sicher.wert(mit.schritt, 'Schritt')[1], 0.80, delta=1e-9)
