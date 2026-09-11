# -*- coding: utf-8 -*-
u"""Die Vorgabe-Form eines Stücks bekommt ihr Häkchen — auch mit Reglern.

WARUM (11.09.2026): Rock- und Schuhformen setzten nur Bausteinfelder
(`meta.*`); die Vorgabe (Bleistiftrock) wurde gehakt, weil alle ihre Pfade
„undefined" lasen. Kleid, Oberteil, Anzug und Unterwäsche setzen dazu
Regler (Ärmellänge 0,3, Hosenlänge 0,85) — die lesen sich als Zahl, und
mit der alten Regel („alle Pfade undefined") bekam keine Form mehr ihr
Häkchen. Jetzt gilt: Regler müssen passen, Bausteinfelder zählen als
Treffer nur für die Vorgabe (`gehakt`).

Läuft in Node gegen das echte Modul; `document` ist eine Attrappe, die
die Kästchen zählt.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('scene', 'garmentcode_passform.js')

SKRIPT = """
const gehakt = [];
globalThis.document = {
    querySelector: (sel) => ({ set checked(v) { if (v) gehakt.push(sel); } }),
    getElementById: () => null,
    createElement: () => ({ classList: { add() {} }, appendChild() {}, dataset: {} }),
};
const { GarmentcodePassform } = await import(MODUL);
const { garmentcodePreset } = await import(MODUL.replace('garmentcode_passform', 'garmentcode_preset'));
const formen = [
    { schluessel: 'form_kleid', titel: 'Kleid', form: true, gehakt: true, zurueck: [],
      werte: { 'meta.upper': 'FittedShirt', 'meta.bottom': 'PencilSkirt',
               'sleeve.sleeveless': false, 'sleeve.length': 0.3 } },
    { schluessel: 'form_sommerkleid', titel: 'Sommerkleid', form: true, gehakt: false, zurueck: [],
      werte: { 'meta.upper': 'Shirt', 'meta.bottom': 'SkirtCircle', 'sleeve.sleeveless': true } },
];
garmentcodePreset.setzen(formen);
const regler = { 'sleeve.sleeveless': false, 'sleeve.length': 0.3 };
const liest = (pfad) => regler[pfad];
const erg = [];
erg.push(GarmentcodePassform.formHaken(formen, liest));          // Vorgabe: Kleid
garmentcodePreset.aktiv.clear();
regler['sleeve.sleeveless'] = true;                               // Ärmel weg: nichts passt
erg.push(GarmentcodePassform.formHaken(formen, liest));
regler['meta.upper'] = 'Shirt'; regler['meta.bottom'] = 'SkirtCircle';   // Bausteine gesetzt
erg.push(GarmentcodePassform.formHaken(formen, liest));
garmentcodePreset.aktiv.add('form_sommerkleid');                 // schon gehakt: nichts tun
erg.push(GarmentcodePassform.formHaken(formen, liest));
console.log(JSON.stringify({ ok: true, erg, gehakt }));
"""


class FormhakenTest(SimpleTestCase):

    databases = []

    def test_die_vorgabe_bekommt_ihr_haekchen_und_sonst_nur_die_passende_form(self):
        daten = MODUL.laufen(SKRIPT)
        self.assertTrue(daten.get('ok'), daten)
        self.assertEqual(daten['erg'], ['form_kleid', None, 'form_sommerkleid', None])
        self.assertEqual(daten['gehakt'], ['input[data-preset="form_kleid"]',
                                           'input[data-preset="form_sommerkleid"]'])
