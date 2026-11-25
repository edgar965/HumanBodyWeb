# -*- coding: utf-8 -*-
u"""Die Anpassung von „Mesh to 3D“ als Kerne (25.11.2026, Edgar: „verbessere weiter, vor allem rig“) — Werte und Gradienten wie die torch-Fassung mit autograd, an Kunstdaten.

1. `Meshfigurhaltungskern` (`nk_anp_*`): Punkte, Gelenke und Drehungen, Gradient nach Winkeln, Lage, Verschiebung, Maßstab, Ruhelage und Gelenken; auch bei fast verschwindender Drehung.
2. `Meshfigurflaechenkern` (`nk_anp_flaeche`): Figur → Netz, Netz → Figur, Stoff → Figur; mit und ohne Gewichtung; mit verdeckten Proben (einseitig).
3. Beide in einer Graph-Aufnahme: die Wiedergabe liest die neuen Parameter.
4. `Meshfigurnachbarn`: der nächste Punkt wie die Suche über alle Paare, je Richtung; gemerkt wird je Tensorobjekt.

Gegenprobe an echten Daten: `ProjektTemp/_wegwerf/tempo_kette/anpassungskern_probe.py` (Gradient relativ 2e-7 bis 1e-6). Sabotage (nicht gelaufen): in `k_anp_kette_zurueck` `zu.a[3 * x + y] += …`
weglassen → Fall 1 rot; in `k_anp_hin` `sammeln(streu + 6 * i + 3 + z, …)` weglassen → Fall 2 rot; in `Meshfigurnachbarn.naechster` `scatter_` durch `index[:, 0]` ersetzen → Fall 4 rot.
Geschrieben, nicht gelaufen.
"""
import sys
import unittest
from types import SimpleNamespace

import torch
from django.conf import settings

for _p in (str(settings.TOOLS_ROOT), str(settings.TOOLS_ROOT / 'meshto3d')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

KARTE = 'cuda'


def _zufall(saat):
    g = torch.Generator(device=KARTE).manual_seed(saat)
    return lambda *form: torch.randn(form, device=KARTE, generator=g)


def _relativ(a, b):
    return float((a - b).norm() / b.norm().clamp_min(1e-12))


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class HaltungskernTest(unittest.TestCase):

    def setUp(self):
        from meshfigur_kinematik import Meshfigurkinematik

        z = _zufall(1)
        eltern = [-1, 0, 1, 1, 3, 4, 0]
        j, n = len(eltern), 90
        knochen = torch.randint(0, j, (n, 4), device=KARTE, generator=torch.Generator(device=KARTE).manual_seed(2))
        gewicht = z(n, 4).abs().double()
        gewicht[::5, 3] = 0.0
        self.p, self.c = z(n, 3), z(j, 3)
        daten = {'eltern': eltern, 'kopf': self.c, 'orientierung': 40.0 * z(j, 3).double(), 'reihenfolge': ['XYZ', 'YZX', 'ZXY', 'XZY', 'YXZ', 'ZYX', 'XYZ'],
                 'frei': [1, 3, 4, 5], 'haut_index': knochen, 'haut_gewicht': gewicht}
        self.kin = Meshfigurkinematik(daten, torch.device(KARTE))
        self.f, self.fg, self.fd = z(n, 3), z(j, 3), z(j, 3, 3)

    def _torch(self, theta, rg, tg, log_s, p, c):
        kin = self.kin
        dreh, lage = kin.kette(theta, c)
        a, b = kin.mischung(dreh, lage, c)
        x = (a @ p[..., None])[..., 0] + b
        m = kin.drehmatrix(rg) * torch.exp(log_s)
        return x @ m.T + tg, lage @ m.T + tg, m @ dreh

    def test_1_wert_und_gradient(self):
        z = _zufall(3)
        self.assertIsNotNone(self.kin.kern)
        for winkel, lage in ((0.0, 0.8), (35.0, 0.0001), (70.0, 2.0)):
            ein = [winkel * z(4, 3), lage * z(3), z(3), torch.tensor(0.05, device=KARTE), self.p.clone(), self.c.clone()]
            erg = []
            for rechnen in (self._torch, self.kin.kern.posieren):
                x = [e.detach().clone().requires_grad_() for e in ein]
                v, g, d = rechnen(*x)
                ((v * self.f).sum() + (g * self.fg).sum() + (d * self.fd).sum()).backward()
                erg.append([v.detach(), g.detach(), d.detach()] + [e.grad for e in x])
            for name, a, b in zip(('x', 'gelenke', 'dreh', 'theta', 'rg', 'tg', 'log_s', 'p', 'c'), erg[1], erg[0], strict=True):
                self.assertLess(_relativ(a, b), 2e-5, (winkel, lage, name))


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class FlaechenkernTest(unittest.TestCase):

    def _abstand(self, kleidung='ignorieren'):
        import trimesh
        from meshfigur_abstand import Meshfigurabstand

        z = _zufall(5)
        kugel = trimesh.creation.icosphere(subdivisions=3)
        v = torch.as_tensor(kugel.vertices.copy(), dtype=torch.float32, device=KARTE)
        d = torch.as_tensor(kugel.faces.copy(), dtype=torch.int64, device=KARTE)
        self.v = v * (1.0 + 0.02 * z(len(v), 1))
        richtung = torch.nn.functional.normalize(z(4000, 3), dim=1)
        proben = richtung * (1.0 + 0.03 * z(4000, 1))
        n = len(v)
        bereich, teil = torch.zeros(n, dtype=torch.int8, device=KARTE), torch.full((n,), 3, dtype=torch.int64, device=KARTE)
        ab = Meshfigurabstand(proben, richtung, torch.full((4000, 3), 128.0, device=KARTE), d, bereich, teil, torch.device(KARTE), kleidung=kleidung)
        ab.haut = torch.arange(4000, device=KARTE) % 3 != 0
        return ab

    def test_2_wert_und_gradient(self):
        for kleidung in ('ignorieren', 'weich', 'nah'):
            ab = self._abstand(kleidung)
            kern = ab._kern
            if kleidung == 'nah':
                self.assertGreater(ab.reichweite_festlegen(self.v)['nah'], 0)
            for gewichtung in (None, torch.rand(len(self.v), device=KARTE, generator=torch.Generator(device=KARTE).manual_seed(7))):
                erg = []
                for k in (None, kern):
                    ab._kern = k
                    x = self.v.clone().requires_grad_()
                    wert, zahlen = ab.verlust(x, 0.1, 0.02, gewichtung, neu=ab._paare is None)
                    (1.5 * wert).backward()
                    erg.append((wert.detach(), x.grad, {n: float(w) for n, w in zahlen.items()}))
                self.assertLess(_relativ(erg[1][0], erg[0][0]), 2e-6)
                self.assertLess(_relativ(erg[1][1], erg[0][1]), 2e-5)
                self.assertEqual(set(erg[0][2]), set(erg[1][2]))
                for name, w in erg[0][2].items():
                    self.assertAlmostEqual(w, erg[1][2][name], delta=2e-5 * max(1.0, abs(w)))

    def test_3_in_einer_aufnahme(self):
        ab = self._abstand()
        v = self.v.clone().requires_grad_()
        ab.paare_setzen(v)
        neben = torch.cuda.Stream()
        with torch.cuda.stream(neben):
            ab.verlust(v, 0.1, 0.02, None, neu=False)[0].backward()
        neben.synchronize()
        v.grad = None
        graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph):
            wert = ab.verlust(v, 0.1, 0.02, None, neu=False)[0]
            wert.backward()
        with torch.no_grad():
            v.mul_(1.01)
        graph.replay()
        torch.cuda.synchronize()
        frisch = v.detach().clone().requires_grad_()
        soll = ab.verlust(frisch, 0.1, 0.02, None, neu=False)[0]
        soll.backward()
        self.assertTrue(torch.equal(wert.detach(), soll.detach()))
        self.assertTrue(torch.equal(v.grad, frisch.grad))

    def test_2b_normalen(self):
        ab = self._abstand()
        self.assertLess(float((ab._kern.normalen(self.v) - ab.normalen(self.v)).abs().max()), 2e-6)


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class NachbarnTest(unittest.TestCase):

    def test_4_wie_alle_paare(self):
        from meshfigur_nachbarn import Meshfigurnachbarn

        z, nachbarn = _zufall(11), Meshfigurnachbarn()
        a, b = z(3000, 3), z(5000, 3)
        soll_hin = torch.cdist(a.double(), b.double()).argmin(1)
        soll_her = torch.cdist(b.double(), a.double()).argmin(1)
        for _ in range(2):          # beim zweiten Mal aus dem Gemerkten
            self.assertTrue(torch.equal(nachbarn.naechster(a, b), soll_hin))
            self.assertTrue(torch.equal(nachbarn.naechster(b, a, fest='anfragen'), soll_her))
        anders = b + 1.0          # ein anderes Tensorobjekt: neuer Baum
        self.assertTrue(torch.equal(nachbarn.naechster(a, anders), torch.cdist(a.double(), anders.double()).argmin(1)))
        for k in range(nachbarn.HOECHSTENS + 2):
            nachbarn.naechster(a, b + k)
        self.assertLessEqual(len(nachbarn._fest), nachbarn.HOECHSTENS)


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class RueckfallTest(unittest.TestCase):

    def test_5_die_hautmischung_gibt_die_torch_fassung(self):
        """`Meshfigurmodell.vorwaerts(mischung=True)` (Rest-Schritt) rechnet in torch und liefert A; sonst rechnet der Kern und A ist None."""
        from meshfigur_modell import Meshfigurmodell

        gerufen = []
        kern = SimpleNamespace(posieren=lambda *a: gerufen.append('kern') or (1, 2, 3))
        m = SimpleNamespace(ruhe=lambda: (torch.zeros(2, 3, device=KARTE), torch.zeros(1, 3, device=KARTE)), theta=None, rg=torch.zeros(3, device=KARTE), tg=torch.zeros(3, device=KARTE),
                            log_s=torch.zeros((), device=KARTE),
                            kin=SimpleNamespace(kern=kern, kette=lambda t, c: (torch.eye(3, device=KARTE)[None], c), mischung=lambda d, g, c: (torch.eye(3, device=KARTE).expand(2, 3, 3),
                                                torch.zeros(2, 3, device=KARTE))))
        self.assertEqual(Meshfigurmodell.vorwaerts(m), (1, 2, 3, None))
        self.assertIsNotNone(Meshfigurmodell.vorwaerts(m, mischung=True)[3])
        self.assertEqual(gerufen, ['kern'])


if __name__ == '__main__':
    unittest.main()
