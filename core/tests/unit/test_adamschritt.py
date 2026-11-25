# -*- coding: utf-8 -*-
u"""`Adamschritt` und `Schrittgraph` — Adam bitgleich im CUDA-Graphen (25.11.2026, Edgar: „muss alles 20 Mal schneller werden“).

1. Wie `torch.optim.Adam` nach 40 Schritten, Zahl für Zahl: eine Gruppe, mehrere Gruppen mit eigener Lernrate und `eps`, andere `betas` (auch β1 = 0,5: der andere Zweig von `lerp`).
2. `geht` sagt nein, wo die Rechnung eine andere wäre (amsgrad, weight_decay, capturable, AdamW, float64).
3. `Schrittgraph.laufen` mit Klemmen im Graphen = die einfache Schleife; der Zustand zählt die Schritte, `opt.step()` geht danach weiter.
4. Eine Lernrate, die sich je Schritt ändert (`danach` ohne `danach_graph`), bleibt außerhalb des Graphen und wirkt.

Sabotage (nicht gelaufen — Tests nur auf Ansage): in `adam.cu` das `fmaf` der letzten Zeile durch `p[i] + groesse * (mi / nenner)` ersetzen → Fall 1 rot; in `Schrittgraph.laufen`
`alles_im_graphen = True` → Fall 4 rot. Geschrieben, nicht gelaufen.
"""
import sys
import unittest

import torch
from django.conf import settings

for _p in (str(settings.TOOLS_ROOT), str(settings.TOOLS_ROOT / 'meshgenesis')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from KoerperKI_alle.adamschritt import Adamschritt  # noqa: E402
from meshgenesis_schrittgraph import Schrittgraph  # noqa: E402

KARTE = 'cuda'


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class AdamschrittTest(unittest.TestCase):
    SCHRITTE = 40

    @staticmethod
    def aufgabe(formen):
        g = torch.Generator(device=KARTE).manual_seed(3)
        x = [(torch.randn(f, device=KARTE, generator=g) * 0.3).requires_grad_(True) for f in formen]
        z = [torch.randn(f, device=KARTE, generator=g) for f in formen]
        return x, lambda: sum((torch.sin(3 * a) - b).pow(2).sum() for a, b in zip(x, z, strict=True))

    def einfach(self, formen, gruppen, **mehr):
        x, verlust = self.aufgabe(formen)
        opt = torch.optim.Adam(gruppen(x), **mehr)
        for _ in range(self.SCHRITTE):
            opt.zero_grad(set_to_none=True)
            verlust().backward()
            opt.step()
        return [a.detach() for a in x]

    def eigen(self, formen, gruppen, **mehr):
        x, verlust = self.aufgabe(formen)
        opt, adam = torch.optim.Adam(gruppen(x), **mehr), None
        for i in range(self.SCHRITTE):
            opt.zero_grad(set_to_none=True)
            verlust().backward()
            if i == 0:
                opt.step()
                self.assertTrue(Adamschritt.geht(opt))
                adam = Adamschritt(opt, self.SCHRITTE - 1)
            else:
                adam.schritt()
        adam.abschliessen(self.SCHRITTE - 1)
        self.assertEqual({int(z['step']) for z in opt.state.values()}, {self.SCHRITTE})
        return [a.detach() for a in x]

    def test_1_bitgleich(self):
        for formen, gruppen, mehr in (([(3, 41)], lambda x: x, {'lr': 0.02}),
                                      ([(200, 3), (17,), (1,)], lambda x: x, {'lr': 0.003, 'betas': (0.5, 0.9)}),
                                      ([(240,), (5, 6), (3,)], lambda x: [{'params': x[:1], 'lr': 0.05}, {'params': x[1:], 'lr': 1e-3, 'eps': 1e-15}], {})):
            with self.subTest(formen=formen):
                self.assertTrue(all(torch.equal(a, b) for a, b in zip(self.einfach(formen, gruppen, **mehr), self.eigen(formen, gruppen, **mehr), strict=True)))

    def test_2_geht_nicht(self):
        x = torch.zeros(3, device=KARTE, requires_grad=True)
        for mehr in ({'amsgrad': True}, {'weight_decay': 0.1}, {'capturable': True}, {'maximize': True}):
            self.assertFalse(Adamschritt.geht(torch.optim.Adam([x], lr=0.1, **mehr)), mehr)
        self.assertFalse(Adamschritt.geht(torch.optim.AdamW([x], lr=0.1)))
        self.assertFalse(Adamschritt.geht(torch.optim.Adam([torch.zeros(3, dtype=torch.float64, device=KARTE, requires_grad=True)], lr=0.1)))
        self.assertTrue(Adamschritt.geht(torch.optim.Adam([x], lr=0.1)))

    def schleife(self, graph):
        x, verlust = self.aufgabe([(30, 3)])
        opt = torch.optim.Adam(x, lr=0.05)

        @torch.no_grad()
        def klemmen():
            x[0].clamp_(-0.4, 0.4)
        Schrittgraph.laufen(verlust, opt, self.SCHRITTE, klemmen, graph=graph, danach_graph=True)
        opt.zero_grad(set_to_none=True)
        verlust().backward()
        opt.step()
        return x[0].detach()

    def test_3_schleife_mit_klemmen(self):
        mit, ohne = self.schleife(True), self.schleife(False)
        self.assertTrue(torch.equal(mit, ohne))

    def test_4_lernrate_je_schritt(self):
        ergebnis = []
        for graph in (True, False):
            x, verlust = self.aufgabe([(30, 3)])
            opt = torch.optim.Adam(x, lr=0.05)
            plan = torch.optim.lr_scheduler.LambdaLR(opt, lambda i: 0.9 ** i)
            Schrittgraph.laufen(verlust, opt, self.SCHRITTE, plan.step, graph=graph)
            ergebnis.append(x[0].detach())
        self.assertTrue(torch.equal(*ergebnis))
