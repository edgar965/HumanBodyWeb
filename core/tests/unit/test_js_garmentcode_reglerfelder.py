# -*- coding: utf-8 -*-
"""`GarmentcodeReglerfelder.schieber`: ein Regler mit Vorgabe aus der Figur zeigt das Wort, nicht die Zahl.

Seit 20.10.2026 schneidet der Bau den Ärmel ohne gestellten Regler für die Armhaltung der
Figur (`Assets/GarmentCode/aermelwinkel.py`). Der Schieber kennt die Figur nicht; zeigte er
weiter die 10 aus `default.yaml`, stünde dort ein Wert, den der Bau nicht nimmt. Er zeigt
„Figur", bis jemand ihn zieht oder ein Wert gesetzt wird, und nach dem Zurücksetzen wieder.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('charakter', 'garmentcode_reglerfelder.js')

SKRIPT = """
class Element {
    constructor(tag) { this.tag = tag; this.textContent = ''; this.value = ''; this.hoerer = {}; }
    addEventListener(art, f) { this.hoerer[art] = f; }
}
globalThis.document = { createElement: (tag) => new Element(tag) };
const { GarmentcodeReglerfelder } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const bestand = () => ({ werte: {}, nachziehen: {}, vonHand() {} });
const feld = (pfad, vorgabe) => ({ pfad, typ: 'int', wert: 10, bereich: [10, 50], hilfe: { vorgabe } });

// --- Ärmelwinkel: ungestellt „Figur" -----------------------------------------
let r = bestand();
let [schieber, anzeige] = GarmentcodeReglerfelder.schieber(r, 'sleeve.sleeve_angle', feld('sleeve.sleeve_angle', 'Figur'));
pruefe('ungestellt', anzeige.textContent, 'Figur');

// gezogen: die Zahl, und der Wert steht in `werte`
schieber.value = '45';
schieber.hoerer.input();
pruefe('gezogen', anzeige.textContent, '45');
pruefe('Wert gemerkt', r.werte['sleeve.sleeve_angle'], 45);

// zurückgesetzt (wie `zuruecksetzen`: erst löschen, dann nachziehen)
delete r.werte['sleeve.sleeve_angle'];
r.nachziehen['sleeve.sleeve_angle'](10);
pruefe('zurück', anzeige.textContent, 'Figur');

// gesetzt (wie `mehrereSetzen`/Gedächtnis: erst setzen, dann nachziehen)
r.werte['sleeve.sleeve_angle'] = 10;
r.nachziehen['sleeve.sleeve_angle'](10);
pruefe('gesetzt 10', anzeige.textContent, '10');

// --- ein Regler ohne Vorgabe zeigt immer die Zahl ------------------------------
r = bestand();
[schieber, anzeige] = GarmentcodeReglerfelder.schieber(r, 'sleeve.length', { pfad: 'sleeve.length', typ: 'float', wert: 0.3, bereich: [0.1, 1.15], hilfe: { vorgabe: null } });
pruefe('ohne Vorgabe', anzeige.textContent, '0.30');

console.log(JSON.stringify({fertig: true}));
"""


class GarmentcodeReglerfelderTest(SimpleTestCase):
    """Der Schieber des GarmentCode-Reiters, in Node ausgeführt."""

    def test_vorgabe_aus_der_figur_zeigt_das_wort(self):
        self.assertEqual(MODUL.laufen(SKRIPT), {'fertig': True})
