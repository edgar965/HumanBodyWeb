"""Gemeinsamer Baustein `KoerperKI_alle.Flaechenstuecke` (01.11.2026, statt `csgraph.connected_components`
in `Vorstufenluecken.gekippt`) — an Kunstgraphen, CPU, ohne Figur.

1. Drei getrennte Gitter, gemischt nummeriert, dazu einzelne Knoten: jede Marke ist die kleinste Nummer
   ihres Stücks, die Einteilung gleich der von csgraph.
2. Eine lange Kette (mehr Runden als `PRUEFEN_JE`, Nummern absteigend): alle Knoten bekommen die 0.
3. `dreiecke` gleich `marken` über die drei Kanten jedes Dreiecks.
"""
import sys
import unittest

import numpy as np
import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_alle.flaechenstuecke import Flaechenstuecke  # noqa: E402


def gitter(n, ab):
    i = torch.arange(n * n).reshape(n, n) + ab
    links = torch.stack([i[:-1, :-1], i[1:, :-1], i[:-1, 1:]], -1).reshape(-1, 3)
    rechts = torch.stack([i[1:, :-1], i[1:, 1:], i[:-1, 1:]], -1).reshape(-1, 3)
    return torch.cat([links, rechts])


def kanten(d):
    return torch.cat([d[:, [0, 1]], d[:, [1, 2]], d[:, [2, 0]]])


class Flaechenstueckeprobe(unittest.TestCase):

    def test_1_kleinste_nummer_und_einteilung_wie_csgraph(self):
        from scipy import sparse
        from scipy.sparse import csgraph

        n = 74 + 81 + 4
        mischen = torch.randperm(n, generator=torch.Generator().manual_seed(3))
        d = mischen[torch.cat([gitter(7, 0), gitter(5, 49), gitter(9, 74)])]
        marke = Flaechenstuecke.dreiecke(n, d)
        k = kanten(d).numpy()
        graph = sparse.csr_matrix((np.ones(len(k)), (k[:, 0], k[:, 1])), shape=(n, n))
        _, cs = csgraph.connected_components(graph, directed=False)
        for s in np.unique(cs):
            knoten = np.flatnonzero(cs == s)
            self.assertEqual(set(marke[knoten].tolist()), {int(knoten.min())})
        self.assertEqual(len(set(marke.tolist())), len(np.unique(cs)))

    def test_2_lange_kette(self):
        n = 200
        k = torch.stack([torch.arange(n - 1, 0, -1), torch.arange(n - 2, -1, -1)], 1)
        self.assertTrue(bool((Flaechenstuecke.marken(n, k) == 0).all()))

    def test_3_dreiecke_gleich_marken(self):
        d = gitter(6, 0)
        self.assertTrue(torch.equal(Flaechenstuecke.dreiecke(40, d), Flaechenstuecke.marken(40, kanten(d))))


if __name__ == '__main__':
    unittest.main()
