# -*- coding: utf-8 -*-
"""Tests für die Ports und Bausteine der Fotos-Kette von KopfKI (24.10.2026): safetensors-Leser (Sapiens2Torch), CLIP-Tokenizer und roi_align (Sam3Torch), Push-Pull der Bartschicht und
Teilung der Haarschale (KopfKI). Klein, auf der CPU, ohne Gewichte und ohne Fotos — die Gegenproben gegen die Originale stehen in `ProjektTemp/_wegwerf/ai2d3d/*_gegenprobe.py`."""
import json
import struct
import sys
import unittest

import numpy as np
import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))
sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))

from KopfKI.fotobart import Fotobart  # noqa: E402
from KopfKI.fotohaarschale import Fotohaarschale  # noqa: E402
from Sam3Torch.roiausrichtung import S3roiausrichtung  # noqa: E402
from Sam3Torch.tokenizer import S3tokenizer  # noqa: E402
from Sapiens2Torch.safetensoren import S2safetensoren  # noqa: E402


class DerSafetensorsLeser(unittest.TestCase):
    def test_liest_f32_und_bf16_wie_geschrieben(self):
        a = torch.arange(6, dtype=torch.float32).reshape(2, 3)
        b = torch.tensor([1.5, -2.0], dtype=torch.bfloat16)
        roh_a, roh_b = a.numpy().tobytes(), b.view(torch.int16).numpy().tobytes()
        kopf = {'a': {'dtype': 'F32', 'shape': [2, 3], 'data_offsets': [0, len(roh_a)]},
                'b': {'dtype': 'BF16', 'shape': [2], 'data_offsets': [len(roh_a), len(roh_a) + len(roh_b)]}, '__metadata__': {'format': 'pt'}}
        k = json.dumps(kopf).encode()
        ordner = settings.TOOLS_ROOT / 'ProjektTemp' / '_wegwerf' / 'test_kopfki'
        ordner.mkdir(parents=True, exist_ok=True)
        datei = ordner / 'probe.safetensors'
        datei.write_bytes(struct.pack('<Q', len(k)) + k + roh_a + roh_b)
        s = S2safetensoren(datei)
        self.assertEqual(sorted(s.namen()), ['a', 'b'])
        self.assertTrue(torch.equal(s.tensor('a'), a))
        self.assertTrue(torch.equal(s.tensor('b'), b))
        self.assertEqual(s.meta, {'format': 'pt'})


class DerTokenizer(unittest.TestCase):
    def setUp(self):
        self.t = S3tokenizer()

    def test_start_ende_und_fuellung(self):
        z = self.t('beard')[0]
        n = int((z != 0).sum())
        self.assertEqual(int(z[0]), self.t.sot)
        self.assertEqual(int(z[n - 1]), self.t.eot)
        self.assertEqual(len(z), 77)
        self.assertTrue(bool((z[n:] == 0).all()))

    def test_gross_klein_und_leerraum_egal(self):
        self.assertTrue(torch.equal(self.t('Beard'), self.t('  beard ')))

    def test_zu_lang_endet_mit_ende(self):
        z = self.t(' '.join(['hair'] * 100))[0]
        self.assertEqual(int(z[-1]), self.t.eot)


class DasRoiAlign(unittest.TestCase):
    def test_ohne_kaesten_leer_in_der_richtigen_form(self):
        x = torch.rand(1, 4, 9, 9)
        self.assertEqual(tuple(S3roiausrichtung.roi_align(x, [torch.zeros((0, 4))], 7).shape), (0, 4, 7, 7))

    def test_konstantes_bild_bleibt_konstant(self):
        x = torch.full((1, 2, 16, 16), 3.0)
        aus = S3roiausrichtung.roi_align(x, [torch.tensor([[2.0, 2.0, 10.0, 12.0]])], 7)
        self.assertTrue(torch.allclose(aus, torch.full_like(aus, 3.0)))


class DerPushPull(unittest.TestCase):
    def test_gueltige_bleiben_luecke_wird_gefuellt(self):
        bild = torch.zeros((32, 32, 3))
        bild[:, :16] = torch.tensor([1.0, 0.5, 0.25])
        bild[:, 16:] = torch.tensor([1.0, 0.5, 0.25])
        maske = torch.ones((32, 32), dtype=torch.bool)
        maske[10:20, 10:20] = False
        bild[~maske] = 0
        aus = Fotobart.pushpull(bild, maske)
        self.assertTrue(torch.allclose(aus[maske], bild[maske]))
        self.assertTrue(torch.allclose(aus[~maske], torch.tensor([1.0, 0.5, 0.25]).expand(int((~maske).sum()), 3), atol=1e-5))


class DieTeilungDerHaarschale(unittest.TestCase):
    def test_ein_dreieck_wird_vier(self):
        p = torch.tensor([[0.0, 0, 0], [1, 0, 0], [0, 1, 0]])
        d = torch.tensor([[0, 1, 2]])
        p2, d2, b2 = Fotohaarschale.teilen(p, d, torch.arange(3))
        self.assertEqual(len(p2), 6)
        self.assertEqual(len(d2), 4)
        flaeche = 0.5 * torch.cross(p2[d2[:, 1]] - p2[d2[:, 0]], p2[d2[:, 2]] - p2[d2[:, 0]], dim=1)
        self.assertTrue(torch.allclose(flaeche[:, 2], torch.full((4,), 0.125)))      # gleiche Ausrichtung, ein Viertel der Fläche
        self.assertTrue(bool(np.isin(b2.numpy(), [0, 1, 2]).all()))
