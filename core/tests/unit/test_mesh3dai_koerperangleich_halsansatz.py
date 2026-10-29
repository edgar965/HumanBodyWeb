# -*- coding: utf-8 -*-
"""Größe „halsansatz“ von „koerper“ (`Koerperangleichhalsansatz`, Fassung 16) an einem Kunstnetz, auf der CPU.

Kunstfigur: Schulterleiste aus Käfigpunkten x −0,20 … 0,20 m (5 mm), z −0,05 … 0,05 m, oben y = 1,40 m, darunter eine zweite Lage bei 1,35 m (Knochen spine4, Rumpf); Kopfpunkte (head) bei
y 1,55–1,60 m, Ohrgelenke bei 1,57 m; Oberarmgelenke bei x ±0,18 m, y 1,36 m. Eingang: eine Ebene aus kleinen Dreiecken in Höhe `hoehe`, Art je Fläche Haut (oder Kleid).
    1  Eingang 1 cm über der Figur → je Seite 15 Spalten (40 … 180 mm), jede 10 mm − 3 mm Toleranz → 7 mm (RMS gleicher Werte)
    2  Eingang 2 mm über der Figur (unter `HALS_TOL_M`) → 0
    3  Eingang kein Haut (Kleid) → keine Spalte, 0
    4  Oberkante des Eingangs 5 mm unter den Ohren (Hals) → keine Spalte
    5  die obere Lage links nicht in `wahl_alle` (stellt „koerper“ nicht) → nur die 15 Spalten rechts
    6  Kopfpunkte in `wahl_alle` (wie die Tabellenpunkte am echten Lauf) zählen nicht als Oberkante → wie Fall 1
    7  Gradient: nur die oberste Lage bekommt einen, nach oben (negativ), und nur in y
Gegenprobe am echten Lauf: `ProjektTemp/_wegwerf/regler_ki/halsansatz_koerper_probe.py` (Oberkante auf das Ziel gesetzt → 0).
Sabotage (von Hand): `.abs()` in `_halsansatz` streichen → Fall 1 negativ, rot; die Prüfung auf Haut in `_halsansatz_spalte` streichen → Fall 3 rot; `HALS_KOPF_ABSTAND_M` auf 0 → Fall 4
rot; die Prüfung „Hals der Figur“ streichen → Fall 5 rot.
"""
import sys
import unittest

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))
sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))

NAMEN = ['spine4', 'head', 'l_upperarm', 'r_upperarm', 'l_ear', 'r_ear']
GRUPPEN = ['rumpf', 'kopf', 'arm', 'arm', 'gesicht', 'gesicht']


class Kunstquelle:
    s = 1.0

    def __init__(self):
        xs, zs = np.arange(-0.20, 0.2001, 0.005), np.arange(-0.05, 0.0501, 0.01)
        x, z = np.meshgrid(xs, zs)
        lage_oben = np.stack([x.ravel(), np.full(x.size, 1.40), z.ravel()], 1)
        lage_unten = lage_oben + [0.0, -0.05, 0.0]
        kopf = np.array([[dx, y, 0.0] for dx in (-0.04, 0.0, 0.04) for y in (1.55, 1.57, 1.60)])
        self.kaefig_haltung = np.concatenate([lage_oben, lage_unten, kopf])
        self.oben = np.arange(len(lage_oben))
        self.knochen = np.zeros((len(self.kaefig_haltung), 1), dtype=np.int64)
        self.knochen[-len(kopf):] = 1
        self.gewicht = np.ones((len(self.kaefig_haltung), 1))
        self.lage = np.array([[0.0, 1.40, 0.0], [0.0, 1.55, 0.0], [0.18, 1.36, 0.0], [-0.18, 1.36, 0.0], [0.07, 1.57, 0.0], [-0.07, 1.57, 0.0]])


class Kunsthalsansatz:
    """Gerade genug von `Koerperangleich` für `_halsansatz_vorbereiten` und `_halsansatz` (die Methoden aus den echten Klassen)."""

    @staticmethod
    def ebene(hoehe):
        """Ebene x −0,22 … 0,22, z −0,06 … 0,06 in Höhe `hoehe` aus Dreiecken von 1 cm → (Punkte, Dreiecke)."""
        xs, zs = np.arange(-0.22, 0.2201, 0.01), np.arange(-0.06, 0.0601, 0.01)
        nx, nz = len(xs), len(zs)
        x, z = np.meshgrid(xs, zs)
        p = np.stack([x.ravel(), np.full(x.size, hoehe), z.ravel()], 1)
        f = []
        for i in range(nz - 1):
            for j in range(nx - 1):
                a = i * nx + j
                f += [[a, a + nx, a + 1], [a + 1, a + nx, a + nx + 1]]
        return p, np.array(f, dtype=np.int64)

    @staticmethod
    def bauen(hoehe=1.41, art='haut', links_frei=False, kopf_in_wahl=False):
        import types

        import torch

        from mesh3dai_koerperangleich_halsansatz import Koerperangleichhalsansatz
        from mesh3dai_koerperangleich_netz import Koerperangleichnetz
        from mesh3dai_kostuemarten import Kostuemarten
        klasse = type('Kunsthalsansatzart', (Koerperangleichhalsansatz,), {'HALS_EINGANG_PUNKTE': 20000, '_eingang_flaechen': Koerperangleichnetz._eingang_flaechen,
                                                                           '_ziehen': Koerperangleichnetz._ziehen})
        a = klasse()
        a.dev = torch.device('cpu')
        a.q = q = Kunstquelle()
        a.namen, a.gruppen = NAMEN, GRUPPEN
        wahl = np.arange(len(q.kaefig_haltung)) if kopf_in_wahl else np.flatnonzero(q.knochen[:, 0] == 0)
        if links_frei:
            wahl = wahl[~np.isin(wahl, q.oben[q.kaefig_haltung[q.oben, 0] > 0])]
        a.wahl_alle = wahl
        a.x0 = torch.as_tensor(q.kaefig_haltung[wahl], dtype=torch.float32)
        p, f = Kunsthalsansatz.ebene(hoehe)
        a.e = types.SimpleNamespace(punkte=torch.as_tensor(p, dtype=torch.float32), dreiecke=torch.as_tensor(f))
        a._halsansatz_vorbereiten(np.full(len(f), Kostuemarten.nummer(art), dtype=np.int64))
        return a


@unittest.skipUnless(__import__('importlib').util.find_spec('torch'), 'torch fehlt')
class HalsansatzTest(unittest.TestCase):
    databases = set()

    def test_eingang_hoeher(self):
        a = Kunsthalsansatz.bauen(1.41)
        self.assertEqual(a.halsansatz_befund['spalten'], 30)
        self.assertAlmostEqual(float(a._halsansatz(a.x0)), 0.007, places=4)

    def test_unter_toleranz(self):
        a = Kunsthalsansatz.bauen(1.402)
        self.assertEqual(float(a._halsansatz(a.x0)), 0.0)

    def test_keine_haut(self):
        a = Kunsthalsansatz.bauen(1.41, art='kleid')
        self.assertEqual(a.halsansatz_befund['spalten'], 0)
        self.assertEqual(float(a._halsansatz(a.x0)), 0.0)

    def test_hals(self):
        a = Kunsthalsansatz.bauen(1.565)
        self.assertEqual(a.halsansatz_befund['spalten'], 0)

    def test_nicht_gestellt(self):
        a = Kunsthalsansatz.bauen(1.41, links_frei=True)
        self.assertEqual(a.halsansatz_befund['spalten'], 15)
        self.assertTrue(all(v == 'Hals der Figur' for v in a.halsansatz_befund['profil_mm']['links'].values()))

    def test_kopf_in_wahl(self):
        a = Kunsthalsansatz.bauen(1.41, kopf_in_wahl=True)
        self.assertEqual(a.halsansatz_befund['spalten'], 30)
        self.assertAlmostEqual(float(a._halsansatz(a.x0)), 0.007, places=4)

    def test_gradient(self):
        a = Kunsthalsansatz.bauen(1.41)
        x = a.x0.clone().requires_grad_(True)
        a._halsansatz(x).backward()
        g = x.grad
        oben = x.detach()[:, 1] > 1.39
        self.assertTrue(bool((g[oben, 1] <= 0).all()) and bool((g[oben, 1] < 0).any()))
        self.assertEqual(float(g[~oben].abs().sum()), 0.0)
        self.assertEqual(float(g[:, [0, 2]].abs().sum()), 0.0)


if __name__ == '__main__':
    unittest.main()
