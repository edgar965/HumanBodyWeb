"""`Kostuemhaarkopf._schnipsel`: kleine Haarinseln auf Arm oder Hand zählen, auch wenn sie anderes Haar berühren (n2, 07.11.2026). Ohne Datenbank, ohne Karte."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'mesh3dai'))
from mesh3dai_kostuem_haarkopf import Kostuemhaarkopf  # noqa: E402


class SchnipselTest(unittest.TestCase):
    databases = []

    def pruefer(self):
        h = object.__new__(Kostuemhaarkopf)
        h.k = SimpleNamespace(t=torch, g='cpu', naechste=lambda a, b: torch.cdist(a, b).min(1))
        # Käfigpunkte: Kopf bei x = 0, Arm bei x = 1
        h.kaefig = torch.tensor([[0.0, 0, 0], [1.0, 0, 0]], dtype=torch.float64)
        h.fremd = torch.tensor([False, True])
        return h

    def rechne(self, punkte, flaeche_cm2):
        p = torch.tensor(punkte, dtype=torch.float64)
        return self.pruefer()._schnipsel(p, torch.zeros(len(p), dtype=torch.long), torch.tensor([flaeche_cm2 * 1e-4], dtype=torch.float64))

    def test_kleine_insel_auf_dem_arm_ist_ein_schnipsel(self):
        self.assertTrue(bool(self.rechne([[0.9, 0, 0], [1.0, 0, 0]], 17.4)[0]))

    def test_kleine_insel_am_kopf_bleibt(self):
        self.assertFalse(bool(self.rechne([[0.1, 0, 0], [0.2, 0, 0]], 17.4)[0]))

    def test_lange_straehne_ueber_dem_arm_bleibt(self):
        self.assertFalse(bool(self.rechne([[0.9, 0, 0], [1.0, 0, 0]], 413.0)[0]))

    def test_halb_auf_dem_arm_ist_kein_schnipsel(self):
        self.assertFalse(bool(self.rechne([[0.1, 0, 0], [0.9, 0, 0]], 8.0)[0]))
