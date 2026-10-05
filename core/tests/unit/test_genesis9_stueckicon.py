# -*- coding: utf-8 -*-
"""Das Icon eines eigenen Stücks (`G9stueckicon`, 05.10.2026): Geometrie und Farbe kommen aus der Bibliothek (`.duf`, `.dsf`, Textur) — gerendert wird hier nicht (kein GL im Test).

Edgar (05.10.2026): „kannst du die ablegen bei den Genesis Assets, richtig einsortiert, mit Icon?" — 80 von 83 Stücken im Ordner EIGEN hatten kein `<Name>.png`.
"""
import gzip
import json
import tempfile
from pathlib import Path

import numpy as np
from django.test import SimpleTestCase
from Genesis9.stueckicon import G9stueckicon


def _schreiben(pfad, daten):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_bytes(gzip.compress(json.dumps(daten).encode('utf-8')))


class DasStueckicon(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory(dir=str(Path(__file__).parent))
        self.addCleanup(self.ordner.cleanup)
        self.wurzel = Path(self.ordner.name)
        self.duf = self.wurzel / 'People' / 'Genesis 9' / 'Clothing' / 'EIGEN' / 'Eigen Probe.duf'

    def _stueck(self, diffus):
        _schreiben(self.duf, {'material_library': [{'diffuse': {'channel': diffus}}]})
        viereck = {'vertices': {'values': [[0, 0, 0], [100, 0, 0], [100, 100, 0], [0, 100, 0], [50, 50, 100]]},
                   'polylist': {'values': [[0, 0, 0, 1, 2, 3], [0, 0, 0, 1, 4]]}}
        _schreiben(self.wurzel / 'data' / 'EIGEN' / 'Eigen Probe' / 'EIGEN_Eigen_Probe.dsf', {'geometry_library': [viereck]})

    def test_die_geometrie_kommt_in_meter_und_als_dreiecke(self):
        self._stueck({'value': [0.2, 0.4, 0.6]})
        punkte, dreiecke = G9stueckicon.netz(self.duf)
        self.assertAlmostEqual(float(punkte[:, 0].max()), 1.0)                 # cm → m
        self.assertEqual(dreiecke.tolist(), [[0, 1, 2], [0, 2, 3], [0, 1, 4]])  # Viereck → 2 Dreiecke, Dreieck bleibt

    def test_ohne_geometrie_gibt_es_kein_icon(self):
        _schreiben(self.duf, {'material_library': [{}]})
        self.assertIsNone(G9stueckicon.netz(self.duf))
        self.assertIsNone(G9stueckicon.ablegen(self.duf))
        self.assertFalse(self.duf.with_suffix('.png').exists())

    def test_die_farbe_ist_die_diffusfarbe_sonst_grau(self):
        self._stueck({'value': [0.2, 0.4, 0.6]})
        self.assertEqual(G9stueckicon.farbe(self.duf), (0.2, 0.4, 0.6))
        _schreiben(self.duf, {'material_library': [{}]})
        self.assertEqual(G9stueckicon.farbe(self.duf), G9stueckicon.GRAU)

    def test_die_farbe_ist_das_mittel_der_sichtbaren_texturpixel(self):
        from PIL import Image
        bild = np.zeros((2, 2, 4), dtype=np.uint8)
        bild[0, 0] = (200, 100, 0, 255)
        bild[0, 1] = (100, 100, 0, 255)                 # die zwei anderen Pixel sind durchsichtig und zählen nicht
        textur = self.wurzel / 'Runtime' / 'Textures' / 'EIGEN' / 'Eigen Probe' / 'textur.png'
        textur.parent.mkdir(parents=True)
        Image.fromarray(bild, 'RGBA').save(str(textur))
        self._stueck({'value': [1.0, 1.0, 1.0], 'image_file': '/Runtime/Textures/EIGEN/Eigen%20Probe/textur.png'})
        rot, gruen, blau = G9stueckicon.farbe(self.duf)
        self.assertAlmostEqual(rot, 150 / 255.0, places=4)
        self.assertAlmostEqual(gruen, 100 / 255.0, places=4)
        self.assertAlmostEqual(blau, 0.0, places=4)

    def test_ein_vorhandenes_icon_bleibt_ohne_neu(self):
        self._stueck({'value': [0.2, 0.4, 0.6]})
        ziel = self.duf.with_suffix('.png')
        ziel.write_bytes(b'alt')
        self.assertIsNone(G9stueckicon.ablegen(self.duf))
        self.assertEqual(ziel.read_bytes(), b'alt')
