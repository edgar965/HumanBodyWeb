# -*- coding: utf-8 -*-
"""Einpasskoerper — Attrappe von `KoerperKI_alle.koerpermodell.Koerpermodell`, so weit `KoerperKI_Fotos.Fotoeinpassung` es benutzt (24.10.2026).

Benutzt werden: `g`, `n.index(knochen)`, `kin.frei`, `r0`, `p0`, `mit_form`, `klemmen(r)`, `koerper(r, roh, mit_gelenken)` → (x, p, enden, d, w), `hoehe(r)` (feste Körpergröße), `volumen(r)`, `kopfform(r)`. Der Körper ist ein Quader
0,4 × 1,6 × 0,25 m, die Gelenke der `Posenpunkte` und der Kopf sitzen an festen Stellen (+x = linke Körperseite); Form = ein Maßstab r (1,), Haltung = eine Verschiebung roh (3,):
x = Quader · r[0] + roh[:3]. Genutzt von `unit/test_koerperki_fotos_einpassung.py` und `longrunner/test_koerperki_fotos_einpassen.py`.
Seit 01.11.2026 dazu `kn`, `gw`, `ruhe(r)`, `koerper_aus(ruhe, c, roh, mit_gelenken)`, `eigen_zug()`,
`zusatz_parameter()`, `zusatz_klemmen()` und die Knochen der `Posenpunkte.ZUSATZ` — ohne sie brachen
Unit- und LongRunner-Test in `Fotoeinpassung` ab.
"""
import sys
from types import SimpleNamespace

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_Fotos.posenpunkte import Posenpunkte  # noqa: E402


class Einpasskoerper:
    #: dazu Zehen und Mittelfinger: `Fotoeinpassung.__init__` sucht die Knochen der
    #: `Posenpunkte.ZUSATZ` (seit 25.10.2026, R7)
    LAGE = {'l_upperarm': (0.18, 0.55, 0.0), 'l_forearm': (0.18, 0.25, 0.02), 'l_hand': (0.18, 0.0, 0.05), 'l_thigh': (0.1, -0.05, 0.0), 'l_shin': (0.1, -0.4, 0.03),
            'l_foot': (0.1, -0.75, -0.02), 'head': (0.0, 0.7, 0.0),
            'l_bigtoe2': (0.08, -0.8, 0.1), 'l_pinkytoe2': (0.14, -0.8, 0.08), 'l_mid1': (0.18, -0.08, 0.05)}

    def __init__(self, mit_form=True, abstand=0.05):
        self.g = torch.device('cpu')
        self.namen = [k for _g, k, _p, _f in Posenpunkte.GELENKE] + ['head']
        self.namen += [k.rstrip('>') for _g, k, _p, _f in Posenpunkte.ZUSATZ]
        self.n = self                                   # wie `Koerpernetz.index`
        self.kin = SimpleNamespace(frei=[0, 1, 2])      # wie `Kinematik.frei`: die freien Werte am Anfang von roh
        self.mit_form = mit_form
        self.r0 = torch.ones(1) if mit_form else torch.zeros(0)
        a = [torch.arange(-h, h + 1e-6, abstand) for h in (0.2, 0.8, 0.125)]
        self.p0 = torch.stack(torch.meshgrid(*a, indexing='ij'), -1).reshape(-1, 3)
        lage = dict(self.LAGE, **{'r' + k[1:]: (-v[0], v[1], v[2]) for k, v in self.LAGE.items() if k.startswith('l_')})
        self.gelenke0 = torch.tensor([lage[k] for k in self.namen])
        # wie `Koerpermodell.kn`/`gw` (für `Randrest.ziele`): jeder Punkt ganz am ersten Knochen
        self.kn, self.gw = torch.zeros((len(self.p0), 1), dtype=torch.long), torch.ones((len(self.p0), 1))

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

    def ruhe(self, r):
        """Wie `Koerpermodell.ruhe`: (Ruhelage, Gelenke in Ruhe) — Quader und feste Gelenke mal Maßstab."""
        m = r[0] if self.mit_form else 1.0
        return self.p0 * m, self.gelenke0 * m

    def koerper_aus(self, ruhe, c, roh, mit_gelenken=False):
        """Wie `Koerpermodell.koerper_aus`: Haltung = Verschiebung roh[:3]."""
        x = ruhe + roh[:3]
        if not mit_gelenken:
            return x
        p = c + roh[:3]
        return x, p, p, torch.eye(3).expand(len(p), 3, 3), torch.zeros((len(p), 3))

    def koerper(self, r, roh, mit_gelenken=False):
        return self.koerper_aus(*self.ruhe(r), roh, mit_gelenken)

    def eigen_zug(self):
        """Wie `Koerpermodell.eigen_zug` ohne Anfasser und Kombiregler."""
        return torch.zeros(())

    def zusatz_parameter(self):
        return []

    def zusatz_klemmen(self):
        """Nichts zu klemmen (keine Anfasser, keine Kombiregler)."""
