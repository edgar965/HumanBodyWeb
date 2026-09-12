# -*- coding: utf-8 -*-
u"""`Ruhematrix`: die Ruhelage des Skeletts, unabhaengig von der Figurlage.

WARUM (Edgar, 07.09.2026: „bei SMPL verschwinden die Kleider beim Abspielen
einer Animation")
=================================================================
`THREE.Skeleton` rechnet seine `boneInverses` aus `bone.matrixWorld` — aus
der Lage, in der die Figur GERADE steht. Der Koerper wird gebunden, waehrend
sie im Ursprung ist; ein GarmentCode-Stueck 16 Sekunden spaeter, wenn sie
laengst 90 cm weiter steht. Dann liegen `bindMatrix` und `boneInverses` in
verschiedenen Bezugssystemen, der Gruppenversatz wird doppelt verrechnet —
und das Kleidungsstueck zerreisst in meterlange Zacken (gemessen: bis
1,92 m). Der Koerper blieb heil, weil er noch im Ursprung gebunden wurde.

`knochenbau.js` rechnet die Ruhelage deshalb aus dem Bauplan; die Rechnung
steht hier, ohne Three.js, und ist damit pruefbar.

ZWEI FEHLER, DIE STILL BLEIBEN, und gegen die dieser Test steht:

1. **Zeilen- statt Spaltenfolge.** `THREE.Matrix4.elements` ist
   spaltenweise. Wer zeilenweise rechnet, bekommt die transponierte —
   also die UMGEKEHRTE — Drehung. Die Figur steht dann verdreht da, und es
   sieht aus wie ein Fehler im Retarget.
2. **Reihenfolge der Multiplikation.** `eltern × eigen` und `eigen ×
   eltern` sind verschieden, sobald eine Drehung im Spiel ist. Bei einer
   Kette ohne Drehungen faellt es nicht auf — genau deshalb steht hier eine
   MIT Drehungen.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'ruhematrix.js')

SKRIPT = """
const { Ruhematrix: R } = await import(MODUL);
const nahe = (was, ist, soll, toleranz = 1e-9) => {
    const weit = ist.some((w, i) => Math.abs(w - soll[i]) > toleranz);
    if (weit) throw new Error(was + ': ' + JSON.stringify(ist.map(w => +w.toFixed(6)))
        + ' statt ' + JSON.stringify(soll.map(w => +w.toFixed(6))));
};

// Eine Kette mit Drehungen — ohne sie merkt man weder Transponierung
// noch vertauschte Reihenfolge.
const halb = Math.SQRT1_2;
const plan = [
    { name: 'wurzel', eltern: null,     pos: [0, 1, 0],   quat: [0, 0, 0, 1] },
    // 90 Grad um Z: +Y zeigt danach nach -X.
    { name: 'arm',    eltern: 'wurzel', pos: [0, 0.2, 0], quat: [0, 0, halb, halb] },
    { name: 'hand',   eltern: 'arm',    pos: [0, 0.3, 0], quat: [0, 0, 0, 1] },
];

// --- 1. Die Kette landet, wo sie soll ------------------------------------
const kette = R.kette(plan);
nahe('Wurzel', R.punkt(kette.get('wurzel')), [0, 1, 0]);
nahe('Arm',    R.punkt(kette.get('arm')),    [0, 1.2, 0]);
// Die Hand geht 0,3 in der GEDREHTEN Achse des Arms, also nach -X.
nahe('Hand',   R.punkt(kette.get('hand')),   [-0.3, 1.2, 0]);

// --- 2. Spaltenfolge, nicht Zeilenfolge ----------------------------------
// Die Verschiebung steht in `THREE.Matrix4.elements` an 12..14.
const m = R.aus([1, 2, 3], [0, 0, 0, 1]);
nahe('Verschiebung an 12..14', [m[12], m[13], m[14]], [1, 2, 3]);
// Eine Drehung um Z um 90 Grad: Spalte 0 (Elemente 0..2) ist das Bild von X.
const dreh = R.aus([0, 0, 0], [0, 0, halb, halb]);
nahe('Bild von X', [dreh[0], dreh[1], dreh[2]], [0, 1, 0]);
nahe('Bild von Y', [dreh[4], dreh[5], dreh[6]], [-1, 0, 0]);

// --- 3. Die Reihenfolge der Multiplikation -------------------------------
const a = R.aus([1, 0, 0], [0, 0, halb, halb]);
const b = R.aus([0, 2, 0], [0, 0, 0, 1]);
// a x b heisst: erst b, dann a. b bringt den Ursprung auf (0,2,0), a dreht
// das um 90 Grad zu (-2,0,0) und verschiebt um (1,0,0).
nahe('a x b', R.punkt(R.mal(a, b)), [-1, 0, 0]);
nahe('b x a', R.punkt(R.mal(b, a)), [1, 2, 0]);

// --- 4. Leere und unbekannte Eltern verschlucken nichts ------------------
if (R.kette([]).size !== 0) throw new Error('leerer Plan liefert Eintraege');
if (R.kette(null).size !== 0) throw new Error('null liefert Eintraege');
const verwaist = R.kette([
    { name: 'x', eltern: 'gibtsnicht', pos: [5, 0, 0], quat: [0, 0, 0, 1] }]);
nahe('verwaist steht absolut', R.punkt(verwaist.get('x')), [5, 0, 0]);

// --- 5. Ohne Drehung die Einheit -----------------------------------------
nahe('Einheit', R.aus([0, 0, 0], null), R.einheit());

console.log(JSON.stringify({ok: true}));
"""


class RuhematrixTest(SimpleTestCase):

    databases = set()

    def test_ruhelage(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
