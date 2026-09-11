# -*- coding: utf-8 -*-
u"""`Kamerafolge`: die Kamera faehrt der Figur in der Bodenebene nach.

Drei Dinge, die stimmen muessen — mit Attrappen fuer Kamera, Steuerung und
Knochen, ohne Three.js:

* Kamera UND Blickpunkt wandern um den Weg der Figur, gleich weit — sonst
  dreht sich der Blick, statt mitzufahren.
* Nur x und z: Das Becken hebt sich bei jedem Schritt; die Kamera nicht.
* `beenden()` stellt die Ausgangslage her, auch nach mehreren Bildern.

Sabotage-Gegenprobe: `versatz` mit `jetzt[1] - start[1]` in der Mitte
macht den zweiten Block rot; ein vergessenes `ziel` im dritten Block den
letzten.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('scene', 'kamerafolge.js')

SKRIPT = """
const { Kamerafolge } = await import(MODUL);
const vek = (x, y, z) => ({ x, y, z, set(a, b, c) { this.x = a; this.y = b; this.z = c; } });
const knochen = (name, x, y, z) => ({ name, matrixWorld: { elements: [1,0,0,0, 0,1,0,0, 0,0,1,0, x, y, z, 1] },
                                      updateWorldMatrix() { this.aktualisiert = (this.aktualisiert || 0) + 1; } });
const becken = knochen('DEF-spine', 0.2, 0.95, 0.1);
const inst = { bodyMesh: { skeleton: { bones: [knochen('DEF-spine_001', 9, 9, 9), becken] } } };
const camera = { position: vek(1.0, 1.5, 3.0), updateMatrixWorld() {} };
const controls = { target: vek(0.2, 1.0, 0.1), update() { this.aktualisiert = (this.aktualisiert || 0) + 1; } };

// 1. Bezug ist das Becken, nicht der erste Knochen der Liste.
if (Kamerafolge.bezugsknochen(inst) !== becken) throw new Error('Bezugsknochen ist nicht DEF-spine');

// 2. Die Figur geht 1,5 m in x, hebt sich 3 cm, 0,4 m in z.
const folge = new Kamerafolge(inst, camera, controls).starten();
becken.matrixWorld.elements[12] = 1.7; becken.matrixWorld.elements[13] = 0.98; becken.matrixWorld.elements[14] = 0.5;
const v = folge.nachfuehren();
const nah = (a, b) => Math.abs(a - b) < 1e-12;
if (!(nah(v[0], 1.5) && v[1] === 0 && nah(v[2], 0.4))) throw new Error('Versatz: ' + v);
if (!(nah(camera.position.x, 2.5) && nah(camera.position.y, 1.5) && nah(camera.position.z, 3.4))) {
    throw new Error('Kamera: ' + JSON.stringify(camera.position));
}
if (!(nah(controls.target.x, 1.7) && nah(controls.target.y, 1.0) && nah(controls.target.z, 0.5))) {
    throw new Error('Blickpunkt: ' + JSON.stringify(controls.target));
}
if (!becken.aktualisiert) throw new Error('Knochenlage nicht frisch gerechnet');

// 3. Ein zweites Bild weiter, dann zurueck auf Anfang.
becken.matrixWorld.elements[12] = 3.0;
folge.nachfuehren();
if (!nah(camera.position.x, 3.8)) throw new Error('zweites Bild: ' + camera.position.x);
folge.beenden();
if (!(nah(camera.position.x, 1.0) && nah(camera.position.z, 3.0) && nah(controls.target.x, 0.2) && nah(controls.target.z, 0.1))) {
    throw new Error('nicht zurueckgestellt: ' + JSON.stringify([camera.position, controls.target]));
}
if (!controls.aktualisiert) throw new Error('Steuerung nach dem Ende nicht aktualisiert');
if (folge.nachfuehren() !== null) throw new Error('nach beenden() darf nichts mehr folgen');
console.log(JSON.stringify({ ok: true }));
"""


class KamerafolgeJsTest(SimpleTestCase):

    databases = []

    def test_kamera_faehrt_in_der_bodenebene_mit(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
