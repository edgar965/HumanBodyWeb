# -*- coding: utf-8 -*-
"""`Koerpertiefe`: der Bodenfix misst den tiefsten Punkt des ganzen Netzes.

WARUM (Edgar, 13.09.2026: „die Fußspitzen gehen noch in den Boden hinein …
nimm den tiefsten Punkt des Körpers bei jedem Animationsframe"): Vorher
zählte ein 1-cm-Sohlenband der Ruhelage, davor der tiefste Knochenkopf.
Geprüft mit Attrappen (eine kleine spaltenweise 4×4-Matrix wie `Matrix4`):

1. `netzY` rechnet die Skinning-Kette — Knochenwelt · Knocheninverse, davor
   `matrixWorld · bindMatrixInverse`, dahinter `bindMatrix` — und liefert
   den tiefsten Punkt, auch wenn er in der Ruhelage NICHT der tiefste ist
   (p0 liegt in Ruhe bei 0,2, hängt aber am Knochen, der um 0,5 sinkt).
2. Gemischte Gewichte werden gemischt (p2: halb/halb → −0,1).
3. Ohne gehäutetes Netz gilt der tiefste Knochen.

Sabotage-Gegenprobe: in `yZeilen` das `.premultiply(vorn)` weglassen →
Fall 1 rot (−0,3 statt −0,2, die Weltverschiebung fehlt).
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul("scene", "koerpertiefe.js")

SKRIPT = """
const { Koerpertiefe: K } = await import(MODUL);
const nah = (was, a, b) => {
    if (Math.abs(a - b) > 1e-6) throw new Error(was + ': ' + a + ' statt ' + b);
};
// Spaltenweise 4x4 wie THREE.Matrix4 — nur, was Koerpertiefe braucht.
class M {
    constructor() { this.elements = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]; }
    static verschoben(y) { const m = new M(); m.elements[13] = y; return m; }
    multiplyMatrices(a, b) {
        const ae = a.elements, be = b.elements, e = new Array(16).fill(0);
        for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++)
            for (let k = 0; k < 4; k++) e[j*4+i] += ae[k*4+i] * be[j*4+k];
        this.elements = e; return this;
    }
    multiply(b) { return this.multiplyMatrices(new M().kopie(this), b); }
    premultiply(a) { return this.multiplyMatrices(a, new M().kopie(this)); }
    kopie(m) { this.elements = m.elements.slice(); return this; }
}
// Knochen 0 sinkt um 0,5; Knochen 1 bleibt. Das Netz steht 0,1 hoeher.
const knochen = [{ matrixWorld: M.verschoben(-0.5) }, { matrixWorld: new M() }];
const netz = {
    isSkinnedMesh: true,
    matrixWorld: M.verschoben(0.1), bindMatrix: new M(), bindMatrixInverse: new M(),
    skeleton: { bones: knochen, boneInverses: [new M(), new M()] },
    geometry: { attributes: {
        position:   { count: 3, array: Float32Array.from([0,0.2,0,  0,0,0,  0,0.05,0]) },
        skinIndex:  { array: Float32Array.from([0,0,0,0,  1,0,0,0,  0,1,0,0]) },
        skinWeight: { array: Float32Array.from([1,0,0,0,  1,0,0,0,  0.5,0.5,0,0]) },
    } },
};
if (!K.messbar(netz)) throw new Error('messbar');
// p0: 0,2 − 0,5 + 0,1 = −0,2 (tiefster, obwohl in Ruhe der hoechste)
// p1: 0 + 0,1 = 0,1 · p2: ½(0,05−0,5+0,1) + ½(0,05+0,1) = −0,1
nah('netzY', K.netzY(netz), -0.2);
let aufrufe = 0;
const wurzel = { updateWorldMatrix() { aufrufe++; }, traverse() {} };
const v = { y: 0 };
nah('tiefste', K.tiefste({ bodyMesh: netz }, wurzel, v), -0.2);
if (aufrufe !== 1) throw new Error('updateWorldMatrix ' + aufrufe + 'x');
// 3. ohne Netz: der tiefste Knochen
const zehe = { isBone: true, getWorldPosition(v) { v.y = 0.02; } };
const wurzel2 = { isBone: true, updateWorldMatrix() {},
    traverse(f) { f(this); f(zehe); }, getWorldPosition(v) { v.y = 0.8; } };
nah('knochen', K.tiefste({ bodyMesh: null }, wurzel2, { y: 0 }), 0.02);
if (K.messbar({ isSkinnedMesh: true, geometry: netz.geometry })) throw new Error('ohne skeleton messbar');
console.log(JSON.stringify({ ok: true }));
"""


class KoerpertiefeTest(SimpleTestCase):
    def test_tiefster_punkt_des_ganzen_netzes(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get("ok"))
