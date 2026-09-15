# -*- coding: utf-8 -*-
u"""Fortschrittsbalken und klebendes Lineal der Studio-Zeitleiste.

WARUM (Edgar, 13.09.2026: „die Überschrift mit der Zeit und dem Playhead
immer sichtbar, auch beim Scrollen. Unten, unterhalb aller Balken mach einen
Play-Fortschrittsbalken, auch immer sichtbar, mit Möglichkeit, die
Play-Position zu verschieben"):

1. `Fortschrittsmass`: Anteil 0…1 (geklemmt, leeres Projekt 0) und das Bild an
   einer Pixelstelle (gerundet, geklemmt; ohne Breite oder Ende 0).
2. Die Vorlage hat die Lineal-Leinwand `#timeline-lineal` (klebend, ohne
   Mausereignisse — die gehen zur Spurenleinwand durch) VOR den Spuren im
   Rahmen und den Fortschrittsbalken `#timeline-fortschritt` HINTER dem Rahmen.
3. `timeline.js` bindet beide an und setzt Höhe/negativen Rand des Lineals aus
   RULER_HEIGHT; `renderTimeline` zeichnet Lineal und Griff auf die Lineal-
   Leinwand und ruft `Fortschrittsbalken.zeichnen()`; der Balken setzt den
   Kopf und blättert die Leiste nach (`Zeitleistenfolge`).

Sabotage-Gegenprobe: in `Fortschrittsmass.bild` `Math.round` → `Math.floor`
→ Fall 1 rot (`bild(2, 3, 100)` 66 statt 67); `pointer-events: none` aus der
Vorlage → Fall 2 rot.
"""
import re

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('bvh_studio', 'fortschrittsmass.js')
STUDIO = settings.BASE_DIR / 'static' / 'viewer' / 'bvh_studio'
VORLAGE = settings.BASE_DIR / 'templates' / 'bvh_studio.html'

SKRIPT = """
const { Fortschrittsmass: F } = await import(MODUL);
const gleich = (was, a, b) => {
    if (a !== b) throw new Error(was + ': ' + a + ' statt ' + b);
};
gleich('halb', F.anteil(50, 100), 0.5);
gleich('am Ende', F.anteil(100, 100), 1);
gleich('dahinter geklemmt', F.anteil(150, 100), 1);
gleich('negativ geklemmt', F.anteil(-5, 100), 0);
gleich('leeres Projekt', F.anteil(5, 0), 0);
gleich('Bild bei 2/3', F.bild(2, 3, 100), 67);
gleich('Bild links', F.bild(-10, 300, 100), 0);
gleich('Bild rechts', F.bild(400, 300, 100), 100);
gleich('ohne Breite', F.bild(10, 0, 100), 0);
gleich('ohne Ende', F.bild(10, 300, 0), 0);
console.log(JSON.stringify({ ok: true }));
"""


def _text(pfad):
    return pfad.read_text(encoding='utf-8')


class FortschrittTest(SimpleTestCase):

    def test_das_mass_rechnet_geklemmt_und_gerundet(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))

    def test_lineal_klebt_und_balken_liegt_unter_dem_rahmen(self):
        html = _text(VORLAGE)
        lineal = html.index('<canvas id="timeline-lineal">')
        spuren = html.index('<canvas id="timeline-canvas">')
        rahmen_ende = html.index('</div>', spuren)
        balken = html.index('<canvas id="timeline-fortschritt">')
        self.assertLess(lineal, spuren)
        self.assertLess(rahmen_ende, balken)
        stil = re.search(r'#timeline-lineal \{([^}]*)\}', html).group(1)
        self.assertIn('position: sticky', stil)
        self.assertIn('pointer-events: none', stil)

    def test_aufbau_und_zeichnen_sind_verdrahtet(self):
        aufbau = _text(STUDIO / 'timeline.js')
        self.assertIn("Zeitleistenflaeche.setzen(flaeche, lineal)", aufbau)
        self.assertIn("Fortschrittsbalken.anbinden("
                      "document.getElementById('timeline-fortschritt'))", aufbau)
        self.assertIn("lineal.style.marginBottom = `-${RULER_HEIGHT}px`", aufbau)
        zeichnen = _text(STUDIO / 'zeitleiste_zeichnen.js')
        self.assertIn('Fortschrittsbalken.zeichnen();', zeichnen)
        self.assertNotIn('Zeitleistenflaeche.oben', zeichnen)
        lineal = _text(STUDIO / 'zeitleiste_lineal.js')
        self.assertIn('Zeitleistenflaeche.linealCtx', lineal)
        kopf = _text(STUDIO / 'zeitleiste_abspielkopf.js')
        self.assertIn('Zeitleistenflaeche.linealCtx', kopf)
        balken = _text(STUDIO / 'zeitleiste_fortschritt.js')
        self.assertIn('Zeitleistenfolge.nachziehen('
                      'state, Zeitleistenflaeche.breite - HEADER_WIDTH)', balken)
        self.assertIn("addEventListener('mousedown'", balken)
