# -*- coding: utf-8 -*-
u"""Animation im Export, Beinstellung und Brauenfarbe (01.10.2026 abends) — Kunstdaten, keine Grafikkarte.

1. `G9glbanimation`: eine Bewegung landet als glTF-Animation in einer GLB — Kanäle je Knochen, Ortsspur auf der
   Wurzel, Knoten mit `matrix` werden TRS; Knochen ohne Knoten stehen in `fehlend`; die Datei liest sich wieder.
2. `Haltungsschaetzung.bein`: gespreizte Beine (Knöchel 10 cm außerhalb der Hüfte auf 85 cm) ≈ 6,7°; geschlossene ≈ 0.
3. `Brauenfarbe._rgb`: Hex → 0…1, Unsinn → None.

Sabotage: in `G9glbanimation.einbauen` den Pfad 'rotation' durch 'scale' ersetzen → Fall 1 rot; in `bein` den Betrag
weglassen und Rechts/Links tauschen → Fall 2 rot.
"""
import json
import math
import struct
import sys

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.brauenfarbe import Brauenfarbe


class AnimationHaltungTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _glb(pfad):
        j = {'asset': {'version': '2.0'}, 'scene': 0, 'scenes': [{'nodes': [0]}],
             'nodes': [{'name': 'hip', 'children': [1], 'matrix': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1]},
                       {'name': 'l_thigh', 'translation': [0.1, -0.1, 0.0]}],
             'buffers': [{'byteLength': 0}]}
        text = json.dumps(j).encode()
        text += b' ' * ((4 - len(text) % 4) % 4)
        with open(pfad, 'wb') as d:
            d.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(text) + 8))
            d.write(struct.pack('<II', len(text), 0x4E4F534A) + text)
            d.write(struct.pack('<II', 0, 0x004E4942))

    def test_1_glb_animation(self):
        sys.path.insert(0, str(settings.BASE_DIR.parent))
        from Genesis9.glbanimation import G9glbanimation
        ordner = settings.BASE_DIR.parent / 'ProjektTemp' / '_wegwerf'
        ordner.mkdir(parents=True, exist_ok=True)
        ein, aus = ordner / 'test_glbanimation_ein.glb', ordner / 'test_glbanimation_aus.glb'
        self._glb(ein)
        bewegung = {'times': [0.0, 0.5, 1.0], 'duration': 1.0,
                    'tracks': {'hip': [0, 0, 0, 1] * 3, 'l_thigh': [0, 0, 0.1, 0.995] * 3, 'fehlt': [0, 0, 0, 1] * 3},
                    'position_track': {'bone': 'hip', 'values': [0, 1, 0, 0, 1.1, 0, 0, 1, 0]}}
        glb = G9glbanimation(ein)
        bericht = glb.einbauen(bewegung)
        glb.schreiben(aus)
        self.assertEqual(bericht['kanaele'], 3)
        self.assertEqual(bericht['fehlend'], ['fehlt'])
        neu = G9glbanimation(aus).j
        pfade = sorted(c['target']['path'] for c in neu['animations'][0]['channels'])
        self.assertEqual(pfade, ['rotation', 'rotation', 'translation'])
        self.assertNotIn('matrix', neu['nodes'][0])
        self.assertEqual(neu['nodes'][0]['translation'], [0.0, 1.0, 0.0])

    def test_2_beinstellung(self):
        sys.path.insert(0, str(settings.BASE_DIR.parent / '2d3DIterationen'))
        from iterationen2d3d.haltungsschaetzung import Haltungsschaetzung
        punkte = [[0.0, 0.0, 0.0, 1.0]] * 33
        punkte[23], punkte[24] = [0.1, 0.0, 0.0, 1.0], [-0.1, 0.0, 0.0, 1.0]       # y der Weltpunkte nach unten
        punkte[27], punkte[28] = [0.2, 0.85, 0.0, 1.0], [-0.2, 0.85, 0.0, 1.0]
        winkel, _gewicht = Haltungsschaetzung.bein(punkte, 0)
        self.assertAlmostEqual(winkel, math.degrees(math.atan2(0.1, 0.85)), places=3)
        punkte[27] = [0.1, 0.85, 0.0, 1.0]
        self.assertLess(Haltungsschaetzung.bein(punkte, 0)[0], 0.01)

    def test_3_brauenfarbe_hex(self):
        np.testing.assert_allclose(Brauenfarbe._rgb('#ff8000'), [1.0, 128 / 255, 0.0])
        self.assertIsNone(Brauenfarbe._rgb('grau'))
