# -*- coding: utf-8 -*-
"""`G9massband` an einer Kunstfigur aus Zylindern (20.09.2026) — Umfänge, Querscheiben, Längen.

Edgar: „Warum nutzt du nicht mehr Körpermaße?" Das Maßband misst beide Netze
(Genesis-Käfig, SMPL-X) mit derselben Definition. Hier ohne Netzdateien: eine
Figur aus Zylindern mit bekannten Radien, Teilen (`G9koerperteile.NUMMER`) und
Gelenken:

1. Waagerechte Umfänge treffen 2πr: Brust/Taille (Rumpf r 0,15 → 94,2 cm),
   Hüfte (Becken r 0,17 → 106,8), Hals (r 0,06 → 37,7), Kopf (r 0,09 → 56,5).
2. Glieder QUER zum Knochen: der Oberarm hängt 43° schräg — der Querumfang ist
   2π·0,045 = 28,3 cm; eine waagerechte Scheibe gäbe die Ellipse (Sabotage: > 34).
3. Längen aus Gelenken (Oberarm 33,97 cm), Größe 172, Schritthöhe 70, Kniehöhe 45.
4. Ohne Arme in der Figur fehlen die Armmaße — kein 0, kein Fehler.
"""

import math

import numpy as np
from django.test import SimpleTestCase
from Genesis9.koerperteile import G9koerperteile
from Genesis9.massband import G9massband

N = G9koerperteile.NUMMER


def zylinder(a, b, r, teil, ringe=None, n=72):
    """Punkte auf dem Mantel eines Zylinders von a nach b (Radius r), Teilnummer je Punkt."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    laenge = np.linalg.norm(d)
    d = d / laenge
    e1 = np.cross(d, [0.0, 0.0, 1.0])
    if np.linalg.norm(e1) < 1e-6:
        e1 = np.cross(d, [1.0, 0.0, 0.0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(d, e1)
    winkel = np.linspace(0, 2 * math.pi, n, endpoint=False)
    ring = np.outer(np.cos(winkel), e1) + np.outer(np.sin(winkel), e2)
    ringe = ringe or max(3, int(laenge / 0.005))
    punkte = np.concatenate([a + t * (b - a) + r * ring for t in np.linspace(0, 1, ringe)])
    return punkte, np.full(len(punkte), N[teil], np.int32)


def figur(mit_armen=True):
    teile = [
        zylinder([0, 0.70, 0], [0, 0.86, 0], 0.17, 'becken'),
        zylinder([0, 0.86, 0], [0, 1.40, 0], 0.15, 'rumpf'),
        zylinder([0, 1.40, 0], [0, 1.50, 0], 0.06, 'hals'),
        zylinder([0, 1.50, 0], [0, 1.72, 0], 0.09, 'kopf'),
    ]
    gelenke = {'becken': [0, 0.78, 0], 'hals': [0, 1.40, 0], 'kopf': [0, 1.52, 0]}
    for s, x in (('l', 1), ('r', -1)):
        teile += [
            zylinder([x * 0.085, 0.78, 0], [x * 0.085, 0.45, 0], 0.08, s + '_oberschenkel'),
            zylinder([x * 0.085, 0.45, 0], [x * 0.085, 0.05, 0], 0.06, s + '_unterschenkel'),
            zylinder([x * 0.085, 0.05, 0], [x * 0.085, 0.05, 0.12], 0.05, s + '_fuss'),
        ]
        gelenke.update({s + '_huefte': [x * 0.085, 0.78, 0], s + '_knie': [x * 0.085, 0.45, 0],
                        s + '_knoechel': [x * 0.085, 0.05, 0]})
        if mit_armen:
            teile += [
                zylinder([x * 0.20, 1.38, 0], [x * 0.45, 1.15, 0], 0.045, s + '_oberarm'),
                zylinder([x * 0.45, 1.15, 0], [x * 0.70, 0.95, 0], 0.04, s + '_unterarm'),
            ]
            gelenke.update({s + '_schulter': [x * 0.20, 1.38, 0], s + '_ellbogen': [x * 0.45, 1.15, 0],
                            s + '_handgelenk': [x * 0.70, 0.95, 0]})
        else:
            gelenke.update({s + '_schulter': [x * 0.20, 1.38, 0]})
    punkte = np.concatenate([p for p, _ in teile])
    nummern = np.concatenate([t for _, t in teile])
    return G9massband(punkte, nummern, gelenke)


class MassbandTest(SimpleTestCase):
    databases = set()

    def test_waagerechte_umfaenge_treffen_2_pi_r(self):
        m = figur().messen()
        for k, soll in (('brust_umfang', 94.2), ('taille_umfang', 94.2), ('huefte_umfang', 106.8),
                        ('hals_umfang', 37.7), ('kopf_umfang', 56.5)):
            self.assertAlmostEqual(m[k], soll, delta=0.8, msg=k)
        self.assertAlmostEqual(m['huefte_breite'], 34.0, delta=0.5)
        self.assertAlmostEqual(m['brust_tiefe'], 30.0, delta=0.5)

    def test_glieder_quer_zum_knochen(self):
        m = figur().messen()
        self.assertAlmostEqual(m['oberarm_umfang'], 2 * math.pi * 4.5, delta=0.6)
        self.assertAlmostEqual(m['unterarm_umfang'], 2 * math.pi * 4.0, delta=0.6)
        self.assertAlmostEqual(m['oberschenkel_umfang'], 2 * math.pi * 8.0, delta=0.8)
        self.assertAlmostEqual(m['wade_umfang'], 2 * math.pi * 6.0, delta=0.8)
        # Sabotage: waagerecht geschnitten wäre der schräge Oberarm eine Ellipse — deutlich mehr.
        f = figur()
        s = f._scheibe(('l_oberarm',), 1.265, 0.0075)
        self.assertGreater(f._huelle(s[:, [0, 2]]), 34.0)

    def test_laengen_und_hoehen(self):
        m = figur().messen()
        self.assertAlmostEqual(m['groesse'], 172.0, delta=0.3)
        self.assertAlmostEqual(m['oberarm_laenge'], 33.97, delta=0.05)
        self.assertAlmostEqual(m['unterschenkel_laenge'], 40.0, delta=0.05)
        self.assertAlmostEqual(m['schritt_hoehe'], 70.0, delta=0.3)
        self.assertAlmostEqual(m['knie_hoehe'], 45.0, delta=0.05)
        self.assertAlmostEqual(m['schulter_hoehe'], 138.0, delta=0.05)

    def test_ohne_arme_fehlen_die_armmasse(self):
        m = figur(mit_armen=False).messen()
        for k in ('oberarm_umfang', 'unterarm_umfang', 'oberarm_laenge', 'arm_laenge'):
            self.assertNotIn(k, m)
        self.assertIn('brust_umfang', m)
        self.assertEqual(set(m) - set(G9massband.SCHLUESSEL), set())
