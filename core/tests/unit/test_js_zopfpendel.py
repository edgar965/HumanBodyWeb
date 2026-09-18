# -*- coding: utf-8 -*-
u"""`Zopfpendel` (`gemeinsam/zopfpendel.js`): die Rechnung des Zopfschwungs
der Daz-Haare ohne Three.js (18.09.2026, Edgar: „Rigging der Haare?").

Drei Eigenschaften, die ein Verlet-Pendel nach VRMs SpringBone haben muss:
1. Ohne Bewegung des Kopfs bleibt die Spitze in Ruhe — Auslenkung 0.
2. Springt der Kopf, bleibt die Spitze zurueck (Traegheit): Auslenkung > 0,
   und die Laenge bleibt die Knochenlaenge.
3. Steht der Kopf danach still, zieht die Steifigkeit die Spitze zurueck
   in die Ruhe — nach zwei Sekunden unter einem Zentimeter (gemessen im
   Browser: 17 cm -> 0,8 cm).

4. Die Formel selbst, an einem Schritt mit Tempo nachgerechnet.

Sabotage-Gegenprobe: `(g.tail[i] - g.prev[i]) * tr` weglassen -> Fall 4
rot (keine Traegheit); `ruhe[i] * s` weglassen -> Fall 3 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'zopfpendel.js')

SKRIPT = """
const { Zopfpendel: Z } = await import(MODUL);
const dt = 1 / 30;
const ruhe = [0, -1, 0];                       // haengt nach unten
let kopf = [0, 1.6, 0];
const g = Z.glied(0.45, kopf, ruhe);

// --- 1. Ruhe bleibt Ruhe ------------------------------------------------
for (let i = 0; i < 30; i++) Z.schritt(g, kopf, ruhe, dt);
const ruht = Z.auslenkung(g, kopf, ruhe);
if (ruht > 1e-9) throw new Error('Ruhe wandert: ' + ruht);

// --- 2. Der Kopf springt, die Spitze bleibt zurueck ---------------------
kopf = [0.3, 1.6, 0];
const richtung = Z.schritt(g, kopf, ruhe, dt);
const aus = Z.auslenkung(g, kopf, ruhe);
if (!(aus > 0.1)) throw new Error('keine Traegheit: ' + aus);
if (richtung[0] > -0.3) throw new Error('Spitze zeigt nicht zurueck: ' + richtung);
const laenge = Math.hypot(g.tail[0] - kopf[0], g.tail[1] - kopf[1],
                          g.tail[2] - kopf[2]);
if (Math.abs(laenge - 0.45) > 1e-9) throw new Error('Laenge ' + laenge);

// --- 3. Die Steifigkeit holt sie zurueck ---------------------------------
let groesste = 0;
for (let i = 0; i < 60; i++) {
    Z.schritt(g, kopf, ruhe, dt);
    groesste = Math.max(groesste, Z.auslenkung(g, kopf, ruhe));
}
const danach = Z.auslenkung(g, kopf, ruhe);
if (!(danach < 0.01)) throw new Error('kehrt nicht zurueck: ' + danach);
if (!(groesste < 0.9)) throw new Error('schwingt ueber die Laenge hinaus: ' + groesste);

// --- 4. Die Formel der Spezifikation, nachgerechnet ----------------------
// tail (0,1.15,0) mit Tempo (0.03,0,0) je Bild, Kopf (0,1.6,0), Ruhe nach unten:
// next = tail + (0.03,0,0)*0.5 + (0,-1,0)*dt  ->  Richtung normalize(next - kopf).
const h = Z.glied(0.45, [0, 1.6, 0], ruhe);
h.prev = [-0.03, 1.15, 0];
const r4 = Z.schritt(h, [0, 1.6, 0], ruhe, dt);
const soll = [0.015, 1.15 - dt - 1.6, 0];
const n4 = Math.hypot(...soll);
for (let i = 0; i < 3; i++) {
    if (Math.abs(r4[i] - soll[i] / n4) > 1e-9) {
        throw new Error('Formel: ' + r4 + ' statt ' + soll.map(w => w / n4));
    }
}

console.log(JSON.stringify({ok: true, sprung_cm: +(aus * 100).toFixed(1),
                            nach2s_cm: +(danach * 100).toFixed(2)}));
"""


class ZopfpendelTest(SimpleTestCase):

    databases = set()

    def test_ruhe_traegheit_und_rueckkehr(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertGreater(ausgabe['sprung_cm'], 10)
        self.assertLess(ausgabe['nach2s_cm'], 1)
