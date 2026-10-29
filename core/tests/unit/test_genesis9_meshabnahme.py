# -*- coding: utf-8 -*-
"""`G9meshabnahme`: ist die eingepasste Figur ein Mensch? (28.10.2026, Edgar: „Wichtig ist, dass es ein Mensch ist und nicht Armgelenke hat, die so groß wie eine Stecknadel sind,
kaputte Hände oder kaputte Füße“ — „mach deinen Vorschlag“). Eine nicht bestandene Abnahme legt in `G9meshgenesis` keine Mesh-Regler ab; misst sie falsch, landet eine kaputte
Figur im Bedienfeld oder eine gute nicht. Geprüft an einer Kunstfigur, ohne Genesis: je Gelenk ein Rohr aus drei Ringen (oben ganz am oberen Knochen, Mitte halb/halb, unten ganz
am unteren) — die Mitte ist der Gelenkring der Abnahme.

1. Dieselbe Figur besteht: Dicke 1, nichts umgeklappt.
2. Ein Gelenkring auf 80 % gestaucht fällt durch, mit dem Gelenk im Grund — die anderen Gelenke bleiben 1.
3. Ein Rohr um seine Achse um 180° verdreht (gleicher Radius, jedes Dreieck zeigt gegen seine Startlage) fällt nur wegen der umgeklappten Dreiecke durch, nicht wegen der Dicke.
"""
import math

import torch
from django.test import SimpleTestCase
from Genesis9.meshabnahme import G9meshabnahme

#: Knochen (Name, Eltern) — die sechs je Seite, die `G9meshabnahme.GELENKE` braucht
KNOCHEN = [('hip', None)] + [(n, e) for s in 'lr' for n, e in (('%s_upperarm' % s, 'hip'), ('%s_forearm' % s, '%s_upperarm' % s), ('%s_hand' % s, '%s_forearm' % s),
                                                                ('%s_thigh' % s, 'hip'), ('%s_shin' % s, '%s_thigh' % s), ('%s_foot' % s, '%s_shin' % s))]
UM = 8                 # Punkte je Ring
RADIUS = 0.04


class _Koerper:
    """Attrappe von `G9meshkoerper`: Punkte, Hautgewichte (die vier größten), Knochen."""

    def __init__(self):
        self.namen = [n for n, _e in KNOCHEN]
        self.eltern = [self.namen.index(e) if e else -1 for _n, e in KNOCHEN]
        punkte, w, wi, tri, self.rohr = [], [], [], [], {}
        for k, (_g, oben, unten) in enumerate([(g, '%s_%s' % (s, o), '%s_%s' % (s, u)) for g, o, u in G9meshabnahme.GELENKE for s in 'lr']):
            erster = len(punkte)
            self.rohr[oben + '>' + unten] = list(range(erster, erster + 3 * UM))
            for ring, (a, b) in enumerate(((1.0, 0.0), (0.5, 0.5), (0.0, 1.0))):
                for i in range(UM):
                    winkel = 2 * math.pi * i / UM
                    punkte.append([k * 0.5 + RADIUS * math.cos(winkel), -0.1 * ring, RADIUS * math.sin(winkel)])
                    w.append([a, b, 0.0, 0.0])
                    wi.append([self.namen.index(oben), self.namen.index(unten), 0, 0])
            for ring in range(2):
                for i in range(UM):
                    p, q = erster + ring * UM + i, erster + ring * UM + (i + 1) % UM
                    tri += [[p, q, p + UM], [q, q + UM, p + UM]]
        self.p0 = torch.tensor(punkte, dtype=torch.float32)
        self.w = torch.tensor(w, dtype=torch.float32)
        self.w_index = torch.tensor(wi, dtype=torch.long)
        self.tri = tri


class DieAbnahme(SimpleTestCase):
    def setUp(self):
        self.k = _Koerper()
        self.ab = G9meshabnahme(self.k, self.k.tri, [-1] * len(self.k.p0))

    def test_dieselbe_figur_besteht(self):
        a = self.ab.bewerten({'parametrisch': self.k.p0, 'ergebnis': self.k.p0.clone()})
        self.assertTrue(a['bestanden'], a['gruende'])
        self.assertEqual(a['ergebnis']['umgeklappt'], 0)
        self.assertEqual(len(a['ergebnis']['gelenkdicke']), 8)
        for name, v in a['ergebnis']['gelenkdicke'].items():
            self.assertAlmostEqual(v, 1.0, places=3, msg=name)

    def test_gestauchtes_handgelenk_faellt_durch(self):
        x = self.k.p0.clone()
        mitte = self.k.rohr['l_forearm>l_hand'][UM:2 * UM]
        m = x[mitte].mean(0)
        x[mitte] = m + (x[mitte] - m) * 0.8
        a = self.ab.bewerten({'parametrisch': self.k.p0, 'ergebnis': x})
        self.assertFalse(a['bestanden'])
        self.assertAlmostEqual(a['ergebnis']['gelenkdicke']['Handgelenk l'], 0.8, places=3)
        self.assertTrue(any('Handgelenk l' in g for g in a['gruende']), a['gruende'])
        self.assertAlmostEqual(a['ergebnis']['gelenkdicke']['Handgelenk r'], 1.0, places=3)

    def test_verdrehtes_rohr_faellt_nur_wegen_umgeklappter_dreiecke_durch(self):
        x = self.k.p0.clone()
        rohr = self.k.rohr['r_thigh>r_shin']
        achse = x[rohr].mean(0)
        x[rohr, 0] = 2 * achse[0] - x[rohr, 0]               # 180° um die Achse: gleicher Radius, jedes Dreieck auf der Gegenseite
        x[rohr, 2] = 2 * achse[2] - x[rohr, 2]
        a = self.ab.bewerten({'parametrisch': self.k.p0, 'ergebnis': x})
        self.assertGreater(a['ergebnis']['umgeklappt'], a['umgeklappt_mehr_erlaubt'])
        self.assertFalse(a['bestanden'])
        self.assertTrue(all('Gelenkdicke' not in g for g in a['gruende']), a['gruende'])
        self.assertTrue(any('umgeklappt' in g for g in a['gruende']), a['gruende'])
