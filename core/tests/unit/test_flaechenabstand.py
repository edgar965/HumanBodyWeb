# -*- coding: utf-8 -*-
"""`Flaechenabstand`: der Abstand von Punkten zur Fläche, schnell auch für Punkte weit von ihr (10.10.2026).

Anlass: Im Rosemary-Import brauchte `trimesh.proximity.closest_point` für 163.810 Körperpunkte 22,5 Minuten und bis zu 28 GB. An den echten
Asian-Daten (Figur 104.480 Punkte, 201.248 Dreiecke, `ProjektTemp/_wegwerf/asian/abstand_echt.py`) wächst die Zeit des alten Aufrufs mit dem
Abstand der Punkte — 0,82 ms je Punkt am Körper, 2,77 ms bei 10 cm, 4,59 ms bei 20 cm —, die neue bleibt bei ~0,1 ms; Abweichung gegen
trimesh höchstens 0,055 mm.

1. Gleiches Maß: auf einem Kugelnetz stimmt der Abstand nahe der Fläche und weit weg mit trimesh überein (Toleranz 0,05 mm).
2. Ein lose hängender Netzpunkt ohne Dreieck bricht nichts: der Punkt dort behält den Abstand zum Netzpunkt.
3. Keine Punkte → leeres Ergebnis; ein einzelner Punkt geht.
4. Mehr Punkte als ein Block (`BLOCK`) liefern dieselben Zahlen wie ein Durchgang.

Sabotage-Gegenprobe: in `abstand` `np.minimum.reduceat` durch `np.maximum.reduceat` ersetzen → Fall 1 rot; `NAECHSTE` auf 1 → Fall 1 (Toleranz) kann kippen.

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage.
"""

import numpy as np
import trimesh
from django.test import SimpleTestCase

from core.dienste.flaechenabstand import Flaechenabstand

TOLERANZ_M = 5e-5       # 0,05 mm — die größte Abweichung an echten Daten war 0,055 mm, an der Kugel 0,015 mm


def _kugel():
    kugel = trimesh.creation.icosphere(subdivisions=4, radius=0.9)           # 5.120 Dreiecke
    rng = np.random.default_rng(5)
    return kugel.vertices + rng.normal(scale=0.002, size=kugel.vertices.shape), kugel.faces


def _proben(n, streuung, seed=11):
    rng = np.random.default_rng(seed)
    r = rng.normal(size=(n, 3))
    r /= np.linalg.norm(r, axis=1, keepdims=True)
    return r * (0.9 + rng.normal(scale=streuung, size=(n, 1)))


class FlaechenabstandTest(SimpleTestCase):
    databases = set()

    def test_1_gleiches_mass_wie_trimesh_nah_und_weit(self):
        punkte, dreiecke = _kugel()
        flaeche = trimesh.Trimesh(punkte, dreiecke, process=False)
        for streuung in (0.004, 0.10):
            p = _proben(800, streuung)
            exakt = trimesh.proximity.closest_point(flaeche, p)[1]
            neu = Flaechenabstand.abstand(p, punkte, dreiecke)
            self.assertLess(float(np.abs(neu - exakt).max()), TOLERANZ_M, 'Streuung %s' % streuung)

    def test_2_ein_loser_netzpunkt_ohne_dreieck(self):
        punkte, dreiecke = _kugel()
        punkte = np.vstack([punkte, [[5.0, 0.0, 0.0]]])                       # hängt an keinem Dreieck
        p = np.array([[5.0, 0.1, 0.0], [0.9, 0.0, 0.0]])
        d = Flaechenabstand.abstand(p, punkte, dreiecke)
        self.assertAlmostEqual(float(d[0]), 4.1, delta=0.2, msg='nächste Fläche ist die Kugel, 4,1 m entfernt')
        self.assertLess(float(d[1]), 0.01)

    def test_3_leer_und_einzeln(self):
        punkte, dreiecke = _kugel()
        self.assertEqual(len(Flaechenabstand.abstand(np.zeros((0, 3)), punkte, dreiecke)), 0)
        einer = Flaechenabstand.abstand([[0.0, 0.0, 1.0]], punkte, dreiecke)
        self.assertAlmostEqual(float(einer[0]), 0.1, delta=0.01)

    def test_4_blockweise_gleich_wie_in_einem_durchgang(self):
        punkte, dreiecke = _kugel()
        p = _proben(700, 0.05, seed=3)
        ganz = Flaechenabstand.abstand(p, punkte, dreiecke)
        alt = Flaechenabstand.BLOCK
        try:
            Flaechenabstand.BLOCK = 128
            blockweise = Flaechenabstand.abstand(p, punkte, dreiecke)
        finally:
            Flaechenabstand.BLOCK = alt
        self.assertTrue(np.array_equal(ganz, blockweise))
