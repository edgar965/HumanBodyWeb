# -*- coding: utf-8 -*-
"""Bausteine vom 14.11.2026 für Gesicht, Hände und Namen der Eigen-Stücke (Edgar: „mach die textur linke hand und gesicht generell besser bei allen jobs“, „Zauberer_Robe, Zauberer_Stab“):
    1  `Gesichtsabbild.tps` 2D ohne Glättung trifft die Stützpunkte, eine affine Abbildung kommt auch mit Glättung genau heraus; `verschmelzen` legt nahe Punkte zusammen (Ziel gemittelt)
    2  `Gesichtsabbild.tps` 3D ebenso
    3  `Gesichtsabbild.innen`: Mitte eines Quadrats innen mit halber Seite, ein Punkt außen negativ
    4  `Gesichtsabbild.bilinear`: Farbverlauf in x wird an Zwischenstellen genau gelesen, außerhalb `drin` False
    5  `Hautgrundhand.rgb_aus_lab` kehrt `Kostuemhautfarbe.lab_aus_rgb` um (bis 0,05 von 255)
    6  `Kostuembegriff.benennen`: stärkster Begriff der passenden Gruppe, Kleidung nur aus „kleid“, unter `ANTEIL` kein Name, Flicken-Flächen (Index ≥ F) zählen nicht
    7  `Gesichtmund.lippen`: bei offenem Mund bekommt ein Texel innerhalb der inneren Lippenlinie die Lippenfarbe, Lippe und Außen bleiben; geschlossener Mund ändert nichts
    8  `Kleiderbau._nur_deckkraft`: eine Gruppe nur mit Deckkraftbild (Mavick Beard) wird ein Eintrag mit Dreiecksbereich, Bildpfad und Faktor Farbe × 2 × Tönung; Gruppen ohne Bild nicht
Synthetische Daten, Dateien nur in einem Ordner unter ProjektTemp. Rechnet auf der Karte.
Sabotage (von Hand): in `Gesichtsabbild.tps` die Glättung `glaette * eye` mit 1 statt glaette → Fall 1 rot; in `_kern` für 3D r² statt r → Fall 2 rot; in `innen` das Vorzeichen tauschen →
Fall 3 rot; in `bilinear` den Versatz `- 0.5` streichen → Fall 4 rot; in `rgb_aus_lab` 116 statt 16 in `fy` → Fall 5 rot; in `Kostuembegriff.GRUPPEN` für 'oberteil' ('kleid', 'kopf') → Fall 6 rot;
in `Gesichtmund.lippen` im Gewicht `w` `d_innen` durch `d_aussen` ersetzen (die Lippe wird mit umgefärbt) → Fall 7 rot; in `_nur_deckkraft` `// 3` streichen → Fall 8 rot.
"""
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'meshgenesis'))
sys.path.insert(0, str(settings.TOOLS_ROOT))
from meshgenesis_gesichtmund import Gesichtmund  # noqa: E402
from meshgenesis_gesichtsabbild import Gesichtsabbild  # noqa: E402
from meshgenesis_hautgrundhand import Hautgrundhand  # noqa: E402
from meshgenesis_kleider_bau import Kleiderbau  # noqa: E402
from meshgenesis_kostuem_begriff import Kostuembegriff  # noqa: E402
from meshgenesis_kostuem_hautfarbe import Kostuemhautfarbe  # noqa: E402

G = 'cuda'


class TestSpline(unittest.TestCase):
    databases = []

    def test_2d_trifft_stuetzpunkte_und_affin(self):
        torch.manual_seed(1)
        von = torch.rand((40, 2), dtype=torch.float64, device=G) * 100
        nach = von + torch.randn((40, 2), dtype=torch.float64, device=G) * 3
        self.assertLess(float((Gesichtsabbild.tps(von, nach, 0.0)(von) - nach).abs().max()), 1e-6)
        a = torch.tensor([[1.1, 0.2], [-0.1, 0.9]], dtype=torch.float64, device=G)
        affin = von @ a.T + torch.tensor([5.0, -2.0], dtype=torch.float64, device=G)
        x = torch.rand((100, 2), dtype=torch.float64, device=G) * 100
        soll = x @ a.T + torch.tensor([5.0, -2.0], dtype=torch.float64, device=G)
        self.assertLess(float((Gesichtsabbild.tps(von, affin, 0.5)(x) - soll).abs().max()), 1e-6)

    def test_3d(self):
        torch.manual_seed(2)
        von = torch.rand((30, 3), dtype=torch.float64, device=G) * 0.2
        nach = von + torch.randn((30, 3), dtype=torch.float64, device=G) * 0.005
        self.assertLess(float((Gesichtsabbild.tps(von, nach, 0.0)(von) - nach).abs().max()), 1e-8)
        verschoben = von + torch.tensor([0.01, 0.02, -0.03], dtype=torch.float64, device=G)
        x = torch.rand((50, 3), dtype=torch.float64, device=G) * 0.2
        self.assertLess(float((Gesichtsabbild.tps(von, verschoben, 0.1)(x) - x - torch.tensor([0.01, 0.02, -0.03], dtype=torch.float64, device=G)).abs().max()), 1e-9)


class TestVerschmelzen(unittest.TestCase):
    databases = []

    def test_nahe_punkte_werden_einer(self):
        weit = [[0.05, 0.0, 0.0], [0.0, 0.05, 0.0], [0.0, 0.0, 0.05], [0.05, 0.05, 0.05], [-0.04, 0.03, 0.02]]      # 3D-TPS braucht ≥ 4 Punkte außerhalb einer Ebene
        von = torch.tensor([[0.0, 0.0, 0.0], [0.001, 0.0, 0.0]] + weit, dtype=torch.float64, device=G)
        nach = torch.tensor([[0.0, 0.01, 0.0], [0.0, -0.01, 0.0]] + weit, dtype=torch.float64, device=G)
        v, n = Gesichtsabbild.verschmelzen(von, nach, 0.002)
        self.assertEqual(len(v), 6)
        nah = int((v.norm(dim=1) < 0.002).nonzero()[0, 0])
        self.assertLess(float((v[nah] - torch.tensor([0.0005, 0.0, 0.0], dtype=torch.float64, device=G)).abs().max()), 1e-12)
        self.assertLess(float(n[nah].abs().max()), 1e-12)                # Ziele gemittelt: Mitte zwischen oben und unten
        self.assertLess(float((Gesichtsabbild.tps(v, n, 0.0)(v) - n).abs().max()), 1e-8)


class TestUmrissBild(unittest.TestCase):
    databases = []

    def test_innen(self):
        quadrat = torch.tensor([[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]], dtype=torch.float64, device=G)
        d = Gesichtsabbild.innen(torch.tensor([[5.0, 5.0], [15.0, 5.0], [5.0, 1.0]], dtype=torch.float64, device=G), quadrat)
        self.assertAlmostEqual(float(d[0]), 5.0, places=9)
        self.assertAlmostEqual(float(d[1]), -5.0, places=9)
        self.assertAlmostEqual(float(d[2]), 1.0, places=9)

    def test_bilinear(self):
        bild = torch.zeros((4, 8, 3), dtype=torch.uint8, device=G)
        bild[..., 0] = (torch.arange(8, device=G) * 30).to(torch.uint8)[None]
        c, drin = Gesichtsabbild.bilinear(bild, torch.tensor([[0.5, 1.5], [2.0, 2.5], [9.0, 1.0]], dtype=torch.float64, device=G))
        self.assertAlmostEqual(float(c[0, 0]) * 255, 0.0, places=3)
        self.assertAlmostEqual(float(c[1, 0]) * 255, 45.0, places=3)          # zwischen Pixel 1 (30) und 2 (60)
        self.assertEqual(drin.tolist(), [True, True, False])


class TestLab(unittest.TestCase):
    databases = []

    def test_umkehrung(self):
        torch.manual_seed(3)
        rgb = torch.rand((500, 3), dtype=torch.float64, device=G) * 255
        zurueck = Hautgrundhand.rgb_aus_lab(Kostuemhautfarbe.lab_aus_rgb(rgb))
        self.assertLess(float((zurueck - rgb).abs().max()), 0.05)


class TestBegriff(unittest.TestCase):
    databases = []

    def setUp(self):
        from KoerperKI_alle.npztorch import Npztorch
        from KoerperKI_alle.torchfeld import Torchfeld
        self.ablage = tempfile.TemporaryDirectory(dir=settings.TOOLS_ROOT / 'ProjektTemp')
        self.addCleanup(self.ablage.cleanup)
        ordner = Path(self.ablage.name)
        # 6 Flächen, Begriffe: staff (requisit), spear (requisit), robe (kleid), hat (kopf)
        stimmen = torch.tensor([[8, 2, 0, 0], [9, 1, 0, 0], [0, 0, 10, 3], [0, 0, 9, 9], [0, 0, 1, 0], [0, 0, 0, 0]], dtype=torch.float32, device=G)
        pixel = torch.tensor([10, 10, 10, 10, 10, 10], dtype=torch.float32, device=G)
        Npztorch.speichern(ordner / 'teile_flaechen.npz', stimmen=stimmen, pixel=pixel, begriffe=Torchfeld.feld(['staff', 'spear', 'robe', 'hat'], copy=True),
                           gruppen=Torchfeld.feld(['requisit', 'requisit', 'kleid', 'kopf'], copy=True))          # wie `_run_sam3teile`
        self.erk = SimpleNamespace(seg=ordner)

    def test_benennen(self):
        st = [{'id': 'r', 'art': 'requisit', 'flaechen_idx': torch.tensor([0, 1, 9], device=G)},          # 9: Flicken, zählt nicht
              {'id': 'o', 'art': 'oberteil', 'flaechen_idx': torch.tensor([2, 3], device=G)},
              {'id': 'w', 'art': 'oberteil', 'flaechen_idx': torch.tensor([4, 5], device=G)},
              {'id': 's', 'art': 'schuh', 'flaechen_idx': torch.tensor([0], device=G)}]
        Kostuembegriff.benennen(st, self.erk)
        self.assertEqual((st[0]['begriff'], st[0]['begriff_name']), ('staff', 'Stab'))
        self.assertAlmostEqual(st[0]['begriff_anteil'], 0.85, places=3)
        self.assertEqual((st[1]['begriff'], st[1]['begriff_name']), ('robe', 'Robe'))      # „hat“ deckt 60 %, ist aber keine Kleidung
        self.assertIsNone(st[2]['begriff'])                                               # 5 % < ANTEIL
        self.assertIsNone(st[3]['begriff'])                                               # Schuhe: keine Gruppe
        self.assertEqual(Kostuembegriff.felder(st[1]), {'begriff': 'robe', 'begriff_name': 'Robe', 'begriff_anteil': 0.95})


class TestMund(unittest.TestCase):
    databases = []

    @staticmethod
    def punkte(halb_innen):
        """478 Gesichtspunkte: äußere Lippenlinie Kreis r = 20 um (100, 100), innere Ellipse 10 × `halb_innen` (13 oben, 14 unten wie bei MediaPipe)."""
        import math
        p = torch.zeros((478, 2), dtype=torch.float64, device=G)
        for liste, rx, ry in ((Gesichtmund.AUSSEN, 20.0, 20.0), (Gesichtmund.INNEN, 10.0, halb_innen)):
            for k, i in enumerate(liste):
                w = math.pi - 2 * math.pi * k / len(liste)
                p[i] = torch.tensor([100 + rx * math.cos(w), 100 - ry * math.sin(w)], dtype=torch.float64, device=G)
        return p

    def test_offen_und_zu(self):
        px = torch.tensor([[100.0, 100.0], [100.0, 113.0], [113.0, 100.0], [200.0, 200.0]], dtype=torch.float64, device=G)     # Zahn, Lippe, Lippe, außen
        c = torch.tensor([[1.0, 1.0, 1.0], [0.6, 0.1, 0.1], [0.8, 0.1, 0.1], [0.0, 0.0, 1.0]], dtype=torch.float32, device=G)
        neu, bericht = Gesichtmund.lippen(px, self.punkte(5.0), 100.0, c)
        self.assertTrue(bericht['offen'])
        self.assertLess(float((neu[0] - torch.tensor([0.7, 0.1, 0.1], device=G)).abs().max()), 1e-6)        # Mittel der Lippe
        self.assertLess(float((neu[1:] - c[1:]).abs().max()), 1e-7)
        neu, bericht = Gesichtmund.lippen(px, self.punkte(0.0), 100.0, c)
        self.assertFalse(bericht['offen'])
        self.assertLess(float((neu - c).abs().max()), 1e-7)


class TestDeckkraft(unittest.TestCase):
    databases = []

    def test_nur_deckkraft(self):
        t = {'gruppen': [{'index_ab': 0, 'index_anzahl': 6, 'bilder': {'alpha': 'Runtime/Textures/x/MBtr.jpg', 'farbe': [0.2, 0.3, 0.4]}},
                         {'index_ab': 6, 'index_anzahl': 3, 'bilder': {'albedo': 'Runtime/Textures/x/a.jpg'}}],
             'toenung': torch.tensor([0.5, 1.0, 1.0], dtype=torch.float64, device=G)}
        aus = Kleiderbau._nur_deckkraft(t)
        self.assertEqual(len(aus), 1)
        self.assertEqual((aus[0]['ab'], aus[0]['anzahl'], aus[0]['albedo']), (0, 2, None))
        self.assertTrue(str(aus[0]['alpha']).replace('\\', '/').endswith('x/MBtr.jpg'))
        self.assertLess(float((aus[0]['faktor'] - torch.tensor([0.2, 0.6, 0.8], dtype=torch.float64, device=G)).abs().max()), 1e-12)
