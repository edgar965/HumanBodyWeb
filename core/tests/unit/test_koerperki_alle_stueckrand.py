"""Gemeinsame Saum-Bausteine `KoerperKI_alle.Stueckrand` und `KoerperKI_alle.Isoschnitt` (01.11.2026, Edgar: „lege auch die Saumbausteine und alle anderen Bausteine mit mesh3d-ai
zusammen“) — an einer Kunstfläche (Gitter 21 × 21, Kanten 1 cm, Höhe verrauscht), ohne Figur.

1. `randabstand` = scipy `dijkstra(min_only, limit)`, den `Schichtsaum` bis 01.11.2026 rechnete — Wert für Wert gleich.
2. `Isoschnitt.schneiden` an einem linearen Feld: alle neuen Randpunkte liegen auf seiner Nulllinie, kein Punkt außerhalb bleibt.
3. `umschlag`: jede Kopie liegt `ueber_haut` über ihrem Käfigpunkt längs der Normale, zwei Wanddreiecke je Randkante.
4. `glaetten` am zackigen Rand: die Randschleife wird kürzer, Punkte abseits von Rand und Band bleiben stehen.
"""
import sys
import unittest

import numpy as np
import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_alle.isoschnitt import Isoschnitt  # noqa: E402
from KoerperKI_alle.stueckrand import Stueckrand  # noqa: E402

N, KANTE = 21, 0.01


def flaeche():
    r = np.random.default_rng(7)
    x, y = np.meshgrid(np.arange(N) * KANTE, np.arange(N) * KANTE, indexing='ij')
    p = np.stack([x.ravel(), y.ravel(), 0.001 * r.standard_normal(N * N)], 1)
    d = []
    for i in range(N - 1):
        for j in range(N - 1):
            a, b, c, e = i * N + j, i * N + j + 1, (i + 1) * N + j, (i + 1) * N + j + 1
            d += [[a, c, b], [b, c, e]]
    return torch.tensor(p, dtype=torch.float64), torch.tensor(d)


class Stueckrandtest(unittest.TestCase):

    def test_1_randabstand_wie_dijkstra(self):
        from scipy.sparse import coo_matrix
        from scipy.sparse.csgraph import dijkstra
        p, d = flaeche()
        alle, rk, _e, _s = Stueckrand.kanten(d)
        quelle = torch.zeros(len(p), dtype=torch.bool)
        quelle[rk.reshape(-1)] = True
        grenze = 0.045
        neu = Stueckrand.randabstand(p, alle, quelle, grenze).numpy()
        a, b = alle[:, 0].numpy(), alle[:, 1].numpy()
        lang = np.linalg.norm(p.numpy()[a] - p.numpy()[b], axis=1)
        graph = coo_matrix((np.concatenate([lang, lang]), (np.concatenate([a, b]), np.concatenate([b, a]))), shape=(len(p), len(p))).tocsr()
        alt = dijkstra(graph, indices=np.unique(rk.numpy()), min_only=True, limit=grenze)
        self.assertTrue(np.array_equal(np.isinf(alt), np.isinf(neu)))
        endlich = np.isfinite(alt)
        self.assertGreater(int(endlich.sum()), 4 * (N - 1))
        self.assertLess(float(np.abs(alt[endlich] - neu[endlich]).max()), 1e-15)

    def test_2_isoschnitt_rand_auf_der_nulllinie(self):
        p, d = flaeche()
        feld = p[:, 1] - 0.0733
        aus = Isoschnitt.schneiden(feld, d, werte={'p': p}, strikt=True)
        self.assertGreater(int(aus['rand'].sum()), N - 2)
        self.assertLess(float((aus['p'][aus['rand'], 1] - 0.0733).abs().max()), 1e-12)
        self.assertGreaterEqual(float(aus['p'][:, 1].min()), 0.0733 - 1e-12)
        self.assertEqual(int(aus['dreiecke'].max()) + 1, len(aus['p']))

    def test_3_umschlag_ueber_der_haut(self):
        p, d = flaeche()
        normalen = torch.tensor([[0.0, 0.0, 1.0]], dtype=torch.float64).expand(len(p), 3).contiguous()
        ruhe = p - 0.004 * normalen
        herkunft = torch.arange(len(p))
        _alle, rk, _e, _s = Stueckrand.kanten(d)
        pn, dn, hn, _uv = Stueckrand.umschlag(p, d, herkunft, ruhe, normalen, 0.001)
        kopie = pn[len(p):]
        self.assertEqual(len(kopie), len(torch.unique(rk)))
        self.assertEqual(len(dn), len(d) + 2 * len(rk))
        self.assertLess(float(((kopie - ruhe[hn[len(p):]]) @ torch.tensor([0.0, 0.0, 1.0], dtype=torch.float64) - 0.001).abs().max()), 1e-12)

    def test_4_glaetten_kuerzt_den_zackigen_rand(self):
        p, d = flaeche()
        r = torch.Generator().manual_seed(3)
        alle, rk, _e, _s = Stueckrand.kanten(d)
        rand = torch.zeros(len(p), dtype=torch.bool)
        rand[rk.reshape(-1)] = True
        zackig = p.clone()
        zackig[rand, :2] += 0.003 * (torch.rand((int(rand.sum()), 2), generator=r, dtype=torch.float64) - 0.5)
        abstand = Stueckrand.randabstand(zackig, alle, rand, 0.03)
        glatt = Stueckrand.glaetten(zackig, alle, rk, abstand < 0.02, 15, 0.5, -0.53)

        def laenge(x):
            return float((x[rk[:, 0]] - x[rk[:, 1]]).norm(dim=1).sum())
        self.assertLess(laenge(glatt), laenge(zackig) * 0.97)
        fern = torch.isinf(abstand)
        self.assertGreater(int(fern.sum()), 0)
        self.assertTrue(torch.equal(glatt[fern], zackig[fern]))


if __name__ == '__main__':
    unittest.main()
