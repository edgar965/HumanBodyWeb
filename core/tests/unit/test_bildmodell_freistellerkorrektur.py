# -*- coding: utf-8 -*-
"""Freisteller-Korrektur (21.09.2026): Striche, Weiß-Key, GrabCut, Reglerprüfung — und die
Gesichtsverzerrung des Texturlaufs (TPS). Kunstbilder, Millisekunden, kein Netz.

WARUM (Edgar: „mehr automatische, halbautomatischen und manuelle Möglichkeiten zur
Korrektur"; „so dass sich die Formen genau mit dem Bild überlagern"):

1. `striche`: ein `drin`-Strich setzt die Maske auf 1, `draussen` auf 0 — auch über einer
   Netzmaske, die anders entschieden hat; die Breite ist ein Anteil der Bildbreite.
2. `weisskey`: ein grauer Kreis auf Weiß wird zur Person, ein weißes Loch IM Kreis bleibt
   Person (nur der mit dem Rand verbundene Grund ist Hintergrund).
3. `grabcut`: legt eine zu grobe Maske (Quadrat) an die Kante des Kreises — IoU steigt.
4. `regler_pruefen` in `Bildmodellfreisteller`: unbekanntes Modell → Vorgabe, Striche ohne
   Punkte fallen weg, Punkte außerhalb 0..1 fallen weg.
5. `Gesichtsverzerrung`: Kontrollpunkte landen (bis auf die Glättung) auf den Zielpunkten,
   weit weg bleibt die Identität, ohne Verschiebung überall Identität.

Sabotage-Gegenprobe: in `striche` die Zeile `aus[draussen] = 0.0` weg → Fall 1 rot.
"""

import unittest

import numpy as np

from core.dienste.bildmodellfreisteller import Bildmodellfreisteller
from core.dienste.bildmodellfreistellerkorrektur import Bildmodellfreistellerkorrektur as K

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from gesichtsverzerrung import Gesichtsverzerrung  # noqa: E402


def _kreisbild(n=160, r=50, loch=False):
    yy, xx = np.mgrid[:n, :n]
    kreis = (xx - n // 2) ** 2 + (yy - n // 2) ** 2 <= r * r
    rgb = np.full((n, n, 3), 255, dtype=np.uint8)
    rgb[kreis] = (120, 90, 70)
    if loch:
        rgb[(xx - n // 2) ** 2 + (yy - n // 2) ** 2 <= 10 * 10] = 255
    return rgb, kreis


class DieKorrektur(unittest.TestCase):

    def test_1_striche_setzen_und_loeschen(self):
        alpha = np.full((100, 200), 0.5, dtype=np.float32)
        striche = [{'art': 'drin', 'breite': 0.05, 'punkte': [[0.1, 0.5], [0.4, 0.5]]},
                   {'art': 'draussen', 'breite': 0.05, 'punkte': [[0.6, 0.5], [0.9, 0.5]]}]
        aus = K.striche(alpha, striche)
        self.assertEqual(float(aus[50, 50]), 1.0)
        self.assertEqual(float(aus[50, 150]), 0.0)
        self.assertEqual(float(aus[10, 100]), 0.5)      # unberührt
        self.assertIs(K.striche(alpha, []), alpha)

    def test_2_weisskey_mit_loch(self):
        rgb, kreis = _kreisbild(loch=True)
        maske = K.weisskey(rgb) > 127
        self.assertGreater((maske & kreis).sum() / kreis.sum(), 0.99)
        self.assertLess((maske & ~kreis).sum(), 50)
        self.assertTrue(maske[80, 80])                    # das weiße Loch bleibt Person

    def test_3_grabcut_legt_die_kante_an(self):
        rgb, kreis = _kreisbild()
        grob = np.zeros((160, 160), dtype=np.float32)
        grob[40:120, 40:120] = 1.0                        # Quadrat statt Kreis
        vorher = (grob > 0.5)
        iou_vorher = (vorher & kreis).sum() / (vorher | kreis).sum()
        nachher = K.grabcut(rgb, grob) > 0.5
        iou_nachher = (nachher & kreis).sum() / (nachher | kreis).sum()
        self.assertGreater(iou_nachher, iou_vorher)      # gemessen: 0,775 → 0,903
        self.assertGreater(iou_nachher, 0.85)

    def test_4_regler_pruefen(self):
        r = Bildmodellfreisteller.regler_pruefen({
            'modell': 'gibtsnicht', 'matting': 1, 'verfeinern': 'zauber',
            'striche': [{'art': 'drin', 'breite': 0.5, 'punkte': []}, {'art': 'draussen', 'punkte': [[0.2, 0.3]]},
                        {'art': 'egal', 'punkte': [[0.2, 0.3]]}],
            'punkte': [[0.5, 0.5, 1], [1.5, 0.5, 0], ['x', 0, 1]]})
        self.assertEqual(r['modell'], 'u2net_human_seg')
        self.assertTrue(r['matting'])
        self.assertEqual(r['verfeinern'], '')
        self.assertEqual(len(r['striche']), 1)
        self.assertEqual(r['striche'][0]['breite'], 0.02)
        self.assertEqual(r['punkte'], [[0.5, 0.5, 1]])

    def test_5_gesichtsverzerrung(self):
        rng = np.random.default_rng(3)
        q = rng.uniform(300, 700, (51, 2))
        z = q + rng.normal(0, 12, (51, 2))
        g = Gesichtsverzerrung(q, z)
        u, v = g.anwenden(q[:, 0], q[:, 1])
        self.assertLess(float(np.linalg.norm(np.stack([u, v], 1) - z, axis=1).mean()), 1.0)
        u2, v2 = g.anwenden(np.array([0.0, 3000.0]), np.array([0.0, 3000.0]))
        self.assertTrue(np.allclose(u2, [0.0, 3000.0]) and np.allclose(v2, [0.0, 3000.0]))
        self.assertEqual(g.bericht()['punkte'], 51)
        identitaet = Gesichtsverzerrung(q, q)
        u3, v3 = identitaet.anwenden(q[:, 0] + 5, q[:, 1] - 3)
        self.assertTrue(np.allclose(u3, q[:, 0] + 5) and np.allclose(v3, q[:, 1] - 3))


if __name__ == '__main__':
    unittest.main()
