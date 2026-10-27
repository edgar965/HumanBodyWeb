# -*- coding: utf-8 -*-
"""Mesh3D-AI, Rechenlauf: Rückfall auf den Formkopf, wenn MIAs A-Pose durchfällt (27.10.2026, Edgar: „In der Kette automatisch auf den Formkopf zurückfallen, sobald MIA durchfällt“).
An Kunstordnern, ohne Karte und ohne Schritt:

    1  `mia_apose`: jüngste Kette mit `weg = 'mia'` → wahr; ohne `weg` (Rig) oder `weg = 'rig'` → falsch; keine Kette → falsch; es zählt die JÜNGSTE Kette
    2  Regler-KI gewählt: der Schritt „form“ ist `FORM_REGLERKI`; der Rückfall nimmt den Befehl des Formkopfs aus `SCHRITTE`
Sabotage (von Hand): in `mia_apose` `ketten[-1]` durch `ketten[0]` ersetzen → Fall 1 rot.
"""
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from django.conf import settings

from core.dienste.mesh3dairechenlauf import Mesh3dairechenlauf


class RechenlaufRueckfallTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=str(Path(settings.TOOLS_ROOT) / 'ProjektTemp'))
        self.test = Path(self._tmp.name) / 'kunsttest'
        self.lauf = Mesh3dairechenlauf('kunsttest')
        self.lauf.test = self.test

    def tearDown(self):
        self._tmp.cleanup()

    def _kette(self, nr, weg):
        d = self.test / 'vorstufe' / ('%04d' % nr)
        d.mkdir(parents=True)
        felder = {'punkte': np.zeros((3, 3), dtype=np.float32)}
        if weg is not None:
            felder['weg'] = np.array(weg)
        np.savez(d / 'apose.npz', **felder)

    def test_mia_apose_jungste_kette(self):
        self.assertFalse(self.lauf.mia_apose())
        self._kette(1, 'mia')
        self.assertTrue(self.lauf.mia_apose())
        self._kette(2, None)
        self.assertFalse(self.lauf.mia_apose())
        self._kette(3, 'rig')
        self.assertFalse(self.lauf.mia_apose())
        self._kette(4, 'mia')
        self.assertTrue(self.lauf.mia_apose())

    def test_rueckfall_nimmt_den_formkopf(self):
        self.test.mkdir(parents=True)
        (self.test / 'einstellung.json').write_text(json.dumps({'form_ki': {'art': 'reglerki', 'lauf': 'x'}}), encoding='utf-8')
        form = dict((s, a) for s, _t, a in self.lauf.schritte())['form']
        self.assertIs(form, Mesh3dairechenlauf.FORM_REGLERKI[2])
        formkopf = next(s[2] for s in Mesh3dairechenlauf.SCHRITTE if s[0] == 'form')
        self.assertIn('{formkopf}', formkopf)
        self.assertNotIn('{reglerki_lauf}', formkopf)


if __name__ == '__main__':
    unittest.main()
