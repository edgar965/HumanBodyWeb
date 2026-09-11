# -*- coding: utf-8 -*-
u"""`Lagenmaske`: welche Punkte eines Stücks unter einem anderen liegen —
geprüft am Kunstkörper, in Node, mit dem echten Modul.

WARUM (11.09.2026, Dance1): Der Bund der Leggings drückte in Bewegung durch
das T-Shirt. Was unter einem anderen Stück liegt, wird nicht gezeichnet —
dieselbe Entscheidung wie für die Haut (`test_js_hautmaske.py`). Geprüft
wird hier, was die Lagenmaske ENTSCHEIDET:

1. Wer außen liegt, wird gemessen: Ein lockeres Rohr (15 mm) über einem
   anliegenden (2 mm) — das innere wird maskiert, das äußere nicht, und die
   Reihenfolge in der Liste ist gleichgültig.
2. Nur die Überlappung zählt; unter dem Saum des äußeren Rohrs bleiben zwei
   Ringe frei (lockere Kante), darunter ist das innere Rohr unberührt.
3. Ein anliegendes äußeres Rohr (Bund über Saum, 2 mm) maskiert bis zu
   seiner Kante.
4. Zwei Stücke ohne Berührung: keine Lage, keine Maske.

Sabotage-Gegenprobe: `bUeberA >= aUeberB ? 1 : -1` → `-1` macht Fall 1 rot;
`if (!bUeberA && !aUeberB) return 0;` entfernt macht Fall 4 rot.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'lagenmaske.js')

SKRIPT = """
const { Lagenmaske } = await import(MODUL);
const fehl = (was) => { throw new Error(was); };

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
    return { punkte: Float32Array.from(P), dreiecke: Uint32Array.from(T), n, ringe, y0, y1 };
}
const yVon = (k, i) => k.y0 + (k.y1 - k.y0) * Math.floor(i / k.n) / (k.ringe - 1);
const summe = (m) => m.reduce((a, b) => a + b, 0);

const koerper = zylinder(0.10, 0.0, 1.0, 51, 36);
const leggings = { schluessel: 'hose', ...zylinder(0.102, 0.10, 0.70, 61, 36) };   // anliegend, Bund bei 0,70
const shirt = { schluessel: 'shirt', ...zylinder(0.115, 0.50, 0.90, 41, 36) };     // locker, Saum bei 0,50

// --- 1. + 2. Das lockere Shirt liegt ueber der Leggings ---------------------
for (const stoffe of [[leggings, shirt], [shirt, leggings]]) {
    const e = Lagenmaske.verdeckt(koerper, stoffe);
    const h = e.get('hose'), s = e.get('shirt');
    if (summe(s.maske) !== 0) fehl('das aeussere Stueck darf nicht maskiert sein: ' + summe(s.maske));
    if (h.ueber.join() !== 'shirt' || s.ueber.length) fehl('ueber: ' + JSON.stringify([h.ueber, s.ueber]));
    const falsch = [];
    for (let i = 0; i < h.maske.length; i++) {
        const y = yVon(leggings, i);
        // Saum des Shirts bei 0,50, zwei Ringe (1 cm) frei: ab 0,525 verdeckt, bis 0,515 frei.
        const soll = y > 0.525 ? 1 : y < 0.515 ? 0 : null;
        if (soll !== null && h.maske[i] !== soll) falsch.push([+y.toFixed(3), h.maske[i]]);
    }
    if (falsch.length) fehl('Leggings-Maske falsch bei ' + JSON.stringify(falsch.slice(0, 6)));
}

// --- 3. Ein anliegender Bund ueber dem Saum maskiert bis zur Kante ---------
const bund = { schluessel: 'bund', ...zylinder(0.104, 0.60, 0.75, 16, 36) };      // 2 mm ueber der Leggings
{
    const e = Lagenmaske.verdeckt(koerper, [leggings, bund]);
    const h = e.get('hose');
    if (e.get('bund').ueber.length) fehl('Bund gilt als innen');
    const falsch = [];
    for (let i = 0; i < h.maske.length; i++) {
        const y = yVon(leggings, i);
        const soll = (y > 0.605 && y < 0.695) ? 1 : y < 0.595 ? 0 : null;
        if (soll !== null && h.maske[i] !== soll) falsch.push([+y.toFixed(3), h.maske[i]]);
    }
    if (falsch.length) fehl('anliegender Bund: ' + JSON.stringify(falsch.slice(0, 6)));
}

// --- 4. Ohne Beruehrung: nichts ---------------------------------------------
const kragen = { schluessel: 'kragen', ...zylinder(0.104, 0.85, 0.95, 11, 36) };
{
    const e = Lagenmaske.verdeckt(koerper, [leggings, kragen]);
    if (summe(e.get('hose').maske) || summe(e.get('kragen').maske)) fehl('ohne Beruehrung maskiert');
    if (e.get('hose').ueber.length || e.get('kragen').ueber.length) fehl('ohne Beruehrung eine Lage');
}

console.log(JSON.stringify({ ok: true }));
"""


class LagenmaskeTest(SimpleTestCase):

    databases = []

    def test_lage_ueberlappung_und_kanten(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
