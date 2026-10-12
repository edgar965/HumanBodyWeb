# -*- coding: utf-8 -*-
"""`Anatomiearbeiter` und `Anatomiearbeit`: Bild und Füllen der Scham-Karten in einem Worker (12.10.2026), in Node mit den echten Modulen.

Edgar: „Ein Worker für Bild und Füllen" (nach dem Zwischenspeicher der Zuordnung blieben 1,5–2 s Rechnung auf dem Hauptfaden). Der Worker rechnet dieselbe `Anatomierechnung` wie der Rückfall auf dem
Hauptfaden; die Fenster der Karten der Haut (Canvas) liest der Hauptfaden (`Anatomiefenster`), die Textur daraus baut er auch (`Anatomietextur`).

Kunstwelt: Haut = Quadrat 50 × 50 mm aus zwei Dreiecken (UV 0–1, Karte 8 × 8 Pixel mit Verlauf), Stück = Quadrat 30 × 30 mm 2 mm darüber, im Atlas 16 × 16 Texel.

Der Arbeiter (`anatomiearbeiter.js`, Attrappe für `self`):
1. `rechnen` → `fertig` mit der Nummer; die Karten sind BIT FÜR BIT die von `Anatomierechnung.rechnen` (mit und ohne Normalen-/Rauheitskarte der Haut), belegt, und jeder Puffer geht übertragen und genau einmal mit.
2. Ein Fehler in der Rechnung kommt als `fehler` mit der Nummer; Fremdes wird überhört.

Der Auftraggeber (`anatomiearbeit.js`, Attrappe für `Worker` und `document`):
3. Ohne `<meta name="anatomiearbeiter">` gibt es keinen Worker (`rechnen` liefert null); mit ihm ein Worker je Auftrag, Modultyp, Pfad aus der Vorlage.
4. Die Nachricht trägt Kopien (kein Original wird übertragen oder leer), ein Feld, das zweimal vorkommt (`uv`/`uvKarte`), geht einmal mit; die Pixel der Fenster gehen mit.
5. `fertig` liefert das Ergebnis und beendet den Worker. Ein neuer Auftrag für DASSELBE Stück überholt den alten (`VERALTET`, Worker beendet, späte Antwort überhört); ein anderes Stück läuft daneben weiter.
6. `fehler` und `onerror` liefern null, setzen `ausgefallen` und verhindern weitere Worker.

Der Importbaum:
7. Von `anatomiearbeiter.js` aus liegt weder Three.js noch DOM (`document`, `window`, `OffscreenCanvas`, `ImageData`) im Baum — sonst startet der Worker im Browser nicht, `Anatomiebacken.bild` fällt STILL auf den Hauptfaden zurück, und nichts wird rot.
   `Anatomiefenster` und `Anatomietextur` (DOM) gehören nicht hinein.
8. Die Vorlage der Szene nennt den Pfad mit Fassung, und `Anatomiebacken.bild` ruft `Anatomiearbeit.rechnen(` und hat den Rückfall `Anatomierechnung.rechnen(`.

Sabotage-Gegenprobe: in `Anatomiearbeiter.puffer` `rauheit` streichen → Fall 1 rot; in `_kopien` `feld.slice()` durch `feld` ersetzen → Fall 4 rot; in `rechnen` `abbrechen(eigner)` streichen → Fall 5 rot; in `_beenden` `terminate()` streichen → Fälle 5, 6 rot;
`ausgefallen = true` streichen → Fall 6 rot; in `Anatomiefuellung` eine Zeile mit `document` → Fall 7 rot. Nicht gelaufen (12.10.2026); im Chrome belegt: Worker-Ergebnis und Hauptfaden-Rückfall sind für Skin 03 in allen drei Karten bitgleich (FNV-Summen).
"""

import json
import re

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

WELT = """
const liste = (a) => (a ? Array.from(a) : a);
const hautDaten = () => ({
    pos: Float32Array.from([0, 0, 0,  0.05, 0, 0,  0.05, 0.05, 0,  0, 0.05, 0]),
    uv: Float32Array.from([0, 0,  1, 0,  1, 1,  0, 1]),
    normal: Float32Array.from([0, 0, 1,  0, 0, 1,  0, 0, 1,  0, 0, 1]),
    ecken: Uint32Array.from([0, 1, 2,  0, 2, 3]),
});
const stueckDaten = () => ({
    pos: Float32Array.from([0.01, 0.01, 0.002,  0.04, 0.01, 0.002,  0.01, 0.04, 0.002,  0.04, 0.04, 0.002]),
    uv: Float32Array.from([0.125, 0.125,  0.875, 0.125,  0.125, 0.875,  0.875, 0.875]),
    index: Uint32Array.from([0, 1, 2,  1, 3, 2]),
    normal: Float32Array.from([0, 0, 1,  0, 0, 1,  0, 0, 1,  0, 0, 1]),
});
// ein Fenster der Karte (8 x 8 Pixel, ganze Karte) mit Verlauf, damit die Texel verschieden ausfallen
const fenster = (wert) => {
    const b = 8, h = 8, daten = new Uint8ClampedArray(b * h * 4);
    for (let y = 0; y < h; y++) for (let x = 0; x < b; x++) {
        const o = 4 * (y * b + x);
        daten[o] = (wert + 25 * x) % 256; daten[o + 1] = (wert + 20 * y) % 256; daten[o + 2] = (wert + 9 * (x + y)) % 256; daten[o + 3] = 255;
    }
    return { daten, x0: 0, y0: 0, b, h, breite: b, hoehe: h, flip: false };
};
"""

ARBEITER = WELT + """
const gesendet = [];
globalThis.self = { postMessage: (nachricht, uebertragen) => gesendet.push({ nachricht, uebertragen }) };
const dir = MODUL.replace('anatomiearbeiter.js', '');
await import(MODUL);
const { Anatomierechnung } = await import(dir + 'anatomierechnung.js');
pruefe('Empfaenger gesetzt', typeof self.onmessage, 'function');

// Die Zuordnung liegt NICHT im Importbaum des Arbeiters (er braucht sie nicht, nur der Hauptfaden) und damit nicht in der Spiegelung dieses Laufs:
// ein eigener Lauf rechnet sie (`ZUORDNUNG`), hier kommt sie als Daten an.
const roh = __ZUORDNUNG__;
const zu = { anzahl: roh.anzahl, texel: Uint32Array.from(roh.texel), btri: Int32Array.from(roh.btri), l2: Float32Array.from(roh.l2),
             l3: Float32Array.from(roh.l3), stri: Int32Array.from(roh.stri), belegt: Uint8Array.from(roh.belegt) };
if (!(zu.anzahl > 100)) throw new Error('Kunstwelt: nur ' + zu.anzahl + ' belegte Texel');
const auftrag = (mit) => {
    const s = stueckDaten();
    return { zu, st: { pos: s.pos, uv: s.uv, normal: s.normal, index: s.index }, ha: hautDaten(), gruppe: Uint8Array.from([0, 0]),
             fenster: [mit ? { farbe: fenster(10), normal: fenster(100), rauh: fenster(200) } : { farbe: fenster(10), normal: null, rauh: null }],
             breite: 16, hoehe: 16, uvKarte: s.uv };
};

// --- 1. rechnen -> fertig, bitgleich zur direkten Rechnung --------------------------------------------------------------------
await self.onmessage({ data: { typ: 'rechnen', id: 7, ...auftrag(true) } });
pruefe('eine Antwort', gesendet.length, 1);
let { nachricht, uebertragen } = gesendet[0];
pruefe('typ und nummer', [nachricht.typ, nachricht.id], ['fertig', 7]);
let e = nachricht.ergebnis, d = await Anatomierechnung.rechnen(auftrag(true));
pruefe('wie direkt gerechnet', [liste(e.farbe), liste(e.normal), liste(e.rauheit)], [liste(d.farbe), liste(d.normal), liste(d.rauheit)]);
pruefe('Karten sind belegt', [new Set(liste(e.farbe)).size > 8, e.farbe.length, e.normal.length, e.rauheit.length], [true, 1024, 1024, 1024]);
pruefe('jeder Puffer uebertragen', [e.farbe, e.normal, e.rauheit].every((a) => uebertragen.includes(a.buffer)), true);
pruefe('keiner doppelt', new Set(uebertragen).size, uebertragen.length);

// ohne Normalen- und Rauheitskarte der Haut: nur die Farbe
await self.onmessage({ data: { typ: 'rechnen', id: 8, ...auftrag(false) } });
({ nachricht, uebertragen } = gesendet[1]);
e = nachricht.ergebnis; d = await Anatomierechnung.rechnen(auftrag(false));
pruefe('nur Farbe', [nachricht.id, e.normal, e.rauheit, liste(e.farbe)], [8, null, null, liste(d.farbe)]);
pruefe('nur ein Puffer', uebertragen.length, 1);

// --- 2. ein Fehler in der Rechnung kommt als `fehler` mit der Nummer; Fremdes wird überhört ----------------------------------
await self.onmessage({ data: { typ: 'rechnen', id: 9, zu: null } });
pruefe('fehler', [gesendet[2].nachricht.typ, gesendet[2].nachricht.id, typeof gesendet[2].nachricht.meldung], ['fehler', 9, 'string']);
await self.onmessage({ data: { typ: 'anderes' } });
await self.onmessage({ data: null });
pruefe('nichts dazu', gesendet.length, 3);
console.log(JSON.stringify({ ok: true }));
"""

ZUORDNUNG = WELT + """
const { Anatomiezuordnung } = await import(MODUL);
const st = stueckDaten(), ha0 = hautDaten();
const zu = await Anatomiezuordnung.rechnen(st, { pos: ha0.pos, ecken: ha0.ecken }, 16, 16);
console.log(JSON.stringify({ ok: true, zu: { anzahl: zu.anzahl, texel: liste(zu.texel), btri: liste(zu.btri), l2: liste(zu.l2), l3: liste(zu.l3),
                                             stri: liste(zu.stri), belegt: liste(zu.belegt) } }));
"""

AUFTRAGGEBER = """
const arbeiter = [];
globalThis.Worker = class {
    constructor(pfad, optionen) { this.pfad = pfad; this.optionen = optionen; this.gesendet = []; this.beendet = false; arbeiter.push(this); }
    postMessage(nachricht, uebertragen) { this.gesendet.push({ nachricht, uebertragen }); }
    terminate() { this.beendet = true; }
};
let meta = null;
globalThis.document = { querySelector: () => (meta ? { content: meta } : null) };
const { Anatomiearbeit: A } = await import(MODUL);
const uv = Float32Array.from([0, 0, 1, 0, 0, 1]);
const auftrag = () => ({
    zu: { anzahl: 1, texel: Uint32Array.from([5]), btri: Int32Array.from([0]), l2: Float32Array.from([0.2]), l3: Float32Array.from([0.3]), stri: Int32Array.from([0]), belegt: Uint8Array.from([0, 1, 0, 0]) },
    st: { pos: Float32Array.from([0, 0, 0, 1, 0, 0, 0, 1, 0]), uv, normal: null, index: Uint32Array.from([0, 1, 2]) },
    ha: { pos: Float32Array.from([0, 0, 0, 1, 0, 0, 0, 1, 0]), uv: Float32Array.from([0, 0, 1, 0, 0, 1]), normal: null, ecken: Uint32Array.from([0, 1, 2]) },
    gruppe: Uint8Array.from([0]),
    fenster: [{ farbe: { daten: Uint8ClampedArray.from([1, 2, 3, 4]), x0: 0, y0: 0, b: 1, h: 1, breite: 1, hoehe: 1, flip: false }, normal: null, rauh: null }, null],
    breite: 2, hoehe: 2, uvKarte: uv,
});
const eigner1 = {}, eigner2 = {};

// --- 3. ohne Meta kein Worker -------------------------------------------------------------------------------------------------
pruefe('ohne Meta', [A.pfad(), A.verfuegbar(), await A.rechnen(auftrag(), eigner1), arbeiter.length], [null, false, null, 0]);
meta = '/statik/v-1/anatomiearbeiter.js';
pruefe('mit Meta', A.verfuegbar(), true);

// --- 4. Nachricht: Kopien, jedes Feld einmal, Pixel der Fenster gehen mit ---------------------------------------------------------
const a = auftrag();
const p1 = A.rechnen(a, eigner1);
pruefe('ein Worker, Modultyp, Pfad', [arbeiter.length, arbeiter[0].optionen, arbeiter[0].pfad], [1, { type: 'module' }, '/statik/v-1/anatomiearbeiter.js']);
const { nachricht, uebertragen } = arbeiter[0].gesendet[0];
pruefe('nachricht', [nachricht.typ, nachricht.id, Object.keys(nachricht).sort()],
       ['rechnen', 1, ['breite', 'fenster', 'gruppe', 'ha', 'hoehe', 'id', 'st', 'typ', 'uvKarte', 'zu']]);
pruefe('Kopien statt Originale', [nachricht.zu.texel !== a.zu.texel, nachricht.zu.belegt !== a.zu.belegt, nachricht.st.pos !== a.st.pos, nachricht.ha.ecken !== a.ha.ecken, nachricht.gruppe !== a.gruppe],
       [true, true, true, true, true]);
pruefe('uv und uvKarte: eine Kopie', [nachricht.st.uv === nachricht.uvKarte, nachricht.uvKarte !== uv], [true, true]);
pruefe('Originale unberuehrt', [a.zu.belegt.length, a.st.pos.length, uv.length], [4, 9, 6]);
pruefe('Fenster-Pixel gehen mit', nachricht.fenster[0].farbe.daten === a.fenster[0].farbe.daten, true);
const kopien = [nachricht.zu.texel, nachricht.zu.btri, nachricht.zu.l2, nachricht.zu.l3, nachricht.zu.stri, nachricht.zu.belegt, nachricht.st.pos, nachricht.st.uv, nachricht.st.index,
                nachricht.ha.pos, nachricht.ha.uv, nachricht.ha.ecken, nachricht.gruppe, nachricht.fenster[0].farbe.daten];
pruefe('alles uebertragen', kopien.every((x) => uebertragen.includes(x.buffer)), true);
pruefe('keiner doppelt', new Set(uebertragen).size, uebertragen.length);

// --- 5. fertig, Überholen, anderes Stück ------------------------------------------------------------------------------------------
arbeiter[0].onmessage({ data: { typ: 'fertig', id: 1, ergebnis: { x: 1 } } });
pruefe('liefert das Ergebnis', await p1, { x: 1 });
pruefe('Worker beendet', arbeiter[0].beendet, true);

const b1 = A.rechnen(auftrag(), eigner1);
const b2 = A.rechnen(auftrag(), eigner1);
pruefe('erster veraltet', await b1, A.VERALTET);
pruefe('erster Worker beendet', arbeiter[1].beendet, true);
arbeiter[1].onmessage({ data: { typ: 'fertig', id: 2, ergebnis: { x: 'spaet' } } });          // zu spät: überhört
arbeiter[2].onmessage({ data: { typ: 'fertig', id: 3, ergebnis: { x: 2 } } });
pruefe('zweiter liefert', await b2, { x: 2 });

const c1 = A.rechnen(auftrag(), eigner1);
const c2 = A.rechnen(auftrag(), eigner2);
pruefe('anderes Stueck: kein Abbruch', [arbeiter[3].beendet, arbeiter[4].beendet], [false, false]);
arbeiter[4].onmessage({ data: { typ: 'fertig', id: 5, ergebnis: 'zwei' } });
arbeiter[3].onmessage({ data: { typ: 'fertig', id: 4, ergebnis: 'eins' } });
pruefe('beide liefern', [await c1, await c2], ['eins', 'zwei']);

// --- 6. Fehler: null, ausgefallen, kein neuer Worker ----------------------------------------------------------------------------
const f1 = A.rechnen(auftrag(), eigner1);
arbeiter[5].onmessage({ data: { typ: 'fehler', id: 6, meldung: 'kaputt' } });
pruefe('fehler gibt null', await f1, null);
pruefe('Worker beendet, ausgefallen', [arbeiter[5].beendet, A.ausgefallen, A.verfuegbar()], [true, true, false]);
pruefe('danach kein Worker mehr', [await A.rechnen(auftrag(), eigner1), arbeiter.length], [null, 6]);

A.ausgefallen = false;                                                                      // der Weg über `onerror`
const f2 = A.rechnen(auftrag(), eigner2);
arbeiter[6].onerror({ message: 'Modul nicht gefunden', preventDefault() {} });
pruefe('onerror gibt null', [await f2, A.ausgefallen, arbeiter[6].beendet], [null, true, true]);
console.log(JSON.stringify({ ok: true }));
"""


class AnatomiearbeitTest(SimpleTestCase):
    databases = set()

    def test_1_der_arbeiter_rechnet_bitgleich_wie_der_hauptfaden(self):
        zuordnung = Jsmodul('gemeinsam', 'anatomiezuordnung.js').laufen(ZUORDNUNG)['zu']
        self.assertTrue(Jsmodul('gemeinsam', 'anatomiearbeiter.js').laufen(ARBEITER.replace('__ZUORDNUNG__', json.dumps(zuordnung))).get('ok'))

    def test_2_der_auftraggeber_haelt_ein_protokoll(self):
        self.assertTrue(Jsmodul('gemeinsam', 'anatomiearbeit.js').laufen(AUFTRAGGEBER).get('ok'))

    def test_3_der_arbeiter_kennt_weder_three_noch_das_dom(self):
        """Ein Import von Three.js, `document` oder `OffscreenCanvas` irgendwo im Importbaum des Workers wirft erst im Browser — und still: der Worker startet nicht, `Anatomiearbeit` fällt auf den
        Hauptfaden zurück, und die Rechnung steht wieder zwischen dem Zeichnen, ohne dass etwas rot wird. Hier wird der ganze Baum von `anatomiearbeiter.js` aus gelesen."""
        gemeinsam = Jsmodul.VIEWER / 'gemeinsam'
        offen, gelesen = ['anatomiearbeiter.js'], {}
        while offen:
            name = offen.pop()
            if name in gelesen:
                continue
            text = (gemeinsam / name).read_text(encoding='utf-8')
            text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
            gelesen[name] = re.sub(r'(?m)//.*$', '', text)
            offen += re.findall(r"from '\./(\w+\.js)'", text)
        for erwartet in ('anatomierechnung.js', 'anatomiebild.js', 'anatomiefuellung.js', 'anatomieproben.js', 'anatomiedreiecke.js', 'anatomierahmen.js'):
            self.assertIn(erwartet, gelesen, 'der Importbaum wurde nicht vollständig gelesen')
        for dom in ('anatomiefenster.js', 'anatomietextur.js', 'anatomiearbeit.js', 'protokoll.js'):
            self.assertNotIn(dom, gelesen, f'{dom} gehört auf den Hauptfaden')
        for name, code in gelesen.items():
            self.assertNotIn("from 'three'", code, name)
            self.assertNotIn("from '/static/", code, name)
            for verboten in ('document', 'window', 'localStorage', 'OffscreenCanvas', 'ImageData'):
                self.assertIsNone(re.search(r'\b%s\b' % verboten, code), '%s braucht %s' % (name, verboten))

    def test_4_die_vorlage_nennt_den_pfad_und_das_backen_hat_den_rueckfall(self):
        vorlage = (settings.BASE_DIR / 'templates' / 'scene_config.html').read_text(encoding='utf-8')
        self.assertIn('<meta name="anatomiearbeiter" content="{% fassungspfad \'viewer/gemeinsam/anatomiearbeiter.js\' %}">', vorlage)
        backen = (Jsmodul.VIEWER / 'gemeinsam' / 'anatomiebacken.js').read_text(encoding='utf-8')
        bild = backen.split('static async bild(', 1)[1].split('\n    }\n', 1)[0]
        self.assertIn('Anatomiearbeit.rechnen(', bild)
        self.assertIn('Anatomiearbeit.VERALTET', bild)
        self.assertIn('Anatomierechnung.rechnen(', bild)             # der Rückfall ohne Worker
        self.assertIn('Anatomiefenster.lesen(', bild)
