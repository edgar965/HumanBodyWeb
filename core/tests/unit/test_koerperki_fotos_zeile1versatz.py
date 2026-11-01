# -*- coding: utf-8 -*-
"""`KoerperKI_Fotos.Zeile1versatz` — die Form der Zeile 1 als Versatz der Ruhelage (31.10.2026 nachts) an einem Kunstnetz mit zwei Knochen, ohne Figur und ohne Datei der Seite.

1. Ein bekannter Versatz der Ruhelage, mit der Haltung eines Fotos gehäutet, kommt zurück (Drehung um 90°: ohne Rückdrehung zeigte er in die falsche Richtung).
2. An einem Punkt, an dem sich die Drehungen zweier Knochen aufheben (Gewicht halb/halb, 180° gegeneinander), bleibt der Versatz so groß wie im Bild — mit der Inversen der Mischung
   lief er dort gegen unendlich (Lauf zeile1a: 440 mm an der Schulter).
"""
import base64
import json
import sys
import unittest
from pathlib import Path

import numpy as np
import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_Fotos.zeile1versatz import Zeile1versatz  # noqa: E402

ABLAGE = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / '_wegwerf' / 'tests' / 'zeile1versatz'


def drehung_z(grad):
    w = np.radians(grad)
    return torch.tensor([[np.cos(w), -np.sin(w), 0], [np.sin(w), np.cos(w), 0], [0, 0, 1]], dtype=torch.float32)


class Netz:
    """Zwei Knochen am Ursprung; Punkt i hängt mit `gewicht[i]` an ihnen."""

    def __init__(self, ruhe, gewicht):
        self.ruhe = torch.tensor(ruhe, dtype=torch.float32)
        self.gewicht = torch.tensor(gewicht, dtype=torch.float32)
        self.knochen = torch.tensor([[0, 1]] * len(ruhe))
        self.zentren = torch.zeros((2, 3))

    def haeuten(self, p, d):
        x = self.ruhe[:, None, :] - self.zentren[self.knochen]
        y = (d[self.knochen] @ x[..., None])[..., 0] + p[self.knochen]
        return (self.gewicht[..., None] * y).sum(1) / self.gewicht.sum(1, keepdim=True)


class Zeile1versatztest(unittest.TestCase):

    def _job(self, punkte_zeile1):
        ordner = ABLAGE / 'job'
        (ordner / 'abnahme').mkdir(parents=True, exist_ok=True)
        fotos = {'1': base64.b64encode(np.asarray(punkte_zeile1, dtype='<f4').tobytes()).decode('ascii')}
        (ordner / 'abnahme' / 'training_figur.json').write_text(json.dumps({'genesis': {'fotos': fotos}}), encoding='utf-8')
        return ordner

    def test_1_versatz_kommt_zurueck(self):
        netz = Netz([[1, 0, 0], [0, 1, 0]], [[1, 0], [1, 0]])
        d = torch.stack([drehung_z(90), drehung_z(90)])
        p = torch.zeros((2, 3))
        versatz = torch.tensor([[0.01, 0, 0], [0, 0, 0.02]])
        ziel = Netz((netz.ruhe + versatz).tolist(), netz.gewicht.tolist()).haeuten(p, d)
        lage = {'je_foto': {'1.jpg': {'p': p, 'd': d}}}
        f = Zeile1versatz.felder(netz, lage, self._job(ziel.numpy()), log=lambda _t: None)
        np.testing.assert_allclose(f['zeile1_versatz'], versatz.numpy(), atol=1e-6)

    def test_2_aufgehobene_drehung_bleibt_endlich(self):
        netz = Netz([[0, 0, 0]], [[0.5, 0.5]])
        d = torch.stack([drehung_z(90), drehung_z(-90)])          # Mischung 0.5·(R + Rᵀ) hat in x/y den Rang 0
        p = torch.zeros((2, 3))
        x = netz.haeuten(p, d)
        ziel = x + torch.tensor([[0.0, 0.03, 0.0]])
        lage = {'je_foto': {'1.jpg': {'p': p, 'd': d}}}
        f = Zeile1versatz.felder(netz, lage, self._job(ziel.numpy()), log=lambda _t: None)
        self.assertLess(float(np.linalg.norm(f['zeile1_versatz'][0])), 0.031)


if __name__ == '__main__':
    unittest.main()
