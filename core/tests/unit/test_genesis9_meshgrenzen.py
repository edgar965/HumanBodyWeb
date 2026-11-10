"""`G9meshgrenzen`: alle Drehreihenfolgen in einem Durchgang (`_euler`, `_matrix`, `klemmen`) gegen die Rechnung je Reihenfolge (`aus_euler`). Auf der CPU, mit den Knochen der Figur."""
import math
import sys
import unittest
from pathlib import Path

import torch
from django.conf import settings

sys.path.insert(0, str(Path(settings.TOOLS_ROOT)))
sys.path.insert(0, str(Path(settings.TOOLS_ROOT) / 'HumanBody'))
from Genesis9.dson import G9dson  # noqa: E402
from Genesis9.meshgrenzen import G9meshgrenzen  # noqa: E402
from Genesis9.meshkoerper import G9meshkoerper  # noqa: E402
from Genesis9.pfade import G9pfade  # noqa: E402


class MeshgrenzenTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        namen = [k['id'] for k in G9dson.lesen(G9pfade.figur()).knochen()]
        cls.gr = G9meshgrenzen(namen, 'cpu')
        torch.manual_seed(3)
        cls.reihen = sorted({cls.gr.reihe[b] for b in cls.gr.sel.tolist()})

    def test_mehrere_reihenfolgen_im_test(self):
        self.assertGreater(len(self.reihen), 1)

    def test_matrix_wie_aus_euler_je_reihenfolge(self):
        w = torch.rand(len(self.gr.sel), 3) * 2.0 - 1.0
        m = self.gr._matrix(w)
        for r in self.reihen:
            stellen = [i for i, b in enumerate(self.gr.sel.tolist()) if self.gr.reihe[b] == r]
            self.assertTrue(torch.allclose(m[stellen], G9meshgrenzen.aus_euler(w[stellen], r), atol=1e-5))

    def test_euler_ist_die_umkehrung_der_matrix(self):
        w = (torch.rand(len(self.gr.sel), 3) * 2.0 - 1.0) * math.radians(60.0)
        self.assertTrue(torch.allclose(self.gr._euler(self.gr._matrix(w)), w, atol=1e-4))

    def test_zu_euler_ist_die_umkehrung_von_aus_euler(self):
        """`meshgenesis_zeile1haltung._start` ruft `zu_euler`; beim Umbau auf `_euler` fiel die Methode weg, die Kette brach erst im Schritt „zeile1“ ab."""
        w = (torch.rand(8, 3) * 2.0 - 1.0) * math.radians(60.0)
        for r in self.reihen:
            self.assertTrue(torch.allclose(G9meshgrenzen.zu_euler(G9meshgrenzen.aus_euler(w, r), r), w, atol=1e-4), r)

    def test_klemmen_legt_die_winkel_in_die_grenzen(self):
        h = torch.zeros((len(self.gr.reihe), 3))
        h[self.gr.sel] = (torch.rand(len(self.gr.sel), 3) * 2.0 - 1.0) * 2.0
        self.gr.klemmen(h)
        o = self.gr.o_sel
        w = self.gr._euler(o.transpose(1, 2) @ G9meshkoerper.rodrigues(h)[self.gr.sel] @ o)
        self.assertLess(float((self.gr.lo_sel - w).clamp_min(0).amax()), 1e-3)
        self.assertLess(float((w - self.gr.hi_sel).clamp_min(0).amax()), 1e-3)

    def test_haltung_in_den_grenzen_bleibt(self):
        h = torch.zeros((len(self.gr.reihe), 3))
        vorher = h.clone()
        self.assertEqual(int(self.gr.klemmen(h)), 0)
        self.assertTrue(torch.equal(h, vorher))
