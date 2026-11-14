# -*- coding: utf-8 -*-
"""`Numpynachsichtfabrik` (KoerperKI_alle, 13.11.2026): `torch.tensor`/`as_tensor`/`new_tensor` mit Tensoren in der Liste rechnen unter der Nachsicht wie torch ohne sie, sobald jeder
Tensor genau einen Wert hat — PSHuman `torch.tensor([noise_level] * n)` (noise_level Form (1,)) wurde (n, 1), jede Diffusion brach ab. Einträge mit mehreren Werten bleiben nach numpy-Art
gestapelt. Erwartet sind die Formen, die torch ohne Nachsicht liefert (gemessen `ProjektTemp/_wegwerf/torchvision_echt/nachsicht_liste_probe.py`). Braucht die Karte (LongRunner).
"""
import sys
import unittest

import torch
from django.conf import settings


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Karte')
class NumpynachsichtFabrikTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if str(settings.TOOLS_ROOT) not in sys.path:
            sys.path.insert(0, str(settings.TOOLS_ROOT))
        from KoerperKI_alle.numpynachsicht import Numpynachsicht
        Numpynachsicht.einschalten()

    def form(self, t, form, typ):
        self.assertEqual((tuple(t.shape), t.dtype, t.device.type), (form, typ, 'cuda'))

    def test_ein_wert_je_eintrag_wie_torch(self):
        k = torch.tensor([7], device='cuda')
        f = torch.tensor([2.5], device='cuda', dtype=torch.float64)
        self.form(torch.tensor([k] * 3, device='cuda'), (3,), torch.int64)
        self.assertEqual(torch.tensor([k] * 3, device='cuda').tolist(), [7, 7, 7])
        self.form(torch.tensor([k, 3, k[0]], device='cuda'), (3,), torch.int64)
        self.form(torch.tensor([[k, k], [k[0], 1]], device='cuda'), (2, 2), torch.int64)
        self.form(torch.tensor([f, f], device='cuda'), (2,), torch.float64)
        self.form(torch.tensor([k, k], device='cuda', dtype=torch.float32), (2,), torch.float32)
        self.form(torch.tensor([k.reshape(1, 1)] * 2, device='cuda'), (2,), torch.int64)
        self.form(torch.as_tensor([k, k], device='cuda'), (2,), torch.int64)
        self.form(f.new_tensor([k, k]), (2,), torch.float64)

    def test_mehrere_werte_gestapelt(self):
        zwei = torch.tensor([torch.tensor([1, 2], device='cuda')] * 3, device='cuda')
        self.form(zwei, (3, 2), torch.int64)
