# -*- coding: utf-8 -*-
"""`Stuecknaht` — der Rand eines verschweißten Stücks folgt der Haut, wie sie JETZT ist, in Node mit dem echten Modul.

BEFUND (Chrome, „cute girl", 09.10.2026): Der Bau legt den Rand des Stücks auf die Ringecken der Haut der Figur des Imports. Die Haut im
Browser weicht davon ab (40 Stichproben im Schambereich: Median 2,2 mm, größte 7,8 mm), und die Randpunkte, die der Server liefert, liegen
bis 1 mm neben der Lage im Bau. Der Rand stand 2–5 mm neben den Ringpunkten der Haut, in Haltung öffnete sich ein Spalt.

Kunstwelt: Stück = Platte 21 × 21 Punkte im Abstand von 2 mm (x, z von −20 bis 20 mm, y = 0), Rand = die vier Seiten, Ring = die vier
Ecken des Quadrats ±20 mm dazu je Seitenmitte (8 Ecken) — die Haut steht an den Ringecken 3 mm höher (y) und 2 mm nach außen.

1. Jede Randecke des Stücks liegt danach (Lage + Verschiebung) genau auf dem Ziel: Lage des Hautpunkts + Verschiebung der Glättung.
   Auch wenn das Stück um 1 mm neben der Lage im Bau steht (die Zuordnung toleriert 4 mm).
2. Die Verschiebung läuft ins Innere aus: ein Punkt 5 mm vom Rand bekommt einen Teil, ab `BAND_M` (10 mm) und im Zentrum bleibt sie 0.
3. Der Bericht nennt die gefundenen Ecken (8 von 8) und die Größe der Verschiebung (größte 3,9 mm an den Ecken des Quadrats).
4. Ein Randpunkt, der keiner Ringecke nahe liegt (das Loch mitten im Stück), bleibt unberührt.

Sabotage-Gegenprobe (nicht gelaufen): `ZUORDNUNG_M` 0,004 → 0,0004 macht Fall 1 rot (das um 1 mm versetzte Stück findet keine Ecke);
`f = 1 − …` zu `f = 1` macht Fall 2 rot; `ring.d` aus dem Ziel streichen macht Fall 1 rot.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'stuecknaht.js')

SKRIPT = """
const { Stuecknaht } = await import(MODUL);
const fehl = (was) => { throw new Error(was); };
const rund = (x) => Math.round(x * 1e6) / 1e6;

const M = 21, H = 0.002;
const P = new Float32Array(M * M * 3), T = [];
for (let r = 0; r < M; r++) for (let c = 0; c < M; c++) P.set([(c - 10) * H, 0, (r - 10) * H], 3 * (r * M + c));
for (let r = 0; r + 1 < M; r++) for (let c = 0; c + 1 < M; c++) {
    const a = r * M + c; T.push(a, a + 1, a + M, a + 1, a + M + 1, a + M);
}
const INDEX = Uint32Array.from(T);
const randId = (r, c) => r * M + c;

// Ring: 8 Ecken auf dem Rand (±20 mm), im Uhrzeigersinn von der Ecke links unten
const ECKEN = [[0, 0], [0, 10], [0, 20], [10, 20], [20, 20], [20, 10], [20, 0], [10, 0]];   // (Zeile, Spalte)
const lage = [], hautpunkte = [], d = [];
const haut = new Float32Array(100 * 3);                              // 8 Hautpunkte für die Ringecken (Nummer 0 … 7)
ECKEN.forEach(([r, c], j) => {
    const x = (c - 10) * H, z = (r - 10) * H;
    lage.push(x, 0, z);
    hautpunkte.push(j);
    // Die Haut steht 3 mm höher und 2 mm weiter außen als im Bau
    const aussenX = Math.sign(x) * 0.002, aussenZ = Math.sign(z) * 0.002;
    haut.set([x + aussenX, 0.003, z + aussenZ], 3 * j);
    d.push(0.0005, 0, 0);                                            // Glättung: 0,5 mm in x
});
const RING = { lage: Float32Array.from(lage), punkte: Uint32Array.from(hautpunkte), d: Float32Array.from(d) };

// --- 1. Randecken auf dem Ziel ------------------------------------------------------------------------
const v = Stuecknaht.verschiebung(P, INDEX, RING, haut);
ECKEN.forEach(([r, c], j) => {
    const i = randId(r, c);
    for (let k = 0; k < 3; k++) {
        const ziel = haut[3 * j + k] + RING.d[3 * j + k];
        const ist = P[3 * i + k] + v.werte[3 * i + k];
        if (Math.abs(ist - ziel) > 1e-6) fehl('Ecke ' + j + ' Achse ' + k + ': ' + rund(ist) + ' statt ' + rund(ziel));
    }
});
// dasselbe mit dem Stück 1 mm neben der Lage im Bau
const P2 = Float32Array.from(P);
for (let i = 0; i < M * M; i++) P2[3 * i + 1] += 0.001;
const v2 = Stuecknaht.verschiebung(P2, INDEX, RING, haut);
ECKEN.forEach(([r, c], j) => {
    const i = randId(r, c), ziel = haut[3 * j + 1] + RING.d[3 * j + 1], ist = P2[3 * i + 1] + v2.werte[3 * i + 1];
    if (Math.abs(ist - ziel) > 1e-6) fehl('versetzt: Ecke ' + j + ': ' + rund(ist) + ' statt ' + rund(ziel));
});

// --- 2. Auslauf ---------------------------------------------------------------------------------------
const mitte = randId(10, 10), nah = randId(10, 2), fern = randId(10, 5);       // 0 mm, 16 mm bzw. 10 mm vom Rand
const betrag = (i) => Math.hypot(v.werte[3 * i], v.werte[3 * i + 1], v.werte[3 * i + 2]);
if (betrag(mitte) !== 0) fehl('im Zentrum bleibt die Verschiebung 0: ' + betrag(mitte));
if (betrag(fern) > 1e-9) fehl('ab 10 mm Weg vom Rand 0: ' + betrag(fern));
const mittel = randId(10, 1);                                                    // 2 mm vom Rand (zwischen zwei Ecken, auf der Kante)
if (!(betrag(mittel) > 0 && betrag(mittel) < betrag(randId(10, 0)))) fehl('der Auslauf nimmt nach innen ab');

// --- 3. Bericht ---------------------------------------------------------------------------------------
if (v.gefunden !== 8 || v.ecken !== 8) fehl('Bericht: ' + v.gefunden + ' von ' + v.ecken);
if (Math.abs(v.maxMm - 3.9) > 0.1) fehl('größte Verschiebung (mm): ' + v.maxMm);     // Ecke links unten: (−1,5 | 3 | −2) mm

// --- 4. ein Loch mitten im Stück bleibt ---------------------------------------------------------------
// Dreieck (5,5)-(5,6)-(6,5) herausnehmen: seine Punkte werden zu Randpunkten, liegen aber an keiner Ringecke
const ohne = [];
for (let t = 0; t + 2 < INDEX.length; t += 3) { if (INDEX[t] === randId(5, 5) && INDEX[t + 1] === randId(5, 6)) continue; ohne.push(INDEX[t], INDEX[t + 1], INDEX[t + 2]); }
const v3 = Stuecknaht.verschiebung(P, Uint32Array.from(ohne), RING, haut);
if (v3.gefunden !== 8) fehl('das Loch darf keine Ecke stehlen: ' + v3.gefunden);
const loch = randId(5, 5);
if (Math.hypot(v3.werte[3 * loch], v3.werte[3 * loch + 1], v3.werte[3 * loch + 2]) > 1e-9) fehl('Punkt am Loch bewegt');
console.log(JSON.stringify({ ok: true, gefunden: v.gefunden, maxMm: v.maxMm }));
"""


class StuecknahtTest(SimpleTestCase):
    databases = set()

    def test_der_rand_des_stuecks_liegt_auf_den_ringecken_der_haut_wie_sie_jetzt_ist(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
