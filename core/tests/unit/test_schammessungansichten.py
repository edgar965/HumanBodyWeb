# -*- coding: utf-8 -*-
"""`Schammessungansichten` — Erhebungen aus mehreren Richtungen und der Absatz am Ring (11.10.2026), an Kunstflächen.

Anlass (Edgar, 11.10.2026): das Daz-Stück sah „komplett ohne Geometrie" aus und hatte „cm hohe Absätze", während die Messung „keine Abweichung" meldete — Form Original → Modell Median 0,32 mm
misst nur, wie nah das Stück am Original liegt (und das Original liegt seitlich bis 15 mm unter der Haut), nicht, wie viel Erhebung es trägt und ob die Haut stufenlos ins Stück übergeht.

Kunstwelt: die Haut ist die Platte z = 0 (±60 mm), das Original trägt in der Mitte einen Hügel von 10 mm (Gauß, σ = 12 mm); `vorne` = +z.

1. Das Modell gleich dem Original: Treue 1 aus jeder Richtung, die den Hügel sieht; Abweichung Median 0.
2. Ein flaches Modell (nur die Haut): Treue 0 — das ist der Fall „komplett ohne Geometrie", den die alte Messung nicht fand.
3. Ein halb so hoher Hügel: Treue ≈ 0,5.
4. Zellen, deren Haut weit neben dem Stück liegt (hier ein hoher Block daneben), zählen nicht: das Volumen bleibt.
5. Absatz am Ring: liegt das Stück 2 mm hinter dem Ring 12 mm unter der Hautebene, meldet der Bericht 12 mm, bei einem bündigen Stück 0.
6. `abweichungen` der `Schammessung` nennt die Treue unter der Schwelle und den Absatz über der Schwelle.

Sabotage-Gegenprobe: in `_ansicht` die Zeile `vm = …` auf `vo` setzen (Modell immer gleich Original) macht Fall 2 und 3 rot; `im_kasten &= …` weglassen macht Fall 4 rot; in `_absatz` das Stück durch das Original ersetzen macht Fall 5 rot.
"""
from unittest import mock

import numpy as np
import trimesh
from django.test import SimpleTestCase

from core.dienste.schammessung import Schammessung
from core.dienste.schammessungansichten import Schammessungansichten
from core.dienste.schammessungrahmen import Schammessungrahmen


def _feld(z_von_xy, halb=0.06, n=61):
    """Höhenfeld `z(x, y)` als Netz über dem Quadrat ±`halb`."""
    xs = np.linspace(-halb, halb, n)
    xx, yy = np.meshgrid(xs, xs)
    punkte = np.column_stack([xx.ravel(), yy.ravel(), z_von_xy(xx.ravel(), yy.ravel())])
    dreiecke = []
    for j in range(n - 1):
        for i in range(n - 1):
            a = j * n + i
            dreiecke += [[a, a + 1, a + n + 1], [a, a + n + 1, a + n]]
    return trimesh.Trimesh(punkte, np.array(dreiecke), process=False)


def _huegel(hoehe):
    return lambda x, y: hoehe * np.exp(-(x * x + y * y) / (2 * 0.012 ** 2))


class SchammessungansichtenTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.haut = _feld(lambda x, y: np.zeros_like(x))
        self.original = _feld(_huegel(0.010))
        self.rahmen = Schammessungrahmen([0.0, 0.0, 0.0], [0.0, 0.0, 1.0], self.original.vertices[np.hypot(self.original.vertices[:, 0], self.original.vertices[:, 1]) < 0.03])
        self.ring = np.array([[0.03 * np.cos(t), 0.03 * np.sin(t), 0.0] for t in np.linspace(0, 2 * np.pi, 24, endpoint=False)])
        self.ring_n = np.tile([0.0, 0.0, 1.0], (len(self.ring), 1))
        patcher = mock.patch.object(Schammessungansichten, 'RASTER_M', 0.004)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _messen(self, modell, stueck=None):
        stueck = stueck if stueck is not None else modell
        return Schammessungansichten(self.rahmen, self.haut, self.original, modell, stueck, self.original, self.ring, self.ring_n).messen()

    @staticmethod
    def _je(aus, name):
        return next(a for a in aus['ansichten'] if a['name'] == name)

    def test_1_das_modell_gleich_dem_original_traegt_die_ganze_erhebung(self):
        aus = self._messen(self.original)
        for name in ('vorn', 'links 45°', 'rechts 45°'):
            a = self._je(aus, name)
            with self.subTest(name):
                self.assertIsNotNone(a['treue'])
                self.assertAlmostEqual(a['treue'], 1.0, delta=0.05)
                self.assertLess(a['abweichung']['median'], 0.05)

    def test_2_ein_flaches_modell_hat_keine_erhebung(self):
        aus = self._messen(self.haut)
        a = self._je(aus, 'vorn')
        self.assertGreater(a['volumen_original_mm3'], 100)
        self.assertEqual(a['volumen_modell_mm3'], 0)
        self.assertGreater(a['abweichung']['max'], 8.0, 'der Hügel von 10 mm fehlt im Modell')

    def test_3_ein_halb_so_hoher_huegel_traegt_die_haelfte(self):
        aus = self._messen(_feld(_huegel(0.005)))
        a = self._je(aus, 'vorn')
        v = a['volumen_modell_mm3'] / a['volumen_original_mm3']
        self.assertAlmostEqual(v, 0.5, delta=0.08)
        self.assertLess(a['hoehe_modell_mm'][1], 0.65 * a['hoehe_original_mm'][1])

    def test_4_zellen_weit_neben_dem_stueck_zaehlen_nicht(self):
        mit_block = _feld(lambda x, y: np.where(x > 0.05, 0.030, 0.0))                   # ein 30 mm hoher Block am Rand der Haut (Schenkel)
        self.haut = mit_block
        original = _feld(lambda x, y: _huegel(0.010)(x, y) + np.where(x > 0.05, 0.030, 0.0))
        self.original = original
        aus = Schammessungansichten(self.rahmen, mit_block, original, original, original, original, self.ring, self.ring_n).messen()
        a = self._je(aus, 'vorn')
        ohne = Schammessungansichten(self.rahmen, _feld(lambda x, y: np.zeros_like(x)), _feld(_huegel(0.010)), _feld(_huegel(0.010)), _feld(_huegel(0.010)),
                                     _feld(_huegel(0.010)), self.ring, self.ring_n).messen()
        self.assertAlmostEqual(a['volumen_original_mm3'], self._je(ohne, 'vorn')['volumen_original_mm3'], delta=30)

    def test_5_der_absatz_am_ring_wird_gemessen(self):
        flach = self._messen(self.haut)['absatz']
        self.assertLess(flach['stueck_mm']['max'], 0.1)
        # ein Stück, das 2 mm hinter dem Ring (r = 28 mm) 12 mm unter der Hautebene liegt. Die Stufe endet bei 31 mm, einen Gitterschritt (2 mm) hinter dem Messpunkt: bei 28,5 mm lag der Messpunkt
        # mitten in der Dreiecksfläche der Stufe, und von 24 Ringpunkten maßen nur 16 mehr als 10 mm (gemessen 12.10.2026: –5,7 / –10,5 / –12,0 mm je nach Winkel zum Gitter).
        stufe = _feld(lambda x, y: np.where(np.hypot(x, y) < 0.031, -0.012, 0.0))
        aus = self._messen(self.haut, stueck=stufe)['absatz']
        self.assertGreater(aus['stueck_mm']['median'], 10.0)
        self.assertEqual(aus['stueck_ueber_10mm'], len(self.ring))

    def test_6_die_abweichungen_nennen_flachheit_und_absatz(self):
        schammessung = Schammessung(np.zeros((3, 3)), np.zeros((1, 3), dtype=np.int64), np.zeros((1, 3, 2)), {'punkte': np.zeros((3, 3)), 'dreiecke': np.zeros((1, 3), dtype=np.int64)}, None)
        bericht = {'ansichten': {'ansichten': [{'name': 'links 45°', 'treue': 0.42}, {'name': 'vorn', 'treue': None}],
                                 'absatz': {'nach_innen_mm': 2.0, 'stueck_mm': {'n': 99, 'median': 0.5, 'p90': 5.2, 'max': 13.5}}}}
        texte = schammessung.abweichungen(bericht)
        self.assertTrue(any('links 45°' in t and '42 %' in t for t in texte), texte)
        self.assertTrue(any('Absatz am Ring' in t and '5.2' in t for t in texte), texte)
        gut = {'ansichten': {'ansichten': [{'name': 'links 45°', 'treue': 0.95}], 'absatz': {'nach_innen_mm': 2.0, 'stueck_mm': {'n': 99, 'median': 0.2, 'p90': 1.0, 'max': 2.0}}}}
        self.assertEqual(schammessung.abweichungen(gut), [])
