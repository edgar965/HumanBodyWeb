"""`Kostuemzwickel` auf Kunstdaten (06.11.2026, Edgar: „die unterhose ist zwischen den beinen nicht geschlossen“).
Käfig: Streifen links Bein, Mitte Becken, rechts Bein; zwei Reihen. Die obere Reihe deckt das Stück, die untere ist frei.
    1  Beine über freie Flächen verbunden: Lücke gefunden, nur Flächen mit Punkten im Becken
    2  Becken ganz gedeckt: Beine getrennt, keine Lücke
    3  Stück deckt das Becken nicht: keine Lücke (`DECKT_MIN`)
    4  `_vierteln`: viermal so viele Flächen, Fläche gleich
    5  Attrappe der Maske hat die Parameter des Originals
Sabotage (von Hand): `~bein[f].all(1)` weglassen → Fall 1 rot; `DECKT_MIN` 0 → Fall 3 rot.
"""
import inspect
import sys
import unittest
from types import SimpleNamespace

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))

S = 0.01
SP, ZE = 9, 3


def streifen():
    xs, ys = (np.arange(SP) - 4) * S, np.arange(ZE) * S
    p = np.stack([np.tile(xs, ZE), np.repeat(ys, SP), np.zeros(SP * ZE)], 1)
    i, j = np.meshgrid(np.arange(SP - 1), np.arange(ZE - 1))
    a = (j * SP + i).ravel()
    b, c, d = a + 1, a + SP + 1, a + SP
    return p, np.concatenate([np.stack([a, b, c], 1), np.stack([a, c, d], 1)])


class Deckung:
    """Attrappe von `Kleiderverdeckung`: gibt die gesetzte Maske zurück."""

    def __init__(self, maske):
        self.maske_fest = maske

    def masken(self, stuecke, verschweissen=True, inseln=True):
        return [self.maske_fest], {}


@unittest.skipUnless(__import__('torch').cuda.is_available(), 'Kostuemgpu rechnet nur auf der Karte')
class Fall(unittest.TestCase):
    def setUp(self):
        from mesh3dai_kostuem_zwickel import Kostuemzwickel
        from mesh3dai_kostuemgpu import Kostuemgpu
        self.k = k = Kostuemgpu.an()
        t = k.t
        self.p, self.f = streifen()
        links, rechts = self.p[:, 0] < -0.015, self.p[:, 0] > 0.015
        kaefig = k.feld(self.p, t.float64)
        self.z = SimpleNamespace(k=k, q=SimpleNamespace(dreiecke=self.f, s=1.0), kaefig=kaefig, normale=k.feld(np.tile([0.0, 0.0, 1.0], (len(self.p), 1)), t.float64),
                                 beine=[kaefig[k.feld(links, t.bool)], kaefig[k.feld(rechts, t.bool)]], bein_maske=[k.feld(links, t.bool), k.feld(rechts, t.bool)],
                                 becken_maske=k.feld(~(links | rechts), t.bool), SPALT_M=0.1, ARTEN=('hose',))
        self.o = Kostuemzwickel(self.z)
        self.x = k.feld(np.zeros((3, 3)), t.float64)
        self.d = np.array([[0, 1, 2]])

    def maske(self, wahl):
        self.o._v = Deckung(wahl)

    def obere_reihe(self):
        return self.p[self.f].mean(1)[:, 1] > 0.01

    def test_luecke_wird_gefunden(self):
        self.maske(self.obere_reihe())
        lu = self.o.luecke(self.x, self.d)
        self.assertIsNotNone(lu)
        wahl = lu[0].cpu().numpy()
        self.assertTrue(bool(wahl.any()))
        self.assertFalse(bool(wahl[self.obere_reihe()].any()))
        self.assertGreater(lu[1], 0.0)
        bein = (np.abs(self.p[:, 0]) > 0.015)[self.f].all(1)
        self.assertFalse(bool(wahl[bein].any()))

    def test_becken_gedeckt_keine_luecke(self):
        self.maske(np.abs(self.p[self.f].mean(1)[:, 0]) < 0.02)
        self.assertIsNone(self.o.luecke(self.x, self.d))

    def test_stueck_ohne_becken_keine_luecke(self):
        self.maske(np.zeros(len(self.f), dtype=bool))
        self.assertIsNone(self.o.luecke(self.x, self.d))

    def test_vierteln(self):
        t = self.k.t
        x, df = self.k.feld(self.p, t.float64), self.k.feld(self.f, t.int64)
        x2, df2 = self.o._vierteln(x, df)
        self.assertEqual(len(df2), 4 * len(df))

        def inhalt(q, g):
            return float((0.5 * t.cross(q[g[:, 1]] - q[g[:, 0]], q[g[:, 2]] - q[g[:, 0]], dim=1).norm(dim=1)).sum())

        self.assertAlmostEqual(inhalt(x, df), inhalt(x2, df2), places=9)

    def test_attrappe_passt(self):
        from mesh3dai_kleider_verdeckung import Kleiderverdeckung
        echte = set(inspect.signature(Kleiderverdeckung.masken).parameters)
        self.assertLessEqual(echte, set(inspect.signature(Deckung.masken).parameters))
