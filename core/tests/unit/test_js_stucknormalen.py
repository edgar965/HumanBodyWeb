# -*- coding: utf-8 -*-
"""`Stucknormalen` — die Normalen am Rand eines verschweißten Stücks gehen in die der Haut über, in Node mit dem echten Modul.

BEFUND (Chrome, „cute girl", 09.10.2026, Edgar: „ich kann es nicht glauben, dass wir einen Tag an einer Naht arbeiten"): Der Rand des
Stücks lag genau auf den Ringecken der Haut, an der Naht stand trotzdem eine Linie — die Farbe sprang quer über sie von 226/203/186 auf
210/182/165. Die Normalen des Stücks am Rand wichen von denen der Haut ab (98 Ringecken: Median 19°, 90. Perzentil 73°, größter 82°);
mit den Normalen der Haut am Rand und einem Übergang über 10 mm lief die Farbe stetig (224/199/182 … 199/163/147 über rund 100 Pixel).

Kunstwelt: Stück = Platte 21 × 21 Punkte im Abstand von 2 mm (x, z von −20 bis 20 mm, y = 0), Normalen des Stücks alle (0, 1, 0);
Rand = die vier Seiten, acht Ringecken (vier Ecken, vier Seitenmitten); die Haut hat an jeder Ecke dieselbe Normale, 45° zur Seite
geneigt. `weg` (Weg über das Netz zum Rand) ist hier der Abstand zur nächsten Randzeile — auf dem Gitter dasselbe.

1. Randpunkte tragen die Normale der Haut ihrer Ringecke (Winkel < 0,01°), auch zwischen zwei Ecken.
2. Die Normale geht nach innen stetig in die des Stücks über: ein Punkt 4 mm vom Rand liegt zwischen beiden und ab `BAND_M` (10 mm)
   und in der Mitte gilt die des Stücks (Winkel 0); der Winkel zum Stück nimmt nach innen ab.
3. Ein zweiter Lauf mit denselben Eingaben ergibt dasselbe (die Rechnung geht von `ruhe` aus, nicht vom Ergebnis).
4. Ohne Randpunkte (`weg` null) bleibt alles, wie es war (Kopie von `ruhe`), und die Zahl der geänderten Punkte ist 0.

Sabotage-Gegenprobe (nicht gelaufen): `normalen.set(ruhe)` am Anfang streichen macht Fall 3 rot; `f = 1 − …` zu `f = 1` macht Fall 2 rot
(die Mitte bekäme die Normale der Haut); `abstand[r] > nah + WEITE_M` zu `abstand[r] > 0` macht Fall 1 rot (nur der nächste zählt nicht mehr —
hier zufällig gleich, darum nicht abgedeckt).

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'stucknormalen.js')

SKRIPT = """
const { Stucknormalen } = await import(MODUL);
const fehl = (was) => { throw new Error(was); };

const M = 21, H = 0.002;
const P = new Float32Array(M * M * 3);
for (let r = 0; r < M; r++) for (let c = 0; c < M; c++) P.set([(c - 10) * H, 0, (r - 10) * H], 3 * (r * M + c));
const randId = (r, c) => r * M + c;

const ECKEN = [[0, 0], [0, 10], [0, 20], [10, 20], [20, 20], [20, 10], [20, 0], [10, 0]];
const hautN = new Float32Array(8 * 3), s = Math.SQRT1_2;
for (let j = 0; j < 8; j++) hautN.set([s, s, 0], 3 * j);                 // 45° zur Seite geneigt
const RINGPUNKTE = Uint32Array.from([0, 1, 2, 3, 4, 5, 6, 7]);
const RUHE = new Float32Array(M * M * 3);
for (let i = 0; i < M * M; i++) RUHE.set([0, 1, 0], 3 * i);
// Winkel über atan2(Kreuzprodukt, Skalarprodukt): `acos` nahe 1 verstärkt den Float32-Rundungsfehler der Normalen auf rund 0,02° (gemessen
// 10.10.2026: 0,015° zwischen zwei gleichen Float32-Normalen, Node 24.12) — das hätte die Schwelle von 0,01° ohne Befund gerissen.
const winkel = (a, i, b, j) => {
    const [ax, ay, az, bx, by, bz] = [a[3*i], a[3*i+1], a[3*i+2], b[3*j], b[3*j+1], b[3*j+2]];
    const kreuz = Math.hypot(ay*bz - az*by, az*bx - ax*bz, ax*by - ay*bx);
    return Math.atan2(kreuz, ax*bx + ay*by + az*bz) * 180 / Math.PI;
};

// Randpunkte: alle Punkte der vier Seiten, je der nächsten der acht Ringecken zugeordnet; `weg` = Abstand zum Rand
const ids = [], ecke = [];
for (let r = 0; r < M; r++) for (let c = 0; c < M; c++) {
    if (r !== 0 && r !== 20 && c !== 0 && c !== 20) continue;
    let best = 0, bd = Infinity;
    ECKEN.forEach(([er, ec], j) => { const dd = Math.hypot(er - r, ec - c); if (dd < bd) { bd = dd; best = j; } });
    ids.push(randId(r, c)); ecke.push(best);
}
const weg = new Float64Array(M * M);
for (let r = 0; r < M; r++) for (let c = 0; c < M; c++) weg[randId(r, c)] = H * Math.min(r, c, 20 - r, 20 - c);
const NAHT = { weg, randpunkte: { ids: Uint32Array.from(ids), ecke: Uint32Array.from(ecke) } };

const N = new Float32Array(RUHE);
const geaendert = Stucknormalen.angleichen(P, N, RUHE, NAHT, RINGPUNKTE, hautN);
if (!(geaendert > 8)) fehl('geänderte Punkte: ' + geaendert);

// --- 1. Randpunkte: Normale der Haut ---------------------------------------------------------------
for (const [r, c] of ECKEN) {
    const w = winkel(N, randId(r, c), hautN, 0);
    if (w > 0.01) fehl('Ecke ' + r + ',' + c + ': ' + w + '° gegen die Haut');
}
const seite = winkel(N, randId(0, 5), hautN, 0);
if (seite > 0.01) fehl('Randpunkt zwischen zwei Ecken: ' + seite + '°');

// --- 2. stetiger Übergang ----------------------------------------------------------------------------
const zumStueck = (i) => winkel(N, i, RUHE, 0);
const nah = zumStueck(randId(2, 10)), mitte = zumStueck(randId(10, 10)), fern = zumStueck(randId(5, 10));
if (!(nah > 0 && nah < 45)) fehl('4 mm vom Rand liegt zwischen beiden: ' + nah);
if (mitte > 1e-6) fehl('in der Mitte gilt die Normale des Stücks: ' + mitte);
if (fern > 1e-6) fehl('10 mm vom Rand gilt die Normale des Stücks: ' + fern);
if (!(zumStueck(randId(0, 10)) > zumStueck(randId(1, 10)) && zumStueck(randId(1, 10)) > nah)) fehl('der Übergang nimmt nach innen ab');

// --- 3. zweiter Lauf ---------------------------------------------------------------------------------
const vorher = Float32Array.from(N);
Stucknormalen.angleichen(P, N, RUHE, NAHT, RINGPUNKTE, hautN);
for (let i = 0; i < N.length; i++) if (Math.abs(N[i] - vorher[i]) > 1e-7) fehl('zweiter Lauf anders bei ' + i);

// --- 4. ohne Randpunkte ----------------------------------------------------------------------------
const N2 = new Float32Array(RUHE.length).fill(7);
const keine = Stucknormalen.angleichen(P, N2, RUHE, { weg: null, randpunkte: { ids: new Uint32Array(0), ecke: new Uint32Array(0) } }, RINGPUNKTE, hautN);
if (keine !== 0) fehl('ohne Randpunkte keine Änderung: ' + keine);
for (let i = 0; i < N2.length; i++) if (N2[i] !== RUHE[i]) fehl('ohne Randpunkte ist das Ergebnis `ruhe`');
console.log(JSON.stringify({ ok: true, geaendert, nah: Math.round(nah * 10) / 10 }));
"""


class StucknormalenTest(SimpleTestCase):
    databases = set()

    def test_die_normalen_am_rand_gehen_stetig_in_die_der_haut_ueber(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
