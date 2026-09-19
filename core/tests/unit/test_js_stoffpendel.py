# -*- coding: utf-8 -*-
u"""`Stoffpendel` (`gemeinsam/stoffpendel.js`): die Rechnung des Stoffschwungs
der dForce-Kleidung ohne Three.js (18.09.2026, Edgar: „dForce-Stoff …
kannst du das einbauen").

Ein haengender Streifen aus 2 × 6 Punkten (Kantenlaenge 5 cm, 21 Kanten mit
Diagonalen), oberste Reihe gebunden (Freiheit 0), der Rest frei:
1. Ohne Bewegung und ohne Schwerkraft bleibt alles auf der gehaeuteten Lage.
2. Mit Schwerkraft sackt der Saum, aber keine Kante wird laenger als ihre
   Ruhelaenge plus 10 % (Kantenbedingungen); gebundene Punkte ruehren sich nicht.
3. Springt die gehaeutete Lage seitlich, bleibt der Saum zurueck (Traegheit)
   und kommt danach zurueck (Schwerkraft; seit 20.09.2026 mit Schwerkraft
   gerechnet, die Feder ist nur noch Formgedaechtnis - `stoffpendel.js`).
4. Eine Kapsel im Weg drueckt die Punkte auf Radius plus Abstand hinaus.
5. Sprungschutz (18.09.2026 abends, Edgar: „kleider animieren nicht" — das
   Kleid hing in Fetzen, weil die Figur bei Sekunden je Bild weitersprang):
   `bild` setzt bei dt > SPRUNG_DT und bei Entgleisung auf die Lage.

Sabotage-Gegenprobe: die Kantenschleife weglassen -> Fall 2 rot (der Saum
faellt ungebremst); `(alt - xAlt)` weglassen -> Fall 3 rot (keine Traegheit).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'stoffpendel.js')

SKRIPT = """
const { Stoffpendel: S } = await import(MODUL);
const dt = 1 / 30;
// 2 Spalten x 6 Reihen, y von 1,0 abwaerts, Kante 0,05. Die zweite Spalte
// liegt 5 mm tiefer (z): ein exakt ebener Streifen ist in der Ebene ein
// starres Fachwerk und kann sich nach einem Sprung ueberkreuzen, ohne dass
// eine Kante es merkt - echter Stoff ist nie eben und dreht sich heraus.
const ruhe = [], frei = [];
for (let r = 0; r < 6; r++) for (let c = 0; c < 2; c++) {
    ruhe.push(c * 0.05, 1.0 - r * 0.05, c * 0.005);
    frei.push(r === 0 ? 0 : 1);
}
const dreiecke = [];
for (let r = 0; r < 5; r++) {
    const a = 2 * r, b = a + 1, c = a + 2, d = a + 3;
    dreiecke.push(a, b, c, b, d, c);
}
const bau = () => S.ausDreiecken(Float32Array.from(ruhe), Uint32Array.from(dreiecke),
                                 Float32Array.from(frei));
const ziel = Float32Array.from(ruhe);
const laengen = (p) => {
    let max = 0;
    for (let e = 0; e < p.kanten.a.length; e++) {
        const i = 3 * p.kanten.a[e], j = 3 * p.kanten.b[e];
        const l = Math.hypot(p.x[j] - p.x[i], p.x[j + 1] - p.x[i + 1],
                             p.x[j + 2] - p.x[i + 2]);
        max = Math.max(max, l / p.kanten.l[e]);
    }
    return max;
};

// --- 1. Ruhe ohne Schwerkraft ---------------------------------------------
const ohne = Object.assign(Object.create(S), { SCHWERE: 0 });
let p = bau();
for (let i = 0; i < 30; i++) p.schritt(ziel, dt, [], ohne);
const ruht = p.auslenkung(ziel);
if (ruht > 1e-6) throw new Error('Ruhe wandert: ' + ruht);
if (p.kanten.a.length !== 21) throw new Error('Kanten: ' + p.kanten.a.length);

// --- 2. Schwerkraft: der Saum sackt, die Kanten halten ---------------------
p = bau();
for (let i = 0; i < 90; i++) p.schritt(ziel, dt);
const sack = p.auslenkung(ziel);
const dehnung = laengen(p);
if (!(sack > 0.005)) throw new Error('kein Sacken: ' + sack);
if (!(dehnung < 1.10)) throw new Error('Kante gedehnt: ' + dehnung);
if (Math.abs(p.x[1] - 1.0) > 1e-9 || Math.abs(p.x[4] - 1.0) > 1e-9) {
    throw new Error('gebundene Reihe bewegt');
}

// --- 3. Sprung der Lage: Traegheit, dann Rueckkehr -------------------------
//        MIT Schwerkraft (seit 20.09.2026): zurueck bringt den haengenden
//        Streifen die Schwerkraft, nicht mehr die Feder - die ist nur noch
//        Formgedaechtnis.
p = bau();
for (let i = 0; i < 30; i++) p.schritt(ziel, dt);
const versetzt = Float32Array.from(ruhe.map((w, k) => k % 3 === 0 ? w + 0.3 : w));
p.schritt(versetzt, dt);
const sprung = p.auslenkung(versetzt);
if (!(sprung > 0.15)) throw new Error('keine Traegheit: ' + sprung);
for (let i = 0; i < 120; i++) p.schritt(versetzt, dt);
const danach = p.auslenkung(versetzt);
if (!(danach < 0.02)) throw new Error('kehrt nicht zurueck: ' + danach);

// --- 4. Kapsel: Punkte auf r + ABSTAND hinaus ------------------------------
p = bau();
const kapsel = [{ a: [0.025, 0.7, -0.1], b: [0.025, 0.7, 0.1], r: 0.05 }];
for (let i = 0; i < 30; i++) p.schritt(ziel, dt, kapsel, ohne);
let naechster = 1;
for (let i = 2; i < 12; i++) {
    const d = Math.hypot(p.x[3 * i] - 0.025, p.x[3 * i + 1] - 0.7);
    naechster = Math.min(naechster, d);
}
if (!(naechster >= 0.05 + S.ABSTAND - 1e-6)) {
    throw new Error('in der Kapsel: ' + naechster);
}

// --- 5. Sprungschutz: ein Bild von 2 s setzt auf die Lage, ein Bild von 1/10 s
//        laeuft in zwei Teilschritten; eine Entgleisung (Lage 3 m weg) setzt zurueck.
p = bau();
for (let i = 0; i < 30; i++) p.schritt(ziel, dt, [], ohne);
const lag = p.bild(versetzt, 2.0, [], ohne);
if (!lag.zurueckgesetzt || p.auslenkung(versetzt) > 1e-9) throw new Error('Sprung nicht gesetzt');
const teil = p.bild(versetzt, 0.1, [], ohne);
if (teil.zurueckgesetzt) throw new Error('Teilschritt als Sprung');
const weit = Float32Array.from(ruhe.map((w, k) => k % 3 === 0 ? w + 3 : w));
const ent = p.bild(weit, dt, [], ohne);
if (!ent.zurueckgesetzt || p.auslenkung(weit) > 1e-9) throw new Error('Entgleisung nicht gesetzt');

console.log(JSON.stringify({
    ok: true, sack_cm: +(sack * 100).toFixed(1), dehnung: +dehnung.toFixed(3),
    sprung_cm: +(sprung * 100).toFixed(1), danach_cm: +(danach * 100).toFixed(2),
    kapsel_cm: +(naechster * 100).toFixed(2), sprungschutz: true}));
"""


class StoffpendelTest(SimpleTestCase):

    databases = set()

    def test_ruhe_schwerkraft_traegheit_kapsel(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertLess(ausgabe['dehnung'], 1.10)
        self.assertGreater(ausgabe['sprung_cm'], 15)
        self.assertLess(ausgabe['danach_cm'], 2)
        self.assertTrue(ausgabe['sprungschutz'])
