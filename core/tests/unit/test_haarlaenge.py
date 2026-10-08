# -*- coding: utf-8 -*-
"""Länge des Herrenhaars (07.10.2026): `Haarlaenge` (unten/oben in cm, glatt dazwischen), Rezeptzeile `haar_laenge`, Optionen `iterationen.haar_laenge_*`, runde Haarlinie (`Haarlinie.rund`) — Kunstdaten, kein Render."""
from types import SimpleNamespace

import numpy as np
from core.dienste.haarlaenge import Haarlaenge
from core.dienste.haarlinie import Haarlinie
from core.dienste.iterationsoptionen import Iterationsoptionen
from django.test import SimpleTestCase
from Genesis9.modellmitkleidern import ModellMitKleidern


class DieLaenge(SimpleTestCase):
    def test_1_unten_bis_zur_unteren_hoehe_oben_ab_der_oberen_dazwischen_glatt(self):
        laenge = Haarlaenge(1.0, 5.0)
        unten, oben = Haarlaenge.HOEHEN
        self.assertAlmostEqual(float(laenge.laenge(unten - 40.0)), 0.010, places=6)        # Nacken: unten
        self.assertAlmostEqual(float(laenge.laenge(unten)), 0.010, places=6)
        self.assertAlmostEqual(float(laenge.laenge(oben)), 0.050, places=6)
        self.assertAlmostEqual(float(laenge.laenge(90.0)), 0.050, places=6)                # Kopfdecke: oben
        mitte = float(laenge.laenge(0.5 * (unten + oben)))
        self.assertAlmostEqual(mitte, 0.030, places=6)                                     # Hermite: in der Mitte genau das Mittel
        werte = laenge.laenge(np.linspace(unten, oben, 20))
        self.assertTrue((np.diff(werte) >= 0).all())

    def test_2_die_vorgabe_und_die_grenzen(self):
        self.assertTrue(Haarlaenge().ist_vorgabe())
        self.assertFalse(Haarlaenge(2.0, None).ist_vorgabe())
        eng, weit = Haarlaenge.GRENZE_CM
        gekappt = Haarlaenge(0.01, 99.0)
        self.assertEqual((gekappt.unten_cm, gekappt.oben_cm), (eng, weit))

    def test_3_die_dicke_folgt_der_laenge_bis_zur_grenze(self):
        lang = Haarlaenge(4.0, 4.0)
        self.assertTrue((lang.dickefaktor(np.array([-30.0, 20.0, 80.0])) == 1.0).all())      # ab `DICKE_AB_M` die volle Dicke der Hülle
        kurz = Haarlaenge(0.5, 0.5)
        self.assertTrue((kurz.dickefaktor(np.array([-30.0, 80.0])) >= Haarlaenge.DICKE_MIN).all())
        gestuft = Haarlaenge(0.8, 4.0).dickefaktor(np.array([-30.0, 80.0]))
        self.assertLess(float(gestuft[0]), float(gestuft[1]))                              # unten dünner als oben

    def test_4_aus_dem_rezept_des_modells(self):
        modell = ModellMitKleidern().haar_laenge(2.0, 6.5)
        self.assertEqual(modell.haltung_werte['haarlaenge'], {'unten': 2.0, 'oben': 6.5})
        laenge = Haarlaenge.aus_modell(modell)
        self.assertEqual((laenge.unten_cm, laenge.oben_cm), (2.0, 6.5))
        self.assertTrue(Haarlaenge.aus_modell(ModellMitKleidern()).ist_vorgabe())          # keine Zeile: Vorgabe
        self.assertEqual(ModellMitKleidern().haar_laenge(0.0, 50.0).haltung_werte['haarlaenge'], {'unten': 0.5, 'oben': 8.0})

    def test_5_die_optionen_des_auftrags(self):
        job = SimpleNamespace(optionen={'iterationen': {'haar_laenge_unten': 2.5, 'haar_laenge_oben': 99}})
        laenge = Iterationsoptionen.haarlaenge(job)
        self.assertEqual(laenge.unten_cm, 2.5)
        self.assertEqual(laenge.oben_cm, Haarlaenge.OBEN_CM)                               # außerhalb der Grenzen: Vorgabe
        self.assertTrue(Iterationsoptionen.haarlaenge(SimpleNamespace(optionen={})).ist_vorgabe())

    def test_6_die_fassung_aendert_sich_mit_der_laenge(self):
        self.assertNotEqual(Haarlaenge(1.0, 5.0).fingerabdruck(), Haarlaenge().fingerabdruck())


class DieRundeHaarlinie(SimpleTestCase):
    def test_1_eine_ecke_wird_zum_bogen(self):
        grob = np.zeros((36, 72), bool)
        grob[10:30, 10:50] = True                                                          # ein Rechteck aus 5°-Feldern: scharfe Ecken
        bereich, zelle = Haarlinie.rund(grob, None, np.zeros(3))
        self.assertEqual(bereich.shape, (36 * Haarlinie.FEIN, 72 * Haarlinie.FEIN))
        self.assertAlmostEqual(zelle, 180.0 / bereich.shape[0])
        z0, s0 = 10 * Haarlinie.FEIN, 10 * Haarlinie.FEIN                                  # die Ecke des Rechtecks auf dem Feinraster
        self.assertFalse(bool(bereich[z0, s0]))                                            # die Ecke selbst fällt weg …
        self.assertTrue(bool(bereich[z0 + 12, s0 + 12]))                                   # … die Mitte bleibt
        self.assertTrue(bool(bereich[20 * Haarlinie.FEIN, 30 * Haarlinie.FEIN]))

    def test_2_das_ohr_ist_eine_flaeche_um_seine_punkte(self):
        mitte = np.zeros(3)
        az, el = np.meshgrid(np.radians(np.arange(70.0, 111.0, 2.0)), np.radians(np.arange(-20.0, 21.0, 2.0)))       # ein Ohr: 40° × 40° um Azimut 90°, Höhenwinkel 0 (wie `_felder`: Azimut von +z nach +x)
        richtung = np.stack([np.cos(el) * np.sin(az), np.sin(el), np.cos(el) * np.cos(az)], axis=-1).reshape(-1, 3)
        netz = {'punkte': 0.1 * richtung, 'haut': {'knochen': ['l_ear'], 'index': np.zeros((len(richtung), 4), int), 'gewicht': np.tile([1.0, 0.0, 0.0, 0.0], (len(richtung), 1))}}
        grob = np.ones((36, 72), bool)
        bereich, _zelle = Haarlinie.rund(grob, netz, mitte)
        fein = Haarlinie.FEIN
        self.assertFalse(bool(bereich[18 * fein, 18 * fein]))                              # Azimut 90°, Höhe 0°: im Ohr kein Haar
        self.assertTrue(bool(bereich[18 * fein, 54 * fein]))                               # gegenüber (270°): Haar
