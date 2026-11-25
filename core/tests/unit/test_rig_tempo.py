# -*- coding: utf-8 -*-
u"""Bausteine des Schritts „rig“, die seit 25.11.2026 schneller sind (Edgar: „muss alles 20 Mal schneller werden“) und dasselbe rechnen müssen.

1. `Mpnetzgraph`: der erste Aufruf rechnet, der zweite nimmt auf, ab dann Wiedergabe — gleiche Zahlen, eigene Kopien (die Ausgabe des einen Aufrufs ändert der nächste nicht), je Form
   ein Graph, mit Ableitung ohne Graph, ein Netz mit Wartepunkt rechnet weiter wie bisher.
2. `Zufallskumuliert`: die Verteilung ist die fortlaufende Summe Wert für Wert; dieselben Gewichte geben das gemerkte Feld, andere nicht; falsche Gewichte werfen wie numpy.
3. `Trimeshnormalen` = `trimesh.vertex_normals` (nach Eckwinkeln).
4. `Meshfiguransichten._lage`: das stehende Netz mit der Lage seit dem Bau = das bewegte Netz.

Sabotage (nicht gelaufen — Tests nur auf Ansage): in `Mpnetzgraph.__call__` `a.clone()` durch `a` ersetzen → Fall 1 rot; in `Zufallskumuliert` `torch.equal` durch `True` → Fall 2 rot;
in `Trimeshnormalen` das `winkel` weglassen → Fall 3 rot; in `_lage` die Reihenfolge der Matrizen tauschen → Fall 4 rot. Geschrieben, nicht gelaufen.
"""
import itertools
import sys
import unittest
from types import SimpleNamespace

import torch
import trimesh
from django.conf import settings

for _p in (str(settings.TOOLS_ROOT), str(settings.TOOLS_ROOT / 'meshto3d')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from KoerperKI_alle.trimeshnormalen import Trimeshnormalen  # noqa: E402
from KoerperKI_alle.zufallskumuliert import Zufallskumuliert  # noqa: E402
from MediapipeTorch.netzgraph import Mpnetzgraph  # noqa: E402
from meshfigur_ansichten import Meshfiguransichten  # noqa: E402

KARTE = 'cuda'


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class NetzgraphTest(unittest.TestCase):

    def test_1_gleich_und_eigene_kopien(self):
        w = torch.arange(12.0, device=KARTE).reshape(4, 3)
        rechnen = lambda x: [torch.tanh(x @ w), (x * x).sum(1)]
        netz = Mpnetzgraph(rechnen)
        ein = [torch.rand(5, 4, device=KARTE, generator=torch.Generator(device=KARTE).manual_seed(k)) for k in range(4)]
        aus = [netz(x) for x in ein]
        for x, a in zip(ein, aus, strict=True):
            self.assertTrue(all(torch.equal(p, q) for p, q in zip(a, rechnen(x), strict=True)))
        self.assertEqual(len(netz._graphen), 1)

    def test_1b_ohne_graph(self):
        netz = Mpnetzgraph(lambda x: [x * 2.0])
        x = torch.ones(3, device=KARTE, requires_grad=True)
        for _ in range(3):
            netz(x)[0].sum().backward()
        self.assertEqual(netz._graphen, {})
        wartet = Mpnetzgraph(lambda y: [y * float(y.sum())])          # ein Wartepunkt passt in keinen Graphen
        y = torch.ones(3, device=KARTE)
        with self.assertLogs('core', 'WARNING'):
            self.assertEqual([wartet(y)[0].tolist() for _ in range(3)], [[3.0] * 3] * 3)


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class VerteilungTest(unittest.TestCase):

    def test_2_verteilung(self):
        p = torch.rand(5000, device=KARTE, dtype=torch.float64, generator=torch.Generator(device=KARTE).manual_seed(1)) ** 3
        p = p / p.sum()
        soll = list(itertools.accumulate(p.tolist()))
        cdf = Zufallskumuliert.verteilung(p, len(p))
        self.assertEqual(cdf.tolist(), [w / soll[-1] for w in soll])
        self.assertIs(Zufallskumuliert.verteilung(p.clone(), len(p)), cdf)
        anders = p.clone()
        anders[[3, 4]] = anders[[4, 3]]
        self.assertIsNot(Zufallskumuliert.verteilung(anders, len(p)), cdf)
        for falsch in ([0.5, 0.6], [1.5, -0.5], [float('nan'), 1.0]):
            with self.assertRaises(ValueError):
                Zufallskumuliert.verteilung(torch.tensor(falsch, dtype=torch.float64, device=KARTE), 2)


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class BildnetzTest(unittest.TestCase):

    def test_3_punktnormalen(self):
        netz = trimesh.creation.icosphere(subdivisions=2)
        netz.vertices[:, 1] *= 0.4
        soll = torch.as_tensor(netz.vertex_normals.copy(), device=KARTE)
        ist = Trimeshnormalen.rechnen(torch.as_tensor(netz.vertices.copy(), device=KARTE), torch.as_tensor(netz.faces.copy(), device=KARTE))
        self.assertLess(float((ist - soll).abs().max()), 1e-9)

    def test_4_lage_seit_dem_bau(self):
        bau = torch.eye(4, dtype=torch.float64, device=KARTE)
        bau[:3, 3] = torch.tensor([0.1, -0.2, 0.3], device=KARTE)
        jetzt = bau.clone()
        jetzt[:2, :2] = torch.tensor([[0.0, -1.0], [1.0, 0.0]], device=KARTE)
        jetzt = jetzt @ bau
        a = Meshfiguransichten(SimpleNamespace(matrix=jetzt))
        a._bau = bau
        roh = torch.tensor([0.4, 1.2, -0.7, 1.0], dtype=torch.float64, device=KARTE)
        self.assertLess(float((a._lage() @ (bau @ roh) - jetzt @ roh).abs().max()), 1e-12)
