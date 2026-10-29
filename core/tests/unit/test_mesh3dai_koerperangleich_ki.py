# -*- coding: utf-8 -*-
"""Schritt „koerper“ von Mesh3D-AI, Größen „ki“ (Fassung 12, `Koerperangleichhaltung._haltung_ziele`/`_ki`) und „kopfhaut“ (Fassung 13, `Koerperangleichnetz._flaeche`) an Kunstdaten,
ohne Figur und ohne Karte (CPU-Tensoren).

    1  „ki“ zählt nur die Gelenke der Glieder: Rumpf und Kopf 50 mm neben den Zielen → 0; ein Knie 30 mm daneben → 30 mm / Zahl der Gliedgelenke
    2  „ki“ ohne Abweichung → 0
    3  „kopfhaut“: Kopfpunkt 10 mm hinter der Haut des Eingangs → (10 − Toleranz 3) mm; derselbe Abstand an einem Körperpunkt zählt nur in „haut“
    4  „kopfhaut“: Kopfpunkt, dessen nächster Flächenpunkt Haar ist → 0 (unter Haar zählt „kopfhaut“ nicht)
    5  „kopfhaut“ ohne Kopfpunkte → 0, kein NaN
Gegenprobe am echten Lauf: Kette edgar ab „figur“ 29.10.2026 (Kostüm-Prüfung `kostuem/lauf_2026.10.29.12.39.json`: Haltung 6,2 mm, Oberschenkel 416 / KI 416 mm, Form des Kopfes 22 cm²).
Sabotage (von Hand): `KI_GRUPPEN` um 'rumpf' erweitern → Fall 1 rot; in `_flaeche` `self.kopfhaut_i` durch alle Punkte ersetzen → Fall 3 (Körperpunkt) rot.
"""
import sys
import unittest

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


class Kunstangleich:
    """Gerade genug von `Koerperangleich` für `_haltung_ziele`, `_ki` und `_flaeche` (die Methoden kommen aus den echten Klassen)."""

    @staticmethod
    def bauen():
        import torch

        from mesh3dai_koerperangleich import Koerperangleich
        a = object.__new__(Koerperangleich)
        a.dev = torch.device('cpu')
        a.namen = ['hip', 'spine1', 'neck1', 'head', 'l_thigh', 'l_shin', 'l_foot', 'l_upperarm', 'l_hand']
        a.gruppen = ['rumpf', 'rumpf', 'kopf', 'kopf', 'bein', 'bein', 'fuss', 'arm', 'hand']
        rig = np.arange(len(a.namen) * 3, dtype=np.float32).reshape(-1, 3) / 10
        a.erg = {'rig': rig, 'stimmen': np.concatenate([rig, np.zeros((4, 3), dtype=np.float32)])}
        a._haltung_ziele()
        return a, torch.as_tensor(rig)

    @staticmethod
    def flaeche(punkte, ist_kopf, eingang_haut):
        """Eingang = Ebene z = 0 mit Normale +z aus 3 Punkten weit auseinander; `eingang_haut` je Flächenpunkt; Körperpunkte `punkte` (N, 3)."""
        import torch

        from mesh3dai_koerperangleich import Koerperangleich
        a = object.__new__(Koerperangleich)
        a.dev = torch.device('cpu')
        a.innen_p = torch.tensor([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        a.innen_n = torch.tensor([[0.0, 0.0, 1.0]] * 3)
        a.innen_haut = torch.tensor(eingang_haut)
        a.kopfhaut_i = torch.as_tensor(np.nonzero(ist_kopf)[0])
        return Koerperangleich._flaeche(a, torch.tensor(punkte, dtype=torch.float32))


@unittest.skipUnless(__import__('importlib').util.find_spec('torch'), 'torch fehlt')
class KoerperangleichKiTest(unittest.TestCase):
    databases = set()

    def test_ki_nur_glieder(self):
        a, p = Kunstangleich.bauen()
        q = p.clone()
        q[[0, 1, 2, 3]] += 0.05                                   # Rumpf und Kopf 50 mm daneben
        self.assertAlmostEqual(float(a._ki(q)), 0.0, places=6)
        q[a.namen.index('l_shin'), 0] += 0.03                     # Knie 30 mm daneben
        self.assertAlmostEqual(float(a._ki(q)), 0.03 / 5, places=6)

    def test_ki_ohne_abweichung(self):
        a, p = Kunstangleich.bauen()
        self.assertAlmostEqual(float(a._ki(p)), 0.0, places=6)

    def test_kopfhaut_hinter_der_haut(self):
        _innen, haut, kopf = Kunstangleich.flaeche([[0.1, 0.1, -0.010], [0.2, 0.1, -0.010]], np.array([True, False]), [True, True, True])
        self.assertAlmostEqual(float(kopf), 0.007, places=5)
        self.assertAlmostEqual(float(haut), 0.007, places=5)      # beide Punkte im Mittel über alle

    def test_kopfhaut_unter_haar_zaehlt_nicht(self):
        _innen, _haut, kopf = Kunstangleich.flaeche([[0.1, 0.1, -0.010]], np.array([True]), [False, False, False])
        self.assertAlmostEqual(float(kopf), 0.0, places=6)

    def test_kopfhaut_ohne_kopfpunkte(self):
        _innen, _haut, kopf = Kunstangleich.flaeche([[0.1, 0.1, -0.010]], np.array([False]), [True, True, True])
        self.assertEqual(float(kopf), 0.0)


if __name__ == '__main__':
    unittest.main()
