"""`Figurbodenstand` auf einer Kunstfigur (05.11.2026, Edgar: „beim Video geht die Person durch den Fussboden mit beiden Schuhen“).
    1  `tiefste` rechnet wie die volle Häutung (`Linearhaut`)
    2  `richten`: nachher liegt der tiefste Punkt in jedem Bild auf 0, hoch und runter
    3  Körper und Schuhe zählen, die Hose nicht
    4  ohne Wurzelspur bleibt die Bewegung, wie sie ist
Sabotage (von Hand): in `richten` das Vorzeichen von `versatz` umdrehen → Fall 2 rot; `SCHUH` leeren → Fall 3 rot.
"""
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np
from Figurfilm.figurbodenstand import Figurbodenstand
from Figurfilm.knochenlage import Knochenlage
from Figurfilm.linearhaut import Linearhaut


class Lage(SimpleNamespace):
    """Zwei Gelenke: `hip` (Wurzel) und `foot` darunter, die `Knochenlage`-Rechnung selbst."""
    welt = Knochenlage.welt
    _welt = Knochenlage._welt
    ruhe = Knochenlage.ruhe
    matrizen = staticmethod(Knochenlage.matrizen)


def lage():
    return Lage(gelenke=[0, 1], namen=['hip', 'foot'], nummer={'hip': 0, 'foot': 1}, eltern=[-1, 0], reihenfolge=[0, 1],
                verschiebung=np.array([[0.0, 1.0, 0.0], [0.0, -1.0, 0.0]]), drehung=np.array([[0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 1.0]]),
                bindung=np.stack([np.eye(4), np.eye(4)]))


def figur(netze):
    """`netze`: [(Name, Punkte (N, 3), Gelenk)] → `Figurbodenstand` ohne GLB."""
    f = Figurbodenstand.__new__(Figurbodenstand)
    f.lage = lage()
    gelesen = [(n, np.asarray(p, dtype=np.float64), g) for n, p, g in netze]
    eintraege = [{'name': n, 'haut': True} for n, _p, _g in gelesen]
    daten = {n: {'punkte': p, 'gelenke': np.full((len(p), 4), g), 'gewichte': np.tile([1.0, 0.0, 0.0, 0.0], (len(p), 1))} for n, p, g in gelesen}
    objekte = SimpleNamespace(eintraege=lambda: eintraege, laden=lambda e: daten[e['name']])
    f.glb = None
    with mock.patch('Figurfilm.figurbodenstand.Netzobjekte', lambda _glb: objekte):
        f.namen, f.punkte, f.gelenke, f.gewichte = f._netze()
    return f


def bewegung(hoehen):
    werte = np.zeros((len(hoehen), 3))
    werte[:, 1] = hoehen
    return {'frame_count': len(hoehen), 'tracks': {}, 'position_track': {'bone': 'hip', 'values': werte.reshape(-1).tolist()}}


class FigurbodenstandTest(unittest.TestCase):
    NETZ = [('koerper__koerper__0_k1003', [[0.0, 0.0, 0.0], [0.1, 0.2, 0.0]], 1), ('kleidung__ki_schuh_1', [[0.0, -0.05, 0.0]], 1), ('kleidung__ki_hose', [[0.0, -0.5, 0.0]], 1)]

    def test_tiefste_wie_volle_haeutung(self):
        f = figur(self.NETZ[:2])
        welt = f.lage.welt(bewegung([1.0, 0.8]))
        voll = Linearhaut(f.punkte[:, :3], f.gelenke, f.gewichte, f.lage.bindung)
        self.assertTrue(np.allclose(f.tiefste(welt), [voll.bild(w)[:, 1].min() for w in welt]))

    def test_richten_hoch_und_runter(self):
        f = figur(self.NETZ[:2])
        b = bewegung([0.8, 1.0, 1.3])
        versatz = f.richten(b)
        self.assertTrue(np.allclose(f.tiefste(f.lage.welt(b)), 0.0))
        self.assertGreater(versatz[0], 0.0)
        self.assertLess(versatz[2], 0.0)

    def test_nur_koerper_und_schuhe(self):
        f = figur(self.NETZ)
        self.assertEqual(f.namen, ['koerper__koerper__0_k1003', 'kleidung__ki_schuh_1'])

    def test_ohne_wurzelspur(self):
        f = figur(self.NETZ[:2])
        b = {'frame_count': 2, 'tracks': {}}
        self.assertIsNone(f.richten(b))
        self.assertNotIn('position_track', b)


if __name__ == '__main__':
    unittest.main()
