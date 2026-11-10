"""`Kostuemverwachsung.trennen` auf Kunstdaten (04.11.2026, Edgar zu Session3dTools: „export hat noch stachel und andere Artefakte“): ein Streifen Stoff über Arm und Bauch.
    1  Arm und Bauch berühren sich im Stand, in Ruhe liegen sie weit auseinander: der Stoff wird aufgetrennt, keine Fläche fehlt, die Kopien liegen genau auf ihren Punkten
    2  in Ruhe nah beieinander (Schulter): nichts wird getrennt
    3  die Haut des Arms zeigt gegen den Stoff (Flicken unter dem Arm): der Stoff bleibt beim Rumpf, nichts wird getrennt
    4  der Arm trägt das Stück nicht (`glieder`): nichts wird getrennt
    5  Flicken gehören immer zum Rest (Lauf 12: sie wanderten mit dem Ärmel)
    6  eine kleine Insel geht an die Seite, die sie umgibt
    7  `Kostuemergaenzung._graph` verschweißt die Kopien nicht wieder
Sabotage (von Hand): in `_seiten` den Normalen-Vergleich weglassen → Fall 3 rot; `RUHE_M` auf 2 → Fall 1 rot, auf 0 → Fall 2 rot; in `trennen` `rest` nicht anwenden → Fall 5 rot; `INSEL_MIN` auf 0 → Fall 6 rot;
in `_graph` `trenn` nicht verwenden → Fall 7 rot.
"""
import sys
import unittest
from types import SimpleNamespace

import numpy as np
import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'meshgenesis'))


class Rueck:
    """Das Nötige von `Kostuemrueckhaeutung`: Käfig aus zwei Flecken, Arm links im Bild, Bauch rechts."""
    abschnitte = ['Oberarm rechts', 'Unterarm rechts']

    def __init__(self, k, abstand_ruhe=1.0, arm_normale=1.0, ohne=()):
        self.k, self.ohne = k, ohne
        x, y = np.meshgrid(np.arange(-0.10, 0.101, 0.02), np.arange(0.0, 0.201, 0.02), indexing='ij')
        flecken = np.stack([x.ravel(), y.ravel(), np.zeros(x.size)], 1)
        self.abschnitt = np.where(flecken[:, 0] < 0, 1, -1)
        ruhe = flecken.copy()
        ruhe[self.abschnitt == 1, 0] -= abstand_ruhe
        self.q = SimpleNamespace(kaefig_ruhe=ruhe)
        self.kaefig = k.feld(flecken, k.t.float64)
        normalen = np.tile([0.0, 0.0, 1.0], (len(flecken), 1))
        normalen[self.abschnitt == 1, 2] = arm_normale
        self.haut_normale = k.feld(normalen, k.t.float64)

    def glieder(self, _x, _traeger, _dreiecke):
        return self.ohne, None

    def _naechste(self, x, traeger, ohne=()):
        maske = ~np.isin(self.abschnitt, list(ohne))
        if traeger == ('arm',):
            maske &= self.abschnitt >= 0
        wahl = self.k.feld(np.nonzero(maske)[0], self.k.t.int64)
        return wahl[torch.cdist(x, self.kaefig[wahl]).argmin(1)]


class TrennenTest(unittest.TestCase):
    databases = []
    TRAEGER = ('rumpf', 'arm')

    def setUp(self):
        from meshgenesis_kostuemgpu import Kostuemgpu
        self.k = Kostuemgpu.an()
        x, y = np.meshgrid(np.arange(-0.09, 0.0901, 0.01), np.arange(0.01, 0.191, 0.01), indexing='ij')
        self.x = np.stack([x.ravel(), y.ravel(), np.full(x.size, 0.02)], 1)
        n, m = x.shape
        i = np.arange(n * m).reshape(n, m)
        a, b, c, d = i[:-1, :-1].ravel(), i[1:, :-1].ravel(), i[1:, 1:].ravel(), i[:-1, 1:].ravel()
        self.f = np.concatenate([np.stack([a, b, c], 1), np.stack([a, c, d], 1)])
        self.st = {'id': 's', 'art': 'oberteil', 'punkte': self.x, 'dreiecke': self.f, 'uv': self.x[:, :2], 'farben': None}

    def _trennen(self, **rueck):
        from meshgenesis_kostuem_verwachsung import Kostuemverwachsung as V
        return V(Rueck(self.k, **rueck)).trennen(self.st, self.x, self.x, self.TRAEGER)

    def test_arm_und_bauch_werden_getrennt(self):
        st, x, _p, trenn, befund = self._trennen()
        self.assertIsNotNone(trenn)
        self.assertGreater(befund['kopien'], 0)
        self.assertEqual(len(st['dreiecke']), len(self.f))                     # keine Fläche fehlt
        self.assertEqual(len(x), len(self.x) + befund['kopien'])
        self.assertEqual(len(st['uv']), len(x))
        np.testing.assert_array_equal(x[:len(self.x)], self.x)
        seite = trenn.cpu().numpy()[st['dreiecke']]
        gemischt = seite.min(1) != seite.max(1)
        self.assertFalse(gemischt[self.x[self.f].mean(1)[:, 0] < 1.0].any())   # kein Dreieck spannt mehr über die Berührung
        flaeche = np.linalg.norm(np.cross(x[st['dreiecke'][:, 1]] - x[st['dreiecke'][:, 0]], x[st['dreiecke'][:, 2]] - x[st['dreiecke'][:, 0]]), axis=1).sum()
        alt = np.linalg.norm(np.cross(self.x[self.f[:, 1]] - self.x[self.f[:, 0]], self.x[self.f[:, 2]] - self.x[self.f[:, 0]]), axis=1).sum()
        self.assertAlmostEqual(flaeche, alt, places=9)                         # im Stand dieselbe Fläche

    def _ganz(self, ergebnis):
        """Fassung 2: kein Riss heißt Stück unverändert, die Seiten bleiben für das Binden."""
        st, x, _p, trenn, befund = ergebnis
        self.assertEqual(befund['kopien'], 0)
        self.assertEqual(len(x), len(self.x))
        np.testing.assert_array_equal(st['dreiecke'], self.f)
        self.assertEqual(len(trenn), len(self.x))
        return trenn.cpu().numpy()

    def test_schulter_bleibt_ganz(self):
        self.assertTrue((self._ganz(self._trennen(abstand_ruhe=0.0)) > 0).any())

    def test_haut_zeigt_gegen_den_stoff(self):
        self.assertFalse(self._ganz(self._trennen(arm_normale=-1.0)).any())     # die Flanke neben dem Arm: alles Rest, auch ohne Riss

    def test_arm_traegt_nicht(self):
        self.assertIsNone(self._trennen(ohne=(0, 1))[3])

    def test_flicken_bleiben_beim_rest(self):
        self.st['flicken'] = self.x[:, 0] < 0                                  # alles über dem Arm ist Flicken: nichts geht mit dem Arm, also kein Riss
        self.assertFalse(self._ganz(self._trennen()).any())

    def test_kleine_insel_geht_an_die_umgebung(self):
        from meshgenesis_kostuem_verwachsung import Kostuemverwachsung as V
        v = V(Rueck(self.k))
        t = self.k.t
        n = 30
        e = self.k.feld(np.stack([np.arange(n - 1), np.arange(1, n)], 1), t.int64)
        seite = t.zeros(n, dtype=t.int64, device=self.k.g)
        seite[10:12] = 2
        self.assertEqual(int(v._inseln(seite, e, n).sum()), 0)

    def test_kopien_bleiben_getrennt(self):
        from meshgenesis_kostuem_ergaenzung import Kostuemergaenzung
        st, x, _p, trenn, _b = self._trennen()
        e = Kostuemergaenzung()
        self.assertEqual(e._graph(x, st['dreiecke'])[1], len(self.x))
        self.assertEqual(e._graph(x, st['dreiecke'], trenn)[1], len(x))
