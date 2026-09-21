# -*- coding: utf-8 -*-
"""`Fototexturlauf.anteile`: Anteil je Bild an den GEDECKTEN Texeln, Summe 1.

WARUM (Edgar, 21.09.2026: „die Summe der Anteile soll 100 % ergeben"). Vorher
war der Nenner die ganze Textur — die Anteile summierten sich zur Deckung
(57 %), und nach einer Abwahl im Browser standen die Zahlen des letzten
Backens weiter da. Der Browser rechnet die gewaehlten Bilder auf 100 % um
(`texturansicht.js`); hier wird der Server-Teil geprueft, mit Attrappen statt
einer echten Textur:

1. Zwei Kacheln, drei Bilder, Ueberlappung: je Texel gewinnt das Bild mit dem
   groesseren Gewicht; die Anteile summieren sich zu 1, `gedeckt` ist die Zahl
   der Texel mit Herkunft, `gesamt` die Zahl aller Texel.
2. Ein Bild ohne Probe hat Anteil 0 und steht nicht in `je_kachel`.

Sabotage-Gegenprobe: `max(gedeckt, 1)` zurueck auf `max(gesamt, 1)` → Fall 1
rot (Summe 0,75 statt 1).
"""

import unittest

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np  # noqa: E402
from fototextur import Fototexturlauf  # noqa: E402


class _Textur:
    """Zwei Kacheln mit 4 bzw. 4 Texeln — `stellen` liefert nur `drin`."""

    kacheln = [1001, 1002]
    seite = 2

    def stellen(self, kachel):
        del kachel
        drin = np.ones((2, 2), dtype=bool)
        return drin, None, None


class DieAnteile(unittest.TestCase):

    def _lauf(self):
        lauf = Fototexturlauf(_Textur(), fotofarben=None)
        idx = np.arange(4, dtype=np.int32)
        w = lambda *werte: np.asarray(werte, dtype=np.float32)  # noqa: E731
        # Kachel 1001: Bild 0 gewinnt Texel 0,1; Bild 1 gewinnt Texel 2; Texel 3 bleibt leer.
        lauf.proben[1001][0] = (idx[:3], None, w(0.9, 0.8, 0.1))
        lauf.proben[1001][1] = (idx[:3], None, w(0.2, 0.3, 0.7))
        # Kachel 1002: Bild 1 gewinnt alle drei, Texel 3 leer.
        lauf.proben[1002][1] = (idx[:3], None, w(0.5, 0.5, 0.5))
        return lauf

    def test_1_summe_eins_und_gedeckt(self):
        anteile, gedeckt, gesamt, je_kachel = self._lauf().anteile(3)
        self.assertEqual(gesamt, 8)
        self.assertEqual(gedeckt, 6)
        self.assertAlmostEqual(float(anteile.sum()), 1.0, places=6)
        self.assertAlmostEqual(float(anteile[0]), 2 / 6, places=6)
        self.assertAlmostEqual(float(anteile[1]), 4 / 6, places=6)
        self.assertEqual(je_kachel[1001], {0: 2, 1: 1})
        self.assertEqual(je_kachel[1002], {1: 3})

    def test_2_bild_ohne_probe(self):
        anteile, _, _, je_kachel = self._lauf().anteile(3)
        self.assertEqual(float(anteile[2]), 0.0)
        self.assertNotIn(2, je_kachel[1001])
        self.assertNotIn(2, je_kachel[1002])


if __name__ == '__main__':
    unittest.main()
