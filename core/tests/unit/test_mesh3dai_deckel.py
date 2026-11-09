"""`Kostuemdeckel` und die Naht in `Kostuembindung` auf Kunstdaten (05.11.2026, Edgar: „fixe die offenen punkte im Tanz“, „der code für den Animationsfix soll auch generisch sein!“).
    1  ein Deckel über einem Kreis: Ring 0 ist der Rand, kein offener Rand außer ihm, die Flächen laufen gegen den Rand des Stücks
    2  ein gewölbter Rand: die inneren Punkte liegen zwischen den Randhöhen (harmonisch)
    3  jenseits des Rands Haut: offen; jenseits ein anderes Stück: eine Naht, nichts zu schließen
    4  `_umlaeufe` findet die Schleife in der Richtung der Flächen
    5  `Kostuembindung._naht`: Randpunkte an derselben Stelle zweier Stücke, nicht die übrigen Randpunkte
Sabotage (von Hand): in `_deckel` die Flächen umdrehen → Fall 1 rot; in `offen` den Vergleich auf Haut weglassen → Fall 3 rot; in `_naht` `grenze` auf 1 m → Fall 5 rot.
"""
import math
import sys
import unittest

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


def platte(n=16, r=1.0):
    """Ring aus Dreiecken um ein Loch: außen Radius 2 r, innen r; → Punkte, Dreiecke (Normale +z), innere Schleife."""
    w = np.arange(n) * 2.0 * math.pi / n
    innen = np.stack([r * np.cos(w), r * np.sin(w), np.zeros(n)], 1)
    aussen = 2.0 * innen
    p = np.concatenate([innen, aussen])
    i, j = np.arange(n), (np.arange(n) + 1) % n
    f = np.concatenate([np.stack([i, i + n, j + n], 1), np.stack([i, j + n, j], 1)])
    return p, f


@unittest.skipUnless(__import__('torch').cuda.is_available(), 'Kostuemgpu rechnet nur auf der Karte')
class Fall(unittest.TestCase):
    def setUp(self):
        from mesh3dai_kostuem_deckel import Kostuemdeckel
        from mesh3dai_kostuemgpu import Kostuemgpu
        self.k = Kostuemgpu.an()
        self.d = Kostuemdeckel.__new__(Kostuemdeckel)
        self.d.k = self.k

    def test_deckel_schliesst_den_rand(self):
        t = self.k.t
        p, f = platte()
        rand = self.k.feld(p[:16], t.float64).flip(0)      # im Umlauf der Flächen der Platte: um das Loch im Uhrzeigersinn
        pos, df, ring = self.d._deckel(rand)
        self.assertTrue(bool((pos[:16] == rand).all()))
        self.assertEqual(int((ring == 0).sum()), 16)
        kanten = self.k.raender(df)
        self.assertEqual(sorted(t.unique(kanten).tolist()), list(range(16)))
        n = t.cross(pos[df[:, 1]] - pos[df[:, 0]], pos[df[:, 2]] - pos[df[:, 0]], dim=1)
        self.assertGreater(float(n[:, 2].min()), 0.0)

    def test_deckel_harmonisch(self):
        t = self.k.t
        p, _f = platte()
        p[:16, 2] = np.where(np.arange(16) % 2 == 0, 0.2, 0.0)
        pos, _df, ring = self.d._deckel(self.k.feld(p[:16], t.float64))
        innen = pos[ring > 0]
        self.assertGreaterEqual(float(innen[:, 2].min()), -1e-6)
        self.assertLessEqual(float(innen[:, 2].max()), 0.2 + 1e-6)

    def test_offen_oder_naht(self):
        from mesh3dai_kostuemarten import Kostuemarten
        t = self.k.t
        p, f = platte()
        pf = self.k.feld(p, t.float64)
        ff = self.k.feld(f, t.int64)
        for art, offen in ((Kostuemarten.nummer('haut'), True), (Kostuemarten.nummer('hose'), False)):
            # eine zweite Platte im Loch: Fächer um die Mitte mit eigener Art
            mitte = t.cat([pf, pf[:16].mean(0, keepdim=True)])
            i = self.k.feld(np.arange(16), t.int64)
            j = i.roll(-1)
            faecher = t.stack([j, i, t.full_like(i, 32)], 1)
            alle = t.cat([ff, faecher])
            arten = t.cat([t.full((len(ff),), Kostuemarten.nummer('oberteil'), device=self.k.g), t.full((16,), art, device=self.k.g)])
            self.assertEqual(self.d.offen(i, self.d._jenseits(mitte, alle, arten)), offen)

    def test_umlauf_in_richtung_der_flaechen(self):
        t = self.k.t
        p, f = platte()
        ff = self.k.feld(f, t.int64)
        fs, _erster = self.k.verschweisst(p, f)
        kanten = self.k.raender(fs)
        innen = kanten[(kanten < 16).all(1)]
        schleifen = self.d._umlaeufe(fs, innen)
        self.assertEqual(len(schleifen), 1)
        folge = schleifen[0][0]
        self.assertEqual(len(folge), 16)
        self.assertEqual(len(ff), len(fs))
        schritt = {(folge[i + 1] - folge[i]) % 16 for i in range(15)}
        self.assertEqual(len(schritt), 1)

    def test_naht(self):
        from mesh3dai_kostuem_bindung import Kostuembindung
        t = self.k.t
        p, f = platte()
        b = Kostuembindung.__new__(Kostuembindung)
        b.k = self.k
        zweite = p.copy()
        zweite[16:] *= 1.5                                 # äußerer Rand woanders, innerer gleich
        zweite = zweite + 0.0
        stuecke = [{'id': 'a', 'dreiecke': f}, {'id': 'b', 'dreiecke': f}]
        naht = b._naht(stuecke, {'a': self.k.feld(p, t.float64), 'b': self.k.feld(zweite, t.float64)})
        self.assertEqual(naht['a'][:16].tolist(), [True] * 16)
        self.assertEqual(naht['a'][16:].tolist(), [False] * 16)
