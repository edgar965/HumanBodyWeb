# -*- coding: utf-8 -*-
u"""`Stoffmischung` (`gemeinsam/stoffmischung.js`): der Stoffschwung eines GEMISCHTEN Stücks aus „Kleidung – Generisch"
(30.09.2026, Edgar: „Stoffschwung (dForce) … mischen nicht — beheb das").

Der Worker schwingt das ursprüngliche Netz; `Stoffmischung` überträgt es auf die bleibenden Punkte des zugeschnittenen,
gemischten Netzes:  Punkt i = schwingender Punkt `quelle[i]` + Häutung(`versatz[i]`).

Ein ursprüngliches Netz aus 5 Punkten, bleiben sollen die Punkte 1, 3 und 4:
1. Ein Punkt ohne Versatz ist genau der schwingende Punkt, Normalen stammen von der Quelle.
2. Ein Punkt mit Versatz liegt um den Versatz daneben (Einheitsknochen).
3. Der Versatz dreht mit dem Knochen: 90° um z macht aus +y ein −x (nur der lineare Anteil der Matrix).
4. Die Dreiecke des zugeschnittenen Netzes bekommen die Nummern des ursprünglichen (für dessen Normalen).
5. `lesen` nimmt base64 (JSON) und fertige Puffer (Binärpaket) und gibt für „keine Mischung" null.

Sabotage-Gegenprobe: die Häutung weglassen (`dx` statt `M · d`) -> Fall 3 rot; `quelle[i]` durch `i` ersetzen -> Fall 1
rot; die Nummern der Dreiecke nicht übersetzen -> Fall 4 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'stoffmischung.js')

SKRIPT = """
const { Stoffmischung: S } = await import(MODUL);
const pos = Float32Array.from([0, 0, 0,  1, 0, 0,  2, 0, 0,  3, 0, 0,  4, 0, 0]);
const nrm = Float32Array.from([0, 0, 1,  0, 0, 1,  0, 0, 1,  0, 1, 0,  1, 0, 0]);
const quelle = Uint32Array.from([1, 3, 4]);
const versatz = Float32Array.from([0, 0, 0,  0.01, 0, 0,  0, 0.02, 0]);
// Zwei Knochen (Spalten-Hauptordnung wie Three): 0 = Einheit, 1 = 90° um z (x -> y, y -> -x).
const M = new Float32Array(32);
M.set([1, 0, 0, 0,  0, 1, 0, 0,  0, 0, 1, 0,  0, 0, 0, 1], 0);
M.set([0, 1, 0, 0,  -1, 0, 0, 0,  0, 0, 1, 0,  0, 0, 0, 1], 16);
const skinIndex = Uint16Array.from([0, 0, 0, 0,  0, 0, 0, 0,  1, 0, 0, 0]);
const skinGewicht = Float32Array.from([1, 0, 0, 0,  1, 0, 0, 0,  1, 0, 0, 0]);
const m = new S({ quelle, versatz, skinIndex, skinGewicht });
const aus = m.anwenden(pos, nrm, M);

// --- 1. ohne Versatz: der schwingende Punkt der Quelle, Normale von der Quelle ----------------------------
if (aus.pos.length !== 9 || aus.nrm.length !== 9) throw new Error('Laenge: ' + aus.pos.length);
if (aus.pos[0] !== 1 || aus.pos[1] !== 0 || aus.pos[2] !== 0) throw new Error('Punkt 0: ' + aus.pos.slice(0, 3));
if (aus.nrm[3] !== 0 || aus.nrm[4] !== 1 || aus.nrm[6] !== 1) throw new Error('Normalen: ' + aus.nrm);

// --- 2. mit Versatz am Einheitsknochen: 1 cm weiter in x -------------------------------------------------
if (Math.abs(aus.pos[3] - 3.01) > 1e-6) throw new Error('Versatz: ' + aus.pos[3]);

// --- 3. der Versatz dreht mit dem Knochen: (0, 0,02, 0) -> (-0,02, 0, 0) ----------------------------------
if (Math.abs(aus.pos[6] - 3.98) > 1e-6 || Math.abs(aus.pos[7]) > 1e-6) {
    throw new Error('Versatz dreht nicht mit: ' + aus.pos.slice(6, 9));
}

// --- 4. Dreiecke: Nummern des zugeschnittenen Netzes -> die des urspruenglichen --------------------------
const alt = m.dreiecke(Uint32Array.from([0, 1, 2]));
if (alt.join() !== '1,3,4') throw new Error('Dreiecke: ' + alt.join());

// --- 5. lesen: base64 und Puffer, null ohne Mischung -----------------------------------------------------
const b64 = (a) => Buffer.from(a.buffer, a.byteOffset, a.byteLength).toString('base64');
const a = S.lesen({ quelle: b64(quelle), versatz: b64(versatz) });
const b = S.lesen({ quelle, versatz });
if (a.quelle.join() !== b.quelle.join() || a.versatz.join() !== b.versatz.join()) throw new Error('lesen');
if (S.lesen(null) !== null || S.lesen({}) !== null) throw new Error('lesen ohne Mischung');

console.log(JSON.stringify({ ok: true, x_versatz: +aus.pos[3].toFixed(3), x_gedreht: +aus.pos[6].toFixed(3) }));
"""


class StoffmischungTest(SimpleTestCase):

    databases = set()

    def test_quelle_versatz_haeutung_dreiecke_lesen(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertAlmostEqual(ausgabe['x_versatz'], 3.01, places=3)
        self.assertAlmostEqual(ausgabe['x_gedreht'], 3.98, places=3)
