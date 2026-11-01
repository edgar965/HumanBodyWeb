# -*- coding: utf-8 -*-
"""`KoerperKI_Fotos.Hautteile` — Glied je Punkt mit Seite und Spiegelteil (31.10.2026, für `KoerperKI_alle.Ergaenzung` in `Koerperhautbild`) an einem Kunstskelett ohne Figur.

1. Ober- und Unterschenkel derselben Seite sind EIN Glied (`bein_l`), die Zehe gehört zum Fuß, ein Knochen ohne Anker zum Rumpf.
2. Das Spiegelteil von `bein_l` ist `bein_r` und umgekehrt, der Rumpf spiegelt auf sich selbst.
"""
import sys
import unittest
from types import SimpleNamespace

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_Fotos.hautteile import Hautteile  # noqa: E402

KNOCHEN = [('hip', -1), ('l_thigh', 0), ('l_shin', 1), ('l_foot', 2), ('l_toes', 3), ('r_thigh', 0), ('r_shin', 5), ('spine1', 0)]


def netz():
    kin = {'knochen': [{'name': n, 'eltern': e} for n, e in KNOCHEN]}
    k = torch.arange(len(KNOCHEN))[:, None].expand(len(KNOCHEN), 2).clone()           # Punkt j hängt nur an Knochen j
    w = torch.tensor([[1.0, 0.0]] * len(KNOCHEN))
    return SimpleNamespace(kin=kin, knochen=k, gewicht=w)


class Hautteilegliedertest(unittest.TestCase):

    def test_1_glieder_mit_seite(self):
        t = Hautteile(netz())
        name = [t.glieder[int(i)] for i in t.punkt_teil]
        self.assertEqual(name, ['rumpf', 'bein_l', 'bein_l', 'fuss_l', 'fuss_l', 'bein_r', 'bein_r', 'rumpf'])

    def test_2_spiegelteil(self):
        t = Hautteile(netz())
        sp = {t.glieder[i]: t.glieder[int(j)] for i, j in enumerate(t.teil_spiegel)}
        self.assertEqual(sp['bein_l'], 'bein_r')
        self.assertEqual(sp['bein_r'], 'bein_l')
        self.assertEqual(sp['fuss_l'], 'fuss_r')
        self.assertEqual(sp['rumpf'], 'rumpf')


if __name__ == '__main__':
    unittest.main()
