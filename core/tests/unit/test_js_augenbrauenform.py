# -*- coding: utf-8 -*-
u"""`Augenbrauenform`: Dichte, Dicke, Länge und Lage der Brauenhärchen.

WARUM (Edgar, 13.09.2026: „augenbrauen regler auch sehr schlecht, die Höhe
sollte weiter nach unten verstellbar sein, es fehlen Regler für dicke,
dichte der Augenbrauen, im Moment sind es wie ein paar vereinzelte
Steckrüben"). Geprüft an einem Kunstgesicht — Haut als Punktraster
(1 mm) auf z = 0,10 m mit einer Sklera je Seite — und einem festen Anker
mit 5 Stützen je Seite:

1. Dichte 1 gibt HAARE Härchen je Seite, Dichte 2 doppelt so viele — die
   Stellen liegen zwischen den Stützen (interpoliert), die Wurzeln sind die
   der Stützen.
2. Lage −0,006 setzt jede Stelle 6 mm tiefer, und die Wurzel wird neu auf
   der Haut gesucht (ein Hautpunkt nahe der neuen Stelle).
3. Dicke 2 verdoppelt die Breite eines Streifens, Stärke 2 seine Länge.
4. Das Zittern ist deterministisch: dieselbe Nummer, dieselben Werte; und
   es bleibt klein (|quer| ≤ 0,4 mm).

Sabotage-Gegenprobe: `+ form.lage` weg in `stellen` → Fall 2 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'augenbrauenform.js')

SKRIPT = """
const { Augenbrauenform: F } = await import(MODUL);
const { Augenbrauen: A } = await import(new URL('./augenbrauen.js', MODUL).href);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const nahe = (was, ist, soll, eps) => { if (Math.abs(ist - soll) > eps) throw new Error(was + ': ' + ist + ' statt ' + soll); };
// Haut: Raster x −0,06..0,06, y 1,54..1,62 (1 mm), z = 0,10; Index mit einem Dreieck je drei Punkte
const punkte = []; const idx = [];
for (let y = 1.54; y <= 1.6201; y += 0.001) for (let x = -0.06; x <= 0.0601; x += 0.001) punkte.push(x, y, 0.10);
const n = punkte.length / 3;
for (let i = 0; i + 2 < n; i += 3) idx.push(i, i + 1, i + 2);
const gruppen = [{ start: 0, count: idx.length, materialIndex: 0 }];
const p = Float32Array.from(punkte);
const haut = A.ecken(idx, gruppen, 0);
const wo = (x, y) => { let b = -1, d = 1e9; for (let i = 0; i < n; i++) { const e = (p[3*i]-x)**2 + (p[3*i+1]-y)**2; if (e < d) { d = e; b = i; } } return b; };
// Anker: 5 Stützen je Seite auf y = 1,585 + 0,002·k, x = ±(0,015 + 0,008·k)
const anker = [];
for (const seite of [-1, 1]) for (let k = 0; k < 5; k++) {
    const x = seite * (0.015 + 0.008 * k), y = 1.585 + 0.002 * k;
    const w = wo(x, y); anker.push({ seite, wurzel: w, t: k / 4, dx: x - p[3*w], dy: y - p[3*w+1] });
}
// 1. Dichte
const eins = F.bauen(p, idx, gruppen, { brauen_dichte: 1 }, anker);
pruefe('haare dichte 1', eins.haare, 2 * F.HAARE);
pruefe('haare dichte 2', F.bauen(p, idx, gruppen, { brauen_dichte: 2 }, anker).haare, 4 * F.HAARE);
pruefe('anker bleibt', eins.anker === anker, true);
const st = F.stellen(anker.filter(a => a.seite === 1), p, F.form({ brauen_dichte: 1 }), haut);
pruefe('stellen', st.length, F.HAARE);
nahe('erste stelle x', st[0].p[0], 0.015, 1e-6); nahe('letzte stelle x', st[st.length - 1].p[0], 0.047, 1e-6);
const mitte = st[Math.floor(st.length / 2)];
nahe('mitte interpoliert', mitte.p[1], 1.585 + 0.002 * 4 * mitte.t, 1e-4);
pruefe('wurzel ist eine stuetze', anker.some(a => a.wurzel === mitte.wurzel), true);
// 2. Lage
const tief = F.stellen(anker.filter(a => a.seite === 1), p, F.form({ brauen_lage: -0.006 }), haut);
nahe('6 mm tiefer', tief[0].p[1], st[0].p[1] - 0.006, 1e-6);
const w = tief[0].wurzel; nahe('wurzel unter der stelle x', p[3*w], tief[0].p[0], F.SUCHWEITE + 0.001); nahe('wurzel y', p[3*w+1], tief[0].p[1], F.SUCHWEITE + 0.001);
// 3. Dicke und Staerke
const breite = (s) => Math.hypot(s.ecken[0][0] - s.ecken[1][0], s.ecken[0][1] - s.ecken[1][1]);
const laenge = (s) => Math.hypot(s.ecken[2][0] - s.ecken[1][0], s.ecken[2][1] - s.ecken[1][1]);
const d1 = F.streifen(st[3], 1, F.form({}), 3), d2 = F.streifen(st[3], 1, F.form({ brauen_dicke: 2 }), 3);
nahe('dicke verdoppelt', breite(d2) / breite(d1), 2, 1e-6);
const l2 = F.streifen(st[3], 1, F.form({ brauen_staerke: 2 }), 3);
pruefe('staerke laenger', laenge(l2) > laenge(d1) * 1.5, true);
// 4. Zittern
pruefe('deterministisch', F.zittern(7), F.zittern(7));
pruefe('drei werte in -1..1', F.zittern(7).every(v => v >= -1 && v <= 1) && F.zittern(7).length === 3, true);
pruefe('verschieden', JSON.stringify(F.zittern(7)) !== JSON.stringify(F.zittern(8)), true);
console.log(JSON.stringify({ ok: true }));
"""


class AugenbrauenformTest(SimpleTestCase):

    def test_dichte_lage_dicke_und_zittern(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))
