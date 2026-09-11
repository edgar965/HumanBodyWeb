# -*- coding: utf-8 -*-
u"""Ein Slipper sieht aus wie ein Slipper — gemessen am simulierten Netz.

WARUM (11.09.2026, Edgar: „slipper sehen ja noch echte sehr schlecht aus.
Mach dir einen testcase, die sollen wie slipper und nicht wie ein
schmetterling ausschauen")
======================================================================
Der Schmetterling: Die Seitenteile standen wie Flügel vom Fuss ab, weil
der Einstieg so lang war wie die Sohle (49,9 cm) und nicht wie der Fuss
dort (38 cm) — und weil Leder mit Biegesteifigkeit 50.000 die Panels als
Kasten stehen liess. Gemessen am Slipper vor dem Umbau, rohes
Simulationsnetz (GarmentCode-Raum, Y oben, cm):

    Schuhbreite minus Fussbreite je Höhenscheibe   +6,5 cm auf 5 cm Höhe,
                                                   +10 cm auf 11 cm
    Einstiegsrand (Randkanten des Netzes) zur Haut  median 17,8 mm,
                                                   90 % 32,7 mm

Nach dem Umbau (`schuh/einstieg.py`, `fusseinstieg.py`,
`Schuhentwurf.HALBSCHUH_STEIFE`): +1,1 cm, median 6,7 mm, 90 % 11,8 mm.
Die Ballerina genauso (+1,1 / 6,8 / 11,0), die Vorgabe aus Leder (+1,0 /
6,5 / 13,4). Die Grenzen hier liegen zwischen beiden Zuständen.

Das Modul baut zwei Schuhe auf dem Produktivweg und simuliert sie (je
etwa 25 s auf CUDA) — deshalb Longrunner. Die Ergebnisse landen wie jeder
Bau unter `Assets/GarmentCode/ausgabe/pruef_<form>/`.
"""
import os
import unittest

import numpy as np


class Schuhmass:
    u"""Masse eines simulierten Schuhs gegen den Fuss der Figur."""

    def __init__(self, netz_obj, figurnetz):
        u"""`netz_obj`: das rohe `*_sim.obj` (GarmentCode-Raum, cm);
        `figurnetz`: die Figur in Projektlage (m, Z oben)."""
        self.punkte, self.dreiecke = self._obj(netz_obj)
        k = np.asarray(figurnetz, dtype=np.float64) * 100.0
        self.koerper = np.column_stack([k[:, 0], k[:, 2], -k[:, 1]])
        self.boden = float(self.koerper[:, 1].min())
        links = self.koerper[:, 0] > 0
        self.fuss = self.koerper[links & (self.koerper[:, 1] < self.boden + 20)]
        self.schuh = self.punkte[self.punkte[:, 0] > 0]

    @staticmethod
    def _obj(pfad):
        v, f = [], []
        with open(pfad, 'r', encoding='utf-8', errors='ignore') as datei:
            for zeile in datei:
                if zeile.startswith('v '):
                    v.append([float(x) for x in zeile.split()[1:4]])
                elif zeile.startswith('f '):
                    f.append([int(x.split('/')[0]) - 1 for x in zeile.split()[1:4]])
        return np.asarray(v, dtype=np.float64), np.asarray(f, dtype=np.int64)

    def ueberstand(self):
        u"""[(Höhe cm, Schuhbreite minus Fussbreite cm)] je 1-cm-Scheibe ab
        1 cm über dem Boden — die Sohle bleibt aussen vor."""
        aus = []
        for y in np.arange(1.0, self.schuh[:, 1].max(), 1.0):
            s = self.schuh[(self.schuh[:, 1] >= y) & (self.schuh[:, 1] < y + 1)]
            f = self.fuss[(self.fuss[:, 1] >= self.boden + y)
                          & (self.fuss[:, 1] < self.boden + y + 1)]
            if len(s) > 3 and len(f) > 3:
                aus.append((float(y), float((s[:, 0].max() - s[:, 0].min())
                                            - (f[:, 0].max() - f[:, 0].min()))))
        return aus

    def rand(self):
        u"""Die Randpunkte des linken Schuhs — Kanten mit nur einem
        Dreieck; am geschlossenen Schuh ist das der Einstieg."""
        zaehler = {}
        for a, b, c in self.dreiecke:
            for u, w in ((a, b), (b, c), (c, a)):
                kante = (min(u, w), max(u, w))
                zaehler[kante] = zaehler.get(kante, 0) + 1
        idx = sorted({i for kante, n in zaehler.items() if n == 1 for i in kante})
        idx = [i for i in idx if self.punkte[i, 0] > 0]
        return self.punkte[idx]

    def randabstand_mm(self):
        u"""(median, 90 %) des Abstands Einstiegsrand -> Haut, Millimeter."""
        from scipy.spatial import cKDTree
        abstand, _ = cKDTree(self.koerper).query(self.rand())
        return float(np.median(abstand)) * 10.0, float(np.quantile(abstand, 0.9)) * 10.0


class SchuhformTest(unittest.TestCase):

    databases = []

    FORMEN = ('slipper', 'ballerina')
    #: Schuhbreite minus Fussbreite, höchstens (cm) — Schmetterling +6,5.
    UEBERSTAND_CM = 2.5
    #: Einstiegsrand zur Haut, Median und 90 % (mm) — Schmetterling 17,8 / 32,7.
    RAND_MEDIAN_MM = 12.0
    RAND_90_MM = 20.0

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from GarmentCode.dienst import GarmentcodeDienst
        if not GarmentcodeDienst.drapierbereit():
            raise unittest.SkipTest('Simulationsumgebung fehlt')
        from GarmentCode.drapierdienst import Garmentdrapierung
        cls.figur = GarmentcodeDienst.figurnetz('female', None, None)
        cls.masse = {}
        for form in cls.FORMEN:
            ergebnis = GarmentcodeDienst.erzeugen(form, 'female', name='pruef_' + form)
            sim = Garmentdrapierung.lauf(GarmentcodeDienst.spezifikation(ergebnis),
                                         'female')
            if sim.get('abgestuerzt') or not os.path.isfile(sim.get('netz') or ''):
                raise AssertionError('%s: Simulation ohne Netz: %s' % (form, sim))
            cls.masse[form] = (Schuhmass(sim['netz'], cls.figur), sim)

    def test_der_schuh_ist_nirgends_viel_breiter_als_der_fuss(self):
        u"""Kein Flügel: in keiner Höhenscheibe über der Sohle steht der
        Schuh mehr als `UEBERSTAND_CM` über den Fuss hinaus."""
        for form in self.FORMEN:
            mass, _ = self.masse[form]
            scheiben = mass.ueberstand()
            self.assertGreaterEqual(len(scheiben), 3, form)
            hoehe, breitester = max(scheiben, key=lambda s: s[1])
            self.assertLessEqual(
                breitester, self.UEBERSTAND_CM,
                '%s: %+.1f cm breiter als der Fuss auf %.0f cm Höhe — %s'
                % (form, breitester, hoehe,
                   ' '.join('%.0f:%+.1f' % s for s in scheiben)))

    def test_der_einstiegsrand_liegt_am_fuss(self):
        for form in self.FORMEN:
            mass, _ = self.masse[form]
            median, neunzig = mass.randabstand_mm()
            self.assertLessEqual(median, self.RAND_MEDIAN_MM,
                                 '%s: Rand median %.1f mm' % (form, median))
            self.assertLessEqual(neunzig, self.RAND_90_MM,
                                 '%s: Rand 90 %% %.1f mm' % (form, neunzig))

    def test_die_simulation_kommt_zur_ruhe(self):
        u"""Ein Schuh, der am Fuss hält, ist nach wenigen hundert Bildern
        still (gemessen 73 und 114); 2.399 ist die Abbruchgrenze."""
        for form in self.FORMEN:
            _, sim = self.masse[form]
            self.assertFalse(sim.get('abgestuerzt'), form)
            self.assertLess(int(sim.get('fin_frame') or 0), 1000, form)
