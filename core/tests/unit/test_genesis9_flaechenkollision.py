# -*- coding: utf-8 -*-
u"""Stoffflaechen ueber durchstechende Haut (`G9flaechenkollision`) und Haut ohne Kollision (`G9stueckverdeckung.normalen_null`), 18.10.2026.

Edgar: „checke alle MakeHuman Assets ob sie alle fitten … auch alle GarmentCode Portierungen", dann „fixe alles". Zehen stachen durch den
Saum bodenlanger GC-Hosenbeine, ohne dass ein Stoffpunkt innen lag (GC Jumpsuit: 2.747 Hautpunkte an den Zehen, Median 5,6 mm vor dem Stoff).

Kunstdaten: ein ebenes Stoffstueck 4 x 4 cm (Gitter 5 x 5 Punkte) in z = 0, die Haut eine Ebene 1 cm dahinter (Normale +z) und EIN
Hautpunkt 5 mm VOR der Mitte des Stoffs — wie eine Zehe zwischen den Stoffpunkten.

1. Der Hautpunkt sticht durch (`treffer`); nach `hinaus` nicht mehr, die mittleren Stoffpunkte liegen mindestens 5 mm + `ABSTAND` vorn.
2. Ein Hautpunkt vor dem RAND des Stoffs zaehlt nicht (die Haut liegt hinter dem Saum) — nichts bewegt sich.
3. `frei` schliesst den Hautpunkt aus (die Haut, die ein MakeHuman-Stueck ausblendet): nichts bewegt sich.
4. `normalen_null`: die verdeckten Punkte haben Normale null, die anderen bleiben; passt die Maske nicht zur Haut, bleibt alles.
5. `G9verdeckungsrand.bedeckt`: Haut unter dem Stoff ja, 1 cm neben dessen Rand nein, durchstechende Haut vor dem Stoff ja (Strahl
   beginnt hinter der Haut). Sabotage: Strahl erst AN der Haut beginnen (`HINTER` = 0) -> dritter Punkt rot.

Sabotage: in `treffer` den Randausschluss (`innen`) weglassen -> Fall 2 rot; in `hinaus` die Richtung `n` durch die Hautnormale unter
dem Punkt ersetzen bleibt hier gruen (Ebene) — dafuer steht die Messung am GC Höschen im Docstring. Geschrieben 18.10.2026, nicht gelaufen.
"""
import numpy as np
from django.test import SimpleTestCase
from Genesis9.flaechenkollision import G9flaechenkollision
from Genesis9.kollision import G9kollision
from Genesis9.stueckverdeckung import G9stueckverdeckung
from Genesis9.verdeckungsrand import G9verdeckungsrand


def stoff():
    u"""(Punkte (25, 3), Vierecke) — Gitter 5 x 5 in z = 0 von -2 bis +2 cm."""
    achse = np.linspace(-0.02, 0.02, 5)
    punkte = np.array([[x, y, 0.0] for y in achse for x in achse])
    flaechen = [[j * 5 + i, j * 5 + i + 1, (j + 1) * 5 + i + 1, (j + 1) * 5 + i] for j in range(4) for i in range(4)]
    return punkte, flaechen


def haut(vorn):
    u"""Hautebene 1 cm hinter dem Stoff (Normale +z) plus die Punkte `vorn`."""
    achse = np.linspace(-0.05, 0.05, 21)
    ebene = np.array([[x, y, -0.01] for y in achse for x in achse])
    punkte = np.vstack([ebene, np.asarray(vorn, dtype=np.float64).reshape(-1, 3)])
    normalen = np.tile([0.0, 0.0, 1.0], (len(punkte), 1))
    return punkte, normalen, G9kollision.baum(punkte)


class G9flaechenkollisionTest(SimpleTestCase):

    def test_1_durchstich_in_der_flaeche_wird_gehoben(self):
        p, f = stoff()
        h, n, b = haut([[0.005, 0.005, 0.005]])
        dreiecke = G9flaechenkollision.dreiecke(f)
        self.assertEqual(len(G9flaechenkollision.treffer(p, dreiecke, h, n, b)[1]), 1)
        neu, bilanz = G9flaechenkollision.hinaus(p, f, h, n, b)
        self.assertEqual(bilanz['treffer_nachher'], 0)
        self.assertEqual(len(G9flaechenkollision.treffer(neu, dreiecke, h, n, b)[1]), 0)
        self.assertGreaterEqual(neu[12, 2], 0.005 + G9flaechenkollision.ABSTAND - 1e-9)

    def test_2_haut_vor_dem_rand_zaehlt_nicht(self):
        p, f = stoff()
        h, n, b = haut([[0.025, 0.0, 0.004]])              # 5 mm neben dem Rand bei x = 2 cm, 4 mm vor der Ebene
        neu, bilanz = G9flaechenkollision.hinaus(p, f, h, n, b)
        self.assertEqual(bilanz['treffer_vorher'], 0)
        np.testing.assert_array_equal(neu, p)

    def test_3_ausgeblendete_haut_hebt_nichts(self):
        p, f = stoff()
        h, n, b = haut([[0.005, 0.005, 0.005]])
        frei = np.ones(len(h), dtype=bool)
        frei[-1] = False
        neu, bilanz = G9flaechenkollision.hinaus(p, f, h, n, b, frei=frei)
        self.assertEqual(bilanz['bewegt'], 0)
        np.testing.assert_array_equal(neu, p)

    def test_4_normalen_null_nur_an_den_verdeckten(self):
        h, n, b = haut([[0.0, 0.0, 0.005]])
        verdeckt = np.zeros(len(h), dtype=bool)
        verdeckt[:3] = True
        _h, neu, _b = G9stueckverdeckung.normalen_null((h, n, b), verdeckt)
        np.testing.assert_array_equal(neu[:3], 0.0)
        np.testing.assert_array_equal(neu[3:], n[3:])
        unveraendert = G9stueckverdeckung.normalen_null((h, n, b), verdeckt[:-1])
        self.assertIs(unveraendert[1], n)

    def test_5_bedeckt_nur_wo_der_stoff_ueber_der_haut_liegt(self):
        u"""Unter dem Stoff ja, 1 cm neben seinem Rand nein (dort standen am GC Höschen Loecher), vor dem Stoff (durchstechend) ja."""
        p, f = stoff()
        p = p + np.array([0.0, 0.0, 0.01])                  # Stoff 1 cm vor der Haut in z = 0
        haut_p = np.array([[0.0, 0.0, 0.0], [0.03, 0.0, 0.0], [0.005, 0.005, 0.015]])
        n = np.tile([0.0, 0.0, 1.0], (3, 1))
        self.assertEqual(G9verdeckungsrand.bedeckt(p, f, haut_p, n).tolist(), [True, False, True])
