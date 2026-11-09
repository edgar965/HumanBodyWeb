"""`Kantenrechnung.calc_edges` gegen die Rechnung des Originals (`torch.unique(dim=0)`), kleine Netze auf der CPU."""
import sys
import unittest
from pathlib import Path

import torch
from django.conf import settings

sys.path.insert(0, str(Path(settings.TOOLS_ROOT) / 'pshuman_port14'))
from kantenrechnung import Kantenrechnung  # noqa: E402


def original(faces):
    """`core.remesh.calc_edges` Z. 41–62 von PSHuman, ohne `torch_scatter` im Import."""
    f = faces.shape[0]
    voll = torch.stack((faces, faces.roll(-1, 1)), dim=-1).reshape(f * 3, 2)
    sortiert, _ = voll.sort(dim=-1)
    edges, zu = torch.unique(input=sortiert, sorted=True, return_inverse=True, dim=0)
    e = edges.shape[0]
    rechts = voll[:, 0] != sortiert[:, 0]
    edge_to_face = torch.zeros((e, 2, 2), dtype=torch.long)
    quelle = torch.cartesian_prod(torch.arange(0, f), torch.arange(0, 3))
    edge_to_face.reshape(2 * e, 2).scatter_(dim=0, index=(2 * zu + rechts)[:, None].expand(f * 3, 2), src=quelle)
    edge_to_face[0] = 0
    return edges, zu.reshape(f, 3), edge_to_face


class KantenrechnungTest(unittest.TestCase):
    def _gleich(self, faces):
        for a, b in zip(original(faces), Kantenrechnung.calc_edges(faces, True), strict=True):
            self.assertTrue(torch.equal(a, b))

    def test_tetraeder_mit_leerem_ersten_dreieck(self):
        self._gleich(torch.tensor([[0, 0, 0], [1, 2, 3], [1, 3, 4], [1, 4, 2], [2, 4, 3]]))

    def test_zufaellige_dreiecke(self):
        torch.manual_seed(1)
        roh = torch.stack([torch.randperm(500)[:3] for _ in range(400)]) + 1
        self._gleich(torch.cat((torch.zeros((1, 3), dtype=torch.long), roh)))

    def test_ohne_edge_to_face_zwei_werte(self):
        self.assertEqual(len(Kantenrechnung.calc_edges(torch.tensor([[0, 0, 0], [1, 2, 3]]))), 2)
