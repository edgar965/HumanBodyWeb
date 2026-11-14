# -*- coding: utf-8 -*-
"""`Testaufrecht.uebernehmen`: Die aufgerichtete Fassung wird zum Netz des Tests, `lage.npz` nennt keine Drehung mehr und behält sie als Nachweis (05.11.2026). Geschrieben, nicht gelaufen."""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, r'A:\3DTools\meshgenesis')

from meshgenesis_testaufrecht import Testaufrecht  # noqa: E402
import sys as _npz_sys  # noqa: E402
if r'A:\3DTools' not in _npz_sys.path:
    _npz_sys.path.append(r'A:\3DTools')
from KoerperKI_alle.npztorch import Npztorch  # noqa: E402


class TestaufrechtTest(unittest.TestCase):
    databases = []

    def _kette(self):
        test = Path(tempfile.mkdtemp(dir=r'A:\3DTools\ProjektTemp\_wegwerf'))
        ablage = test / 'vorstufe' / '0001' / 'lage'
        ablage.mkdir(parents=True)
        (ablage / 'eingabe_aufrecht.glb').write_bytes(b'glTF')
        matrix = np.diag([1.0, -1.0, -1.0, 1.0])
        Npztorch.speichern(ablage / 'lage.npz', matrix=matrix, aufgerichtet=np.bool_(True), netz=np.array('liegend.glb'), glb=np.array(str(ablage / 'eingabe_aufrecht.glb')), winkel=np.float64(72.0))
        return test, ablage, matrix

    def test_das_aufgerichtete_netz_liegt_im_test(self):
        test, ablage, _m = self._kette()
        ziel = Testaufrecht.uebernehmen(ablage / 'lage.npz', test)
        self.assertEqual(ziel, test / 'aufrecht.glb')
        self.assertTrue(Npztorch.da(ziel))
        self.assertFalse((ablage / 'eingabe_aufrecht.glb').exists())

    def test_lage_nennt_keine_drehung_mehr(self):
        test, ablage, matrix = self._kette()
        ziel = Testaufrecht.uebernehmen(ablage / 'lage.npz', test)
        with Npztorch.lesen_numpy(ablage / 'lage.npz') as z:
            self.assertFalse(bool(z['aufgerichtet']))
            self.assertEqual(str(z['glb']), str(ziel))
            np.testing.assert_array_equal(z['matrix'], np.eye(4))
            np.testing.assert_array_equal(z['matrix_datei'], matrix)
            self.assertEqual(str(z['netz_datei']), 'liegend.glb')
