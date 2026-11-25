# -*- coding: utf-8 -*-
"""Bausteine, die am 25.11.2026 numpy, cv2, trimesh und cuSPARSE in der Kette abgelöst haben (Edgar: „fixe: numpy taucht noch an 57 Stellen der Kette auf“): `Punkt2`, `Punktabweichung`,
`Koerpermesspunkte._weg`, `Formeltabelle`, `Torchnetz`, `Duennprodukt`, `Dreiecksfragen.abstand`, `Cvgroesse`, `Pilbild`, `Kleidungsentposen.entzerren`. Läuft nur auf Ansage; beim Schreiben nicht gelaufen.

Sabotage (von Hand): in `Koerpermesspunkte._weg` `k - cls.LUECKE_PX` durch `k` ersetzen → „Randsuche“ rot; in `Dreiecksfragen` `NULL` auf 1e-12 → „kleine Dreiecke“ rot; in `duennprodukt.cu`
`zeiger[z + 1]` durch `zeiger[z + 1] - 1` ersetzen → „Produkt“ rot; in `Formeltabelle.summiert` die Runden weglassen (alles in einem `index_put_` ohne `accumulate`) → „mehrfache Stellen“ rot.
"""
import math
import sys
import unittest

import torch
from django.conf import settings
from PIL import Image

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_alle.cvgroesse import Cvgroesse  # noqa: E402
from KoerperKI_alle.dreiecksfragen import Dreiecksfragen  # noqa: E402
from KoerperKI_alle.duennprodukt import Duennprodukt  # noqa: E402
from KoerperKI_alle.formeltabelle import Formeltabelle  # noqa: E402
from KoerperKI_alle.laplaceloeser import Laplaceloeser  # noqa: E402
from KoerperKI_alle.pilbild import Pilbild  # noqa: E402
from KoerperKI_alle.punkt2 import Punkt2  # noqa: E402
from KoerperKI_alle.torchnetz import Torchnetz  # noqa: E402
from KoerperKI_Fotos.koerpermesspunkte import Koerpermesspunkte  # noqa: E402
from KoerperKI_Fotos.punktabweichung import Punktabweichung  # noqa: E402
from KoerperKI_Fotos.randweg import Randweg  # noqa: E402


def zufall(samen):
    return torch.Generator(device='cuda').manual_seed(samen)


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Karte')
class Punktetest(unittest.TestCase):
    databases = []

    def test_punkt2_rechnet_wie_ein_feld(self):
        p, q = Punkt2(3.0, 4.0), Punkt2(1.0, -2.0)
        self.assertEqual((p + 2 * q - q / 2, -p), ((4.5, 1.0), (-3.0, -4.0)))
        self.assertEqual(Punkt2.laenge(p), 5.0)
        self.assertEqual(Punkt2.punktprodukt(p, q), -5.0)
        self.assertEqual(Punkt2.liste(torch.tensor([[1.0, 2.0]], device='cuda')), [(1.0, 2.0)])

    def test_abweichung_findet_versatz_massstab_und_seitentausch(self):
        xy = [Punkt2(*v) for v in (torch.rand((133, 2), device='cuda', generator=zufall(4), dtype=torch.float64) * 400).tolist()]
        w = [0.9] * 133
        versetzt = [p + Punkt2(2.0, -3.0) for p in xy]
        m = Punktabweichung.messen(xy, w, versetzt, w, 2.0)
        self.assertFalse(m['seiten_getauscht'])
        self.assertEqual(m['gesicht']['versatz_mm'], [4.0, -6.0])
        self.assertAlmostEqual(m['gesicht']['abstand_mm'], round(2 * math.hypot(2, 3), 1))
        mitte = Punkt2(200.0, 200.0)
        gross = [mitte + 1.25 * (p - mitte) for p in xy]
        self.assertAlmostEqual(Punktabweichung.messen(xy, w, gross, w, 1.0)['gesicht']['massstab'], 1.25, places=3)
        self.assertTrue(Punktabweichung.messen(xy, w, *Punktabweichung._getauscht(xy, w), 1.0)['seiten_getauscht'])
        self.assertEqual(Punktabweichung.messen(xy, [0.1] * 133, xy, w, 1.0)['kopf'], {'punkte': 0})

    def test_randsuche_auf_feldern_wie_auf_der_karte(self):
        g = zufall(7)
        maske = torch.nn.functional.avg_pool2d(torch.rand((1, 1, 90, 120), device='cuda', generator=g), 9, 1, 4)[0, 0] > 0.5
        feld = maske.cpu().numpy()
        werte = (torch.rand((60, 4), device='cuda', generator=g, dtype=torch.float64)).tolist()
        for x, y, winkel, weit in werte:
            mitte, n = Punkt2(x * 119, y * 89), Punkt2(math.cos(6.28 * winkel), math.sin(6.28 * winkel))
            kappe = int(5 + 60 * weit)
            a, grund_a = Koerpermesspunkte._weg(feld, mitte, n, kappe)
            b, grund_b = Randweg.karte(maske, mitte, n, kappe, Koerpermesspunkte.LUECKE_PX)
            c, grund_c = Randweg.viele(maske, [(mitte, n, kappe)], Koerpermesspunkte.LUECKE_PX)[0]
            self.assertEqual((grund_a, a), (grund_b, b))
            self.assertEqual((grund_a, a), (grund_c, c))


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Karte')
class Netztest(unittest.TestCase):
    databases = []

    @staticmethod
    def _wuerfel():
        p = torch.tensor([[x, y, z] for x in (0.0, 1.0) for y in (0.0, 1.0) for z in (0.0, 1.0)], dtype=torch.float64, device='cuda')
        f = torch.tensor([[0, 1, 3], [0, 3, 2], [4, 6, 7], [4, 7, 5], [0, 4, 5], [0, 5, 1], [2, 3, 7], [2, 7, 6], [0, 2, 6], [0, 6, 4], [1, 5, 7], [1, 7, 3]], device='cuda')
        return p, f

    def test_wuerfel_normalen_nachbarn_und_strahlen(self):
        n = Torchnetz(*self._wuerfel())
        soll = torch.nn.functional.normalize(n.vertices - 0.5, dim=1)
        torch.testing.assert_close(n.vertex_normals, soll, rtol=0, atol=1e-12)
        self.assertEqual(len(n.face_adjacency_edges), 18)
        grad = torch.rad2deg(n.face_adjacency_angles)
        self.assertEqual((int((grad < 1e-6).sum()), int(((grad - 90).abs() < 1e-6).sum())), (6, 12))
        runter = torch.tensor([0.0, 0.0, -1.0], dtype=torch.float64, device='cuda')
        t = n.erste(torch.tensor([[0.3, 0.4, 2.0], [3.0, 0.4, 2.0]], dtype=torch.float64, device='cuda'), runter)
        self.assertAlmostEqual(float(t[0]), 1.0, places=12)
        self.assertTrue(math.isinf(float(t[1])))

    def test_ohne_lose_und_zusammen(self):
        p, f = self._wuerfel()
        n = Torchnetz(torch.cat([torch.full((2, 3), 9.0, dtype=torch.float64, device='cuda'), p]), f + 2).ohne_lose()
        self.assertTrue(torch.equal(n.vertices, p) and torch.equal(n.faces, f))
        zwei = Torchnetz.zusammen([n, Torchnetz(p + 2, f)])
        self.assertEqual((len(zwei.vertices), len(zwei.faces), int(zwei.faces.max())), (16, 24, 15))

    def test_abstand_gilt_auch_fuer_kleine_dreiecke(self):
        """Bis 25.11.2026 griff die Nullschwelle 1e-12 an Dreiecken unter etwa 1 mm² — der Fußpunkt lag bis 0,12 mm daneben."""
        p, f = self._wuerfel()
        q = torch.randn((400, 3), dtype=torch.float64, device='cuda', generator=zufall(5)) * 0.6 + 0.5
        gross = Dreiecksfragen.abstand(p, f, q)
        for massstab in (1e-2, 1e-3, 1e-4):
            torch.testing.assert_close(Dreiecksfragen.abstand(p * massstab, f, q * massstab) / massstab, gross, rtol=0, atol=1e-9)

    def test_abstand_wie_dicht_abgetastet(self):
        p, f = self._wuerfel()
        q = torch.randn((60, 3), dtype=torch.float64, device='cuda', generator=zufall(6)) * 0.6 + 0.5
        i, j = torch.meshgrid(torch.arange(101, device='cuda'), torch.arange(101, device='cuda'), indexing='ij')
        uv = torch.stack([i, j], -1).reshape(-1, 2).double() / 100
        uv = uv[uv.sum(1) <= 1]
        e = p[f]
        proben = (e[:, None, 0] + uv[None, :, :1] * (e[:, None, 1] - e[:, None, 0]) + uv[None, :, 1:] * (e[:, None, 2] - e[:, None, 0])).reshape(-1, 3)
        dicht = torch.cdist(q, proben).amin(1)
        genau = Dreiecksfragen.abstand(p, f, q)
        self.assertTrue(bool((genau <= dicht + 1e-12).all()))
        self.assertLess(float((dicht - genau).max()), 0.01)


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Karte')
class Duenntest(unittest.TestCase):
    databases = []

    @staticmethod
    def _matrix(n, m, samen):
        g = zufall(samen)
        k = torch.stack([torch.randint(0, n, (8 * n,), device='cuda', generator=g), torch.randint(0, m, (8 * n,), device='cuda', generator=g)])
        w = torch.randn(8 * n, dtype=torch.float64, device='cuda', generator=g)
        return torch.sparse_coo_tensor(k, w, (n, m)).coalesce().to_sparse_csr()

    def test_produkt_wie_dicht_und_bei_jedem_aufruf_gleich(self):
        a = self._matrix(300, 170, 2)
        m, dicht = Duennprodukt.von(a), a.to_dense()
        for c in (1, 3, 8):
            v = torch.randn((170, c), dtype=torch.float64, device='cuda', generator=zufall(c))
            torch.testing.assert_close(m @ v, dicht @ v, rtol=0, atol=1e-12)
            self.assertTrue(all(torch.equal(m @ v, m @ v) for _ in range(20)))
        self.assertEqual(tuple((m @ v[:, 0]).shape), (300,))

    def test_andere_matrizen_bleiben_wie_sie_sind(self):
        a = self._matrix(20, 20, 3)
        self.assertIs(Duennprodukt.von(a.float()).__class__, torch.Tensor)

    def test_laplace_bei_gleichem_eingang_gleich(self):
        """cuSPARSE gab am echten System (35.200 Zeilen, Grad 3…54) in 300 Aufrufen zwei Ergebnisse, nach 400 Runden war jeder Lauf anders."""
        n = 4000
        g = zufall(9)
        k = torch.randint(0, n, (6 * n, 2), device='cuda', generator=g)
        stern = torch.stack([torch.zeros(400, dtype=torch.int64, device='cuda'), torch.arange(1, 401, device='cuda')], 1)          # ein Knoten mit hohem Grad
        k = torch.unique(torch.sort(torch.cat([k[k[:, 0] != k[:, 1]], stern]), dim=1).values, dim=0)
        a, grad = Laplaceloeser.graph(n, k, gewichte=torch.rand(len(k), dtype=torch.float64, device='cuda', generator=g) * 1e3)
        w = torch.randn((n, 3), dtype=torch.float64, device='cuda', generator=g)
        fest, zusatz = torch.zeros(n, dtype=torch.bool, device='cuda'), torch.rand(n, dtype=torch.float64, device='cuda', generator=g)
        x = [Laplaceloeser.loesen(a, grad, w, fest, 200, zusatz=zusatz)[0] for _ in range(6)]
        self.assertTrue(all(torch.equal(x[0], y) for y in x[1:]))

    def test_mehrfache_stellen_werden_in_listenfolge_addiert(self):
        m = Formeltabelle.summiert([(0, 1, 0.1), (2, 0, 1.5), (0, 1, 0.2), (0, 1, -0.05)], (3, 2), torch.device('cuda'))
        soll = torch.zeros((3, 2), dtype=torch.float32, device='cuda')
        for i, j, w in ((0, 1, 0.1), (2, 0, 1.5), (0, 1, 0.2), (0, 1, -0.05)):
            soll[i, j] += w
        self.assertTrue(torch.equal(m, soll))
        self.assertEqual(float(Formeltabelle.summiert([], (2, 2), torch.device('cuda')).abs().sum()), 0.0)


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Karte')
class Bildtest(unittest.TestCase):
    databases = []

    def test_bild_und_tensor_hin_und_zurueck(self):
        for kanaele in (1, 3, 4):
            t = torch.randint(0, 256, (7, 5, kanaele), dtype=torch.uint8, device='cuda', generator=zufall(kanaele))
            t = t[..., 0] if kanaele == 1 else t
            self.assertTrue(torch.equal(Pilbild.feld(Pilbild.aus(t)), t))
        with self.assertRaises(TypeError):
            Pilbild.aus(torch.zeros((2, 2), dtype=torch.float32, device='cuda'))

    def test_grau_wie_pil(self):
        t = torch.randint(0, 256, (40, 30, 3), dtype=torch.uint8, device='cuda', generator=zufall(8))
        self.assertTrue(torch.equal(Pilbild.grau(t), Pilbild.feld(Pilbild.aus(t).convert('L'))))

    def test_verkleinern_mittelt_und_laesst_flaechen_stehen(self):
        flaeche = torch.full((90, 60, 3), 137, dtype=torch.uint8, device='cuda')
        for art in ('area', 'cubic'):
            for breite, hoehe in ((20, 30), (17, 41), (120, 180)):
                self.assertTrue(bool((Cvgroesse.aendern(flaeche, breite, hoehe, art) == 137).all()), (art, breite, hoehe))
        t = torch.randint(0, 256, (12, 9, 3), dtype=torch.uint8, device='cuda', generator=zufall(1))
        kasten = t.view(4, 3, 3, 3, 3).double().mean((1, 3))
        self.assertLessEqual(float((Cvgroesse.aendern(t, 3, 4, 'area').double() - kasten).abs().max()), 0.5 + 1e-6)

    def test_bild_aus_palette(self):
        bild = Image.new('P', (3, 2))
        self.assertEqual(tuple(Pilbild.feld(bild).shape[:2]), (2, 3))


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Karte')
class Entzerrentest(unittest.TestCase):
    databases = []

    def test_entzerren_wie_die_dichte_loesung(self):
        """Das Gleichungssystem (Anker + Federn je Kante) dicht aufgestellt und gelöst — derselbe Weg wie die Docstring-Formel."""
        from Kleidung.kleidungsentposen import Kleidungsentposen
        g = zufall(3)
        nr = torch.arange(15 * 15, device='cuda').view(15, 15)
        f = torch.cat([torch.stack([nr[:-1, :-1], nr[1:, :-1], nr[1:, 1:]], -1).reshape(-1, 3), torch.stack([nr[:-1, :-1], nr[1:, 1:], nr[:-1, 1:]], -1).reshape(-1, 3)])
        p = torch.stack([nr // 15, nr % 15, nr * 0], -1).reshape(-1, 3).double() * 0.02 + torch.randn((225, 3), device='cuda', generator=g, dtype=torch.float64) * 0.002
        ruhe = p + torch.randn((225, 3), device='cuda', generator=g, dtype=torch.float64) * 0.01
        abstand = torch.rand(225, device='cuda', generator=g, dtype=torch.float64) * 0.05
        x = Kleidungsentposen.entzerren(ruhe, p, f, abstand, koppeln=0.0)
        kanten = torch.unique(torch.sort(torch.cat([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]), dim=1).values, dim=0)
        i, j = kanten.unbind(1)
        laenge = (p[i] - p[j]).norm(dim=1)
        bezug = float(laenge.median()) if len(laenge) % 2 else float(torch.sort(laenge).values[len(laenge) // 2 - 1:len(laenge) // 2 + 1].mean())
        w = (bezug / laenge.clamp_min(0.25 * bezug)) ** 2
        guete = torch.exp(-((((ruhe[i] - ruhe[j]).norm(dim=1) / laenge).clamp(0.05, 20.0).log().abs()) / 0.2) ** 2)
        z = torch.ones(225, dtype=torch.float64, device='cuda').scatter_reduce(0, i, guete, 'amin').scatter_reduce(0, j, guete, 'amin')
        z = z.scatter_reduce(0, i, z[j], 'amin').scatter_reduce(0, j, z[i], 'amin')
        lam = 200.0 * torch.exp(-abstand / 0.010) * (0.02 + 0.98 * z) + 1e-3
        m = torch.diag(lam)
        m.index_put_((torch.cat([i, j, i, j]), torch.cat([i, j, j, i])), torch.cat([w, w, -w, -w]), accumulate=True)
        soll = p + torch.linalg.solve(m, lam[:, None] * (ruhe - p))
        torch.testing.assert_close(x, soll, rtol=0, atol=1e-7)


if __name__ == '__main__':
    unittest.main()
