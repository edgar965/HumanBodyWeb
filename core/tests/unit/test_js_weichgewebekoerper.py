# -*- coding: utf-8 -*-
u"""`Weichgewebekoerper`: die ausgeschriebene Bildschleife gegen die Formeln.

`takt()` rechnet die vier Verformungen INLINE — ohne die Aufrufe von
`velocityskinning.js`, weil die je Punkt-Knochen-Paar kleine Felder
anlegen und bei 600.000 Paaren je Bild den Renderer einfrieren. Damit gibt
es die Formeln zweimal in JavaScript. Dieser Test rechnet ein kleines Netz
einmal ueber `takt()` und einmal Punkt fuer Punkt ueber `Velocityskinning`
(die Fassung, die gegen Python geprueft ist) und verlangt Gleichheit.

Dazu die zwei Proben, die ohne Formelkenntnis gelten:

* RUHE: Ohne Tempo ist der Zuschlag exakt null — Zeile 145/165 des
  Originals ueberspringt jeden stehenden Knochen.
* AHNEN: Ein Punkt, der nur am Handknochen haengt, muss die Drehung des
  Oberarms spueren (Zeile 1259–1294, „rig extended to ancestor"). Ohne
  die Ausdehnung waere sein Zuschlag bei einer Oberarmdrehung null.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'weichgewebekoerper.js')

SKRIPT = """
const { Weichgewebekoerper: K } = await import(MODUL);
const { Velocityskinning: V } = await import(MODUL.replace('weichgewebekoerper', 'velocityskinning'));

// Kette: 0 Rumpf -> 1 Oberarm -> 2 Unterarm -> 3 Hand
const eltern = new Int32Array([-1, 0, 1, 2]);
const gelenke = new Float32Array([0,0,0,  0.2,0,0,  0.5,0,0,  0.8,0,0]);
// Sechs Punkte, jeder an genau einem Knochen (Gewicht 1) — so ist die
// Referenzrechnung je Punkt eindeutig.
const ruhe = new Float32Array([0.1,0.05,0,  0.3,0.1,0.02,  0.4,-0.1,0.05,
                               0.6,0.08,0,  0.9,0.05,0.03, 0.95,-0.05,-0.02]);
const knochenJePunkt = [0, 1, 1, 2, 3, 3];
const n = 6;
const si = new Float32Array(n * 4), sw = new Float32Array(n * 4);
for (let i = 0; i < n; i++) { si[4*i] = knochenJePunkt[i]; sw[4*i] = 1; }
const koerper = new K(ruhe, si, sw, eltern, gelenke);

// Einheitsmatrizen: LBS = Ruhe
const mat = new Float64Array(4 * 16);
for (let k = 0; k < 4; k++) { mat[16*k] = 1; mat[16*k+5] = 1; mat[16*k+10] = 1; mat[16*k+15] = 1; }

// --- 1. Ruhe: kein Tempo, kein Zuschlag --------------------------------
const still = koerper.takt(mat, new Float64Array(gelenke), new Float64Array(12), new Float64Array(12), 1.0);
if (Math.max(...still.map(Math.abs)) !== 0) throw new Error('Ruhe: Zuschlag ' + Array.from(still));

// --- 2. Ahnen: Oberarm dreht, Handpunkt bewegt sich --------------------
const winkel = new Float64Array(12); winkel[3*1 + 2] = 2.0;     // Oberarm um z
const linear = new Float64Array(12);
const aus = koerper.takt(mat, new Float64Array(gelenke), linear, winkel, 1.0);
const hand = Math.hypot(aus[3*4], aus[3*4+1], aus[3*4+2]);
if (hand < 1e-6) throw new Error('Ahnen: Handpunkt spuert die Oberarmdrehung nicht');
// Und der Rumpfpunkt (Knochen 0, Vorfahr des Oberarms, nicht Nachkomme) NICHT.
const rumpf = Math.hypot(aus[0], aus[1], aus[2]);
if (rumpf > 1e-12) throw new Error('Rumpfpunkt bewegt sich bei Oberarmdrehung: ' + rumpf);

// --- 3. Inline gegen Formeln, Punkt fuer Punkt --------------------------
// Beliebige Geschwindigkeiten an allen Knochen.
for (let k = 0; k < 4; k++) { linear[3*k] = 0.3*k - 0.2; linear[3*k+1] = 0.1; linear[3*k+2] = -0.05*k; }
// Winkeltempi so hoch, dass an mindestens einem Punkt der HOECHSTWINKEL
// greift — sonst prueft der Vergleich nur die ungedeckelte Haelfte der
// Formel (Gegenprobe 11.09.2026: „Deckel weg" blieb gruen).
winkel.set([0.5,-0.2,0.1,  6.0,2.4,-1.8,  -0.2,0.9,0.6,  10.0,10.0,-20.0]);
const staerke = 2.5;
let deckelGetroffen = 0;
const ist = koerper.takt(mat, new Float64Array(gelenke), linear, winkel, staerke);
const soll = new Float64Array(n * 3);
const wS = K.SQUASHY * staerke, wF = K.FLOPPY * staerke;
const tmp = new Float64Array(n * 3);
for (let k = 0; k < 4; k++) {
    const { idx, gew } = koerper.punkteJeKnochen[k];
    const v = [linear[3*k], linear[3*k+1], linear[3*k+2]];
    const w = [winkel[3*k], winkel[3*k+1], winkel[3*k+2]];
    const g = [gelenke[3*k], gelenke[3*k+1], gelenke[3*k+2]];
    const c = [koerper.schwerpunktRuhe[3*k], koerper.schwerpunktRuhe[3*k+1], koerper.schwerpunktRuhe[3*k+2]];
    const achse = V.einheit(w);
    const medial = V.einheit([c[0]-g[0], c[1]-g[1], c[2]-g[2]]);
    for (let j = 0; j < idx.length; j++) {
        const i = idx[j], haut = gew[j], wf = wF * koerper.weich[i];
        const p = koerper._lbs;
        let d = [0, 0, 0];
        V.flappyLinear(wf, v, tmp, i);   d = d.map((x, a) => x + tmp[3*i+a]);
        V.squashyLinear(wS, v, p, c, tmp, i); d = d.map((x, a) => x + tmp[3*i+a]);
        const rel = [p[3*i]-g[0], p[3*i+1]-g[1], p[3*i+2]-g[2]];
        const punkttempo = V.norm(V.kreuz(w, rel));
        if (punkttempo * wf > V.HOECHSTWINKEL) deckelGetroffen += 1;
        V.flappyRotation(wf, p, g, achse, punkttempo, tmp, i); d = d.map((x, a) => x + tmp[3*i+a]);
        V.squashyRotation(wS, p, g, medial, achse, punkttempo, tmp, i); d = d.map((x, a) => x + tmp[3*i+a]);
        for (let a = 0; a < 3; a++) soll[3*i+a] += haut * d[a];
    }
}
let groesster = 0;
for (let i = 0; i < n * 3; i++) groesster = Math.max(groesster, Math.abs(ist[i] - soll[i]));
if (groesster > 1e-6) throw new Error('Inline weicht von den Formeln ab: ' + groesster);
if (deckelGetroffen === 0) throw new Error('Kein Punkt traf den Hoechstwinkel — Deckel ungeprueft');
console.log(JSON.stringify({ ok: true, hand_mm: hand * 1000, abweichung: groesster, deckel: deckelGetroffen }));
"""


class WeichgewebekoerperJsTest(SimpleTestCase):

    databases = set()

    def test_inline_rechnet_wie_die_formeln(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertLess(ausgabe['abweichung'], 1e-6)
        self.assertGreater(ausgabe['hand_mm'], 0.0)
