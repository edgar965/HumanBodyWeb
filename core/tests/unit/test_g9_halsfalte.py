"""`G9halsfalte` auf Kunstdaten (05.11.2026, Edgar: „Kopf klebt nicht an hals“).
    1  ohne Überlappung bleibt die Haut dasselbe Objekt
    2  eine Falte: die Unterkante bekommt die Gewichte der Halshaut, die Eingabe bleibt unverändert
    3  über `RAND_M` hinaus ändert sich nichts
    4  die Summe der Gewichte bleibt 1, höchstens vier Einflüsse
    5  ohne `neck1` oder `head` bleibt die Haut, wie sie ist
    6  `punkte`: ohne Rinne dasselbe Objekt
    7  `punkte`: die Rinne ist danach zu, Kinn und Hals bleiben, die Eingabe bleibt unverändert
Sabotage (von Hand): in `haut` den Vergleich `oben > unten` umdrehen → Fall 1 und 2 rot; in `_mischen` `teil` durch 0 ersetzen → Fall 2 rot; `RAND_M` auf 1 m → Fall 3 rot;
in `_rinne` `t < RINNE_M` durch `t < 0` ersetzen → Fall 7 rot; `RINGE` auf 40 → Fall 7 rot (Kinn wandert).
"""
import unittest
from types import SimpleNamespace

import numpy as np
from Genesis9.halsfalte import G9halsfalte

KNOCHEN = [{'name': 'neck1', 'eltern': None, 'kopf': [0.0, 1.30, 0.0]}, {'name': 'neck2', 'eltern': 'neck1', 'kopf': [0.0, 1.38, 0.0]},
           {'name': 'head', 'eltern': 'neck2', 'kopf': [0.0, 1.46, 0.0]}, {'name': 'lowerjaw', 'eltern': 'head', 'kopf': [0.0, 1.47, 0.02]}]
NAMEN = ['neck1', 'neck2', 'head', 'lowerjaw']


def figur(unterkante):
    """Halsring bis y = 1,40 (Radius 4 cm, ganz an `neck2`), davor Kinnhaut von `unterkante` bis 1,46 (Radius 6 cm, ganz am Kiefer), alles rund um den Hals."""
    w = np.radians(np.arange(0, 360, 5))
    punkte, index, gewicht = [], [], []
    for y in np.arange(1.32, 1.401, 0.01):
        for a in w:
            punkte.append([0.04 * np.sin(a), y, 0.04 * np.cos(a)])
            index.append([1, 0, 0, 0])
            gewicht.append([1.0, 0.0, 0.0, 0.0])
    for y in np.arange(unterkante, 1.461, 0.005):
        for a in w:
            punkte.append([0.06 * np.sin(a), y, 0.06 * np.cos(a)])
            index.append([3, 0, 0, 0])
            gewicht.append([1.0, 0.0, 0.0, 0.0])
    return np.array(punkte), {'knochen': NAMEN, 'index': np.array(index, dtype=np.int32), 'gewicht': np.array(gewicht, dtype=np.float32)}


#: Profil (Radius, Höhe) vom Kinn über die Spitze der Falte und ihren Grat in den Hals; Punkte bis `SPITZE` am Kiefer, danach an `neck2`.
PROFIL = [(0.095, 1.45), (0.09, 1.44), (0.085, 1.43), (0.08, 1.42), (0.075, 1.41), (0.07, 1.40), (0.065, 1.39), (0.06, 1.40), (0.056, 1.41), (0.052, 1.42),
          (0.05, 1.41), (0.048, 1.40), (0.046, 1.39), (0.045, 1.38), (0.045, 1.37), (0.045, 1.36), (0.045, 1.35), (0.045, 1.34)]
SPITZE = 7


def falte(profil):
    """Ein Band aus `profil` um den Hals (vorn, ±60°) als Stufe 0: Dreiecke über dem Raster, keine Nahtkopien."""
    winkel = np.radians(np.arange(-60, 61, 10))
    zeilen, spalten = len(profil), len(winkel)
    punkte = np.array([[r * np.sin(a), y, r * np.cos(a)] for r, y in profil for a in winkel])
    nummer = lambda z, s: z * spalten + s
    dreiecke = []
    for z in range(zeilen - 1):
        for s in range(spalten - 1):
            dreiecke += [[nummer(z, s), nummer(z + 1, s), nummer(z, s + 1)], [nummer(z, s + 1), nummer(z + 1, s), nummer(z + 1, s + 1)]]
    index = np.array([[3 if z < SPITZE else 1, 0, 0, 0] for z in range(zeilen) for _s in range(spalten)], dtype=np.int32)
    gewicht = np.tile(np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32), (len(punkte), 1))
    haut = {'knochen': NAMEN, 'index': index, 'gewicht': gewicht}
    return punkte, SimpleNamespace(name='falte_%d' % zeilen, haut=haut, ursprung=np.arange(len(punkte)), dreiecke=np.array(dreiecke, dtype=np.int64))


class G9halsfalteFlaecheTest(unittest.TestCase):
    def test_ohne_rinne_dasselbe_objekt(self):
        p, stufe = falte([(r, y) for r, y in PROFIL[:SPITZE]] + [(0.045, 1.38), (0.045, 1.37), (0.045, 1.36), (0.045, 1.35), (0.045, 1.34)])
        self.assertIs(G9halsfalte.punkte(p, stufe, KNOCHEN), p)

    def test_rinne_geht_zu(self):
        p, stufe = falte(PROFIL)
        vorher = p.copy()
        neu = G9halsfalte.punkte(p, stufe, KNOCHEN)
        self.assertIsNot(neu, p)
        self.assertTrue(np.array_equal(p, vorher))
        spalten = 13
        mitte = neu[spalten // 2::spalten]
        self.assertLess(np.diff(mitte[:, 1]).max(), 0.002)                          # die Mittellinie fällt vom Kinn zum Hals, ohne wieder zu steigen
        self.assertTrue(np.allclose(neu[:spalten], p[:spalten]))                    # oberste Reihe: Kinn
        self.assertTrue(np.allclose(neu[-spalten:], p[-spalten:]))                  # unterste Reihe: Hals


class G9halsfalteTest(unittest.TestCase):
    def test_ohne_ueberlappung_dasselbe_objekt(self):
        p, haut = figur(1.41)
        self.assertIs(G9halsfalte.haut(p, haut, KNOCHEN), haut)

    def test_falte_nimmt_halsgewichte(self):
        p, haut = figur(1.37)
        vorher = haut['gewicht'].copy()
        neu = G9halsfalte.haut(p, haut, KNOCHEN)
        self.assertIsNot(neu, haut)
        unten = np.nonzero(np.isclose(p[:, 1], 1.37) & (np.hypot(p[:, 0], p[:, 2]) > 0.05))[0]
        self.assertTrue(len(unten))
        self.assertTrue((neu['index'][unten] != 3).all())          # kein Kiefer mehr an der Unterkante
        self.assertTrue(np.array_equal(haut['gewicht'], vorher))    # die Eingabe gehört allen Figuren

    def test_oben_unveraendert(self):
        p, haut = figur(1.37)
        neu = G9halsfalte.haut(p, haut, KNOCHEN)
        oben = p[:, 1] > 1.40 + G9halsfalte.RAND_M + 1e-6
        self.assertTrue(oben.any())
        self.assertTrue(np.array_equal(neu['index'][oben], haut['index'][oben]))
        self.assertTrue(np.array_equal(neu['gewicht'][oben], haut['gewicht'][oben]))

    def test_summe_eins(self):
        p, haut = figur(1.37)
        neu = G9halsfalte.haut(p, haut, KNOCHEN)
        self.assertEqual(neu['index'].shape, haut['index'].shape)
        self.assertTrue(np.allclose(neu['gewicht'].sum(1), 1.0, atol=1e-5))

    def test_ohne_halsknochen(self):
        p, haut = figur(1.37)
        self.assertIs(G9halsfalte.haut(p, haut, KNOCHEN[2:]), haut)


if __name__ == '__main__':
    unittest.main()
