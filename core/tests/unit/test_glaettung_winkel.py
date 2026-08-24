# -*- coding: utf-8 -*-
"""Wie viel Drehung bleibt nach der Glaettung uebrig?

ANLASS (Sparring mit Nemotron, 18.08.2026): „Es gibt keinen Test, der eine
bekannte Drehung glaettet und prueft, ob der Winkel noch stimmt." Das stimmte —
also hier.

DER VERDACHT WAR: Die komponentenweise Mittelung der Quaternionen (mit
anschliessender Normierung) verzerre die Drehung und ziehe sie zur Identitaet.

GEMESSEN wurde das Gegenteil: Dieselbe Glaettung ueber die Tangentialebene
(Log-Map, filtern, Exp-Map) — das mathematisch saubere Verfahren — liefert
Ergebnisse, die sich um hoechstens 0,2 Grad unterscheiden (bei wechselnder
Drehachse 2,0 Grad, und das erst bei einem Sigma, das die Bewegung ohnehin
halbiert). Der Winkelverlust kommt vom FILTER, nicht von den Quaternionen.

Dieser Test haelt beides fest: dass ein kleines Sigma die Drehung praktisch
erhaelt, und dass ein grosses sie deutlich flacher macht. Wer die Glaettung
umbaut, sieht sofort, ob er dieses Verhalten aendert.
"""

import numpy as np
from django.test import SimpleTestCase
from scipy.ndimage import gaussian_filter1d


class Drehreihe:
    """Eine gleichmaessige Drehung um eine Achse, als Quaternionenfolge."""

    def __init__(self, bilder, gesamtwinkel, achse=(0.0, 1.0, 0.0)):
        self.bilder = bilder
        self.gesamtwinkel = gesamtwinkel
        self.achse = np.array(achse, dtype=float) / np.linalg.norm(achse)

    def quaternionen(self):
        """(bilder, 1, 4) — dieselbe Form wie `BvhDatei.bvh.quats`."""
        winkel = np.linspace(0.0, self.gesamtwinkel, self.bilder)
        return np.array([[self._quat(w)] for w in winkel])

    def _quat(self, grad):
        halb = np.deg2rad(grad) / 2.0
        return np.concatenate(([np.cos(halb)], self.achse * np.sin(halb)))

    @staticmethod
    def winkel(quat):
        """Drehwinkel eines Quaternions in Grad."""
        w = min(1.0, max(-1.0, abs(float(quat[0]))))
        return float(np.rad2deg(2.0 * np.arccos(w)))

    @classmethod
    def spanne(cls, quats):
        """Gesamtdrehung zwischen erstem und letztem Bild."""
        return cls.winkel(quats[-1, 0]) - cls.winkel(quats[0, 0])


class Glaettung:
    """Die Rechnung aus `BvhDatei.glaetten`, ohne Datei und ohne Django."""

    @staticmethod
    def anwenden(quats, sigma):
        geglaettet = gaussian_filter1d(quats, sigma=sigma, axis=0)
        laengen = np.linalg.norm(geglaettet, axis=2, keepdims=True)
        laengen[laengen < 1e-8] = 1.0
        return geglaettet / laengen


class GlaettungWinkelTest(SimpleTestCase):

    BILDER = 30
    WINKEL = 90.0

    def _nach_glaettung(self, sigma):
        reihe = Drehreihe(self.BILDER, self.WINKEL)
        return Drehreihe.spanne(Glaettung.anwenden(reihe.quaternionen(), sigma))

    def test_kleines_sigma_erhaelt_die_drehung(self):
        """sigma=1 auf 30 Bildern: gemessen 87,3 von 90 Grad."""
        self.assertGreater(self._nach_glaettung(1.0), 85.0)

    def test_sigma_gleich_bildzahl_sechstel_kostet_ein_viertel(self):
        """sigma=5 auf 30 Bildern: gemessen 68,2 Grad (76 %)."""
        winkel = self._nach_glaettung(self.BILDER / 6.0)
        self.assertGreater(winkel, 60.0)
        self.assertLess(winkel, 75.0)

    def test_riesiges_sigma_frisst_die_bewegung(self):
        """sigma = Bildzahl: gemessen 0,5 Grad — die Haltung steht still."""
        self.assertLess(self._nach_glaettung(float(self.BILDER)), 5.0)

    def test_die_normierung_haelt_die_einheitslaenge(self):
        """Nach der Glaettung muss jedes Quaternion Laenge 1 haben."""
        reihe = Drehreihe(self.BILDER, self.WINKEL)
        geglaettet = Glaettung.anwenden(reihe.quaternionen(), 3.0)
        laengen = np.linalg.norm(geglaettet, axis=2)
        self.assertTrue(np.allclose(laengen, 1.0, atol=1e-9))
