# -*- coding: utf-8 -*-
"""`Baumsortierung`: Baumlisten und Listen stehen alphabetisch (Edgar, 10.10.2026: „mach das auch" — die Baumlisten waren bei den Combo-Boxen
ausgenommen), geprüft in Node an einer kleinen DOM-Attrappe (Kinder, `querySelectorAll` mit `:scope >`, `matches`, `append`).

1. `ordnen` ohne `anhaengen`: Einträge nach Namen (ohne Groß-/Kleinschreibung, Zahlen als Zahlen), Nicht-Einträge bleiben an ihrem Platz.
2. `ordnen` mit `anhaengen` und `vorn`: eine Zeile samt dem, was hinter ihr steht („Einstellungen"), wandert als Gruppe; Sammeleinträge
   („Kleidung – Generisch …") stehen vorn; was vor der ersten Zeile steht (Überschrift), bleibt.
3. Beschriftungen: Kopf eines Kastens ohne Pfeil und Zähler, Kategorie der Garderobe ohne „(98)", Eintrag nach `dataset.name`.
4. `sortiere` an den vier Formen: Liste „Getragen", Kategorie der Garderobe, Körper eines Kastens (Kästen und Einträge je für sich, an den
   Plätzen ihrer Art), und die Kästen im Elternelement.
5. Eine schon sortierte Liste wird nicht angefasst (Rückgabe `false`, kein `append`); `data-reihenfolge="fest"` lässt sie, wie sie ist.

Sabotage-Gegenprobe: in `ordnen` die Zeile `neu.some(…) ? neu : null` auf `neu` setzen → Fall 5 rot (jede Liste würde bei jeder Änderung neu
gesetzt, der Beobachter liefe endlos); die Gruppenbildung (`aktuell.push(k)`) streichen → Fall 2 rot („Einstellungen" bliebe an der Stelle); die Zeile
mit `vorn ?` auf `[]` setzen → Fall 2 rot (die Sammeleinträge sortierten sich ein); `Combosortierung.schluessel` weglassen (Datum) merkt dieser Test
nicht — den prüft `test_js_combosortierung`.

Nicht getestet (kein DOM in Node): der `MutationObserver` und die Selektoren gegen echtes HTML — im Chrome an den echten Listen geprüft.
Nicht gelaufen — läuft nur auf Ansage.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'baumsortierung.js')

SKRIPT = """
// ---- DOM-Attrappe: Kinder, Selektoren der Form „tag.klasse", „.klasse", „#id", durch Komma getrennt, optional mit „:scope > "
class El {
    constructor(tag, { cls = '', id = '', text = '', kids = [], dataset = {} } = {}) {
        Object.assign(this, { tagName: tag.toUpperCase(), className: cls, id, dataset, nodeType: 1, isConnected: true, fest: false });
        this._text = text; this.children = []; this.aenderungen = 0; this.parentElement = null;
        kids.forEach(k => this.add(k));
    }
    add(k) { k.parentElement = this; this.children.push(k); return k; }
    get firstElementChild() { return this.children[0] || null; }
    get textContent() { return this._text + this.children.map(k => k.textContent).join(''); }
    get childNodes() { return [...(this._text ? [{ nodeType: 3, textContent: this._text }] : []), ...this.children]; }
    _passt(teil) {
        const m = teil.trim().match(/^([a-z0-9]+)?(?:#([a-z0-9_-]+))?((?:[.][a-z0-9_-]+)*)$/i);
        if (!m) throw new Error('Selektor nicht verstanden: ' + teil);
        const klassen = this.className.split(' ');
        return (!m[1] || this.tagName === m[1].toUpperCase()) && (!m[2] || this.id === m[2])
            && m[3].split('.').filter(Boolean).every(c => klassen.includes(c));
    }
    matches(sel) { return sel.split(',').some(t => this._passt(t)); }
    closest(sel) { return sel.includes('data-reihenfolge') && this.fest ? this : null; }
    _alle(nur) { return nur ? this.children : this.children.flatMap(k => [k, ...k._alle(false)]); }
    querySelectorAll(sel) {
        const teile = sel.split(',').map(t => t.trim());
        const ergebnis = new Set();
        for (const t of teile) {
            const direkt = t.startsWith(':scope >');
            const regel = t.replace(':scope >', '').trim();
            this._alle(direkt).filter(k => k._passt(regel)).forEach(k => ergebnis.add(k));
        }
        return [...this._alle(false)].filter(k => ergebnis.has(k));
    }
    querySelector(sel) { return this.querySelectorAll(sel)[0] || null; }
    append(...neu) { this.aenderungen += 1; this.children = neu; }
}
const { Baumsortierung: B } = await import(MODUL);
const namen = kinder => kinder.map(k => k.name || k.textContent);
const mk = (name, extra = {}) => Object.assign(new El('div', { text: name, cls: extra.cls || '' }), { name });

// 1. ordnen ohne anhaengen
const a = [mk('b'), mk('Haupt'), mk('A2'), mk('a10'), mk('a9')];
const sortiert = B.ordnen(a, [a[0], a[2], a[3], a[4]], e => e.name);
pruefe('Einträge sortiert, Nicht-Eintrag am Platz', namen(sortiert), ['A2', 'Haupt', 'a9', 'a10', 'b']);
pruefe('schon sortiert → null', B.ordnen([mk('a'), mk('b')], [], e => e.name), null);
const s2 = [mk('a'), mk('b')];
pruefe('schon sortiert → null (mit Einträgen)', B.ordnen(s2, s2, e => e.name), null);

// 2. mit anhaengen und vorn
const kopf = mk('Überschrift');
const generisch = mk('Kleidung – Generisch: Oberteile'), gEinst = mk('Einstellungen G');
const zebra = mk('Zebra Top'), zEinst = mk('Einstellungen Z'), angie = mk('Angie Top'), aEinst = mk('Einstellungen A');
const kinder = [kopf, zebra, zEinst, generisch, gEinst, angie, aEinst];
const gruppiert = B.ordnen(kinder, [zebra, generisch, angie], e => e.name, { anhaengen: true, vorn: n => /Generisch/.test(n) });
pruefe('Gruppen wandern mit, Sammeleintrag vorn, Überschrift bleibt',
       namen(gruppiert), ['Überschrift', 'Kleidung – Generisch: Oberteile', 'Einstellungen G', 'Angie Top', 'Einstellungen A', 'Zebra Top', 'Einstellungen Z']);

// 3. Beschriftungen
const kasten = new El('div', { cls: 'anim-category', kids: [new El('div', { cls: 'anim-category-header', kids: [
    new El('span', { cls: 'cat-chevron', text: '>' }), new El('span', { text: 'Röcke' }), new El('span', { cls: 'cat-count', text: '19' })] })] });
pruefe('Kopf ohne Pfeil und Zähler', B.kopfname(kasten), 'Röcke');
// Kleider und MakeHuman: der Pfeil ist ein Element, der Zähler steht als Text hinter dem Namen; geöffnet steht ▼ statt ▶ (im Chrome sortierte
// sich das geöffnete „dresses" hinter alle geschlossenen, solange der Pfeil mitzählte)
const ordner = (n, pfeil) => new El('div', { cls: 'anim-folder', kids: [new El('div', { cls: 'anim-folder-header', text: ' ' + n + ' (27)', kids: [new El('span', { cls: 'chevron', text: pfeil })] })] });
pruefe('Ordnerkopf ohne Pfeil und Zähler', B.kopfname(ordner('accessories', '▶')), 'accessories');
const ordnerliste = new El('div', { id: 'kleider-list', kids: [ordner('pants', '▶'), ordner('dresses', '▼'), ordner('accessories', '▶')] });
B.sortiere(ordnerliste);
pruefe('geöffneter Ordner sortiert sich ein', ordnerliste.children.map(k => B.kopfname(k)), ['accessories', 'dresses', 'pants']);
const kategorie = new El('details', { cls: 'g9-kategorie', kids: [new El('summary', { text: 'Oberteile ', kids: [new El('span', { cls: 'gedaempft', text: '(98)' })] })] });
pruefe('Kategorie ohne Zähler', B.kategoriename(kategorie), 'Oberteile');
pruefe('Eintrag nach dataset.name', B.eintragsname(new El('div', { cls: 'anim-item', dataset: { name: 'Walk' }, text: 'x' })), 'Walk');
pruefe('Eintrag nach Namensfeld', B.eintragsname(new El('div', { cls: 'anim-item', kids: [new El('span', { cls: 'kld-name', text: 'Jacke' }), new El('span', { text: '3f' })] })), 'Jacke');

// 4. sortiere an den vier Formen
const li = (n) => new El('li', { kids: [new El('span', { cls: 'equipped-item-name', text: n })] });
const getragen = new El('ul', { id: 'prop-equipped-list', kids: [li('Asian Schuhe'), li('Asian Haar Bang'), li('Asian Augen')] });
pruefe('Getragen: geändert', B.sortiere(getragen), true);
pruefe('Getragen: Reihenfolge', getragen.children.map(k => B.text(k)), ['Asian Augen', 'Asian Haar Bang', 'Asian Schuhe']);

const zeile = (n) => new El('div', { cls: 'slider-row', kids: [new El('label', { cls: 'stueckname', text: n })] });
const einst = (n) => new El('details', { cls: 'uma-gruppe', text: 'Einstellungen ' + n });
const garderobe = new El('details', { cls: 'g9-kategorie', kids: [new El('summary', { text: 'Oberteile' }), zeile('Zebra'), einst('Z'), zeile('Kleidung – Generisch: Oberteile'), einst('G'), zeile('Angie'), einst('A')] });
pruefe('Garderobe: geändert', B.sortiere(garderobe), true);
pruefe('Garderobe: Reihenfolge', garderobe.children.map(k => B.text(k)),
       ['Oberteile', 'Kleidung – Generisch: Oberteile', 'Einstellungen G', 'Angie', 'Einstellungen A', 'Zebra', 'Einstellungen Z']);

const kastenNamed = (n) => new El('div', { cls: 'anim-category', kids: [new El('div', { cls: 'anim-category-header', kids: [new El('span', { text: n })] })] });
const eintrag = (n) => new El('div', { cls: 'anim-item', dataset: { name: n }, text: n });
const koerper = new El('div', { cls: 'anim-category-body', kids: [eintrag('b'), kastenNamed('Zeta'), eintrag('a'), kastenNamed('Alpha')] });
pruefe('Körper: geändert', B.sortiere(koerper), true);
pruefe('Körper: Einträge und Kästen je an den Plätzen ihrer Art', koerper.children.map(k => k.dataset.name || B.kopfname(k)), ['a', 'Alpha', 'b', 'Zeta']);

const baum = new El('div', { id: 'anim-tree', kids: [kastenNamed('Tanz'), kastenNamed('Gehen'), kastenNamed('Idle')] });
pruefe('Kästen im Elternelement: geändert', B.sortiere(baum), true);
pruefe('Kästen im Elternelement: Reihenfolge', baum.children.map(k => B.kopfname(k)), ['Gehen', 'Idle', 'Tanz']);

// 5. schon sortiert / fest
const vorher = getragen.aenderungen;
pruefe('sortiert: Rückgabe', B.sortiere(getragen), false);
pruefe('sortiert: nicht angefasst', getragen.aenderungen, vorher);
const fest = new El('ul', { id: 'prop-equipped-list', kids: [li('Zebra'), li('Alpha')] });
fest.fest = true;
pruefe('fest: Rückgabe', B.sortiere(fest), false);
pruefe('fest: Reihenfolge bleibt', fest.children.map(k => B.text(k)), ['Zebra', 'Alpha']);
console.log(JSON.stringify({ ok: true }));
"""


class BaumsortierungTest(SimpleTestCase):
    databases = set()

    def test_baumlisten_und_listen_stehen_alphabetisch_gruppen_wandern_mit(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
