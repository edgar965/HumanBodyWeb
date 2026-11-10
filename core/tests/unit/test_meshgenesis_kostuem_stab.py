# -*- coding: utf-8 -*-
"""Stab im Eingang (`Kostuemstab`, Erkennung Fassung 10) und Kostüm-Prüfung „Stab ganz erkannt“ (`Kostuemstabganz`) an einer Kunströhre, auf der CPU.

Anlass (Edgar, 08.11.2026, Zauberer: „zauberer stock hast fehlende teile“): SAM deckte den mittleren Stab vor der Robe nicht, Sapiens nannte ihn Oberteil — er wurde mit der Robe geschnitten.

Kunstnetz: Röhre längs y, Halbmesser 1,5 cm, 1,2 m lang, 24 Segmente × 60 Ringe. Requisit unten (0–0,3 m) und oben (0,7–1,2 m), dazwischen Oberteil; in der Mitte ein Band Haut der rechten
Hand (Griff). Zusagen:
    1  Zwei Requisit-Inseln auf einer Achse sind EIN Stab, Halbmesser ≈ 1,5 cm, Achse längs y, Länge ≈ 1,2 m.
    2  `fortsetzen` macht alle Oberteil-Flächen des Mantels zu Requisit, die Haut der Hand bleibt Haut (Griff).
    3  Eine dicke Röhre (Halbmesser 10 cm, dicker als `STAB_DICKE_M`) ist kein Stab.
    4  „Stab ganz erkannt“: vorher 0,4 m minus Griff als andere Art (rot), nach `fortsetzen` 0 m fremd (grün), der Griff zählt nie als fremd.
Sabotage gefahren 09.11.2026 (`ProjektTemp/_wegwerf/mehrfoto/stab_test_sabotage.py`, per mock): Griff nicht aus dem Mantel genommen → Fall 2 rot; `stabpaare` leer → Fall 1 rot.
"""
import sys
import unittest

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))
sys.path.insert(0, str(settings.TOOLS_ROOT / 'meshgenesis'))


def roehre(halbmesser=0.015, laenge=1.2, segmente=24, ringe=60):
    """(punkte, dreiecke, Höhe je Fläche) einer offenen Röhre längs y, Fläche nach außen."""
    y = np.linspace(0.0, laenge, ringe + 1)
    w = np.linspace(0.0, 2 * np.pi, segmente, endpoint=False)
    p = np.stack([np.repeat(np.cos(w)[None], len(y), 0) * halbmesser, np.repeat(y[:, None], segmente, 1), np.repeat(np.sin(w)[None], len(y), 0) * halbmesser], -1).reshape(-1, 3)
    f = []
    for r in range(ringe):
        for s in range(segmente):
            a, b, c, d = r * segmente + s, r * segmente + (s + 1) % segmente, (r + 1) * segmente + s, (r + 1) * segmente + (s + 1) % segmente
            f += [[a, c, b], [b, c, d]]
    f = np.asarray(f, dtype=np.int64)
    return p, f, p[f].mean(1)[:, 1]


def arten(hoehe):
    """Art und Sapiens-Klasse je Fläche: Requisit außen, Oberteil in der Mitte, Haut der rechten Hand bei 0,48–0,52 m."""
    from meshgenesis_kostuemarten import Kostuemarten
    from Sapiens2Torch.segmentierung import S2segmentierung
    art = np.full(len(hoehe), Kostuemarten.nummer('requisit'), dtype=np.int64)
    mitte = (hoehe > 0.3) & (hoehe < 0.7)
    art[mitte] = Kostuemarten.nummer('oberteil')
    hand = (hoehe > 0.48) & (hoehe < 0.52)
    art[hand] = Kostuemarten.nummer('haut')
    klasse = np.full(len(hoehe), S2segmentierung.NAMEN.index('Upper_Clothing'), dtype=np.int64)
    klasse[hand] = S2segmentierung.NAMEN.index('Right_Hand')
    return art, klasse, mitte & ~hand, hand


@unittest.skipUnless(__import__('importlib').util.find_spec('torch'), 'torch fehlt')
class KostuemstabTest(unittest.TestCase):
    databases = set()

    def setUp(self):
        import torch
        from meshgenesis_kostuemgpu import Kostuemgpu
        self.vorher = Kostuemgpu._ich
        k = Kostuemgpu.__new__(Kostuemgpu)
        k.t, k.g = torch, torch.device('cpu')            # die Rechnung ist reines torch: im Test auf der CPU, die Karte bleibt der Kette
        Kostuemgpu._ich = k

    def tearDown(self):
        from meshgenesis_kostuemgpu import Kostuemgpu
        Kostuemgpu._ich = self.vorher

    def test_1_zwei_requisit_inseln_auf_einer_achse_sind_ein_stab(self):
        from meshgenesis_kostuem_stab import Kostuemstab
        p, f, h = roehre()
        art, _klasse, _mitte, _hand = arten(h)
        staebe = Kostuemstab(p, f).staebe(art)
        self.assertEqual(len(staebe), 1, 'unten und oben sind derselbe Stab')
        s = staebe[0]
        self.assertAlmostEqual(s['r'], 0.015, delta=0.002)
        self.assertGreater(abs(float(s['a'][1])), 0.99, 'Achse längs y')
        self.assertAlmostEqual(s['hi'] - s['lo'], 1.2, delta=0.05)

    def test_2_fortsetzen_macht_den_mantel_zu_requisit_ausser_dem_griff(self):
        from meshgenesis_kostuem_stab import Kostuemstab
        from meshgenesis_kostuemarten import Kostuemarten
        p, f, h = roehre()
        art, klasse, mitte, hand = arten(h)
        neu, zahl = Kostuemstab(p, f).fortsetzen(art, klasse)
        neu = neu.cpu().numpy()
        self.assertEqual(zahl, int(mitte.sum()))
        self.assertTrue((neu[mitte] == Kostuemarten.nummer('requisit')).all())
        self.assertTrue((neu[hand] == Kostuemarten.nummer('haut')).all(), 'die Faust bleibt Haut')

    def test_3_eine_dicke_roehre_ist_kein_stab(self):
        from meshgenesis_kostuem_stab import Kostuemstab
        p, f, h = roehre(halbmesser=0.10)
        art, _klasse, _mitte, _hand = arten(h)
        self.assertEqual(Kostuemstab(p, f).staebe(art), [])

    def test_4_stab_ganz_erkannt_vorher_rot_nachher_gruen(self):
        from types import SimpleNamespace

        from meshgenesis_kostuem_stab import Kostuemstab
        from meshgenesis_kostuem_stabganz import Kostuemstabganz
        p, f, h = roehre()
        art, klasse, _mitte, _hand = arten(h)
        pruefung = Kostuemstabganz(SimpleNamespace(punkte=p, dreiecke=f), SimpleNamespace(s=1.0))
        vorher = pruefung.messen(None, art, klasse)['staebe']
        self.assertEqual(len(vorher), 1)
        self.assertGreater(vorher[0]['fremd_m'], Kostuemstabganz.FREMD_MAX_M)
        self.assertAlmostEqual(vorher[0]['fremd_m'], 0.36, delta=0.08, msg='0,4 m Oberteil minus 4 cm Griff')
        self.assertGreater(vorher[0]['griff_m'], 0.0)
        neu, _zahl = Kostuemstab(p, f).fortsetzen(art, klasse)
        nachher = pruefung.messen(None, neu.cpu().numpy(), klasse)['staebe']
        self.assertEqual(nachher[0]['fremd_m'], 0.0)
        self.assertGreater(nachher[0]['griff_m'], 0.0, 'der Griff bleibt Griff, nicht fremd')


if __name__ == '__main__':
    unittest.main()
