# -*- coding: utf-8 -*-
"""Mesh3D-AI, Schritt „koerper“ (25.10.2026, `Koerperangleich`) an Kunstdaten, ohne Karte und ohne Figur:

    1  Seitenpaare: MakeHuman `_r-`/`_l-` und Daz `Right`/`Left` finden ihr Gegenstück, nur unter freien Reglern; ein Regler ohne Gegenstück bleibt allein
    2  Regler zurück in die Figur: nur freie und geänderte (|Δ| ≥ 0,005); unter 0,01 fällt der Regler weg; nicht freie und fremde bleiben wie vorher
    3  Platz in der Kette: nach „lage“, vor „haut“, Skript im Skriptdienst erlaubt
    4  Haut des Eingangs nur nah am Körper (`HAUT_NAH_M` steht, der Grund — der Stab des Zauberers — im Docstring)
    5  Größe „gesicht“ (Fassung 5, `Koerpergesicht`): die Gesichtsmitte folgt dem Knochen `head` starr und dem Mittel der Kopfpunkte; gemessen wird nur in der Bildebene (Tiefe zählt nicht)
    6  Prüfung „Stück in Hautfarbe“ (Fassung 20): Requisiten und Haar zählen nicht, andere Stücke ja
Sabotage (von Hand): in `_paare` `maske[j]` streichen → Fall 1 rot; in `_regler` die Schwelle 0,005 auf 0 → Fall 2 rot; Schritt „koerper“ vor „lage“ → Fall 3 rot;
in `Koerpergesicht._mitte` `d[self.h] @` streichen → Fall 5 rot; in `Kostuemhautpruefung.stuecke` die Bedingung `NIE_HAUT` streichen → Fall 6 rot.
"""
import sys
import unittest
from types import SimpleNamespace

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


def _torch():
    try:
        import torch  # noqa: F401
        return True
    except ImportError:
        return False


@unittest.skipUnless(_torch(), 'kein torch')
class KoerperangleichTest(unittest.TestCase):
    def setUp(self):
        import torch
        from mesh3dai_koerperangleich import Koerperangleich
        self.torch = torch
        self.K = Koerperangleich
        self.a = Koerperangleich.__new__(Koerperangleich)

    def test_1_seitenpaare(self):
        namen = ['mh:armslegs_r-lowerarm-fat-decr_incr', 'mh:armslegs_l-lowerarm-fat-decr_incr', 'body_bs_ThighRight', 'body_bs_ThighLeft', 'hb:Torso_Mass',
                 'mh:armslegs_r-foot-scale-decr_incr', 'mh:armslegs_l-foot-scale-decr_incr']
        self.a.fm = SimpleNamespace(namen=namen)
        maske = np.array([1, 1, 1, 1, 1, 1, 0], dtype=bool)
        paare = sorted(self.a._paare(maske))
        self.assertEqual(paare, [(0, 1), (2, 3)])

    def test_2_regler_zurueck(self):
        t = self.torch
        self.a.fm = SimpleNamespace(namen=['a', 'b', 'c', 'd'])
        self.a.vorher = {'a': 0.5, 'b': 0.2, 'd': 0.3, 'fremd': 1.0}
        self.a.r0 = t.tensor([0.5, 0.2, 0.0, 0.3])
        self.a.maske = t.tensor([1.0, 1.0, 1.0, 0.0])
        neu = self.a._regler(t.tensor([0.502, 0.005, 0.4, 0.9]))
        self.assertEqual(neu['a'], 0.5)                  # Δ 0,002 < 0,005: unverändert
        self.assertNotIn('b', neu)                       # 0,005 < 0,01: fällt weg
        self.assertAlmostEqual(neu['c'], 0.4, places=4)
        self.assertEqual(neu['d'], 0.3)                  # nicht frei
        self.assertEqual(neu['fremd'], 1.0)

    def test_3_platz_in_der_kette(self):
        from pathlib import Path
        from core.dienste.mesh3dairechenlauf import Mesh3dairechenlauf
        folge = [s for s, _t, _a in Mesh3dairechenlauf.SCHRITTE]
        self.assertLess(folge.index('lage'), folge.index('koerper'))
        self.assertLess(folge.index('koerper'), folge.index('haut'))
        roh = dict((s, a) for s, _t, a in Mesh3dairechenlauf.SCHRITTE)['koerper']
        self.assertIn('mesh3dai_koerperangleich_lauf.py', roh)
        ruf = (Path(settings.TOOLS_ROOT) / 'mesh3dai' / 'mesh3dai_skriptdienstruf.py').read_text(encoding='utf-8')
        self.assertIn("'mesh3dai_koerperangleich_lauf.py'", ruf)

    def test_4_haut_nur_nah(self):
        self.assertGreater(self.K.HAUT_NAH_M, 0)
        self.assertLessEqual(self.K.HAUT_NAH_M, 0.08)
        self.assertIn('Stab', self.K.__module__ and sys.modules[self.K.__module__].__doc__)

    def test_5_gesicht_folgt_dem_kopf(self):
        t = self.torch
        from mesh3dai_koerpergesicht import Koerpergesicht
        g = Koerpergesicht.__new__(Koerpergesicht)
        g.aktiv, g.h = True, 1
        g.kopf = t.tensor([False, True, True])
        g.fc0 = t.tensor([0.0, 1.6, 0.1])                 # Gesichtsmitte in Ruhe
        g.kopf0 = t.tensor([0.0, 1.6, 0.0])               # Mittel der Kopfpunkte in Ruhe
        g.mitte, g.r, g.o = t.zeros(3), t.tensor([1.0, 0.0, 0.0]), t.tensor([0.0, 1.0, 0.0])
        g.ziel = t.tensor([0.0, 1.6])
        ruhe = t.tensor([[0.0, 1.0, 0.0], [0.0, 1.55, 0.0], [0.0, 1.65, 0.0]])
        c = t.tensor([[0.0, 1.0, 0.0], [0.0, 1.5, 0.0]])
        eins = t.eye(3).expand(2, 3, 3)
        p = c.clone()
        self.assertAlmostEqual(float(g.groesse(ruhe, c, p, eins)), 0.0, places=6)
        self.assertAlmostEqual(float(g.groesse(ruhe, c, p + t.tensor([0.0, 0.02, 0.05]), eins)), 0.02, places=6)   # Tiefe zählt nicht
        nicken = t.tensor([[1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]])                                         # 90° um x: Gesicht vor dem Kopf
        d = t.stack([t.eye(3), nicken])
        self.assertAlmostEqual(float(g.groesse(ruhe, c, p, d)), float(t.tensor([0.0, 0.1 + 0.1]).norm()), places=5)

    def test_6_requisit_nie_hautfarbe(self):
        from mesh3dai_kostuem_hautpruefung import Kostuemhautpruefung
        h = Kostuemhautpruefung.__new__(Kostuemhautpruefung)
        h.ton = object()
        h.s = SimpleNamespace(teile=[{'id': 1, 'art': 'requisit', 'punkte': None, 'dreiecke': [0], 'farben': None},
                                     {'id': 2, 'art': 'oberteil', 'punkte': None, 'dreiecke': [0], 'farben': None},
                                     {'id': 3, 'art': 'haar', 'punkte': None, 'dreiecke': [0], 'farben': None}])
        h._anteil = lambda _p, _d, _f: 0.9
        self.assertEqual(set(h.stuecke()), {2})


if __name__ == '__main__':
    unittest.main()
