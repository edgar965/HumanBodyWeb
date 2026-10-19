# -*- coding: utf-8 -*-
u"""`Feldpaket` und `Hautmaskenvorrat` — die Haut-Maske dauerhaft auf dem Server (19.10.2026, `core/dienste/g9hautmasken.py`).

1. `Feldpaket`: Felder (auch ±Unendlich, NaN, Float64), verschachtelte Objekte, Listen mit null — gepackt und zurück gleich, auch über gzip.
2. Schlüssel: gleiche Eingabe gleich (auch als Kopie, Index 16/32 Bit), jede Änderung an Punkt, Einstellung oder Reihenfolge der Stücke ein anderer; er passt auf
   das Muster des Servers.
3. Einstellung: „fein" sucht und legt grob und fein ab, nicht ultrafein; „aus" nichts; ohne Stufe nichts.
4. `rechnen`: beim ersten Mal gerechnet und abgelegt (Adresse mit Fassung, Schlüssel, Stufe), beim zweiten aus dem Vorrat — mit dem Inhalt VOR dem Schreiben
   (`Hautverdeckung.anwenden` schreibt in `weg` und `maske`), ohne Normalen, wenn kein Ersatzstück dabei ist, mit, wenn eines dabei ist.
5. Ohne Meta `hautmaskenfassung`: gerechnet, nichts gefragt, nichts abgelegt. Eine Ablage, die nicht zur Figur passt (Punktzahl), gilt nicht.

Sabotage (von Hand, nicht als Lauf): in `ablegen` nicht sofort packen (erst nach dem Hochladen) → Fall 4 rot („Inhalt vor dem Schreiben");
in `schluessel` die Einstellungen weglassen → Fall 2 rot („anders bei starr"). Geschrieben, nicht gelaufen.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'hautmaskenvorrat.js')

SKRIPT = """
globalThis.window = globalThis.window || { addEventListener() {}, removeEventListener() {} };
globalThis.document = globalThis.document || { addEventListener() {}, removeEventListener() {}, dispatchEvent() { return true; }, cookie: '' };
const FASSUNG = '0123456789abcdef';
document.querySelector = (s) => (s.includes('hautmaskenfassung') ? { content: FASSUNG } : null);
const basis = MODUL.replace('hautmaskenvorrat.js', '');
const { Hautmaskenvorrat: V } = await import(MODUL);
const { Feldpaket: F } = await import(basis + 'feldpaket.js');
const { Hautarbeit: A } = await import(basis + 'hautarbeit.js');
const { Netzstufenstand: S } = await import(basis + 'netzstufenstand.js');
const { Genesis9vorrat: G } = await import(basis + 'genesis9vorrat.js');
const liste = (f) => (f ? Array.from(f, String) : f);

// 1. Feldpaket
const obj = { maske: Uint8Array.from([0, 1, 1, 0, 1]), hoehe: Float32Array.from([-Infinity, 1.5, NaN]), normalen: Float64Array.from([0.1, -2e-9]),
              einzug: { werte: Float32Array.from([1, 2, 3]), gesetzt: 2, weg: null }, randabstaende: [null, Float64Array.from([3.25])], ms: 7, text: 'ä' };
for (const [name, z] of [['roh', F.entpacken(F.packen(obj).buffer)], ['gzip', await F.ungzip((await F.gzip(obj)).stream())]]) {
    pruefe(name + ': Felder', [liste(z.maske), liste(z.hoehe), liste(z.normalen), liste(z.einzug.werte), liste(z.randabstaende[1])],
           [liste(obj.maske), liste(obj.hoehe), liste(obj.normalen), liste(obj.einzug.werte), liste(obj.randabstaende[1])]);
    pruefe(name + ': Typen', [z.maske instanceof Uint8Array, z.hoehe instanceof Float32Array, z.normalen instanceof Float64Array], [true, true, true]);
    pruefe(name + ': Rest', [z.einzug.gesetzt, z.einzug.weg, z.randabstaende[0], z.ms, z.text], [2, null, null, 7, 'ä']);
}
let fremd = false;
try { F.entpacken(new Uint8Array(16).buffer); } catch (e) { fremd = true; }
pruefe('fremde Bytes werfen', fremd, true);

// 2. Schlüssel
const pos = Float32Array.from([0, 0, 0, 1, 0, 0, 0, 1, 0]), index = Uint32Array.from([0, 1, 2]);
const stoff = (d = 0, name = 'hemd') => ({ schluessel: name, punkte: Float32Array.from([0, 0, 0.01 + d, 1, 0, 0.01, 0, 1, 0.01]), dreiecke: Uint16Array.from([0, 1, 2]),
                                          starr: false, ersatz: false });
const k1 = V.schluessel(pos, index, [stoff()]);
pruefe('gleiche Eingabe, gleicher Schlüssel', V.schluessel(pos.slice(), Uint16Array.from(index), [stoff()]), k1);
pruefe('anders bei anderem Stoffpunkt', V.schluessel(pos, index, [stoff(1e-6)]) !== k1, true);
pruefe('anders bei starr', V.schluessel(pos, index, [{ ...stoff(), starr: true }]) !== k1, true);
pruefe('anders bei Reihenfolge', V.schluessel(pos, index, [stoff(), stoff(0, 'hose')]) !== V.schluessel(pos, index, [stoff(0, 'hose'), stoff()]), true);
pruefe('Muster des Servers', /^[a-z0-9]{8,64}$/.test(k1), true);

// 3. Einstellung
G.einstellen('fein');
pruefe('fein', [V.an('grob'), V.an('fein'), V.an('ultrafein')], [true, true, false]);
G.einstellen('aus');
pruefe('aus', V.an('grob'), false);
G.einstellen('ultrafein');
pruefe('ohne Stufe', V.an(null), false);

// 4. rechnen und holen
const inst = { id: 'f1' };
S.melden(inst, 'fein');
let gerechnet = 0;
const abgelegt = new Map(), anfragen = [];
A.rechnen = async (p) => {
    gerechnet += 1;
    const n = p.length / 3;
    return { maske: Uint8Array.from([1, 0, 1]), ersatz: new Uint8Array(n), hoehe: new Float32Array(n).fill(-Infinity), rand: new Float32Array(n).fill(Infinity),
             normalen: new Float64Array(3 * n).fill(0.5), einzug: { werte: new Float32Array(3 * n).fill(0.25), gesetzt: 2, geschnappt: 0, band: 1, weg: Uint8Array.from([0, 0, 1]) },
             randabstaende: [null], ms: 1234 };
};
globalThis.fetch = async (url, o = {}) => {
    anfragen.push([o.method || 'GET', url]);
    const k = url.split('?')[0];
    if (o.method === 'POST') {
        abgelegt.set(k, new Uint8Array(await o.body.get('maske').arrayBuffer()));
        return new Response('{"ok": true}', { status: 200 });
    }
    return abgelegt.has(k) ? new Response(abgelegt.get(k)) : new Response('', { status: 404 });
};
const warten = async (n = 1) => { for (let i = 0; i < 100 && abgelegt.size < n; i++) await new Promise(r => setTimeout(r, 10)); };
const r1 = await V.rechnen(inst, pos, index, [stoff()]);
r1.einzug.weg[0] = 9; r1.maske[1] = 7;                     // so schreibt `Hautverdeckung.anwenden` hinein
await warten();
pruefe('einmal gerechnet', gerechnet, 1);
pruefe('abgelegt unter Fassung und Schlüssel', [...abgelegt.keys()], [`/api/character/genesis9-figur/hautmasken/${FASSUNG}/${k1}/`]);
pruefe('Stufe in der Adresse', anfragen.find(a => a[0] === 'POST')[1].endsWith('?stufe=fein'), true);
const r2 = await V.rechnen(inst, pos, index, [stoff()]);
pruefe('zweites Mal aus dem Vorrat', [gerechnet, r2.ausVorrat], [1, true]);
pruefe('Inhalt vor dem Schreiben', [liste(r2.maske), liste(r2.einzug.weg)], [['1', '0', '1'], ['0', '0', '1']]);
pruefe('ohne Ersatzstück keine Normalen', r2.normalen, null);
pruefe('Werte', [r2.einzug.gesetzt, r2.einzug.band, r2.ms, liste(r2.einzug.werte.subarray(0, 2))], [2, 1, 1234, ['0.25', '0.25']]);
pruefe('Ablage passt nicht (Punktzahl)', await V.holen(FASSUNG, k1, 5, 1), null);
const mitErsatz = [{ ...stoff(0, 'scham'), ersatz: true }];
await V.rechnen(inst, pos, index, mitErsatz);
await warten(2);
const r3 = await V.rechnen(inst, pos, index, mitErsatz);
pruefe('mit Ersatzstück die Normalen', [r3.ausVorrat, r3.normalen instanceof Float64Array, r3.normalen?.length], [true, true, 9]);

// 5. ohne Meta
document.querySelector = () => null;
const vorher = anfragen.length;
await V.rechnen(inst, pos, index, [stoff(0.5)]);
pruefe('ohne Fassung: gerechnet, nichts gefragt', [gerechnet, anfragen.length - vorher], [3, 0]);
console.log(JSON.stringify({ ok: true }));
"""


class HautmaskenvorratTest(SimpleTestCase):
    databases = set()

    def test_maske_aus_dem_vorrat(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
