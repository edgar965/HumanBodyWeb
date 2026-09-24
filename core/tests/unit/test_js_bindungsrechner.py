# -*- coding: utf-8 -*-
u"""`Bindungsrechner` (`gemeinsam/bindungsrechner.js`): die Oberflaechenbindung
fuer HumanBody im Browser (24.09.2026, Edgar: „Implementiere das auch fuer
HumanBody"). Dieselben Felder wie `G9oberflaechenbindung` auf dem Server.

Koerper: ein Quadrat 1 × 1 m in der Ebene z = 0 aus 3 × 3 Punkten (8 Dreiecke),
Normalen +z.
1. Ein Punkt 1 cm ueber der Flaeche: q ist sein Lot, Baryzentrik summiert 1,
   Abstand +0,01, Mischung 1.
2. Mischung: 5 cm → (8 − 5) / (8 − 2,5); 10 cm → frei (Dreieck −1, Mischung 0).
3. Unter der Flaeche: Abstand negativ.
4. Neben dem Rand (x = 1,03 — 3 cm, innerhalb FERN; bei 1,2 waere er frei):
   der naechste Punkt liegt AUF der Kante, eine
   Baryzentrik ist 0, der Abstand ist der schraege Weg nicht — er ist die
   Hoehe entlang der Normale (0,01).
5. `vorzeichen`: ein Wuerfel mit Normalen nach aussen +1, nach innen −1
   (HumanBodys `normal`-Attribut zeigt nach innen).

Sabotage im Kopf: in `naechsterAufDreieck` die Kantenfaelle streichen (nur
„innen") → Fall 4 rot (Baryzentrik ausserhalb [0, 1]); das Vorzeichen in
`vorzeichen` umdrehen → Fall 5 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'bindungsrechner.js')

SKRIPT = """
const { Bindungsrechner: B } = await import(MODUL);
const punkte = [], normalen = [], index = [];
for (let j = 0; j < 3; j++) for (let i = 0; i < 3; i++) {
    punkte.push(i * 0.5, j * 0.5, 0);
    normalen.push(0, 0, 1);
}
for (let j = 0; j < 2; j++) for (let i = 0; i < 2; i++) {
    const a = j * 3 + i, b = a + 1, c = a + 3, d = a + 4;
    index.push(a, b, d, a, d, c);
}
const r = new B(Float32Array.from(punkte), Uint32Array.from(index), Float32Array.from(normalen));
const nah = (a, b, eps = 1e-5) => Math.abs(a - b) < eps;
const q = (aus, i) => {
    const p = [0, 0, 0];
    for (let e = 0; e < 3; e++) {
        const ecke = 3 * aus.dreieck[3 * i + e];
        for (let k = 0; k < 3; k++) p[k] += aus.bary[3 * i + e] * punkte[ecke + k];
    }
    return p;
};
const aus = r.fuer(Float32Array.from([
    0.3, 0.4, 0.01,  0.3, 0.4, 0.05,  0.3, 0.4, 0.10,  0.3, 0.4, -0.01,  1.03, 0.4, 0.01]));

// 1. Lot, Baryzentrik, Abstand, Mischung
const q0 = q(aus, 0);
if (!nah(q0[0], 0.3) || !nah(q0[1], 0.4) || !nah(q0[2], 0)) throw new Error('Lot falsch: ' + q0);
const summe = aus.bary[0] + aus.bary[1] + aus.bary[2];
if (!nah(summe, 1)) throw new Error('Baryzentrik ' + summe);
if (!nah(aus.abstand[0], 0.01)) throw new Error('Abstand ' + aus.abstand[0]);
if (aus.mischung[0] !== 1) throw new Error('Mischung ' + aus.mischung[0]);
// 2. Mischung linear, frei jenseits FERN
const soll = (B.FERN - 0.05) / (B.FERN - B.NAH);
if (!nah(aus.mischung[1], soll, 1e-4)) throw new Error('Mischung 5 cm ' + aus.mischung[1] + ' statt ' + soll);
if (aus.mischung[2] !== 0 || aus.dreieck[6] !== -1) throw new Error('10 cm nicht frei');
// 3. unter der Flaeche
if (!nah(aus.abstand[3], -0.01)) throw new Error('Abstand unten ' + aus.abstand[3]);
// 4. neben dem Rand: auf der Kante, Baryzentrik in [0, 1], eine davon 0
const b4 = [aus.bary[12], aus.bary[13], aus.bary[14]];
if (b4.some(w => w < -1e-6 || w > 1 + 1e-6)) throw new Error('Baryzentrik ausserhalb: ' + b4);
if (!b4.some(w => nah(w, 0))) throw new Error('nicht auf der Kante: ' + b4);
const q4 = q(aus, 4);
if (!nah(q4[0], 1.0) || !nah(q4[1], 0.4)) throw new Error('Kantenpunkt ' + q4);
if (!nah(aus.abstand[4], 0.01)) throw new Error('Abstand am Rand ' + aus.abstand[4]);

// 5. Vorzeichen am Wuerfel
const w = [], wn = [];
for (const x of [-1, 1]) for (const y of [-1, 1]) for (const z of [-1, 1]) {
    w.push(x, y, z);
    wn.push(x, y, z);
}
const aussen = B.vorzeichen(Float32Array.from(w), Float32Array.from(wn));
const innen = B.vorzeichen(Float32Array.from(w), Float32Array.from(wn.map(v => -v)));

console.log(JSON.stringify({ ok: true, aussen, innen, mischung5: aus.mischung[1] }));
"""


class BindungsrechnerTest(SimpleTestCase):

    databases = set()

    def test_lot_mischung_rand_vorzeichen(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertEqual(ausgabe['aussen'], 1)
        self.assertEqual(ausgabe['innen'], -1)
