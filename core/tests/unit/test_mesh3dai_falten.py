# -*- coding: utf-8 -*-
"""Falten in der Haut: Prüfung `Kostuemfalten` (Kanten, Knick) und Größe „glatt“ von „koerper“ (`Koerperangleichglatt`, Fassung 15) an Kunstnetzen, auf der CPU.

Kunstnetz: Gitter 7 × 7 Punkte im Abstand 1 cm (Ebene z = 0), je Zelle zwei Dreiecke; alle Punkte gehören zum Rumpf. Haltung vor „koerper“ (`x0`) = das flache Gitter; Grundfigur und Eingang
sind Kunstnetze desselben Gitters (Grundfigur über `_glatt_grundfigur`, Eingang über `e` mit den echten `Koerperangleichnetz._eingang_flaechen` und `_ziehen`).
    1  `kanten`: zwei Dreiecke mit gemeinsamer Kante → genau eine Innenkante zwischen Fläche 0 und 1
    2  Knick: flach → 0°, um 90° gefaltet → 90°
    3  „glatt“ ohne Verschiebung → 0; schräg gestellte Ebene (2 mm je cm) → 0 (kein Knick)
    4  „glatt“: Zeile 3 um 6 mm gehoben (Knick 31° und 62°, erlaubt 10°) → über 0; um 0,5 mm (Knick bis 5,7°) → 0
    5  dieselbe Falte in der Grundfigur → 0 (erlaubt ist der Knick der Grundfigur + 5°)
    6  dieselbe Falte im Eingang bis 12 mm → 0, alle Kanten „nah am Eingang“; der Eingang 5 cm weg → keine Kante nah, die Falte kostet
    7  „glatt“ zählt nur Kanten in `GLATT_GRUPPEN`: dieselbe Falte an Punkten der Gruppe 'hand' → 0, keine Kante
Gegenprobe am echten Lauf: `ProjektTemp/_wegwerf/regler_ki/falten_probe.py` (edgar Rumpf vorn 228 cm Falte vor Fassung 14, 4 cm nach Fassung 15), `glatt_probe.py` (Grundfigur 0).
Sabotage (von Hand): in `_glatt_vorbereiten` `k_grund` aus dem Maximum nehmen → Fall 5 rot; `k_e` herausnehmen → Fall 6 rot; in `_glatt` `- self.glatt_erlaubt` streichen → Fall 3 und 4
(0,5 mm) rot; `GLATT_GRUPPEN` um 'hand' erweitern → Fall 7 rot.
"""
import sys
import unittest

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))
sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))

N = 7
FALTE_M = 0.006


def gitter():
    x, y = np.meshgrid(np.arange(N) * 0.01, np.arange(N) * 0.01)
    p = np.stack([x.ravel(), y.ravel(), np.zeros(N * N)], 1)
    f = []
    for i in range(N - 1):
        for j in range(N - 1):
            a = i * N + j
            f += [[a, a + 1, a + N], [a + 1, a + N + 1, a + N]]
    return p, np.array(f, dtype=np.int64)


class Kunstquelle:
    s = 1.0

    def __init__(self, gruppe):
        self.kaefig_ruhe, self.dreiecke = gitter()
        self.knochen = np.zeros((N * N, 1), dtype=np.int64) + (0 if gruppe == 'rumpf' else 1)
        self.gewicht = np.ones((N * N, 1))


class Kunstglatt:
    """Gerade genug von `Koerperangleich` für `_glatt_vorbereiten` und `_glatt` (die Methoden aus den echten Klassen)."""

    @staticmethod
    def gefaltet(p, hub):
        """Zeile 3 des Gitters um `hub` Meter aus der Ebene gehoben — eine Falte quer über das Gitter."""
        g = p.clone()
        g[3 * N:4 * N, 2] += hub
        return g

    @staticmethod
    def bauen(gruppe='rumpf', grund_hub=0.0, eingang_hub=0.0, eingang_z=0.0):
        import types

        import torch

        from mesh3dai_koerperangleich_glatt import Koerperangleichglatt
        from mesh3dai_koerperangleich_netz import Koerperangleichnetz

        def grundfigur(self, wahl):
            return Kunstglatt.gefaltet(self.p_k, grund_hub)

        art = type('Kunstglattart', (Koerperangleichglatt,), {'GLATT_EINGANG_PUNKTE': 30000, '_glatt_grundfigur': grundfigur,
                                                               '_eingang_flaechen': Koerperangleichnetz._eingang_flaechen, '_ziehen': Koerperangleichnetz._ziehen})
        a = art()
        a.dev = torch.device('cpu')
        a.q = Kunstquelle(gruppe)
        a.gruppen = ['rumpf', 'hand']
        a.wahl_alle = np.arange(N * N)
        a.p_k = torch.as_tensor(a.q.kaefig_ruhe, dtype=torch.float32)
        a.x0 = a.p_k.clone()
        e = Kunstglatt.gefaltet(a.p_k, eingang_hub)
        e[:, 2] += eingang_z
        a.e = types.SimpleNamespace(punkte=e, dreiecke=torch.as_tensor(a.q.dreiecke))
        a._glatt_vorbereiten()
        return a


@unittest.skipUnless(__import__('importlib').util.find_spec('torch'), 'torch fehlt')
class FaltenTest(unittest.TestCase):
    databases = set()

    def test_kanten(self):
        import torch

        from mesh3dai_kostuem_falten import Kostuemfalten
        ka, kb, f1, f2 = Kostuemfalten.kanten(torch.tensor([[0, 1, 2], [1, 3, 2]]))
        self.assertEqual((ka.tolist(), kb.tolist()), ([1], [2]))
        self.assertEqual(sorted([int(f1[0]), int(f2[0])]), [0, 1])

    def test_knick(self):
        import torch

        from mesh3dai_kostuem_falten import Kostuemfalten
        flach = torch.tensor([[0.0, 0.0, 1.0]])
        self.assertAlmostEqual(float(Kostuemfalten.winkel(flach, flach)[0]), 0.0, places=3)
        self.assertAlmostEqual(float(Kostuemfalten.winkel(flach, torch.tensor([[1.0, 0.0, 0.0]]))[0]), 90.0, places=3)

    def test_glatt_ohne_und_schraeg(self):
        a = Kunstglatt.bauen()
        self.assertGreater(a.glatt_befund['kanten'], 0)
        self.assertEqual(float(a._glatt(a.p_k.clone())), 0.0)
        schief = a.p_k.clone()
        schief[:, 2] += 0.2 * schief[:, 0]                      # 2 mm je cm
        self.assertAlmostEqual(float(a._glatt(schief)), 0.0, places=6)

    def test_glatt_falte(self):
        a = Kunstglatt.bauen()
        self.assertGreater(float(a._glatt(Kunstglatt.gefaltet(a.p_k, FALTE_M))), 0.0)
        self.assertEqual(float(a._glatt(Kunstglatt.gefaltet(a.p_k, 0.0005))), 0.0)

    def test_glatt_falte_in_der_grundfigur(self):
        a = Kunstglatt.bauen(grund_hub=FALTE_M)
        self.assertEqual(float(a._glatt(Kunstglatt.gefaltet(a.p_k, FALTE_M))), 0.0)

    def test_glatt_falte_im_eingang(self):
        a = Kunstglatt.bauen(eingang_hub=FALTE_M)
        self.assertEqual(a.glatt_befund['eingang_nah'], a.glatt_befund['kanten'])
        self.assertEqual(float(a._glatt(Kunstglatt.gefaltet(a.p_k, FALTE_M))), 0.0)

    def test_glatt_eingang_fern(self):
        a = Kunstglatt.bauen(eingang_hub=FALTE_M, eingang_z=0.05)
        self.assertEqual(a.glatt_befund['eingang_nah'], 0)
        self.assertGreater(float(a._glatt(Kunstglatt.gefaltet(a.p_k, FALTE_M))), 0.0)

    def test_glatt_nur_gruppen(self):
        a = Kunstglatt.bauen('hand')
        self.assertEqual(a.glatt_befund['kanten'], 0)
        self.assertEqual(float(a._glatt(Kunstglatt.gefaltet(a.p_k, FALTE_M))), 0.0)


if __name__ == '__main__':
    unittest.main()
