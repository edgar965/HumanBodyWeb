# -*- coding: utf-8 -*-
"""`Hautnaht` — der Faktor, mit dem die Haut an der Naht zu einem verschweißten Stück ihr Relief verliert, in Node mit dem echten Modul.

BEFUND (Chrome, „cute girl", 09.10.2026): Nach der Angleichung der Normalen blieb an der Naht eine feine Linie — die gebackene Haut trägt
Poren und Wellen, der Rand des Stücks nicht (seine Normalenkarte ist am Inselrand neutral). Ohne Normalenkarten verschwand die Linie fast.

Kunstwelt: Haut = Platte 31 × 31 Punkte im Abstand von 2 mm (x, z von −30 bis 30 mm, y = 0); Ring = die Punkte der mittleren Zeile
z = 0 (31 Punkte, eine Linie — der Weg über das Netz misst den Abstand zu ihr).

1. Auf dem Ring ist der Faktor 1; 6 mm daneben (Zeile 3) liegt er zwischen 0 und 1, ab `BAND_M` (12 mm, Zeile 6; Float32 an der Grenze)
   ist er 0 bis auf Rundung, ab Zeile 7 genau 0.
2. Der Faktor nimmt mit dem Weg monoton ab (Zeile 0 > 1 > 2 > … > 5).
3. Er ist links und rechts vom Ring gleich (die Platte ist symmetrisch).
4. Ohne Ringpunkte: alles 0.

Sabotage-Gegenprobe (nicht gelaufen): `BAND_M` ohne `Infinity`-Abbruch (alle Punkte bekämen Werte) macht Fall 1 rot; `1 − t · t · (3 − 2 · t)` zu
`t` macht Fall 2 rot (der Faktor stiege nach außen).

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'hautnaht.js')

SKRIPT = """
const { Hautnaht } = await import(MODUL);
const fehl = (was) => { throw new Error(was); };

const M = 31, H = 0.002;
const P = new Float32Array(M * M * 3), T = [];
for (let r = 0; r < M; r++) for (let c = 0; c < M; c++) P.set([(c - 15) * H, 0, (r - 15) * H], 3 * (r * M + c));
for (let r = 0; r + 1 < M; r++) for (let c = 0; c + 1 < M; c++) { const a = r * M + c; T.push(a, a + 1, a + M, a + 1, a + M + 1, a + M); }
const INDEX = Uint32Array.from(T);
const id = (r, c) => r * M + c;
const ring = []; for (let c = 0; c < M; c++) ring.push(id(15, c));

const f = Hautnaht.faktor(P, INDEX, ring);
const zeile = (z) => f[id(15 + z, 15)];

// --- 1. Ring 1, 3 Zeilen daneben dazwischen, ab BAND_M 0 -------------------------------------------
if (zeile(0) !== 1) fehl('auf dem Ring: ' + zeile(0));
if (!(zeile(3) > 0 && zeile(3) < 1)) fehl('6 mm daneben: ' + zeile(3));
if (zeile(6) > 1e-6) fehl('12 mm daneben (Float32 an der Grenze): ' + zeile(6));
for (const z of [7, 10, 15]) if (zeile(z) !== 0) fehl('Zeile ' + z + ' (' + (z * 2) + ' mm): ' + zeile(z));

// --- 2. monoton ---------------------------------------------------------------------------------------
for (let z = 0; z < 6; z++) if (!(zeile(z) > zeile(z + 1))) fehl('nicht monoton bei ' + z + ': ' + zeile(z) + ' ≤ ' + zeile(z + 1));

// --- 3. symmetrisch -------------------------------------------------------------------------------------
for (let z = 1; z < 6; z++) if (Math.abs(zeile(z) - zeile(-z)) > 1e-6) fehl('links ≠ rechts bei ' + z);

// --- 4. ohne Ringpunkte --------------------------------------------------------------------------------
const keiner = Hautnaht.faktor(P, INDEX, []);
for (let i = 0; i < keiner.length; i++) if (keiner[i] !== 0) fehl('ohne Ring muss alles 0 sein');
console.log(JSON.stringify({ ok: true, drei: Math.round(zeile(3) * 1000) / 1000 }));
"""


class HautnahtTest(SimpleTestCase):
    databases = set()

    def test_der_faktor_klingt_vom_ring_ueber_das_band_aus(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
