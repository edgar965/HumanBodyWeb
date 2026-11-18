"""`Hochziehen.bilinear` rechnet wie `F.interpolate(bilinear, align_corners=False)` (17.11.2026, Edgar:
„mach deine Empfehlung“ — Training der Haut-KI deterministisch, ohne das Sortieren der Rückrechnung im
deterministischen Modus).

1. Faktor 2 und 16, vorwärts bis auf Rundung gleich (gemessen höchstens 4,77e-7 bei Zufallswerten um 1).
2. Rückwärts: derselbe Gradient bis auf Rundung.
3. Kein ganzer Faktor → ValueError.
"""

import sys
import unittest

import torch
from django.conf import settings
from torch.nn import functional as F

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_alle.hochziehen import Hochziehen  # noqa: E402


class Hochziehprobe(unittest.TestCase):
    def setUp(self):
        self.gen = torch.Generator(device='cuda').manual_seed(3)

    def test_1_vorwaerts(self):
        for form, ziel in (((2, 3, 4, 4), (64, 64)), ((1, 8, 5, 7), (10, 14))):
            x = torch.randn(form, generator=self.gen, device='cuda')
            erwartet = F.interpolate(x, size=ziel, mode='bilinear', align_corners=False)
            self.assertLess(float((Hochziehen.bilinear(x, ziel) - erwartet).abs().max()), 2e-6)

    def test_2_rueckwaerts(self):
        x = torch.randn((2, 4, 6, 6), generator=self.gen, device='cuda', requires_grad=True)
        gew = torch.randn((2, 4, 12, 12), generator=self.gen, device='cuda')
        (a,) = torch.autograd.grad((Hochziehen.bilinear(x, (12, 12)) * gew).sum(), x)
        b_aus = F.interpolate(x, size=(12, 12), mode='bilinear', align_corners=False)
        (b,) = torch.autograd.grad((b_aus * gew).sum(), x)
        self.assertLess(float((a - b).abs().max()), 1e-5)

    def test_3_kein_ganzer_faktor(self):
        with self.assertRaises(ValueError):
            Hochziehen.bilinear(torch.zeros((1, 1, 4, 4), device='cuda'), (6, 6))


if __name__ == '__main__':
    unittest.main()
