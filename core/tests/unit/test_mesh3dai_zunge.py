"""`Kostuemzunge` auf Kunstdaten (06.11.2026, Edgar zu Edgar 1: „hat fehler in der Unterhose, da hängt ein stück in der Luft“, „fixe generisch“).
    1  eine Platte mit Zunge in der Mitte des Unterrands: die Zunge wird gefunden, die Platte bleibt
    2  zwei Anbindungen: ein Steg zwischen zwei Platten bleibt
    3  nicht nah an beiden Beinen: dieselbe Zunge bleibt
    4  aufliegend (Normale wie die Haut): dieselbe Zunge bleibt
    5  zu klein: unter `FLAECHE_MIN_M2` bleibt sie
    6  `Kostuemschnitt._ohne` nimmt die Flächen heraus und nummeriert die Inseln dicht
    7  Steg: Insel im Spalt am Saum wird gefunden, die Platte bleibt
    8  ohne Saum im Spalt bleibt sie
    9  auf der Haut liegend bleibt sie
   10  größer als `STEG_MAX_M2` bleibt sie
   11  `steg_anlegen`: keine Fläche quer über die Mitte, Punkte bleiben, der Steg liegt an der Haut, fern davon rührt sich nichts
Sabotage (von Hand): in `flaechen` die Bedingung `_anbindungen … <= 1` weglassen → Fall 2 rot; `spalt` immer wahr → Fall 3 rot; `COS_MAX` auf 2 → Fall 4 rot.
"""
import sys
import unittest

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


def gitter(x0, x1, y0, y1, schritt):
    """Rechteck aus Dreiecken in z = 0, Normale +z → Punkte, Dreiecke."""
    xs, ys = np.arange(x0, x1 + schritt / 2, schritt), np.arange(y0, y1 + schritt / 2, schritt)
    nx, ny = len(xs), len(ys)
    p = np.stack([np.tile(xs, ny), np.repeat(ys, nx), np.zeros(nx * ny)], 1)
    i, j = np.meshgrid(np.arange(nx - 1), np.arange(ny - 1))
    a = (j * nx + i).ravel()
    b, c, d = a + 1, a + nx + 1, a + nx
    return p, np.concatenate([np.stack([a, b, c], 1), np.stack([a, c, d], 1)])


def verbinde(*teile):
    punkte, flaechen, n = [], [], 0
    for p, f in teile:
        punkte.append(p)
        flaechen.append(f + n)
        n += len(p)
    return np.concatenate(punkte), np.concatenate(flaechen)


S = 0.005


def platte_mit_zunge(y_ende=-0.05, links=-0.01, rechts=0.01):
    """Platte 30 × 20 cm, darunter in der Mitte eine Zunge von `links` bis `rechts`, unten bis `y_ende`."""
    return verbinde(gitter(-0.15, 0.15, 0.0, 0.2, S), gitter(links, rechts, y_ende, 0.0, S))


@unittest.skipUnless(__import__('torch').cuda.is_available(), 'Kostuemgpu rechnet nur auf der Karte')
class Fall(unittest.TestCase):
    def setUp(self):
        from mesh3dai_kostuem_zunge import Kostuemzunge
        from mesh3dai_kostuemgpu import Kostuemgpu
        self.k = k = Kostuemgpu.an()
        self.z = Kostuemzunge.__new__(Kostuemzunge)
        self.z.k = k
        self.beine(0.02, 1.0)

    def beine(self, seite, nz):
        """Zwei Punktreihen links und rechts der Zunge; Käfig mit einer Normale je Punkt, `nz` gegen die Fläche der Zunge."""
        t = self.k.t
        y = np.arange(-0.06, 0.02, 0.005)
        li = np.stack([np.full_like(y, -seite), y, np.zeros_like(y)], 1)
        re = np.stack([np.full_like(y, seite), y, np.zeros_like(y)], 1)
        self.z.beine = [self.k.feld(li, t.float64), self.k.feld(re, t.float64)]
        self.z.kaefig = self.k.feld(np.concatenate([li, re]), t.float64)
        n = np.zeros((2 * len(y), 3))
        n[:, 2] = nz
        n[:, 0] = np.sqrt(max(0.0, 1.0 - nz * nz))
        self.z.normale = self.k.feld(n, self.k.t.float64)

    def anteil(self, p, f):
        maske, befund = self.z.flaechen(p, f)
        return maske.cpu().numpy(), befund

    def test_zunge_wird_gefunden(self):
        p, f = platte_mit_zunge()
        self.beine(0.02, 0.0)
        m, befund = self.anteil(p, f)
        self.assertEqual(int(befund['zahl']), 1)
        unten = p[f].mean(1)[:, 1] < -0.015          # die Wurzel gehört zur Anbindung
        self.assertTrue(bool(m[unten].all()))
        self.assertFalse(bool(m[p[f].mean(1)[:, 1] > 0.05].any()))

    def test_steg_mit_zwei_enden_bleibt(self):
        p, f = verbinde(gitter(-0.15, 0.15, 0.0, 0.2, S), gitter(-0.01, 0.01, -0.05, 0.0, S), gitter(-0.15, 0.15, -0.25, -0.05, S))
        self.beine(0.02, 0.0)
        m, _b = self.anteil(p, f)
        self.assertFalse(bool(m.any()))

    def test_fern_der_beine_bleibt(self):
        p, f = platte_mit_zunge()
        self.beine(0.3, 0.0)
        m, _b = self.anteil(p, f)
        self.assertFalse(bool(m.any()))

    def test_aufliegend_bleibt(self):
        p, f = platte_mit_zunge()
        self.beine(0.02, 1.0)
        m, _b = self.anteil(p, f)
        self.assertFalse(bool(m.any()))

    def test_zu_klein_bleibt(self):
        p, f = platte_mit_zunge(y_ende=-0.005, links=-0.005, rechts=0.0)
        self.beine(0.02, 0.0)
        m, _b = self.anteil(p, f)
        self.assertFalse(bool(m.any()))

    def test_schnitt_nimmt_heraus(self):
        from mesh3dai_kostuem_schnitt import Kostuemschnitt
        t = self.k.t
        s = Kostuemschnitt.__new__(Kostuemschnitt)
        s.k = self.k
        idx = self.k.feld(np.array([4, 5, 6, 7]), t.int64)
        insel = self.k.feld(np.array([0, 2, 2, 5]), t.int64)
        weg = self.k.feld(np.array([False, True, False, False]), t.bool)
        neu_idx, neu_insel = s._ohne(idx, insel, weg)
        self.assertEqual(neu_idx.tolist(), [4, 6, 7])
        self.assertEqual(neu_insel.tolist(), [0, 1, 2])
        self.assertEqual(s._ohne(idx, insel, ~(weg | True))[0].tolist(), idx.tolist())

    def beine_steg(self, y0, y1, z=0.015):
        """Beine als Punktreihen vor der Platte: Käfig gleich den Beinen, darum steht die Platte `z` von der Haut."""
        t = self.k.t
        y = np.arange(y0, y1, 0.005)
        li = np.stack([np.full_like(y, -0.015), y, np.full_like(y, z)], 1)
        re = np.stack([np.full_like(y, 0.015), y, np.full_like(y, z)], 1)
        self.z.beine = [self.k.feld(li, t.float64), self.k.feld(re, t.float64)]
        self.z.kaefig = self.k.feld(np.concatenate([li, re]), t.float64)

    def steg(self, p, f):
        maske, befund = self.z.steg(p, f)
        return maske.cpu().numpy(), befund

    def test_steg_wird_gefunden(self):
        p, f = gitter(-0.15, 0.15, 0.0, 0.2, S)
        self.beine_steg(-0.06, 0.02)
        m, befund = self.steg(p, f)
        self.assertEqual(int(befund['zahl']), 1)
        self.assertTrue(bool(m.any()))
        self.assertFalse(bool(m[p[f].mean(1)[:, 1] > 0.08].any()))

    def test_steg_ohne_saum_bleibt(self):
        p, f = gitter(-0.15, 0.15, 0.0, 0.2, S)
        self.beine_steg(0.09, 0.11)
        m, _b = self.steg(p, f)
        self.assertFalse(bool(m.any()))

    def test_steg_auf_der_haut_bleibt(self):
        p, f = gitter(-0.15, 0.15, 0.0, 0.2, S)
        self.beine_steg(-0.06, 0.02)
        self.z.kaefig = self.k.feld(p, self.k.t.float64)
        m, _b = self.steg(p, f)
        self.assertFalse(bool(m.any()))

    def test_steg_zu_gross_bleibt(self):
        p, f = gitter(-0.15, 0.15, 0.0, 0.2, S)
        self.beine_steg(-0.06, 0.02)
        self.z.STEG_MAX_M2 = 1e-4
        m, _b = self.steg(p, f)
        self.assertFalse(bool(m.any()))

    def test_steg_anlegen(self):
        from types import SimpleNamespace
        t = self.k.t
        p, f = gitter(-0.15, 0.15, 0.0, 0.2, S)
        self.beine_steg(-0.06, 0.02)
        self.z.q = SimpleNamespace(s=1.0)
        n = self.z.kaefig.shape[0]
        self.z.normale = self.k.feld(np.tile([0.0, 0.0, -1.0], (n, 1)), t.float64)
        st = {'punkte_gpu': self.k.feld(p, t.float64), 'punkte': p.copy(), 'dreiecke': f.copy()}
        self.assertTrue(self.z.steg_anlegen(st))
        neu = st['punkte']
        self.assertEqual(len(neu), len(p))
        self.assertLess(len(st['dreiecke']), len(f))
        x, y = p[st['dreiecke']][:, :, 0], p[st['dreiecke']][:, :, 1]
        mitte = (x < -1e-9).any(1) & (x >= -1e-9).any(1) & (y < 0.015).all(1)
        self.assertFalse(bool(mitte.any()))
        self.assertTrue(bool((np.abs(neu - p).max(1)[p[:, 1] > 0.1] < 1e-9).all()))
        self.assertGreater(float(neu[:, 2].max()), 0.0)
