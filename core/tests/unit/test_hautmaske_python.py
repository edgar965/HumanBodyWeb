# -*- coding: utf-8 -*-
u"""`ModelPhysik/hautmaske.py` — die Server-Fassung der Hautmaske am
Kunstkörper: anliegende Kante bis zum Rand, lockere mit zwei Ringen frei,
Inselschließung, Index und Einzug.

Der Punkt-für-Punkt-Vergleich mit der Browser-Fassung (Node) liegt wegen
seiner Dauer in `core/tests/longrunner/test_hautmaske_gegen_browser.py`.

Sabotage-Gegenprobe: `groesse_frei < groesste` entfernt (`maskeninseln`)
macht die Insel rot; `t >= -tiefe` → `t >= 0` macht den Browser-Vergleich rot.
"""
import numpy as np
from django.test import SimpleTestCase
from ._modelphysik import Modelphysik

from ._kunstkoerper import zylinder


def _hautmaske_modul():
    return Modelphysik.modul('hautmaske')


class HautmaskePythonTest(SimpleTestCase):

    databases = set()

    def setUp(self):
        self.hm = _hautmaske_modul()
        self.koerper = zylinder(0.10, 0.0, 1.0, 51, 36)

    def _maske(self, stoff, **optionen):
        P, T = self.koerper
        return self.hm.Hautmaske.verdeckt(P, T, [stoff], **optionen)

    def test_die_anliegende_kante_wird_bis_zum_rand_verdeckt(self):
        P, _T = self.koerper
        m = self._maske(zylinder(0.102, 0.30, 0.70, 41, 36))
        y = P[:, 1]
        self.assertTrue(m[(y > 0.305) & (y < 0.695)].all())
        self.assertFalse(m[(y < 0.295) | (y > 0.705)].any())
        # locker: zwei Ringe (2 cm) frei
        m = self._maske(zylinder(0.110, 0.30, 0.70, 41, 36))
        self.assertTrue(m[(y > 0.325) & (y < 0.675)].all())
        self.assertFalse(m[(y < 0.315) | (y > 0.685)].any())

    def test_insel_und_index(self):
        P, T = self.koerper
        stoff_p, stoff_t = zylinder(0.102, 0.30, 0.70, 41, 36)
        mitte = 20 * 36 + 7
        loch = stoff_t[~(stoff_t == mitte).any(axis=1)]
        roh = self.hm.Hautmaske.verdeckt(P, T, [(stoff_p, loch)], inseln=0)
        zu = self.hm.Hautmaske.verdeckt(P, T, [(stoff_p, loch)])
        y = P[:, 1]
        band = (y > 0.35) & (y < 0.65)
        frei = int((~roh[band]).sum())
        self.assertGreater(frei, 0)
        self.assertEqual(int((~roh[band] & zu[band]).sum()), frei)
        dreiecke, entfernt = self.hm.Hautmaske.index_ohne(T, zu)
        self.assertGreater(entfernt, 0)
        self.assertEqual(len(dreiecke) + entfernt, len(T))
        # Einzug: nur verdeckte Punkte wandern, und zwar nach innen
        innen = self.hm.Hautmaske.einzug(P, T, zu)
        r = np.linalg.norm(innen[:, [0, 2]], axis=1)
        self.assertTrue(np.allclose(r[~zu], 0.10, atol=1e-6))
        self.assertTrue(np.allclose(r[zu], 0.10 - 0.010, atol=1e-6))
