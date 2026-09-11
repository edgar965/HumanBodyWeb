# -*- coding: utf-8 -*-
u"""Kleidungsstuecke aus der Szene -> `.npz` -> `Figurnetze` (11.09.2026).

Der Weg hat drei stille Fallen, und jede hat hier einen Fall:

* DIE ACHSEN. Die Szene rechnet Y oben, der Filmlauf Z oben. Ein Paket,
  das ungedreht abgelegt wird, laege im Video flach am Boden — ohne
  Fehler, ohne Warnung. Gepruefter Punkt: Three (0,1; 1,2; −0,3) muss in
  Blender (0,1; 0,3; 1,2) ankommen.
* DIE KNOCHENNUMMERN. Die Nummer im Paket zeigt in die Liste DES PAKETS;
  die Spalte in `Figurnetze` folgt der Liste der FIGUR. Die beiden stehen
  hier absichtlich in verschiedener Reihenfolge — wer die Nummer
  durchreicht statt den Namen, bekommt die Gewichte am falschen Knochen
  und einen Test, der rot wird.
* DIE LAENGE. Ein Paket ohne Kopf ist nur ueber seine Laenge pruefbar.
  Ein Byte zu wenig oder ein Dreieck ausserhalb der Punkte muss abbrechen,
  nicht stumm Unsinn lesen.

Sabotage-Gegenprobe gemacht: Drehung entfernt -> `test_achsen` rot;
Umsetzung ueber die Nummer statt den Namen -> `test_gewichte` rot.
"""
import os
import sys

import numpy as np
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from core.dienste.figurvideostuecke import Figurvideostuecke
from ._pruefablage import Pruefablage

MODELPHYSIK = os.path.join(str(settings.BASE_DIR), 'TheatreJS', 'ModelPhysik')

#: Die Knochenliste des PAKETS (Reihenfolge der Szene) …
PAKET_KNOCHEN = ['DEF-spine', 'DEF-thigh.L', 'DEF-shin.L', 'DEF-foot.L']


class _Figur:
    u"""… und die der FIGUR — absichtlich anders sortiert."""
    knochen = {'DEF-foot.L': {}, 'DEF-shin.L': {}, 'DEF-spine': {},
               'DEF-thigh.L': {}, 'DEF-hand.L': {}}


def _paket(punkte, dreiecke, nummern, gewichte):
    return (np.asarray(punkte, np.float32).tobytes()
            + np.asarray(dreiecke, np.uint32).tobytes()
            + np.asarray(nummern, np.uint16).tobytes()
            + np.asarray(gewichte, np.float32).tobytes())


PUNKTE = [[0.1, 1.2, -0.3], [0.2, 1.0, 0.0], [-0.1, 0.9, 0.2]]
DREIECKE = [[0, 1, 2]]
NUMMERN = [[1, 2, 0, 0], [3, 0, 0, 0], [2, 3, 0, 0]]
GEWICHTE = [[0.75, 0.25, 0, 0], [1.0, 0, 0, 0], [0.5, 0.5, 0, 0]]


class FigurvideostueckeTest(SimpleTestCase):

    databases = []

    def _ablegen(self, ordner, paket=None, knochen=PAKET_KNOCHEN, **meta):
        roh = paket if paket is not None else _paket(PUNKTE, DREIECKE,
                                                     NUMMERN, GEWICHTE)
        eintrag = {'name': 'Hose', 'farbe': '#ff8000', 'punkte': 3,
                   'dreiecke': 1, 'datei': 'stueck_0'}
        eintrag.update(meta)
        dateien = {'stueck_0': SimpleUploadedFile('stueck_0.bin', roh)}
        return Figurvideostuecke.ablegen(dateien, [eintrag], knochen, ordner)

    def test_achsen(self):
        with Pruefablage.ordner('figurvideo_') as ordner:
            aus = self._ablegen(ordner)
            self.assertEqual(aus[0]['name'], 'Hose')
            self.assertEqual(aus[0]['farbe'], [1.0, 128 / 255.0, 0.0])
            daten = np.load(aus[0]['pfad'])
            np.testing.assert_allclose(daten['punkte'][0], [0.1, 0.3, 1.2],
                                       atol=1e-6)
            np.testing.assert_array_equal(daten['dreiecke'], DREIECKE)
            self.assertEqual(list(daten['knochen']), PAKET_KNOCHEN)

    def test_gewichte(self):
        u"""Ueber den NAMEN umgesetzt, nicht ueber die Nummer."""
        if MODELPHYSIK not in sys.path:
            sys.path.insert(0, MODELPHYSIK)
        from figurnetze import Figurnetze
        with Pruefablage.ordner('figurvideo_') as ordner:
            aus = self._ablegen(ordner)
            netze = Figurnetze(_Figur())
            punkte, dreiecke, gewichte = netze.stueck(aus[0]['pfad'])
        self.assertEqual(punkte.shape, (3, 3))
        self.assertEqual(gewichte.shape, (3, 5))
        spalte = netze.spalte
        # Punkt 0: 0,75 auf DEF-thigh.L (Paketnummer 1), 0,25 auf DEF-shin.L.
        self.assertAlmostEqual(gewichte[0, spalte['DEF-thigh.L']], 0.75)
        self.assertAlmostEqual(gewichte[0, spalte['DEF-shin.L']], 0.25)
        # Punkt 1: ganz auf DEF-foot.L (Paketnummer 3 — Figurspalte 0).
        self.assertAlmostEqual(gewichte[1, spalte['DEF-foot.L']], 1.0)
        self.assertAlmostEqual(gewichte[1, spalte['DEF-spine']], 0.0)
        np.testing.assert_allclose(gewichte.sum(axis=1), 1.0)

    def test_unbekannter_knochen_bricht_ab(self):
        if MODELPHYSIK not in sys.path:
            sys.path.insert(0, MODELPHYSIK)
        from figurnetze import Figurnetze
        knochen = list(PAKET_KNOCHEN)
        knochen[3] = 'DEF-fremd'
        with Pruefablage.ordner('figurvideo_') as ordner:
            aus = self._ablegen(ordner, knochen=knochen)
            with self.assertRaises(ValueError) as fehler:
                Figurnetze(_Figur()).stueck(aus[0]['pfad'])
        self.assertIn('DEF-fremd', str(fehler.exception))

    def test_falsche_laenge_bricht_ab(self):
        roh = _paket(PUNKTE, DREIECKE, NUMMERN, GEWICHTE)[:-1]
        with Pruefablage.ordner('figurvideo_') as ordner:
            with self.assertRaises(ValueError) as fehler:
                self._ablegen(ordner, paket=roh)
        self.assertIn('Bytes', str(fehler.exception))

    def test_dreieck_ausserhalb_bricht_ab(self):
        roh = _paket(PUNKTE, [[0, 1, 7]], NUMMERN, GEWICHTE)
        with Pruefablage.ordner('figurvideo_') as ordner:
            with self.assertRaises(ValueError):
                self._ablegen(ordner, paket=roh)

    def test_knochennummer_ohne_namen_bricht_ab(self):
        with Pruefablage.ordner('figurvideo_') as ordner:
            with self.assertRaises(ValueError) as fehler:
                self._ablegen(ordner, knochen=PAKET_KNOCHEN[:3])
        self.assertIn('Knochennummer', str(fehler.exception))

    def test_fehlende_datei_bricht_ab(self):
        with Pruefablage.ordner('figurvideo_') as ordner:
            with self.assertRaises(ValueError) as fehler:
                Figurvideostuecke.ablegen({}, [{'name': 'Hose',
                                                'datei': 'stueck_9'}],
                                          PAKET_KNOCHEN, ordner)
        self.assertIn('ohne Daten', str(fehler.exception))

    def test_ohne_stuecke_nichts(self):
        self.assertEqual(Figurvideostuecke.ablegen({}, [], [], 'nirgends'), [])

    def test_farbe(self):
        self.assertEqual(Figurvideostuecke.farbe(None), Figurvideostuecke.FARBE)
        self.assertEqual(Figurvideostuecke.farbe('#000000'), [0.0, 0.0, 0.0])
        self.assertEqual(Figurvideostuecke.farbe('xyz'), Figurvideostuecke.FARBE)
