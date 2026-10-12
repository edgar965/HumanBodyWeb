# -*- coding: utf-8 -*-
"""Dazgeograftbacken liest die Hautkachel auch ohne `.klein.jpg` (11.10.2026, „cute girl daz5").

Gesehen: bei `browser_px = 8192` (Vorgabe, keine Verkleinerung) gibt es keine `haut_<k>_<kanal>.klein.jpg`. `_kachelbild` gab dann `None`, `_hautwerte` füllte die Haut mit Grau (128) — das Daz-Stück bekam am Rand
und überall außerhalb des Originals ein graues Bild statt der Hautfarbe (gemessen am Bake: Farbbild Mittel 129 / 128 / 128). Kunstwelt: kleine einfarbige Kacheln in einem Ordner neben dieser Datei.

1. Nur die volle Kachel (`haut_1002_farbe.png`): sie wird gelesen, ihre Farbe kommt an.
2. Die volle Kachel ist größer als `KACHEL_MAX_PX`: sie wird mit `reduce` verkleinert (64 px → 16 px bei Grenze 16).
3. Gibt es `.klein.jpg`, gilt sie vor der vollen Kachel.
4. Gar keine Datei: `None` (der Aufrufer entscheidet; der Bake in `Dazgeograftverlegt` fragt vorher nach den Kacheln).

Nicht gelaufen (Stand 11.10.2026) — läuft nur auf Ansage. Sabotage-Gegenprobe NICHT gemacht (erst auf Ansage): vorgesehen ist `KACHEL_NAMEN` auf die `.klein.jpg` zu kürzen → Fälle 1 und 2 rot.
"""
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from PIL import Image

from core.dienste.dazgeograftbacken import Dazgeograftbacken


class DazgeograftbackenKachelTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory(dir=str(Path(__file__).parent))
        self.addCleanup(self.ordner.cleanup)

    def _bild(self, name, farbe, kante=64):
        Image.new('RGB', (kante, kante), farbe).save(Path(self.ordner.name) / name)

    def _backen(self):
        return Dazgeograftbacken(SimpleNamespace(netz=lambda: None), {}, Path(self.ordner.name))

    def test_1_die_volle_kachel_wird_gelesen(self):
        self._bild('haut_1002_farbe.png', (199, 143, 128))
        bild = self._backen()._kachelbild(1002, 'farbe')
        self.assertIsNotNone(bild, 'ohne .klein.jpg gilt die volle Kachel')
        self.assertEqual(tuple(bild[0, 0]), (199, 143, 128))

    def test_2_eine_grosse_kachel_wird_verkleinert(self):
        self._bild('haut_1002_farbe.png', (199, 143, 128), kante=64)
        with mock.patch.object(Dazgeograftbacken, 'KACHEL_MAX_PX', 16):
            bild = self._backen()._kachelbild(1002, 'farbe')
        self.assertEqual(bild.shape, (16, 16, 3))
        self.assertEqual(tuple(bild[0, 0]), (199, 143, 128))

    def test_3_die_verkleinerte_fassung_geht_vor(self):
        self._bild('haut_1002_farbe.png', (10, 10, 10))
        self._bild('haut_1002_farbe.klein.jpg', (200, 150, 130), kante=16)
        bild = self._backen()._kachelbild(1002, 'farbe')
        self.assertEqual(bild.shape[0], 16)
        np.testing.assert_allclose(bild[8, 8], (200, 150, 130), atol=4)

    def test_4_ohne_datei_gibt_es_kein_bild(self):
        self.assertIsNone(self._backen()._kachelbild(1002, 'farbe'))
