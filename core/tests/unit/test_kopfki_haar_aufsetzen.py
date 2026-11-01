# -*- coding: utf-8 -*-
"""Tests für `KopfKI.Fotohaarschale.aufsetzen` und `auf_figur` (01.11.2026, Besitzer 2d-3d-AI): die Haarschale auf einen anderen Kopf derselben Punktfolge setzen.

WARUM: Bis zum 01.11.2026 wurde die Schale (am Kopf der Startfigur geschnitten) nur um die Differenz der Kopfmitten auf die eingepasste Figur verschoben. Wo die Einpassung den Schädel
anders formte, stach er durch die nur Millimeter hohe Schale (`_wegwerf/ai2d3d/haut_haar_lage_probe.py`: Baron 19,8 %, Ed2010 49,1 % der Punkte; EdgarTrip kahler Hinterkopf).
Aufgesetzt liegt jeder Punkt genau seine Höhe über dem NEUEN Kopf — auch wo der Kopf gewachsen ist —, und auf dem alten Kopf kommt dieselbe Schale wieder heraus.
"""
import sys
import unittest

import numpy as np
import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from HaarKI.haarschale import Haarschale  # noqa: E402
from KopfKI.fotohaarschale import Fotohaarschale  # noqa: E402

D = torch.float64
#: Tetraeder mit nach außen zeigender Reihenfolge (wie `test_haarki_haarschale`)
TETRA = torch.tensor([[1.0, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], dtype=D) * 0.05
TETRA_D = torch.tensor([[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]])


class NpzAttrappe(dict):
    """Wie `np.load(…)`: Felder über [] und ihre Namen in `files`."""

    @property
    def files(self):
        return list(self)


class DasAufsetzen(unittest.TestCase):

    def schale(self, kopf, stelle, hoehe):
        s = Haarschale(kopf, TETRA_D)
        p, n = s.punkte.double(), s.normalen.double()
        return p[stelle] + hoehe[:, None] * n[stelle]

    def test_auf_dem_alten_kopf_dieselbe_schale(self):
        stelle = torch.arange(0, 34, 2)
        hoehe = torch.linspace(0.004, 0.02, len(stelle), dtype=D)
        q = Fotohaarschale.aufsetzen(TETRA, TETRA_D, stelle, hoehe)
        self.assertLess(float((q - self.schale(TETRA, stelle, hoehe)).abs().max()), 1e-6)  # Haarschale rechnet in float32

    def test_gewachsener_kopf_sticht_nicht_durch(self):
        stelle = torch.arange(34)
        hoehe = torch.full((34,), 0.004, dtype=D)
        gross = TETRA.clone()
        gross[0] *= 1.6                                                       # eine Ecke 3 cm weiter draußen (wie ein Hinterkopf, den die Einpassung wachsen ließ)
        neu_p = Haarschale(gross, TETRA_D)
        q = Fotohaarschale.aufsetzen(gross, TETRA_D, stelle, hoehe)
        ueber = ((q - neu_p.punkte.double()) * neu_p.normalen.double()).sum(1)
        self.assertTrue(torch.allclose(ueber, hoehe, atol=1e-6))
        alt = self.schale(TETRA, stelle, hoehe)
        verschoben = alt + (gross.mean(0) - TETRA.mean(0))                    # der alte Weg
        alt_ueber = ((verschoben - neu_p.punkte.double()) * neu_p.normalen.double()).sum(1)
        self.assertTrue(bool((alt_ueber < 0).any()))                           # Gegenprobe: verschoben stach der Schädel durch

    def test_alte_ablage_ohne_stelle_wird_verschoben(self):
        punkte = np.zeros((3, 3), dtype=np.float32)
        h = NpzAttrappe(punkte=punkte, ruhe=np.array('start'))
        kopf, start = TETRA + 0.1, TETRA
        q, versatz = Fotohaarschale.auf_figur(h, kopf, start)
        self.assertTrue(np.allclose(versatz, [0.1, 0.1, 0.1]))
        self.assertTrue(np.allclose(q, 0.1))

    def test_neue_ablage_wird_aufgesetzt(self):
        stelle = torch.arange(34)
        hoehe = torch.full((34,), 0.005, dtype=D)
        h = NpzAttrappe(punkte=np.zeros((34, 3), dtype=np.float32), stelle=stelle.numpy(), hoehe=hoehe.numpy(), kopfdreiecke=TETRA_D.numpy(), ruhe=np.array('start'))
        q, versatz = Fotohaarschale.auf_figur(h, TETRA * 1.2, TETRA)
        self.assertEqual(list(versatz), [0.0, 0.0, 0.0])
        self.assertLess(float(np.abs(q - Fotohaarschale.aufsetzen(TETRA * 1.2, TETRA_D, stelle, hoehe).numpy()).max()), 1e-12)


if __name__ == '__main__':
    unittest.main()
