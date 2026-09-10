# -*- coding: utf-8 -*-
u"""Die zwei Sitz-Kennzahlen eines drapierten Stuecks.

Bis zum 10.09.2026 gab es eine: den Median ueber alle Stoffpunkte. Er hat
dreimal in die falsche Zone gefuehrt — 9,4 mm gemeldet, waehrend der Stoff
an der Brust auf 2,7 mm anlag, weil Dekollete, Achsel und frei fallender
Saum mitzaehlen.
"""

import numpy as np
from django.test import SimpleTestCase

from GarmentCode.hautabstand import Hautabstand


def rig_mit(abstaende_mm):
    u"""Ein Rig-dict, dessen Ankerversatz genau diese Laengen hat."""
    versatz = [[0.0, 0.0, mm / 1000.0] for mm in abstaende_mm]
    # Dictionary gewollt: so liegt die Rig-Datei auf der Platte.
    return {'anker': {'versatz': versatz}}


class ZweiZahlenStattEiner(SimpleTestCase):

    def test_das_engste_viertel_ist_das_untere_quartil(self):
        sitz = Hautabstand.aus_rig(rig_mit([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
        self.assertAlmostEqual(sitz.eng_mm, np.percentile(range(1, 11), 25),
                               places=6)

    def test_der_median_bleibt_der_median(self):
        sitz = Hautabstand.aus_rig(rig_mit([1, 2, 3, 4, 100]))
        self.assertAlmostEqual(sitz.median_mm, 3.0, places=6)

    def test_frei_haengende_punkte_verderben_das_enge_viertel_nicht(self):
        u"""Der Kern der Aenderung.

        Ein Stueck, das mit einem Viertel seiner Punkte anliegt und mit dem
        Rest frei haengt — genau die Lage am T-Shirt. Der Median sagt 20 mm,
        das engste Viertel 2,5 mm, und nur die zweite Zahl beantwortet die
        Frage „liegt es an?".
        """
        sitz = Hautabstand.aus_rig(rig_mit([2, 2, 3, 3] + [20, 30, 40, 50]))
        self.assertLess(sitz.eng_mm, 3.0)
        self.assertGreater(sitz.median_mm, 10.0)

    def test_die_punktzahl_wird_mitgefuehrt(self):
        self.assertEqual(Hautabstand.aus_rig(rig_mit([1, 2, 3])).punkte, 3)


class OhneAnkerGibtEsNichtsZuMessen(SimpleTestCase):
    u"""Ein Stueck ohne Verankerung ist kein Fehlerfall, sondern ein Stueck
    ohne Rig — es darf keine Ausnahme werfen."""

    def test_leere_ankerliste(self):
        sitz = Hautabstand.aus_rig(rig_mit([]))
        self.assertEqual((sitz.eng_mm, sitz.median_mm, sitz.punkte),
                         (0.0, 0.0, 0))

    def test_gar_kein_rig(self):
        sitz = Hautabstand.aus_rig(None)
        self.assertEqual(sitz.punkte, 0)

    def test_rig_ohne_ankerschluessel(self):
        sitz = Hautabstand.aus_rig({'punkte': 12})
        self.assertEqual(sitz.punkte, 0)


class SitztOderSitztNicht(SimpleTestCase):
    u"""Beide Grenzen muessen halten — sie fangen verschiedene Fehler."""

    def test_ein_anliegendes_stueck_sitzt(self):
        u"""Zahlen des gemessenen „T-Shirt (anliegend)": 2,4 / 4,5 mm."""
        self.assertTrue(Hautabstand(2.4, 4.5).sitzt)

    def test_ein_weit_fallender_rock_sitzt_auch(self):
        u"""Kreisrock, gemessen: 8,2 mm im engsten Viertel, 27,4 Median.

        Er steht ab — das ist sein Schnitt, kein Passungsfehler. Genau
        deshalb reicht die Median-Grenze allein nicht.
        """
        self.assertTrue(Hautabstand(8.2, 27.4).sitzt)

    def test_auf_dem_falschen_koerper_sitzt_es_nicht(self):
        u"""Der dokumentierte Fall vom 06.09.2026: Median 27,4 mm mit 31 %
        der Punkte ueber 5 cm — dort ist auch das engste Viertel weit weg."""
        self.assertFalse(Hautabstand(25.0, 45.0).sitzt)

    def test_durchgehend_zu_weit_faellt_an_der_engen_grenze(self):
        u"""Ein Stueck, dessen Median die 40 mm haelt, das aber nirgends
        anliegt — ohne die zweite Grenze ginge das als „sitzt" durch."""
        self.assertFalse(Hautabstand(25.0, 30.0).sitzt)

    def test_nur_der_median_reisst(self):
        self.assertFalse(Hautabstand(5.0, 50.0).sitzt)


class WasAnDenBrowserGeht(SimpleTestCase):

    def test_alle_drei_felder(self):
        # 4,57 und nicht 4,55: Bei einer Zahl, die genau auf der Haelfte
        # liegt, entscheidet die Float-Darstellung, wohin `round` geht —
        # der Test pruefte dann nicht die Klasse, sondern Python.
        werte = Hautabstand(2.44, 4.57).als_dict()
        self.assertEqual(werte, {'hautabstand_mm': 4.6,
                                 'hautabstand_eng_mm': 2.4,
                                 'hautabstand_sitzt': True})

    def test_hautabstand_mm_bleibt_der_median(self):
        u"""Damit frueher gemessene Werte vergleichbar bleiben — die Zahl
        steht in Dutzenden Notizen und Docstrings."""
        werte = Hautabstand(2.0, 9.4).als_dict()
        self.assertEqual(werte['hautabstand_mm'], 9.4)


class DerGemeinsameKernNimmtBeideEingaben(SimpleTestCase):
    u"""`aus_laengen` bekommt aus der Vorschau eine Liste und aus `aus_rig`
    ein numpy-Array. Beides muss gehen.

    Der Array-Fall ist kein hypothetischer: `laengen_mm or []` hat genau
    hier geworfen („The truth value of an array … is ambiguous"), und der
    Weg ueber `aus_rig` ist der, den jeder fertige Bau nimmt.
    """

    def test_eine_liste(self):
        self.assertEqual(Hautabstand.aus_laengen([2.0, 4.0, 6.0]).punkte, 3)

    def test_ein_numpy_array(self):
        sitz = Hautabstand.aus_laengen(np.array([2.0, 4.0, 6.0]))
        self.assertEqual(sitz.punkte, 3)
        self.assertAlmostEqual(sitz.median_mm, 4.0, places=6)

    def test_ein_leeres_array(self):
        self.assertEqual(Hautabstand.aus_laengen(np.array([])).punkte, 0)

    def test_none(self):
        self.assertEqual(Hautabstand.aus_laengen(None).punkte, 0)

    def test_vorschau_und_bau_rechnen_gleich(self):
        u"""Dieselben Abstaende muessen dieselbe Kennzahl ergeben, egal auf
        welchem Weg sie gemessen wurden — sonst vergleicht der Nutzer
        Vorschau und Ergebnis mit zwei verschiedenen Zahlen."""
        laengen = [2.0, 3.0, 5.0, 9.0, 20.0]
        ueber_liste = Hautabstand.aus_laengen(laengen)
        ueber_rig = Hautabstand.aus_rig(rig_mit(laengen))
        self.assertAlmostEqual(ueber_liste.eng_mm, ueber_rig.eng_mm, places=6)
        self.assertAlmostEqual(ueber_liste.median_mm, ueber_rig.median_mm,
                               places=6)
