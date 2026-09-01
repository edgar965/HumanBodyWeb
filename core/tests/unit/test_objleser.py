# -*- coding: utf-8 -*-
u"""`Objleser` — die OBJ-Dateien der SMPL-Kleiderbibliothek.

WARUM DIESER TEST EXISTIERT (01.09.2026)
----------------------------------------
Die Zerlegung stand als zwei Schleifen in `smpl_library/garment.py`
(312 Zeilen, eine Klasse mit elf Aufgaben) und rechnete die Normalen
Dreieck fuer Dreieck in Python. Beim Zusammenlegen sind drei Dinge
leicht zu verlieren, die man dem Ergebnis nicht ansieht:

* **Die Z-Achse.** SMPL liefert Z nach VORN, Three.js will Z nach
  hinten. Ohne Spiegelung steht das Kleidungsstueck hinter der Figur.
* **Die Einheit.** Zentimeter gegen Meter — Faktor 100.
* **Der Typ.** Three.js liest die Puffer roh; ein `float64` verdoppelt
  die Uebertragung, ein `int64` wird gar nicht angenommen.

Die Zenodo-Archive liegen nicht im Projekt, deshalb prueft dieser Test
an erfundenen OBJ-Texten.

Aufruf:  python manage.py test core.tests.unit.test_objleser
"""
import numpy as np
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from assetCreator.GarmentFitter.smpl_library.objleser import Objleser  # noqa: E402


class ObjleserTest(SimpleTestCase):
    u"""Zerlegung, Umrechnung und Normalen."""

    databases = []

    #: Zwei Dreiecke als ein Viereck, ein Punkt bei 100 cm.
    TEXT = '\n'.join([
        'v 0 0 0',
        'v 100 0 0',
        'v 100 100 0',
        'v 0 100 0',
        'f 1 2 3 4',
    ])

    def test_faecher_triangulierung(self):
        u"""Ein Viereck wird zu zwei Dreiecken — a-b-c und a-c-d."""
        leser = Objleser(self.TEXT)
        self.assertEqual(leser.dreiecke, [0, 1, 2, 0, 2, 3])

    def test_roh_bleibt_unveraendert(self):
        u"""`roh` rechnet NICHT um — Zentimeter bleiben Zentimeter."""
        roh = Objleser(self.TEXT).roh()
        self.assertEqual(roh['vertices'].dtype, np.float64)
        self.assertEqual(roh['faces'].dtype, np.uint32)
        self.assertEqual(roh['faces'].shape, (2, 3))
        self.assertAlmostEqual(float(roh['vertices'][1][0]), 100.0)

    def test_browser_meter_und_z_gespiegelt(self):
        u"""Zentimeter → Meter, Z nach hinten."""
        daten = Objleser('v 100 200 300\nf 1 1 1').fuer_browser()
        self.assertEqual(daten['vertices'].dtype, np.float32)
        np.testing.assert_allclose(daten['vertices'][:3], [1.0, 2.0, -3.0])

    def test_gelesene_normalen_werden_gespiegelt(self):
        u"""Steht `vn` in der Datei, wird nur die Z-Achse gedreht."""
        text = 'v 0 0 0\nv 1 0 0\nv 0 1 0\nvn 0 0 1\nvn 0 0 1\nvn 0 0 1\nf 1 2 3'
        daten = Objleser(text).fuer_browser()
        np.testing.assert_allclose(daten['normals'][:3], [0.0, 0.0, -1.0])

    def test_fehlende_normalen_werden_gerechnet(self):
        u"""Ohne `vn` entstehen sie aus den Flaechen — und sind normiert."""
        daten = Objleser(self.TEXT).fuer_browser()
        normalen = daten['normals'].reshape(-1, 3)
        self.assertEqual(len(normalen), 4)
        np.testing.assert_allclose(np.linalg.norm(normalen, axis=1),
                                   np.ones(4), atol=1e-6)

    def test_leerer_text_bricht_nicht(self):
        u"""Eine leere Datei liefert leere Felder, keinen Fehler."""
        daten = Objleser('').fuer_browser()
        self.assertEqual(daten['vertices'].size, 0)
        self.assertEqual(daten['faces'].size, 0)
        self.assertEqual(Objleser('').roh()['faces'].shape, (0, 3))

    def test_flaechen_mit_texturindex(self):
        u"""``f 1/2/3`` — nur der erste Wert ist der Punkt."""
        leser = Objleser('v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1/7/9 2/8/9 3/9/9')
        self.assertEqual(leser.dreiecke, [0, 1, 2])

    def test_normalen_summe_ist_die_der_flaechen(self):
        u"""Gegenprobe zur alten Schleife: dieselbe Rechnung, vektorisiert."""
        rng = np.random.default_rng(3)
        punkte = rng.normal(size=(30, 3)).astype(np.float32)
        felder = np.array([[i, (i + 1) % 30, (i + 2) % 30] for i in range(28)])
        erwartet = np.zeros_like(punkte)
        for f in felder:
            v0, v1, v2 = punkte[f[0]], punkte[f[1]], punkte[f[2]]
            fn = np.cross(v1 - v0, v2 - v0)
            for i in f:
                erwartet[i] += fn
        laengen = np.linalg.norm(erwartet, axis=1, keepdims=True)
        laengen[laengen == 0] = 1.0
        np.testing.assert_allclose(
            Objleser.normalen_rechnen(punkte, felder.ravel()),
            (erwartet / laengen).flatten(), atol=1e-6)
