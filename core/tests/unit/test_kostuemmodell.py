# -*- coding: utf-8 -*-
"""BlenderModel, Modell je Runde (29.09.2026): Renders auf die Figur zugeschnitten. Ohne Datenbank, ohne
Blender; Dateien nur unter `HumanBodyWeb/_wegwerf/` (nie System-Temp).
"""

import shutil
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase
from PIL import Image

from core.dienste.kostuemrunde import Kostuemrunde


class KostuemmodellTest(SimpleTestCase):
    def setUp(self):
        self.ordner = Path(settings.BASE_DIR) / '_wegwerf' / 'test_kostuemmodell'
        self.ordner.mkdir(parents=True, exist_ok=True)
        self.addCleanup(shutil.rmtree, self.ordner, True)

    def test_render_wird_auf_die_figur_zugeschnitten(self):
        quelle = self.ordner / 'render.png'
        bild = Image.new('RGBA', (256, 384), (0, 0, 0, 0))
        bild.paste((200, 100, 50, 255), (100, 50, 150, 250))  # Figur: 50 × 200 px
        bild.save(quelle)
        Kostuemrunde.zuschneiden(quelle, self.ordner / 'aus.png')
        with Image.open(self.ordner / 'aus.png') as aus:
            rand = round(200 * Kostuemrunde.RAND)
            self.assertEqual(aus.size, (50 + 2 * rand, 200 + 2 * rand))

    def test_leerer_render_bleibt_unveraendert(self):
        quelle = self.ordner / 'leer.png'
        Image.new('RGBA', (256, 384), (0, 0, 0, 0)).save(quelle)
        Kostuemrunde.zuschneiden(quelle, self.ordner / 'aus.png')
        with Image.open(self.ordner / 'aus.png') as aus:
            self.assertEqual(aus.size, (256, 384))
