# -*- coding: utf-8 -*-
u"""Szene: die Bereiche Haut · Augen · Augenbrauen · Mund · Nägel im Reiter „Modell".

WARUM (Edgar, 12.09.2026: „muss ich doch einen Bereich haben wo ich die
Farbe der Fingernägel, die Augenwimpern, die Farbe der Augen usw einstellen
kann?" — „es fehlen noch die Lippen (farbe usw.) … schön nach Bereich
geordnet" — „FORMAT des Zuklappbaren bereichs wie bei Augen/Wimpern … für
alle"): Die Seite trägt fünf klappbare Bereiche im Format `panel-section`
+ `h3` + `panel-body`, jeder mit eigenem Reset (`data-bereich`); die
Kennungen der Felder sind der Vertrag mit `scene/detailbereiche.js` und
werden HIER aus dieser Tabelle gelesen, nicht abgeschrieben. Die Rechnung
prüft `unit/test_js_koerperdetails.py`.
"""
import re

from django.conf import settings
from django.test import Client, TestCase

JS = settings.BASE_DIR / 'static' / 'viewer' / 'scene' / 'detailbereiche.js'
BEREICHE = ('haut', 'augen', 'brauen', 'mund', 'naegel')
KLAPPBAR = ('prop-transform-section', 'prop-equipped-section',
            'prop-bodytype-section', 'prop-gemeinsam-section', 'prop-morphs-section')


class SzeneDetails(TestCase):

    def setUp(self):
        antwort = Client().get('/humanbody/scene/')
        self.assertEqual(antwort.status_code, 200)
        self.text = antwort.content.decode('utf-8')
        self.tabelle = JS.read_text(encoding='utf-8')

    def _kennungen(self, sorte):
        """Alle `['prop-detail-…', 'feld']`-Kennungen einer Sorte aus der JS-Tabelle."""
        if sorte == 'felder':
            return re.findall(r"\['(prop-detail-[\w-]+)', '\w+'\]", self.tabelle)
        return re.findall(r"'((?:Eyelids|Eyebrows|Hands)_\w+)'", self.tabelle)

    def test_fuenf_klappbare_bereiche_mit_reset(self):
        for name in BEREICHE:
            muster = (r'<div class="panel-section prop-section collapsed" '
                      r'id="prop-details-%s">\s*<h3>[^<]+<span class="chevron">' % name)
            self.assertRegex(self.text, muster)
            self.assertRegex(self.text, r'class="btn-reset-morphs prop-detail-reset" '
                                        r'data-bereich="%s"' % name)

    def test_jede_kennung_der_tabelle_steht_auf_der_seite(self):
        felder = self._kennungen('felder')
        self.assertGreaterEqual(len(felder), 15)
        for kennung in felder:
            muster = r'<input type="(color|range)" id="%s"' % kennung
            self.assertRegex(self.text, muster, kennung)
        morphe = self._kennungen('morphe')
        self.assertGreaterEqual(len(morphe), 9)
        for name in morphe:
            muster = (r'<input type="range" id="prop-detail-morph-%s" '
                      r'min="-100" max="100"' % name)
            self.assertRegex(self.text, muster, name)

    def test_die_uebrigen_bereiche_des_reiters_klappen_ebenso(self):
        for kennung in KLAPPBAR:
            self.assertRegex(self.text, r'<div class="panel-section prop-section[^"]*" '
                                        r'id="%s">\s*<h3>' % kennung, kennung)
        self.assertLess(self.text.index('id="prop-details-section"'),
                        self.text.index('id="prop-morphs-section"'))
