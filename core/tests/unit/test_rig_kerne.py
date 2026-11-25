# -*- coding: utf-8 -*-
u"""Die Kerne des Schritts „rig“ und der Flächenabstand (25.11.2026, Edgar: „verbessere weiter, vor allem rig“) — dieselben Zahlen wie die Fassungen davor.

1. `Ikkern`: Gradient gegen Differenzen; die Anpassung senkt den Verlust und lässt den Eingang stehen.
2. `Lochohren`: ein Würfel ohne Deckel ist danach geschlossen (jede Kante zweimal), Fläche des Deckels; `groesste` hält größere Löcher offen.
3. `Miaeigenring.waehlen` (Kern) = `Miaeigenring.einzeln` (dünne Matrizen).
4. `Flaechenabstand` = die Formeln von `Kleidergpu.naechste_stelle` über alle Dreiecke (K groß), auch an entarteten Dreiecken; kein Nachbardreieck → Abstand unendlich, Dreieck −1.
5. `Perspektivbild`: ein Viereck quer zur Kamera trifft die erwarteten Bildpunkte in der erwarteten Tiefe; von hinten bleibt das Bild leer.

Sabotage (nicht gelaufen): in `flaechenabstand.cu` `d2 < bester` → `d2 <= bester` → Fall 4 (erstes Minimum) rot; in `ohren.cu` ein Dreieck weglassen → Fall 2 rot; in `ring.cu` `RINGE` um 1
kleiner rufen → Fall 3 rot. Geschrieben, nicht gelaufen.
"""
import math
import sys
import unittest
from types import SimpleNamespace

import torch
import trimesh
from django.conf import settings

for _p in (str(settings.TOOLS_ROOT), str(settings.TOOLS_ROOT / 'meshgenesis')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from KoerperKI_alle.ikkern import Ikkern  # noqa: E402
from KoerperKI_alle.lochohren import Lochohren  # noqa: E402
from KoerperKI_alle.perspektivbild import Perspektivbild  # noqa: E402

KARTE = 'cuda'


def _felder(netz):
    return torch.as_tensor(netz.vertices.copy(), dtype=torch.float64, device=KARTE), torch.as_tensor(netz.faces.copy(), dtype=torch.int64, device=KARTE)


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class IkkernTest(unittest.TestCase):

    def setUp(self):
        eltern = [-1, 0, 1, 1, 2]
        n = len(eltern)
        z = lambda *form: torch.randn(form, device=KARTE, generator=torch.Generator(device=KARTE).manual_seed(len(form) + sum(form)))
        eins = torch.eye(3, device=KARTE).expand(n, 3, 3).contiguous()
        self.n = n
        self.kin = SimpleNamespace(n=n, eltern=eltern, frei=torch.arange(3, 3 * n, device=KARTE), reihe=torch.tensor([[0, 1, 2]] * n, device=KARTE), c=0.3 * z(n, 3), e=0.3 * z(n, 3) + 0.2, o=eins,
                                   lo=torch.full((n, 3), -1.5, device=KARTE), hi=torch.full((n, 3), 1.5, device=KARTE), fest_wert=torch.zeros(n, 3, device=KARTE))
        self.kern = Ikkern(self.kin)
        self.ziele = 0.5 * z(1, 2 * n, 3)
        self.roh = 0.3 * z(1, 3 * n - 3 + 9)

    def test_1_gradient_und_anpassung(self):
        _v, g = self.kern.gradient(self.roh, self.ziele)
        for i in (0, 4, 9, len(g[0]) - 9, len(g[0]) - 1):
            h = 1e-2
            plus, minus = self.roh.clone(), self.roh.clone()
            plus[0, i] += h
            minus[0, i] -= h
            diff = float(self.kern.gradient(plus, self.ziele)[0] - self.kern.gradient(minus, self.ziele)[0]) / (2 * h)
            self.assertAlmostEqual(float(g[0, i]), diff, delta=0.02 * max(0.05, abs(diff)))
        vorher = self.roh.clone()
        nachher = self.kern.rechnen(self.roh, self.ziele, stufen=[(60, 0.03, True), (200, 0.02, False)])
        self.assertTrue(torch.equal(self.roh, vorher))
        self.assertLess(float(self.kern.gradient(nachher, self.ziele)[0]), 0.7 * float(self.kern.gradient(self.roh, self.ziele)[0]))


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class LochohrenTest(unittest.TestCase):

    def test_2_wuerfel_ohne_deckel(self):
        x, f = _felder(trimesh.creation.box())
        oben = (x[f][:, :, 2] > 0.49).all(1)
        netz = Lochohren(x, f[~oben])
        neu, loch = netz.schliessen(400)
        self.assertEqual((len(neu), int(loch.max())), (2, 0))
        alle = torch.cat([f[~oben], neu])
        kanten = torch.stack([alle, alle[:, [1, 2, 0]]], 2).reshape(-1, 2)
        gerichtet = kanten[:, 0] * len(x) + kanten[:, 1]
        self.assertEqual(len(torch.unique(gerichtet)), len(gerichtet))          # jede gerichtete Kante einmal: geschlossen und gleich umlaufend
        self.assertTrue(torch.equal(torch.unique(gerichtet), torch.unique(kanten[:, 1] * len(x) + kanten[:, 0])))
        a, b, c = (x[neu[:, i]] for i in range(3))
        self.assertAlmostEqual(float(torch.linalg.cross(b - a, c - a).norm(dim=1).sum() / 2), 1.0, places=9)

    def test_2b_groesse(self):
        x, f = _felder(trimesh.creation.box())
        self.assertEqual(len(Lochohren(x, f[~(x[f][:, :, 2] > 0.49).all(1)]).schliessen(4)[0]), 0)          # die Schleife hat vier Kanten: nicht „weniger als vier“


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class RingTest(unittest.TestCase):

    def test_3_wie_duenne_matrizen(self):
        from meshgenesis_miaeigen_ring import Miaeigenring

        x, f = _felder(trimesh.creation.icosphere(subdivisions=4))
        bw = torch.rand(len(x), 24, device=KARTE, generator=torch.Generator(device=KARTE).manual_seed(4)) ** 6
        neu = Miaeigenring.waehlen(bw, f, len(x), KARTE)
        alt = Miaeigenring.einzeln(torch.full((len(x),), -1, dtype=torch.int64, device=KARTE), torch.arange(len(x), device=KARTE), bw, f, len(x), KARTE)
        self.assertLessEqual(int((neu != alt).sum()), 1)          # Summen in float32 statt double: höchstens ein Gleichstand


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class FlaechenabstandTest(unittest.TestCase):

    def setUp(self):
        from Genesis9.rechenkarte import G9rechenkarte
        self.stand = G9rechenkarte.stand()
        G9rechenkarte.einschalten()
        self.karte = G9rechenkarte.an()
        self.addCleanup(lambda: G9rechenkarte.zuruecksetzen(self.stand))

    def _alle(self, p, d, q):
        """Über alle Dreiecke mit `Kleidergpu.naechste_stelle` — (Abstand, Fußpunkt)."""
        from meshgenesis_kleidergpu import Kleidergpu
        a, b, c = (p[d[:, i]] for i in range(3))
        u = Kleidergpu.an().naechste_stelle(q[:, None], a, b, c)
        fuss = u[..., :1] * a + u[..., 1:2] * b + u[..., 2:] * c
        d2 = ((q[:, None] - fuss) ** 2).sum(-1)
        wahl = d2.argmin(1)
        return d2.gather(1, wahl[:, None])[:, 0].sqrt(), fuss[torch.arange(len(q), device=KARTE), wahl]

    def test_4_naechster_punkt(self):
        from KoerperKI_Fotos.flaechenabstand import Flaechenabstand
        z = torch.Generator(device=KARTE).manual_seed(8)
        p, d = _felder(trimesh.creation.icosphere(subdivisions=1))
        q = torch.randn(300, 3, device=KARTE, dtype=torch.float64, generator=z)
        abstand, fuss, dreieck, bary, vorzeichen = Flaechenabstand(self.karte, p, d).abfragen(q, k=len(p))
        soll, ort = self._alle(p, d, q)
        self.assertTrue(torch.equal(abstand, soll))
        self.assertLess(float((fuss - ort).abs().max()), 1e-15)
        self.assertLess(float(((bary[..., None] * p[d[dreieck]]).sum(1) - fuss).abs().max()), 1e-15)
        self.assertTrue(bool(((q.norm(dim=1) > 1.0) <= (vorzeichen > 0)).all()))
        entartet = torch.tensor([[0, 0, 1], [2, 3, 3], [4, 4, 4], [5, 6, 7]], device=KARTE)
        self.assertTrue(torch.equal(Flaechenabstand(self.karte, p, entartet).abfragen(q, k=8)[0], self._alle(p, entartet, q)[0]))

    def test_4b_gleichstand_und_wenige_punkte(self):
        from KoerperKI_Fotos.flaechenabstand import Flaechenabstand
        p = torch.tensor([[0.0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]], device=KARTE, dtype=torch.float64)
        d = torch.tensor([[0, 1, 2], [2, 1, 0]], device=KARTE)          # dasselbe Dreieck zweimal, gegenläufig: das erste gewinnt
        f = Flaechenabstand(self.karte, p, d)
        dreieck = f.abfragen(torch.tensor([[0.2, 0.2, 0.5]], device=KARTE, dtype=torch.float64))[2]
        self.assertEqual(dreieck.tolist(), [0])


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class PerspektivbildTest(unittest.TestCase):

    def test_5_viereck(self):
        p = torch.tensor([[-0.5, -0.5, 0], [0.5, -0.5, 0], [0.5, 0.5, 0], [-0.5, 0.5, 0]], device=KARTE, dtype=torch.float64)
        n = torch.tensor([[0.0, 0.0, 1.0]] * 4, device=KARTE)
        f = torch.tensor([[0, 1, 2], [0, 2, 3]], device=KARTE)
        bild = Perspektivbild(p, n, f, punktfarben=torch.full((4, 3), 200, dtype=torch.uint8, device=KARTE))
        lage = torch.eye(4, dtype=torch.float64, device=KARTE)
        lage[2, 3] = 2.0
        yfov = 2 * math.atan(0.5)          # bei 2 m ist das Bild 2 m hoch: das Viereck füllt die mittlere Hälfte
        rgb, tiefe = bild.rendern(lage, yfov, 64, 64, (0.0, 0.0, 0.0), (0.5, 0.5, 0.5), 2.0)
        self.assertTrue(bool((tiefe[18:46, 18:46] > 0).all()) and bool((tiefe[:14] == 0).all()) and bool((tiefe[:, :14] == 0).all()))
        self.assertLess(float((tiefe[18:46, 18:46] - 2.0).abs().max()), 1e-3)
        self.assertGreater(int(rgb[32, 32].max()), 0)
        hinten = torch.diag(torch.tensor([-1.0, 1.0, -1.0, 1.0], dtype=torch.float64, device=KARTE))
        hinten[2, 3] = -2.0
        self.assertEqual(float(bild.rendern(hinten, yfov, 64, 64, (0.0, 0.0, 0.0), (0.5, 0.5, 0.5), 2.0)[1].max()), 0.0)


if __name__ == '__main__':
    unittest.main()
