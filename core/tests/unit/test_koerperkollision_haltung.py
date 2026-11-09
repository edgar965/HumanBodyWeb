"""`Koerperkollision` Fassung 3 auf Kunstdaten (05.11.2026, Edgar: „fixe die offenen punkte im Tanz“): erlaubt ist nur die Tiefe, die ein Punkt in der Ruhe UND in der Haltung der KI in einer Kapsel hat.
    1  liegt in der Ruhe in der Kapsel, in der Haltung nicht: wird geschoben (Steg zwischen den Beinen, Edgar2010)
    2  liegt in Ruhe und Haltung in der Kapsel: bleibt (Bund über der Hüfte)
    3  liegt in der Haltung in der Kapsel, in der Ruhe nicht: wird geschoben (Flanke neben dem Arm, Fassung „nur Haltung“ verworfen)
    4  Kapseln ohne `haltung` (Fassung 2): wie bisher nur die Ruhe, `lesen` nimmt sie weiter an
Sabotage (von Hand): in `_schub` `torch.minimum` durch die Haltung allein ersetzen → Fall 3 rot; die Zeile mit `s0` entfernen → Fall 1 rot; `FASSUNGEN` ohne 2 → Fall 4 rot.
"""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
from KoerperKI_alle.koerperkollision import Koerperkollision

EINS = np.eye(3).tolist()


def kapseln(versch_kapsel=None):
    """Eine Kapsel an Knochen 1 längs y; `versch_kapsel`: die Kapsel steht in der Haltung so weit versetzt, Knochen 0 bleibt."""
    kap = {'fassung': 3, 'kapseln': [{'knochen': 'k', 'nummer': 1, 'a': [0.0, 0.0, 0.0], 'b': [0.0, 1.0, 0.0], 'ra': 0.1, 'rb': 0.1}]}
    if versch_kapsel is not None:
        kap['haltung'] = {'dreh': [EINS, EINS], 'versch': [[0.0, 0.0, 0.0], list(versch_kapsel)]}
    return kap


class Fall(unittest.TestCase):
    def schub(self, kap, ruhe, bild_punkt):
        """Länge des Schubs eines Punkts an Knochen 0, die Kapsel steht im Bild wie in der Ruhe."""
        kollision = Koerperkollision(kap)
        kollision.GRAPHEN = 0
        r = torch.tensor([ruhe], dtype=torch.float64)
        q = torch.tensor([bild_punkt], dtype=torch.float64)
        bild = SimpleNamespace(dreh=np.stack([np.eye(3)] * 2), lage=np.zeros((2, 3)), zentren=np.zeros((2, 3)))
        kn = torch.tensor([[0, 0, 0, 0]])
        gw = torch.tensor([[1.0, 0.0, 0.0, 0.0]], dtype=torch.float64)
        return float((kollision.schieben(q, kn, gw, bild, ruhe=r) - q).norm())

    def test_ruhe_tief_haltung_frei(self):
        self.assertAlmostEqual(self.schub(kapseln((1.0, 0.0, 0.0)), [0.05, 0.5, 0.0], [0.05, 0.5, 0.0]), 0.05, places=6)

    def test_in_ruhe_und_haltung_tief(self):
        self.assertAlmostEqual(self.schub(kapseln((0.0, 0.0, 0.0)), [0.05, 0.5, 0.0], [0.05, 0.5, 0.0]), 0.0, places=6)

    def test_haltung_tief_ruhe_frei(self):
        self.assertAlmostEqual(self.schub(kapseln((0.2, 0.0, 0.0)), [0.2, 0.5, 0.0], [0.05, 0.5, 0.0]), 0.05, places=6)

    def test_ohne_haltung(self):
        self.assertAlmostEqual(self.schub(kapseln(None), [0.05, 0.5, 0.0], [0.05, 0.5, 0.0]), 0.0, places=6)
        self.assertAlmostEqual(self.schub(kapseln(None), [0.5, 0.5, 0.0], [0.05, 0.5, 0.0]), 0.05, places=6)
        with tempfile.TemporaryDirectory(dir=str(Path(__file__).parent)) as d:
            (Path(d) / Koerperkollision.DATEI).write_text(json.dumps(dict(kapseln(None), fassung=2)), encoding='utf-8')
            self.assertIsNotNone(Koerperkollision.lesen(Path(d)))
