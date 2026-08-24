# -*- coding: utf-8 -*-
"""Koerperhuelle — Nachbarschaft, Normalen, Aufblähen; mit gerechneten Zahlen.

WARUM (17.08.2026)
=================
`glatt` (68 Zeilen) baute die Nachbarschaftsmatrix in einer Python-Schleife über
alle Flächen und Eckenpaare — bei 17.288 Vierecken über 100.000 Einzelzuweisungen
in eine `lil_matrix`. Gemessen am weiblichen Grundkörper (18.210 Punkte), gleiche
Daten, gleiche Maschine:

    vorher   0,70 s / 0,65 s
    nachher  0,039 s / 0,038 s / 0,044 s

Die Ausgabe ist dieselbe (größter Abstand 2,65e-23 m — Rundung). Umbauten an
Geometrie sind aber genau die Sorte, bei der ein Vorzeichen unbemerkt kippt;
deshalb prüft dieser Test die Matrix und die Normalen an einem Netz, das man
nachrechnen kann.

DAS PRÜFNETZ
============
Ein Quadrat in der XY-Ebene, ein Viereck:

    0 (0,0,0)   1 (1,0,0)   2 (1,1,0)   3 (0,1,0)

* Nachbarschaft: In EINEM Viereck grenzt jede Ecke an jede andere (auch die
  Diagonale) — die alte Fassung tat das genauso. Jede Zeile hat also drei
  Einsen, und die Matrix ist symmetrisch.
* Normalen: Beide Dreiecke (0,1,2) und (0,2,3) laufen gegen den Uhrzeigersinn,
  das Kreuzprodukt zeigt in +Z. Aufblähen um 15 mm hebt alle Punkte um genau
  0,015 in Z.
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.koerperhuelle import Koerperhuelle


class Netz:
    PUNKTE = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0],
                       [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]])
    VIERECK = np.array([[0, 1, 2, 3]])


class HuelleDreieckeTest(SimpleTestCase):

    def test_viereck_wird_zu_zwei_dreiecken(self):
        dreiecke = Koerperhuelle.dreiecke(Netz.VIERECK)
        self.assertEqual(dreiecke.shape, (2, 3))
        self.assertEqual(list(dreiecke[0]), [0, 1, 2])
        self.assertEqual(list(dreiecke[1]), [0, 2, 3])

    def test_dreiecke_bleiben_wie_sie_sind(self):
        dreiecke = Koerperhuelle.dreiecke(np.array([[3, 4, 5]]))
        self.assertEqual(list(dreiecke[0]), [3, 4, 5])


class NachbarschaftTest(SimpleTestCase):

    def matrix(self):
        return Koerperhuelle._nachbarschaft(Netz.VIERECK, 4).toarray()

    def test_jede_ecke_hat_drei_nachbarn(self):
        self.assertEqual(list(self.matrix().sum(axis=1)), [3, 3, 3, 3])

    def test_matrix_ist_symmetrisch(self):
        matrix = self.matrix()
        self.assertTrue(np.array_equal(matrix, matrix.T))

    def test_geteilte_kanten_zaehlen_einmal(self):
        """Zwei Vierecke an einer Kante: Der Eintrag bleibt 1, nicht 2.

        Die alte Fassung SETZTE den Wert (`adj[i, j] = 1`), addierte nicht. Wer
        beim Vektorisieren addiert, gewichtet geteilte Kanten doppelt — die
        Glättung zieht dann in die falsche Richtung.
        """
        zwei = np.array([[0, 1, 2, 3], [1, 4, 5, 2]])
        matrix = Koerperhuelle._nachbarschaft(zwei, 6).toarray()
        self.assertEqual(matrix[1, 2], 1.0)
        self.assertEqual(sorted(set(matrix.flatten())), [0.0, 1.0])

    def test_keine_selbstverbindung(self):
        self.assertEqual(list(np.diag(self.matrix())), [0.0, 0.0, 0.0, 0.0])


class NormalenTest(SimpleTestCase):

    def test_flaechennormalen_zeigen_nach_z(self):
        normalen = Koerperhuelle._flaechennormalen(Netz.PUNKTE, Netz.VIERECK)
        for normale in normalen:
            self.assertAlmostEqual(normale[2], 1.0, places=6)

    def test_ohne_flaechen_radial_vom_schwerpunkt(self):
        punkte = np.array([[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]])
        normalen = Koerperhuelle._flaechennormalen(punkte, None)
        self.assertAlmostEqual(normalen[0][0], 1.0, places=6)
        self.assertAlmostEqual(normalen[1][0], -1.0, places=6)


class GlattTest(SimpleTestCase):

    def test_aufblaehen_hebt_um_die_angegebenen_millimeter(self):
        huelle = Koerperhuelle.glatt(Netz.PUNKTE, Netz.VIERECK,
                                     inflate_mm=15, smooth_iterations=0)
        for punkt in huelle:
            self.assertAlmostEqual(punkt[2], 0.015, places=6)

    def test_glaetten_zieht_zum_mittel(self):
        """Ein herausstehender Punkt wandert zu seinen Nachbarn."""
        punkte = Netz.PUNKTE.copy()
        punkte[0] = [0.0, 0.0, 1.0]
        huelle = Koerperhuelle.glatt(punkte, Netz.VIERECK, inflate_mm=0,
                                     smooth_iterations=5)
        self.assertLess(huelle[0][2], 1.0)

    def test_ohne_flaechen_wird_nur_aufgeblaeht(self):
        punkte = np.array([[1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]])
        huelle = Koerperhuelle.glatt(punkte, None, inflate_mm=10)
        self.assertAlmostEqual(huelle[0][0], 1.01, places=6)

    def test_die_eingabe_bleibt_unberuehrt(self):
        """`glatt` arbeitet auf einer Kopie — der Aufrufer zeichnet die Figur
        weiter mit denselben Punkten."""
        punkte = Netz.PUNKTE.copy()
        Koerperhuelle.glatt(punkte, Netz.VIERECK)
        self.assertTrue(np.array_equal(punkte, Netz.PUNKTE))


class HuelleEinpassenTest(SimpleTestCase):

    def test_umgebungsquader_wird_je_achse_angeglichen(self):
        """Ein Würfel von 1 wird auf einen Kasten 2×4×6 gestreckt."""
        quelle = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        ziel = np.array([[0.0, 0.0, 0.0], [2.0, 4.0, 6.0]])
        eingepasst = Koerperhuelle._einpassen(quelle, ziel)
        self.assertTrue(np.allclose(eingepasst[0], [0, 0, 0]))
        self.assertTrue(np.allclose(eingepasst[1], [2, 4, 6]))

    def test_flache_achse_wird_nicht_skaliert(self):
        """Alle Punkte auf einer Ebene: Die Achse hat Länge 0 — kein Teilen."""
        quelle = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 0.0]])
        ziel = np.array([[0.0, 0.0, 0.0], [2.0, 2.0, 5.0]])
        eingepasst = Koerperhuelle._einpassen(quelle, ziel)
        self.assertTrue(np.all(np.isfinite(eingepasst)))
        self.assertAlmostEqual(eingepasst[0][2], 2.5, places=6,
                              msg='nur verschoben, nicht gestreckt')
