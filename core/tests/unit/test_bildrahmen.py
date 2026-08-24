# -*- coding: utf-8 -*-
"""Wächter für `Bildrahmen` — das Drahtformat der Foto-Rechtecke.

WARUM (17.08.2026): Dieselbe Min-Max-Rechnung stand DREIMAL im Projekt
(`Gesichtskontur._rahmen`, `Gesichtskontur` für die Landmarken,
`Silhouette.netz_rahmen`), zweimal davon mit dem Wörterbuch `{x, y, w, h}` im
Rumpf. Der Browser liest genau diese vier Schlüssel: `assistentenbild.js`
rechnet `rahmen.x + rahmen.w / 2`. Wer dort `width` schreibt, bekommt `NaN` und
ein unsichtbares Rechteck — ohne Fehler, ohne Meldung.

Deshalb prüft dieser Test nicht nur die Zahlen, sondern die SCHLÜSSEL.
"""

import numpy as np

from django.test import SimpleTestCase

from core.daten.bildrahmen import Bildrahmen


class BildrahmenTest(SimpleTestCase):

    def test_schluessel_sind_x_y_w_h(self):
        """Das Drahtformat für den Browser — `w`/`h`, nicht `width`/`height`."""
        rahmen = Bildrahmen.um([[0.0, 0.0], [4.0, 8.0]])
        self.assertEqual(sorted(rahmen.als_dict()), ['h', 'w', 'x', 'y'])

    def test_rechnet_die_ausdehnung(self):
        rahmen = Bildrahmen.um([[10.0, 20.0], [30.0, 50.0]])
        self.assertEqual(rahmen.als_dict(),
                         {'x': 10.0, 'y': 20.0, 'w': 20.0, 'h': 30.0})
        self.assertEqual(rahmen.mitte(), (20.0, 35.0))

    def test_nan_punkte_zaehlen_nicht(self):
        """Die Projektion einer Silhouette enthält Punkte hinter der Kamera als
        `NaN`. Ein einfaches `min()` machte daraus einen Rahmen aus `NaN` —
        genau davor schützt `Bildrahmen`."""
        punkte = np.array([[10.0, 20.0], [np.nan, 5.0], [30.0, 50.0]])
        self.assertEqual(Bildrahmen.um(punkte).als_dict(),
                         {'x': 10.0, 'y': 20.0, 'w': 20.0, 'h': 30.0})

    def test_ohne_brauchbaren_punkt_kein_rahmen(self):
        """`None` statt eines Rahmens aus `NaN`: Der Browser zeichnet dann
        nichts, statt ein Rechteck ohne Ausdehnung an Position `NaN`."""
        for punkte in (np.zeros((0, 2)),
                       np.full((3, 2), np.nan),
                       np.zeros((3, 1)),
                       np.zeros(3)):
            with self.subTest(form=getattr(punkte, 'shape', None)):
                self.assertIsNone(Bildrahmen.um(punkte))

    def test_liste_von_paaren_geht_auch(self):
        """`Gesichtskontur` baut die Landmarken als Liste, nicht als Array."""
        rahmen = Bildrahmen.um([[1, 2], [4, 6]])
        self.assertEqual(rahmen.als_dict(), {'x': 1.0, 'y': 2.0,
                                             'w': 3.0, 'h': 4.0})

    def test_werte_sind_immer_float(self):
        """JSON mag `numpy.float32` nicht — `float()` steht im Konstruktor."""
        rahmen = Bildrahmen.um(np.array([[1, 2], [4, 6]], dtype=np.float32))
        for wert in rahmen.als_dict().values():
            self.assertIsInstance(wert, float)
