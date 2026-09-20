# -*- coding: utf-8 -*-
"""`Hoehengriff`: die Achse ist die einzige Abweichung vom `Bereichsgriff`.

WARUM (20.09.2026, Edgar, Szene → „Form (Daz-Regler)": „mach unten an der
Stelle einen Griff, mit dem ich die Ansicht nach unten verschieben kann"):
Der Griff erbt Ziehen, Grenzen und Gedächtnis vom `Bereichsgriff` und
tauscht nur die Achse. Geprüft wird genau der Tausch, ohne DOM:

1. Der Mausweg kommt aus `clientY`, nicht `clientX`.
2. Nach unten gezogen = höher (Richtung +1 wie ein Feld links im Fenster).
3. `_anwenden` setzt `height` UND `max-height` — `.anim-tree` bringt eine
   Höchstgrenze mit, die sonst weiter gälte.
4. Der Zeiger ist `row-resize`, und `_nachziehen` feuert kein `resize`.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'hoehengriff.js')

SKRIPT = """
const { Hoehengriff } = await import(MODUL);
const stil = {};
const griff = new Hoehengriff({ griff: {}, bereich: { style: stil },
                                min: 120, max: 1600, vorgabe: 300 });

// 1. Achse
pruefe('clientY', griff._koordinate({ clientX: 7, clientY: 42 }), 42);
// 2. Nach unten = höher
pruefe('höher', Hoehengriff.naechsteBreite(300, 150, griff.richtung, 120, 1600), 450);
pruefe('niedriger', Hoehengriff.naechsteBreite(300, -100, griff.richtung, 120, 1600), 200);
pruefe('Grenze', Hoehengriff.naechsteBreite(300, 5000, griff.richtung, 120, 1600), 1600);
// 3. height und max-height
griff._anwenden('450px');
pruefe('height', stil.height, '450px');
pruefe('max-height', stil.maxHeight, '450px');
pruefe('keine Breite', stil.width, undefined);
// 4. Zeiger und kein resize
pruefe('Zeiger', Hoehengriff.CURSOR, 'row-resize');
let gefeuert = 0;
globalThis.window = { dispatchEvent: () => { gefeuert++; } };
griff._nachziehen();
pruefe('kein resize', gefeuert, 0);
console.log(JSON.stringify({ok: true}));
"""


class HoehengriffTest(SimpleTestCase):
    databases = set()

    def test_achse_ist_senkrecht(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
