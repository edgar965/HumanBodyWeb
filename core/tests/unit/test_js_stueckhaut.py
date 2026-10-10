# -*- coding: utf-8 -*-
"""`Stueckhautrechnung` — das verschweißte Stück nimmt an seinem Rand die Farbe der Haut an, in Node mit dem echten Modul.

BEFUND (Chrome, „cute girl", 09.10.2026; Edgar: „die Texturanpassung an die Umgebung, warum machst du keine Interpolation der Textur?"): Das Stück hat sein
eigenes Material und die Karte des Originals; an der Naht lag es im Ton neben der Haut (Texturfarben Median 1 %, im untersten Band 7 % im Grün, ohne Licht
gemessen). Erster Versuch mit der UV der Haut je Punkt: an der UV-Naht der Haut (am Damm) kam keine Überblendung zustande (71 Punkte ohne), deshalb die
FARBE je Punkt (Mittel der nächsten Hautpunkte), nicht die UV.

Kunstwelt: Haut = Raster 16 × 16 bei y = 0 im Abstand von 4 mm (x, z von −30 bis 30 mm), Normalen +y; Farbe links (x < 0) 0,3, rechts 0,7 im Rotkanal.
Stück = fünf Punkte auf der Haut oder darüber, `weg` (Weg zum Rand) vorgegeben.

1. Ein Randpunkt (weg 0, 1 mm über der Haut, bei x = 0) hat Maß 1 und die Farbe der Haut dort: Mittel aus links und rechts (0,5).
2. Bei halbem Band (7 mm von 14) ist das Maß 0,5; ab dem Band (14 mm) 0.
3. Ein Punkt 9 mm über der Haut (mehr als `FLUSH_AUS_M`) bekommt Maß 0, auch am Rand — die Lippen behalten ihre Farbe.
4. Ein Punkt über der rechten Hälfte (x = 20 mm) bekommt deren Farbe (0,7), einer über der linken 0,3: die Farbe folgt dem Ort.
5. Die Dünnheit (`dicke`) kommt vom nächsten Hautpunkt.

Sabotage-Gegenprobe (nicht gelaufen): `FLUSH_AUS_M` 0,006 → 1 macht Fall 3 rot; in `rechnen` die Gewichte `1 / (d2 + eps2)` zu `1` (ungewichtet) lässt Fall 4 grün, aber
`K` 4 → 1 macht Fall 1 rot (ein Hautpunkt: 0,3 oder 0,7 statt 0,5); `BAND_M` 0,014 → 1 macht Fall 2 rot.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'stueckhautrechnung.js')

SKRIPT = """
const { Stueckhautrechnung } = await import(MODUL);
const fehl = (was) => { throw new Error(was); };
const nah = (a, b, t = 0.02) => Math.abs(a - b) <= t;

const N = 16, H = 0.004, ox = -0.030;
const pos = new Float32Array(N * N * 3), normal = new Float32Array(N * N * 3), dicke = new Float32Array(N * N);
for (let r = 0; r < N; r++) for (let c = 0; c < N; c++) {
    const i = r * N + c;
    pos.set([ox + c * H, 0, ox + r * H], 3 * i); normal.set([0, 1, 0], 3 * i); dicke[i] = i / 1000;
}
const farbe = (j) => [pos[3 * j] < 0 ? 0.3 : 0.7, 0.5, 0.4];
const haut = { pos, normal, dicke, farbe };
// Stück: Randpunkt auf der Haut bei x = 0; halbes Band; hinter dem Band; 9 mm über der Haut; rechts (x = 20 mm); links (x = −20 mm)
const punkte = Float32Array.from([0, 0.001, 0,   0, 0.001, 0.007,   0, 0.001, 0.014,   0, 0.009, 0.004,   0.020, 0.001, 0,   -0.020, 0.001, 0]);
const weg = Float64Array.from([0, 0.007, 0.014, 0, 0, 0]);
const r = Stueckhautrechnung.rechnen(punkte, { weg }, haut);

// 1. Randpunkt
if (!nah(r.misch[0], 1, 1e-6)) fehl('Randpunkt: Maß ' + r.misch[0]);
if (!nah(r.farbe[0], 0.5, 0.03)) fehl('Randpunkt: Rot ' + r.farbe[0] + ' statt 0,5');
// 2. halbes Band, hinter dem Band
if (!nah(r.misch[1], 0.5, 0.02)) fehl('halbes Band: Maß ' + r.misch[1]);
if (r.misch[2] !== 0) fehl('hinter dem Band: Maß ' + r.misch[2]);
// 3. nicht flach
if (r.misch[3] !== 0) fehl('9 mm über der Haut: Maß ' + r.misch[3]);
// 4. die Farbe folgt dem Ort
if (!nah(r.farbe[3 * 4], 0.7, 0.03)) fehl('rechts: Rot ' + r.farbe[3 * 4]);
if (!nah(r.farbe[3 * 5], 0.3, 0.03)) fehl('links: Rot ' + r.farbe[3 * 5]);
// 5. Dünnheit vom nächsten Hautpunkt: endlich und aus dem Bereich der Haut
if (!(r.dicke[0] >= 0 && r.dicke[0] < 0.256)) fehl('dicke: ' + r.dicke[0]);
console.log(JSON.stringify({ ok: true, mitFarbe: r.mitFarbe }));
"""


class StueckhautTest(SimpleTestCase):
    databases = set()

    def test_das_stueck_nimmt_am_rand_die_farbe_der_haut_an(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
