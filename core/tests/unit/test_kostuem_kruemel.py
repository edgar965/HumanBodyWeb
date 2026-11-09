"""`Kostuemkruemel` auf Kunstdaten (roboter, 07.11.2026: Krümel neben dem Unterarm hingen am Rumpf und schwebten im Tanz).
Stück: Gitter als Hauptteil, dazu kleine Dreiecke nah und fern. Ohne Datenbank.
    1  Krümel neben dem Rest: nimmt seinen nächsten Punkt
    2  Krümel fern vom Rest: bleibt für sich
    3  Stück ohne Krümel: None
    4  nur gleich große kleine Inseln, kein Rest: None
    5  `erben` übernimmt Knochen und Gewichte nur auf den Krümelpunkten
    6  Riss: Krümel an fremdem Knochen wird rot, an denselben Knochen nicht
    7  Langer Streifen neben dem Rest: erbt nicht (`WEITE_MAX_M`), die Prüfung sieht ihn
    8  Eine Quelle je Insel: alle Punkte des Krümels nehmen denselben Punkt des Rests
Sabotage (von Hand): in `paare` `nah` immer wahr → Fall 2 rot; `RISS_M` 10 m → Fall 6 rot; in `quelle` `krumel` immer wahr → Fall 7 rot; `von[kr[krumel]] = naechster[krumel]` → Fall 8 rot.
"""
import sys
import unittest
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'mesh3dai'))
from mesh3dai_kostuem_kruemel import Kostuemkruemel  # noqa: E402

SP = 40
S = 0.01


def gitter():
    i, j = np.meshgrid(np.arange(SP), np.arange(SP), indexing='ij')
    p = np.stack([i.ravel() * S, j.ravel() * S, np.zeros(SP * SP)], 1)
    a = (i[:-1, :-1] * SP + j[:-1, :-1]).ravel()
    b, c, d = a + 1, a + SP + 1, a + SP
    return p, np.concatenate([np.stack([a, b, c], 1), np.stack([a, c, d], 1)])


def dreieck(lage, n, weite=0.002):
    """Drei Punkte bei `lage`, Nummern ab `n`."""
    return np.asarray(lage, dtype=np.float64) + np.array([[0.0, 0, 0], [weite, 0, 0], [0, 0.002, 0]]), np.array([[n, n + 1, n + 2]])


@unittest.skipUnless(torch.cuda.is_available(), 'Kostuemgpu rechnet nur auf der Karte')
class Fall(unittest.TestCase):
    databases = []

    def setUp(self):
        self.o = Kostuemkruemel()
        self.k = self.o.k

    def stueck(self, *lagen, weite=0.002):
        p, f = gitter()
        for lage in lagen:
            q, g = dreieck(lage, len(p), weite)
            p, f = np.concatenate([p, q]), np.concatenate([f, g])
        return self.k.feld(p, torch.float64), f

    def test_streifen_erbt_nicht(self):
        p, f = self.stueck([0.0, 0.0, 0.005], weite=0.3)
        self.assertIsNone(self.o.quelle(p, f))
        self.assertIsNotNone(self.o.paare(p, f))

    def test_eine_quelle_je_insel(self):
        p, f = self.stueck([0.0, 0.0, 0.005], weite=0.1)
        _maske, von = self.o.quelle(p, f)
        self.assertEqual(von[SP * SP:].tolist(), [0, 0, 0])

    def test_krumel_nah_nimmt_den_naechsten_punkt(self):
        p, f = self.stueck([0.0, 0.0, 0.005])
        maske, von = self.o.quelle(p, f)
        self.assertEqual(maske.nonzero()[:, 0].tolist(), [SP * SP, SP * SP + 1, SP * SP + 2])
        self.assertEqual(int(von[SP * SP]), 0)
        self.assertEqual(int(von[0]), 0)

    def test_krumel_fern_bleibt_fuer_sich(self):
        p, f = self.stueck([0.0, 0.0, 0.1])
        self.assertIsNone(self.o.quelle(p, f))

    def test_stueck_ohne_krumel(self):
        p, f = self.stueck()
        self.assertIsNone(self.o.quelle(p, f))

    def test_nur_kleine_inseln(self):
        ps, fs = [], []
        for i in range(120):
            q, g = dreieck([i * 0.1, 0.0, 0.0], 3 * i)
            ps.append(q)
            fs.append(g)
        p = self.k.feld(np.concatenate(ps), torch.float64)
        self.assertIsNone(self.o.quelle(p, np.concatenate(fs)))

    def test_erben(self):
        kn = torch.tensor([[1, 2], [3, 4], [5, 6]])
        gw = torch.tensor([[200, 55], [100, 155], [10, 245]])
        maske = torch.tensor([False, False, True])
        kn2, gw2 = Kostuemkruemel.erben(torch, (maske, torch.tensor([0, 1, 0])), kn, gw)
        self.assertEqual(kn2.tolist(), [[1, 2], [3, 4], [1, 2]])
        self.assertEqual(gw2.tolist(), [[200, 55], [100, 155], [200, 55]])

    def test_riss(self):
        class Quelle:
            pass

        p, f = self.stueck([0.0, 0.0, 0.005])
        ruhe = p.clone()
        self.k.haeuten = lambda _q, r, _k, _g: p                               # Haltung fest, die Ruhe entscheidet
        s = {'id': 'a', 'dreiecke': f, 'knochen': None, 'gewicht': None, 'ruhe': ruhe}
        try:
            self.assertFalse(self.o.messen([s], Quelle())['stuecke']['a']['rot'])
            ruhe[SP * SP:] += torch.tensor([0.3, 0.0, 0.0], dtype=ruhe.dtype, device=ruhe.device)
            self.assertTrue(self.o.messen([s], Quelle())['stuecke']['a']['rot'])
        finally:
            del self.k.haeuten


if __name__ == '__main__':
    unittest.main()
