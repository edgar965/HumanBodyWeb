"""Haar in Weg z, 14.11.2026 (Edgar zum Zauberer: „Die allgemeine Drapierung und Erstellung von Haar usw. muss generisch besser werden“):
    1  `Haarmasse.messen` → `stirn`: eine Kugel als Kopf, Haar als Kappe — mit Pony vor der Stirn 1, ohne Pony 0; ohne Kopfpunkte in Stirnhöhe ein Fehler statt stumm 0
    2  `Bartengine.strecken`: ein Bart aus Punkten unter dem Kinn wird auf den Saum des Netzbarts gestreckt und in der Tiefe an ihn gelegt; Punkte über der Kinnlinie bleiben, die
       übrigen Felder der Ablage bleiben
    3  `Haarkatalog.zeigbar`: Deckkraft unter `DECKKRAFT_ANTEIL` nicht zeigbar, ab ihr und ohne Feld (Fassung 1) zeigbar
Synthetische Daten, Dateien nur in einem Ordner unter ProjektTemp. Rechnet auf der Karte.
Sabotage (von Hand): in `Haarmasse.messen` `vorn_z - cls.STIRN_TIEFE_M` durch `vorn_z + cls.STIRN_TIEFE_M` ersetzen (Band leer) → Fall 1 rot; in `Bartengine.strecken` `dreh - unter * faktor`
durch `dreh - unter` ersetzen → Fall 2 rot; in `Haarkatalog.zeigbar` `>=` durch `>` → Fall 3 rot.
"""
import math
import sys
import tempfile
import unittest
from pathlib import Path

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'meshgenesis'))
sys.path.insert(0, str(settings.TOOLS_ROOT))
from KoerperKI_alle.npztorch import Npztorch  # noqa: E402
from haar_Bart.haarkatalog import Haarkatalog  # noqa: E402
from meshgenesis_haarmasse import Haarmasse  # noqa: E402
from haar_Bart.bart_engine import Bartengine  # noqa: E402

G = 'cuda'
ABLAGE = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / '_testlauf'


def kugel(r, mitte, n=60):
    """Punkte auf einer Kugel (n × 2n Raster), (M, 3) float64."""
    t = torch.linspace(0.02, math.pi - 0.02, n, dtype=torch.float64, device=G)
    f = torch.linspace(0, 2 * math.pi, 2 * n + 1, dtype=torch.float64, device=G)[:-1]
    tt, ff = torch.meshgrid(t, f, indexing='ij')
    p = torch.stack([torch.sin(tt) * torch.cos(ff), torch.cos(tt), torch.sin(tt) * torch.sin(ff)], -1).reshape(-1, 3)
    return p * r + torch.tensor(mitte, dtype=torch.float64, device=G)


class TestStirn(unittest.TestCase):
    databases = []

    def setUp(self):
        self.kopf = kugel(0.1, [0.0, 1.6, 0.0])          # Scheitel 1,70, Kinn 1,50, vorn z = +0,1
        self.maske = torch.ones(len(self.kopf), dtype=torch.bool, device=G)
        self.kappe = kugel(0.106, [0.0, 1.6, 0.0])
        self.kappe = self.kappe[self.kappe[:, 1] > 1.66]   # nur über der Stirn (oben 4 cm)

    def test_mit_und_ohne_pony(self):
        ohne = Haarmasse.messen(self.kappe, self.kopf, self.maske)
        pony = kugel(0.106, [0.0, 1.6, 0.0])
        pony = pony[(pony[:, 1] > 1.58) & (pony[:, 1] <= 1.66) & (pony[:, 2] > 0.05)]
        mit = Haarmasse.messen(torch.cat([self.kappe, pony]), self.kopf, self.maske)
        self.assertLess(float(ohne[7]), 0.05)
        self.assertGreater(float(mit[7]), 0.95)

    def test_ohne_stirnhoehe_fehler(self):
        maske = self.kopf[:, 1] > 1.66                       # nur die Schädelkappe als Kopf: in Stirnhöhe kein Punkt
        with self.assertRaises(ValueError):
            Haarmasse.messen(self.kappe, self.kopf, maske)


class TestBart(unittest.TestCase):
    databases = []

    def test_strecken_und_anlegen(self):
        kinn = 1.45
        y = torch.linspace(1.40, 1.50, 41, dtype=torch.float64, device=G)                 # Bart: 5 cm unter dem Kinn, 5 cm darüber
        x = torch.linspace(-0.04, 0.04, 9, dtype=torch.float64, device=G)
        yy, xx = torch.meshgrid(y, x, indexing='ij')
        bart = torch.stack([xx, yy, torch.full_like(xx, 0.10)], -1).reshape(-1, 3)
        yn = torch.linspace(1.25, 1.45, 81, dtype=torch.float64, device=G)               # Netzbart bis 20 cm unter dem Kinn, 3 cm weiter vorn
        yy, xx = torch.meshgrid(yn, x, indexing='ij')
        netz = torch.stack([xx, yy, torch.full_like(xx, 0.13)], -1).reshape(-1, 3)
        ABLAGE.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=str(ABLAGE)) as tmp:
            ordner = Path(tmp)
            (ordner / 'anzeige').mkdir()
            Npztorch.speichern(ordner / 'anzeige' / 'netz.npz', ruhe=bart.float(), material=torch.zeros(len(bart), dtype=torch.int16, device=G))
            bericht = Bartengine(None).strecken(ordner, netz, kinn)
            with Npztorch.lesen(ordner / 'anzeige' / 'netz.npz') as z:
                neu = torch.as_tensor(z['ruhe'], device=G).double()
                self.assertIn('material', z.files)
        dreh = kinn + Bartengine.UEBER_KINN_M
        soll = (dreh - float(torch.quantile(netz[:, 1], 0.02))) / (dreh - float(torch.quantile(bart[:, 1], 0.02)))
        self.assertAlmostEqual(bericht['faktor'], min(soll, Bartengine.STRECKUNG), delta=0.05)
        self.assertLess(abs(float(torch.quantile(neu[:, 1], 0.02)) - float(torch.quantile(netz[:, 1], 0.02))), 0.01)
        oben = bart[:, 1] >= dreh
        self.assertTrue(torch.allclose(neu[oben], bart[oben].float().double(), atol=1e-6))
        tief = neu[:, 1] < dreh - 0.05
        self.assertLess(float((neu[tief, 2] - 0.13).abs().max()), 0.005)


class TestZeigbar(unittest.TestCase):
    databases = []

    def test_grenze(self):
        a = Haarkatalog.DECKKRAFT_ANTEIL
        self.assertFalse(Haarkatalog.zeigbar({'deckkraft': a - 0.01}))
        self.assertTrue(Haarkatalog.zeigbar({'deckkraft': a}))
        self.assertTrue(Haarkatalog.zeigbar({}))
