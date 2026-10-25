# -*- coding: utf-8 -*-
"""Tests für den ViTPose-Nachbau `A:\\3DTools\\VitposeTorch` (24.10.2026): Dekodierung (DARK-UDP), Spiegeltabelle, Ausschnitt, Rückgrat und Kopf.

WARUM: Die Gelenke der Körperlage aus den Fotos kommen seit 24.10.2026 aus diesem Nachbau (Sapiens2-Teilgrenzen lagen bis 40 cm daneben). Die Gegenprobe gegen das Original (FootMR, python10)
braucht Gewichte und Fotos und steht in `ProjektTemp/_wegwerf/ai2d3d/vitpose_gegenprobe.py`; hier wird ohne Gewichte auf der CPU geprüft, was jede Stelle für sich zusagt — auch der ganze Weg
Foto → Ausschnitt → Wärmebild → Foto mit einem Kunstkopf, der sein Wärmebild dorthin legt, wo der Eingang hell ist.
"""
import sys
import unittest

import numpy as np
import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from VitposeTorch.dekodierung import Vpdekodierung  # noqa: E402
from VitposeTorch.kopf import Vpkopf  # noqa: E402
from VitposeTorch.punkte import Vppunkte  # noqa: E402
from VitposeTorch.rueckgrat import Vprueckgrat  # noqa: E402


class HellerFleckKopf(torch.nn.Module):
    """Kunstkopf: legt in allen 133 Wärmebildern einen Gauß dorthin, wo Kanal 0 des Eingangs (N, 3, 256, 192) am hellsten ist — Abbildung Ausschnitt → Wärmebild wie UDP:
    Wärmebildpunkt = Ausschnittpunkt · (48 − 1) / (192 − 1) bzw. (64 − 1) / (256 − 1)."""

    def forward(self, x):
        n, _c, h, w = x.shape
        hell = x[:, 0] - x[:, 0].amin((1, 2), keepdim=True)
        hell = hell ** 4
        yy, xx = torch.meshgrid(torch.arange(h, dtype=x.dtype), torch.arange(w, dtype=x.dtype), indexing='ij')
        cx = (hell * xx).sum((1, 2)) / hell.sum((1, 2)) * 47 / 191
        cy = (hell * yy).sum((1, 2)) / hell.sum((1, 2)) * 63 / 255
        wy, wx = torch.meshgrid(torch.arange(64, dtype=x.dtype), torch.arange(48, dtype=x.dtype), indexing='ij')
        g = torch.exp(-((wx[None] - cx[:, None, None]) ** 2 + (wy[None] - cy[:, None, None]) ** 2) / 8.0)
        return g[:, None].expand(n, 133, 64, 48)


class DieDekodierung(unittest.TestCase):
    @staticmethod
    def waerme(x0, y0, h=64, w=48, sigma=2.0):
        yy, xx = torch.meshgrid(torch.arange(h).float(), torch.arange(w).float(), indexing='ij')
        return torch.exp(-((xx - x0) ** 2 + (yy - y0) ** 2) / (2 * sigma ** 2))[None, None]

    def test_spitze_zwischen_den_bildpunkten(self):
        gr = torch.tensor([[47.0, 63.0]])            # Ausschnitt = (W − 1, H − 1): Bildpunkt = Wärmebildpunkt
        for x0, y0 in ((20.3, 30.7), (10.8, 50.2), (33.6, 12.4)):
            xy, wert = Vpdekodierung.punkte(self.waerme(x0, y0), gr * 0.5, gr)
            self.assertLess(float((xy[0, 0] - torch.tensor([x0, y0])).norm()), 0.05, (x0, y0, xy[0, 0].tolist()))
            self.assertGreater(float(wert[0, 0]), 0.9)

    def test_ausschnitt_zurueck_ins_bild(self):
        """UDP: Bild = Wärmebildpunkt · Ausschnitt / (W − 1) + Mitte − Ausschnitt / 2."""
        xy, _ = Vpdekodierung.punkte(self.waerme(20.3, 30.7), torch.tensor([[100.0, 200.0]]), torch.tensor([[94.0, 126.0]]))
        self.assertLess(float((xy[0, 0] - torch.tensor([20.3 * 2 + 100 - 47, 30.7 * 2 + 200 - 63])).norm()), 0.1)

    def test_leeres_waermebild_ohne_zuversicht(self):
        xy, wert = Vpdekodierung.punkte(torch.zeros((1, 2, 64, 48)), torch.zeros((1, 2)), torch.tensor([[47.0, 63.0]]))
        self.assertEqual(wert.tolist(), [[0.0, 0.0]])
        self.assertTrue(bool(torch.isfinite(xy).all()))


class DieSpiegeltabelle(unittest.TestCase):
    def setUp(self):
        self.p = Vppunkte.SPIEGEL()

    def test_zweimal_gespiegelt_ist_nichts_getauscht(self):
        self.assertEqual(len(self.p), 133)
        self.assertEqual([self.p[i] for i in self.p], list(range(133)))

    def test_links_wird_rechts(self):
        for i, n in Vppunkte.NAMEN.items():
            if n.endswith('_l'):
                self.assertEqual(Vppunkte.NAMEN[self.p[i]], n[:-2] + '_r', n)

    def test_haende_paarweise_und_mitte_bleibt(self):
        self.assertEqual([self.p[91 + a] for a in range(21)], [112 + a for a in range(21)])
        for i in (0, 23 + 8, 23 + 27, 23 + 28, 23 + 29, 23 + 30, 23 + 33, 23 + 51, 23 + 57, 23 + 62, 23 + 66):   # Nase, Kinn, Nasenrücken, Nasenspitze, Lippenmitten
            self.assertEqual(self.p[i], i, i)


class DerAusschnitt(unittest.TestCase):
    def test_kasten_hoch_wird_drei_zu_vier_und_groesser(self):
        mitte, seite = Vppunkte.kasten_quadrat((10, 20, 110, 420))
        self.assertEqual(mitte.tolist(), [60.0, 220.0])
        self.assertAlmostEqual(seite, 480.0, places=4)

    def test_kasten_breit_wird_hoeher(self):
        mitte, seite = Vppunkte.kasten_quadrat((0, 0, 300, 100))
        self.assertEqual(mitte.tolist(), [150.0, 50.0])
        self.assertAlmostEqual(seite, 480.0, places=4)

    @staticmethod
    def ohne_gewichte():
        """`Vppunkte` ohne das Laden der Gewichte (2,5 GB) — dieselben Felder, die `__init__` setzt, mit dem Kunstkopf."""
        v = object.__new__(Vppunkte)
        v.g = torch.device('cpu')
        v.modell = torch.nn.Module()
        v.modell.backbone = torch.nn.Identity()
        v.modell.keypoint_head = HellerFleckKopf()
        v.spiegel = torch.as_tensor(Vppunkte.SPIEGEL())
        v.mittel = torch.tensor(Vppunkte.MITTEL).view(1, 3, 1, 1)
        v.streuung = torch.tensor(Vppunkte.STREUUNG).view(1, 3, 1, 1)
        return v

    @staticmethod
    def fleck(x0, y0, h=400, w=300):
        yy, xx = np.mgrid[0:h, 0:w]
        f = np.exp(-((xx - x0) ** 2 + (yy - y0) ** 2) / (2 * 3.0 ** 2))
        return np.repeat((f * 255).astype(np.uint8)[..., None], 3, 2)

    def test_eingang_in_form_und_kastenmitte_in_der_mitte(self):
        v = self.ohne_gewichte()
        x, mitte, seite = v.eingang(self.fleck(150, 200), (100, 50, 200, 350))
        self.assertEqual(tuple(x.shape), (1, 3, 256, 192))
        self.assertEqual(mitte.tolist(), [150.0, 200.0])
        self.assertAlmostEqual(seite, 360.0, places=4)
        hell = (x[0, 0] - x[0, 0].min()) ** 4
        yy, xx = torch.meshgrid(torch.arange(256.0), torch.arange(192.0), indexing='ij')
        self.assertAlmostEqual(float((hell * xx).sum() / hell.sum()), 95.5, delta=0.3)       # Bildmitte 127,5 − 32 abgeschnittene Spalten
        self.assertAlmostEqual(float((hell * yy).sum() / hell.sum()), 127.5, delta=0.3)

    def test_foto_ausschnitt_waermebild_foto(self):
        """Der ganze Weg mit Spiegelprobe: ein heller Fleck im Foto kommt als Punkt an derselben Stelle zurück (Toleranz 1,5 px: Hin- und Rückweg skalieren mit 255 bzw. 191·4/3)."""
        v = self.ohne_gewichte()
        for x0, y0 in ((170, 150), (120, 260)):
            xy, wert = v.punkte(self.fleck(x0, y0), (100, 50, 200, 350))
            self.assertEqual(tuple(xy.shape), (133, 2))
            self.assertLess(float((xy - torch.tensor([float(x0), float(y0)])).norm(dim=1).max()), 1.5, (x0, y0, xy[0].tolist()))
            self.assertGreater(float(wert.min()), 0.5)


class RueckgratUndKopf(unittest.TestCase):
    #: Namen der Gewichte im Original (`vit.py`, `topdown_heatmap_simple_head.py`) — sonst lädt `load_state_dict(strict=False)` stumm nichts
    NAMEN_RUECKGRAT = ('patch_embed.proj.weight', 'pos_embed', 'blocks.0.norm1.weight', 'blocks.0.attn.qkv.weight', 'blocks.0.attn.qkv.bias', 'blocks.0.attn.proj.weight',
                       'blocks.0.norm2.weight', 'blocks.0.mlp.fc1.weight', 'blocks.0.mlp.fc2.weight', 'last_norm.weight')
    NAMEN_KOPF = ('deconv_layers.0.weight', 'deconv_layers.1.weight', 'deconv_layers.1.running_mean', 'deconv_layers.3.weight', 'deconv_layers.4.running_var',
                  'final_layer.weight', 'final_layer.bias')

    def test_formen_256x192_zu_16x12_zu_64x48(self):
        torch.manual_seed(0)
        r = Vprueckgrat(breite=32, tiefe=2, koepfe=4).eval()
        k = Vpkopf(ein=32, punkte=133, filter_=8).eval()
        with torch.no_grad():
            y = r(torch.randn(2, 3, 256, 192))
            self.assertEqual(tuple(y.shape), (2, 32, 16, 12))
            self.assertEqual(tuple(k(y).shape), (2, 133, 64, 48))
        self.assertEqual(tuple(r.pos_embed.shape), (1, 16 * 12 + 1, 32))

    def test_namen_wie_im_original(self):
        r = Vprueckgrat(breite=32, tiefe=1, koepfe=4).state_dict()
        k = Vpkopf(ein=32, punkte=133, filter_=8).state_dict()
        for n in self.NAMEN_RUECKGRAT:
            self.assertIn(n, r)
        for n in self.NAMEN_KOPF:
            self.assertIn(n, k)
        self.assertNotIn('deconv_layers.0.bias', k)

    def test_aufmerksamkeit_wie_von_hand(self):
        """`scaled_dot_product_attention` rechnet dasselbe wie `softmax(q·kᵀ·d^−0,5)·v` aus `vit.py`."""
        torch.manual_seed(0)
        r = Vprueckgrat(breite=32, tiefe=1, koepfe=4).eval()
        a = r.blocks[0].attn
        x = torch.randn(2, 10, 32)
        with torch.no_grad():
            qkv = a.qkv(x).reshape(2, 10, 3, 4, 8).permute(2, 0, 3, 1, 4)
            att = (qkv[0] @ qkv[1].transpose(-2, -1)) * 8 ** -0.5
            soll = a.proj((att.softmax(-1) @ qkv[2]).transpose(1, 2).reshape(2, 10, 32))
            self.assertTrue(torch.allclose(r._aufmerksamkeit(a, x), soll, atol=1e-5))
