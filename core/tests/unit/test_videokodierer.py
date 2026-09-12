# -*- coding: utf-8 -*-
u"""`Videokodierer.aus_bildfolge`: ungerade Bilder muessen kodierbar bleiben.

x264 mit `yuv420p` verlangt gerade Breite und Hoehe. Die Leinwand der
Szene-Seite liefert je nach Fenster ungerade Masse (gemessen 11.09.2026:
3185x1849); ffmpeg brach dann ab — „width not divisible by 2" — und der
Browser-Weg des Figurvideos endete mit 500. Der Befehl traegt seither den
Rundungsfilter, wenn keine feste Groesse verlangt ist.

Der zweite Fall FAEHRT ffmpeg (drei Bilder 319x185) und ist deshalb
absichtlich klein; ohne den Filter wird er rot (Gegenprobe gemacht).
"""
import os
import subprocess

from django.test import SimpleTestCase

from core.dienste.videokodierer import Videokodierer
from ._pruefablage import Pruefablage


class VideokodiererTest(SimpleTestCase):

    databases = set()

    def test_befehl_rundet_ohne_feste_groesse(self):
        befehl = Videokodierer.aus_bildfolge('ordner', 'ziel.mp4', fps=24)
        self.assertIn(Videokodierer.GERADE, befehl)
        fest = Videokodierer.aus_bildfolge('ordner', 'ziel.mp4', breite=1920,
                                          hoehe=1080)
        self.assertNotIn(Videokodierer.GERADE, fest)
        self.assertIn('scale=1920:1080', fest)

    def test_ungerade_bilder_werden_kodiert(self):
        try:
            import numpy as np
            import cv2
        # stumm gewollt: ohne cv2 wird uebersprungen, und das steht im Lauf
        except ImportError:                                  # pragma: no cover
            self.skipTest('cv2 fehlt')
        with Pruefablage.ordner('videokodierer_') as ordner:
            for i in range(3):
                cv2.imwrite(os.path.join(ordner, '%06d.png' % i),
                            np.full((185, 319, 3), 90 + 40 * i, np.uint8))
            ziel = os.path.join(ordner, 'ungerade.mp4')
            befehl = Videokodierer.aus_bildfolge(ordner, ziel, fps=24, crf=30)
            lauf = subprocess.run(befehl, capture_output=True, text=True)
            self.assertEqual(lauf.returncode, 0, lauf.stderr[-400:])
            self.assertGreater(os.path.getsize(ziel), 0)
