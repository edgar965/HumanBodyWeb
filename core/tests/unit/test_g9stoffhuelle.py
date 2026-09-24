# -*- coding: utf-8 -*-
u"""Haar ueber dem GarmentCode-Kleid (24.09.2026, Edgar mit Bild: „haar geht immer noch durch das
Garment Code Kleid, auch beim Neubau"). Gemessen an Damira: Haarpunkte mehr als 2 mm unter der
Kleidflaeche 18.057 ohne Kleid in der Rechnung, 5.080 mit der umgebauten Flaeche, 1.304 mit der
Huelle (`ProjektTemp/gc_ueber_daz/haar_varianten.py`).

Kunstdaten: Haut = Ebene y = 0 (Normale +y, `Kunsthaut`), Stuecke als Gitter darueber.

    DieFlaecheMitZweiStuecken
      1. Ein BH (4 mm) unter einem Kleid, das 3 cm vor der Haut haengt (Zelt unter der Brust),
         faellt aus der Flaeche; ein Saumpunkt dazwischen geht ueber das KLEID, nicht nur den BH.
         Sabotage: `ZWISCHEN_R` auf 0,015 (nur die raeumliche Naehe) -> rot.
      2. Ein einlagiges Stueck (GarmentCode) verliert an einer Schraege keine Punkte; mehrlagig
         (Daz) faellt die Schraege durch `aussenlage`. Sabotage: `einlagig` ignorieren -> rot.
    DieStoffhuelle
      3. Ein Punkt hinter dem Kleid geht auf `ABSTAND` davor; einer daneben (ueber offener Haut)
         und einer davor bleiben. Sabotage: `RAND_TOLERANZ` auf 10 -> der daneben wandert, rot.
      4. Umgekehrt gewickelt hebt die Huelle genauso (Vorzeichen am Median gegen die Haut).
         Sabotage: die Median-Umkehr weglassen -> rot.
"""
import numpy as np
from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.kollision import G9kollision  # noqa: E402
from Genesis9.lagen import G9lagen  # noqa: E402
from Genesis9.stoffhuelle import G9stoffhuelle  # noqa: E402

from .test_genesis9_lagen import Kunsthaut, gitter  # noqa: E402


def netz(hoehe, x0=-0.1, x1=0.1, z0=-0.1, z1=0.1, schritt=0.01, umgekehrt=False):
    u"""`(punkte, dreiecke)`: Gitter auf Hoehe `hoehe`, nach +y gewickelt (`umgekehrt`: −y)."""
    xs, zs = np.arange(x0, x1 + 1e-9, schritt), np.arange(z0, z1 + 1e-9, schritt)
    punkte = np.array([[x, hoehe, z] for z in zs for x in xs])
    n = len(xs)
    dreiecke = []
    for j in range(len(zs) - 1):
        for i in range(n - 1):
            a, b, c, d = j * n + i, j * n + i + 1, (j + 1) * n + i, (j + 1) * n + i + 1
            dreiecke += [[a, c, b], [b, c, d]]            # (c − a) × (b − a) zeigt nach +y
    dreiecke = np.array(dreiecke)
    return punkte, (dreiecke[:, ::-1] if umgekehrt else dreiecke)


class DieFlaecheMitZweiStuecken(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.lagen = G9lagen(Kunsthaut.koerper())

    def test_1_der_bh_unter_dem_zelt_faellt_heraus(self):
        bh, kleid = gitter(0.004, -0.1, 0.1, -0.1, 0.1), gitter(0.03, -0.2, 0.2, -0.2, 0.2)
        p, n, _ = self.lagen.flaeche([bh, kleid], einlagig=[False, True])
        mitte = (np.abs(p[:, 0]) < 0.08) & (np.abs(p[:, 2]) < 0.08)
        self.assertTrue((p[mitte, 1] > 0.02).all(), sorted(set(np.round(p[mitte, 1], 3))))
        saum = np.array([[0.0, 0.010, 0.0]])
        self.assertGreaterEqual(G9kollision.hinaus(saum, p, n)[0, 1], 0.03 + G9kollision.ABSTAND - 1e-9)

    def test_2_ein_einlagiges_stueck_behaelt_seine_schraege(self):
        schraege = gitter(0.0, -0.1, 0.1, -0.1, 0.1)
        schraege[:, 1] = 0.01 + 0.5 * np.maximum(schraege[:, 2], 0.0)     # 5 mm je cm
        einlagig, _n, _ = self.lagen.flaeche([schraege], einlagig=[True])
        mehrlagig, _n, _ = self.lagen.flaeche([schraege])
        stoff = lambda p: (p[:, 1] > 0.005).sum()                         # noqa: E731
        self.assertEqual(stoff(einlagig), len(schraege))
        self.assertLess(stoff(mehrlagig), len(schraege))


class DieStoffhuelle(SimpleTestCase):
    databases = set()

    def _huelle(self, umgekehrt=False):
        punkte, dreiecke = netz(0.03, umgekehrt=umgekehrt)
        return G9stoffhuelle(punkte, dreiecke, haut=Kunsthaut.koerper())

    def test_3_dahinter_hinaus_daneben_und_davor_bleiben(self):
        punkte = np.array([[0.004, 0.010, 0.006],     # unter dem Kleid
                           [0.130, 0.010, 0.000],     # 3 cm neben dem Rand, ueber offener Haut
                           [0.004, 0.050, 0.006]])    # davor
        neu = self._huelle().hinaus(punkte)
        self.assertAlmostEqual(neu[0, 1], 0.03 + G9stoffhuelle.ABSTAND, places=9)
        np.testing.assert_allclose(neu[1:], punkte[1:])

    def test_4_umgekehrt_gewickelt_hebt_genauso(self):
        neu = self._huelle(umgekehrt=True).hinaus(np.array([[0.004, 0.010, 0.006]]))
        self.assertAlmostEqual(neu[0, 1], 0.03 + G9stoffhuelle.ABSTAND, places=9)
