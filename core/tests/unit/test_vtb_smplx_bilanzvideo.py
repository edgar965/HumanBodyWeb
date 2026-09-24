# -*- coding: utf-8 -*-
"""Neumischen mit `--no_video`: der Eintrag des liegengebliebenen Netzvideos bleibt.

ANLASS (24.09.2026): Beim Nachziehen der Finger (`lift_3d.py --pipeline smplx
… --no_video`) schrieb `Smplxlauf.bilanz_schreiben` die Bilanz ohne `video` —
das Netzvideo lag weiter daneben, die Ergebnisseite kannte es nicht mehr.

BDD - GEGEBEN / DANN
====================
    DerVideoeintrag ... bleibt markiert, wenn Video und alte Bilanz liegen
                    ... entfaellt ohne Videodatei und nach einem gescheiterten Video
"""

import json
import os
import unittest

from ._pruefablage import Pruefablage
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from smplxlauf import Smplxlauf  # noqa: E402
from smplxvideo import Smplxvideo  # noqa: E402


class DerVideoeintrag(unittest.TestCase):
    def setUp(self):
        ablage = Pruefablage.ordner('bilanzvideo_')
        self.ordner = ablage.__enter__()
        self.addCleanup(ablage.__exit__, None, None, None)
        self.lauf = object.__new__(Smplxlauf)
        self.lauf.ziel_bvh = os.path.join(str(self.ordner), 'smplx_tanz.bvh')
        self.bilanz = self.lauf.stamm + '_smplx_bilanz.json'

    def _alte_bilanz(self, video):
        with open(self.bilanz, 'w', encoding='utf-8') as datei:
            json.dump({'bilder': 3, 'video': video}, datei)

    def _videodatei(self):
        with open(self.lauf.stamm + Smplxvideo.ENDUNG, 'wb') as datei:
            datei.write(b'mp4')

    def test_liegt_das_video_bleibt_der_eintrag_markiert(self):
        self._alte_bilanz({'video_datei': 'smplx_tanz_smplx.mp4', 'video_bilder': 3})
        self._videodatei()
        video = self.lauf._frueheres_video(self.bilanz)['video']
        self.assertEqual(video['video_datei'], 'smplx_tanz_smplx.mp4')
        self.assertTrue(video['aus_frueherem_lauf'])

    def test_ohne_videodatei_kein_eintrag(self):
        self._alte_bilanz({'video_datei': 'smplx_tanz_smplx.mp4'})
        self.assertEqual(self.lauf._frueheres_video(self.bilanz), {})

    def test_gescheitertes_video_wird_nicht_weitergetragen(self):
        self._alte_bilanz({'fehler': 'kein EGL'})
        self._videodatei()
        self.assertEqual(self.lauf._frueheres_video(self.bilanz), {})
