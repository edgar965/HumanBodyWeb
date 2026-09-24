# -*- coding: utf-8 -*-
"""`Lebendigkeit`: Blinzeln, Blick, Atmen, Variation, Zucken, Schlucken — wiederholbar.

WARUM (Edgar, 13.09.2026: „Lebendigkeit, Blinzeln, Mimikveränderungen um die
aktuelle Mimik … an bei neuer Spur, aber konfigurierbar"):

1. Vorgabe: an, Blinzeln und Blick an, der Rest aus; `vorgabe()` ist eine
   Kopie (Ändern trifft die Vorgabe nicht).
2. Blinzeln: über 60 s Ereignisse mit Abständen im Bereich [2, 6] s, jedes
   0,15 s lang mit Spitze 1 auf beiden Lidern; dieselbe Saat → dieselben
   Zeiten, andere Saat → andere; setzt aus, wenn die Pose die Augen schließt.
3. Variation schwankt um die Pose (nie über ±Stärke), Atmen liegt in [0, s],
   `an: false` liefert nichts.

Sabotage-Gegenprobe: in `ereignis` `if (beginn > t) return null;` entfernen
→ Fall 2 rot (Ereignisse vor ihrem Beginn).
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('studio', 'lebendigkeit.js')

SKRIPT = """
const { Lebendigkeit: L } = await import(MODUL);
const pruefe = (bed, was) => { if (!bed) throw new Error(was); };
// 1. Vorgabe
const v = L.vorgabe();
pruefe(v.an && v.blinzeln.an && v.blick.an && !v.atmen.an && !v.variation.an, 'Vorgabe');
v.blinzeln.an = false;
pruefe(L.VORGABE.blinzeln.an === true, 'vorgabe() ist keine Kopie');
// 2. Blinzeln: Ereignisse sammeln
const e = L.vorgabe(); e.blick.an = false;
const zeiten = (saat) => {
    const aus = []; e.saat = saat; let drin = false;
    for (let t = 0; t < 60; t += 0.005) {
        const z = L.zuschlag(e, t, {});
        const zu = (z.eyeClosedL || 0) > 0.05;
        if (zu && !drin) aus.push(+t.toFixed(3));
        drin = zu;
    }
    return aus;
};
const a = zeiten(7), b = zeiten(7), c = zeiten(8);
pruefe(a.length >= 8 && a.length <= 30, 'Anzahl Blinzeln in 60 s: ' + a.length);
for (let i = 1; i < a.length; i++) {
    const d = a[i] - a[i - 1];
    pruefe(d >= 2 - 0.2 && d <= 6 + 0.2, 'Abstand ' + d);
}
pruefe(JSON.stringify(a) === JSON.stringify(b), 'gleiche Saat, andere Zeiten');
pruefe(JSON.stringify(a) !== JSON.stringify(c), 'andere Saat, gleiche Zeiten');
e.saat = 7;
let spitze = 0, rechts = 0;
for (let t = a[0]; t < a[0] + 0.2; t += 0.002) { const z = L.zuschlag(e, t, {});
spitze = Math.max(spitze, z.eyeClosedL || 0);
rechts = Math.max(rechts, z.eyeClosedR || 0); }
pruefe(spitze > 0.95 && rechts > 0.95, 'Spitze ' + spitze + '/' + rechts);
pruefe(!(L.zuschlag(e, a[0] + 0.03, { eyeClosedL: 1 }).eyeClosedL), 'blinzelt bei geschlossenen Augen');
// 3. Variation, Atmen, aus
const va = L.vorgabe(); va.blinzeln.an = false; va.blick.an = false;
va.variation.an = true; va.variation.staerke = 0.2;
for (let t = 0; t < 20; t += 0.1) {
    const z = L.zuschlag(va, t, { mouthSmile: 1 });
    pruefe(Math.abs(z.mouthSmile || 0) <= 0.2 + 1e-9, 'Variation zu gross: ' + z.mouthSmile);
}
const at = L.vorgabe(); at.blinzeln.an = false; at.blick.an = false; at.atmen.an = true;
at.atmen.staerke = 0.5;
for (let t = 0; t < 8;
t += 0.1) { const n = L.zuschlag(at, t, {}).nostrilsExpansion || 0;
pruefe(n >= 0 && n <= 0.5 + 1e-9, 'Atmen ' + n); }
pruefe(Object.keys(L.zuschlag({ ...L.vorgabe(), an: false }, 3, {})).length === 0, 'aus liefert etwas');
console.log(JSON.stringify({ ok: true, blinzeln: a.length }));
"""


class LebendigkeitTest(SimpleTestCase):
    def test_bausteine_sind_wiederholbar_und_begrenzt(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))
