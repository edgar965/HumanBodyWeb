# -*- coding: utf-8 -*-
"""Kostüm-Prüfung „Haut am Saum wie der Eingang“ (29.10.2026, `Kostuemsaumhaut`, Prüfung Fassung 26) an Kunstdaten: Eingang = geschlossener Zylinder r 10 cm, Stück = offene Röhre r 10,5 cm
von y 0,5 bis 0,7 (zwei Ränder je 0,66 m), Figur = Zylinder mit wählbarem Halbmesser je Höhe.

    1  Figur wie der Eingang → beide Ränder grün (0 % davor)
    2  Figur unter dem unteren Saum 15 mm dicker (y 0,46–0,54, Edgars Beule unter der Unterhose) → unterer Rand rot, oberer grün
    3  Figur überall 2 cm dünner (im Eingang) → grün: unter und neben Kleidung darf der Körper innen liegen
    4  kein Stück mit Öffnungen → keine Messung
Die Gegenprobe am echten Lauf (edgar 29.10.2026 nachts: Hose rechts 14,8 %, links 9,2 % rot) rechnet `ProjektTemp/_wegwerf/regler_ki/saumhaut_pruefen.py`.
Sabotage (von Hand): in `messen` `w < -cls.VOR_MM` statt `w > cls.VOR_MM` → Fall 3 rot, Fall 2 grün; `koerper_alle` → `koerper` mit leerem Dreieckssatz → Fall 2 ohne Messung.
"""
import math
import sys
import unittest
from types import SimpleNamespace

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


def _cuda():
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def _zylinder(halbmesser, y0=0.0, y1=1.0, deckel=True, n_um=96, n_hoch=101):
    """(Punkte, Dreiecke): Mantel mit `halbmesser(y)` je Höhe, auf Wunsch mit Deckeln."""
    ys = np.linspace(y0, y1, n_hoch)
    w = np.linspace(0, 2 * math.pi, n_um, endpoint=False)
    p = np.array([[halbmesser(y) * math.cos(a), y, halbmesser(y) * math.sin(a)] for y in ys for a in w])
    f = []
    for j in range(n_hoch - 1):
        for i in range(n_um):
            a, b, c, d = j * n_um + i, j * n_um + (i + 1) % n_um, (j + 1) * n_um + i, (j + 1) * n_um + (i + 1) % n_um
            f += [[a, c, b], [b, c, d]]
    if deckel:
        unten, oben = len(p), len(p) + 1
        p = np.vstack([p, [[0, y0, 0], [0, y1, 0]]])
        o = (n_hoch - 1) * n_um
        f += [[unten, i, (i + 1) % n_um] for i in range(n_um)] + [[oben, o + (i + 1) % n_um, o + i] for i in range(n_um)]
    return p, np.array(f, dtype=np.int64)


@unittest.skipUnless(_cuda(), 'keine CUDA')
class KostuemsaumhautTest(unittest.TestCase):
    def setUp(self):
        from mesh3dai_kostuem_saumhaut import Kostuemsaumhaut
        from mesh3dai_kostuemgpu import Kostuemgpu
        self.S = Kostuemsaumhaut
        self.k = Kostuemgpu.an()

    def _szene(self, halbmesser, mit_stueck=True):
        k, t = self.k, self.k.t
        ep, ef = _zylinder(lambda y: 0.10)
        fp, ff = _zylinder(halbmesser)
        teile = []
        if mit_stueck:
            sp, sf = _zylinder(lambda y: 0.105, 0.5, 0.7, deckel=False, n_hoch=41)
            teile.append({'id': 'h', 'art': 'hose', 'name': 'Hose', 'punkte': k.feld(sp, t.float64), 'dreiecke': k.feld(sf, t.int64)})
        return SimpleNamespace(k=k, eingang=(k.feld(ep, t.float64), k.feld(ef, t.int64), None),
                               koerper_alle=(k.feld(fp, t.float64), k.feld(ff, t.int64), None), teile=teile)

    def _rot(self, m):
        return {round(r['mitte'][1], 1): r['vor_anteil'] > self.S.ANTEIL_MAX for r in m.values()}

    def test_1_wie_der_eingang(self):
        self.assertEqual(self._rot(self.S.messen(self._szene(lambda y: 0.10))), {0.5: False, 0.7: False})

    def test_2_beule_unter_dem_saum(self):
        m = self.S.messen(self._szene(lambda y: 0.115 if 0.46 <= y <= 0.54 else 0.10))
        self.assertEqual(self._rot(m), {0.5: True, 0.7: False})
        unten = [r for r in m.values() if round(r['mitte'][1], 1) == 0.5][0]
        self.assertGreater(unten['p90_mm'], 10.0)

    def test_3_innen_ist_erlaubt(self):
        self.assertEqual(self._rot(self.S.messen(self._szene(lambda y: 0.08))), {0.5: False, 0.7: False})

    def test_4_ohne_stueck(self):
        self.assertEqual(self.S.messen(self._szene(lambda y: 0.10, mit_stueck=False)), {})


if __name__ == '__main__':
    unittest.main()
