"""`Exportleistekollision._ziel`: das Morph-Ziel der GLB muss auch strenge Leser passieren (04.11.2026, Edgar: GLB öffnet nicht, F3D 3.5 verlangt `sparse.indices.byteOffset`).
Sabotage (von Hand): im Eintrag `indices` oder `values` den `byteOffset` entfernen → rot."""
import unittest
from types import SimpleNamespace

import numpy as np

from core.dienste.exportleistekollision import Exportleistekollision


class ZielTest(unittest.TestCase):
    databases = []

    @staticmethod
    def _kollision():
        k = Exportleistekollision.__new__(Exportleistekollision)
        k.j = {'accessors': [], 'bufferViews': []}
        k.m = SimpleNamespace(bin=bytearray())
        return k

    def test_byteoffset_steht_ausdruecklich_da(self):
        k = self._kollision()
        versatz = np.zeros((5, 3), dtype=np.float32)
        versatz[2] = [0.01, 0.0, 0.0]
        a = k.j['accessors'][k._ziel(versatz)]
        self.assertEqual(a['sparse']['indices']['byteOffset'], 0)
        self.assertEqual(a['sparse']['values']['byteOffset'], 0)

    def test_ohne_geschobenen_punkt_bleibt_ein_eintrag(self):
        k = self._kollision()
        a = k.j['accessors'][k._ziel(np.zeros((5, 3), dtype=np.float32))]
        self.assertEqual(a['sparse']['count'], 1)
        self.assertEqual(a['sparse']['values']['byteOffset'], 0)
