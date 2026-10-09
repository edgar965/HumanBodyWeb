# -*- coding: utf-8 -*-
"""Gewichte des Scham-Stücks (Edgar, 09.10.2026: „gespreizte Beine: das Stück ist starr"): `Blendimportschamgewichte` ohne Genesis.

Gemessen am Modell „cute girl" (Oberschenkel 25° gespreizt): die Haut neben dem Stück bewegte sich im Median 6,6 mm, das Stück 0 mm —
es hing zu 98,1 % am Becken, weil seine drei im Raum nächsten Hautpunkte (der Grundfigur) in der Mitte lagen, während es bis 25 mm
HINTER der Haut sitzt. Hier die Bausteine an einer Kunsthaut:

* Haut A: ein Blatt bei z = 0 (Normale +z), links `r_thigh`, in der Mitte `pelvis`, rechts `l_thigh`.
* Haut B: eine Wand bei x = 12 mm, hinter dem Blatt (z −80 … −10 mm), Normale −x (zur Lücke hin), `l_thigh`.

1. Ein Stückpunkt 20 mm hinter der Mitte des Blatts bekommt `pelvis` — obwohl die Wand mit 12 mm näher liegt als das Blatt mit 20 mm
   (der Weg der Grundfigur hätte `l_thigh` genommen: die Wand ist ihm im Raum näher).
2. Ein Punkt auf dem Blatt bekommt genau die Gewichte der Haut dort (rechts `l_thigh`, links `r_thigh`).
3. `kuerzen` behält die vier stärksten Knochen und normiert; `glaetten` rückt einen Punkt ins Mittel seiner Netznachbarn.
4. Ein Punkt, den keine Haut verdeckt (weit weg), bekommt trotzdem Gewichte (die nächsten) und steht in `bericht['ohne_verdecker']`.

Sabotage-Gegenprobe: `DAVOR_M` auf 1,0 → Fall 1 rot (die Wand gewinnt); `NACHBARN` auf 1 und `GLAETTEN` 0 ändern Fall 1/3 nicht, das
Streichen der Normierung in `kuerzen` macht Fall 3 rot.

Nicht gelaufen (Stand 09.10.2026) — läuft nur auf Ansage.
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportschamgewichte import Blendimportschamgewichte


class SchamgewichteTest(SimpleTestCase):
    databases = set()

    KNOCHEN = ['pelvis', 'l_thigh', 'r_thigh']

    @staticmethod
    def _gitter(achsen, feste_achse, fest, bereiche, schritt, umdrehen):
        """Ein ebenes Punktgitter mit Dreiecken; `achsen` = die zwei freien Achsen (0/1/2); `umdrehen` kehrt die Flächenrichtung um."""
        u = np.arange(bereiche[0][0], bereiche[0][1] + 1e-9, schritt)
        v = np.arange(bereiche[1][0], bereiche[1][1] + 1e-9, schritt)
        punkte = np.zeros((len(u) * len(v), 3))
        for i, a in enumerate(u):
            for j, b in enumerate(v):
                p = punkte[i * len(v) + j]
                p[achsen[0]], p[achsen[1]], p[feste_achse] = a, b, fest
        dreiecke = []
        for i in range(len(u) - 1):
            for j in range(len(v) - 1):
                a, b, c, d = i * len(v) + j, (i + 1) * len(v) + j, i * len(v) + j + 1, (i + 1) * len(v) + j + 1
                dreiecke += [[a, b, c], [b, d, c]]
        dreiecke = np.array(dreiecke)
        return punkte, dreiecke[:, ::-1] if umdrehen else dreiecke

    def _haut(self):
        blatt, d1 = self._gitter((0, 1), 2, 0.0, ((-0.08, 0.08), (0.0, 0.1)), 0.005, False)
        wand, d2 = self._gitter((2, 1), 0, 0.012, ((-0.08, -0.01), (0.0, 0.1)), 0.005, False)
        # Die Richtung prüfen, statt sie zu glauben: das Blatt zeigt nach +z, die Wand nach −x.
        n1 = Blendimportschamgewichte.punktnormalen(blatt, d1).mean(axis=0)
        n2 = Blendimportschamgewichte.punktnormalen(wand, d2).mean(axis=0)
        if n1[2] < 0:
            d1 = d1[:, ::-1]
        if n2[0] > 0:
            d2 = d2[:, ::-1]
        punkte = np.vstack([blatt, wand])
        dreiecke = np.vstack([d1, d2 + len(blatt)])
        index = np.zeros((len(punkte), 4), dtype=np.int64)
        gewicht = np.zeros((len(punkte), 4))
        gewicht[:, 0] = 1.0
        index[:len(blatt), 0] = np.where(blatt[:, 0] > 0.03, 1, np.where(blatt[:, 0] < -0.03, 2, 0))
        index[len(blatt):, 0] = 1
        return Blendimportschamgewichte(punkte, dreiecke, index, gewicht, self.KNOCHEN)

    @staticmethod
    def _je_punkt(gewichte, anzahl):
        dicht = {}
        for knochen, liste in gewichte.items():
            for punkt, w in liste:
                dicht.setdefault(punkt, {})[knochen] = w
        return [dicht.get(i, {}) for i in range(anzahl)]

    def test_1_ein_punkt_hinter_der_haut_folgt_der_haut_davor_nicht_der_naechsten_wand(self):
        haut = self._haut()
        normalen = haut.normalen
        self.assertGreater(normalen[0][2], 0.9, 'Kunsthaut: das Blatt muss nach +z zeigen')
        aus = haut.gewichte(np.array([[0.0, 0.05, -0.020]]), np.zeros((0, 3), dtype=np.int64))
        punkt = self._je_punkt(aus, 1)[0]
        self.assertGreaterEqual(punkt.get('pelvis', 0.0), 0.9, 'die Wand (12 mm, zur Lücke) darf das Stück nicht an den Oberschenkel binden: %s' % punkt)
        self.assertEqual(haut.bericht['ohne_verdecker'], 0)

    def test_2_ein_punkt_auf_der_haut_bekommt_deren_gewichte(self):
        haut = self._haut()
        aus = haut.gewichte(np.array([[0.05, 0.05, 0.0], [-0.05, 0.05, -0.002]]), np.zeros((0, 3), dtype=np.int64))
        punkte = self._je_punkt(aus, 2)
        self.assertGreaterEqual(punkte[0].get('l_thigh', 0.0), 0.9, punkte[0])
        self.assertGreaterEqual(punkte[1].get('r_thigh', 0.0), 0.9, punkte[1])

    def test_3_kuerzen_behaelt_vier_knochen_und_normiert_glaetten_mittelt(self):
        haut = self._haut()
        dicht = np.array([[0.3, 0.25, 0.2, 0.15, 0.06, 0.04]])
        kurz = haut.kuerzen(dicht.copy())
        self.assertEqual(int((kurz[0] > 0).sum()), 4)
        self.assertAlmostEqual(float(kurz[0].sum()), 1.0, places=9)
        zwei = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        self.assertEqual(Blendimportschamgewichte.GLAETTEN, 0, 'gemessen: jedes Glätten öffnet die Lücke beim Spreizen wieder')
        haut.GLAETTEN = 2                                                       # die Rechnung selbst bleibt prüfbar
        glatt = haut.glaetten(zwei, np.array([[0, 1, 2]]))
        self.assertTrue(np.allclose(glatt.sum(axis=1), 1.0))
        self.assertLess(glatt[0, 0], 1.0, 'der Punkt rückt ins Mittel seiner Netznachbarn')
        self.assertGreater(glatt[0, 1], 0.0)

    def test_4_ohne_verdecker_gilt_der_naechste_und_wird_gezaehlt(self):
        haut = self._haut()
        aus = haut.gewichte(np.array([[0.0, 0.05, 0.5]]), np.zeros((0, 3), dtype=np.int64))
        punkt = self._je_punkt(aus, 1)[0]
        self.assertAlmostEqual(sum(punkt.values()), 1.0, places=3)
        self.assertEqual(haut.bericht['ohne_verdecker'], 1)
