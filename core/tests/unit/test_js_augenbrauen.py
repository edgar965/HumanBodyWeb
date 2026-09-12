# -*- coding: utf-8 -*-
u"""`Augenbrauen`: Härchen aus dem Netz — Bogen vom Auge aus, auf der Haut.

WARUM (Edgar, 12.09.2026: „bei Augen - Wimpern - Nägel fehlen die
Augenbrauen"): Das HumanBody-Netz hat keine Brauen (keine Gruppe, keine
Textur an der Stelle — `ProjektTemp/brauen_probe.py`). Sie werden gebaut:
je Seite ein Bogen relativ zur Augenmitte (Sklera, Gruppe 4), jeder Punkt
auf den vordersten Hautpunkt (Gruppe 0) seiner Umgebung gelegt, darauf
Streifen mit Wurzelpunkt für Hautgewichte.

Geprüft an einem Kunstgesicht: eine ebene Hautplatte (Gruppe 0) vor der
Ebene z = 0,1 mit leichter Wölbung, zwei Augen (Gruppe 4) als Punktwolken:

1. Augenmitten links/rechts kommen aus der Sklera (x-Vorzeichen).
2. Der Bogen hat `haare` Punkte je Seite, liegt ÜBER dem Auge (y größer),
   innen näher an der Nase als außen, und JEDER Punkt sitzt auf einem
   Hautpunkt (Wurzel ist ein Hautindex; z = dessen z).
3. Die Geometrie hat 4 Ecken und 6 Indexeinträge je Streifen; `staerke` 2
   verlängert die Streifen; links und rechts sind spiegelsymmetrisch.
4. Ohne Sklera: keine Brauen (0 Streifen), kein Fehler.
5. Der ANKER (Hautpunkt je Bogenpunkt + Versatz): hebt sich die Haut über
   dem Auge um 5 mm, folgen die Streifen mit dem gemerkten Anker exakt;
   ohne Anker (Bogen neu vom Auge aus) bleiben sie stehen — das war Edgars
   „die einstellung der Augenbrauen (Höhe usw) funktionieren nicht".

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'augenbrauen.js')

SKRIPT = """
const { Augenbrauen: A } = await import(MODUL);
const fehl = (was) => { throw new Error(was); };
const nah = (a, b, eps = 1e-6) => Math.abs(a - b) <= eps;

// Kunstgesicht: Hautgitter 41 x 41 ueber x -0.1..0.1, y 1.50..1.70, z = 0.10 - 0.5*x*x
const P = [], T = [], gruppen = [];
const n = 41;
for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const x = -0.1 + 0.2 * i / (n - 1), y = 1.5 + 0.2 * j / (n - 1);
    P.push(x, y, 0.10 - 0.5 * x * x);
}
const hautStart = T.length;
for (let j = 0; j + 1 < n; j++) for (let i = 0; i + 1 < n; i++) {
    const a = j * n + i, b = a + 1, c = a + n, d = c + 1;
    T.push(a, b, c, b, d, c);
}
gruppen.push({ start: hautStart, count: T.length - hautStart, materialIndex: 0 });
// Augen: je 4 Punkte um (+-0.03, 1.566, 0.09), als Dreiecke der Gruppe 4
const augenStart = T.length;
for (const s of [-1, 1]) {
    const basis = P.length / 3;
    for (const [dx, dy] of [[-0.01, 0], [0.01, 0], [0, 0.01], [0, -0.01]]) {
        P.push(s * 0.03 + dx, 1.566 + dy, 0.09);
    }
    T.push(basis, basis + 1, basis + 2, basis, basis + 3, basis + 1);
}
gruppen.push({ start: augenStart, count: T.length - augenStart, materialIndex: 4 });
const punkte = Float32Array.from(P), index = Uint32Array.from(T);

// 1. Augenmitten
const haut = A.ecken(index, gruppen, 0), sklera = A.ecken(index, gruppen, 4);
if (haut.length !== n * n) fehl('Hautecken ' + haut.length);
const auge = A.augen(punkte, sklera);
if (!nah(auge.links[0], -0.03) || !nah(auge.rechts[0], 0.03) || !nah(auge.links[1], 1.566)) {
    fehl('Augenmitte ' + JSON.stringify(auge));
}

// 2. Bogen
const rechts = A.bogen(punkte, haut, auge.rechts, 1);
if (rechts.length !== A.BOGEN.haare) fehl('Bogenpunkte ' + rechts.length);
for (const b of rechts) {
    if (b.p[1] <= auge.rechts[1]) fehl('Bogen nicht ueber dem Auge');
    if (b.wurzel < 0 || b.wurzel >= n * n) fehl('Wurzel kein Hautpunkt: ' + b.wurzel);
    if (!nah(b.p[2], punkte[3 * b.wurzel + 2])) fehl('Bogenpunkt nicht auf der Haut');
}
if (!(rechts[0].p[0] < rechts[rechts.length - 1].p[0])) fehl('innen/aussen vertauscht');
const aussen = rechts[rechts.length - 1].p[0];
if (!(rechts[0].p[0] < auge.rechts[0] && aussen > auge.rechts[0])) {
    fehl('Braue ueberspannt das Auge nicht');
}

// 3. Geometrie, Staerke, Symmetrie
const g1 = A.bauen(punkte, index, gruppen, 1);
if (g1.haare !== 2 * A.BOGEN.haare) fehl('Streifen ' + g1.haare);
if (g1.positionen.length !== g1.haare * 12 || g1.index.length !== g1.haare * 6
    || g1.wurzeln.length !== g1.haare * 4) fehl('Puffergroessen');
for (const w of g1.wurzeln) if (w >= n * n) fehl('Wurzel ausserhalb der Haut');
const laenge = (g, k) => Math.hypot(g.positionen[12 * k + 6] - g.positionen[12 * k],
                                    g.positionen[12 * k + 7] - g.positionen[12 * k + 1]);
const g2 = A.bauen(punkte, index, gruppen, 2);
if (!(laenge(g2, 0) > 1.8 * laenge(g1, 0))) {
    fehl('Staerke 2 verlaengert nicht: ' + laenge(g1, 0) + ' -> ' + laenge(g2, 0));
}
const h = A.BOGEN.haare;
for (let k = 0; k < h; k++) {
    const l = g1.positionen.subarray(12 * k, 12 * k + 12);
    const r = g1.positionen.subarray(12 * (h + k), 12 * (h + k) + 12);
    for (let e = 0; e < 4; e++) {
        const gespiegelt = nah(l[3 * e], -r[3 * e], 1e-5) && nah(l[3 * e + 1], r[3 * e + 1], 1e-5)
            && nah(l[3 * e + 2], r[3 * e + 2], 1e-5);
        if (!gespiegelt) fehl('nicht symmetrisch, Streifen ' + k);
    }
}
// Streifen liegen VOR der Haut (z groesser als die Wurzel)
for (let k = 0; k < g1.haare; k++) {
    const w = g1.wurzeln[4 * k];
    if (!(g1.positionen[12 * k + 2] > punkte[3 * w + 2])) fehl('Streifen in der Haut');
}

// 4. ohne Sklera
const g0 = A.bauen(punkte, index, [gruppen[0]], 1);
if (g0.haare !== 0) fehl('ohne Auge Brauen gebaut');

// 5. Anker: die Haut ueber den Augen hebt sich um 5 mm (wie Eyebrows_PosZ),
// das Auge bleibt. Mit dem gemerkten Anker folgen die Streifen der Haut;
// ohne Anker (neu vom Auge aus) bleiben sie, wo sie waren.
const gehoben = punkte.slice();
for (let i = 0; i < n * n; i++) {
    if (gehoben[3 * i + 1] > 1.575) gehoben[3 * i + 1] += 0.005;
}
const mitAnker = A.bauen(gehoben, index, gruppen, 1, g1.anker);
const ohneAnker = A.bauen(gehoben, index, gruppen, 1);
if (g1.anker.length !== g1.haare) fehl('Anker je Streifen: ' + g1.anker.length);
if (!nah(mitAnker.positionen[1], g1.positionen[1] + 0.005, 1e-6)) {
    fehl('folgt der Haut nicht: ' + g1.positionen[1] + ' -> ' + mitAnker.positionen[1]);
}
if (Math.abs(ohneAnker.positionen[1] - g1.positionen[1]) > 0.0026) {
    fehl('ohne Anker verschoben');
}

console.log(JSON.stringify({ ok: true, haare: g1.haare,
                             laenge_mm: +(laenge(g1, 0) * 1000).toFixed(2) }));
"""


class AugenbrauenTest(SimpleTestCase):

    def test_bogen_auf_der_haut_und_streifen(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertEqual(ausgabe['haare'], 60)
