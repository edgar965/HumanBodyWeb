# -*- coding: utf-8 -*-
"""`Kleidhautfilter` (06.10.2026): welche Foto-Pixel zählen für die Fotoprojektion eines Stücks als Haut und fallen weg.

Kunstfarben aus dem Auftrag „Edgar - Sapiens": dunkle Hose (0,25 0,19 0,18), der Glanz ihres Satins (0,50 0,45 0,55), Haut (0,47 0,30 0,21), eine Hautzelle neben dem Saum (0,80 0,45 0,20). Keine Datenbank, keine Dateien.
Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).

Sabotage: in `Kleidhautfilter.haut` `cls.ab(...)` durch die rohen RGB-Werte ersetzen (Abstand im Farbraum mit Helligkeit) → Fall 1 rot (der Glanz zählt als Haut); `MIN_ABSTAND` auf 0 → Fall 2 rot;
in `Kleidhautfilter.reinster` `max` durch `min` → Fall 4 rot (die Hand im Seitenfoto bliebe im Stück).
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.kleidhautfilter import Kleidhautfilter

HOSE, GLANZ, HAUT, ORANGE, BEIGE = (0.25, 0.19, 0.18), (0.50, 0.45, 0.55), (0.47, 0.30, 0.21), (0.80, 0.45, 0.20), (0.62, 0.50, 0.42)


def _bild(stoff=HOSE):
    """Links das Stück (mit einem Glanz und einer Hautzelle), rechts die Haut; `stueck` links, `koerper` rechts, die Figur überall."""
    farbe = np.zeros((40, 40, 3))
    farbe[:, :20] = stoff
    farbe[:, 20:] = HAUT
    farbe[5:8, 5:8] = GLANZ
    farbe[30:33, 10:13] = ORANGE
    stueck = np.zeros((40, 40), bool)
    stueck[:, :20] = True
    return farbe, np.ones((40, 40), bool), stueck, ~stueck


class DerKleidhautfilter(SimpleTestCase):
    def test_1_eine_hautzelle_faellt_weg_der_glanz_und_der_stoff_bleiben(self):
        aus = Kleidhautfilter.haut(*_bild())
        self.assertTrue(aus[31, 11])                              # Hautzelle im Stück
        self.assertTrue(aus[20, 30])                              # die Haut selbst
        self.assertFalse(aus[6, 6])                               # der helle Glanz: ein Farbton wie der Stoff, nur heller (in RGB lag er näher an der Haut)
        self.assertFalse(aus[20, 2])                              # der Stoff

    def test_2_ein_stueck_in_hautfarbe_wird_nicht_gefiltert(self):
        self.assertIsNone(Kleidhautfilter.haut(*_bild(BEIGE)))    # Farbtöne zu ähnlich: kein Ausschluss

    def test_3_ohne_genug_pixel_kein_urteil(self):
        farbe, figur, stueck, koerper = _bild()
        wenig = np.zeros_like(stueck)
        wenig[0, :10] = True                                      # 10 Pixel < `MIN_PIXEL`
        self.assertIsNone(Kleidhautfilter.haut(farbe, figur, wenig, koerper))

    def test_4_die_hand_vor_dem_stueck_faellt_mit_dem_farbton_der_reinsten_ansicht_weg(self):
        """Seitenfoto (06.10.2026): die Hand deckt 70 % der Maske der Hose, ihr Mittel liegt an der Haut — der Filter schaltete sich ab, die Hand kam als hautfarbener Fleck in die Textur."""
        farbe, figur, stueck, koerper = _bild()
        farbe[:28, :20] = HAUT
        hand = (farbe, figur, stueck, koerper)
        self.assertIsNone(Kleidhautfilter.haut(*hand))                                       # aus der eigenen Maske: kein Unterschied zur Haut
        bezug = Kleidhautfilter.reinster([Kleidhautfilter.bezug(*_bild()), Kleidhautfilter.bezug(*hand)])
        self.assertIsNotNone(bezug)
        aus = Kleidhautfilter.haut(*hand, stoff_ab=bezug[0])
        self.assertTrue(aus[10, 5])                                                          # die Hand
        self.assertFalse(aus[35, 2])                                                         # der Stoff darunter
        self.assertIsNone(Kleidhautfilter.reinster([None, None]))
        self.assertIsNone(Kleidhautfilter.reinster([Kleidhautfilter.bezug(*_bild(BEIGE))]))  # Farbtöne überall zu ähnlich
