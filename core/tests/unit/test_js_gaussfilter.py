# -*- coding: utf-8 -*-
"""`Gaussfilter` gegen die alte, zweite Fassung — Wert für Wert.

WARUM (18.08.2026)
=================
Der Gauß-Filter stand in `werkzeug_glaettung.js` ZWEIMAL: als `_gaussFilter` und
ausgeschrieben in `smoothSelectedClip`. Beide Fassungen bauten denselben Kern,
falteten gleich und normierten Quaternionen gleich — nur eben getrennt. Jetzt ist
es eine Klasse, und dieser Test rechnet sie gegen die ALTE Fassung.

Geglättet werden QUATERNIONEN. Eine falsche Rechnung fällt beim Ansehen kaum auf:
Die Figur bewegt sich weiter, nur etwas anders — und wer die Glättung einschaltet,
erwartet genau das. Deshalb Zahlen statt Blick.

DIE FÄLLE, DIE WEHTUN
=====================
* **Ränder**: Am Anfang und Ende wird der Randwert gehalten, nicht gespiegelt und
  nicht mit 0 aufgefüllt. Ein Nullwert würde die Figur dort in die Ruhelage
  ziehen.
* **Normierung**: Nach der Faltung ist ein Quaternion nicht mehr auf Länge 1 —
  ein nicht normiertes Quaternion SKALIERT das Skelett (die Figur wird verzerrt).
* **stride 3** (Positionen): Da wird NICHT normiert; eine Normierung würde die
  Figur in den Einheitskreis um den Ursprung zwingen.
* **Entartetes Quaternion** (Länge 0): bleibt, wie es ist — kein Teilen durch 0.

Ohne `node` im Pfad wird der Test übersprungen, nicht rot.
"""
import shutil
import unittest
from pathlib import Path

from djangobase.testhelfer import Webmodul

WURZEL = Path(__file__).resolve().parents[3]
MODUL = WURZEL / 'static' / 'viewer' / 'bvh_studio' / 'gaussfilter.js'
STATIC_WURZELN = {
    '/static/djangobase/': Path(__import__('djangobase').__file__).parent
                           / 'static' / 'djangobase',
    '/static/': WURZEL / 'static',
}

SKRIPT = """
const { Gaussfilter } = await import(MODUL);

// --- die ALTE Fassung, unveraendert aus werkzeug_glaettung.js ---------------
function alt(values, stride, sigma) {
    const nKeys = values.length / stride;
    const radius = Math.ceil(sigma * 3);
    const kernel = [];
    let ksum = 0;
    for (let i = -radius; i <= radius; i++) {
        const v = Math.exp(-0.5 * (i / sigma) ** 2);
        kernel.push(v); ksum += v;
    }
    for (let i = 0; i < kernel.length; i++) kernel[i] /= ksum;
    const orig = new Float32Array(values);
    for (let c = 0; c < stride; c++) {
        for (let k = 0; k < nKeys; k++) {
            let sum = 0;
            for (let j = 0; j < kernel.length; j++) {
                const idx = Math.max(0, Math.min(nKeys - 1, k + j - radius));
                sum += kernel[j] * orig[idx * stride + c];
            }
            values[k * stride + c] = sum;
        }
    }
    if (stride === 4) {
        for (let k = 0; k < nKeys; k++) {
            const i = k * 4;
            const len = Math.sqrt(values[i]**2 + values[i+1]**2 + values[i+2]**2 + values[i+3]**2);
            if (len > 1e-8) { values[i]/=len; values[i+1]/=len; values[i+2]/=len; values[i+3]/=len; }
        }
    }
    return values;
}

function reihe() {
    // Eine Stufe: vier Bilder in Ruhe, vier gedreht (stride 4).
    const werte = [];
    for (let i = 0; i < 8; i++) {
        werte.push(i < 4 ? 1 : 0.7071, 0, i < 4 ? 0 : 0.7071, 0);
    }
    return new Float32Array(werte);
}

const ergebnis = {};

// 1) Gleichheit mit der alten Fassung, drei Sigmas
ergebnis.gleich = [];
for (const sigma of [0.5, 1, 2.5]) {
    const a = alt(reihe(), 4, sigma);
    const b = new Gaussfilter(sigma).anwenden(reihe(), 4);
    let groesster = 0;
    for (let i = 0; i < a.length; i++) {
        groesster = Math.max(groesster, Math.abs(a[i] - b[i]));
    }
    ergebnis.gleich.push(Number(groesster.toFixed(12)));
}

// 2) Kern: Summe 1, symmetrisch, Laenge 2r+1
const kern = Gaussfilter.kern(2, 6);
ergebnis.kern = {
    laenge: kern.length,
    summe: Number(kern.reduce((s, x) => s + x, 0).toFixed(9)),
    symmetrisch: Math.abs(kern[0] - kern[kern.length - 1]) < 1e-12,
    mitteAmGroessten: kern[6] === Math.max(...kern),
};

// 3) Quaternionen sind nach der Glaettung auf Laenge 1
const geglaettet = new Gaussfilter(1.5).anwenden(reihe(), 4);
ergebnis.laengen = [];
for (let i = 0; i < geglaettet.length; i += 4) {
    ergebnis.laengen.push(Number(Math.sqrt(
        geglaettet[i]**2 + geglaettet[i+1]**2 + geglaettet[i+2]**2
        + geglaettet[i+3]**2).toFixed(6)));
}

// 4) Raender werden GEHALTEN: eine konstante Reihe bleibt konstant
const konstant = new Float32Array(Array.from({length: 6 * 3}, (_, i) => (i % 3 === 0 ? 5 : 0)));
const nachher = new Gaussfilter(2).anwenden(konstant, 3);
ergebnis.raender = { erster: Number(nachher[0].toFixed(6)),
                     letzter: Number(nachher[nachher.length - 3].toFixed(6)) };

// 5) stride 3 wird NICHT normiert
const positionen = new Float32Array([3, 4, 0, 3, 4, 0, 3, 4, 0]);
const posNachher = new Gaussfilter(1).anwenden(positionen, 3);
ergebnis.positionslaenge = Number(
    Math.sqrt(posNachher[0]**2 + posNachher[1]**2 + posNachher[2]**2).toFixed(4));

// 6) Entartetes Quaternion bleibt, wie es ist
const entartet = new Float32Array([0, 0, 0, 0]);
Gaussfilter.normieren(entartet);
ergebnis.entartet = [...entartet];

console.log(JSON.stringify(ergebnis));
"""


@unittest.skipUnless(shutil.which('node'), 'node fehlt')
class GaussfilterTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ergebnis = Webmodul(MODUL, STATIC_WURZELN).laufen(SKRIPT)

    def test_gleiche_werte_wie_die_alte_fassung(self):
        """Bei drei Sigmas: kein Wert weicht messbar ab."""
        for abweichung in self.ergebnis['gleich']:
            self.assertLess(abweichung, 1e-6, 'Filter rechnet anders als vorher')

    def test_kern_ist_normiert_und_symmetrisch(self):
        kern = self.ergebnis['kern']
        self.assertEqual(kern['laenge'], 13, '2·6 + 1')
        self.assertEqual(kern['summe'], 1.0)
        self.assertTrue(kern['symmetrisch'])
        self.assertTrue(kern['mitteAmGroessten'])

    def test_quaternionen_haben_laenge_eins(self):
        """Ohne Normierung skaliert ein Quaternion das Skelett."""
        for laenge in self.ergebnis['laengen']:
            self.assertEqual(laenge, 1.0)

    def test_raender_werden_gehalten(self):
        """Eine konstante Reihe bleibt konstant — kein Abfall an den Enden."""
        self.assertEqual(self.ergebnis['raender']['erster'], 5.0)
        self.assertEqual(self.ergebnis['raender']['letzter'], 5.0)

    def test_positionen_werden_nicht_normiert(self):
        """(3, 4, 0) hat Länge 5 und muss sie behalten."""
        self.assertEqual(self.ergebnis['positionslaenge'], 5.0)

    def test_entartetes_quaternion_bleibt(self):
        self.assertEqual(self.ergebnis['entartet'], [0, 0, 0, 0])
