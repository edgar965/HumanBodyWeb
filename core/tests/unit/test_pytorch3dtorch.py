"""Tests für `Pytorch3dTorch`: die Kerne von `pytorch3d._C` in reinem torch, auf der CPU an kleinen Zahlen.

Der Vergleich mit dem Original in python10 steht in `ProjektTemp/_wegwerf/pytorch3d_port/gegenprobe.py`; hier das, was ohne Original gilt: Haufensuche gegen alle Paare, jeder Rückweg gegen die Ableitung der Vorwärtsrechnung, Handrechnungen.
"""
import unittest
from unittest import mock

import pytorch3d
import torch
from pytorch3d import _C
from pytorch3d._C.abstand import Abstandkern
from pytorch3d._C.knn import Knnkern
from pytorch3d._C.knnhaufen import Knnhaufen
from pytorch3d.ops import knn_points


def netz():
    """Kleines gewelltes Gitter, 40 Punkte, ein entartetes Dreieck am Ende."""
    g = torch.Generator().manual_seed(4)
    y, x = torch.meshgrid(torch.arange(5.0), torch.arange(8.0), indexing='ij')
    v = torch.stack([x.flatten() / 8.0, y.flatten() / 8.0, 1.5 + 0.05 * torch.rand(40, generator=g)], 1)
    f = []
    for i in range(4):
        for j in range(7):
            a = i * 8 + j
            f += [[a, a + 1, a + 8], [a + 1, a + 9, a + 8]]
    return v, torch.tensor(f + [[0, 0, 1]])


class Pakettest(unittest.TestCase):
    def test_kommt_aus_dem_projekt(self):
        self.assertIn('Pytorch3dTorch', pytorch3d.__file__)
        self.assertIn('Pytorch3dTorch', _C.__file__)

    def test_fehlender_kern_nennt_sich(self):
        with self.assertRaisesRegex(AttributeError, 'marching_cubes'):
            _C.marching_cubes  # noqa: B018
        self.assertFalse(hasattr(_C, 'ball_query'))


class Knntest(unittest.TestCase):
    def _punkte(self, n, m, d=3):
        g = torch.Generator().manual_seed(7)
        return torch.randn(n, d, generator=g), torch.randn(m, d, generator=g)

    def _gleich(self, a, b, k, norm):
        d, i = Knnhaufen.suche(a, b, k, norm)
        with mock.patch.object(Knnkern, 'DIREKT', 1 << 40):
            i0, d0 = Knnkern.vorwaerts(a[None], b[None], torch.tensor([len(a)]), torch.tensor([len(b)]), norm, k)
        d0, i0 = d0[0].sort(1).values, i0[0]
        self.assertTrue(torch.equal(d, d0), 'Abstände weichen ab')
        self.assertEqual(i.shape, i0.shape)

    def test_haufen_wie_alle_paare(self):
        for k, norm in ((1, 2), (1, 1), (4, 2), (70, 2)):        # 70 > GROESSE: die Keimsuche nimmt zwei Haufen
            with self.subTest(k=k, norm=norm):
                self._gleich(*self._punkte(500, 900), k, norm)

    def test_haufen_mit_mehr_achsen_und_weniger_zielen_als_haufen(self):
        self._gleich(*self._punkte(300, 400, 6), 3, 2)
        self._gleich(*self._punkte(300, 20), 5, 2)

    def test_gleiche_punkte_abstand_null(self):
        a = self._punkte(300, 1)[0]
        d, i = Knnhaufen.suche(a, a, 1, 2)
        self.assertEqual(float(d.max()), 0.0)
        self.assertTrue(torch.equal(a[i[:, 0]], a))

    def test_gross_geht_ueber_die_haufen_und_luecken_bleiben_null(self):
        a, b = self._punkte(200, 300)
        a, b = torch.stack([a, a]), torch.stack([b, b])
        laengen1, laengen2 = torch.tensor([200, 150]), torch.tensor([300, 2])
        with mock.patch.object(Knnkern, 'DIREKT', 0), mock.patch.object(Knnhaufen, 'suche', wraps=Knnhaufen.suche) as suche:
            r = knn_points(a, b, lengths1=laengen1, lengths2=laengen2, K=3)
        self.assertEqual(suche.call_count, 2)
        self.assertEqual(float(r.dists[1, 150:].abs().max()), 0.0)
        self.assertEqual(float(r.dists[1, :, 2].abs().max()), 0.0)

    def test_nicht_endlich_faellt_auf_alle_paare(self):
        a, b = self._punkte(200, 300)
        b[5, 0] = float('nan')
        with mock.patch.object(Knnkern, 'DIREKT', 0), mock.patch.object(Knnhaufen, 'suche') as suche:
            knn_points(a[None], b[None], K=1)
        suche.assert_not_called()

    def test_rueckweg_gegen_autograd(self):
        for norm in (1, 2):
            a, b = self._punkte(60, 90)
            a, b = a[None], b[None]
            gewicht = torch.randn(60, 3, generator=torch.Generator().manual_seed(2))[None]
            x, y = a.clone().requires_grad_(), b.clone().requires_grad_()
            r = knn_points(x, y, K=3, norm=norm)
            (r.dists * gewicht).sum().backward()
            p, q = x.detach().clone().requires_grad_(), y.detach().clone().requires_grad_()
            diff = p[:, :, None] - q[0][r.idx[0]][None]
            d = diff.abs().sum(-1) if norm == 1 else (diff * diff).sum(-1)
            (d * gewicht).sum().backward()
            self.assertLess(float((x.grad - p.grad).abs().max()), 1e-4)
            self.assertLess(float((y.grad - q.grad).abs().max()), 1e-4)


class Flaechentest(unittest.TestCase):
    def test_rueckweg_gegen_autograd(self):
        v, f = netz()
        f = f[:-1]
        ga = torch.randn(len(f), generator=torch.Generator().manual_seed(1))
        gn = torch.randn(len(f), 3, generator=torch.Generator().manual_seed(2))
        p = v.double().requires_grad_()
        a, n = _C.face_areas_normals_forward(p, f)
        auto = torch.autograd.grad((a * ga.double()).sum() + (n * gn.double()).sum(), p)[0]
        hand = _C.face_areas_normals_backward(ga.double(), gn.double(), v.double(), f)
        self.assertLess(float((auto - hand).abs().max()), 1e-9)

    def test_entartet_endlich(self):
        v, f = netz()
        a, n = _C.face_areas_normals_forward(v, f)
        self.assertEqual(float(a[-1]), 0.0)
        self.assertTrue(bool(torch.isfinite(n).all()))
        self.assertTrue(bool(torch.isfinite(_C.face_areas_normals_backward(torch.ones(len(f)), torch.ones(len(f), 3), v, f)).all()))


class Graphtest(unittest.TestCase):
    def test_paare_wie_im_quelltext(self):
        # Beispiele aus `mesh_normal_consistency_cpu.cpp`
        for ein, aus in (([1, 0, 1, 1, 0], []), ([3], [[0, 1], [0, 2], [1, 2]]), ([0, 3], [[0, 1], [0, 2], [1, 2]]), ([1, 3], [[1, 2], [1, 3], [2, 3]]), ([1, 0, 2, 1, 0, 2], [[1, 2], [4, 5]])):
            gefunden = _C.mesh_normal_consistency_find_verts(torch.tensor(ein))
            self.assertEqual(sorted(gefunden.tolist()), sorted(aus), ein)

    def test_gather_scatter(self):
        x = torch.tensor([[1.0], [2.0], [4.0]])
        kanten = torch.tensor([[0, 1], [1, 2]])
        self.assertEqual(_C.gather_scatter(x, kanten, True, False).flatten().tolist(), [2.0, 4.0, 0.0])
        self.assertEqual(_C.gather_scatter(x, kanten, True, True).flatten().tolist(), [0.0, 1.0, 2.0])
        self.assertEqual(_C.gather_scatter(x, kanten, False, False).flatten().tolist(), [2.0, 5.0, 2.0])


class Mischtest(unittest.TestCase):
    def test_sigmoid_rueckweg(self):
        d = torch.randn(1, 3, 4, 2, generator=torch.Generator().manual_seed(1)) * 0.01
        p = torch.randint(-1, 5, (1, 3, 4, 2), generator=torch.Generator().manual_seed(2))
        x = d.clone().requires_grad_()
        a = _C.sigmoid_alpha_blend(x, p, 0.01)
        g = torch.randn(1, 3, 4, generator=torch.Generator().manual_seed(3))
        auto = torch.autograd.grad((a * g).sum(), x)[0]
        self.assertLess(float((auto - _C.sigmoid_alpha_blend_backward(g, a.detach(), d, p, 0.01)).abs().max()), 1e-3)

    def test_kompositoren_rueckweg(self):
        z = torch.Generator().manual_seed(5)
        f = torch.rand(3, 9, generator=z)
        a = torch.rand(2, 4, 3, 5, generator=z)
        idx = torch.randint(-1, 9, (2, 4, 3, 5), generator=z)
        g = torch.randn(2, 3, 3, 5, generator=z)
        for vor, zurueck in ((_C.accum_alphacomposite, _C.accum_alphacomposite_backward), (_C.accum_weightedsum, _C.accum_weightedsum_backward), (_C.accum_weightedsumnorm, _C.accum_weightedsumnorm_backward)):
            x, y = f.clone().requires_grad_(), a.clone().requires_grad_()
            auto_f, auto_a = torch.autograd.grad((vor(x, y, idx) * g).sum(), (x, y))
            hand_f, hand_a = zurueck(g, f, a, idx)
            self.assertLess(float((auto_f - hand_f).abs().max()), 1e-4, vor)
            self.assertLess(float((auto_a - hand_a).abs().max()), 1e-3, vor)


class Interpolationstest(unittest.TestCase):
    def test_vor_und_zurueck(self):
        p = torch.tensor([0, -1, 1])
        b = torch.tensor([[1.0, 0, 0], [0.2, 0.3, 0.5], [0.5, 0.5, 0]])
        f = torch.arange(18.0).view(2, 3, 3)
        x = _C.interp_face_attrs_forward(p, b, f)
        self.assertEqual(x[0].tolist(), [0.0, 1.0, 2.0])
        self.assertEqual(x[1].tolist(), [0.0, 0.0, 0.0])
        g = torch.tensor([[1.0, 0, 0], [5.0, 5, 5], [0, 1.0, 0]])
        gb, gf = _C.interp_face_attrs_backward(p, b, f, g)
        self.assertEqual(gb[1].tolist(), [0.0, 0.0, 0.0])
        self.assertEqual(gf[0, 0].tolist(), [1.0, 0.0, 0.0])


class Rastertest(unittest.TestCase):
    def _raster(self, v, f, groesse, blur=0.0, k=1, perspektive=False, klemmen=False, rueck=False):
        erste, zahl = torch.tensor([0]), torch.tensor([len(f)])
        return _C.rasterize_meshes(v[f], erste, zahl, torch.full((len(f),), -1), groesse, blur, k, 0, 0, perspektive, klemmen, rueck)

    def test_quadrat_fuellt_das_bild_und_spiegelt(self):
        v = torch.tensor([[-2.0, -2, 1], [2, -2, 1], [2, 2, 1], [-2, 2, 1]])
        f = torch.tensor([[0, 1, 2], [0, 2, 3]])
        p, z, _b, d = self._raster(v, f, (4, 6))
        self.assertEqual(p.shape, (1, 4, 6, 1))
        self.assertTrue(bool((p >= 0).all()))
        self.assertAlmostEqual(float(z.max()), 1.0, 5)
        self.assertLess(float(d.max()), 0.0)

    def test_nahes_dreieck_gewinnt_und_k_zwei_zeigt_beide(self):
        v = torch.tensor([[-2.0, -2, 1], [2, -2, 1], [0, 2, 1], [-2.0, -2, 2], [2, -2, 2], [0, 2, 2]])
        f = torch.tensor([[3, 4, 5], [0, 1, 2]])
        p, z, _b, _d = self._raster(v, f, (8, 8), k=2)
        self.assertEqual(p[0, 4, 4].tolist(), [1, 0])
        self.assertEqual(z[0, 4, 4].tolist(), [1.0, 2.0])

    def test_rueckweg_ohne_nan_auch_bei_winzigen_dreiecken(self):
        v, f = netz()
        p, z, b, d = self._raster(v, f, 32, blur=1e-3, k=3, perspektive=True, klemmen=True)
        aus = _C.rasterize_meshes_backward(v[f], p, torch.ones_like(z), torch.ones_like(b), torch.ones_like(d), True, True)
        self.assertEqual(aus.shape, (len(f), 3, 3))
        self.assertTrue(bool(torch.isfinite(aus).all()))

    def test_punkte_rueckweg_gegen_handrechnung(self):
        punkte = torch.tensor([[0.0, 0.0, 1.0], [0.05, 0.0, 2.0], [0.0, 0.0, -1.0]])
        r = torch.full((3,), 0.2)
        i, z, d = _C.rasterize_points(punkte, torch.tensor([0]), torch.tensor([3]), (8, 8), r, 2, 0, 0)
        self.assertEqual(i.dtype, torch.int32)
        self.assertFalse(bool((i == 2).any()), 'Punkt hinter der Kamera')
        self.assertLess(float(z[i == 1].sub(2.0).abs().max()), 1e-6)
        g = _C.rasterize_points_backward(punkte, i, torch.ones_like(z), torch.zeros_like(d))
        self.assertEqual(float(g[0, 2]), float((i == 0).sum()))


class Abstandtest(unittest.TestCase):
    def test_ueber_und_neben_dem_dreieck(self):
        t = torch.tensor([[[0.0, 0, 0], [1, 0, 0], [0, 1, 0]]])
        p = torch.tensor([[0.2, 0.2, 3.0], [-1.0, 0.0, 0.0], [2.0, 0.0, 0.0]])
        n = torch.tensor([0])
        d, i = _C.point_face_dist_forward(p, n, t, n, 3, 1e-5)
        self.assertLess(float((d - torch.tensor([9.0, 1.0, 1.0])).abs().max()), 1e-5)
        self.assertEqual(i.tolist(), [0, 0, 0])

    def test_stapel_bleiben_getrennt(self):
        t = torch.tensor([[[0.0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0.0, 0, 5], [1, 0, 5], [0, 1, 5]]])
        p = torch.tensor([[0.2, 0.2, 0.0], [0.2, 0.2, 0.0]])
        d, i = _C.point_face_dist_forward(p, torch.tensor([0, 1]), t, torch.tensor([0, 1]), 1, 1e-5)
        self.assertEqual(i.tolist(), [0, 1])
        self.assertLess(float((d - torch.tensor([0.0, 25.0])).abs().max()), 1e-4)

    def test_entartet_endlich_auch_im_rueckweg(self):
        t = torch.tensor([[[0.0, 0, 0], [0, 0, 0], [0, 0, 0]], [[0.0, 0, 0], [1, 0, 0], [1, 0, 0]]])
        p = torch.tensor([[0.5, 2.0, 0.0], [0.5, 0.0, 0.0]])
        i = torch.tensor([0, 1])
        d = Abstandkern.dreieck(p, t[i, 0], t[i, 1], t[i, 2], 1e-5)
        self.assertTrue(bool(torch.isfinite(d).all()))
        g = _C.point_face_dist_backward(p, t, i, torch.ones(2), 1e-5)
        self.assertTrue(all(bool(torch.isfinite(x).all()) for x in g))

    def test_kante(self):
        s = torch.tensor([[[0.0, 0, 0], [1, 0, 0]]])
        p = torch.tensor([[0.5, 2.0, 0.0], [3.0, 0.0, 0.0]])
        n = torch.tensor([0])
        d, _i = _C.point_edge_dist_forward(p, n, s, n, 2)
        self.assertEqual(d.tolist(), [4.0, 4.0])
