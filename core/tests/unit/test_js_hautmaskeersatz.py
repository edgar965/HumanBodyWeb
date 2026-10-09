# -*- coding: utf-8 -*-
"""`Hautmaskeersatz`: die Haut vor und auf einem Ersatzstück — am Kunstkörper, in Node, mit den echten Modulen.

WARUM (Edgar, 09.10.2026: „die hat im moment zwei mal Geschlechtsorgane"): Das Scham-Stück liegt zum großen Teil 5–25 mm HINTER
der Genesis-Fläche und war darum ganz verdeckt; die Maske des Stoffs (Strahl, Dreiecke um den nächsten Stoffpunkt) fand dort
nur 111 von etwa 650 Hautpunkten, und das Saumband ließ den Rest versenkt STEHEN — vor dem Stück. Geprüft wird die Antwort darauf:

1. Ein Stück 15 mm HINTER einer ebenen Haut verdeckt die Punkte vor sich — bis einen Zylinder (4 mm) neben seinem Rand, und
   nicht weiter (Haut 6 mm neben dem Rand bleibt).
2. Ein Stück 40 mm dahinter (jenseits `tiefe`) verdeckt nichts, eines 20 mm davor (innerhalb `abstand`) verdeckt, eines 30 mm
   davor nicht.
3. `ersatz` bekommt ALLE Punkte, die das Stück trifft — auch die, die ein Stoff davor schon verdeckt hat (sie lägen sonst als
   Saumband versenkt VOR dem Stück, gesehen 09.10.2026); `hoehe` die Höhe des höchsten Stückpunkts über ihnen, `rand` dessen
   Abstand vom Netzrand des Stücks.
4. Über `Hautmaske.verdeckt` mit `ersatz: true` (und `starr`, `nahe` wie in `hautverdeckung.js`) fällt der Ring um den Rand
   dazu (169 Punkte); ohne die Angabe bleibt es beim Strahl (höchstens 121, die Punkte über dem Stück).
5. `innen` ohne `rand` lässt `RINGE` Schichten Haut am Rand stehen: Block 10 × 10 → 36 Punkte bei 2 Ringen, 64 bei 1, 100 bei 0.
6. `innen` mit `rand` lässt die Haut bis `RING_M` vom Stückrand stehen, gleich wie schmal das Stück ist (Block 4 breit: nichts
   fällt weg, wo Schichten allein alles weggenommen hätten), und `beruehrt` nimmt die Randdreiecke des Lochs mit.

Sabotage-Gegenprobe: `t < -tiefe` → `false` in `_hoechster` macht Fall 2 rot; `r2` auf `1e9` setzen macht Fall 1 rot; in `maskieren`
`if (maske[i]) continue;` einfügen macht Fall 3 rot; `RINGE` auf 0 setzen macht Fall 5 rot; `rand[i] > RING_M` → `true` macht Fall 6
rot; `if (stoff.ersatz)` in `hautmaske.js` entfernen macht Fall 4 rot.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'hautmaskeersatz.js')
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
const basis = { koerper: K, normalen: NORM };

// Stück: Quadrat -22 … 22 mm (Punkte im Abstand von 2 mm) in der Höhe y, mit Dreiecken.
function stueck(y) {
    const P = [], D = [], M = 23;
    for (let i = 0; i < M; i++) for (let j = 0; j < M; j++) P.push((j - 11) * 0.002, y, (i - 11) * 0.002);
    for (let i = 0; i + 1 < M; i++) for (let j = 0; j + 1 < M; j++) {
        const a = i * M + j; D.push(a, a + 1, a + M, a + 1, a + M + 1, a + M);
    }
    return { punkte: Float32Array.from(P), dreiecke: Uint32Array.from(D) };
}
"""

SKRIPT_ERSATZ = """
const { Hautmaskeersatz } = await import(MODUL);
""" + GEMEINSAM + """
const lauf = (y, abstand = 0.025, tiefe = 0.03, maske = new Uint8Array(N * N)) => {
    const ersatz = new Uint8Array(N * N), hoehe = new Float32Array(N * N).fill(-Infinity), rand = new Float32Array(N * N).fill(Infinity);
    Hautmaskeersatz.maskieren(basis, maske, stueck(y), abstand, tiefe, ersatz, hoehe, rand);
    return { maske, ersatz, hoehe, rand };
};

// --- 1. 15 mm hinter der Haut: Punkte bis 24 mm (2 mm neben dem Rand bei 22), nicht die bei 28 mm -------
const a = lauf(-0.015);
const falsch = [];
for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
    const x = Math.abs((c - 20) * 4), z = Math.abs((r - 20) * 4);       // mm
    const soll = (x <= 24 && z <= 24) ? 1 : (x >= 28 || z >= 28) ? 0 : null;
    if (soll !== null && a.maske[r * N + c] !== soll) falsch.push([x, z, a.maske[r * N + c]]);
}
if (falsch.length) fehl('Zylinder falsch bei ' + JSON.stringify(falsch.slice(0, 6)));
if (zaehl(a.maske) !== 169) fehl('13 x 13 Punkte erwartet, es sind ' + zaehl(a.maske));

// --- 2. zu tief dahinter / vor der Haut -------------------------------------------------------------
if (zaehl(lauf(-0.040).maske) !== 0) fehl('40 mm hinter der Haut gilt als verdeckt (tiefe 30 mm)');
// Die Reichweite (eine Zelle, 30 mm) allein hält 40 mm schon fern — die Tiefe selbst prüft dieser Fall, bei tiefe 20 mm:
if (zaehl(lauf(-0.022, 0.025, 0.02).maske) !== 0) fehl('22 mm hinter der Haut gilt bei tiefe 20 mm als verdeckt');
if (zaehl(lauf(-0.015, 0.025, 0.02).maske) !== 169) fehl('15 mm hinter der Haut muss bei tiefe 20 mm verdecken');
if (zaehl(lauf(0.020).maske) !== 169) fehl('20 mm vor der Haut muss verdecken (abstand 25 mm): ' + zaehl(lauf(0.020).maske));
if (zaehl(lauf(0.030).maske) !== 0) fehl('30 mm vor der Haut gilt als verdeckt (abstand 25 mm)');

// --- 3. `ersatz` = alle getroffenen, auch die schon verdeckten; `hoehe`, `rand` ------------------------------
if (zaehl(a.ersatz) !== 169) fehl('ersatz: ' + zaehl(a.ersatz));
const vorher = new Uint8Array(N * N);
for (let i = 0; i < 100; i++) vorher[i] = 1;                                   // schon vorher verdeckt (Stoff)
const b = lauf(-0.015, 0.025, 0.03, vorher);
if (zaehl(b.ersatz) !== 169) fehl('ersatz lässt Vorverdecktes aus: ' + zaehl(b.ersatz) + ' statt 169');
const mitte = 20 * N + 20;
if (Math.abs(a.hoehe[mitte] + 0.015) > 1e-6) fehl('hoehe in der Mitte: ' + a.hoehe[mitte] + ' statt -0,015');
if (a.hoehe[0] !== -Infinity) fehl('hoehe ohne Stück muss -Infinity bleiben');
// Rand des Stücks: Netzrand bei 22 mm; der Punkt über der Mitte ist 22 mm davon entfernt (`RING_M` + 4 mm Reichweite = 13 mm → Infinity),
// ein Punkt bei x = 20 mm trifft Stückpunkte bei 16 … 24 mm — höchstens 6 mm vom Rand (welcher der gleich hohen gewählt wird,
// hängt von der Reihenfolge im Gitter ab).
const rand20 = 20 * N + 25;                                                    // x = 20 mm
if (!(a.rand[rand20] <= 0.0061)) fehl('rand bei x = 20 mm: ' + a.rand[rand20] + ' statt höchstens 0,006');
if (!(a.rand[mitte] >= 0.016)) fehl('rand in der Mitte (22 mm vom Rand, Punkte 2 mm): mindestens 16 mm: ' + a.rand[mitte]);

// --- 5. `innen` ohne `rand`: Ringe Haut am Rand --------------------------------------------------------
const G = 20, TG = [];
for (let r = 0; r + 1 < G; r++) for (let c = 0; c + 1 < G; c++) {
    const q = r * G + c; TG.push(q, q + 1, q + G, q + 1, q + G + 1, q + G);
}
const block = new Uint8Array(G * G);
for (let r = 5; r <= 14; r++) for (let c = 5; c <= 14; c++) block[r * G + c] = 1;
const erwartet = { 0: 100, 1: 64, 2: 36 };
if (Hautmaskeersatz.RINGE < 1) fehl('Standard ohne Ring Haut am Rand: klafft am gezackten Stückrand');
for (const ringe of [0, 1, 2]) {
    Hautmaskeersatz.RINGE = ringe;
    const n = zaehl(Hautmaskeersatz.innen(block, block, Uint32Array.from(TG)));
    if (n !== erwartet[ringe]) fehl('innen mit ' + ringe + ' Ringen: ' + n + ' statt ' + erwartet[ringe]);
}

// --- 6. `innen` mit `rand`: Abstand vom Stückrand statt Schichten ----------------------------------------------
const randFeld = new Float32Array(G * G).fill(Infinity);
for (let r = 5; r <= 14; r++) for (let c = 5; c <= 14; c++) randFeld[r * G + c] = 0.004 * Math.min(r - 5, 14 - r, c - 5, 14 - c);
Hautmaskeersatz.RING_M = 0.009;                                                // der Mechanismus, nicht die Vorgabe (30 mm)
const rIn = zaehl(Hautmaskeersatz.innen(block, block, Uint32Array.from(TG), randFeld));
// Abstand 0,004 · k > RING_M (0,009) → k ≥ 3: Kern 4 × 4 = 16 Punkte (k = 3 und 4 → Ring von 5 bis 14: 10 breit, k = 0…4)
if (rIn !== 16) fehl('innen mit rand: ' + rIn + ' statt 16');
const schmal = new Uint8Array(G * G), randSchmal = new Float32Array(G * G).fill(Infinity);
for (let r = 5; r <= 14; r++) for (let c = 8; c <= 11; c++) { schmal[r * G + c] = 1; randSchmal[r * G + c] = 0.004 * Math.min(c - 8, 11 - c); }
if (zaehl(Hautmaskeersatz.innen(schmal, schmal, Uint32Array.from(TG), randSchmal)) !== 0) fehl('schmales Stück: nichts darf wegfallen');
if (zaehl(Hautmaskeersatz.innen(schmal, schmal, Uint32Array.from(TG))) !== 0) fehl('schmales Stück mit Ringen: vier Spalten, 2 Ringe → nichts');
const innen6 = new Uint8Array(G * G); innen6[10 * G + 10] = 1;
const weg6 = new Uint8Array(G * G);
Hautmaskeersatz.beruehrt(innen6, Uint32Array.from(TG), weg6);
if (zaehl(weg6) < 7) fehl('beruehrt: ein innen-Punkt nimmt seine Nachbarn mit (mindestens 7 mit den Dreiecken um ihn): ' + zaehl(weg6));

console.log(JSON.stringify({ ok: true, verdeckt: zaehl(a.maske) }));
"""

SKRIPT_MASKE = """
const { Hautmaske } = await import(MODUL);
""" + GEMEINSAM + """
// --- 4. über `Hautmaske.verdeckt` -----------------------------------------------------------------------
const s = stueck(-0.015);
const ersatz4 = new Uint8Array(N * N);
const mit = Hautmaske.verdeckt(K, Uint32Array.from(T), [{ ...s, ersatz: true, starr: true, nahe: 0.006, tiefe: 0.03 }],
                               { ersatz: ersatz4, inseln: 0, normalen: NORM });
const ohne = Hautmaske.verdeckt(K, Uint32Array.from(T), [{ ...s, tiefe: 0.03 }], { inseln: 0, normalen: NORM });
if (zaehl(mit) !== 169) fehl('mit ersatz: 169 erwartet, es sind ' + zaehl(mit));
if (zaehl(ohne) > 121) fehl('ohne ersatz höchstens der Strahl (121), es sind ' + zaehl(ohne));
if (zaehl(ersatz4) !== 169) fehl('optionen.ersatz: 169 erwartet, es sind ' + zaehl(ersatz4));
// `indexOhne` mit `dreieckWeg`: ein Dreieck fällt weg, auch wenn seine Ecken nicht verdeckt sind
const index = Uint32Array.from(T);
const dreieckWeg = new Uint8Array(index.length / 3); dreieckWeg[3] = 1;
const ohneDreieck = Hautmaske.indexOhne(index, [], new Uint8Array(N * N), dreieckWeg);
if (ohneDreieck.entfernt !== 1 || ohneDreieck.index.length !== index.length - 3) fehl('dreieckWeg: ' + ohneDreieck.entfernt);
console.log(JSON.stringify({ ok: true, mitErsatz: zaehl(mit), ohneErsatz: zaehl(ohne) }));
"""


class HautmaskeersatzTest(SimpleTestCase):
    databases = set()

    def test_zylinder_tiefe_ersatz_und_ringe(self):
        ausgabe = MODUL.laufen(SKRIPT_ERSATZ)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertEqual(ausgabe['verdeckt'], 169)

    def test_hautmaske_nimmt_den_ring_nur_mit_ersatz(self):
        ausgabe = MODUL_MASKE.laufen(SKRIPT_MASKE)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertEqual(ausgabe['mitErsatz'], 169)
        self.assertLessEqual(ausgabe['ohneErsatz'], 121)
