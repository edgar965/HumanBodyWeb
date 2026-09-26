# -*- coding: utf-8 -*-
u"""Die Vorschaubilder der Daz-Garderobe stehen auf hellem Grund (19.09.2026,
Edgar: „in der genesis Leiste sind viele Icons viel zu dunkel … leuchtende
Farben, so wie diese Assets auch in Wirklichkeit sind").

Daz' `<Name>.png` neben der `.duf` sind RGBA mit durchsichtigem Grund; auf
der dunklen Seite war ein LVA-Lederstueck fast schwarz (gemessen: mittlere
Helligkeit 24 von 255, auf `#e6e6ea` ueber 100). Das ist reines CSS plus
eine Klasse — und beides ist schon einmal still verloren gegangen, deshalb:

1. `animationsbaum.css` gibt `.garment-thumb.daz-vorschau` UND
   `.bildauswahl-bild` (Farbvarianten) einen hellen Grund: Helligkeit des
   Hintergrunds ueber 200 von 255.
2. `genesis9garderobe.js` haengt die Klasse `daz-vorschau` an das Bild der
   Liste, `bildauswahl.js` die Klasse `bildauswahl-bild` an die Varianten.
3. Ein durchsichtiges dunkles Bild ist auf diesem Grund hell — dieselbe
   Rechnung wie im Longrunner mit dem echten LVA-Bild, hier mit einem
   Kunstbild: 60 % Deckung in Dunkelbraun.

Sabotage-Gegenprobe: `background: #e6e6ea` -> `#1e1e2e` in der CSS-Regel ->
Fall 1 rot; `daz-vorschau` aus `genesis9garderobe.js` -> Fall 2 rot.
"""
import re

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

CSS = settings.BASE_DIR / 'static' / 'css' / 'animationsbaum.css'
GARDEROBE = settings.BASE_DIR / 'static' / 'viewer' / 'charakter' / 'genesis9' / 'genesis9garderobe.js'
BILDAUSWAHL = settings.BASE_DIR / 'static' / 'viewer' / 'gemeinsam' / 'bildauswahl.js'


def helligkeit(hexfarbe):
    r, g, b = (int(hexfarbe[i:i + 2], 16) for i in (1, 3, 5))
    return 0.299 * r + 0.587 * g + 0.114 * b


class DazVorschauHell(SimpleTestCase):
    databases = set()

    def regel(self):
        text = CSS.read_text(encoding='utf-8')
        treffer = re.search(r'\.garment-thumb\.daz-vorschau\s*,\s*\.bildauswahl-bild\s*\{([^}]*)\}', text)
        self.assertIsNotNone(treffer, 'CSS-Regel fuer .garment-thumb.daz-vorschau und .bildauswahl-bild fehlt')
        return treffer.group(1)

    def test_1_heller_grund_in_der_css_regel(self):
        farbe = re.search(r'background\s*:\s*(#[0-9a-fA-F]{6})', self.regel())
        self.assertIsNotNone(farbe, 'kein Hintergrund in der Regel')
        self.assertGreater(helligkeit(farbe.group(1)), 200, farbe.group(1))

    def test_2_die_bilder_tragen_die_klassen(self):
        self.assertIn("bild.className = 'garment-thumb daz-vorschau'", GARDEROBE.read_text(encoding='utf-8'))
        self.assertIn("'bildauswahl-bild'", BILDAUSWAHL.read_text(encoding='utf-8'))

    def test_3_ein_durchsichtiges_dunkles_bild_wird_hell(self):
        farbe = re.search(r'background\s*:\s*(#[0-9a-fA-F]{6})', self.regel()).group(1)
        grund = np.array([int(farbe[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.float64)
        leder, deckung = np.array([60.0, 40.0, 30.0]), 0.6                  # Kunstbild
        hell = helligkeit('#%02x%02x%02x' % tuple(int(v) for v in deckung * leder + (1 - deckung) * grund))
        dunkel = helligkeit('#%02x%02x%02x' % tuple(int(v) for v in deckung * leder + (1 - deckung) * np.array([30, 30, 46])))
        self.assertGreater(hell, 100, hell)
        self.assertLess(dunkel, 50, dunkel)
