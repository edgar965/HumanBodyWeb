# -*- coding: utf-8 -*-
"""Retarget torch (`humanbody_core.skeleton.retarget.bilderkarte.Retargetbilderkarte`, alle Bilder als Stapel auf der Karte) gegen die numpy-Bild-Schleife (13.11.2026, Edgar: „torch fassung
retarget“): je BVH und Ziel (DEF, Genesis 9) alle Spuren und die Wurzelspur Wert für Wert gleich. Gegenprobe: ein falsches Vorzeichen im Hamilton-Produkt der Karte muss abweichen.
Echte BVH-Dateien aus `3DObjects/animations/bvh/` (fehlen sie, wird übersprungen). Braucht die Karte (CUDA-Start > 1 s, darum LongRunner). Messreihe über 9 Dateien:
`ProjektTemp/_wegwerf/kartenwaechter/retarget_probe.py`.
"""
import os
import unittest
from pathlib import Path

import torch
from django.conf import settings

BVH = Path(settings.TOOLS_ROOT) / '3DObjects' / 'animations' / 'bvh'
DATEIEN = [BVH / 'MocapNET' / 'mocapnet_doubleclap.bvh', BVH / 'Daz' / 'Dance.bvh']


def rechnen(pfad, ziel, numpy_weg):
    from core.dienste.retargetdaten import Retargetdaten
    alt = os.environ.get('HUMANBODY_RETARGET_NUMPY')
    os.environ['HUMANBODY_RETARGET_NUMPY'] = '1' if numpy_weg else '0'
    try:
        e = Retargetdaten(str(pfad), ziel=ziel)._rechnen()
    finally:
        if alt is None:
            os.environ.pop('HUMANBODY_RETARGET_NUMPY', None)
        else:
            os.environ['HUMANBODY_RETARGET_NUMPY'] = alt
    werte = {('spur', k): v for k, v in e.tracks.items()}
    if e.position_track:
        werte[('wurzel', e.position_track['bone'])] = e.position_track['values']
    return werte


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Karte')
class RetargetKarteTest(unittest.TestCase):
    def test_karte_gleich_numpy(self):
        from core.dienste.retargetdaten import Retargetdaten
        da = [p for p in DATEIEN if p.exists()]
        if not da:
            self.skipTest('keine BVH-Dateien')
        for pfad in da:
            for ziel in (Retargetdaten.ZIEL_DEF, Retargetdaten.ZIEL_G9):
                with self.subTest(bvh=pfad.name, ziel=ziel):
                    a, b = rechnen(pfad, ziel, True), rechnen(pfad, ziel, False)
                    self.assertEqual(set(a), set(b))
                    self.assertEqual(a, b)

    def test_gegenprobe_falsches_produkt(self):
        from core.dienste.retargetdaten import Retargetdaten
        from humanbody_core.skeleton.retarget import bilderkarte
        pfad = next((p for p in DATEIEN if p.exists()), None)
        if pfad is None:
            self.skipTest('keine BVH-Dateien')
        echt = bilderkarte.Retargetbilderkarte._mul

        def falsch(selbst, a, b):
            m = echt(selbst, a, b)
            return torch.stack([m[..., 0], m[..., 1], -m[..., 2], m[..., 3]], -1)
        bilderkarte.Retargetbilderkarte._mul = falsch
        try:
            b = rechnen(pfad, Retargetdaten.ZIEL_DEF, False)
        finally:
            bilderkarte.Retargetbilderkarte._mul = echt
        self.assertNotEqual(rechnen(pfad, Retargetdaten.ZIEL_DEF, True), b)
