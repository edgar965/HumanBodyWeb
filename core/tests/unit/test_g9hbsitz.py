# -*- coding: utf-8 -*-
u"""Sitz eines Daz-Stuecks auf HumanBody: Landmarken, Rumpfhoehen, oertlicher
Massstab (`core/dienste/g9hbsitz.py`).

WARUM (19.09.2026, Edgar mit Bildern: „die Hose … etwas zu tief", „das
Oberteil zu weit"): Die Paarung der Grundkoerper schaetzt den Rumpf ueber die
Gelenke; Bund und Saum sitzen aber an der Oberflaeche. Gemessen an den
Grundfiguren: Bund 10,1 cm ueber der Hueftweite auf Genesis, 3,6 cm auf
HumanBody; Taille 13 cm schmaler, das Top 1,74- statt 1,55-fach um den Rumpf.

Kunstdaten: ein Rumpf als Stapel von Kreisringen (Schritt bei 0,8 m, Huefte
weit, Taille eng) — einmal wie Genesis, einmal mit anderen Hoehen und
schmalerer Taille.

1. `landmarken` findet Schritt, Hueftweite und Taille des Kunstrumpfs.
2. `rumpfhoehen` zieht die Schaetzung an den Landmarken auf die HumanBody-
   Hoehen; oberhalb des obersten Knotens bleibt sie (der Kopf liegt nicht auf
   Brusthoehe — `np.interp` haelt sonst den Randwert fest); nicht monotone
   Landmarken lassen alles stehen.
3. `massstab`: am Rumpf das Umfangsverhaeltnis in der Hoehe, am Rest der
   Hoehenmassstab; ueber `bis` blendet es auf ihn zurueck.
"""
import numpy as np
from django.test import SimpleTestCase

from core.dienste.g9hbsitz import G9hbsitz


def rumpf(schritt, huefte, taille, oben, r_huefte=0.16, r_taille=0.11, n=48):
    u"""Kreisringe je cm von `schritt` bis `oben`: Radius steigt bis `huefte`,
    faellt bis `taille`, steigt danach wieder leicht. (Punkte, Rumpfnummern)."""
    phi = np.linspace(0, 2 * np.pi, n, endpoint=False)
    punkte = []
    for y in np.arange(schritt, oben, 0.01):
        if y < huefte:
            r = 0.10 + (r_huefte - 0.10) * (y - schritt) / (huefte - schritt)
        elif y < taille:
            r = r_huefte + (r_taille - r_huefte) * (y - huefte) / (taille - huefte)
        else:
            r = r_taille + 0.02 * (y - taille)
        punkte.append(np.column_stack([r * np.cos(phi), np.full(n, y), r * np.sin(phi)]))
    p = np.vstack(punkte)
    return p, np.arange(len(p))


class Landmarken(SimpleTestCase):
    databases = set()

    def test_schritt_huefte_taille(self):
        p, idx = rumpf(0.80, 0.90, 1.08, 1.40)
        lm = G9hbsitz.landmarken(p, idx)
        self.assertAlmostEqual(lm['schritt'], 0.80, places=3)
        self.assertAlmostEqual(lm['huefte'], 0.90, delta=0.011)
        self.assertAlmostEqual(lm['taille'], 1.08, delta=0.011)


class Rumpfhoehen(SimpleTestCase):
    databases = set()

    def test_landmarken_fallen_aufeinander(self):
        g9, idx = rumpf(0.80, 0.90, 1.08, 1.40)
        hb, hb_idx = rumpf(0.81, 0.96, 1.10, 1.40)
        aus, knoten = G9hbsitz.rumpfhoehen(g9, g9, idx, hb, hb_idx)   # Schaetzung = Genesis selbst
        self.assertIsNotNone(knoten)
        huefte = np.abs(g9[:, 1] - 0.90) < 0.004
        taille = np.abs(g9[:, 1] - 1.08) < 0.004
        self.assertAlmostEqual(aus[huefte, 1].mean(), 0.96, delta=0.011)
        self.assertAlmostEqual(aus[taille, 1].mean(), 1.10, delta=0.011)
        # x und z unangetastet
        np.testing.assert_allclose(aus[:, [0, 2]], g9[:, [0, 2]])

    def test_ueber_dem_obersten_knoten_bleibt_die_schaetzung(self):
        g9, idx = rumpf(0.80, 0.90, 1.08, 1.60)
        hb, hb_idx = rumpf(0.81, 0.96, 1.10, 1.60)
        aus, knoten = G9hbsitz.rumpfhoehen(g9, g9, idx, hb, hb_idx)
        kopf = g9[:, 1] > knoten['von'][-1] + 0.01
        self.assertTrue(kopf.any())
        np.testing.assert_allclose(aus[kopf, 1], g9[kopf, 1])

    def test_nicht_monotone_landmarken_lassen_alles_stehen(self):
        g9, idx = rumpf(0.80, 0.90, 1.08, 1.40)
        hb, hb_idx = rumpf(0.81, 0.96, 1.10, 1.40)
        alt = G9hbsitz.landmarken
        try:
            G9hbsitz.landmarken = classmethod(lambda cls, p, r: {'schritt': 0.8, 'huefte': 1.1, 'taille': 0.9})
            aus, knoten = G9hbsitz.rumpfhoehen(g9, g9, idx, hb, hb_idx)
        finally:
            G9hbsitz.landmarken = alt
        self.assertIsNone(knoten)
        np.testing.assert_allclose(aus, g9)


class Massstab(SimpleTestCase):
    databases = set()

    def test_umfangsverhaeltnis_am_rumpf_sonst_hoehenmassstab(self):
        g9, idx = rumpf(0.80, 0.90, 1.08, 1.40, r_huefte=0.16, r_taille=0.12)
        hb, hb_idx = rumpf(0.80, 0.90, 1.08, 1.40, r_huefte=0.16, r_taille=0.09)
        zu = np.arange(len(g9))                       # gleiche Hoehen: Punkt fuer Punkt
        arm = np.array([[0.5, 1.2, 0.0]])
        alle = np.vstack([g9, arm])
        s = G9hbsitz.massstab(alle, idx, np.append(zu, 0), np.vstack([hb, arm]), hb_idx,
                              sonst=0.9, bis=1.30)
        taille = np.abs(g9[:, 1] - 1.08) < 0.004
        huefte = np.abs(g9[:, 1] - 0.90) < 0.004
        self.assertAlmostEqual(s[:-1][taille].mean(), 0.09 / 0.12, delta=0.03)
        self.assertAlmostEqual(s[:-1][huefte].mean(), 1.0, delta=0.03)
        self.assertAlmostEqual(s[-1], 0.9)                       # der Arm: Hoehenmassstab
        self.assertTrue((s >= G9hbsitz.MASSSTAB_MIN).all() and (s <= G9hbsitz.MASSSTAB_MAX).all())

    def test_ueber_bis_gilt_der_hoehenmassstab(self):
        g9, idx = rumpf(0.80, 0.90, 1.08, 1.60, r_taille=0.12)
        hb, hb_idx = rumpf(0.80, 0.90, 1.08, 1.60, r_taille=0.09)
        s = G9hbsitz.massstab(g9, idx, np.arange(len(g9)), hb, hb_idx, sonst=0.9, bis=1.20)
        oben = g9[:, 1] > 1.20 + G9hbsitz.UEBERGANG + 0.01
        self.assertTrue(oben.any())
        np.testing.assert_allclose(s[oben], 0.9)

    def test_ohne_bis_ueberall_der_hoehenmassstab(self):
        g9, idx = rumpf(0.80, 0.90, 1.08, 1.40)
        s = G9hbsitz.massstab(g9, idx, np.arange(len(g9)), g9, idx, sonst=0.95)
        np.testing.assert_allclose(s, 0.95)

