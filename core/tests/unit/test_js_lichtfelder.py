# -*- coding: utf-8 -*-
u"""`Lichtfelder`: Winkel, Penumbra und Reichweite eines Spotlichts.

WARUM (31.08.2026, Befund `doppelcode`)
=======================================
Die drei Felder standen zweimal — in `eigenschaften/licht.js` als HTML von
Hand, in `eigenschaften/klip_schluesselbilder.js` über die Maskenbausteine.
Gleich waren beide Male die Grenzen: `1…170` für den Winkel, `0…1` in
Schritten von 0.05 für die Penumbra, `0…200` für die Reichweite.

DIE STELLE, DIE WEHTUT, ist der Winkel. Er wird in RADIANT gehalten und in
GRAD angezeigt; die Umrechnung stand an beiden Stellen ausgeschrieben. Wer
sie an einer davon anfasst, bekommt ein Licht, das in der Spur anders
aussieht als am Schlüsselbild — und beide Masken sehen dabei normal aus.

Dieser Test hält deshalb die erzeugten Zeichenketten fest, nicht nur die
Existenz der Felder: Ein verrutschtes `toFixed` oder eine vergessene
Grenze wäre sonst unsichtbar.

FEHLT `node`, ist das ein FEHLER — node ist Werkzeug dieses Projekts,
kein Zufall der Umgebung (siehe `Jsmodul.laufen`).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('bvh_studio', 'eigenschaften', 'lichtfelder.js')

SKRIPT = """
const { Lichtfelder } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (ist !== soll) throw new Error(was + ':\\n  ist : ' + ist
                                      + '\\n  soll: ' + soll);
};

// --- Winkel: Radiant rein, Grad raus ---------------------------------------
pruefe('Winkel 30 Grad',
    Lichtfelder.winkel('prop-light', Math.PI / 6),
    '<div class="prop-row"><label>Winkel:</label>'
    + '<input type="number" value="30.0" id="prop-light-angle" '
    + 'min="1" max="170" step="1"> \\u00b0</div>');

// Ohne Wert gilt die Vorgabe — dieselben 30 Grad wie in der alten Fassung.
pruefe('Winkel ohne Wert',
    Lichtfelder.winkel('prop-light', null),
    Lichtfelder.winkel('prop-light', Math.PI / 6));

// 0 IST EIN WERT, keine fehlende Angabe: `??` statt `||`. Mit `||` fiele ein
// zusammengezogener Kegel auf die Vorgabe von 30 Grad zurueck.
pruefe('Winkel null Radiant',
    Lichtfelder.winkel('prop-light', 0).includes('value="0.0"'), true);

// --- Penumbra und Reichweite ----------------------------------------------
pruefe('Penumbra',
    Lichtfelder.penumbra('prop-lkf', 0.25),
    '<div class="prop-row"><label>Penumbra:</label>'
    + '<input type="number" value="0.25" id="prop-lkf-penumbra" '
    + 'min="0" max="1" step="0.05"></div>');
pruefe('Penumbra 0 bleibt 0',
    Lichtfelder.penumbra('prop-lkf', 0).includes('value="0.00"'), true);
pruefe('Reichweite',
    Lichtfelder.reichweite('prop-lkf', 12.5),
    '<div class="prop-row"><label>Reichweite:</label>'
    + '<input type="number" value="12.5" id="prop-lkf-distance" '
    + 'min="0" max="200" step="1"></div>');

// --- Die Vorsilbe trennt die beiden Masken ---------------------------------
// Spur und Schluesselbild koennen gleichzeitig im DOM stehen; zwei Elemente
// mit derselben `id` liefern bei `getElementById` immer dasselbe.
const spur = Lichtfelder.alle('prop-light', {angle: Math.PI / 4,
                                             penumbra: 0.5, distance: 20});
const bild = Lichtfelder.alle('prop-lkf', {angle: Math.PI / 4,
                                           penumbra: 0.5, distance: 20});
pruefe('Spur traegt ihre Kennungen', spur.includes('prop-light-angle'), true);
pruefe('Bild traegt seine Kennungen', bild.includes('prop-lkf-angle'), true);
pruefe('keine Vermischung', spur.includes('prop-lkf-'), false);
pruefe('drei Zeilen', (spur.match(/prop-row/g) || []).length, 3);

console.log(JSON.stringify({fertig: true}));
"""


class LichtfelderTest(SimpleTestCase):
    u"""Die gemeinsamen Lichtfelder, in Node ausgeführt."""

    def test_masken_und_grenzen_bleiben(self):
        self.assertEqual(MODUL.laufen(SKRIPT), {'fertig': True})
