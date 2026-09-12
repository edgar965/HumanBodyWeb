# -*- coding: utf-8 -*-
u"""`Gemeinsameregler`: derselbe Block für UMA (Knochen) und HumanBody (Punkte).

WARUM (06.09.2026, Edgar: „ein Name, zwei Übersetzungen"): Ein fachlicher
Regler steht für beide Figurarten an derselben Stelle und stellt darunter,
was die jeweilige Welt kennt. Geprüft wird genau der Unterschied:

1. Bei einer UMA-Figur wandert der Wert in `inst.dna` (Knochen), sofort beim
   Ziehen — UMA rechnet im Browser.
2. Bei einer HumanBody-Figur wandert er in `inst.morphs` (Punkte), und zwar
   erst beim Loslassen: jeder Zwischenschritt wäre ein Serverlauf.
3. Ein Regler mit mehreren Zielen stellt ALLE.
4. Was die Figur nicht kennt, kommt nicht auf die Seite — sonst stünde dort
   ein Schieber, der sich ziehen lässt und nichts tut.
5. Ein Wert unter der Schwelle wird aus `inst.morphs` ENTFERNT, damit die
   Figur keine Nullwerte mitschleppt.
6. Die Gruppe „Nur UMA" erscheint bei einer UMA-Figur und bei einer
   HumanBody-Figur gar nicht (Edgar, 06.09.2026: „die sollen auch irgendwo
   erscheinen" — aber nur dort, wo sie etwas bewirken).

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('scene', 'gemeinsameregler.js')

#: DOM-Attrappe: nur was die Klasse anfasst — Bereich, Kopfzeile, Liste.
DOM = """
class Knoten {
    constructor(id) {
        this.id = id; this._html = ''; this.textContent = ''; this.dataset = {};
        this.kinder = []; this.zuhoerer = {}; this.klassen = new Set();
        this.className = ''; this.title = ''; this.value = '0';
        this.classList = {
            add: (k) => this.klassen.add(k),
            remove: (k) => this.klassen.delete(k),
            contains: (k) => this.klassen.has(k),
        };
    }
    get innerHTML() { return this._html; }
    set innerHTML(v) { this._html = v; this.kinder = []; }
    append(...k) { this.kinder.push(...k); }
    appendChild(k) { this.kinder.push(k); return k; }
    addEventListener(art, f) { (this.zuhoerer[art] = this.zuhoerer[art] || []).push(f); }
    ausloesen(art) { for (const f of this.zuhoerer[art] || []) f(); }
    get parentElement() { return this._eltern || null; }
    querySelector(sel) { return this.suchen(sel)[0] || null; }
    suchen(sel) {
        const treffer = [];
        for (const kind of this.kinder) {
            if (sel === 'input' && kind.tag === 'input') treffer.push(kind);
            if (sel === '.slider-val' && kind.className === 'slider-val') treffer.push(kind);
            treffer.push(...(kind.suchen ? kind.suchen(sel) : []));
        }
        return treffer;
    }
}
const knoten = {};
for (const id of ['prop-gemeinsam-section', 'prop-gemeinsam-kopf', 'prop-gemeinsam-liste']) {
    knoten[id] = new Knoten(id);
}
globalThis.document = {
    getElementById: (id) => knoten[id] || null,
    createElement: (tag) => { const k = new Knoten(null); k.tag = tag; return k; },
    querySelectorAll: () => [],
};
"""

#: Die Tabelle, wie sie der Endpunkt liefert — hier fest, damit kein fetch nötig ist.
TABELLE = """
const TABELLE = {min: -100, max: 100, gruppen: [
    {name: 'Körper', regler: [
        {name: 'bauch', anzeige: 'Bauch', gruppe: 'Körper',
         uma: ['belly'], humanbody: ['Stomach_Volume']},
        {name: 'ohren_groesse', anzeige: 'Ohren', gruppe: 'Körper',
         uma: ['earsSize'], humanbody: ['Ears_SizeX', 'Ears_SizeY']},
        {name: 'nur_uma_kennt_das', anzeige: 'Sonderfall', gruppe: 'Körper',
         uma: ['gibtEsHierNicht'], humanbody: ['GibtEsHierNicht']},
    ]},
    {name: 'Nur UMA', regler: [
        {name: 'nase_schief', anzeige: 'Nase schief', gruppe: 'Nur UMA',
         uma: ['noseBroken']},
    ]},
]};
"""

SKRIPT = DOM + TABELLE + """
const { Gemeinsameregler } = await import(MODUL);
Gemeinsameregler._tabelle = TABELLE;
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const liste = knoten['prop-gemeinsam-liste'];
const schieber = (nr) => liste.kinder[0].kinder[nr + 1].suchen('input')[0];

// === 1. UMA-Figur: der Wert geht in die Knochen, sofort beim Ziehen ==========
let gerufen = 0;
const uma = {quelle: 'uma', dna: {belly: 0.5, earsSize: 0.5, noseBroken: 0.5},
             anwenden() { gerufen++; }};
await Gemeinsameregler.fuellen(uma, {nachAenderung: () => {}});
// Der dritte Regler fehlt der Rasse und darf nicht erscheinen (Fall 4).
pruefe('UMA: zwei Regler', liste.kinder[0].kinder.length - 1, 2);
// Die Gruppe „Nur UMA" kommt bei einer UMA-Figur dazu: 2 + 1 = 3.
pruefe('Gruppen bei UMA', liste.kinder.length, 2);
pruefe('Nur-UMA-Gruppe', liste.kinder[1].kinder[0].textContent, 'Nur UMA (1)');
pruefe('Kopfzeile', knoten['prop-gemeinsam-kopf'].textContent,
       '3 Regler · stellt Knochen');
const bauchUma = schieber(0);
bauchUma.value = '50';
bauchUma.ausloesen('input');
pruefe('UMA: Knochen gestellt', uma.dna.belly, 0.75);
pruefe('UMA: sofort angewandt', gerufen > 0, true);

// Fall 3: ein Regler stellt ALLE seine Ziele.
const ohrenUma = schieber(1);
ohrenUma.value = '-100';
ohrenUma.ausloesen('input');
pruefe('UMA: mehrere Ziele', uma.dna.earsSize, 0);

// === 2. HumanBody-Figur: der Wert geht in die Punkte, erst beim Loslassen ====
const morphDefs = {morphs: [{name: 'Stomach_Volume'}, {name: 'Ears_SizeX'},
                            {name: 'Ears_SizeY'}], meta_sliders: {}};
let neuGeladen = 0;
const hb = {quelle: 'humanbody', morphs: {}, meta: {}};
await Gemeinsameregler.fuellen(hb, {morphDefs, nachAenderung: () => neuGeladen++});
pruefe('HB: zwei Regler', liste.kinder[0].kinder.length - 1, 2);
// Bei HumanBody bleibt „Nur UMA" ganz weg — sonst stünde dort ein Regler
// ohne Wirkung (Edgar, 06.09.2026).
pruefe('keine Nur-UMA-Gruppe bei HumanBody', liste.kinder.length, 1);
pruefe('Kopfzeile HB', knoten['prop-gemeinsam-kopf'].textContent,
       '2 Regler · stellt Punkte');
const bauchHb = schieber(0);
bauchHb.value = '-30';
bauchHb.ausloesen('input');
pruefe('HB: beim Ziehen NICHT gestellt', hb.morphs, {});
pruefe('HB: beim Ziehen kein Serverlauf', neuGeladen, 0);
bauchHb.ausloesen('change');
pruefe('HB: beim Loslassen gestellt', hb.morphs, {Stomach_Volume: -0.3});
pruefe('HB: ein Serverlauf', neuGeladen, 1);

// Fall 3 auf der Punkte-Seite.
const ohrenHb = schieber(1);
ohrenHb.value = '60';
ohrenHb.ausloesen('change');
pruefe('HB: mehrere Ziele', hb.morphs,
       {Stomach_Volume: -0.3, Ears_SizeX: 0.6, Ears_SizeY: 0.6});

// === 5. Zurück auf die Mitte entfernt den Morph, statt 0 zu speichern ========
ohrenHb.value = '0';
ohrenHb.ausloesen('change');
pruefe('HB: Null wird entfernt', hb.morphs, {Stomach_Volume: -0.3});

// === 4b. HumanBody ohne den Morph: die Zeile bleibt weg =====================
await Gemeinsameregler.fuellen(
    {quelle: 'humanbody', morphs: {}, meta: {}},
    {morphDefs: {morphs: [{name: 'Stomach_Volume'}], meta_sliders: {}}});
pruefe('HB: unvollstaendiger Regler faellt weg', liste.kinder[0].kinder.length - 1, 1);

console.log(JSON.stringify({ok: true}));
"""


class GemeinsamereglerTest(SimpleTestCase):

    databases = set()

    def test_derselbe_regler_stellt_knochen_oder_punkte(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
