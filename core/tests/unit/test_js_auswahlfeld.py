# -*- coding: utf-8 -*-
u"""`Auswahlfeld`: Optionen an ein `<select>` hängen.

WARUM (30.08.2026, Befund `doppelcode` + „lange Zeile")
=========================================================================
Diese vier Zeilen standen SECHZEHNMAL im Projekt, auf neun Dateien verteilt
— fünf davon in EINE Zeile gequetscht (bis 240 Zeichen):

    const opt = document.createElement('option');
    opt.value = t.key; opt.textContent = t.label; feld.appendChild(opt);

DIE STELLEN, DIE WEHTUN, sind die Ränder. Drei der sechzehn Kopien prüften
nicht, ob es das `<select>` überhaupt gibt (`scene/hair.js` verliess sich
darauf, dass `select` vorher geprüft wurde, `colorSelect` aber nicht), und
zwei liefen ungeprüft in eine fehlende Serverliste. Beides wirft im Browser
mitten im Aufbau der Seitenleiste — und weil das in einem `await`-Zweig
passiert, bleibt die halbe Leiste leer, ohne dass etwas rot wird.

Deshalb prüft dieser Test vor allem: fehlendes Feld, fehlende Liste, leere
Liste. Alle drei müssen 0 ergeben und dürfen NICHT werfen.

FEHLT `node`, ist das ein FEHLER — node ist Werkzeug dieses Projekts,
kein Zufall der Umgebung (siehe `Jsmodul.laufen`).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'auswahlfeld.js')

#: Ein `<select>`, so viel davon, wie die Klasse anfasst. Node hat kein DOM;
#: eine echte Attrappe ist ehrlicher als ein Test, der nur den Rückgabewert
#: liest — `appendChild` und `dataset` sollen ja wirklich benutzt werden.
DOM = """
class Option {
    constructor() {
        this.value = null; this.textContent = null;
        this.dataset = {}; this.selected = false;
    }
}
globalThis.document = {
    createElement(tag) {
        if (tag !== 'option') throw new Error('unerwartet: ' + tag);
        return new Option();
    },
};
const feld = () => ({ kinder: [], appendChild(k) { this.kinder.push(k); } });
"""

SKRIPT = DOM + """
const { Auswahlfeld } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist)
                        + ' statt ' + JSON.stringify(soll));
    }
};

// --- die haeufigste Bauart: Serverliste aus {key, label} -------------------
let f = feld();
pruefe('Anzahl', Auswahlfeld.ausSchluesseln(
    f, [{key: 'a', label: 'Hemd'}, {key: 'b', label: 'Hose'}]), 2);
pruefe('Werte', f.kinder.map(k => k.value), ['a', 'b']);
pruefe('Aufschriften', f.kinder.map(k => k.textContent), ['Hemd', 'Hose']);

// --- Namen, wahlweise mit Anzeigeform -------------------------------------
f = feld();
Auswahlfeld.ausNamen(f, ['MALE_CAUCASIAN'], (n) => n.replace(/_/g, ' '));
pruefe('Name als Wert', f.kinder[0].value, 'MALE_CAUCASIAN');
pruefe('Anzeige getrennt', f.kinder[0].textContent, 'MALE CAUCASIAN');

// --- dataset und selected -------------------------------------------------
f = feld();
Auswahlfeld.fuellen(f, [
    {wert: '/a.glb', text: 'Kurz', daten: {name: 'kurz'}},
    {wert: '/b.glb', text: 'Lang', gewaehlt: true},
]);
pruefe('dataset', f.kinder[0].dataset.name, 'kurz');
pruefe('nicht vorgewaehlt', f.kinder[0].selected, false);
pruefe('vorgewaehlt', f.kinder[1].selected, true);

// --- ANGEHAENGT, nicht ersetzt --------------------------------------------
f = feld();
Auswahlfeld.ausNamen(f, ['eins']);
Auswahlfeld.ausNamen(f, ['zwei']);
pruefe('haengt an', f.kinder.map(k => k.value), ['eins', 'zwei']);

// --- die Raender: nichts davon darf werfen --------------------------------
pruefe('kein Feld', Auswahlfeld.fuellen(null, [{wert: 'x', text: 'X'}]), 0);
pruefe('keine Liste', Auswahlfeld.fuellen(feld(), null), 0);
pruefe('Liste fehlt (Schluessel)', Auswahlfeld.ausSchluesseln(feld(), null), 0);
pruefe('Liste fehlt (Namen)', Auswahlfeld.ausNamen(feld(), undefined), 0);
pruefe('leere Liste', Auswahlfeld.ausNamen(feld(), []), 0);
pruefe('kein Feld, keine Liste', Auswahlfeld.ausNamen(null, null), 0);

console.log(JSON.stringify({fertig: true}));
"""


class AuswahlfeldTest(SimpleTestCase):
    u"""Der gemeinsame Optionen-Füller, in Node ausgeführt."""

    def test_fuellt_und_haelt_die_raender_aus(self):
        self.assertEqual(MODUL.laufen(SKRIPT), {'fertig': True})
