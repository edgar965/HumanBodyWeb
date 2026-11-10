# -*- coding: utf-8 -*-
"""`Meshgenesismeshhuelle`: Glieder unter Stoff halten an MIA, Haut und gemeinsame Hüllen nicht; `G9meshipnet` ohne Hülle wie bisher (05.11.2026). Geschrieben, nicht gelaufen."""
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np
import torch

sys.path.insert(0, r'A:\3DTools\meshgenesis')
sys.path.insert(0, r'A:\3DTools')

from Genesis9.koerperteile import G9koerperteile  # noqa: E402
from Genesis9.meshziel import G9meshziel  # noqa: E402
from meshgenesis_meshhuelle import Meshgenesismeshhuelle  # noqa: E402


def ziel(zahlen):
    """{Teil: (Punkte Haut, Punkte Stoff)} → Attrappe mit `teil`, `klasse`, `p`, `tri`."""
    teil, klasse = [], []
    for name, (haut, stoff) in zahlen.items():
        teil += [G9koerperteile.NUMMER[name]] * (haut + stoff)
        klasse += [G9meshziel.HAUT] * haut + [G9meshziel.KLEID] * stoff
    return SimpleNamespace(teil=torch.tensor(teil), klasse=torch.tensor(klasse), p=torch.zeros((3, 3)), tri=torch.zeros((1, 3), dtype=torch.long))


class MeshgenesismeshhuelleTest(unittest.TestCase):
    databases = []
    NAMEN = ['l_shin', 'l_foot', 'r_shin', 'r_foot', 'l_forearm', 'l_hand']

    def _rechnen(self, z, schnitte, bericht=None):
        start = SimpleNamespace(namen=self.NAMEN, gelenke=np.arange(18.0).reshape(6, 3), bericht=bericht or {},
                                mia=SimpleNamespace(ANHALT={'shin': (('thigh', 'shin'), ('shin', 'foot')), 'foot': (('shin', 'foot'),)}, anhalt=lambda *_a: schnitte))
        koerper = SimpleNamespace(namen=self.NAMEN, eltern=[-1] * 6, x0=torch.zeros(3))
        zu = SimpleNamespace(direkt=np.ones(6, dtype=bool), ende=np.arange(6))
        with mock.patch('meshgenesis_mia_zuordnung.Miazuordnung', return_value=zu):
            return Meshgenesismeshhuelle(start).rechnen(koerper, z, lambda _t: None)

    def test_stoff_ist_die_mehrheit_der_punkte(self):
        s = Meshgenesismeshhuelle(None).stoff(ziel({'l_oberschenkel': (10, 90), 'l_oberarm': (60, 40)}))
        self.assertTrue(s['l_oberschenkel'])
        self.assertFalse(s['l_oberarm'])
        self.assertNotIn('r_oberschenkel', s)

    def test_hose_haelt_beide_beinenden(self):
        h, bericht = self._rechnen(ziel({'l_oberschenkel': (0, 50), 'l_unterschenkel': (0, 50)}), {('thigh', 'shin'): 0, ('shin', 'foot'): 2})
        self.assertEqual(bericht['gelenke'], ['l_shin', 'l_foot'])
        self.assertEqual(h[0].tolist(), [0, 1])
        np.testing.assert_array_equal(h[1].numpy(), [[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]])

    def test_unter_dem_rock_raet_mia(self):
        h, bericht = self._rechnen(ziel({'l_oberschenkel': (0, 50), 'l_unterschenkel': (0, 50)}), {('thigh', 'shin'): 0, ('shin', 'foot'): 0})
        self.assertIsNone(h)
        self.assertEqual(bericht['gemeinsame_huelle'], ['l_shin', 'l_foot'])

    def test_haut_haelt_nichts(self):
        h, bericht = self._rechnen(ziel({'l_unterarm': (50, 0)}), {})
        self.assertIsNone(h)
        self.assertEqual(bericht['gelenke'], [])

    def test_unplausibles_mia_haelt_nichts(self):
        h, _b = self._rechnen(ziel({'l_oberschenkel': (0, 50)}), {}, {'mia_unplausibel': [('l_shin', 0.3)]})
        self.assertIsNone(h)
