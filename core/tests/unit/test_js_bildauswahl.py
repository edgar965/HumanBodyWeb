# -*- coding: utf-8 -*-
u"""`Bildauswahl` (Varianten mit Vorschaubild, 18.09.2026): wie ein `<select>`.

In Node mit einer kleinen DOM-Attrappe (Elemente mit Kindern, Klassen,
`dataset`, Hörern):

1. `bauen` zeigt die Vorgabe mit Bild und Name; `.value` liest sie.
2. Die Liste ist zu, ihre Bilder haben KEIN `src` (erst beim Aufklappen).
3. Klick auf den Knopf klappt auf: Bilder bekommen ihr `src`, Liste sichtbar.
4. Klick auf einen Eintrag: `.value` neu, `change` gefeuert, Liste zu, Knopf
   zeigt das Bild der Wahl; ein Eintrag ohne Bild versteckt das Knopfbild.
5. `.value = …` setzt ohne `change`; `.disabled` sperrt den Knopf.

Sabotage-Gegenprobe: `feld.dispatchEvent(new Event('change'…))` weg → Fall 4 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'bildauswahl.js')

SKRIPT = """
class Klassen {
    constructor() { this.s = new Set(); }
    add(k) { this.s.add(k); } remove(k) { this.s.delete(k); }
    contains(k) { return this.s.has(k); }
    toggle(k, an) { if (an === undefined) an = !this.s.has(k); an ? this.s.add(k) : this.s.delete(k); return an; }
}
class Element {
    constructor(tag) {
        this.tag = tag; this.kinder = []; this.eltern = null; this.attribute = {};
        this.dataset = {}; this.style = {}; this.textContent = ''; this.hoerer = {};
        this.classList = new Klassen(); this.disabled = false;
    }
    set className(v) { v.split(/\\s+/).filter(Boolean).forEach(k => this.classList.add(k)); }
    appendChild(k) { k.eltern = this; this.kinder.push(k); return k; }
    setAttribute(n, v) { this.attribute[n] = v; }
    getAttribute(n) { return this.attribute[n] ?? null; }
    addEventListener(art, f) { (this.hoerer[art] ||= []).push(f); }
    removeEventListener(art, f) { this.hoerer[art] = (this.hoerer[art] || []).filter(g => g !== f); }
    dispatchEvent(e) { e.target ||= this; (this.hoerer[e.type] || []).forEach(f => f(e)); return true; }
    klick() { this.dispatchEvent({ type: 'click', target: this }); }
    contains(e) { for (let x = e; x; x = x.eltern) if (x === this) return true; return false; }
    getBoundingClientRect() { return { left: 10, bottom: 30, width: 200 }; }
    _alle() { return this.kinder.flatMap(k => [k, ...k._alle()]); }
    _passt(sel) {
        if (sel.startsWith('.')) return this.classList.contains(sel.slice(1));
        const m = sel.match(/^(\\w+)\\[data-(\\w+)\\]$/);
        if (m) return this.tag === m[1] && this.dataset[m[2]] !== undefined;
        return this.tag === sel;
    }
    querySelector(sel) { return this._alle().find(e => e._passt(sel)) || null; }
    querySelectorAll(sel) { return this._alle().filter(e => e._passt(sel)); }
}
globalThis.Event = class { constructor(type, o) { this.type = type; this.bubbles = !!o?.bubbles; } };
const docHoerer = {};
globalThis.document = {
    createElement: (t) => new Element(t),
    addEventListener: (a, f) => (docHoerer[a] ||= []).push(f),
    removeEventListener: (a, f) => { docHoerer[a] = (docHoerer[a] || []).filter(g => g !== f); },
};
globalThis.window = { addEventListener() {}, removeEventListener() {} };
const { Bildauswahl } = await import(MODUL);

const eintraege = [{ id: '', name: 'Standard' }, { id: 'rot', name: 'Rot' }, { id: 'ohne', name: 'Ohne Bild' }];
const bild = (e) => e.id === 'ohne' ? null : `/vorschau/${e.id || 'standard'}.png`;
const feld = Bildauswahl.bauen(eintraege, 'rot', bild);
const knopf = feld.querySelector('.bildauswahl-knopf');
const liste = feld.querySelector('.bildauswahl-liste');

// 1. Vorgabe
pruefe('wert', feld.value, 'rot');
pruefe('name am knopf', knopf.querySelector('.bildauswahl-name').textContent, 'Rot');
pruefe('bild am knopf', knopf.querySelector('.bildauswahl-bild').getAttribute('src'), '/vorschau/rot.png');
pruefe('gewaehlt markiert', liste.querySelectorAll('li').map(l => l.classList.contains('gewaehlt')), [false, true, false]);

// 2. zu, Bilder ungeladen
pruefe('liste zu', liste.classList.contains('hb-versteckt'), true);
pruefe('kein src', liste.querySelectorAll('img').map(i => i.getAttribute('src')), [null, null, null]);
pruefe('adressen vorgemerkt', liste.querySelectorAll('img').map(i => i.dataset.adresse ?? null),
       ['/vorschau/standard.png', '/vorschau/rot.png', null]);

// 3. auf
knopf.klick();
pruefe('liste auf', liste.classList.contains('hb-versteckt'), false);
pruefe('src geladen', liste.querySelectorAll('img').map(i => i.getAttribute('src')),
       ['/vorschau/standard.png', '/vorschau/rot.png', null]);
pruefe('fest platziert', [liste.style.left, liste.style.top, liste.style.width], ['10px', '32px', '200px']);
pruefe('hoerer draussen', (docHoerer.mousedown || []).length, 1);

// 4. waehlen
let geaendert = 0;
feld.addEventListener('change', () => { geaendert += 1; });
liste.querySelectorAll('li')[2].klick();
pruefe('wert ohne', feld.value, 'ohne');
pruefe('change', geaendert, 1);
pruefe('liste wieder zu', liste.classList.contains('hb-versteckt'), true);
pruefe('hoerer weg', (docHoerer.mousedown || []).length, 0);
pruefe('knopfbild versteckt', knopf.querySelector('.bildauswahl-bild').classList.contains('hb-versteckt'), true);

// 5. value setzen ohne change, disabled
feld.value = '';
pruefe('standard', [feld.value, knopf.querySelector('.bildauswahl-name').textContent], ['', 'Standard']);
pruefe('kein change beim setzen', geaendert, 1);
pruefe('knopfbild sichtbar', knopf.querySelector('.bildauswahl-bild').classList.contains('hb-versteckt'), false);
feld.disabled = true;
pruefe('gesperrt', [knopf.disabled, feld.classList.contains('gedaempft')], [true, true]);
knopf.klick();
pruefe('gesperrt bleibt zu', liste.classList.contains('hb-versteckt'), true);
console.log(JSON.stringify({ ok: true }));
"""


class BildauswahlTest(SimpleTestCase):

    def test_wie_ein_select_mit_bildern(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))
