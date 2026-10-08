# -*- coding: utf-8 -*-
"""Kein Treffertest beim Drehen und Verschieben (08.10.2026, Edgar: „die Bedienung ist wieder holprig, Drehungen, Verschiebungen ruckeln").

`Schwebeanzeige` strahlte bei jeder Mausbewegung über der Fläche — auch mit gedrückter Taste (Kamera drehen, verschieben, zoomen) und beim Greifen (G). Eine
gehäutete Figur in Animation geht nicht über den Suchbaum (`Raycastbeschleunigung.ruhend`); der Test gegen alle Netze kostet dort laut Messung in
`gemeinsam/raycastbeschleunigung.js` 297 ms (68 Netze, 335.025 Dreiecke) — bei jedem Bild ein Hänger. Jetzt:

1. Bei gedrückter Taste oder im Greifen (`state.greiftGerade`) kein Test.
2. War der letzte Test langsamer als `LANGSAM_MS`, läuft der nächste erst, wenn die Maus `RUHE_MS` stillsteht (Entprellen); war er schnell, wie bisher je Bild.
3. Die Dauer wird am Ende von `_pruefen` gemessen; `_verlassen` räumt den Wartetimer.

Am Quelltext geprüft (die Module hängen an `three`). Im Chrome mit künstlichem Raycast und virtueller Uhr gemessen: 30 Bewegungen mit Taste → 0 Treffertests,
ohne Taste → 1 je Bild; nach einem 50-ms-Test 0 Tests während der Bewegung und einer 150 ms nach dem Stillstand; danach mit schnellem Test wieder einer je Bild.

Sabotage: `e.buttons ||` aus `_gemerkt` streichen → Fall 1 rot; die Dauermessung (`this._dauer = …`) streichen → Fall 2 rot.
"""
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


def quelltext():
    return (Path(settings.BASE_DIR) / 'static' / 'viewer' / 'charakter' / 'schwebeanzeige.js').read_text(encoding='utf-8')


class SchwebeanzeigeTasteTest(SimpleTestCase):
    databases = set()

    def test_1_gedrueckte_taste_und_greifen_pruefen_nicht(self):
        text = quelltext()
        gemerkt = text[text.index('_gemerkt(e) {'):text.index('_nachgemerkt() {')]
        self.assertIn('if (e.buttons || state.greiftGerade) return;', gemerkt)
        # die Sperre steht VOR dem Planen jedes Tests (Entprellen und Bildtakt)
        sperre = gemerkt.index('e.buttons')
        self.assertLess(sperre, gemerkt.index('setTimeout('))
        self.assertLess(sperre, gemerkt.index('requestAnimationFrame('))

    def test_2_nach_langsamem_test_erst_bei_ruhender_maus(self):
        text = quelltext()
        self.assertRegex(text, r'static LANGSAM_MS = \d+;')
        self.assertRegex(text, r'static RUHE_MS = \d+;')
        self.assertIn('if (this._dauer > Schwebeanzeige.LANGSAM_MS) {', text)
        self.assertIn('clearTimeout(this._ruhe);', text)
        self.assertIn('setTimeout(() => this._nachgemerkt(), Schwebeanzeige.RUHE_MS);', text)

    def test_3_dauer_wird_gemessen_und_der_timer_geraeumt(self):
        text = quelltext()
        pruefen = text[text.index('_pruefen(e) {'):text.index('static _ziele() {')]
        self.assertIn('const start = performance.now();', pruefen)
        self.assertTrue(re.search(r'this\._dauer = performance\.now\(\) - start;\s*\}\s*$', pruefen.split('/**')[0].rstrip()),
                        'die Dauer wird als letzte Zeile von _pruefen gesetzt')
        verlassen = text[text.index('_verlassen() {'):text.index('_pruefen(e) {')]
        self.assertIn('clearTimeout(this._ruhe);', verlassen)
