"""`Kostuemraster.rendern(eine_probe=True)` (30.10.2026): Kennfarben ungemittelt — gemittelt wurde an edgar jede Kante Hose (Art 3 → 64) über Hintergrund zu 32 = Haar, und „Haut durch
Stück“ zählte Bund, Saum und Uhr als Haar (`Kostuembild`, Fassung 29 der Kostüm-Prüfung). Ein Quadrat in Kennfarbe 64 auf schwarzem Grund, Kante quer durch eine Bildpunktreihe, auf der CPU:
    1  ohne `eine_probe` gibt es an der Kante Mischwerte (weder 0 noch 64) — die Gegenprobe, dass die Kante wirklich Bildpunkte teilt
    2  mit `eine_probe` nur 0 und 64, und Farbe ≠ 0 genau dort, wo die Maske gesetzt ist
Sabotage (von Hand): in `_faerben` `proben` immer `range(len(self.PROBEN))` → Fall 2 rot.
"""
import sys
import unittest

from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


class KostuemrasterEineProbeTest(unittest.TestCase):
    databases = []

    @staticmethod
    def rendern(eine_probe):
        import torch
        from mesh3dai_kostuem_raster import Kostuemraster
        # Quadrat x, y ∈ [−0,53, 0,47] (mag 1, Kante 16 Bildpunkte: Kante bei Bildpunkt 3,76 — mitten in einem Bildpunkt), Blick +Z zur Kamera, gegen den Uhrzeigersinn im Bild
        p = torch.tensor([[-0.53, -0.53, 0.0], [0.47, -0.53, 0.0], [0.47, 0.47, 0.0], [-0.53, 0.47, 0.0]])
        f = torch.tensor([[0, 1, 2], [0, 2, 3]])
        farbe = torch.full((4, 3), 64, dtype=torch.uint8)
        r = Kostuemraster(16, 1.0)
        bild, maske = r.rendern([(p, f, farbe)], (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), eine_probe=eine_probe)
        return bild[..., 0], maske

    def test_gemittelt_mischt_an_der_kante(self):
        bild, _m = self.rendern(False)
        werte = set(bild.unique().tolist())
        self.assertTrue(werte - {0, 64}, werte)

    def test_eine_probe_ohne_mischwerte(self):
        bild, maske = self.rendern(True)
        self.assertEqual(set(bild.unique().tolist()), {0, 64})
        self.assertTrue(bool(((bild > 0) == maske).all()))


if __name__ == '__main__':
    unittest.main()
