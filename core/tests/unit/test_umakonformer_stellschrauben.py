# -*- coding: utf-8 -*-
u"""Jede Einstellung des Konformers muss WIRKEN.

Probe aus der Abdeckungstabelle (`UMA_Python/abdeckung.py`); die
Tabelle nennt jede Testmethode hier beim Namen, `test_umaabdeckung_
tabelle` haelt das. Herausgeloest aus `test_umaabdeckung` (12.09.2026).
"""
import unittest

import numpy as np

from ._umaabdeckung import (Einstellungen, Glaettung, Kleidungskonformer,
                            Nahtgruppen, Netzgeometrie)
from .test_umakonformer import zylinder


class Stellschrauben(unittest.TestCase):
    u"""Jede Einstellung muss WIRKEN — eine, die nichts tut, ist die
    stillste Sorte Fehler."""

    databases = set()

    def setUp(self):
        self.koerper, self.k_tri = zylinder(0.20)
        self.stoff, self.s_tri = zylinder(0.21, ringe=18, stufen=12)

    def _binden(self, **abweichungen):
        e = Einstellungen(**abweichungen)
        k = Kleidungskonformer(self.koerper, self.k_tri, e)
        return k, k.binden('huelle', self.stoff, self.s_tri)

    def test_suchradius_begrenzt_die_bindung(self):
        u"""`maxSearchRadius`. Mit 1 mm findet kein Punkt mehr eine Fläche
        — mit 20 cm alle."""
        _, weit = self._binden(suchradius_m=0.2)
        _, eng = self._binden(suchradius_m=0.001, hoechstabstand_m=0.001)
        self.assertEqual(int(weit.gebunden.sum()), weit.punktzahl)
        self.assertLess(int(eng.gebunden.sum()), weit.punktzahl)

    def test_abstandsschwelle_entscheidet_ueber_die_kollision(self):
        u"""`normalOffsetEpsilon`: Ab welchem Abstand ein Punkt als „auf
        der Fläche" gilt. Wird sie grösser als der Stoffabstand, gilt der
        ganze Stoff als aufliegend."""
        k, b = self._binden(abstandsschwelle_m=0.001)
        eng = k.anwenden(b)
        k2 = Kleidungskonformer(self.koerper, self.k_tri,
                                Einstellungen(abstandsschwelle_m=0.05))
        b2 = k2.binden('huelle', self.stoff, self.s_tri)
        weit = k2.anwenden(b2)
        self.assertGreater(float(np.abs(eng - weit).max()), 1e-6,
                           u'Die Schwelle wirkt gar nicht')

    def _mit_glaettung(self, beheben, deckel=0.05):
        u"""Ein gezackter Stoff, stark geglättet — der Fall, in dem die
        Kollisionsbehebung ÜBERHAUPT etwas tut.

        GEMESSEN AM 08.09.2026, und das ist der Lehrsatz: Ohne
        Glättung feuert sie NIE. `binden` merkt sich je Punkt seinen
        Abstand zur Fläche, und `anwenden` stellt genau den wieder her
        — einsinken kann dabei nichts. Ein Test, der den Punkt vorher
        eindrückt oder den Körper weitet, misst mit und ohne Behebung
        denselben Wert (0,30949623684534955 gegen sich selbst).

        Erst die Glättung zieht Punkte von der Fläche weg — deshalb
        steht die Behebung in `anwenden` DANACH ein zweites Mal.
        """
        rau = self.stoff.copy()
        rau[::3] *= 1.10
        e = Einstellungen(kollision_beheben=beheben, glaetten=True,
                          glaettungsverfahren='laplace',
                          glaettungsdurchgaenge=20,
                          glaettungsstaerke=1.0, schub_deckel_m=deckel,
                          naehte_halten=False, tangential_halten=False)
        k = Kleidungskonformer(self.koerper, self.k_tri, e)
        ergebnis = k.anwenden(k.binden('huelle', rau, self.s_tri))
        return float(np.hypot(ergebnis[:, 0], ergebnis[:, 2]).min())

    def test_ohne_kollisionsbehebung_bleibt_der_punkt_drin(self):
        u"""`enableCollisionCorrection`. Gemessen: kleinster Radius
        0,101 ohne, 0,151 mit Behebung — bei einem Körperradius von
        0,20. Ohne sie steckt der geglättete Stoff im Körper."""
        self.assertGreater(self._mit_glaettung(True),
                           self._mit_glaettung(False) + 0.01,
                           u'Mit Behebung muss der Stoff deutlich weiter '
                           u'draussen liegen')

    def test_der_schub_ist_gedeckelt(self):
        u"""`maxCollisionDisplacement`. Ohne Deckel wanderte am
        06.09.2026 ein Kragenpunkt 123,65 mm — weil die ZÄHNE im Kopf
        in seinen Umkreis fielen.

        Gemessen wird der WEITESTE Punkt: Der Deckel greift je Punkt,
        und ein Mittelwert verdünnt ihn zu Unkenntlichkeit.
        """
        eng = self._mit_glaettung(True, deckel=0.002)
        weit = self._mit_glaettung(True, deckel=0.05)
        ohne = self._mit_glaettung(False)
        self.assertGreater(weit, eng,
                           u'Ein grösserer Deckel muss mehr herausholen')
        self.assertGreater(eng, ohne,
                           u'Auch ein kleiner Deckel muss etwas tun')

    def test_glaettung_laesst_sich_abschalten(self):
        u"""`enableSmoothing`."""
        rau = self.stoff.copy()
        rau[::3] += np.array([0.0, 0.004, 0.0])
        ergebnisse = {}
        for an in (True, False):
            e = Einstellungen(glaetten=an, naehte_halten=False)
            k = Kleidungskonformer(self.koerper, self.k_tri, e)
            ergebnisse[an] = k.anwenden(k.binden('h', rau, self.s_tri))
        self.assertGreater(float(np.abs(ergebnisse[True]
                                        - ergebnisse[False]).max()), 1e-6)

    def test_mehr_durchgaenge_glaetten_staerker(self):
        u"""`smoothingIterations`: Die Rauheit muss mit der Zahl der
        Durchgänge fallen — sonst ist die Schleife wirkungslos."""
        punkte, dreiecke = zylinder(0.2, ringe=16, stufen=8)
        rau = punkte.copy()
        rau[::2] *= 1.02
        starts, nachbarn = Netzgeometrie.nachbarschaft(len(punkte),
                                                       dreiecke)
        # GEMESSEN WIRD DIE RAUHEIT, nicht der Abstand zum Ausgangsnetz
        # und nicht die Streuung der Radien. Laplace SCHRUMPFT (sein
        # bekannter Nachteil), deshalb wächst der Abstand zum Original
        # mit jedem Durchgang, während die Rauheit fällt — zwei
        # gegenläufige Grössen, und nur eine davon ist gemeint.
        # Rauheit hier: der Abstand jedes Punktes zum Mittel seiner
        # Nachbarn. Genau das verkleinert eine Glättung.

        def rauheit(v):
            anzahl = np.diff(starts)
            summe = np.add.reduceat(v[nachbarn], starts[:-1], axis=0)
            mittel = summe / np.maximum(anzahl, 1)[:, None]
            return float(np.linalg.norm(v - mittel, axis=1).mean())

        werte = []
        for durchgaenge in (1, 4, 16):
            g = Glaettung.glaetten(rau, (starts, nachbarn), 'laplace',
                                   durchgaenge=durchgaenge, staerke=0.5)
            werte.append(rauheit(g))
        self.assertLess(werte[1], werte[0])
        self.assertLess(werte[2], werte[1])

    def test_staerke_null_bewegt_nichts(self):
        u"""`smoothingStrength = 0`. Die schärfste Probe auf die
        Parameterkette: Kommt hier etwas anderes heraus als die Eingabe,
        ist irgendwo eine feste Zahl eingebaut."""
        punkte, dreiecke = zylinder(0.2, ringe=12, stufen=6)
        rau = punkte.copy()
        rau[::2] *= 1.02
        starts, nachbarn = Netzgeometrie.nachbarschaft(len(punkte), dreiecke)
        g = Glaettung.glaetten(rau, (starts, nachbarn), 'laplace',
                               durchgaenge=8, staerke=0.0)
        np.testing.assert_allclose(g, rau, atol=1e-12)

    def test_hc_alpha_zieht_zur_ausgangslage(self):
        u"""`hcAlpha` = 1 hält die Ausgangslage fest — das ist der ganze
        Sinn von HC (Vollmer/Mencl/Müller): Es zieht zurück, was Laplace
        weggezogen hat."""
        punkte, dreiecke = zylinder(0.2, ringe=16, stufen=8)
        rau = punkte.copy()
        rau[::2] *= 1.03
        starts, nachbarn = Netzgeometrie.nachbarschaft(len(punkte), dreiecke)
        weg = {}
        for alpha in (0.0, 1.0):
            g = Glaettung.glaetten(rau, (starts, nachbarn), 'hc',
                                   durchgaenge=8, staerke=0.5,
                                   alpha=alpha, beta=0.5)
            weg[alpha] = float(np.abs(np.linalg.norm(g, axis=1)
                                      - np.linalg.norm(rau, axis=1)).mean())
        self.assertLess(weg[1.0], weg[0.0],
                        u'alpha=1 muss näher an der Ausgangslage bleiben')

    def test_hc_beta_zieht_zu_den_nachbarn(self):
        u"""`hcBeta`: der Gegenspieler von alpha. Zwei verschiedene Werte
        müssen zwei verschiedene Ergebnisse liefern."""
        punkte, dreiecke = zylinder(0.2, ringe=16, stufen=8)
        rau = punkte.copy()
        rau[::2] *= 1.03
        starts, nachbarn = Netzgeometrie.nachbarschaft(len(punkte), dreiecke)
        a = Glaettung.glaetten(rau, (starts, nachbarn), 'hc', 8, 0.5,
                               alpha=0.5, beta=0.0)
        b = Glaettung.glaetten(rau, (starts, nachbarn), 'hc', 8, 0.5,
                               alpha=0.5, beta=1.0)
        self.assertGreater(float(np.abs(a - b).max()), 1e-6)

    def test_nahttoleranz_entscheidet_ueber_die_gruppe(self):
        u"""`weldedSeamTolerance`: Zwei Punkte an fast derselben Stelle
        gehören zusammen — aber nur, wenn die Toleranz sie erreicht."""
        punkte = np.array([[0.0, 0.0, 0.0], [1e-5, 0.0, 0.0],
                           [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        dreiecke = np.array([[0, 2, 3]])
        eng = Nahtgruppen.bauen(punkte, dreiecke, toleranz=1e-7)
        weit = Nahtgruppen.bauen(punkte, dreiecke, toleranz=1e-4)
        # −1 heisst „gehört zu keiner Gruppe" — zwei Punkte, die BEIDE
        # −1 tragen, sind NICHT zusammengefasst. Wer hier schlicht auf
        # Ungleichheit prüft, vergleicht −1 mit −1 und hält die
        # Toleranz für wirkungslos.
        self.assertEqual(int(eng[0]), -1,
                         u'1e-7 darf die beiden nicht zusammenfassen')
        self.assertEqual(int(eng[1]), -1)
        self.assertGreaterEqual(int(weit[0]), 0,
                                u'1e-4 muss sie zusammenfassen')
        self.assertEqual(int(weit[0]), int(weit[1]))
