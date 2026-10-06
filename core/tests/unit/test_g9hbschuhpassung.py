# -*- coding: utf-8 -*-
"""Der Schuh als Ganzes am HumanBody-Fuss (`G9hbschuhpassung`, 05.10.2026).

Edgar (05.10.2026): „Angie_Sneakers passt nicht auf Modell F2_ShirtLeggins, große Zehe geht durch den Schuh“, danach „nichts geändert“. Gemessen an
F2_ShirtLeggins (`_wegwerf/edgar/schuh_ueberstand.py`): Punkt für Punkt übertragen stand die Kappe 3–4 mm VOR der Sohle, 17–19 von 960 Hautpunkten der Zehen
ragten durch die Kappe, und die Kappe hatte Spitzen bis 12 mm. Zusagen (mit einer Kunstfigur, ohne Netze):

1. Ein Fuss, der auf dem HumanBody-Fuss gestreckt ist (z · 1,2), streckt den Schuh mit — Sohle und Kappe behalten ihre Lage zueinander.
2. Hoch über dem Boden (ab `AUS_AB`) gilt die Übertragung Punkt für Punkt, darunter (bis `VOLL_BIS`) die Passung ganz, dazwischen linear gemischt.
3. Ohne genug gepaarte Fusspunkte bleibt es bei der Übertragung — kein Fehler.
4. Die Seiten (x > 0 / x < 0) bekommen je ihre Abbildung.
5. Die Schuhwahl: `ist_schuh` liest die WIRKSAME Kategorie; ist die Einteilung nicht lesbar, ist es Kleidung.
"""
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.api.g9kleidhumanbody import G9kleidhumanbody
from core.dienste.g9hbschuhpassung import G9hbschuhpassung


def _fuss(n=600, streck=1.2):
    """Kunstfuss: Punkte beider Füsse (x = ±0,09 ± 0,04, y 0–0,07, z −0,03–0,15), HumanBody-Fuss = gestreckt in z."""
    zufall = np.random.RandomState(7)
    g9 = np.column_stack([zufall.uniform(-0.04, 0.04, n), zufall.uniform(0.0, 0.07, n), zufall.uniform(-0.03, 0.15, n)])
    g9 = np.vstack([g9 + [0.09, 0.0, 0.0], g9 + [-0.09, 0.0, 0.0]])
    hb = g9 * [1.0, 1.0, streck]
    return g9, hb


def _traeger(g9, hb, uebertragen=None):
    zu = np.arange(len(g9))
    return SimpleNamespace(paarung={'g9_punkte': g9, 'zu': zu}, figur=lambda: {'punkte': hb},
                           uebertragen=uebertragen or (lambda p, bindung=None: np.asarray(p) + 0.5))


class DerSchuhAlsGanzes(SimpleTestCase):
    def test_1_ein_gestreckter_fuss_streckt_den_schuh_mit(self):
        g9, hb = _fuss()
        schuh = np.array([[0.09, 0.02, 0.15], [0.09, -0.01, 0.15], [0.09, 0.02, 0.0], [-0.09, 0.02, 0.15]])
        aus = G9hbschuhpassung.passen(_traeger(g9, hb), schuh)
        np.testing.assert_allclose(aus, schuh * [1.0, 1.0, 1.2], atol=2e-3)
        # Sohle und Kappe an der Spitze (gleich weit vorn) bleiben gleich weit vorn.
        self.assertAlmostEqual(aus[0, 2], aus[1, 2], places=6)

    def test_2_hoch_ueber_dem_boden_gilt_die_punktweise_uebertragung(self):
        g9, hb = _fuss()
        schuh = np.array([[0.09, 0.30, 0.05], [0.09, 0.15, 0.05], [0.09, 0.05, 0.05]])
        aus = G9hbschuhpassung.passen(_traeger(g9, hb), schuh)
        np.testing.assert_allclose(aus[0], schuh[0] + 0.5)                       # ab AUS_AB: nur die Uebertragung
        np.testing.assert_allclose(aus[2], schuh[2] * [1.0, 1.0, 1.2], atol=2e-3)  # unter VOLL_BIS: nur die Passung
        mitte = 0.5 * (schuh[1] + 0.5) + 0.5 * schuh[1] * [1.0, 1.0, 1.2]
        np.testing.assert_allclose(aus[1], mitte, atol=2e-3)                       # dazwischen linear

    def test_3_ohne_genug_fusspunkte_bleibt_es_bei_der_uebertragung(self):
        g9, hb = _fuss(n=20)
        schuh = np.array([[0.09, 0.02, 0.1], [-0.09, 0.02, 0.1]])
        aus = G9hbschuhpassung.passen(_traeger(g9, hb), schuh)
        np.testing.assert_allclose(aus, schuh + 0.5)

    def test_4_jede_seite_bekommt_ihre_abbildung(self):
        g9, hb = _fuss()
        hb = hb.copy()
        hb[len(hb) // 2:, 2] += 0.03                                             # rechter Fuss (x < 0) 3 cm weiter vorn
        schuh = np.array([[0.09, 0.02, 0.1], [-0.09, 0.02, 0.1]])
        aus = G9hbschuhpassung.passen(_traeger(g9, hb), schuh)
        self.assertAlmostEqual(aus[0, 2], 0.12, delta=2e-3)
        self.assertAlmostEqual(aus[1, 2], 0.15, delta=2e-3)

    def test_5_leere_punkte_gehen_durch(self):
        g9, hb = _fuss()
        self.assertEqual(G9hbschuhpassung.passen(_traeger(g9, hb), np.zeros((0, 3))).shape, (0, 3))


class DieSchuhwahl(SimpleTestCase):
    def test_6_die_wirksame_kategorie_entscheidet(self):
        kategorie = 'Genesis9.garderobekategorien.G9garderobekategorien.kategorie'
        with mock.patch(kategorie, return_value=u'Schuhe'):
            self.assertTrue(G9kleidhumanbody.ist_schuh({'id': 'angie_sneakers'}))
        with mock.patch(kategorie, return_value=u'Oberteile'):
            self.assertFalse(G9kleidhumanbody.ist_schuh({'id': 'g9_base_shirt'}))
        with mock.patch(kategorie, side_effect=OSError('weg')):
            self.assertFalse(G9kleidhumanbody.ist_schuh({'id': 'x'}))
