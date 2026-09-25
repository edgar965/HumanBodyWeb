# -*- coding: utf-8 -*-
u"""`Punktdurchstich._versatz_koerperseite` hebt nur Stoff, der der Haut ZUGEWANDT ist
(25.09.2026, Edgar: „Schuhe auf Ursula1 kaputt … voellig unfoermig, Haut kommt durch").
An der Zehe war der naechste Stoffpunkt oft einer der Sohle; entlang der Hautnormale gehoben,
wanderte er bis an den Deckel (15 mm) durch die Zehe (Ballerina auf Ursula1: Zehenhaut offen
nach oben 564 -> 0, groesster Hub 15,0 -> 6,6 mm, `ProjektTemp/gc_ueber_daz/schuh_ab_ursula.py`).

Kunstdaten wie `test_flaechendurchstich`: Haut = Ebene z = 0 mit Zehenkuppe (8 mm); das Oberteil
deckt nur x ≤ 1 cm, die Sohle liegt 6 mm unter der Haut und zeigt von ihr weg. Ueber der
„Oeffnung" (x ab 1,7 cm) ist ein Sohlenpunkt der naechste Stoffpunkt.

    1. Die Sohle bewegt sich nicht; die Kuppe unter dem Oberteil hebt es weiterhin (6 mm).
    2. Umgekehrt gewickelt dasselbe (Wicklung aus dem Median, `_zugewandt`).

Sabotage-Gegenprobe (noch nicht gelaufen): die Zeile `fehlt[cos < self.FLAECHEN_COS_MIN] = 0.0`
weg -> 1 und 2 rot (Sohle 7 mm gehoben); `_zugewandt` ohne Median-Umkehr -> 2 rot.
"""
import numpy as np
from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from GarmentCode.stoffkorrektur import Stoffkorrektur  # noqa: E402

from .test_flaechendurchstich import haut, raster  # noqa: E402


class DerPunktdurchstich(SimpleTestCase):
    databases = set()

    @staticmethod
    def versatz(umgekehrt):
        u"""(Versatz des Oberteils, Versatz der Sohle) aus dem Punktschritt allein."""
        oben, d_oben = raster(0.003, umgekehrt=umgekehrt, x_bis=0.01)
        sohle, d_sohle = raster(-0.006, umgekehrt=not umgekehrt, versatz=len(oben))
        punkte, normalen = haut()
        korrektur = Stoffkorrektur(punkte, normalen, np.vstack([d_oben, d_sohle]))
        versatz = korrektur._versatz_koerperseite(np.vstack([oben, sohle]), 0.001)
        return versatz[: len(oben)], versatz[len(oben):]

    def test_1_die_sohle_unter_der_haut_bleibt_die_kuppe_hebt_das_oberteil(self):
        oben, sohle = self.versatz(umgekehrt=False)
        self.assertEqual(np.abs(sohle).max(), 0.0)
        self.assertGreater(np.abs(oben).max(), 0.004)

    def test_2_umgekehrt_gewickelt_genauso(self):
        oben, sohle = self.versatz(umgekehrt=True)
        self.assertEqual(np.abs(sohle).max(), 0.0)
        self.assertGreater(np.abs(oben).max(), 0.004)
