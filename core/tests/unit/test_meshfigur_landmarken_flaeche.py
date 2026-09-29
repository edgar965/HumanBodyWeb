# -*- coding: utf-8 -*-
"""Gesichtspunkte auf der Netzfläche und fester Genitalregler in „Mesh to 3D" (29.09.2026) — Kunstdaten.

Edgar: „warum fehlt die Nase??" und „die Erkennung oder Erzeugung des männlichen Geschlechtsteils ist schlecht …
nicht so unförmig". Gemessen am Lauf 2026.09.29.15.42.36: 126 von 478 Gesichts-Landmarken des Körpernetzes lagen
mehr als 8 mm neben dessen Fläche (die Nasenspitze 17 mm davor, Damiras Kopfnetz: Median 1,4 mm), fast alle
Nasenregler standen an der Grenze — und `Hip Genital Bulge` auf 100 %, um die Beule der Shorts nachzuformen.

Alles an Kunstdaten (eine Ebene als Netz, keine Datenbank, keine GPU, keine Daz-Bibliothek).
NICHT gelaufen (Tests nur auf Ansage).
"""

import re
from pathlib import Path

import numpy as np
from django.test import SimpleTestCase

from core.dienste.meshfigurregler import Meshfigurregler

from ._wrappersuchpfad import WRAPPERS, Wrappersuchpfad

Wrappersuchpfad.setzen()

from meshfigur_landmarkenflaeche import Meshfigurlandmarkenflaeche  # noqa: E402

TOOLS = WRAPPERS.parents[1]


class Ebene:
    """Ein „Netz" aus Punkten auf der Ebene z = 0, 20 × 20 cm — nur `abtasten`, wie `Meshfigurscan`."""

    def abtasten(self, anzahl, zufall=0):
        z = np.random.default_rng(zufall)
        p = np.zeros((int(anzahl), 3))
        p[:, :2] = z.uniform(-0.1, 0.1, (int(anzahl), 2))
        return p, np.tile([0.0, 0.0, 1.0], (len(p), 1)), np.zeros(len(p), dtype=int), np.zeros((len(p), 3))


class Leer:
    def abtasten(self, anzahl, zufall=0):
        return np.zeros((0, 3)), np.zeros((0, 3)), np.zeros(0, dtype=int), np.zeros((0, 3))


class Klein(Meshfigurlandmarkenflaeche):
    PROBEN = 40_000  # 20 × 20 cm: gut 1 mm Abstand — genug für die 3-mm-Grenze


class LandmarkenAufDerFlaecheTest(SimpleTestCase):
    def test_nah_bleibt_mittel_wird_gelegt_weit_faellt_weg(self):
        punkte = np.array(
            [
                (0.00, 0.00, 0.001),  # 1 mm davor: liegt auf der Fläche
                (0.05, 0.02, 0.015),  # 15 mm davor (die Nasenspitze des Körpernetzes: 17 mm)
                (0.00, 0.05, 0.050),  # 50 mm davor: kein Nachbar der Fläche
                (np.nan, np.nan, np.nan),  # nie erkannt
            ]
        )
        neu, befund = Klein(Ebene()).anlegen(punkte)
        np.testing.assert_array_equal(neu[0], punkte[0])
        self.assertLess(abs(neu[1][2]), 0.002)
        self.assertLess(np.linalg.norm(neu[1][:2] - punkte[1][:2]), 0.003)
        self.assertTrue(np.isnan(neu[2]).all())
        self.assertTrue(np.isnan(neu[3]).all())
        self.assertEqual((befund['geprueft'], befund['unveraendert'], befund['auf_flaeche'], befund['verworfen']), (3, 1, 1, 1))

    def test_nach_dem_auflegen_liegt_kein_punkt_mehr_daneben(self):
        z = np.random.default_rng(3)
        punkte = np.column_stack([z.uniform(-0.08, 0.08, 60), z.uniform(-0.08, 0.08, 60), z.uniform(0.0, 0.025, 60)])
        neu, _ = Klein(Ebene()).anlegen(punkte)
        self.assertLess(np.abs(neu[:, 2]).max(), 0.004)  # Sabotage (nur `return punkte`): bis 25 mm

    def test_ohne_flaeche_bleibt_alles_stehen(self):
        punkte = np.array([(0.0, 0.0, 0.02), (0.0, 0.0, 0.0)])
        neu, _ = Klein(Leer()).anlegen(punkte)
        np.testing.assert_array_equal(neu, punkte)


class FesterGenitalreglerTest(SimpleTestCase):
    REGLER = 'body_bs_HipGenitalBulge'

    def test_maennliche_grundfigur_bekommt_den_vorgabewert(self):
        self.assertEqual(Meshfigurregler.festwerte({'basis': 'masculine'}), {self.REGLER: 0.3})

    def test_wert_folgt_der_option_und_bleibt_zwischen_0_und_1(self):
        self.assertEqual(Meshfigurregler.festwerte({'basis': 'masculine', 'genitalform': 60})[self.REGLER], 0.6)
        self.assertEqual(Meshfigurregler.festwerte({'basis': 'masculine', 'genitalform': 250})[self.REGLER], 1.0)
        self.assertEqual(Meshfigurregler.festwerte({'basis': 'masculine', 'genitalform': 0}), {})

    def test_andere_grundfiguren_bekommen_nichts(self):
        self.assertEqual(Meshfigurregler.festwerte({'basis': 'feminine'}), {})
        self.assertEqual(Meshfigurregler.festwerte({'basis': 'neutral'}), {})
        self.assertEqual(Meshfigurregler.festwerte({}), {})

    def test_die_kette_darf_den_regler_nicht_stellen(self):
        # Stufe 0 = gar nicht frei; ein gewöhnlicher Körperregler bleibt frei (Sabotage: ohne den Eintrag in `AUS` → 3).
        self.assertEqual(Meshfigurregler.stufe(self.REGLER, 'hueften', 'koerper'), 0)
        self.assertEqual(Meshfigurregler.stufe('body_bs_BodyMass', 'koerper', 'koerper'), 1)


class DoppelteKonstantenTest(SimpleTestCase):
    """Die Bereichsnummern stehen im Genesis9-Paket UND im Runner (python10 sieht das Paket nicht) — sie müssen gleich sein."""

    MUSTER = re.compile(r'HAUT, KOPFHAUT, FINGER, HAND, INNEN, OHR, ZEHEN, SCHRITT = ([0-9, ]+)')

    def _nummern(self, pfad):
        treffer = self.MUSTER.search(Path(pfad).read_text(encoding='utf-8'))
        self.assertIsNotNone(treffer, pfad)
        return treffer.group(1).strip()

    def test_bereichsnummern_stimmen_ueberein(self):
        a = self._nummern(TOOLS / 'Genesis9' / 'netzbereiche.py')
        b = self._nummern(WRAPPERS / 'meshfigur_abstand.py')
        self.assertEqual(a, b)
        self.assertEqual(a, '0, 1, 2, 3, 4, 5, 6, 7')

    def test_der_schritt_hat_ein_gewicht(self):
        text = (WRAPPERS / 'meshfigur_abstand.py').read_text(encoding='utf-8')
        self.assertIn('SCHRITT: 0.1', text)
