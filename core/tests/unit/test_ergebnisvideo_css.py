# -*- coding: utf-8 -*-
u"""Das Video der Ergebnisseite passt ganz ins Feld — auch im Hochformat.

WARUM (12.09.2026, Edgar: „ich möchte das ganze Video links oben sehen, es
wird abgeschnitten unten"): `.video-overlay-wrapper` ist ein Flex-Kind der
70vh hohen Spalte, und ein Flex-Kind hat `min-height: auto` — es schrumpft
nie unter die natürliche Höhe seines Inhalts. Dance1 (1080×1920) wurde bei
705 px Breite 1253 px hoch, das Feld zeigte 749 davon. Gemessen im DOM mit
einer 1080×1920-Leinwand an Stelle des Videos: 503 px abgeschnitten, mit
`min-height: 0` keiner. Der Block liegt seither in `ergebnisvideo.css`
(style.css war 1447 Zeilen).
"""
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

BASIS = Path(settings.BASE_DIR)
CSS = BASIS / 'static' / 'css' / 'ergebnisvideo.css'
SEITEN = ('job_result.html', 'standalone_result.html')


def regel(css, selektor):
    treffer = re.search(r'^' + re.escape(selektor) + r'\s*\{([^}]*)\}', css, re.M)
    return treffer.group(1) if treffer else ''


class DasErgebnisvideo(SimpleTestCase):

    def test_der_wrapper_darf_unter_den_inhalt_schrumpfen(self):
        css = CSS.read_text(encoding='utf-8')
        self.assertIn('min-height: 0', regel(css, '.video-overlay-wrapper'))
        self.assertIn('object-fit: contain', regel(css, '.video-overlay-wrapper video'))

    def test_beide_ergebnisseiten_binden_die_datei_ein(self):
        for name in SEITEN:
            with self.subTest(seite=name):
                html = (BASIS / 'templates' / name).read_text(encoding='utf-8')
                self.assertIn("{% fassungspfad 'css/ergebnisvideo.css' %}", html)
                self.assertIn('{% load fassung %}', html)

    def test_style_css_fuehrt_den_block_nicht_mehr(self):
        css = (BASIS / 'static' / 'css' / 'style.css').read_text(encoding='utf-8')
        self.assertEqual(regel(css, '.video-overlay-wrapper'), '')
        self.assertEqual(regel(css, '.skeleton-overlay'), '')
