# -*- coding: utf-8 -*-
"""Tests für die Bausteine von EconTorch vom 03.11.2026 (Ausschnitt, pytorch3d-Teile, Registrierung) und die Normalen-Wahl der Kette — klein, auf der CPU, ohne Gewichte und
ohne Fotos. Die Gegenproben gegen die Originale (kornia, pytorch3d, ECONs `register`, FBNet) stehen in `ProjektTemp/_wegwerf/ergaenzung/econ_gegenprobe2.py`."""
import sys
import unittest

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from EconTorch.ausschnitt import Ecausschnitt  # noqa: E402
from EconTorch.p3d import Ecp3d  # noqa: E402
from EconTorch.register import Ecregister  # noqa: E402
from KoerperKI_Fotos.normalenecon import Normalenecon  # noqa: E402
from KoerperKI_Fotos.normalenpshuman import Normalenpshuman  # noqa: E402


def gitter(n=6):
    """Ebenes Gitter n × n in z = 0, zwei Dreiecke je Zelle."""
    y, x = torch.meshgrid(torch.arange(n, dtype=torch.float32), torch.arange(n, dtype=torch.float32), indexing='ij')
    v = torch.stack([x.flatten(), y.flatten(), torch.zeros(n * n)], 1)
    f = []
    for i in range(n - 1):
        for j in range(n - 1):
            a = i * n + j
            f += [[a, a + 1, a + n], [a + 1, a + n + 1, a + n]]
    return v, torch.tensor(f)


class DerAusschnitt(unittest.TestCase):
    def test_kasten_landet_mittig_mit_neun_zehnteln(self):
        m = Ecausschnitt.matrix_box(torch.tensor([[100.0, 50.0, 300.0, 450.0]]), 512, 512)[0]
        oben_links, unten_rechts = m[:2, :2] @ torch.tensor([100.0, 50.0]) + m[:2, 2], m[:2, :2] @ torch.tensor([300.0, 450.0]) + m[:2, 2]
        self.assertAlmostEqual(float((unten_rechts - oben_links)[1]), 512 * 0.9, places=3)
        self.assertAlmostEqual(float((oben_links + unten_rechts)[0] / 2), 256.0, places=3)

    def test_einheit_verzerrt_nicht(self):
        bild = torch.rand((1, 2, 7, 9))
        self.assertTrue(torch.allclose(Ecausschnitt.warp_affine(bild, torch.eye(3)[None], (7, 9)), bild, atol=1e-6))


class DiePytorch3dTeile(unittest.TestCase):
    def test_kanten_eindeutig_und_unterteilung_vierfach(self):
        v, f = gitter()
        e, f2e = Ecp3d.kanten(f, len(v))
        self.assertEqual(len(e), len({tuple(k) for k in e.tolist()}))
        self.assertTrue(bool((e[:, 0] < e[:, 1]).all()))
        self.assertEqual(f2e.shape, f.shape)
        sv, sf = Ecp3d.unterteilen(v, f)
        self.assertEqual(len(sv), len(v) + len(e))
        self.assertEqual(len(sf), 4 * len(f))
        self.assertTrue(torch.equal(sv[:len(v)], v))

    def test_chamfer_null_bei_gleichen_punkten_und_quadriert(self):
        v, _f = gitter()
        self.assertEqual(float(Ecp3d.chamfer(v, v)), 0.0)
        self.assertAlmostEqual(float(Ecp3d.chamfer(v, v + torch.tensor([0.0, 0.0, 0.1]))), 2 * 0.01, places=6)

    def test_laplace_null_innen_auf_der_ebene(self):
        v, f = gitter(3)
        e = Ecp3d.kanten(f, len(v))[0]
        self.assertGreater(float(Ecp3d.laplace(v, e)), 0.0)                  # Ränder ziehen nach innen
        self.assertEqual(float(Ecp3d.laplace(v * 0, e)), 0.0)


class DieRegistrierung(unittest.TestCase):
    def test_folgt_einer_verschiebung(self):
        v, f = gitter()
        v = v / 5.0
        neu, verlauf = Ecregister.registrieren(v + torch.tensor([0.0, 0.0, 0.05]), v, f)
        self.assertLess(verlauf[-1], verlauf[0])
        self.assertLess(float((neu[:, 2] - 0.05).abs().mean()), 0.02)


class DieNormalenWahl(unittest.TestCase):
    def test_gegenpaare_nach_winkel(self):
        w = {'1.jpg': 0, '4.jpg': 90, '2.jpg': 180, '3.jpg': 270}
        self.assertEqual(Normalenecon.paare_aus(w, 'mehrere', None), [('1.jpg', '2.jpg'), ('4.jpg', '3.jpg')])
        self.assertEqual(Normalenecon.paare_aus(w, 'ein_foto', '3.jpg'), [('3.jpg', None)])
        self.assertEqual(Normalenecon.paare_aus(w, 'ein_foto', None), [('1.jpg', None)])
        self.assertEqual(Normalenecon.paare_aus({'a': 0, 'b': 45}, 'mehrere', None), [('a', None), ('b', None)])

    def test_pshuman_gewichte_je_winkel(self):
        self.assertEqual([Normalenpshuman.ansicht_gewicht(w) for w in (0, 90, 180, 270, 45, 330)], [1.0, 0.8, 1.0, 0.8, 0.4, 0.4])
