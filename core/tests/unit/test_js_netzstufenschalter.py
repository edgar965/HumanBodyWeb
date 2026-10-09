# -*- coding: utf-8 -*-
u"""Drei Netzstufen (Edgar, 09.10.2026): `Netzstufenstand` und `Netzstufenschalter` (Strg+Alt+H: grob → fein → ultrafein).

In Node mit Attrappen für `document`, `window` und `location` (wie `test_js_netzstufe`):

1. `naechste`: grob → fein → ultrafein → grob.
2. `zusammen` ohne Figur: die gewählte Stufe; mit Figuren: die NIEDRIGSTE fertige, „lädt", wenn eine lädt, die Zähler nur der
   ladenden; `vergessen` nimmt eine Figur heraus.
3. `text`: fertig → „Netz: fein · Strg+Alt+H zum Ändern"; ladend → „Netz: grob → fein lädt … (3/10) · …".
4. Die Anzeige steht IMMER da (auch ohne Figur), mit `data-stufe`/`data-laedt`, und folgt dem Ereignis `netzstufe-stand`.
5. Die Taste: fein → ultrafein setzt den Keks `netzstufen=3` und ruft `umbauen('ultrafein')`; ultrafein → grob löscht ihn;
   grob → fein ebenso. Liefert `umbauen` true, lädt die Seite nicht neu.
6. Ohne Genesis-Figur (`umbauen` liefert false): Neuladen; auf ultrafein mit dem Einmal-Keks `netzstufen_neuladen=1`.

Sabotage: `naechste` ohne Kreis (Modulo) → Fall 1 rot; Keks nicht gesetzt → Fall 5 rot; Anzeige nur bei Wahl → Fall 4 rot.

Gelaufen am 09.10.2026 (Gesamtlauf auf Ansage): grün.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'netzstufenschalter.js')

SKRIPT = """
const elemente = [];
const element = () => ({ style: {}, dataset: {}, textContent: '', id: '', entfernt: false, remove() { this.entfernt = true; } });
const glas = new Map();
const hoerer = {};
globalThis.document = {
    get cookie() { return [...glas].map(([k, v]) => `${k}=${v}`).join('; '); },
    set cookie(text) {
        const [paar] = text.split(';');
        const [name, wert = ''] = paar.split('=');
        if (wert === '' || /max-age=0(;|$)/.test(text)) glas.delete(name.trim()); else glas.set(name.trim(), wert);
    },
    getElementById: (id) => elemente.find(e => e.id === id && !e.entfernt) || null,
    createElement: () => element(),
    body: { appendChild: (e) => elemente.push(e) },
    addEventListener: (art, f) => { (hoerer[art] = hoerer[art] || []).push(f); },
    dispatchEvent: (e) => { (hoerer[e.type] || []).forEach(f => f(e)); return true; },
};
globalThis.CustomEvent = class { constructor(type, opt) { this.type = type; this.detail = opt && opt.detail; } };
const tasten = [];
const fenster = { addEventListener: (art, f) => { if (art === 'keydown') tasten.push(f); } };
let neugeladen = 0;
globalThis.location = { reload() { neugeladen += 1; } };
globalThis.window = fenster;

const { Netzstufenschalter: S } = await import(MODUL);
const { Netzstufenstand: Z } = await import(MODUL.replace('netzstufenschalter.js', 'netzstufenstand.js'));
const taste = () => tasten.forEach(f => f({ code: 'KeyH', ctrlKey: true, altKey: true, shiftKey: false,
                                           preventDefault() {}, stopImmediatePropagation() {} }));
const anzeige = () => document.getElementById('netzstufe-abzeichen');

// 1. Kreis
pruefe('kreis', ['grob', 'fein', 'ultrafein'].map(s => Z.naechste(s)), ['fein', 'ultrafein', 'grob']);

// 2. zusammen
pruefe('ohne figur: die wahl', Z.zusammen(), { stufe: 'fein', laedt: false, fertig: 0, gesamt: 0 });
const a = { id: 'a' }, b = { id: 'b' };
Z.melden(a, 'fein', false);
Z.melden(b, 'grob', true, 3, 10);
pruefe('niedrigste, laedt, zaehler', Z.zusammen(), { stufe: 'grob', laedt: true, fertig: 3, gesamt: 10 });
Z.vergessen(b);
pruefe('b vergessen', Z.zusammen().stufe, 'fein');
Z.vergessen(a);

// 3. text
pruefe('text fertig', S.text({ stufe: 'fein', laedt: false, fertig: 0, gesamt: 0 }, 'fein'), 'Netz: fein · Strg+Alt+H zum Ändern');
pruefe('text ladend', S.text({ stufe: 'grob', laedt: true, fertig: 3, gesamt: 10 }, 'fein'),
       'Netz: grob → fein lädt … (3/10) · Strg+Alt+H zum Ändern');

// 4. anzeige immer da
const umgebaut = [];
S.einrichten(fenster, async (ziel) => { umgebaut.push(ziel); return true; });
pruefe('anzeige ohne figur', [anzeige().textContent, anzeige().dataset.stufe, anzeige().dataset.laedt],
       ['Netz: fein · Strg+Alt+H zum Ändern', 'fein', '0']);
const f = { id: 'f' };
Z.melden(f, 'grob', true, 1, 4);
pruefe('anzeige folgt dem ereignis', [anzeige().dataset.stufe, anzeige().dataset.laedt], ['grob', '1']);
Z.melden(f, 'fein', false);

// 5. taste: fein -> ultrafein -> grob -> fein
taste(); await new Promise(r => setTimeout(r, 0));
pruefe('ultrafein: umbauen + keks', [umgebaut.at(-1), document.cookie.includes('netzstufen=3'), Z.wahl], ['ultrafein', true, 'ultrafein']);
Z.melden(f, 'ultrafein', false);
taste(); await new Promise(r => setTimeout(r, 0));
pruefe('grob: umbauen, kein keks', [umgebaut.at(-1), document.cookie.includes('netzstufen=3'), Z.wahl], ['grob', false, 'grob']);
Z.melden(f, 'grob', false);
taste(); await new Promise(r => setTimeout(r, 0));
pruefe('fein: umbauen', [umgebaut.at(-1), Z.wahl], ['fein', 'fein']);
pruefe('kein neuladen mit umbau', neugeladen, 0);

// 6. ohne genesis-figur
Z.vergessen(f);
S.einrichten(fenster, async () => false);
Z.melden({ id: 'x' }, 'fein', false);
tasten.splice(0, 1);   // nur der zweite Zuhoerer (der mit umbauen = false) bleibt
taste(); await new Promise(r => setTimeout(r, 0));
pruefe('neuladen ohne umbau', neugeladen >= 1, true);
pruefe('einmal-keks auf ultrafein', document.cookie.includes('netzstufen_neuladen=1'), true);
console.log(JSON.stringify({ ok: true }));
"""


class NetzstufenschalterTest(SimpleTestCase):

    def test_drei_stufen_taste_und_anzeige(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))
