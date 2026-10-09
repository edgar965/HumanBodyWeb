# -*- coding: utf-8 -*-
"""`Stueckluecke` und `Stueckdeckung.gedeckt`: Haut, die nur wegen des Ersatzstücks wegfiele, aber nichts dahinter hat, bleibt stehen —
am Kunstkörper, in Node, mit den echten Modulen.

BEFUND (Edgar: „Damm-Loch"; Chrome, Modell „Fallout ranger", 09.10.2026): Mit dem Scham-Stück zeigten Ansichten von unten und hinten
unten 61.000 und 50.000 Pixel Hintergrund MEHR als ohne. Von 284 entfernten Hautdreiecken deckte das Stück 200 ganz, 26 zur Hälfte und
58 gar nicht (die Leisten, x ±20…40 mm). `Hautmaskeersatz.beruehrt` markiert jede Ecke eines Dreiecks, das einen Innenpunkt berührt, und
`indexOhne` nimmt jedes Dreieck mit DREI markierten Ecken weg — auch eines, dessen Ecken je an einem anderen Nachbarn hängen.

Kunstwelt: Haut = Ebene y = 0 (41 × 41 Punkte im Abstand von 4 mm, Normalen nach oben), Stück = Quadrat −20 … 20 mm, 3 mm dahinter.

1. `gedeckt`: ein Dreieck, dessen Ecken alle höchstens 16 mm von der Mitte liegen, ist gedeckt; eines ab 28 mm nicht; ein Dreieck, das
   `pruefen` nicht nennt, bleibt 0, auch wenn es gedeckt wäre.
2. `bleibt`: Von den Dreiecken, die erst durch `beruehrt` wegfielen (alle Ecken in `weg`, nicht alle in `vorher`, nicht in `vorStueck`),
   bleiben die stehen, die das Stück nicht trägt — keines im Inneren, keines im Stoffblock, keines mit `vorStueck`, wohl welche am
   Rand der markierten Fläche, außerhalb des Stücks. Ohne Kandidaten: null.
3. `Hautmaske.indexOhne` mit `dreieckBleibt`: ein Dreieck mit drei verdeckten Ecken bleibt, wenn es genannt wird; `dreieckWeg` schlägt es.

Sabotage-Gegenprobe: in `_aufStueck` `getroffen < 2` → `getroffen < 0` macht Fall 1 rot (der Rand zählt als gedeckt); in `bleibt` die
Zeile mit `vorher` streichen macht Fall 2 rot; `!gedeckt[k]` → `true` macht Fall 2 rot; in `indexOhne` `!(dreieckBleibt && …)` entfernen
macht Fall 3 rot.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'stueckluecke.js')
MODUL_MASKE = Jsmodul('gemeinsam', 'hautmaske.js')

GEMEINSAM = """
const fehl = (was) => { throw new Error(was); };
const zaehl = (m) => { let n = 0; for (const v of m) n += v; return n; };

// Haut: Ebene y = 0, 41 x 41 Punkte im Abstand von 4 mm (x, z von -80 bis 80 mm), Normalen nach oben.
const N = 41, H = 0.004;
const K = new Float32Array(N * N * 3), NORM = new Float32Array(N * N * 3), T = [];
for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
    K.set([(c - 20) * H, 0, (r - 20) * H], 3 * (r * N + c));
    NORM.set([0, 1, 0], 3 * (r * N + c));
}
for (let r = 0; r + 1 < N; r++) for (let c = 0; c + 1 < N; c++) {
    const a = r * N + c; T.push(a, a + 1, a + N, a + 1, a + N + 1, a + N);
}
const INDEX = Uint32Array.from(T), EINZUG = new Float32Array(N * N * 3);
const NT = INDEX.length / 3;
// Float32 rundet (16 mm → 16,0000007): Schwellen mit Spielraum von 0,01 mm. `TOL(v)` = v + 0,01; `-TOL(-v)` = v − 0,01.
const TOL = (v) => v + 0.01;
// Abstand (mm) der Ecken eines Dreiecks von der Mitte: kleinster und größter Wert von max(|x|, |z|).
const randmm = (k) => {
    const w = [0, 1, 2].map((e) => { const i = INDEX[3 * k + e]; return Math.max(Math.abs(K[3 * i]), Math.abs(K[3 * i + 2])) * 1000; });
    return [Math.min(...w), Math.max(...w)];
};

// Stück: Quadrat -20 … 20 mm (Punkte im Abstand von 2 mm) in der Höhe y = -3 mm, mit Dreiecken.
const P = [], D = [], M = 21;
for (let i = 0; i < M; i++) for (let j = 0; j < M; j++) P.push((j - 10) * 0.002, -0.003, (i - 10) * 0.002);
for (let i = 0; i + 1 < M; i++) for (let j = 0; j + 1 < M; j++) {
    const a = i * M + j; D.push(a, a + 1, a + M, a + 1, a + M + 1, a + M);
}
const STOFF = { punkte: Float32Array.from(P), dreiecke: Uint32Array.from(D), ersatz: true };
"""

SKRIPT_LUECKE = """
const { Stueckluecke } = await import(MODUL);
const { Stueckdeckung } = await import(MODUL.replace('stueckluecke.js', 'stueckdeckung.js'));
""" + GEMEINSAM + """
// --- 1. gedeckt ---------------------------------------------------------------------------------------
const alle = new Uint8Array(NT).fill(1);
const g = Stueckdeckung.gedeckt(K, EINZUG, NORM, INDEX, STOFF, alle, new Uint8Array(NT));
let innen = 0, aussen = 0, falsch = [];
for (let k = 0; k < NT; k++) {
    const [lo, hi] = randmm(k);
    if (hi <= TOL(16)) { innen++; if (!g[k]) falsch.push(['innen nicht gedeckt', k, lo, hi]); }
    if (lo >= -TOL(-28)) { aussen++; if (g[k]) falsch.push(['aussen gedeckt', k, lo, hi]); }
}
if (falsch.length) fehl('gedeckt: ' + JSON.stringify(falsch.slice(0, 4)));
if (innen < 100 || aussen < 500) fehl('Kunstwelt zu klein: innen ' + innen + ', aussen ' + aussen);
const g0 = Stueckdeckung.gedeckt(K, EINZUG, NORM, INDEX, STOFF, new Uint8Array(NT), new Uint8Array(NT));
if (zaehl(g0) !== 0) fehl('ohne pruefen darf nichts gedeckt sein: ' + zaehl(g0));
// Zwei lange, schmale Dreiecke über einem Stück von ±22 mm: beider Mitte liegt darauf, aber nur bei T2 treffen zwei Ecken (Ecken A, D);
// bei T1 trifft nur A (B und C liegen bei 30 mm, daneben) — `getroffen < 2` hält T1 zurück: sonst bliebe ein Loch bis zum Hintergrund.
const P22 = [], D22 = [], M22 = 23;
for (let i = 0; i < M22; i++) for (let j = 0; j < M22; j++) P22.push((j - 11) * 0.002, -0.003, (i - 11) * 0.002);
for (let i = 0; i + 1 < M22; i++) for (let j = 0; j + 1 < M22; j++) {
    const a = i * M22 + j; D22.push(a, a + 1, a + M22, a + 1, a + M22 + 1, a + M22);
}
const STOFF22 = { punkte: Float32Array.from(P22), dreiecke: Uint32Array.from(D22), ersatz: true };
const K2 = Float32Array.from([0, 0, 0, 0.03, 0, 0.006, 0.03, 0, -0.006, 0.01, 0, 0.006]);
const N2 = Float32Array.from([0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0]);
const I2 = Uint32Array.from([0, 1, 2, 0, 3, 2]);
const g2 = Stueckdeckung.gedeckt(K2, new Float32Array(12), N2, I2, STOFF22, Uint8Array.from([1, 1]), new Uint8Array(2));
if (g2[0] !== 0 || g2[1] !== 1) fehl('schmale Dreiecke: T1 (eine Ecke auf dem Stück) darf nicht gedeckt sein, T2 (zwei Ecken) schon: ' + Array.from(g2));

// --- 2. bleibt ----------------------------------------------------------------------------------------
const weg = new Uint8Array(N * N), vorher = new Uint8Array(N * N);
for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
    const x = Math.abs((c - 20) * 4), z = Math.abs((r - 20) * 4);
    if (x <= 32 && z <= 32) weg[r * N + c] = 1;                                      // beruehrt-Fläche: 17 x 17 Punkte
    if (x <= 8 && z <= 8) vorher[r * N + c] = 1;                                     // davon ein Block durch Stoff verdeckt
}
// Ein zweiter Stoffblock AUSSERHALB des Stücks (x 28 … 32 mm, z 0 … 4 mm): ohne die Prüfung auf `vorher` bliebe er als „ohne Stück dahinter".
for (let r = 20; r <= 21; r++) for (let c = 27; c <= 28; c++) vorher[r * N + c] = 1;
const e = Stueckluecke.bleibt(INDEX, weg, vorher, null, K, EINZUG, NORM, [STOFF]);
if (!e || e.offen <= 0 || e.offen !== zaehl(e.bleibt)) fehl('bleibt: ' + JSON.stringify(e && { offen: e.offen, geprueft: e.geprueft }));
const fehler2 = [];
for (let k = 0; k < NT; k++) {
    const [lo, hi] = randmm(k);
    if (e.bleibt[k] && hi <= TOL(16)) fehler2.push(['im Inneren geblieben', k, lo, hi]);
    if (e.bleibt[k] && hi <= TOL(8)) fehler2.push(['im Stoffblock geblieben', k, lo, hi]);
}
if (fehler2.length) fehl('bleibt: ' + JSON.stringify(fehler2.slice(0, 4)));
let aussenRand = 0;
for (let k = 0; k < NT; k++) { const [lo, hi] = randmm(k); if (lo >= -TOL(-28) && hi <= TOL(32) && e.bleibt[k]) aussenRand++; }
if (aussenRand < 10) fehl('Am Rand außerhalb des Stücks müssen Dreiecke bleiben: ' + aussenRand);
let imStoffAussen = 0;
for (let k = 0; k < NT; k++) {
    const a = INDEX[3 * k], b = INDEX[3 * k + 1], c = INDEX[3 * k + 2];
    if (vorher[a] && vorher[b] && vorher[c] && K[3 * a] > 0.02) { imStoffAussen++; if (e.bleibt[k]) fehl('Stoffblock außerhalb des Stücks darf nicht bleiben: Dreieck ' + k); }
}
if (imStoffAussen < 2) fehl('Kunstwelt: der Stoffblock außerhalb fehlt (' + imStoffAussen + ')');
// Ein Dreieck mit vorStueck bleibt nicht (es ist gedeckt, sonst wäre es nicht dort) — hier eines am Rand, das sonst bliebe:
const vs = new Uint8Array(NT);
const k0 = [...Array(NT).keys()].find((k) => e.bleibt[k]);
vs[k0] = 1;
const e2 = Stueckluecke.bleibt(INDEX, weg, vorher, vs, K, EINZUG, NORM, [STOFF]);
if (e2.bleibt[k0] || e2.offen !== e.offen - 1) fehl('vorStueck: ' + e2.bleibt[k0] + ', ' + e2.offen + ' statt ' + (e.offen - 1));
const keine = Stueckluecke.bleibt(INDEX, new Uint8Array(N * N), vorher, null, K, EINZUG, NORM, [STOFF]);
if (keine !== null) fehl('ohne Kandidaten: null erwartet');
const ohneErsatz = Stueckluecke.bleibt(INDEX, weg, vorher, null, K, EINZUG, NORM, [{ ...STOFF, ersatz: false }]);
if (!ohneErsatz || ohneErsatz.offen <= e.offen) fehl('ohne Ersatzstück trägt nichts: alle Kandidaten bleiben (' + (ohneErsatz && ohneErsatz.offen) + ')');

// --- 3. splitter --------------------------------------------------------------------------------------
// Verdeckte Fläche |x|, |z| ≤ 12 mm; der Einzug wechselt je Spalte zwischen 1 und 9 mm (steile Dreiecke dazwischen).
const maske3 = new Uint8Array(N * N), steil = new Float32Array(N * N * 3), sanft = new Float32Array(N * N * 3);
for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
    const x = Math.abs((c - 20) * 4), z = Math.abs((r - 20) * 4);
    if (x <= 12 && z <= 12) maske3[r * N + c] = 1;
    steil[3 * (r * N + c) + 1] = -(c % 2 ? 0.009 : 0.001);
    sanft[3 * (r * N + c) + 1] = -(c % 2 ? 0.0012 : 0.001);
}
const s1 = Stueckluecke.splitter(INDEX, maske3, steil, null, K, NORM, [STOFF]);
let ausserhalb = 0, weg3 = 0;
for (let k = 0; k < NT; k++) {
    if (!s1.weg[k]) continue;
    weg3++;
    const [lo, hi] = randmm(k);
    if (lo > TOL(16)) ausserhalb++;
}
if (s1.splitter < 20 || s1.splitter !== weg3) fehl('splitter: ' + s1.splitter + ' entfernt, gezählt ' + weg3);
if (ausserhalb) fehl('splitter: ' + ausserhalb + ' Dreiecke ohne verdeckte Ecke entfernt');
const s2 = Stueckluecke.splitter(INDEX, maske3, sanft, null, K, NORM, [STOFF]);
if (s2.splitter !== 0) fehl('splitter: Unterschiede unter 4 mm dürfen nichts entfernen: ' + s2.splitter);
// Am Rand des Stücks (±20 mm; Abstand der Treffer bis 7 mm) bleiben auch steile Dreiecke stehen: der weiche Rand lässt die Haut durchscheinen.
const maske4 = new Uint8Array(N * N);
for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) { const x = Math.abs((c - 20) * 4), z = Math.abs((r - 20) * 4); if (x >= 12 && x <= 24 && z <= 12) maske4[r * N + c] = 1; }
const s3 = Stueckluecke.splitter(INDEX, maske4, steil, null, K, NORM, [STOFF]);
for (let k = 0; k < NT; k++) {
    if (!s3.weg[k]) continue;
    if (randmm(k)[0] > TOL(12)) {
        // innen liegende Dreiecke (alle Ecken höchstens 12 mm vom Stückrand entfernt?) — der Rand liegt bei 20 mm, innen = bis 13 mm
        if (randmm(k)[1] > TOL(16)) fehl('splitter: ein Dreieck am Stückrand (Treffer < 7 mm vom Rand) fiel weg: ' + k);
    }
}
// `vorStueck` bleibt unverändert; das Ergebnis ist ein neues Feld, das es enthält.
const vs3 = new Uint8Array(NT); vs3[0] = 1;
const s4 = Stueckluecke.splitter(INDEX, maske3, steil, vs3, K, NORM, [STOFF]);
if (vs3[1] !== 0 || !s4.weg[0] || s4.weg === vs3) fehl('splitter: vorStueck verändert oder nicht enthalten');
const s5 = Stueckluecke.splitter(INDEX, new Uint8Array(N * N), steil, vs3, K, NORM, [STOFF]);
if (s5.weg !== vs3 || s5.splitter !== 0) fehl('splitter: ohne Kandidaten dasselbe Feld zurück');
console.log(JSON.stringify({ ok: true, offen: e.offen, geprueft: e.geprueft, innen, aussen, splitter: s1.splitter }));
"""

SKRIPT_MASKE = """
const { Hautmaske } = await import(MODUL);
""" + GEMEINSAM + """
const verdeckt = new Uint8Array(N * N).fill(1);
const alles = Hautmaske.indexOhne(INDEX, [], verdeckt, null);
if (alles.entfernt !== NT) fehl('alles verdeckt: ' + alles.entfernt + ' statt ' + NT);
const bleibt = new Uint8Array(NT); bleibt[3] = 1;
const mit = Hautmaske.indexOhne(INDEX, [], verdeckt, null, bleibt);
if (mit.entfernt !== NT - 1 || mit.index.length !== 3) fehl('dreieckBleibt: ' + mit.entfernt);
if (!(mit.index[0] === INDEX[9] && mit.index[1] === INDEX[10] && mit.index[2] === INDEX[11])) fehl('das falsche Dreieck blieb: ' + Array.from(mit.index));
const weg = new Uint8Array(NT); weg[3] = 1;
const beide = Hautmaske.indexOhne(INDEX, [], verdeckt, weg, bleibt);
if (beide.entfernt !== NT) fehl('dreieckWeg schlägt dreieckBleibt: ' + beide.entfernt);
const unverdeckt = Hautmaske.indexOhne(INDEX, [], new Uint8Array(N * N), null, bleibt);
if (unverdeckt.entfernt !== 0) fehl('ohne verdeckte Ecken fällt nichts weg: ' + unverdeckt.entfernt);
console.log(JSON.stringify({ ok: true, entfernt: mit.entfernt }));
"""


class StueckSchliesstLueckenTest(SimpleTestCase):
    databases = set()

    def test_gedeckte_dreiecke_und_die_haut_ohne_stueck_dahinter(self):
        ausgabe = MODUL.laufen(SKRIPT_LUECKE)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertGreater(ausgabe['offen'], 10)

    def test_indexohne_laesst_genannte_dreiecke_stehen(self):
        ausgabe = MODUL_MASKE.laufen(SKRIPT_MASKE)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
