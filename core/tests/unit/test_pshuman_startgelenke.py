"""Startgelenke: MHR-70 von SAM 3D Body → Namen und Achsen des Starts von PSHumans Rekonstruktion, mit Kunstpunkten, ohne Karte."""
import sys
import unittest
from pathlib import Path

import numpy as np
from django.conf import settings

sys.path.insert(0, str(Path(settings.TOOLS_ROOT) / 'mesh3dai'))
sys.path.insert(0, str(Path(settings.TOOLS_ROOT) / 'pshuman_port14'))
from mesh3dai_mia_zuordnung import Miazuordnung  # noqa: E402
from startgelenke import Startgelenke  # noqa: E402


class StartgelenkeTest(unittest.TestCase):
    def setUp(self):
        self.punkte = sorted({p for je in Startgelenke.zuordnung().values() for p in je})

    def _sam(self, **orte):
        k3 = np.zeros((len(self.punkte), 3))
        for name, ort in orte.items():
            k3[self.punkte.index(name.replace('_', '-'))] = ort
        return k3

    def test_achsen_sam_zu_pshuman(self):
        s = Startgelenke.aus_sam(self.punkte, self._sam(neck=(0.1, -1.4, -0.2)))
        self.assertEqual(s.gelenke[s.namen.index('Neck')].tolist(), [0.1, 1.4, 0.2])

    def test_mitte_aus_zwei_punkten(self):
        s = Startgelenke.aus_sam(self.punkte, self._sam(left_ear=(0.2, 0, 0), right_ear=(-0.1, 0, 0)))
        self.assertAlmostEqual(float(s.gelenke[s.namen.index('Head')][0]), 0.05)

    def test_huefte_liegt_ueber_den_hueftgelenken(self):
        s = Startgelenke.aus_sam(self.punkte, self._sam(left_hip=(0.1, -1, 0), right_hip=(-0.1, -1, 0), neck=(0, -2, 0)))
        self.assertAlmostEqual(float(s.gelenke[s.namen.index('Hips')][1]), 1 + Startgelenke.HUEFTE_HOCH)

    def test_jedes_gelenk_hat_seine_punkte(self):
        s = Startgelenke.aus_sam(self.punkte, np.ones((len(self.punkte), 3)))
        self.assertEqual(s.gelenke.shape, (len(Startgelenke.zuordnung()), 3))

    def test_namen_sind_mia_namen(self):
        """`Mesh3daimeshstart` ordnet über `Miazuordnung` zu; ein Tippfehler im Namen ließe das Gelenk still ohne Ziel."""
        namen = ['hip', 'l_forearm', 'l_hand', 'neck1', 'head']
        zu = Miazuordnung(list(Startgelenke.zuordnung()), namen, [-1, 0, 1, 0, 3])
        self.assertTrue(zu.direkt.all(), zu.bericht())

    def test_steht_fuer_den_datensatz(self):
        s = Startgelenke.aus_sam(self.punkte, np.zeros((len(self.punkte), 3)))
        self.assertIs(s[0], s)
        self.assertEqual(s.faces.shape, (0, 3))
