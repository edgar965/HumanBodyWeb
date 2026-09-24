# -*- coding: utf-8 -*-
u"""`Gcnachformung` (`gemeinsam/gcnachformung.js`): GarmentCode-Stuecke auf Genesis 9
folgen einem Reglerzug (24.09.2026, Edgar: „fixe auch dies").

Koerper: das Quadrat aus `test_js_bindungsrechner` (3 × 3 Punkte, z = 0).
1. Gleicher Koerper: jeder Punkt bleibt, auch einer neben dem Rand (dort ist
   der Versatz schraeg — mit nur Normale plus Abstand wanderte er).
2. Koerper um 0,1 m in z gehoben: die Punkte mit.
3. Koerper um 90 Grad um z gedreht: ein Punkt 2 cm ueber der Flaeche bleibt 2 cm
   darueber und dreht mit; seine Normale (+x) wird +y.
4. Andere Punktzahl: null (nichts umsetzen).

Sabotage: in `umsetzen` den alten Rahmen fuer den neuen nehmen -> Fall 3 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'gcnachformung.js')

SKRIPT = """
const { Gcnachformung: G } = await import(MODUL);
const punkte = [], index = [];
for (let j = 0; j < 3; j++) for (let i = 0; i < 3; i++) punkte.push(i * 0.5, j * 0.5, 0);
for (let j = 0; j < 2; j++) for (let i = 0; i < 2; i++) {
    const a = j * 3 + i, b = a + 1, c = a + 3, d = a + 4;
    index.push(a, b, d, a, d, c);
}
const alt = Float32Array.from(punkte), I = Uint32Array.from(index);
const stoff = Float32Array.from([0.3, 0.4, 0.02,  1.03, 0.4, 0.01,  0.7, 0.9, -0.005]);
const nah = (a, b, eps = 1e-5) => a.every((w, i) => Math.abs(w - b[i]) < eps);

// 1. gleicher Koerper
const gleich = G.umsetzen(alt, alt, I, stoff);
if (!nah(Array.from(gleich.punkte), Array.from(stoff))) throw new Error('gleich: ' + gleich.punkte);
// 2. gehoben
const hoch = alt.map((w, i) => i % 3 === 2 ? w + 0.1 : w);
const gehoben = G.umsetzen(alt, hoch, I, stoff);
if (!nah(Array.from(gehoben.punkte), Array.from(stoff).map((w, i) => i % 3 === 2 ? w + 0.1 : w)))
    throw new Error('gehoben: ' + gehoben.punkte);
// 3. gedreht um z (x, y) -> (-y, x), mit Normale
const dreh = new Float32Array(alt.length);
for (let i = 0; i < alt.length; i += 3) {
    dreh[i] = -alt[i + 1]; dreh[i + 1] = alt[i]; dreh[i + 2] = alt[i + 2];
}
const gedreht = G.umsetzen(alt, dreh, I, stoff.slice(0, 3), Float32Array.from([1, 0, 0]));
if (!nah(Array.from(gedreht.punkte), [-0.4, 0.3, 0.02])) throw new Error('gedreht: ' + gedreht.punkte);
if (!nah(Array.from(gedreht.normalen), [0, 1, 0])) throw new Error('Normale: ' + gedreht.normalen);
// 4. andere Punktzahl
if (G.umsetzen(alt, alt.slice(3), I, stoff) !== null) throw new Error('andere Topologie umgesetzt');
console.log(JSON.stringify({ ok: true }));
"""


class GcnachformungTest(SimpleTestCase):
    databases = set()

    def test_gleich_gehoben_gedreht_andere_topologie(self):
        self.assertEqual(MODUL.laufen(SKRIPT), {'ok': True})
