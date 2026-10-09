# -*- coding: utf-8 -*-
"""Haut und Ersatzstück verschmelzen (Scham aus einer .blend): `Stueckrand`, `Hautanschmiegung`, `Stueckdeckung` — am Kunstkörper,
in Node, mit den echten Modulen.

WARUM (Edgar, 09.10.2026, mit Bild: „die ist ja wie aus der Haut ausgeschnitten", „die soll mit der Nachbarhaut verschmelzen",
„noch nicht an der Haut dran"): Das Stück war ein Fremdkörper mit Stufe, Treppenkante und Lücken. Daz löst es mit einem Geograft,
dessen Randring Punkt für Punkt auf dem Loch im Körper sitzt (Daz-Forum: „facets of the grafting loop must match exactly");
hier folgt die Haut dem Stück, und dessen Rand läuft in sie aus. Geprüft wird:

1. `Stueckrand.deckkraft`: 0 am Netzrand, 1 jenseits `FEDER_M`, dazwischen Hermite; UV-Nähte (doppelte Punkte gleicher Lage) sind
   KEIN Rand.
2. `Hautanschmiegung.senkung`: die Haut unter dem Stück sinkt auf dessen Höhe plus `UNTER_M` und nach innen bis `UNTER_TIEF_M`
   mehr; neben dem Stück läuft sie aus (nie über `KRAGEN_M` + Glättung hinaus, nie nach außen steigend); Punkte mit entgegen-
   gesetzter Normale (anderer Schenkel) sinken nicht mit; `eintragen` lässt Punkte, die ein anderer Stoff verdeckt, in Ruhe.
3. `Stueckdeckung.dreiecke`: Hautdreiecke weit (≥ 2 mm) vor dem Stück fallen überall weg, knapp davor nur im Inneren (ab `grenze` vom
   Netzrand — im Auslauf schiene sonst der Hintergrund durch); Haut HINTER dem Stück bleibt.

Sabotage-Gegenprobe: `UNTER_TIEF_M` auf 0 macht Fall 2 rot (Mitte 0,0105 statt 0,014); `GLEICHRICHTUNG` auf −1 macht Fall 2 rot
(Punkte mit Gegennormale sinken); `KRAGEN_M` auf 0,5 macht Fall 2 rot (weit entfernte Haut sinkt); in `Stueckrand.randpunkte` die
Verschweißung (`schweiss[...]`) durch die Punktnummer ersetzen macht Fall 1 rot; `MIN_DAVOR_M` auf 1 macht Fall 3 rot (nichts fällt weg);
in `Stueckdeckung.dreiecke` `if (d > grenze) weg[k / 3] = 1;` durch `weg[k / 3] = 1;` ersetzen macht Fall 3 rot (knapp davor fällt auch die Haut im Auslauf weg); `STARK_M` auf 1 macht Fall 3 rot (weit davor fällt im Auslauf nichts weg).

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL_RAND = Jsmodul('gemeinsam', 'stueckrand.js')
MODUL_SCHMIEGUNG = Jsmodul('gemeinsam', 'hautanschmiegung.js')
MODUL_DECKUNG = Jsmodul('gemeinsam', 'stueckdeckung.js')

GEMEINSAM = """
const fehl = (was) => { throw new Error(was); };
const zaehl = (m) => { let n = 0; for (const v of m) n += v; return n; };
const nah = (a, b, tol = 1e-5) => Math.abs(a - b) <= tol;

// Haut: Ebene y = 0, 41 x 41 Punkte im Abstand von 4 mm (x, z von -80 bis 80 mm), Normalen nach oben.
const N = 41, H = 0.004;
const K = new Float32Array(N * N * 3), NORM = new Float64Array(N * N * 3), T = [];
for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
    K.set([(c - 20) * H, 0, (r - 20) * H], 3 * (r * N + c));
    NORM.set([0, 1, 0], 3 * (r * N + c));
}
for (let r = 0; r + 1 < N; r++) for (let c = 0; c + 1 < N; c++) {
    const a = r * N + c; T.push(a, a + 1, a + N, a + 1, a + N + 1, a + N);
}
const INDEX = Uint32Array.from(T);

// Ein Blatt aus M x M Punkten im Abstand `schritt` um (0, y, 0), mit Dreiecken.
function blatt(M, schritt, y) {
    const P = [], D = [];
    for (let i = 0; i < M; i++) for (let j = 0; j < M; j++) P.push((j - (M - 1) / 2) * schritt, y, (i - (M - 1) / 2) * schritt);
    for (let i = 0; i + 1 < M; i++) for (let j = 0; j + 1 < M; j++) {
        const a = i * M + j; D.push(a, a + 1, a + M, a + 1, a + M + 1, a + M);
    }
    return { punkte: Float32Array.from(P), dreiecke: Uint32Array.from(D) };
}
"""

SKRIPT_RAND = """
const { Stueckrand } = await import(MODUL);
""" + GEMEINSAM + """
// --- 1a. ein Blatt 9 x 9 Punkte im Abstand von 2 mm: Rand 0, Mitte (8 mm vom Rand) 1, zwei Reihen weiter innen (2 mm) Hermite ----
const b = blatt(9, 0.002, 0);
const a = Stueckrand.deckkraft(b.punkte, b.dreiecke);
const M = 9;
for (let i = 0; i < M; i++) for (let j = 0; j < M; j++) {
    const randNah = Math.min(i, j, M - 1 - i, M - 1 - j);                      // Reihen vom Rand
    const soll = (x => x * x * (3 - 2 * x))(Math.min(randNah * 0.002 / Stueckrand.FEDER_M, 1));
    if (!nah(a[i * M + j], soll, 1e-4)) fehl('deckkraft bei Reihe ' + randNah + ': ' + a[i * M + j] + ' statt ' + soll);
}
if (a[4 * M + 4] !== 1) fehl('Mitte 8 mm vom Rand muss 1 sein: ' + a[4 * M + 4]);

// --- 1b. zwei Blätter 5 x 9, Naht in der Mitte mit DOPPELTEN Punkten: die Naht ist kein Rand ---------------------------------------
const P = [], D = [];
const spalten = 5, zeilen = 9;
for (let seite = 0; seite < 2; seite++) {
    const basis = P.length / 3;
    for (let i = 0; i < zeilen; i++) for (let j = 0; j < spalten; j++) P.push((seite * (spalten - 1) + j - (spalten - 1)) * 0.002, 0, (i - 4) * 0.002);
    for (let i = 0; i + 1 < zeilen; i++) for (let j = 0; j + 1 < spalten; j++) {
        const q = basis + i * spalten + j; D.push(q, q + 1, q + spalten, q + 1, q + spalten + 1, q + spalten);
    }
}
const pn = Float32Array.from(P), dn = Uint32Array.from(D);
const randpunkte = Stueckrand.randpunkte(pn, dn);
// Mitte der Naht, mittlere Zeile: beide Punkte (rechter Rand von Blatt 0, linker von Blatt 1) liegen bei x = 0, z = 0
const mitteNaht = [];
for (let i = 0; i < pn.length / 3; i++) if (Math.abs(pn[3 * i]) < 1e-9 && Math.abs(pn[3 * i + 2]) < 1e-9) mitteNaht.push(i);
if (mitteNaht.length !== 2) fehl('Testaufbau: zwei Punkte an der Nahtmitte erwartet, es sind ' + mitteNaht.length);
if (mitteNaht.some(i => randpunkte.includes(i))) fehl('Nahtpunkte gelten als Rand: ' + JSON.stringify(randpunkte.filter(i => mitteNaht.includes(i))));
const dk = Stueckrand.deckkraft(pn, dn);
if (!mitteNaht.every(i => dk[i] === 1)) fehl('Nahtmitte (8 mm vom echten Rand) muss deckend sein: ' + mitteNaht.map(i => dk[i]));
// --- 1c. `fahnen`: ein Dreieck, das nur an EINER Kante am Netz hängt, fällt weg; das Innere nie ------------------------------------
const bl = blatt(5, 0.002, 0), nb = 5;
const Pf = Float32Array.from([...bl.punkte, 0.006, 0, -0.001]);                 // Punkt 25 neben dem rechten Rand
const Df = Uint32Array.from([...bl.dreiecke, 1 * nb + 4, 2 * nb + 4, 25]);      // die Fahne hängt an der Kante (Zeile 1, Spalte 4)–(Zeile 2, Spalte 4)
const weg1 = Stueckrand.fahnen(Pf, Df, 1);
const fahne = Df.length / 3 - 1;
if (!weg1[fahne]) fehl('fahnen: die Fahne bleibt stehen');
let inneres = 0;
for (let t = 0; t < bl.dreiecke.length / 3; t++) {
    const v = [bl.dreiecke[3 * t], bl.dreiecke[3 * t + 1], bl.dreiecke[3 * t + 2]];
    if (v.every(i => { const r = Math.floor(i / nb), c = i % nb; return r >= 1 && r <= 3 && c >= 1 && c <= 3; }) && weg1[t]) inneres++;
}
if (inneres) fehl('fahnen: ' + inneres + ' Dreiecke im Inneren abgetragen');
if (zaehl(weg1) !== 3) fehl('fahnen: ein Durchgang trägt die Fahne und die zwei Eckdreiecke mit einem Nachbarn ab (3), es sind ' + zaehl(weg1));
console.log(JSON.stringify({ ok: true, randpunkte: randpunkte.length }));
"""

SKRIPT_SCHMIEGUNG = """
const { Hautanschmiegung: A } = await import(MODUL);
""" + GEMEINSAM + """
// Stück: 5 x 5 Haut-Punkte (|x|, |z| <= 8 mm) werden vom Stück 10 mm HINTER der Haut verdeckt; `rand` unendlich (tief im Stück).
const n = N * N, extra = 3;
const koerper = new Float32Array((n + extra) * 3); koerper.set(K);
const normalen = new Float64Array((n + extra) * 3); normalen.set(NORM);
const ersatz = new Uint8Array(n + extra), maske = new Uint8Array(n + extra);
const hoehe = new Float32Array(n + extra).fill(-Infinity), rand = new Float32Array(n + extra).fill(Infinity);
for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
    if (Math.abs((c - 20) * 4) <= 8 && Math.abs((r - 20) * 4) <= 8) { const i = r * N + c; ersatz[i] = 1; maske[i] = 1; hoehe[i] = -0.010; }
}
// drei Punkte AUF der Haut, aber vom anderen Schenkel: Normale nach unten (an 12, 16 und 20 mm neben dem Block)
[12, 16, 20].forEach((x, k) => { const i = n + k; koerper.set([x * 0.001, 0, 0], 3 * i); normalen.set([0, -1, 0], 3 * i); });
const s = A.senkung(koerper, normalen, ersatz, hoehe, maske, INDEX, rand);
const mitte = 20 * N + 20;
const soll = 0.010 + A.UNTER_M + A.UNTER_TIEF_M;
if (!nah(s[mitte], soll, 1e-6)) fehl('Senkung in der Mitte: ' + s[mitte] + ' statt ' + soll);
// Auslauf nach +x entlang z = 0: 12, 16, 20, 24 mm neben der Mitte (Block bis 8 mm) → 4, 8, 12, 16 mm vom Rand des Blocks
const ent = (mm) => s[20 * N + 20 + mm / 4];
if (!(ent(12) > 0 && ent(12) < soll)) fehl('Auslauf bei 4 mm: ' + ent(12));
for (const [a, b] of [[12, 16], [16, 20], [20, 24], [24, 28]]) if (!(ent(a) >= ent(b) - 1e-7)) fehl('Auslauf steigt von ' + a + ' nach ' + b + ': ' + ent(a) + ' → ' + ent(b));
if (!nah(ent(80 - 4), 0, 1e-9)) fehl('weit entfernte Haut darf nicht sinken: ' + ent(76));
if (s[0] !== 0) fehl('Ecke der Haut sinkt: ' + s[0]);
// Gegennormale: kein Mitsinken (sie hängen an keinem Dreieck, also zählt allein die Richtung)
for (let k = 0; k < extra; k++) if (s[n + k] !== 0) fehl('Punkt mit Gegennormale sinkt mit (' + (12 + 4 * k) + ' mm): ' + s[n + k]);
// eintragen: schreibt −s·N für Ersatz und freie Haut daneben; was ein anderer Stoff verdeckt (maske, nicht ersatz), bleibt
const andere = 20 * N + 30;                                  // 40 mm neben der Mitte, von einem anderen Stoff verdeckt
maske[andere] = 1;
const einzug = new Float32Array((n + extra) * 3); einzug.set([0.5, 0.5, 0.5], 3 * andere);
const gesenkt = A.eintragen(einzug, s, normalen, ersatz, maske);
if (!nah(einzug[3 * mitte + 1], -soll, 1e-6)) fehl('einzug in der Mitte: ' + einzug[3 * mitte + 1]);
if (einzug[3 * andere] !== 0.5) fehl('eintragen überschreibt einen Punkt, den ein anderer Stoff verdeckt');
if (gesenkt < 25) fehl('gesenkte Punkte: ' + gesenkt);
console.log(JSON.stringify({ ok: true, mitte: s[mitte], gesenkt }));
"""

SKRIPT_DECKUNG = """
const { Stueckdeckung: D } = await import(MODUL);
""" + GEMEINSAM + """
const lauf = (y) => {
    const b = blatt(23, 0.002, y);                          // ±22 mm; der Randabstand wird in `dreiecke` gerechnet
    const einzug = new Float32Array(K.length);
    const weg = D.dreiecke(K, einzug, NORM, INDEX, b, 0.006);
    const gewaehlt = [];
    for (let k = 0; k < INDEX.length; k += 3) {
        const c = [0, 1, 2].map(d => (K[3 * INDEX[k] + d] + K[3 * INDEX[k + 1] + d] + K[3 * INDEX[k + 2] + d]) / 3);
        gewaehlt.push({ weg: weg[k / 3], rand: Math.max(Math.abs(c[0]), Math.abs(c[2])) * 1000 });
    }
    return gewaehlt;
};
// --- 3a. Stück 10 mm HINTER der Haut (Haut weit davor): überall im Stück weg, auch im Auslauf des Stückrands (Platte über der
//         Furche), nicht außerhalb des Stücks und nicht dort, wo das Dreieck über den Stückrand hinausragt (zu wenige Ecken treffen) ----
const stark = lauf(-0.010);
if (!stark.some(t => t.weg && t.rand <= 12)) fehl('weit davor: nichts im Inneren entfernt');
if (!stark.some(t => t.weg && t.rand >= 17 && t.rand <= 21)) fehl('weit davor: auch im Auslauf (Mitte 17–21 mm) muss die Platte weg');
if (stark.some(t => t.weg && t.rand > 22)) fehl('weit davor: Dreiecke jenseits des Stückrands entfernt (Mitte > 22 mm)');
// --- 3b. Stück 1 mm hinter der Haut (knapp davor): nur im Inneren (Mitte über 6 mm vom Rand), nicht am Rand -------------------------------
const knapp = lauf(-0.001);
if (!knapp.some(t => t.weg && t.rand <= 12)) fehl('knapp davor: nichts im Inneren entfernt');
if (knapp.some(t => t.weg && t.rand > 18)) fehl('knapp davor: am Rand (Mitte > 18 mm) darf die Haut bleiben: ' + knapp.filter(t => t.weg && t.rand > 18).length);
if (!knapp.some(t => !t.weg && t.rand >= 17 && t.rand <= 21)) fehl('knapp davor: die Haut im Auslauf (Mitte 17–21 mm) muss stehen bleiben');
// --- 3c. Stück VOR der Haut (Haut dahinter): nichts fällt weg -------------------------------------------------------------------------
const dahinter = lauf(0.010);
if (dahinter.some(t => t.weg)) fehl('Haut hinter dem Stück entfernt: ' + dahinter.filter(t => t.weg).length);
console.log(JSON.stringify({ ok: true, stark: stark.filter(t => t.weg).length, knapp: knapp.filter(t => t.weg).length }));
"""


class HautanschmiegungTest(SimpleTestCase):
    databases = set()

    def test_1_der_stueckrand_laeuft_weich_aus_und_naehte_sind_kein_rand(self):
        ausgabe = MODUL_RAND.laufen(SKRIPT_RAND)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_2_die_haut_sinkt_unter_das_stueck_und_laeuft_neben_ihm_aus(self):
        ausgabe = MODUL_SCHMIEGUNG.laufen(SKRIPT_SCHMIEGUNG)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertAlmostEqual(ausgabe['mitte'], 0.014, places=5)

    def test_3_haut_vor_dem_stueck_faellt_weg_dahinter_bleibt_sie(self):
        ausgabe = MODUL_DECKUNG.laufen(SKRIPT_DECKUNG)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertGreater(ausgabe['stark'], 0)
        self.assertGreater(ausgabe['knapp'], 0)
