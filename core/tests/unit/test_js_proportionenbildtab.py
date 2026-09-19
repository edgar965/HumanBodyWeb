# -*- coding: utf-8 -*-
"""`Proportionenlinien`: Länge, Strecken, Verschieben, Enden — und das Markup (19.09.2026).

Edgar: „einmal mit Bild, wo ich alle Maße per Ziehen festlegen kann … auch die
Position." Die Rechnung hinter den Griffen des Popups, ohne DOM:

1. `cm`: Länge in Pixeln durch Maßstab, auf 0,1 gerundet, nie unter 0,5; ohne
   Maßstab null.
2. `strecken`: Mitte und Richtung bleiben, die Länge stimmt.
3. `verschoben`: beide Enden um denselben Vektor, die Länge bleibt.
4. `mitEnde`: nur das gezogene Ende wandert, das andere bleibt — und die
   Länge folgt dem Ende (so wird aus einem Zug ein anderer Wert).
5. `markup`: je Maß eine Gruppe mit Linie, Beschriftung am rechten Ende und
   — nur mit Griffen — zwei Kreisen; Klassen für eingestellt und aktiv.
6. Sabotage: ein Ende, das beim Verschieben stehen bliebe, änderte die Länge.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('bildmodell', 'proportionenlinien.js')

SKRIPT = """
const { Proportionenlinien: L } = await import(MODUL);
const linie = [[100, 300], [300, 300]];               // waagerecht, Mitte (200, 300), Länge 200

// 1. cm
pruefe('cm', L.cm(linie, 1000), 20);
pruefe('cm gerundet', L.cm([[0, 0], [345.6, 0]], 1000), 34.6);
pruefe('cm Minimum', L.cm([[0, 0], [1, 0]], 1000), 0.5);
pruefe('cm ohne Maßstab', L.cm(linie, 0), null);
pruefe('cm ohne Linie', L.cm(null, 1000), null);

// 2. strecken
pruefe('gestreckt', L.strecken(linie, 80), [[160, 300], [240, 300]]);
pruefe('gestreckt senkrecht', L.strecken([[0, 0], [0, 100]], 300), [[0, -100], [0, 200]]);

// 3. verschoben
const v = L.verschoben(linie, 15, -40);
pruefe('verschoben', v, [[115, 260], [315, 260]]);
pruefe('verschoben gleiche Länge', L.cm(v, 1000), L.cm(linie, 1000));

// 4. mitEnde
const e = L.mitEnde(linie, 1, [350, 340]);
pruefe('Ende 1 gesetzt', e, [[100, 300], [350, 340]]);
pruefe('Ende 0 bleibt', e[0], [100, 300]);
pruefe('Original unberührt', linie, [[100, 300], [300, 300]]);
pruefe('Länge folgt dem Ende', Math.round(L.cm(e, 1000) * 10) / 10, 25.3);

// 5. markup
const m = L.markup([{ k: 'huefte_breite', name: 'Hüftbreite', p: [100, 300], q: [300, 300], wert: 37.8, eingestellt: true, aktiv: true }], 600, true);
pruefe('Gruppe', m.includes('data-mass="huefte_breite"'), true);
pruefe('Klassen', m.includes('class="prop-linie prop-eingestellt prop-aktiv"'), true);
pruefe('zwei Griffe', (m.match(/prop-griff/g) || []).length, 2);
pruefe('Beschriftung rechts', m.includes('<text x="311.2" y="305">Hüftbreite 37.8</text>'), true);
const ohne = L.markup([{ k: 'x', name: 'X', p: [0, 0], q: [10, 0], wert: 3, eingestellt: false, aktiv: false }], 600);
pruefe('ohne Griffe', ohne.includes('prop-griff'), false);
pruefe('ganze Zahl ohne Komma', ohne.includes('>X 3<'), true);
pruefe('Bezug breit', L.bezug(1200, 1600), 1200);
pruefe('Bezug hochkant', L.bezug(319, 1600), 960);

// 6. Sabotage: bliebe ein Ende beim Verschieben stehen, änderte sich die Länge
const kaputt = [linie[0], [linie[1][0] + 15, linie[1][1] - 40]];
if (L.cm(kaputt, 1000) === L.cm(linie, 1000)) throw new Error('Sabotage nicht erkannt');
console.log(JSON.stringify({ok: true}));
"""


class ProportionenlinienTest(SimpleTestCase):
    databases = set()

    def test_linien_rechnung_und_markup(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
