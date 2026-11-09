"""`Mesh3daifotogelenke.verdeckt`: Ein Gelenk hinter einem anderen Körperteil ist im Foto nicht zu sehen. Ohne Karte."""
import sys
import unittest

sys.path.insert(0, r'A:\3DTools\mesh3dai')

from mesh3dai_fotogelenke import Mesh3daifotogelenke as F  # noqa: E402


class VerdecktTest(unittest.TestCase):
    databases = []

    def test_ein_stueck_verdeckt_nichts(self):
        self.assertFalse(F.verdeckt([0.3, -0.2], 0.1))
        self.assertFalse(F.verdeckt([0.3], 0.1))
        self.assertFalse(F.verdeckt([], 0.1))

    def test_gelenk_im_ersten_stueck(self):
        self.assertFalse(F.verdeckt([0.4, 0.2, -0.1, -0.5], 0.3))

    def test_gelenk_hinter_dem_kopf(self):
        self.assertTrue(F.verdeckt([0.4, 0.2, -0.1, -0.5], -0.3))

    def test_gelenk_in_der_luecke_zaehlt_zum_naeheren_stueck(self):
        self.assertFalse(F.verdeckt([0.4, 0.2, -0.3, -0.5], 0.1))
        self.assertTrue(F.verdeckt([0.4, 0.2, -0.3, -0.5], -0.2))

    def test_vor_dem_netz_ist_nichts_verdeckt(self):
        self.assertFalse(F.verdeckt([0.4, 0.2, -0.1, -0.5], 0.9))
