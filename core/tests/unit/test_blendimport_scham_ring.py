# -*- coding: utf-8 -*-
"""Die Linie des Kantenrings wird glatt (`Blendimportschamring`) — an einem gezackten Ring auf einer Ebene, ohne Django.

BEFUND (Chrome, „cute girl", 09.10.2026, Haut und Stück verschweißt): Die Kanten der Haut an den Leisten sind 2,3–9 mm lang, der Ring
wechselt dort die Richtung um bis zu 134° (Summe der Richtungswechsel 5.412° auf 98 Ecken). Die Naht war dicht, ihre Linie aber gezähnt.
Mit 20 Durchgängen und höchstens 4 mm Weg: 1.013°, zwei Ecken über 60°.

Kunstwelt: Haut = Ebene y = 0 (Normalen nach oben), Ring = Kreis aus 48 Ecken, Radius 30 mm, jede zweite Ecke 2 mm nach außen gezogen
(Zickzack); als Dreiecke eine Scheibe über dem Ring (Mitte + Ring), damit das Umklappen geprüft werden kann.

1. `glaetten`: der Zickzack ist kleiner (die Spanne der Radien sinkt auf unter die Hälfte; gemessen 2,0 → 0,0 mm), keine Ecke wandert weiter als
   `MAX_MM`, die Ebene wird nicht verlassen (y bleibt 0).
2. `glaetten` verändert die Eingabe nicht; ein glatter Kreis bleibt rund (er schrumpft gleichmäßig, wie jede Laplace-Glättung, höchstens
   um `MAX_MM`).
3. `ziehen`: gibt die Verschiebung ALLER Punkte auf dem Ring zurück (auch Doppelgänger an UV-Nähten), mit `d` je Punkt; wo ein Dreieck
   AUSSERHALB des Lochs umklappen würde, wird die Ecke gekürzt (`halbiert`), danach klappt keines um.

Sabotage-Gegenprobe (nicht gelaufen): in `glaetten` die Tangentialebene (`d -= …`) weglassen macht Fall 1 rot, sobald die Normalen schief
stehen; `grenze` auf unendlich macht Fall 1 rot; die Prüfung in `ziehen` weglassen macht Fall 3 rot.
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportschamring import Blendimportschamring


class SchamringTest(SimpleTestCase):
    databases = set()

    K = 48
    RADIUS = 0.030

    def _zickzack(self):
        winkel = np.arange(self.K) * (2 * np.pi / self.K)
        radius = np.where(np.arange(self.K) % 2 == 0, self.RADIUS, self.RADIUS + 0.002)
        return np.stack([radius * np.cos(winkel), np.zeros(self.K), radius * np.sin(winkel)], axis=1)

    @staticmethod
    def _zacken(lage):
        """Die Spanne der Radien (größter − kleinster): wie gezackt der Ring ist. Nicht die Abweichung von einem festen Radius — jede
        Laplace-Glättung lässt einen Kreis schrumpfen (hier 30 → 28,45 mm; gemessen 10.10.2026, `scham_ring_probe.py`), das ist keine Zacke."""
        r = np.linalg.norm(lage[:, [0, 2]], axis=1)
        return float(r.max() - r.min())

    def test_1_der_zickzack_wird_kleiner_und_bleibt_in_der_ebene(self):
        lage = self._zickzack()
        normalen = np.tile([0.0, 1.0, 0.0], (self.K, 1))
        glatt = Blendimportschamring.glaetten(lage, normalen)
        self.assertLess(self._zacken(glatt), 0.5 * self._zacken(lage))
        weg = np.linalg.norm(glatt - lage, axis=1)
        self.assertLessEqual(float(weg.max()), Blendimportschamring.MAX_MM / 1000.0 + 1e-12)
        self.assertTrue(np.allclose(glatt[:, 1], 0.0))

    def test_2_die_eingabe_bleibt_und_ein_kreis_bleibt_ein_kreis(self):
        lage = self._zickzack()
        vorher = lage.copy()
        Blendimportschamring.glaetten(lage, np.tile([0.0, 1.0, 0.0], (self.K, 1)))
        self.assertTrue(np.array_equal(lage, vorher))
        winkel = np.arange(self.K) * (2 * np.pi / self.K)
        kreis = np.stack([self.RADIUS * np.cos(winkel), np.zeros(self.K), self.RADIUS * np.sin(winkel)], axis=1)
        glatt = Blendimportschamring.glaetten(kreis, np.tile([0.0, 1.0, 0.0], (self.K, 1)))
        radius = np.linalg.norm(glatt[:, [0, 2]], axis=1)
        self.assertLess(float(radius.max() - radius.min()), 1e-9, 'ein Kreis bleibt rund (er schrumpft nur gleichmäßig)')
        self.assertLessEqual(float(np.linalg.norm(glatt - kreis, axis=1).max()), Blendimportschamring.MAX_MM / 1000.0 + 1e-12)

    def test_3_ziehen_meldet_alle_ringpunkte_und_klappt_nichts_um(self):
        lage = self._zickzack()
        # Haut: Scheibe über dem Ring (Mitte + 48 Ringpunkte) PLUS ein Außenring (Punkte 49 … 96) mit Dreiecken nach außen
        mitte = np.zeros((1, 3))
        aussen = lage * 1.25
        punkte = np.vstack([mitte, lage, aussen])
        k = self.K
        innen = [[0, 1 + i, 1 + (i + 1) % k] for i in range(k)]
        ausser = []
        for i in range(k):
            a, b = 1 + i, 1 + (i + 1) % k
            c, d = 1 + k + i, 1 + k + (i + 1) % k
            ausser += [[a, c, b], [b, c, d]]
        dreiecke = np.array(innen + ausser)
        im_loch = np.zeros(len(dreiecke), dtype=bool)
        im_loch[:k] = True
        ring_punkte = np.arange(1, 1 + k)
        normalen = np.tile([0.0, 1.0, 0.0], (k, 1))
        ziel, v = Blendimportschamring.ziehen(punkte, dreiecke, im_loch, ring_punkte, lage, normalen)
        self.assertEqual(sorted(v['punkte'].tolist()), ring_punkte.tolist())
        self.assertEqual(v['d'].shape, (k, 3))
        self.assertTrue(np.allclose(v['d'], ziel - lage))
        neu = punkte.copy()
        neu[ring_punkte] = ziel
        aussen_dreiecke = dreiecke[~im_loch]
        vorher = Blendimportschamring.flaechennormalen(punkte, aussen_dreiecke)
        nachher = Blendimportschamring.flaechennormalen(neu, aussen_dreiecke)
        self.assertTrue(bool(((vorher * nachher).sum(axis=1) > 0).all()), 'kein Hautdreieck außerhalb des Lochs klappt um')
