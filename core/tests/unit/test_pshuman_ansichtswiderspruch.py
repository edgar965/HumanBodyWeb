"""`Ansichtswiderspruch` an einem Kunstkörper: Rumpf und freier Arm als Quader, sechs orthografische
Ansichten wie PSHuman, Umrisse analytisch, klein auf der CPU.

Stimmen alle Ansichten überein, behält jede überall ihre Stimme. Lässt die Rückansicht den Arm weg
(wie die Diagonalen bei n1, 09.11.2026), verliert nur sie dort ihre Stimme.
"""
import math
import sys
import unittest
from pathlib import Path

import torch
from django.conf import settings

sys.path.insert(0, str(Path(settings.TOOLS_ROOT) / 'pshuman_port14'))
from ansichtswiderspruch import Ansichtswiderspruch  # noqa: E402


class Klein(Ansichtswiderspruch):
    """Raster und Pixelmaße auf Masken von 128 statt 1024 Pixeln verkleinert."""
    RASTER, TIEFEN, STUECK = 32, 32, 32
    RAND_PX, TIEF_PX, NAH_PX = 2, 2, 8


class AnsichtswiderspruchTest(unittest.TestCase):
    WINKEL = (0, 45, 90, 180, 270, 315)          # 0_front_face … 5_front_left
    S, PX = 0.6, 128                             # halbe Breite des Bildes in Metern, Pixel je Seite
    RUMPF = ((-0.2, 0.2), (-0.5, 0.5), (-0.1, 0.1))
    ARM = ((0.3, 0.4), (-0.3, 0.3), (-0.05, 0.05))
    RUECKEN = 3

    @classmethod
    def mvp(cls):
        """(C, 4, 4): Drehung um die Hochachse, dann orthografisch; Bild-y nach unten wie `grid_sample`."""
        aus = []
        for w in cls.WINKEL:
            c, s = math.cos(math.radians(w)), math.sin(math.radians(w))
            aus.append([[c / cls.S, 0, s / cls.S, 0], [0, -1 / cls.S, 0, 0],
                        [-s * 0.05, 0, c * 0.05, -0.97], [0, 0, 0, 1]])
        return torch.tensor(aus, dtype=torch.float32)

    @classmethod
    def umriss(cls, winkel, quader):
        """(H, W) Umriss der Quader in der Ansicht `winkel`, analytisch an den Pixelmitten."""
        c, s = math.cos(math.radians(winkel)), math.sin(math.radians(winkel))
        ndc = (torch.arange(cls.PX) + 0.5) / cls.PX * 2 - 1
        y, x = (-ndc * cls.S)[:, None], (ndc * cls.S)[None, :]
        aus = torch.zeros(cls.PX, cls.PX, dtype=torch.bool)
        for (x0, x1), (y0, y1), (z0, z1) in quader:
            quer = [c * a + s * b for a in (x0, x1) for b in (z0, z1)]
            aus |= (y >= y0) & (y <= y1) & (x >= min(quer)) & (x <= max(quer))
        return aus

    @classmethod
    def masken(cls, ohne_arm=()):
        teile = [(cls.RUMPF,) if i in ohne_arm else (cls.RUMPF, cls.ARM) for i in range(len(cls.WINKEL))]
        umrisse = [cls.umriss(w, q) for w, q in zip(cls.WINKEL, teile, strict=True)]
        return torch.stack(umrisse).float()[..., None]

    def test_einig_alle_behalten_ihre_stimme(self):
        vertrauen, bericht = Klein.rechnen(self.mvp(), self.masken())
        self.assertEqual(bericht['foto_ohne_erklaerung'], 0)
        self.assertEqual(float(vertrauen.min()), 1.0)

    def test_rueckansicht_ohne_arm_verliert_dort_die_stimme(self):
        vertrauen, bericht = Klein.rechnen(self.mvp(), self.masken(ohne_arm=(self.RUECKEN,)))
        stumm = bericht['stumm_je_ansicht']
        self.assertGreater(stumm[self.RUECKEN], 0, bericht)
        self.assertEqual([n for i, n in enumerate(stumm) if i != self.RUECKEN], [0] * 5, bericht)
        andere = [i for i in range(len(self.WINKEL)) if i != self.RUECKEN]
        self.assertEqual(float(vertrauen[andere].min()), 1.0)
        arm = self.umriss(self.WINKEL[self.RUECKEN], (self.ARM,))
        leer = vertrauen[self.RUECKEN, ..., 0] < 0.5
        self.assertGreater(float((leer & arm).sum()) / float(arm.sum()), 0.9)
        nah = torch.nn.functional.max_pool2d(arm.float()[None, None], 9, 1, 4)[0, 0] > 0.5
        self.assertEqual(int((leer & ~nah).sum()), 0, 'stumm auch fern des Arms')

    def test_huelle_schneidet_ohne_stimme_nichts_weg(self):
        masken = self.masken(ohne_arm=(self.RUECKEN,))
        vertrauen, _ = Klein.rechnen(self.mvp(), masken)
        h = Ansichtswiderspruch.huelle(masken, vertrauen)
        self.assertTrue(bool((h >= masken).all()))
        arm = self.umriss(self.WINKEL[self.RUECKEN], (self.ARM,))
        self.assertGreater(float(h[self.RUECKEN, ..., 0][arm].mean()), 0.9)


if __name__ == '__main__':
    unittest.main()
