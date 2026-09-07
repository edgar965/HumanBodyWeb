# -*- coding: utf-8 -*-
u"""Die Panels liegen dort, wo GarmentCode sie hinlegt (07.09.2026).

WARUM DIESER TEST (Edgar: „der 2D button könnte das Schnittmuster gleich
aufs Modell tun, so wie die Online version")
=====================================================================
Drei Dinge koennen an der Platzierung still falsch sein — die
Euler-Reihenfolge, die Achsenlage und das Vorzeichen der 2D-y-Achse. Jede
davon ergibt ein Netz, das fuer sich plausibel aussieht und am falschen
Ort haengt. Im Bild faellt das erst auf, wenn man den Koerper daneben
haelt, und auch dann nur bei den Aermeln: Vorder- und Rueckteil sind
achsenparallel (Drehung 0) und sehen bei JEDER Reihenfolge richtig aus.

Die Gegenprobe ist billig, weil derselbe Lauf sein `*_boxmesh.obj`
mitbringt — dieselben Panels, vom Upstream platziert. Gemessen am T-Shirt
auf `mean_all`: fuenf der sechs Huellgrenzen stimmen auf 0,0 cm, die
sechste (Y oben) auf 0,41 cm. Der Rest ist die Rasterung des Boxmesh, das
ein Gitter INNERHALB der Kontur ist.

DER OHRSCHNITT SCHEITERT STUMM
==============================
Eine im Uhrzeigersinn angegebene Kontur liefert KEINE Dreiecke — nicht
falsche, sondern gar keine, und ein leeres Panel sieht aus wie ein
fehlendes. Deshalb steht die Umlaufrichtung hier mit beiden Vorzeichen.
"""
import os
import unittest

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.assets()

from GarmentCode.ohrschnitt import Ohrschnitt              # noqa: E402
from GarmentCode.schnittvorschau import Schnittvorschau     # noqa: E402


class OhrschnittTest(SimpleTestCase):

    databases = []

    QUADRAT = [[0, 0], [10, 0], [10, 10], [0, 10]]

    def test_ein_quadrat_wird_zu_zwei_dreiecken(self):
        dreiecke = Ohrschnitt(self.QUADRAT).dreiecke()
        self.assertEqual(len(dreiecke), 2)
        self.assertEqual(sorted(set(dreiecke.flatten())), [0, 1, 2, 3])

    def test_die_umlaufrichtung_ist_egal(self):
        u"""Die stille Falle: rueckwaerts kaeme sonst NICHTS heraus."""
        vorwaerts = Ohrschnitt(self.QUADRAT).dreiecke()
        rueckwaerts = Ohrschnitt(self.QUADRAT[::-1]).dreiecke()
        self.assertEqual(len(vorwaerts), len(rueckwaerts))
        self.assertGreater(len(rueckwaerts), 0)

    def test_die_flaeche_traegt_ihr_vorzeichen(self):
        self.assertAlmostEqual(Ohrschnitt(self.QUADRAT).flaeche(), 100.0)
        self.assertAlmostEqual(Ohrschnitt(self.QUADRAT[::-1]).flaeche(), -100.0)

    def test_eine_konkave_form_bleibt_vollstaendig(self):
        u"""L-Form: sechs Ecken, vier Dreiecke, und die Flaeche stimmt."""
        form = [[0, 0], [20, 0], [20, 10], [10, 10], [10, 20], [0, 20]]
        dreiecke = Ohrschnitt(form).dreiecke()
        self.assertEqual(len(dreiecke), 4)
        p = np.asarray(form, float)
        summe = sum(abs(np.cross(p[b] - p[a], p[c] - p[a])) / 2
                    for a, b, c in dreiecke)
        self.assertAlmostEqual(summe, 300.0, places=6)

    def test_zu_wenig_punkte_gibt_nichts(self):
        self.assertEqual(len(Ohrschnitt([[0, 0], [1, 1]]).dreiecke()), 0)


class SchnittvorschauTest(SimpleTestCase):

    databases = []

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ordner = os.path.join(str(settings.ASSETS_ROOT), 'GarmentCode',
                                  'ausgabe', 't-shirt_mean_all')
        cls.spez = os.path.join(cls.ordner,
                                't-shirt_mean_all_specification.json')
        if not os.path.isfile(cls.spez):
            raise unittest.SkipTest('kein Beispiellauf t-shirt_mean_all')

    def test_das_netz_traegt_alle_panels(self):
        netz = Schnittvorschau(self.spez).netz()
        self.assertEqual(len(netz['panels']), 8, 'T-Shirt hat 8 Panels')
        self.assertGreater(len(netz['punkte']), 100)
        self.assertGreater(len(netz['dreiecke']), 100)

    def test_die_lage_stimmt_mit_dem_upstream_ueberein(self):
        u"""Gegen das Boxmesh DESSELBEN Laufs — die eigentliche Probe."""
        vorschau = Schnittvorschau(self.spez)
        abweichung = vorschau.abweichung(
            os.path.join(self.ordner, 't-shirt_mean_all_boxmesh.obj'))
        self.assertIsNotNone(abweichung, 'kein Boxmesh zum Vergleichen')
        for achse in range(3):
            self.assertLess(abweichung['min_cm'][achse], 0.6,
                            'Untergrenze Achse %d: %s' % (achse, abweichung))
            self.assertLess(abweichung['max_cm'][achse], 0.6,
                            'Obergrenze Achse %d: %s' % (achse, abweichung))

    def test_eine_falsche_eulerreihenfolge_faellt_auf(self):
        u"""Gegenprobe: Der Test muss rot werden koennen.

        `Rx · Ry · Rz` statt `Rz · Ry · Rx` — bei achsenparallelen Panels
        identisch, an den Aermeln nicht.
        """
        soll = Schnittvorschau.drehmatrix([0, 30, 45])
        a, b, c = np.deg2rad([0, 30, 45])
        dy = np.array([[np.cos(b), 0, np.sin(b)], [0, 1, 0],
                       [-np.sin(b), 0, np.cos(b)]])
        dz = np.array([[np.cos(c), -np.sin(c), 0],
                       [np.sin(c), np.cos(c), 0], [0, 0, 1]])
        verdreht = dy @ dz
        self.assertFalse(np.allclose(soll, verdreht),
                         'Die Reihenfolge macht keinen Unterschied — dann '
                         'prueft der Vergleich oben nichts')

    def test_kurvenpunkte_liegen_in_kantenkoordinaten(self):
        u"""`rel_to_abs_2d`: x entlang der Kante, y senkrecht darauf.

        Wer die Kontrollpunkte fuer absolut haelt, bekommt Zacken.
        """
        punkt = Schnittvorschau._nach_absolut([0, 0], [10, 0], [0.5, 0.2])
        self.assertAlmostEqual(punkt[0], 5.0)
        self.assertAlmostEqual(punkt[1], 2.0)
        # Dieselbe relative Angabe an einer SENKRECHTEN Kante.
        punkt = Schnittvorschau._nach_absolut([0, 0], [0, 10], [0.5, 0.2])
        self.assertAlmostEqual(punkt[0], -2.0)
        self.assertAlmostEqual(punkt[1], 5.0)

    def test_eine_gerade_kante_bekommt_keine_zwischenpunkte(self):
        vorschau = Schnittvorschau({'pattern': {'panels': {}}})
        self.assertEqual(vorschau._kurvenpunkte([0, 0], [1, 0], None), [])

    def test_die_kontur_loest_kurven_auf(self):
        u"""Mehr Punkte als Ecken — sonst sind die Rundungen Kanten."""
        vorschau = Schnittvorschau(self.spez)
        panels = vorschau.daten['pattern']['panels']
        name = next(n for n, p in panels.items()
                    if any(k.get('curvature') for k in p['edges']))
        kontur = vorschau.kontur(panels[name])
        self.assertGreater(len(kontur), len(panels[name]['vertices']))
