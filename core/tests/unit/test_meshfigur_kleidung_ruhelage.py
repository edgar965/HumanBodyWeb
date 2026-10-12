# -*- coding: utf-8 -*-
"""Mesh to 3D, 12.10.2026: das Kleidungsobjekt wird mit Körperteilen in die Ruhelage zurückgerechnet (`Meshfigurkleidungsruhelage`).

Anlass (Auftrag „Edgar", `2026.10.12.12.18.38`, Edgar mit Bild: „Kleider stimmen noch nicht, siehe Unterhose"): die linke Hand hängt 6 cm neben dem Saum der Unterhose. Ihre 3.000 dichten Käfigpunkte stellten 25 % der 40 Nachbarn
der Saumpunkte; `Meshfigurkleidung.objekt` rechnete ohne Teile zurück, 627 Punkte (7 cm Saum) drehten mit dem Arm nach außen — eine Fahne bis 131 mm vom Körper, Kantenverzerrung bis 37,4×. Mit Teilen und Entzerren: größter Abstand
53 mm, Kanten außerhalb 0,75–1,33 von 5,25 auf 1,66 %, größte Streckung 2,2× (`ProjektTemp/_wegwerf/mesh3d/hose_entposen_ursache.py`).

Hier an Kunstdaten: ein Becken-Gitter (Teil „becken", dünn), daneben ein dichtes Handgitter (Teil „r_hand"), das sich in Ruhe um 180° verdreht und 0,3 m weit entfernt; der Stoff liegt 10 mm über dem Becken, sein Rand 25 mm vor der Hand.
Sabotage-Gegenprobe: in `Meshfigurkleidungsruhelage.punkte` `self.entposen.ruhelage(netz, teile)` durch `self.entposen.ruhelage(netz)` ersetzen → Fall 1 rot; den Zweig `self.teil is None` streichen → Fall 2 rot.

Ohne Datenbank. Geschrieben am 12.10.2026, nicht gelaufen — läuft nur auf Ansage.
"""

import unittest

import numpy as np
from Genesis9.koerperteile import G9koerperteile
from Kleidung.kleidungsentposen import Kleidungsentposen

from core.dienste.meshfigurkleidungsruhelage import Meshfigurkleidungsruhelage

BECKEN, HAND = G9koerperteile.NUMMER['becken'], G9koerperteile.NUMMER['r_hand']


def _gitter(nx, ny, x0, x1, y0, y1, z):
    x, y = np.meshgrid(np.linspace(x0, x1, nx), np.linspace(y0, y1, ny))
    return np.column_stack([x.ravel(), y.ravel(), np.full(nx * ny, z)])


def _kaefig():
    """Becken (21 × 21 Punkte, x −0,1 … 0,1) und daneben die dichte Hand (40 × 40, x 0,12 … 0,2); alle Normalen +z. Die Hand dreht sich in Ruhe um 180° um y und wandert 0,3 m weg."""
    becken = _gitter(21, 21, -0.1, 0.1, -0.1, 0.1, 0.0)
    hand = _gitter(40, 40, 0.12, 0.20, -0.1, 0.1, 0.0)
    drehung = np.diag([-1.0, 1.0, -1.0])
    hand_ruhe = hand @ drehung.T + np.array([0.3, 0.0, 0.0])
    posiert = np.vstack([becken, hand])
    ruhe = np.vstack([becken, hand_ruhe])
    teil = np.array([BECKEN] * len(becken) + [HAND] * len(hand))
    normalen = np.tile([0.0, 0.0, 1.0], (len(posiert), 1))
    return ruhe, posiert, teil, normalen


def _stoff(n=14):
    """Ein Stoffstück 10 mm über dem Becken, x 0,05 … 0,095: sein Rand liegt 25 mm vor der Hand. Dreiecke gegen den Uhrzeigersinn (Normale +z)."""
    punkte = _gitter(n, n, 0.05, 0.095, -0.03, 0.03, 0.01)
    dreiecke = []
    for j in range(n - 1):
        for i in range(n - 1):
            a = j * n + i
            dreiecke += [[a, a + 1, a + n], [a + 1, a + n + 1, a + n]]
    return punkte, np.array(dreiecke)


class RuhelageMitTeilenTest(unittest.TestCase):
    def test_1_die_hand_neben_dem_saum_zieht_den_stoff_nicht_mit(self):
        ruhe, posiert, teil, normalen = _kaefig()
        punkte, dreiecke = _stoff()
        # Erwartet: das Becken ändert sich zwischen Haltung und Ruhe nicht — der Stoff bleibt, wo er ist.
        ohne = Kleidungsentposen(ruhe, posiert).ruhelage(punkte)
        mit = Meshfigurkleidungsruhelage(ruhe, posiert, teil, normalen).punkte(punkte, dreiecke)
        abweichung_ohne = np.linalg.norm(ohne - punkte, axis=1).max()
        abweichung_mit = np.linalg.norm(mit - punkte, axis=1).max()
        self.assertGreater(abweichung_ohne, 0.01, 'ohne Teile hätte die Hand den Stoffrand mitgenommen')
        self.assertLess(abweichung_mit, 0.003, 'mit Teilen bleibt der Stoff am Becken')

    def test_2_ohne_teile_rechnet_es_wie_vorher(self):
        ruhe, posiert, _, normalen = _kaefig()
        punkte, dreiecke = _stoff()
        r = Meshfigurkleidungsruhelage(ruhe, posiert, None, normalen)
        np.testing.assert_array_equal(r.punkte(punkte, dreiecke), Kleidungsentposen(ruhe, posiert).ruhelage(punkte))
        self.assertEqual(r.befund, {'mit_teilen': False})

    def test_3_der_befund_nennt_den_abstand_zum_kaefig(self):
        ruhe, posiert, teil, normalen = _kaefig()
        punkte, dreiecke = _stoff()
        r = Meshfigurkleidungsruhelage(ruhe, posiert, teil, normalen)
        r.punkte(punkte, dreiecke)
        b = r.befund
        self.assertTrue(b['mit_teilen'])
        self.assertAlmostEqual(b['abstand_median_mm'], 10.0, delta=2.0)
        self.assertLess(b['abstand_max_mm'], 20.0)


if __name__ == '__main__':
    unittest.main()
