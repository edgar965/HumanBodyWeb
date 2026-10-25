# -*- coding: utf-8 -*-
"""Einpasskoerper — Attrappe von `KoerperKI_alle.koerpermodell.Koerpermodell`, so weit `KoerperKI_Fotos.Fotoeinpassung` es benutzt (24.10.2026).

Benutzt werden: `g`, `n.index(knochen)`, `kin.frei`, `r0`, `p0`, `mit_form`, `klemmen(r)`, `koerper(r, roh, mit_gelenken)` → (x, p, enden, d, w), `hoehe(r)` (feste Körpergröße), `volumen(r)`, `kopfform(r)`. Der Körper ist ein Quader
0,4 × 1,6 × 0,25 m, die Gelenke der `Posenpunkte` und der Kopf sitzen an festen Stellen (+x = linke Körperseite); Form = ein Maßstab r (1,), Haltung = eine Verschiebung roh (3,):
x = Quader · r[0] + roh[:3]. Genutzt von `unit/test_koerperki_fotos_einpassung.py` und `longrunner/test_koerperki_fotos_einpassen.py`.
"""
import sys
from types import SimpleNamespace

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_Fotos.posenpunkte import Posenpunkte  # noqa: E402


class Einpasskoerper:
    LAGE = {'l_upperarm': (0.18, 0.55, 0.0), 'l_forearm': (0.18, 0.25, 0.02), 'l_hand': (0.18, 0.0, 0.05), 'l_thigh': (0.1, -0.05, 0.0), 'l_shin': (0.1, -0.4, 0.03),
            'l_foot': (0.1, -0.75, -0.02), 'head': (0.0, 0.7, 0.0)}

    def __init__(self, mit_form=True, abstand=0.05):
        self.g = torch.device('cpu')
        self.namen = [k for _g, k, _p, _f in Posenpunkte.GELENKE] + ['head']
        self.n = self                                   # wie `Koerpernetz.index`
        self.kin = SimpleNamespace(frei=[0, 1, 2])      # wie `Kinematik.frei`: die freien Werte am Anfang von roh
        self.mit_form = mit_form
        self.r0 = torch.ones(1) if mit_form else torch.zeros(0)
        a = [torch.arange(-h, h + 1e-6, abstand) for h in (0.2, 0.8, 0.125)]
        self.p0 = torch.stack(torch.meshgrid(*a, indexing='ij'), -1).reshape(-1, 3)
        lage = dict(self.LAGE, **{'r' + k[1:]: (-v[0], v[1], v[2]) for k, v in self.LAGE.items() if k.startswith('l_')})
        self.gelenke0 = torch.tensor([lage[k] for k in self.namen])

    def index(self, name):
        return self.namen.index(name)

    def klemmen(self, r):
        return r.clamp(0.8, 1.25)

    def hoehe(self, r):
        """Wie `Koerpermodell.hoehe`: der Quader ist 1,6 m hoch, mal Maßstab."""
        return 1.6 * (r[0] if self.mit_form else 1.0)

    def volumen(self, r):
        """Wie `Koerpermodell.volumen`: Quader 0,4 × 1,6 × 0,25 m, mal Maßstab hoch drei."""
        return 0.16 * (r[0] if self.mit_form else 1.0) ** 3

    def kopfform(self, r):
        """Wie `Koerpermodell.kopfform`: der Maßstab ändert die Kopfform nicht (der Kopf ist ein Punkt)."""
        return r.sum() * 0.0

    def koerper(self, r, roh, mit_gelenken=False):
        m = r[0] if self.mit_form else 1.0
        x = self.p0 * m + roh[:3]
        if not mit_gelenken:
            return x
        p = self.gelenke0 * m + roh[:3]
        return x, p, p, torch.eye(3).expand(len(p), 3, 3), torch.zeros((len(p), 3))
