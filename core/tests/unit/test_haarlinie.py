# -*- coding: utf-8 -*-
"""Haarlinie (05.10.2026, Edgar: „Haar ist eine Linie über den Ohren, ist nicht so im Bild"): Ohrfelder aus dem Hautgewicht auf dem Ohrknochen, Gesicht, Koteletten und der runde Nacken.

Kunstdaten: Punkte einer Kugel im 5°-Raster um MITTE (Azimut von +z nach +x, Höhenwinkel von der Waagerechten, wie `Haarklemme`), Haut mit den Knochen `head` und `l_ear`. Keine Datenbank, keine Dateien.
Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).

Sabotage: in `Haarlinie.nacken` `UNTEN_SEITE` und `UNTEN_MITTE` vertauschen → Fall 1 rot; in `ohrfelder` `OHR_GEWICHT` auf 2,0 setzen → Fall 2 rot; in `ausschluss` `KOTELETT_ANTEIL` auf 0 setzen → Fall 5 rot.
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.haarlinie import Haarlinie
from core.dienste.haarwuchs import Haarwuchs

MITTE = np.array([0.0, 1.6, 0.0])
HOEHE, BREITE = 36, 72


def _netz(ohr=False):
    """Eine Kugel im 5°-Raster; `ohr`: Gewicht 1 auf `l_ear` für Azimut 85–105° und Höhenwinkel −10…10°."""
    el = np.arange(-87.5, 90.0, 5.0)
    az = np.arange(2.5, 360.0, 5.0)
    punkte, am_ohr = [], []
    for e in el:
        for a in az:
            punkte.append(MITTE + 0.1 * Haarwuchs.einheit(a, e))
            am_ohr.append(bool(ohr and 85.0 <= a <= 105.0 and -10.0 <= e <= 10.0))
    n = len(punkte)
    index = np.zeros((n, 4), dtype=np.int64)
    index[:, 0] = np.where(am_ohr, 1, 0)                              # Knochen 1 = `l_ear`
    gewicht = np.zeros((n, 4))
    gewicht[:, 0] = 1.0
    return {'punkte': np.array(punkte), 'haut': {'knochen': ['head', 'l_ear'], 'index': index.reshape(-1), 'gewicht': gewicht.reshape(-1)}}


def _hoehen_und_azimute():
    return ((np.arange(HOEHE) + 0.5) * 5.0 - 90.0)[:, None], (np.arange(BREITE) + 0.5) * 5.0


class DieHaarlinie(SimpleTestCase):
    def test_1_der_nacken_steigt_von_der_mitte_zu_den_ohren_an(self):
        el, az = _hoehen_und_azimute()
        nacken = Haarlinie.nacken(el, az)
        self.assertEqual(nacken.shape, (HOEHE, BREITE))
        hinten, seite = int(180.0 / 5.0), int(90.0 / 5.0)            # Azimut 180° bzw. 90°
        zeile = lambda grad: int((grad + 90.0) / 5.0)                # noqa: E731
        self.assertTrue(nacken[zeile(-42.5), hinten])                # unter −38° hinten: kein Haar
        self.assertFalse(nacken[zeile(-32.5), hinten])               # darüber: Haar
        self.assertTrue(nacken[zeile(-27.5), seite])                 # an den Ohren (−24°) liegt der Rand höher …
        self.assertFalse(nacken[zeile(-17.5), seite])                # … und darüber wächst Haar

    def test_2_die_ohrfelder_kommen_aus_dem_hautgewicht_auf_dem_ohrknochen(self):
        felder = Haarlinie.ohrfelder(_netz(ohr=True), MITTE, HOEHE, BREITE)
        self.assertTrue(felder[17:19, 18:20].all())                  # Höhe −2,5…2,5°, Azimut 92,5…97,5°
        self.assertFalse(felder[18, 54])                             # Azimut 272,5°: das andere Ohr hat hier keine Punkte
        self.assertFalse(felder[30, 19])                             # weit über dem Ohr
        self.assertGreater(int(felder.sum()), 16)                    # um ein Feld erweitert (`OHR_RAND`)

    def test_3_ohne_ohrknochen_gibt_es_keine_ohrfelder(self):
        self.assertFalse(Haarlinie.ohrfelder(_netz(ohr=False), MITTE, HOEHE, BREITE).any())
        self.assertFalse(Haarlinie.ohrfelder(None, MITTE, HOEHE, BREITE).any())
        netz = _netz(ohr=False)
        netz['haut'] = {'knochen': ['head'], 'index': netz['haut']['index'], 'gewicht': netz['haut']['gewicht']}
        self.assertFalse(Haarlinie.ohrfelder(netz, MITTE, HOEHE, BREITE).any())

    def test_4_gesicht_wange_und_nacken_haben_kein_haar_die_stirnseite_oben_schon(self):
        weg, _kotelett = Haarlinie.ausschluss(_netz(), MITTE, np.full((HOEHE, BREITE), 0.11))
        zeile = lambda grad: int((grad + 90.0) / 5.0)                # noqa: E731
        self.assertTrue(weg[zeile(2.5), 0])                          # Gesicht (Azimut 2,5°, Höhe 2,5°)
        self.assertTrue(weg[zeile(22.5), 5])                         # Schläfe vorn unter `GESICHT_EL`
        self.assertFalse(weg[zeile(37.5), 0])                        # Stirn über 30°: entscheidet der Haaransatz des Netzhaars, nicht die Regel
        self.assertTrue(weg[zeile(2.5), 15])                         # Wange (Azimut 77,5°) unter den Koteletten; ohne Ohrknochen gilt ein Ohr bei 100°
        self.assertTrue(weg[zeile(-42.5), 36])                       # Nacken
        self.assertFalse(weg[zeile(62.5), 36])                       # Hinterkopf oben

    def test_5_koteletten_wachsen_nur_wo_das_netzhaar_dort_haar_zeigt(self):
        zeile = lambda grad: int((grad + 90.0) / 5.0)                # noqa: E731
        roh = np.full((HOEHE, BREITE), 0.11)
        weg, kotelett = Haarlinie.ausschluss(_netz(), MITTE, roh)
        self.assertTrue(kotelett[zeile(17.5), 15])                   # Azimut 77,5°, Höhe 17,5°: zwischen Gesicht und Ohr, über `KOTELETT_EL`
        self.assertFalse(weg[zeile(17.5), 15])
        leer = roh.copy()
        leer[20:24, 12:20] = np.nan                                  # Zone der Koteletten rechts (Azimut 62,5…97,5°, Höhe 12,5…27,5°) …
        leer[20:24, 52:60] = np.nan                                  # … und links (262,5…297,5°) ohne Netzhaar
        _weg, kotelett = Haarlinie.ausschluss(_netz(), MITTE, leer)
        self.assertFalse(kotelett.any())

    def test_6_mit_ohr_endet_die_kotelettenzone_vor_dem_ohr_und_das_ohr_selbst_hat_kein_haar(self):
        roh = np.full((HOEHE, BREITE), 0.11)
        weg, kotelett = Haarlinie.ausschluss(_netz(ohr=True), MITTE, roh)
        zeile = lambda grad: int((grad + 90.0) / 5.0)                # noqa: E731
        self.assertTrue(weg[zeile(2.5), 19])                         # Ohr (Azimut 97,5°)
        self.assertTrue(weg[zeile(7.5), 18])
        self.assertTrue(kotelett[zeile(17.5), 14])                   # Azimut 72,5° liegt vor dem Ohr (Rand bei 82,5°)
        self.assertFalse(kotelett[zeile(17.5), 19])                  # hinter dem vorderen Rand des Ohrs keine Koteletten mehr
