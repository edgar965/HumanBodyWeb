"""`Kostuemrandglatt` auf Kunstdaten (06.11.2026, gezackter Schnittrand an Edgar 1 und Edgar2010).
    1  ein Sägezahn am Rand wird gemessen, ein gerader Rand nicht
    2  die Glättung senkt das Maß unter die Grenze, Mitte der Platte bleibt
    3  Punkte an einem anderen Stück bleiben (Naht)
    4  die UV bleibt
    5  das Maß ist das von `Saummass`
    6  zur Naht hin läuft der Versatz am Rand aus
Sabotage (von Hand): `naht` immer falsch → Fall 3 rot; `v` nie anwenden → Fall 2 rot; Auslauf weglassen → Fall 6 rot.
"""
import sys
import unittest

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'meshgenesis'))

S = 0.002


def rohr(zacke=0.0):
    """Rohr (Radius 8 cm, 8 cm hoch) wie ein Hosenbein, unterer Rand um `zacke` im Wechsel versetzt → Punkte, Dreiecke, Punkte je Ring."""
    nx = 250
    ys = np.arange(0.0, 0.08 + S / 2, S)
    ny = len(ys)
    w = 2 * np.pi * np.arange(nx) / nx
    p = np.stack([0.08 * np.tile(np.cos(w), ny), np.repeat(ys, nx), 0.08 * np.tile(np.sin(w), ny)], 1)
    p[:nx, 1] += zacke * (2 * (np.arange(nx) % 2) - 1)
    i, j = np.meshgrid(np.arange(nx), np.arange(ny - 1))
    a = (j * nx + i).ravel()
    b = (j * nx + (i + 1) % nx).ravel()
    c, d = b + nx, a + nx
    return p, np.concatenate([np.stack([a, b, c], 1), np.stack([a, c, d], 1)]), nx


@unittest.skipUnless(__import__('torch').cuda.is_available(), 'Kostuemgpu rechnet nur auf der Karte')
class Fall(unittest.TestCase):
    def setUp(self):
        from meshgenesis_kostuem_randglatt import Kostuemrandglatt
        self.o = Kostuemrandglatt()
        self.k, self.t = self.o.k, self.o.k.t

    def stueck(self, p, f):
        return {'punkte_gpu': self.k.feld(p, self.t.float64), 'punkte': p.copy(), 'dreiecke': f, 'uv': p[:, :2].copy()}

    def zacke(self, p, f):
        return self.o.zacke(self.k.feld(p, self.t.float64), self.k.feld(f, self.t.int64))

    def test_saegezahn_wird_gemessen(self):
        p, f, _n = rohr(0.003)
        self.assertGreater(self.zacke(p, f), self.o.ZACKE_MAX_M)
        p, f, _n = rohr()
        self.assertLess(self.zacke(p, f), self.o.ZACKE_MAX_M)

    def test_glaettung_senkt_das_mass(self):
        p, f, _n = rohr(0.003)
        st = self.stueck(p, f)
        self.assertGreater(self.o.stueck(st, None, 1.0), 0)
        self.assertLess(self.zacke(st['punkte'], f), self.o.ZACKE_MAX_M)
        mitte = np.abs(p[:, 1] - 0.04) < 0.005
        self.assertLess(float(np.abs(st['punkte'] - p)[mitte].max()), 1e-9)

    def test_naht_bleibt(self):
        p, f, nx = rohr(0.003)
        st = self.stueck(p, f)
        self.o.stueck(st, self.k.feld(p[:nx], self.t.float64), 1.0)
        self.assertLess(float(np.abs(st['punkte'] - p)[:nx].max()), 1e-9)

    def test_mass_ist_das_der_foto_kette(self):
        from KoerperKI_Fotos.saummass import Saummass
        p, f, _n = rohr(0.003)
        q, fs, _rand = self.o._netz(self.k.feld(p, self.t.float64), self.k.feld(f, self.t.int64))
        soll = max(s['zacken_mm'] for s in Saummass.messen(q, fs)['saeume'])
        self.assertAlmostEqual(self.zacke(p, f), soll / 1e3, places=6)

    def test_versatz_laeuft_zur_naht_aus(self):
        p, f, nx = rohr(0.003)
        st = self.stueck(p, f)
        self.o.stueck(st, self.k.feld(p[:nx // 2], self.t.float64), 1.0)
        weg = np.linalg.norm(st['punkte'] - p, axis=1)[:nx]
        self.assertLess(float(weg[: nx // 2].max()), 1e-9)
        self.assertLess(float(weg[nx // 2]), float(weg[nx // 2 + 10:nx - 10].max()))

    def test_kurze_schleife_wird_nicht_eng(self):
        from KoerperKI_Fotos.saumkurve import Saumkurve
        self.assertAlmostEqual(Saumkurve._breite(0.155, 0.02), 0.00496, places=4)
        self.assertEqual(Saumkurve._breite(1.0, 0.02), Saumkurve.GLAETTE_M)
        self.assertEqual(Saumkurve._breite(0.155, None), Saumkurve.GLAETTE_M)

    def test_uv_bleibt(self):
        p, f, _n = rohr(0.003)
        st = self.stueck(p, f)
        uv = st['uv'].copy()
        self.o.stueck(st, None, 1.0)
        self.assertTrue(bool((st['uv'] == uv).all()))
