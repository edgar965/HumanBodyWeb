"""`Kostuemstoffsaum` auf Kunstdaten (06.11.2026, weiße Linie am Saum im Render von Edgar 1).
    1  Rand in Hautfarbe: nimmt Farbe und UV aus dem Stoff dahinter
    2  weißer Besatz auf dunklem Stoff bleibt
    3  ein Stück im Hautton bleibt ganz
    4  eine UV-Naht ist kein Rand
    5  die Quelle bleibt auf derselben Insel der Karte
Sabotage (von Hand): in `stueck` die Bedingung `rest < DELTA_E` weglassen → Fall 2 rot; `_trennt` immer den Stoff → Fall 3 rot; in `_weg` ohne Verschweißen → Fall 4 rot.
"""
import sys
import unittest

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'meshgenesis'))

S = 0.002
HAUT = (225.0, 183.0, 165.0)
STOFF = (70.0, 80.0, 150.0)
DUNKEL = (30.0, 30.0, 45.0)
WEISS = (250.0, 250.0, 250.0)


def gitter(x0, x1, y0, y1):
    """Rechteck aus Dreiecken in z = 0 → Punkte, Dreiecke."""
    xs, ys = np.arange(x0, x1 + S / 2, S), np.arange(y0, y1 + S / 2, S)
    nx, ny = len(xs), len(ys)
    p = np.stack([np.tile(xs, ny), np.repeat(ys, nx), np.zeros(nx * ny)], 1)
    i, j = np.meshgrid(np.arange(nx - 1), np.arange(ny - 1))
    a = (j * nx + i).ravel()
    b, c, d = a + 1, a + nx + 1, a + nx
    return p, np.concatenate([np.stack([a, b, c], 1), np.stack([a, c, d], 1)])


def randabstand(p):
    """Abstand jedes Punkts zum Rand des Rechtecks."""
    return np.minimum.reduce([p[:, 0] - p[:, 0].min(), p[:, 0].max() - p[:, 0], p[:, 1] - p[:, 1].min(), p[:, 1].max() - p[:, 1]])


@unittest.skipUnless(__import__('torch').cuda.is_available(), 'Kostuemgpu rechnet nur auf der Karte')
class Fall(unittest.TestCase):
    def setUp(self):
        from meshgenesis_kostuem_hautfarbe import Kostuemhautfarbe
        from meshgenesis_kostuem_stoffsaum import Kostuemstoffsaum
        from meshgenesis_kostuemgpu import Kostuemgpu
        self.k = k = Kostuemgpu.an()
        t = k.t
        self.o = Kostuemstoffsaum(Kostuemhautfarbe.lab_aus_rgb(t.tensor([HAUT], dtype=t.float64, device=k.g))[0])

    def stueck(self, p, f, rgb, uv=None):
        k, t = self.k, self.k.t
        return {'id': 'x', 'art': 'hose', 'punkte_gpu': k.feld(p, t.float64), 'dreiecke': f, 'farben': None, 'farbe_je_punkt': k.feld(np.asarray(rgb, dtype=np.uint8), t.uint8),
                'uv': p[:, :2].copy() if uv is None else uv}

    def test_hautrand_nimmt_stoff(self):
        p, f = gitter(-0.05, 0.05, 0.0, 0.06)
        rgb = np.tile(STOFF, (len(p), 1))
        rand = randabstand(p) < 0.0035
        rgb[rand] = HAUT
        st = self.stueck(p, f, rgb)
        self.assertGreater(self.o.stueck(st, 1.0), 0)
        neu = st['farbe_je_punkt'].cpu().numpy()
        self.assertTrue(bool((np.abs(neu - np.array(STOFF)).max(1) < 2).all()))
        uv = st['uv'][rand]
        rahmen = np.minimum.reduce([uv[:, 0] - p[:, 0].min(), p[:, 0].max() - uv[:, 0], uv[:, 1] - p[:, 1].min(), p[:, 1].max() - uv[:, 1]])
        self.assertTrue(bool((rahmen >= self.o.BAND_M - 1e-6).all()))

    def test_weisser_besatz_bleibt(self):
        p, f = gitter(-0.05, 0.05, 0.0, 0.06)
        rgb = np.tile(DUNKEL, (len(p), 1))
        rgb[randabstand(p) < 0.0035] = WEISS
        st = self.stueck(p, f, rgb)
        self.assertEqual(self.o.stueck(st, 1.0), 0)

    def test_stoff_im_hautton_bleibt(self):
        p, f = gitter(-0.05, 0.05, 0.0, 0.06)
        rgb = np.tile((215.0, 175.0, 160.0), (len(p), 1))
        rgb[randabstand(p) < 0.0035] = HAUT
        st = self.stueck(p, f, rgb)
        self.assertEqual(self.o.stueck(st, 1.0), 0)

    def _zwei_inseln(self):
        """Zwei Rechtecke, Naht bei x = 0: gleiche Lage, andere UV."""
        pa, fa = gitter(-0.05, 0.0, 0.0, 0.06)
        pb, fb = gitter(0.0, 0.05, 0.0, 0.06)
        p = np.concatenate([pa, pb])
        f = np.concatenate([fa, fb + len(pa)])
        uv = np.concatenate([pa[:, :2], pb[:, :2] + [0.5, 0.0]])
        return p, f, uv, len(pa)

    def test_uv_naht_ist_kein_rand(self):
        k, t = self.k, self.k.t
        p, f, _uv, _n = self._zwei_inseln()
        d = self.o._weg(k.feld(p, t.float64), k.feld(f, t.int64)).cpu().numpy()
        naht = (np.abs(p[:, 0]) < 1e-9) & (p[:, 1] > 0.02) & (p[:, 1] < 0.04)
        self.assertTrue(bool((d[naht] >= self.o.BAND_M - 1e-9).all()))

    def test_quelle_auf_derselben_insel(self):
        p, f, uv, n = self._zwei_inseln()
        rgb = np.tile(STOFF, (len(p), 1))
        rgb[(p[:, 1] < 0.0035)] = HAUT
        st = self.stueck(p, f, rgb, uv)
        self.assertGreater(self.o.stueck(st, 1.0), 0)
        self.assertTrue(bool((st['uv'][:n, 0] < 0.25).all()))
        self.assertTrue(bool((st['uv'][n:, 0] > 0.25).all()))
