# -*- coding: utf-8 -*-
"""`GarmentcodeStueckquelle`: nach einem Klick auf ein GarmentCode-Stück in
der Szene die Toolbox GENAU dorthin springen lassen — das Vorbild in der
Kleiderbibliothek markieren, oder die Formcheckbox ankreuzen.

WARUM (Edgar, 24.09.2026: „wenn ich ein Garment Code anklicke, soll die
Toolbox links exakt zu dem hinspringen, also z.B: in der Kleiderbibliothek
das Garment Code selektieren, oder die Checkboxen aktivieren falls keine
Kleiderbibliothek")
=====================================================================
Der Vorlagenwechsel (`fn.garmentcodeVorlageZeigen`, unveraendert) setzte bis
dahin nur die KATALOG-Auswahl („Schuh") — Vorbild-Knopf und Formcheckbox
blieben unangetastet. Die Vorbild-Knöpfe und Formcheckboxen holt der Server
ASYNCHRON (`GarmentcodeVorbilder.laden`, `/api/garmentcode/regler/`); hier
wird das mit einer Warteschleife nachgebildet, die den Knopf erst nach ein
paar Versuchen einfügt.

`garmentcodePreset` wird ECHT importiert (kein Mock): `anhaken()` ist so
einfach (Häkchen setzen, KEINE Werte anfassen), dass eine Attrappe nur die
Aussage verdeckt hätte, die hier zählt — kein `change`-Ereignis, also keine
Reglerbewegung.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('scene', 'garmentcode_stueckquelle.js')

DOM = """
globalThis.CSS = { escape: s => s };

// Vorbild-Knoepfe und Formcheckboxen als einfache Objekte -- ECHTE CSS-Selektoren
// braucht nur `garmentcode_stueckquelle.js` selbst (zwei feste Formen); `anhaken()`
// aus `garmentcode_preset.js` sucht zusaetzlich OHNE das `#gc-passform`-Praefix.
const vorbildKnoepfe = [];
const presetBoxen = [];
function vorbild(schluessel) {
    const k = { dataset: { schluessel }, klicks: 0, click() { this.klicks += 1; } };
    vorbildKnoepfe.push(k);
    return k;
}
function preset(schluessel) {
    const b = { dataset: { preset: schluessel }, checked: false };
    presetBoxen.push(b);
    return b;
}
globalThis.document = {
    querySelector(sel) {
        let m = /^#gc-vorbilder \\.vorbild-knopf\\[data-schluessel="([^"]*)"\\]$/.exec(sel);
        if (m) return vorbildKnoepfe.find(k => k.dataset.schluessel === m[1]) || null;
        m = /^#gc-passform input\\[data-preset="([^"]*)"\\]$/.exec(sel);
        if (m) return presetBoxen.find(b => b.dataset.preset === m[1]) || null;
        m = /^input\\[data-preset="([^"]*)"\\]$/.exec(sel);
        if (m) return presetBoxen.find(b => b.dataset.preset === m[1]) || null;
        throw new Error('Selektor unerwartet: ' + sel);
    },
};
"""

SKRIPT = DOM + """
const { fn } = await import(new URL('../gemeinsam/registrierung.js', MODUL).href);
const { garmentcodePreset } = await import(new URL('./garmentcode_preset.js', MODUL).href);
const { GarmentcodeStueckquelle } = await import(MODUL);
GarmentcodeStueckquelle.WARTEN_MS = 1;

const warten = (ms) => new Promise((r) => setTimeout(r, ms));

// --- 1. Vorbild sofort da: Knopf wird geklickt, nichts gebaut -------------
let vorlagen = [];
fn.garmentcodeVorlageZeigen = (v) => { vorlagen.push(v); return true; };
const knopfSchuh = vorbild('vorbild_shoes_toigo_flats');
fn.garmentcodeQuelleZeigen('schuh', { art: 'vorbild', schluessel: 'vorbild_shoes_toigo_flats' });
await warten(5);
pruefe('Vorlage gewechselt', vorlagen, ['schuh']);
pruefe('Knopf geklickt', knopfSchuh.klicks, 1);

// --- 2. Vorbild erscheint erst nach dem Nachladen (3 Versuche) ------------
vorlagen = [];
GarmentcodeStueckquelle.zeigen('kleid', { art: 'vorbild', schluessel: 'vorbild_x' });
await warten(2);
pruefe('noch kein Knopf', vorbildKnoepfe.some((k) => k.dataset.schluessel === 'vorbild_x'), false);
const knopfKleid = vorbild('vorbild_x');
await warten(10);
pruefe('nachgeladener Knopf geklickt', knopfKleid.klicks, 1);

// --- 3. Form: Haekchen gesetzt, KEIN Wert angefasst -----------------------
garmentcodePreset.setzen([{ schluessel: 'form_plateauschuh', werte: { 'shoe.heel': 9 } }]);
const box = preset('form_plateauschuh');
GarmentcodeStueckquelle.zeigen('schuh', { art: 'form', schluessel: 'form_plateauschuh' });
await warten(5);
pruefe('Haekchen gesetzt', box.checked, true);
pruefe('als aktiv gemerkt', garmentcodePreset.aktiv.has('form_plateauschuh'), true);

// --- 4. Vorlage nicht gefunden: nichts gesucht, kein Fehler ---------------
fn.garmentcodeVorlageZeigen = () => false;
GarmentcodeStueckquelle.zeigen('nix', { art: 'vorbild', schluessel: 'vorbild_x' });
await warten(5);
pruefe('Knopf unveraendert', knopfKleid.klicks, 1);

// --- 5. Keine bekannte Herkunft: Vorlage wechselt, sonst nichts -----------
vorlagen = [];
fn.garmentcodeVorlageZeigen = (v) => { vorlagen.push(v); return true; };
GarmentcodeStueckquelle.zeigen('hose', null);
await warten(5);
pruefe('nur die Vorlage', vorlagen, ['hose']);

// --- 6. Element erscheint nie: kein Fehler nach den Versuchen -------------
GarmentcodeStueckquelle.VERSUCHE = 2;
GarmentcodeStueckquelle.zeigen('schuh', { art: 'vorbild', schluessel: 'gibtesnicht' });
await warten(10);
pruefe('kein Knopf entstanden', vorbildKnoepfe.some((k) => k.dataset.schluessel === 'gibtesnicht'), false);

console.log(JSON.stringify({ok: true}));
"""


class Stueckquelle(SimpleTestCase):
    databases = set()

    def test_vorbild_und_form_werden_wiedergefunden(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'))
