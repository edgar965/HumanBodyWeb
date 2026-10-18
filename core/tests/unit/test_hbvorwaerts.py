# -*- coding: utf-8 -*-
"""`Hbvorwaerts`: ein HumanBody-Delta vorwärts auf den Genesis-Käfig legen (17.10.2026), an einem ebenen Flicken aus Kunstpunkten.

WARUM (Edgar, 17.10.2026: „fixe alle die keine Wirkung haben"): `hb:Torso_BreastNipple` kam mit 0,000 mm an (Quelle 5,9 mm), `hb:Mouth_Protusion` mit 0,04, `hb:Mouth_SideCrease` mit 0 — der nächste Genesis-Punkt
lag 12–40 mm neben dem Merkmal, kein Genesis-Punkt las die Quellpunkte. Vorwärts legt jeder bewegte HumanBody-Punkt sein Delta auf die nächsten Genesis-Punkte. Zusagen:

1. Ein Merkmal, das neben den Genesis-Punkten liegt, kommt an: Feld größer null, Schwerpunkt der Wirkung nahe am Merkmal.
2. Die Stärke liegt nie über der Quelle (gemittelt, nicht addiert), auch wenn viele Quellpunkte auf denselben Genesis-Punkt zeigen.
3. Teile ohne Haut (`face_internal`: Augen, Mundinnenraum, Zähne — bei Genesis Anhänge) werden nicht übertragen.
4. Gegenläufige Normalen zählen nicht (Innen- gegen Außenseite): dann kommt nichts an, statt auf der falschen Seite.
5. Weiter als `NAEHE_M` vom Quellpunkt gibt es kein Gegenstück.
6. Das Delta wird im Rahmen des Zielpunkts aufgebaut: ein Delta entlang der Normale bleibt entlang der Normale, auch wo das Ziel anders steht.

FEHLERBILD OHNE DIESEN TEST: ein Regler steht im Bedienfeld und tut nichts, oder ein Iris-/Zahnregler beult das Augenlid.
Gefahren am 17.10.2026. Sabotage-Gegenprobe nicht gefahren: `AUSSEN` leeren → Fall 3 rot; `EINIG` auf −1 → Fall 4 rot; `NAEHE_M` auf 9 → Fall 5 rot.
"""
import numpy as np
from core.dienste.hbvorwaerts import Hbvorwaerts
from django.test import SimpleTestCase
from scipy.spatial import cKDTree

RAHMEN = np.array([[0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]])        # Normale z, aufwärts y, quer x
RASTER = 0.005


def flicken(g9_normale=1.0, merkmal=(0.030, 0.030), verschoben=0.012, quell_normale=1.0, teil='body', zahl_quelle=3):
    """Genesis: Raster 13 × 13 (5 mm) in der Ebene z = 0; HumanBody: `zahl_quelle` Punkte am Merkmal, um `verschoben` neben dem Raster-Gitter."""
    gitter = np.array([[i * RASTER, j * RASTER, 0.0] for i in range(13) for j in range(13)])
    zahl = len(gitter)
    quelle = np.array([[merkmal[0] + verschoben * 0.0, merkmal[1] + 0.001 * k, 0.0] for k in range(zahl_quelle)])
    paar = {'g9_punkte': gitter, 'segmente': {'body': (np.arange(zahl), np.array([], dtype=int))}, 'g9_normalen': np.tile([0.0, 0.0, g9_normale], (zahl, 1)),
            'g9_rahmen': np.tile(RAHMEN, (zahl, 1, 1)), 'massstab': 1.0}
    paar['segmente'] = {teil: (np.arange(zahl), np.arange(zahl_quelle))}
    hb = {'punkte': quelle, 'normalen': np.tile([0.0, 0.0, quell_normale], (zahl_quelle, 1)), 'rahmen': np.tile(RAHMEN, (zahl_quelle, 1, 1))}
    nachbar = cKDTree(gitter).query(gitter, k=5)[1]
    suche = gitter + np.array([verschoben, 0.0, 0.0])          # die Genesis-Punkte, wie sie im HumanBody-Raum liegen: um 12 mm verschoben
    return Hbvorwaerts(paar, hb, suche, np.arange(zahl), zahl, nachbar), gitter


def delta(n, mm=3.0, achse=2):
    d = np.zeros((n, 3))
    d[:, achse] = mm / 1000.0
    return d


class VorwaertsTest(SimpleTestCase):
    databases = set()

    def test_1_ein_merkmal_neben_den_punkten_kommt_an(self):
        v, gitter = flicken()
        feld = v.uebertragen(delta(3))
        stark = np.linalg.norm(feld, axis=1)
        self.assertGreater(float(stark.max()), 0.0005, 'es kommt etwas an')
        schwer = (stark[:, None] * gitter).sum(axis=0) / stark.sum()
        # Die Suchpunkte liegen 12 mm neben den Käfigpunkten: das Merkmal bei x = 30 mm trifft die Käfigpunkte bei x = 18 mm.
        self.assertLess(float(np.hypot(schwer[0] - (0.030 - 0.012), schwer[1] - 0.031)), 0.006, 'der Schwerpunkt liegt am Merkmal (in der Lage der Käfigpunkte)')

    def test_2_die_staerke_liegt_nie_ueber_der_quelle(self):
        v, _g = flicken(zahl_quelle=60)
        feld = v.uebertragen(delta(60))
        self.assertLessEqual(float(np.linalg.norm(feld, axis=1).max()), 0.003 + 1e-9)

    def test_3_teile_ohne_haut_werden_nicht_uebertragen(self):
        v, _g = flicken(teil='face_internal')
        self.assertEqual(float(np.abs(v.uebertragen(delta(3))).max()), 0.0)

    def test_4_gegenlaeufige_normalen_zaehlen_nicht(self):
        v, _g = flicken(g9_normale=-1.0)
        self.assertEqual(float(np.abs(v.uebertragen(delta(3))).max()), 0.0)

    def test_5_weiter_als_die_naehe_gibt_es_kein_gegenstueck(self):
        v, _g = flicken(merkmal=(0.30, 0.30))
        self.assertEqual(float(np.abs(v.uebertragen(delta(3))).max()), 0.0)

    def test_6_das_delta_wird_im_rahmen_des_ziels_aufgebaut(self):
        v, _g = flicken()
        feld = v.uebertragen(delta(3, 3.0, achse=2))              # entlang der Normale
        spitze = np.abs(feld).max(axis=0)
        self.assertGreater(float(spitze[2]), 0.0005)
        self.assertLess(float(spitze[0]) + float(spitze[1]), 1e-9, 'nichts in der Fläche')
