# -*- coding: utf-8 -*-
u"""`Netzkerne` — eigene CUDA-Kerne für Rechnungen, die in torch viele kleine Aufrufe waren (25.11.2026, Edgar: „muss alles 20 Mal schneller werden“), gegen die einfache Rechnung.

1. Windungszahl eines Würfels: innen 1, außen 0.
2. Häuten (geteilt durch die Gewichtssumme) und Mischen (nicht geteilt).
3. Punktnormalen aus Vierecken und Dreiecken; die Nahtkopie trägt die Normale ihres Punkts.
4. Morphsumme: Morph für Morph, Abschnitt ab:bis, Nummern hinter dem Feld zählen nicht.
5. Stimmen glätten: je Schritt Summe je Punkt, dann je Fläche, Zeile auf 1.
6. Komponenten: kleinste Nummer, auch ohne Kanten und in langen Ketten; `Kartengraph.komponenten` zählt fortlaufend.
7. Bildinseln und Rand.
8. 16 Bit (`kurz`): auf eine halbe Stufe genau, kein gültiger Kopf bei NaN.
9. Ein Feld mit Gradient wird abgewiesen (die Kerne leiten nicht ab).

Sabotage (nicht gelaufen — Tests nur auf Ansage): in `k_mischen` (`netzkerne_cu/figur.cu`) `d[1]` durch `d[3]` ersetzen → Fall 2 rot; in `vereinen` das `min` umdrehen → Fall 6
rot; in `k_kurz` ohne `+ 0.5` runden → Fall 8 rot. Geschrieben, nicht gelaufen.
"""
import sys
import unittest

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_alle.kartengraph import Kartengraph  # noqa: E402
from KoerperKI_alle.netzkerne import Netzkerne  # noqa: E402

KARTE = 'cuda'


def wuerfel():
    """(Punkte (8, 3), Dreiecke (12, 3)) des Einheitswürfels, Umlauf nach außen."""
    p = torch.tensor([[x, y, z] for x in (0.0, 1.0) for y in (0.0, 1.0) for z in (0.0, 1.0)], dtype=torch.float64, device=KARTE)
    v = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    f = torch.tensor([d for a, b, c, e in v for d in ((a, b, c), (a, c, e))], device=KARTE)
    mitte = p.mean(0)
    n = torch.linalg.cross(p[f[:, 1]] - p[f[:, 0]], p[f[:, 2]] - p[f[:, 0]])
    falsch = ((p[f].mean(1) - mitte) * n).sum(1) < 0
    f[falsch] = f[falsch][:, [0, 2, 1]]
    return p, f


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class NetzkerneTest(unittest.TestCase):

    def setUp(self):
        self.gen = torch.Generator(device=KARTE).manual_seed(4)

    def zufall(self, *form, typ=torch.float64):
        return torch.rand(*form, device=KARTE, dtype=typ, generator=self.gen)

    def test_1_windung(self):
        p, f = wuerfel()
        x = torch.tensor([[0.5, 0.5, 0.5], [0.1, 0.9, 0.2], [2.0, 0.5, 0.5], [0.5, -0.4, 0.5]], device=KARTE)
        w = Netzkerne.windung(x, p[f])
        self.assertLess(float((w - torch.tensor([1.0, 1.0, 0.0, 0.0], device=KARTE)).abs().max()), 1e-5)

    def test_2_haeuten_und_mischen(self):
        x, kn = self.zufall(300, 3), torch.randint(0, 5, (300, 4), device=KARTE, generator=self.gen)
        w, dreh, versch = self.zufall(300, 4), self.zufall(5, 3, 3), self.zufall(5, 3)
        summe = torch.einsum('nk,nkij,nj->ni', w, dreh[kn], x) + torch.einsum('nk,nkj->nj', w, versch[kn])
        self.assertLess(float((Netzkerne.mischen(x, kn, w, dreh, versch) - summe).abs().max()), 1e-12)
        self.assertLess(float((Netzkerne.haeuten(x, kn, w, dreh, versch) - summe / w.sum(1, keepdim=True)).abs().max()), 1e-12)
        ohne = Netzkerne.haeuten(x, kn, torch.zeros_like(w), dreh, versch)
        self.assertTrue(torch.equal(ohne, x), 'ohne Gewicht bleibt der Punkt')

    def test_3_flaechennormalen(self):
        p, f = wuerfel()
        flaechen = torch.cat([f, torch.full((len(f), 1), -1, device=KARTE)], 1).to(torch.int32)
        flaechen = torch.cat([flaechen, torch.tensor([[0, 1, 3, 2]], dtype=torch.int32, device=KARTE)])          # dazu ein Viereck
        ecken = Netzkerne.flaechen_je_punkt(flaechen, 8)
        x = torch.cat([p, p[3:4]])                                                                                # Nahtkopie von Punkt 3
        n = Netzkerne.flaechennormalen(x, flaechen, ecken, torch.tensor([3], dtype=torch.int32, device=KARTE))
        soll = torch.zeros((8, 3), dtype=torch.float64, device=KARTE)
        for a, b, c, d in flaechen.tolist():
            k = torch.linalg.cross(p[c] - p[a], p[d] - p[b]) if d >= 0 else torch.linalg.cross(p[b] - p[a], p[c] - p[a])
            for e in (a, b, c, d):
                if e >= 0:
                    soll[e] += k
        soll = soll / soll.norm(dim=1, keepdim=True)
        self.assertLess(float((n[:8] - soll).abs().max()), 1e-12)
        self.assertTrue(torch.equal(n[8], n[3]))

    def test_4_morphe(self):
        acc, d = torch.zeros((50, 3), dtype=torch.float64, device=KARTE), self.zufall(40, 3, typ=torch.float32)
        nr = torch.randint(0, 60, (40,), device=KARTE, dtype=torch.int32, generator=self.gen)
        Netzkerne.morphe(acc, [(nr, d, 0.7, False, 0, 40), (nr, d, -0.25, False, 10, 30)])
        soll = torch.zeros((60, 3), dtype=torch.float64, device=KARTE).index_add_(0, nr.long(), d.double() * 0.7)
        soll.index_add_(0, nr.long()[10:30], d.double()[10:30] * -0.25)
        self.assertLess(float((acc - soll[:50]).abs().max()), 1e-14)

    def test_5_stimmen(self):
        p, f = wuerfel()
        w = self.zufall(len(f), 4, typ=torch.float32)
        soll = w.clone()
        for _ in range(3):
            je_punkt = torch.zeros((len(p), 4), device=KARTE)
            for e in range(3):
                je_punkt.index_add_(0, f[:, e], soll)
            soll = je_punkt[f].sum(1)
            soll = soll / soll.sum(1, keepdim=True)
        self.assertLess(float((Netzkerne.stimmen(w, f, 3) - soll).abs().max()), 1e-5)

    def test_6_komponenten(self):
        kette = torch.arange(999, device=KARTE)
        a, b = torch.cat([kette, kette + 1001]), torch.cat([kette + 1, kette + 1002])
        ordnung = torch.randperm(len(a), device=KARTE, generator=self.gen)
        lab = Netzkerne.komponenten(2002, b[ordnung], a[ordnung])
        soll = torch.cat([torch.zeros(1000, device=KARTE), torch.tensor([1000.0], device=KARTE), torch.full((1000,), 1001.0, device=KARTE), torch.tensor([2001.0], device=KARTE)]).long()
        self.assertTrue(torch.equal(lab.long(), soll))
        self.assertEqual(Kartengraph.komponenten(2002, a, b).unique().tolist(), [0, 1, 2, 3])
        self.assertEqual(Kartengraph.komponenten(3, a[:0], b[:0]).tolist(), [0, 1, 2])

    def test_7_bildinseln(self):
        m = torch.zeros((6, 8), dtype=torch.bool, device=KARTE)
        m[1:3, 1:3] = True          # innen
        m[4:, 5:] = True            # am Rand
        m[3, 3] = True              # berührt die innere nur über Eck: eigene Insel
        lab, rand = Netzkerne.bildinseln(m)
        self.assertEqual(sorted(lab[m].unique().tolist()), [9, 27, 37])
        self.assertEqual([bool(rand[k]) for k in (9, 27, 37)], [False, False, True])

    def test_8_kurz(self):
        w = self.zufall(20000, typ=torch.float32) * 3 - 1
        q, kopf = Netzkerne.kurz(w, 65534)
        ab, schritt, gueltig = kopf.tolist()
        self.assertEqual(gueltig, 1.0)
        self.assertLess(float((ab + q.to(torch.float64) * schritt - w.double()).abs().max()), schritt * 0.51)
        w[7] = float('nan')
        self.assertEqual(float(Netzkerne.kurz(w, 65534)[1][2]), 0.0)

    def test_9_kein_gradient(self):
        x = self.zufall(4, 3).requires_grad_(True)
        with self.assertRaises(RuntimeError):
            Netzkerne.mischen(x * 1.0, torch.zeros((4, 1), dtype=torch.int64, device=KARTE), self.zufall(4, 1), self.zufall(1, 3, 3), self.zufall(1, 3))
