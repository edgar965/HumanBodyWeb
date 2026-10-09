# -*- coding: utf-8 -*-
"""Die Haut-Maske im Worker (09.10.2026): `Hautrechnung`, `Hautarbeiter`, `Hautarbeit` — in Node, mit den echten Modulen.

WARUM (Edgar: „warum dauert laden des Characters ewig … ich brauche schnelles Anzeigen damit ich drehen und vergrößern kann"):
`Hautverdeckung.anwenden` hielt den Hauptfaden am feinen Körper (104.480 Punkte, 7 Stücke) 2,8 s im Leerlauf, 11–14 s belastet, auf
der Filmstufe bis 19 s. Die Zahlenrechnung läuft jetzt in einem Web Worker; der Hauptfaden schreibt nur das Ergebnis. Es ist
derselbe Code (`Hautrechnung.rechnen`) auf beiden Wegen — geprüft wird, dass das Ergebnis dasselbe ist und dass das Protokoll hält:

1. `Hautrechnung.rechnen` = die Bausteine einzeln: Maske wie `Hautmaske.verdeckt`; der Einzug mit den schon gerechneten Normalen
   (`hautnormalen`) Bit für Bit wie ohne sie (die Option spart nur die zweite Rechnung); verdeckte Punkte wandern nach innen,
   freie nicht; ohne Stücke nichts verdeckt.
2. `Hautarbeiter`: eine Nachricht `rechnen` → `fertig` mit derselben Rechnung, jeder Puffer des Ergebnisses übertragen und keiner
   doppelt (eine doppelte Nennung wirft beim Übertragen); ein Fehler in der Rechnung → `fehler` mit der Nummer; Fremdes wird ignoriert.
3. `Hautarbeit`: ein Worker je Auftrag (Modultyp), vom Netz geht nichts mit, die Puffer sind Kopien und werden übertragen; ein
   neuer Auftrag überholt den alten (`VERALTET`, Worker beendet, späte Antwort ignoriert); ein Fehler → null, `ausgefallen`, danach
   kein neuer Worker.

Sabotage: `hautnormalen` ignorieren und die Normalen anders rechnen → Fall 1 rot; in `Hautarbeiter.puffer` `.buffer` weglassen oder den
`Set` entfernen → Fall 2 rot; in `Hautarbeit.rechnen` das `abbrechen()` weglassen → Fall 3 rot.

Gelaufen am 09.10.2026 (3 Fälle grün); Sabotage `abbrechen()` weglassen: Fall 3 rot. Regel: `szene-ladezeit.md`.
"""
import re

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

KOERPER = """
// Ein Zylinder um die y-Achse: `ringe` Reihen zu `n` Punkten (Wicklung nach aussen).
function zylinder(radius, y0, y1, ringe, n) {
    const P = [], T = [];
    for (let r = 0; r < ringe; r++) {
        const y = y0 + (y1 - y0) * r / (ringe - 1);
        for (let i = 0; i < n; i++) { const w = 2 * Math.PI * i / n; P.push(radius * Math.cos(w), y, radius * Math.sin(w)); }
    }
    for (let r = 0; r + 1 < ringe; r++) for (let i = 0; i < n; i++) {
        const a = r * n + i, b = r * n + (i + 1) % n, c = (r + 1) * n + i, d = (r + 1) * n + (i + 1) % n;
        T.push(a, c, b, b, c, d);
    }
    return { P: Float32Array.from(P), T: Uint32Array.from(T) };
}
const koerper = zylinder(0.10, 0.0, 1.0, 51, 36);
const stoff = zylinder(0.102, 0.30, 0.70, 41, 36);          // 2 mm ueber der Haut: anliegend
const stoffe = () => [{ schluessel: 'rohr', punkte: stoff.P.slice(), dreiecke: stoff.T.slice() }];
const liste = (a) => Array.from(a);
"""

RECHNUNG = KOERPER + """
const dir = MODUL.replace('hautrechnung.js', '');
const { Hautrechnung } = await import(MODUL);
const { Hautmaske } = await import(dir + 'hautmaske.js');
const { Hauteinzugrechnung } = await import(dir + 'hauteinzugrechnung.js');
const { Hautmaskegeometrie: G } = await import(dir + 'hautmaskegeometrie.js');
const { Saumschnitt } = await import(dir + 'saumschnitt.js');

const r = Hautrechnung.rechnen(koerper.P, koerper.T, stoffe());
const n = koerper.P.length / 3;

// --- 1. die Bausteine einzeln --------------------------------------------------------------------------------------------
pruefe('maske wie Hautmaske.verdeckt', liste(r.maske), liste(Hautmaske.verdeckt(koerper.P, koerper.T, stoffe())));
const verdeckt = r.maske.reduce((a, b) => a + b, 0);
if (!(verdeckt > 500 && verdeckt < n)) throw new Error('Kunstkoerper: ' + verdeckt + ' von ' + n + ' verdeckt');
pruefe('normalen wie Hautmaskegeometrie', liste(r.normalen), liste(G.normalen(koerper.P, koerper.T)));

// Der Einzug ohne die schon gerechneten Normalen: dasselbe, Bit fuer Bit.
const ohne = Hauteinzugrechnung.rechnen(koerper.P, r.maske, koerper.T, { kanten: Saumschnitt.kanten(stoffe()) });
pruefe('einzug ohne hautnormalen', [liste(ohne.werte), ohne.gesetzt, ohne.geschnappt, ohne.band, liste(ohne.weg)],
       [liste(r.einzug.werte), r.einzug.gesetzt, r.einzug.geschnappt, r.einzug.band, liste(r.einzug.weg)]);

// Verdeckte Punkte wandern nach innen (hoechstens `TIEFE_M` = 10 mm), freie bleiben stehen.
let frei = 0, bewegt = 0;
for (let i = 0; i < n; i++) {
    const l = Math.hypot(r.einzug.werte[3 * i], r.einzug.werte[3 * i + 1], r.einzug.werte[3 * i + 2]);
    if (!r.maske[i]) { if (l !== 0) frei += 1; continue; }
    if (l > 0.0101) throw new Error('Einzug ' + l + ' m bei Punkt ' + i);
    if (l > 0) bewegt += 1;
}
pruefe('freie Punkte ohne Einzug', frei, 0);
if (bewegt < verdeckt * 0.9) throw new Error('nur ' + bewegt + ' von ' + verdeckt + ' verdeckten Punkten eingezogen');
pruefe('gesetzt zaehlt die verdeckten', r.einzug.gesetzt, verdeckt);

// --- 1b. ohne Stuecke nichts verdeckt ------------------------------------------------------------------------------------
const leer = Hautrechnung.rechnen(koerper.P, koerper.T, []);
pruefe('ohne stuecke', [leer.maske.reduce((a, b) => a + b, 0), leer.einzug.gesetzt, leer.randabstaende], [0, 0, []]);
console.log(JSON.stringify({ ok: true, verdeckt, ms: r.ms >= 0 }));
"""

ARBEITER = KOERPER + """
const gesendet = [];
globalThis.self = { postMessage: (nachricht, uebertragen) => gesendet.push({ nachricht, uebertragen }) };
const dir = MODUL.replace('hautarbeiter.js', '');
await import(MODUL);
const { Hautrechnung } = await import(dir + 'hautrechnung.js');
pruefe('Empfaenger gesetzt', typeof self.onmessage, 'function');

const auftrag = (id, pos = koerper.P, index = koerper.T) => ({ data: { typ: 'rechnen', id, pos: pos && pos.slice(), index: index && index.slice(), stoffe: stoffe() } });

// --- 2. rechnen -> fertig ------------------------------------------------------------------------------------------------
self.onmessage(auftrag(7));
pruefe('eine Antwort', gesendet.length, 1);
const { nachricht, uebertragen } = gesendet[0];
pruefe('typ und nummer', [nachricht.typ, nachricht.id], ['fertig', 7]);
const e = nachricht.ergebnis, direkt = Hautrechnung.rechnen(koerper.P, koerper.T, stoffe());
pruefe('wie direkt gerechnet', [liste(e.maske), liste(e.einzug.werte), liste(e.einzug.weg)],
       [liste(direkt.maske), liste(direkt.einzug.werte), liste(direkt.einzug.weg)]);
const puffer = [e.maske, e.ersatz, e.hoehe, e.rand, e.normalen, e.einzug.werte, e.einzug.weg].map((a) => a.buffer);
pruefe('jeder Puffer uebertragen', puffer.every((b) => uebertragen.includes(b)), true);
pruefe('keiner doppelt', new Set(uebertragen).size, uebertragen.length);

// --- 2b. ein Fehler in der Rechnung kommt als `fehler` mit der Nummer --------------------------------------------------
self.onmessage(auftrag(8, null, null));
pruefe('fehler', [gesendet[1].nachricht.typ, gesendet[1].nachricht.id, typeof gesendet[1].nachricht.meldung], ['fehler', 8, 'string']);

// --- 2c. Fremdes wird ignoriert ----------------------------------------------------------------------------------------
self.onmessage({ data: { typ: 'anderes' } });
self.onmessage({ data: null });
pruefe('nichts dazu', gesendet.length, 2);
console.log(JSON.stringify({ ok: true }));
"""

CLIENT = """
const arbeiter = [];
globalThis.Worker = class {
    constructor(pfad, optionen) { this.pfad = pfad; this.optionen = optionen; this.gesendet = []; this.beendet = false; arbeiter.push(this); }
    postMessage(nachricht, uebertragen) { this.gesendet.push({ nachricht, uebertragen }); }
    terminate() { this.beendet = true; }
};
const { Hautarbeit } = await import(MODUL);
const P = Float32Array.from([0, 0, 0, 1, 0, 0, 0, 1, 0]), T = Uint32Array.from([0, 1, 2]);
const stoff = (z) => ({ schluessel: 's', punkte: Float32Array.from([0, 0, z, 1, 0, z, 0, 1, z]), dreiecke: Uint32Array.from([0, 1, 2]),
                        tiefe: undefined, starr: false, nahe: undefined, ersatz: false, netz: { vom: 'Three.js' } });

// --- 3. ein Worker je Auftrag, nur Zahlenwerk, Kopien uebertragen ------------------------------------------------------
const a = Hautarbeit.rechnen(P, T, [stoff(0.001)]);
pruefe('ein Worker, Modultyp', [arbeiter.length, arbeiter[0].optionen], [1, { type: 'module' }]);
const { nachricht, uebertragen } = arbeiter[0].gesendet[0];
pruefe('nachricht', [nachricht.typ, nachricht.id, Object.keys(nachricht.stoffe[0]).sort()],
       ['rechnen', 1, ['dreiecke', 'ersatz', 'nahe', 'punkte', 'schluessel', 'starr', 'tiefe']]);
pruefe('kopien statt Original', [nachricht.pos !== P, nachricht.index !== T, nachricht.stoffe[0].punkte.length], [true, true, 9]);
pruefe('kopien uebertragen', [nachricht.pos, nachricht.index, nachricht.stoffe[0].punkte, nachricht.stoffe[0].dreiecke]
       .every((x) => uebertragen.includes(x.buffer)), true);

// --- 3b. ein neuer Auftrag ueberholt den alten ---------------------------------------------------------------------------
const b = Hautarbeit.rechnen(P, T, [stoff(0.002)]);
pruefe('erster veraltet', await a, Hautarbeit.VERALTET);
pruefe('erster Worker beendet', arbeiter[0].beendet, true);
arbeiter[0].onmessage({ data: { typ: 'fertig', id: 1, ergebnis: { x: 1 } } });          // zu spaet: ignoriert
arbeiter[1].onmessage({ data: { typ: 'fertig', id: 2, ergebnis: { x: 2 } } });
pruefe('zweiter liefert', await b, { x: 2 });
pruefe('zweiter Worker beendet', arbeiter[1].beendet, true);

// --- 3c. ein Fehler: null, ausgefallen, kein neuer Worker ----------------------------------------------------------------
const c = Hautarbeit.rechnen(P, T, [stoff(0.003)]);
arbeiter[2].onmessage({ data: { typ: 'fehler', id: 3, meldung: 'kaputt' } });
pruefe('fehler gibt null', await c, null);
pruefe('ausgefallen', Hautarbeit.ausgefallen, true);
pruefe('danach kein Worker mehr', [await Hautarbeit.rechnen(P, T, [stoff(0.004)]), arbeiter.length], [null, 3]);
console.log(JSON.stringify({ ok: true }));
"""


class HautrechnungTest(SimpleTestCase):
    databases = set()

    def test_1_die_rechnung_ist_die_summe_der_bausteine(self):
        self.assertTrue(Jsmodul('gemeinsam', 'hautrechnung.js').laufen(RECHNUNG).get('ok'))

    def test_2_der_arbeiter_antwortet_mit_uebertragenen_puffern(self):
        self.assertTrue(Jsmodul('gemeinsam', 'hautarbeiter.js').laufen(ARBEITER).get('ok'))

    def test_3_der_auftraggeber_haelt_ein_protokoll(self):
        self.assertTrue(Jsmodul('gemeinsam', 'hautarbeit.js').laufen(CLIENT).get('ok'))

    def test_4_der_arbeiter_kennt_weder_three_noch_das_dom(self):
        """Ein Import von Three.js, `document` oder `window` irgendwo im Importbaum des Workers wirft erst im Browser — und
        still: der Worker startet nicht, `Hautarbeit` fällt auf den Hauptfaden zurück, und der Block von 3–14 s ist wieder da,
        ohne dass etwas rot wird. Hier wird der ganze Baum von `hautarbeiter.js` aus gelesen."""
        gemeinsam = Jsmodul.VIEWER / 'gemeinsam'
        offen, gelesen = ['hautarbeiter.js'], {}
        while offen:
            name = offen.pop()
            if name in gelesen:
                continue
            text = (gemeinsam / name).read_text(encoding='utf-8')
            text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
            gelesen[name] = re.sub(r'(?m)//.*$', '', text)
            offen += re.findall(r"from '\./(\w+\.js)'", text)
        for erwartet in ('hautrechnung.js', 'hautmaske.js', 'hauteinzugrechnung.js', 'saumband.js', 'hautwege.js', 'hautdicke.js'):
            self.assertIn(erwartet, gelesen, 'der Importbaum wurde nicht vollständig gelesen')
        for name, code in gelesen.items():
            self.assertNotIn("from 'three'", code, name)
            self.assertNotIn("from '/static/", code, name)
            for verboten in ('document', 'window', 'localStorage'):
                self.assertIsNone(re.search(r'\b%s\b' % verboten, code), '%s braucht %s' % (name, verboten))

    def test_5_die_szene_ruft_den_arbeiter_und_die_vorlage_nennt_den_pfad(self):
        szene = (Jsmodul.VIEWER / 'gemeinsam' / 'hautverdeckung.js').read_text(encoding='utf-8')
        self.assertIn('inst._maskeVersion = (inst._maskeVersion || 0) + 1;', szene)        # jeder Plan überholt den Auftrag
        self.assertIn('Hautverdeckung.anwendenAsync(inst, () => inst._maskeVersion === lauf)', szene)
        self.assertIn('Hautarbeit.rechnen(', szene)
        vorlage = (settings.BASE_DIR / 'templates' / 'scene_config.html').read_text(encoding='utf-8')
        self.assertIn('<meta name="hautarbeiter" content="{% fassungspfad \'viewer/gemeinsam/hautarbeiter.js\' %}">', vorlage)
