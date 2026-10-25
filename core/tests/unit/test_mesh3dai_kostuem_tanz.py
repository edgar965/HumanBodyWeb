# -*- coding: utf-8 -*-
"""Kostüm-Prüfung „Haut durch Stück im Tanz“ (25.10.2026, `Kostuemtanz`, Prüfung Fassung 19) an Kunstdaten.

    1  Zylinder: Stückpunkt 5 cm vor der Haut → davor; 1 cm dahinter → dahinter, Tiefe 10 mm; 2 cm seitlich → weder noch; 20 cm dahinter → nicht dahinter (nur bis `HINTER_M`)
    2  Tiefe = NÄCHSTE Fläche dahinter (Vorder- und Rückseite eines Hosenbeins: 10 mm, nicht 80 mm)
    3  gemeinsame Knochen: gleiche Gewichte → 1, fremde Knochen → 0, halb/halb → 0,5
    4  „bedeckt“ verlangt gemeinsame Knochen: die Hose vor dem Arm bedeckt ihn nicht (edgar_knopf, Bild 690)
    5  Rot ab `ROT_MIN` Punkten in einem Bild, unabhängig vom Anteil (Robe des Zauberers: 62 Punkte = 0,97 %)
    6  nicht messbar (Figur fehlt) → rot mit Grund, keine Ausnahme
Die Gegenproben am echten Lauf (Haltung als Bild → 0, Haut +6 mm → rot) rechnet `ProjektTemp/_wegwerf/augen_ohren/tanz_pruefen.py`.
Sabotage (von Hand): in `zylinder` `amin` statt `amax` zurück → Fall 2 rot; `GEMEINSAM_MIN = 0` → Fall 4 rot; die alte Regel mit Anteil in `messen` → Fall 5 rot.
"""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


def _cuda():
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


@unittest.skipUnless(_cuda(), 'keine CUDA')
class KostuemtanzTest(unittest.TestCase):
    def setUp(self):
        from mesh3dai_kostuem_tanz import Kostuemtanz
        self.T = Kostuemtanz
        self.t = Kostuemtanz(None, None, [])
        self.torch = self.t.k.t

    def _p(self, x):
        return self.torch.as_tensor(np.asarray(x, dtype=np.float64), device='cuda')

    def test_1_zylinder(self):
        haut, n = self._p([[0, 0, 0]] * 4), self._p([[0, 0, 1]] * 4)
        davor, dahinter, tief = self.t.zylinder(haut[:1], n[:1], self._p([[0, 0, 0.05]]))
        self.assertTrue(bool(davor[0]))
        self.assertFalse(bool(dahinter[0]))
        davor, dahinter, tief = self.t.zylinder(haut[:1], n[:1], self._p([[0, 0, -0.01]]))
        self.assertFalse(bool(davor[0]))
        self.assertTrue(bool(dahinter[0]))
        self.assertAlmostEqual(float(tief[0]), 0.01, places=4)
        davor, dahinter, _ = self.t.zylinder(haut[:1], n[:1], self._p([[0.02, 0, 0.05]]))
        self.assertFalse(bool(davor[0]) or bool(dahinter[0]))
        _d, dahinter, _ = self.t.zylinder(haut[:1], n[:1], self._p([[0, 0, -0.20]]))
        self.assertFalse(bool(dahinter[0]))

    def test_2_naechste_flaeche(self):
        _d, dahinter, tief = self.t.zylinder(self._p([[0, 0, 0]]), self._p([[0, 0, 1]]), self._p([[0, 0, -0.01], [0, 0, -0.08]]))
        self.assertTrue(bool(dahinter[0]))
        self.assertAlmostEqual(float(tief[0]), 0.01, places=4)

    def test_3_gemeinsam(self):
        kn = np.array([[1, 2, 0, 0]])
        gw = np.array([[128, 127, 0, 0]], dtype=np.uint8)
        self.assertAlmostEqual(float(self.t.gemeinsam(kn, gw, kn, gw)[0]), 1.0, places=5)
        self.assertAlmostEqual(float(self.t.gemeinsam(kn, gw, np.array([[5, 6, 0, 0]]), gw)[0]), 0.0, places=5)
        halb = float(self.t.gemeinsam(np.array([[1, 0, 0, 0]]), np.array([[255, 0, 0, 0]], dtype=np.uint8), np.array([[1, 3, 0, 0]]), np.array([[128, 127, 0, 0]], dtype=np.uint8))[0])
        self.assertAlmostEqual(halb, 128 / 255, places=3)

    def test_4_bedeckt_nur_mit_gemeinsamen_knochen(self):
        p0, n0 = self._p([[0, 0, 0], [1, 0, 0]]), self._p([[0, 0, 1], [0, 0, 1]])
        idx = self.torch.arange(2, device='cuda')
        kn = np.array([[1, 0, 0, 0], [7, 0, 0, 0]])           # 1 = Becken, 7 = Arm
        gw = np.array([[255, 0, 0, 0], [255, 0, 0, 0]], dtype=np.uint8)
        hose = {'knochen': np.array([[1, 0, 0, 0], [1, 0, 0, 0]]), 'gewicht': np.array([[255, 0, 0, 0]] * 2, dtype=np.uint8)}
        q0 = self._p([[0, 0, 0.05], [1, 0, 0.05]])           # vor beiden Hautpunkten
        bedeckt = self.t.bedeckt(p0, n0, idx, kn, gw, hose, q0).cpu().numpy().tolist()
        self.assertEqual(bedeckt, [0])

    def test_5_rot_ab_punkten(self):
        befund = {'stuecke': {'robe': {'je_bild': [{'bild': 1, 'durch': 62, 'anteil': 0.0097, 'frei': 0, 'tiefster_mm': 5.0}]},
                              'schuh': {'je_bild': [{'bild': 1, 'durch': 9, 'anteil': 0.2, 'frei': 0, 'tiefster_mm': 5.0}]}}}
        for e in befund['stuecke'].values():               # dieselbe Regel wie am Ende von `messen`
            s = max(e['je_bild'], key=lambda x: (x['durch'], x['anteil']))
            e['rot'] = bool(s['durch'] >= self.T.ROT_MIN)
        self.assertTrue(befund['stuecke']['robe']['rot'])
        self.assertFalse(befund['stuecke']['schuh']['rot'])
        quelltext = (Path(settings.TOOLS_ROOT) / 'mesh3dai' / 'mesh3dai_kostuem_tanz.py').read_text(encoding='utf-8')
        self.assertIn("e['rot'] = bool(schlimm and schlimm['durch'] >= self.ROT_MIN)", quelltext)

    def test_6_nicht_messbar_ist_rot(self):
        z = {self.T.NAME: {'nachher': 0, 'pruefungen': 0, 'fehlertexte': [], 'geeicht': None}}
        messung = {}

        def zaehle(zeile, fehler, text):
            zeile['pruefungen'] += 1
            if fehler:
                zeile['nachher'] += 1
                zeile['fehlertexte'].append(text)
        quelle = SimpleNamespace(fig=Path(settings.TOOLS_ROOT) / 'ProjektTemp' / '_gibt_es_nicht_' / 'form_weiblich')
        self.T.pruefen(quelle.fig.parent, 'weiblich', quelle, [], z, zaehle, messung)
        self.assertEqual(z[self.T.NAME]['nachher'], 1)
        self.assertIn('nicht messbar', z[self.T.NAME]['fehlertexte'][0])
        self.assertIn('fehler', messung['tanz'])
