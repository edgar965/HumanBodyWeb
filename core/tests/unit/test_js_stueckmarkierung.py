# -*- coding: utf-8 -*-
"""`Stueckmarkierung`: der Klick auf ein Stueck in der Szene oeffnet SEINEN
Reiter und markiert SEINE Zeile.

WARUM (Edgar, 20.09.2026: „wenn ich auf ein Asset oder Garment Code oder
was auch immer klicke, soll in der Toolbar genau das ausgewaehlt sein. das
hatte ich schon oft so als Auftrag vergeben!")
=====================================================================
Bis dahin tat das nur GarmentCode. Die Daz-Garderobe, MakeHuman und Garment
Fit blieben im Modell-Reiter, ihre Zeile unmarkiert — und `selected` hatte
in der Kleider- und MakeHuman-Liste nicht einmal eine CSS-Regel.

Node hat kein DOM; die Attrappe traegt genau das, was die Klasse anfasst:
Reiterknoepfe mit `active`, Zeilen mit `data-garment-id`, einen `<details>`-
Kasten und einen `.anim-folder`. `Reiterinhalt.bauen` liefert ein
Versprechen — die Markierung wartet darauf.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('scene', 'stueckmarkierung.js')

DOM = """
class Klassen {
    constructor() { this.s = new Set(); }
    add(k) { this.s.add(k); } remove(k) { this.s.delete(k); }
    contains(k) { return this.s.has(k); }
}
class Element {
    constructor(art, attribute = {}) {
        this.art = art; this.classList = new Klassen(); this.kinder = [];
        this.parentElement = null; this.style = {}; this.klicks = 0;
        this.open = false; this.textContent = ''; this.gerollt = 0;
        Object.assign(this, attribute);
        for (const k of (this.klassen || [])) this.classList.add(k);
    }
    anhaengen(kind) { kind.parentElement = this; this.kinder.push(kind); return kind; }
    click() {
        // Wie `initTabs`: der geklickte Reiter allein aktiv.
        this.klicks += 1;
        for (const t of wurzel.querySelectorAll('.panel-tab')) t.classList.remove('active');
        this.classList.add('active');
    }
    scrollIntoView() { this.gerollt += 1; }
    alle() { return this.kinder.flatMap(k => [k, ...k.alle()]); }
    closest(selektor) {
        const passt = (el) => selektor.split(',').map(s => s.trim()).some(s =>
            s.startsWith('#') ? el.id === s.slice(1)
            : s.startsWith('.') ? el.classList.contains(s.slice(1)) : el.art === s);
        let el = this;
        while (el) { if (passt(el)) return el; el = el.parentElement; }
        return null;
    }
    querySelector(selektor) { return this.querySelectorAll(selektor)[0] || null; }
    querySelectorAll(selektor) {
        // Nur die Formen, die die Klasse benutzt: `.a.b`, `#id .klasse[data-x="y"]`
        const teile = selektor.trim().split(/\\s+/);
        let kandidaten = this.alle();
        for (const teil of teile) {
            const m = /^(#([\\w-]+))?((?:\\.[\\w-]+)*)(\\[data-([\\w-]+)="([^"]*)"\\])?$/.exec(teil);
            if (!m) throw new Error('Selektor unerwartet: ' + selektor);
            if (m[2]) {
                const start = kandidaten.find(el => el.id === m[2]);
                kandidaten = start ? start.alle() : [];
                continue;
            }
            const klassen = m[3] ? m[3].slice(1).split('.') : [];
            const feld = m[5] && m[5].replace(/-(\\w)/g, (_, b) => b.toUpperCase());
            kandidaten = kandidaten.filter(el =>
                klassen.every(k => el.classList.contains(k))
                && (!feld || el.dataset?.[feld] === m[6]));
        }
        return kandidaten;
    }
}
const wurzel = new Element('body');
globalThis.CSS = { escape: s => s };
globalThis.document = {
    querySelector: s => wurzel.querySelector(s),
    querySelectorAll: s => wurzel.querySelectorAll(s),
    getElementById: id => wurzel.alle().find(el => el.id === id) || null,
};
// Reiterleiste: Modell aktiv, Assets und Kleider daneben.
const reiter = {};
for (const name of ['eigenschaften', 'kleider', 'assets', 'garmentcode']) {
    reiter[name] = wurzel.anhaengen(new Element('div', {klassen: ['panel-tab'], dataset: {tab: name}}));
}
reiter.eigenschaften.classList.add('active');
// Daz-Garderobe: <details> zu, darin Zeilen mit Haken `g9-kleid-<id>`.
// … in einem zugeklappten Bereich (`collapsed` aus `expanded_panels_scene`).
const bereich = wurzel.anhaengen(new Element('div', {klassen: ['panel-section', 'collapsed']}));
const garderobe = bereich.anhaengen(
    new Element('div', {id: 'assets-genesis9-garderobe', klassen: ['anim-tree']}));
const kasten = garderobe.anhaengen(new Element('details'));
const zeileJeans = kasten.anhaengen(new Element('div', {klassen: ['slider-row']}));
zeileJeans.anhaengen(new Element('input', {id: 'g9-kleid-angie_jeans'}));
const zeileShirt = kasten.anhaengen(new Element('div', {klassen: ['slider-row', 'selected']}));
zeileShirt.anhaengen(new Element('input', {id: 'g9-kleid-g9_base_shirt'}));
// MakeHuman-Liste: Ordner zu, Zeile mit data-garment-id.
const mh = wurzel.anhaengen(new Element('div', {id: 'mh-list', klassen: ['anim-tree']}));
const ordner = mh.anhaengen(new Element('div', {klassen: ['anim-folder']}));
const pfeil = ordner.anhaengen(new Element('span', {klassen: ['chevron'], textContent: '▶'}));
const rumpf = ordner.anhaengen(new Element('div', {klassen: ['anim-folder-body'], style: {display: 'none'}}));
const zeileMh = rumpf.anhaengen(
    new Element('div', {klassen: ['anim-item'], dataset: {garmentId: 'shoes01'}}));
// Garment Fit: Kategorie zu.
const gl = wurzel.anhaengen(new Element('div', {id: 'garment-list'}));
const kategorie = gl.anhaengen(new Element('div', {klassen: ['anim-category']}));
const zeileGar = kategorie.anhaengen(
    new Element('div', {klassen: ['anim-item', 'garment-item'], dataset: {garmentId: 'dress01'}}));
"""

SKRIPT = DOM + """
const { fn } = await import(new URL('../gemeinsam/registrierung.js', MODUL).href);
const { Stueckmarkierung } = await import(MODUL);
const aufrufe = [];
fn.garmentcodeVorlageZeigen = v => aufrufe.push(['gc', v]);
fn.kleiderSelectById = v => aufrufe.push(['kleider', v]);
fn.mhAuswahlGeaendert = () => aufrufe.push(['mh']);
Stueckmarkierung.WARTEN_MS = 1;
const zustand = {};
const markierung = new Stueckmarkierung(zustand);

// --- 1. Daz-Stueck auf Genesis 9: Assets-Reiter geklickt, Zeile markiert ---
await markierung.zeigen({key: 'angie_jeans/2'});
pruefe('Assets geklickt', reiter.assets.klicks, 1);
pruefe('Assets aktiv', reiter.assets.classList.contains('active'), true);
pruefe('Kasten offen', kasten.open, true);
pruefe('Bereich offen', bereich.classList.contains('collapsed'), false);
pruefe('Jeans markiert', zeileJeans.classList.contains('selected'), true);
pruefe('Shirt nicht mehr', zeileShirt.classList.contains('selected'), false);
pruefe('im Blick', zeileJeans.gerollt, 1);

// --- 2. Derselbe Reiter noch einmal: kein zweiter Klick ------------------
await markierung.zeigen({key: 'daz_g9_base_shirt/0'});
pruefe('kein zweiter Klick', reiter.assets.klicks, 1);
pruefe('Shirt markiert', zeileShirt.classList.contains('selected'), true);
pruefe('Jeans frei', zeileJeans.classList.contains('selected'), false);

// --- 3. MakeHuman: Zustand, Ordner auf, Zeile, Meldung --------------------
await markierung.zeigen({key: 'mhk_shoes01'});
pruefe('MH-Kennung', zustand._selectedMHId, 'shoes01');
pruefe('Ordner auf', rumpf.style.display, '');
pruefe('Pfeil', pfeil.textContent, '▼');
pruefe('MH-Zeile', zeileMh.classList.contains('selected'), true);
pruefe('MH gemeldet', aufrufe.some(a => a[0] === 'mh'), true);

// --- 4. Garment Fit: `active` wie der eigene Klick, Kategorie offen -------
await markierung.zeigen({key: 'gar_dress01'});
pruefe('Garment-Kennung', zustand._selectedGarmentId, 'dress01');
pruefe('Garment-Zeile', zeileGar.classList.contains('active'), true);
pruefe('Kategorie offen', kategorie.classList.contains('open'), true);

// --- 5. GarmentCode und Kleider gehen an ihre eigene Auswahl --------------
await markierung.zeigen({key: 'gc_hose'});
pruefe('GC-Reiter', reiter.garmentcode.klicks, 1);
await markierung.zeigen({key: 'kld_dress01'});
pruefe('Kleider-Reiter', reiter.kleider.klicks, 1);
pruefe('Auswahlen', aufrufe.filter(a => a[0] !== 'mh'), [['gc', 'hose'], ['kleider', 'dress01']]);

// --- 6. Abwahl: Vorgabereiter, nichts markiert ---------------------------
await markierung.zeigen(null);
pruefe('Modell geklickt', reiter.eigenschaften.klicks, 1);
pruefe('Daz-Marke weg', zeileShirt.classList.contains('selected'), false);
pruefe('MH-Wahl bleibt', zeileMh.classList.contains('selected'), true);

// --- 7. Fehlende Zeile: kein Fehler, nach den Versuchen null --------------
Stueckmarkierung.VERSUCHE = 2;
pruefe('fehlt', await Stueckmarkierung.zeile('daz', 'gibtesnicht'), null);

console.log(JSON.stringify({ok: true}));
"""


class Markierung(SimpleTestCase):
    databases = set()

    def test_reiter_und_zeile(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'))
