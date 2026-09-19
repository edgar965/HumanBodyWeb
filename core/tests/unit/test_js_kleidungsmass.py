# -*- coding: utf-8 -*-
u"""`Kleidungsmass` (`gemeinsam/kleidungsmass.js`) — die Maße der Kleidungsprobe,
die eine Animation im laufenden Chrome misst (19.09.2026 nachts, Edgar:
„teste mit der ganzen Animation … die Arme sollen nicht in die Kleider
hineinragen, die Hose soll am Koerper bleiben" — und „teste nur in chrome").

Kunstdaten, kein Netz, kein Retarget:
1. Kanten eines Dreiecksindex, jede einmal; Dehnung 2 bei verdoppelter Laenge.
2. Raster: der naechste Punkt und sein Abstand; fern = Rasterweite.
3. Tiefe hinter einer Flaeche: ein Punkt vor der Flaeche positiv, dahinter
   negativ; `wahl` schliesst Flaechenpunkte aus (NaN).
4. Kennzahlen ohne NaN.

Sabotage-Gegenprobe: in `naechster` `d2 = Infinity` statt `weite²` -> Fall 2
rot (der ferne Punkt bekaeme einen echten Abstand statt der Weite).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MASS = Jsmodul('gemeinsam', 'kleidungsmass.js')

SKRIPT = """
const { Kleidungsmass: K } = await import(MODUL);
// 1. zwei Dreiecke mit gemeinsamer Kante: 5 Kanten
const index = Uint32Array.from([0, 1, 2, 0, 2, 3]);
const k = K.kanten(index);
if (k.a.length !== 5) throw new Error('Kanten: ' + k.a.length);
const ruhe = Float32Array.from([0,0,0, 1,0,0, 1,1,0, 0,1,0]);
const bewegt = Float32Array.from([0,0,0, 2,0,0, 2,2,0, 0,2,0]);
const d = K.dehnung(ruhe, bewegt, k);
if (Math.abs(K.kennzahlen(d).max - 2) > 1e-6 || Math.abs(K.kennzahlen(d).p1 - 2) > 1e-6) throw new Error('Dehnung');
// 2. Raster: Koerperpunkte auf einer Linie x = 0..1 (Schritt 0,01), Weite 0,05
const n = 101, koerper = new Float32Array(n * 3);
for (let i = 0; i < n; i++) koerper[3 * i] = i / 100;
const raster = K.raster(koerper, n, 0.05);
const nah = K.naechster(raster, 0.503, 0.02, 0), fern = K.naechster(raster, 0.5, 0.4, 0);
if (nah.i !== 50 || Math.abs(nah.d - Math.hypot(0.003, 0.02)) > 1e-6) throw new Error('nah: ' + JSON.stringify(nah));
if (fern.i !== -1 || Math.abs(fern.d - 0.05) > 1e-9) throw new Error('fern: ' + JSON.stringify(fern));
const ab = K.abstaende(Float32Array.from([0.25, 0.01, 0, 0.5, 0.4, 0]), 2, raster);
if (Math.abs(ab[0] - 0.01) > 1e-6 || Math.abs(ab[1] - 0.05) > 1e-9) throw new Error('abstaende ' + ab);
// 3. Flaeche z = 0 (zwei Dreiecke, Normale +z), Punkte davor und dahinter
const fl = Float32Array.from([0,0,0, 1,0,0, 1,1,0, 0,1,0]);
const fn = K.normalen(fl, index, 4);
if (Math.abs(fn[2] - 1) > 1e-6) throw new Error('Normale ' + fn[2]);
const fr = K.raster(fl, 4, 0.05);
const t = K.tiefen(Float32Array.from([0.01, 0.01, 0.02, 0.01, 0.01, -0.03]), 2, fr, fn);
if (Math.abs(t[0] - 0.02) > 1e-6 || Math.abs(t[1] + 0.03) > 1e-6) throw new Error('Tiefe ' + t);
const tw = K.tiefen(Float32Array.from([0.01, 0.01, 0.02]), 1, fr, fn, (j) => j !== 0);
if (!Number.isNaN(tw[0])) throw new Error('wahl');
// 4. Kennzahlen ohne NaN
const z = K.kennzahlen([3, NaN, 1, 2]);
if (z.n !== 3 || z.min !== 1 || z.max !== 3) throw new Error('Kennzahlen ' + JSON.stringify(z));
console.log(JSON.stringify({ ok: true, kanten: k.a.length, nah_cm: +(nah.d * 100).toFixed(2), tiefe_mm: +(t[1] * 1000).toFixed(1) }));
"""


class KleidungsmassTest(SimpleTestCase):

    databases = set()

    def test_kanten_raster_tiefe(self):
        ausgabe = MASS.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertEqual(ausgabe['kanten'], 5)
        self.assertLess(ausgabe['tiefe_mm'], 0)

    def test_die_probe_ist_in_der_szene_registriert(self):
        from django.conf import settings
        statik = settings.BASE_DIR / 'static' / 'viewer' / 'scene'
        self.assertIn("import './kleidungsprobe.js';", (statik / 'boot.js').read_text(encoding='utf-8'))
        probe = (statik / 'kleidungsprobe.js').read_text(encoding='utf-8')
        self.assertIn('window.__kleidungsprobe = Kleidungsprobe;', probe)
        self.assertIn('Stoffhaut.welt(', probe)
        self.assertIn('Genesis9stoffschwung.probe(sprung, dt)', probe)
