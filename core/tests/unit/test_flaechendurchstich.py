# -*- coding: utf-8 -*-
u"""`Flaechendurchstich`: Haut, die zwischen den Stoffpunkten durch ein Dreieck sticht, hebt
das Dreieck (24.09.2026, Edgar mit Bild: „garment code Ballerinas noch mit Haut"; die Zehen
standen bis 11,6 mm vor der Schuhflaeche, obwohl nur 14 von 1.045 Schuhpunkten unter der
Haut lagen).

Kunstdaten: Die Haut ist die Ebene z = 0 (1-mm-Raster, Normale +z) mit einer „Zehe", einer
Kuppe von 8 mm Hoehe und 3 mm Radius. Der Stoff ist ein 10-mm-Raster 3 mm ueber der Ebene,
nach +z gewickelt. Die Zehe steht in der MITTE eines Dreiecks, kein Stoffpunkt liegt ueber ihr.

    1. Ein Flaechenschritt hebt das Dreieck ueber der Zehe um mindestens `soll` darueber;
       `anwenden` (mit Punktmessung, Glaettung, Deckel) ebenso.
    2. Eine Sohle UNTER offener Haut (von der Haut weg gewickelt) bewegt sich nicht (Probe:
       ohne diese Bedingung wanderten Sohlenecken der Ballerina 58 mm).
    3. Ein umgekehrt gewickeltes Stueck wird genauso gehoben (Wicklung aus dem Median).

Sabotagen: `_versatz_flaechen` gibt Nullen -> 1 und 3 rot; `_zugewandt` ohne Vorzeichen
(`np.abs`) -> 2 rot; `_zugewandt` ohne Median-Umkehr -> 3 rot.
"""
import numpy as np
from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from GarmentCode.stoffkorrektur import Stoffkorrektur  # noqa: E402

ZEHE = np.array([0.0067, 0.0033])      # Schwerpunkt des Stoffdreiecks (0,0)-(1,0)-(1,1) cm
HOEHE, RADIUS = 0.008, 0.003


def haut():
    u"""`(punkte, normalen)`: Ebene (1-mm-Raster) mit einer flachen Zehenkuppe: Punkte binnen
    `RADIUS` um `ZEHE` auf `HOEHE`, alle Normalen +z. So ist die richtige Antwort ausrechenbar:
    die Flaeche muss ueber der Kuppe um `soll` hoeher liegen, senkrecht."""
    achse = np.arange(-0.03, 0.0301, 0.001)
    x, y = np.meshgrid(achse, achse)
    x, y = x.ravel(), y.ravel()
    z = np.where((x - ZEHE[0]) ** 2 + (y - ZEHE[1]) ** 2 < RADIUS ** 2, HOEHE, 0.0)
    return np.column_stack([x, y, z]), np.tile([0.0, 0.0, 1.0], (len(x), 1))


def raster(z, umgekehrt=False, versatz=0, x_bis=0.03):
    u"""10-mm-Raster auf Hoehe `z` (x bis `x_bis`), gewickelt nach +z (`umgekehrt`: nach −z)."""
    achse = np.arange(-0.03, 0.0301, 0.01)
    spalten = achse[achse <= x_bis + 1e-9]
    n, m = len(spalten), len(achse)
    punkte = np.array([[a, b, z] for b in achse for a in spalten])
    dreiecke = []
    for j in range(m - 1):
        for i in range(n - 1):
            a, b, c, d = j * n + i, j * n + i + 1, (j + 1) * n + i, (j + 1) * n + i + 1
            dreiecke += [[a, b, d], [a, d, c]]
    dreiecke = np.array(dreiecke) + versatz
    return punkte, (dreiecke[:, ::-1] if umgekehrt else dreiecke)


def flaeche_ueber_zehe(punkte, dreiecke):
    u"""Hoehe der Stoffflaeche senkrecht ueber der Zehenspitze (Dreieck, das sie ueberdeckt)."""
    for t in dreiecke:
        a, b, c = punkte[t]
        m = np.array([[b[0] - a[0], c[0] - a[0]], [b[1] - a[1], c[1] - a[1]]])
        v, w = np.linalg.solve(m, ZEHE - a[:2])
        if v >= 0 and w >= 0 and v + w <= 1 and abs(a[2]) < 0.05 and a[2] > -0.001:
            return a[2] + v * (b[2] - a[2]) + w * (c[2] - a[2])
    return None


class DerFlaechendurchstich(SimpleTestCase):
    databases = set()

    def _korrektur(self, dreiecke):
        punkte, normalen = haut()
        return Stoffkorrektur(punkte, normalen, dreiecke)

    def test_1_die_zehe_hebt_das_dreieck(self):
        stoff, dreiecke = raster(0.003)
        self.assertLess(flaeche_ueber_zehe(stoff, dreiecke), HOEHE)        # die Zehe sticht durch
        korrektur = self._korrektur(dreiecke)
        versatz = korrektur._versatz_flaechen(stoff, 0.001)
        self.assertGreaterEqual(flaeche_ueber_zehe(stoff + versatz, dreiecke), HOEHE + 0.0009)
        neu, _ = korrektur.anwenden(stoff, abstand_mm=1.0)
        self.assertGreaterEqual(flaeche_ueber_zehe(neu, dreiecke), HOEHE + 0.0009)

    def test_2_die_sohle_unter_offener_haut_bleibt(self):
        u"""Das Oberteil deckt nur x ≤ 1 cm (dahinter die „Einstiegsoeffnung"), die Sohle alles.
        Die Haut ueber der Oeffnung hat nur die Sohle unter sich; die zeigt von ihr weg."""
        oben, d_oben = raster(0.003, x_bis=0.01)
        sohle, d_sohle = raster(-0.006, umgekehrt=True, versatz=len(oben))
        stoff, dreiecke = np.vstack([oben, sohle]), np.vstack([d_oben, d_sohle])
        # Nur der Flaechenschritt: Die Punktmessung schoebe die Sohle als „eingesunken"
        # heraus. Hier liegt sie unter einer Haut ohne Gegenseite, am Fuss unter der Sohlenhaut.
        versatz = self._korrektur(dreiecke)._versatz_flaechen(stoff, 0.001)
        self.assertEqual(np.abs(versatz[len(oben):]).max(), 0.0)
        self.assertGreater(np.abs(versatz[: len(oben)]).max(), 0.004)   # die Zehe hebt oben

    def test_3_umgekehrt_gewickelt_wird_genauso_gehoben(self):
        stoff, dreiecke = raster(0.003, umgekehrt=True)
        versatz = self._korrektur(dreiecke)._versatz_flaechen(stoff, 0.001)
        self.assertGreaterEqual(flaeche_ueber_zehe(stoff + versatz, dreiecke), HOEHE + 0.0009)
