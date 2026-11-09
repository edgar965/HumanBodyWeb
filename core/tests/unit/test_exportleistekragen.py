"""`Exportleistekragen` auf Kunstdaten (06.11.2026, Edgar zu Edgar2010: ausgefranstes Loch am Kragen).
    1  ein Kragenrand mit Spalt liegt danach an der Haut, der Stoff weit unter dem Rand bleibt
    2  ein weiter Ausschnitt (über `WEIT_M`) bleibt, wie er ist
    3  ein Stück, das nicht deckt, bleibt
    4  ohne `neck1` kein Eingriff
Sabotage (von Hand): `LUFT_M` auf 0,05 → Fall 1 rot; `WEIT_M` auf 1 m → Fall 2 rot; in `anlegen` die Abfrage `s['deckt']` entfernen → Fall 3 rot.
"""
import numpy as np
from django.test import SimpleTestCase

from core.dienste.exportleistekragen import Exportleistekragen

KNOCHEN = [{'name': 'neck1', 'eltern': None, 'kopf': [0.0, 1.40, 0.0]}, {'name': 'head', 'eltern': 'neck1', 'kopf': [0.0, 1.50, 0.0]}]


def netz():
    """Hals als Zylinder (Radius 5 cm, y 1,30 bis 1,55), Normalen waagerecht nach außen."""
    punkte, normalen = [], []
    for y in np.arange(1.30, 1.551, 0.01):
        for a in np.radians(np.arange(0, 360, 10)):
            n = [np.sin(a), 0.0, np.cos(a)]
            punkte.append([0.05 * n[0], y, 0.05 * n[2]])
            normalen.append(n)
    return {'punkte': np.array(punkte), 'normalen': np.array(normalen), 'skelett': {'knochen': KNOCHEN}}


def rohr(spalt, deckt=True):
    """Stoff als Rohr um den Hals, Radius 5 cm + `spalt`, von y 1,10 bis zum offenen Rand bei 1,42."""
    hoehen, winkel = np.arange(1.10, 1.421, 0.01), np.radians(np.arange(0, 360, 10))
    punkte = np.array([[(0.05 + spalt) * np.sin(a), y, (0.05 + spalt) * np.cos(a)] for y in hoehen for a in winkel])
    z, s = len(hoehen), len(winkel)
    dreiecke = []
    for i in range(z - 1):
        for j in range(s):
            a, b, c, d = i * s + j, i * s + (j + 1) % s, (i + 1) * s + j, (i + 1) * s + (j + 1) % s
            dreiecke += [[a, c, b], [b, c, d]]
    return {'name': 'stueck', 'punkte': punkte, 'dreiecke': np.array(dreiecke, dtype=np.int64), 'deckt': deckt}


class ExportleistekragenTest(SimpleTestCase):
    @staticmethod
    def _radius(punkte):
        return np.hypot(punkte[:, 0], punkte[:, 2])

    def test_rand_liegt_an(self):
        s = rohr(0.015)
        vorher = s['punkte'].copy()
        bericht = Exportleistekragen.anlegen([s], netz())
        self.assertIn('stueck', bericht)
        rand = s['punkte'][:, 1] > 1.415
        self.assertLess(np.abs(self._radius(s['punkte'][rand]) - 0.05 - Exportleistekragen.LUFT_M).max(), 0.001)
        unten = vorher[:, 1] < 1.30
        self.assertTrue(np.array_equal(s['punkte'][unten], vorher[unten]))

    def test_weiter_ausschnitt_bleibt(self):
        s = rohr(Exportleistekragen.WEIT_M + 0.01)
        vorher = s['punkte'].copy()
        self.assertEqual(Exportleistekragen.anlegen([s], netz()), {})
        self.assertTrue(np.array_equal(s['punkte'], vorher))

    def test_nicht_deckend_bleibt(self):
        s = rohr(0.015, deckt=False)
        vorher = s['punkte'].copy()
        self.assertEqual(Exportleistekragen.anlegen([s], netz()), {})
        self.assertTrue(np.array_equal(s['punkte'], vorher))

    def test_ohne_hals(self):
        n = netz()
        n['skelett'] = {'knochen': KNOCHEN[1:]}
        self.assertEqual(Exportleistekragen.anlegen([rohr(0.015)], n), {})
