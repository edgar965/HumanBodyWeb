# -*- coding: utf-8 -*-
u"""`Figurvideostuecke`: das Binaerpaket eines Szenennetzes, Byte fuer Byte.

Das Paket hat keinen Kopf — der Server liest es allein nach den Zahlen im
Auftrag (`figurvideostuecke.py`). Stimmt die Reihenfolge der vier Bloecke
nicht oder fehlt die eigene Matrix des Netzes, kommt kein Fehler, sondern
ein Kleidungsstueck an der falschen Stelle. Hier mit Attrappen fuer
Geometrie und Material, in Node:

* Punkte durch `netz.matrix` (Verschiebung um 0,5 in x) — ein GarmentCode-
  Stueck bindet mit dieser Matrix.
* Dreiecke als Uint32, Knochennummern als Uint16 GERUNDET (die Szene haelt
  sie als Float32), Gewichte als Float32.
* Ein starres Netz und ein Netz am fremden Skelett kommen nicht mit,
  werden aber GENANNT.
* `formular` nennt je Stueck die Datei und legt die Knochenliste bei.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('scene', 'figurvideo_stuecke.js')

SKRIPT = """
const { Figurvideostuecke: F } = await import(MODUL);
const attribut = (werte, groesse) => ({
    count: werte.length / groesse, array: werte,
    getX: (i) => werte[groesse * i], getY: (i) => werte[groesse * i + 1], getZ: (i) => werte[groesse * i + 2],
    getComponent: (i, j) => werte[groesse * i + j],
});
const skelett = { name: 'eigenes' };
const netz = (punkte, dx, ok = true, sk = skelett) => ({
    isSkinnedMesh: ok, skeleton: sk, name: 'gc_hose', userData: { beschriftung: 'Hose (GarmentCode)' },
    material: { color: { getHexString: () => 'ff8000' } },
    matrix: { elements: [1,0,0,0, 0,1,0,0, 0,0,1,0, dx,0,0,1] }, updateMatrix() {},
    geometry: {
        index: { array: new Uint16Array([0, 1, 2]) },
        getAttribute: (name) => ({
            position: attribut(new Float32Array(punkte), 3),
            skinIndex: ok ? attribut(new Float32Array([3, 0, 0, 0, 1, 2, 0, 0, 2, 0, 0, 0]), 4) : null,
            skinWeight: ok ? attribut(new Float32Array([1, 0, 0, 0, 0.75, 0.25, 0, 0, 1, 0, 0, 0]), 4) : null,
        })[name],
    },
});
const inst = { bodyMesh: { skeleton: skelett }, clothMeshes: {
    gc_hose: netz([0.1, 1.2, -0.3, 0.2, 1.0, 0.0, -0.1, 0.9, 0.2], 0.5),
    tpl_starr: netz([0, 0, 0], 0, false),
    mh_fremd: netz([0, 0, 0, 0, 0, 0, 0, 0, 0], 0, true, { name: 'fremd' }),
} };
const { stuecke, starre } = F.sammeln(inst);
if (stuecke.length !== 1) throw new Error('Stuecke: ' + stuecke.length);
if (starre.join() !== 'tpl_starr,mh_fremd') throw new Error('starre: ' + starre);
const s = stuecke[0];
if (s.name !== 'Hose (GarmentCode)' || s.farbe !== '#ff8000' || s.punkte !== 3 || s.dreiecke !== 1) throw new Error(JSON.stringify(s));
const roh = new Uint8Array(await s.blob.arrayBuffer());
if (roh.length !== 3 * 12 + 1 * 12 + 3 * 8 + 3 * 16) throw new Error('Laenge ' + roh.length);
const punkte = new Float32Array(roh.buffer, 0, 9);
const nah = (a, b) => Math.abs(a - b) < 1e-6;
if (!(nah(punkte[0], 0.6) && nah(punkte[1], 1.2) && nah(punkte[2], -0.3) && nah(punkte[3], 0.7))) throw new Error('Punkte: ' + Array.from(punkte));
const dreiecke = new Uint32Array(roh.buffer, 36, 3);
if (dreiecke.join() !== '0,1,2') throw new Error('Dreiecke: ' + dreiecke);
const nummern = new Uint16Array(roh.buffer, 48, 12);
if (nummern.join() !== '3,0,0,0,1,2,0,0,2,0,0,0') throw new Error('Nummern: ' + nummern);
const gewichte = new Float32Array(roh.buffer, 72, 12);
if (!(gewichte[0] === 1 && gewichte[4] === 0.75 && gewichte[5] === 0.25)) throw new Error('Gewichte: ' + Array.from(gewichte));
const formular = F.formular({ sekunden: 3 }, stuecke, ['DEF-spine', 'DEF-thigh.L']);
const auftrag = JSON.parse(formular.get('auftrag'));
if (auftrag.sekunden !== 3 || auftrag.knochen.length !== 2 || auftrag.stuecke[0].datei !== 'stueck_0') throw new Error(formular.get('auftrag'));
if (!(formular.get('stueck_0') instanceof Blob)) throw new Error('Paket fehlt im Formular');
console.log(JSON.stringify({ ok: true, bytes: roh.length }));
"""


class FigurvideoStueckeJsTest(SimpleTestCase):

    databases = []

    def test_paket_byte_fuer_byte(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertEqual(ausgabe['bytes'], 120)
