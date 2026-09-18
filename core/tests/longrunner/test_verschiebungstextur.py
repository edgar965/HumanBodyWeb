# -*- coding: utf-8 -*-
"""Verschiebungstextur: MB-Labs Displacement-Textur kommt als PNG mit
Cache-Kopf, gerundet benannt, in die Ablage — nicht nach `media/`.

LongRunner: das 2048²-Feld kostet rund eine Sekunde.
"""

from pathlib import Path
from unittest import mock

from django.test import Client, SimpleTestCase

from core.dienste.verschiebungstextur import Verschiebungstextur
from core.tests.unit._pruefablage import Pruefablage


class Textur(SimpleTestCase):
    def test_dateiname_rundet_und_kennt_das_geschlecht(self):
        self.assertEqual(
            Verschiebungstextur.dateiname('Male_Caucasian', 0.123, -2, 1),
            'verschiebung_male_a+0.10_t-1.00_m+1.00.png',
        )
        self.assertEqual(Verschiebungstextur.runden('quatsch'), 0.0)

    def test_endpunkt_liefert_png_mit_cache_und_schreibt_in_die_ablage(self):
        with (
            Pruefablage.ordner('verschiebung_') as ordner,
            mock.patch.object(Verschiebungstextur, 'ORDNER', Path(ordner)),
        ):
            antwort = Client().get('/api/character/textur/verschiebung/female/?age=0.5&tone=0.2&mass=0')
            self.assertEqual(antwort.status_code, 200)
            self.assertEqual(antwort['Content-Type'], 'image/png')
            self.assertEqual(antwort['Cache-Control'], 'public, max-age=86400')
            antwort.close()
            dateien = sorted(p.name for p in Path(ordner).glob('*.png'))
            self.assertEqual(dateien, ['verschiebung_female_a+0.50_t+0.20_m+0.00.png'])
        feld = Verschiebungstextur.feld('female', 0.5, 0.2, 0.0)
        self.assertEqual(feld.shape, (2048, 2048))
        self.assertLessEqual(float(feld.max()), 1.0)
