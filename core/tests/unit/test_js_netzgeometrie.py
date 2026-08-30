# -*- coding: utf-8 -*-
u"""`Netzgeometrie` gegen die alten, handgebauten Fassungen — Wert für Wert.

WARUM (28.08.2026, Befund `doppelcode`)
=======================================
Neun Stellen bauten dieselbe BufferGeometry aus einer Serverantwort selbst
nach. Sieben davon gehen jetzt durch `Netzgeometrie.bauen` — und dieser Test
rechnet die neue Fassung gegen die ALTEN Zeilen, so wie sie in `viewer/
cloth.js` und `viewer/garment.js` standen.

WAS DABEI SCHIEFGEHEN KANN, OHNE AUFZUFALLEN
============================================
Eine Geometrie mit falsch gedrehten NORMALEN sieht nicht kaputt aus — das
Kleidungsstück ist nur anders beleuchtet, und zwar nur auf der einen Seite.
Genau dieser Fehler ist im Projekt schon einmal passiert (siehe den Kopf von
`netzgeometrie.js`). Deshalb wird hier Zahl für Zahl verglichen.

DIE ZWEI FÄLLE, DIE SICH UNTERSCHEIDEN
======================================
* **Mit Normalen vom Server** (`cloth.js`): Sie kommen in Blender-Achsen und
  brauchen dieselbe Drehung wie die Punkte.
* **Ohne** (`garment.js`): Dann rechnet Three.js sie — und das darf die neue
  Fassung nicht stillschweigend anders machen.

FEHLT `node`, ist das ein FEHLER — node ist Werkzeug dieses Projekts,
kein Zufall der Umgebung (siehe `Jsmodul.laufen`).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'netzgeometrie.js')

SKRIPT = """
const { Netzgeometrie } = await import(MODUL);
const { base64ToFloat32, base64ToUint32, blenderToThreeCoords }
    = await import(MODUL.replace('netzgeometrie.js', 'kodierung.js'));

// --- Three.js, so weit es hier gebraucht wird ------------------------------
class BufferAttribute {
    constructor(array, itemSize) { this.array = array; this.itemSize = itemSize; }
}
class BufferGeometry {
    constructor() { this.attribute = {}; this.index = null; this.gerechnet = false; }
    setAttribute(name, wert) { this.attribute[name] = wert; }
    setIndex(wert) { this.index = wert; }
    computeVertexNormals() { this.gerechnet = true; }
}
const THREE = { BufferGeometry, BufferAttribute };

// --- Testdaten: base64 wie vom Server --------------------------------------
function alsBase64(typed) {
    const bytes = new Uint8Array(typed.buffer, typed.byteOffset, typed.byteLength);
    let bin = '';
    for (const b of bytes) bin += String.fromCharCode(b);
    return btoa(bin);
}
const punkte = new Float32Array([0, 1, 2,  3, 4, 5,  6, 7, 8,  -1, -2, -3]);
const flaechen = new Uint32Array([0, 1, 2,  1, 2, 3]);
const normalen = new Float32Array([0, 0, 1,  0, 1, 0,  1, 0, 0,  0, -1, 0]);
const uvs = new Float32Array([0, 0,  1, 0,  1, 1,  0, 1]);
const daten = {vertices: alsBase64(punkte), faces: alsBase64(flaechen),
               normals: alsBase64(normalen), uvs: alsBase64(uvs)};

// --- die ALTE Fassung, unveraendert aus viewer/cloth.js --------------------
function altMitNormalen(data) {
    const vertBuf = base64ToFloat32(data.vertices);
    blenderToThreeCoords(vertBuf);
    const faceBuf = base64ToUint32(data.faces);
    const normalBuf = base64ToFloat32(data.normals);
    blenderToThreeCoords(normalBuf);
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
    geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
    geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
    return geo;
}

// --- und aus viewer/garment.js (rechnet die Normalen selbst) ---------------
function altOhneNormalen(data) {
    const vertBuf = base64ToFloat32(data.vertices);
    blenderToThreeCoords(vertBuf);
    const faceBuf = base64ToUint32(data.faces);
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
    geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
    geo.computeVertexNormals();
    return geo;
}

const alt1 = altMitNormalen(daten);
const neu1 = Netzgeometrie.bauen(daten, THREE);
const alt2 = altOhneNormalen({...daten, normals: null});
const neu2 = Netzgeometrie.bauen({...daten, normals: null}, THREE);

// Der Haken am Punktpuffer (mhproxynetz merkt sich den Puffer).
let gemerkt = null;
const neu3 = Netzgeometrie.bauen(daten, THREE, (p) => { gemerkt = Array.from(p); });

// --- SMPL: dieselbe Rechnung OHNE Drehung ---------------------------------
function altOhneDrehung(data) {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(
        base64ToFloat32(data.vertices), 3));
    geo.setIndex(new THREE.BufferAttribute(base64ToUint32(data.faces), 1));
    geo.setAttribute('normal', new THREE.BufferAttribute(
        base64ToFloat32(data.normals), 3));
    return geo;
}
const alt4 = altOhneDrehung(daten);
const neu4 = Netzgeometrie.bauen(daten, THREE, null, false);

// --- und aus fertigen Puffern (smpl_koerper) ------------------------------
const fertigePunkte = new Float32Array([9, 8, 7,  6, 5, 4]);
const fertigeNormalen = new Float32Array([1, 0, 0,  0, 1, 0]);
const neu5 = Netzgeometrie.ausPuffern(fertigePunkte, fertigeNormalen,
                                      daten.faces, THREE);
const neu6 = Netzgeometrie.ausPuffern(fertigePunkte, null, null, THREE);

const feld = (g, n) => g.attribute[n] ? Array.from(g.attribute[n].array) : null;
console.log(JSON.stringify({
    altPosition: feld(alt1, 'position'), neuPosition: feld(neu1, 'position'),
    altNormal: feld(alt1, 'normal'),     neuNormal: feld(neu1, 'normal'),
    altIndex: Array.from(alt1.index.array), neuIndex: Array.from(neu1.index.array),
    altGerechnet: alt2.gerechnet, neuGerechnet: neu2.gerechnet,
    altNormal2: feld(alt2, 'normal'),   neuNormal2: feld(neu2, 'normal'),
    neuUv: feld(neu1, 'uv'),
    ohneUv: feld(Netzgeometrie.bauen({vertices: daten.vertices}, THREE), 'uv'),
    ohneIndex: Netzgeometrie.bauen({vertices: daten.vertices}, THREE).index,
    gemerkt, neu3Position: feld(neu3, 'position'),
    altUngedreht: feld(alt4, 'position'), neuUngedreht: feld(neu4, 'position'),
    altUngedrehtN: feld(alt4, 'normal'), neuUngedrehtN: feld(neu4, 'normal'),
    puffPosition: feld(neu5, 'position'), puffNormal: feld(neu5, 'normal'),
    puffIndex: Array.from(neu5.index.array),
    puffOhneIndex: neu6.index, puffGerechnet: neu6.gerechnet,
}));
"""


class NetzgeometrieTest(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.e = MODUL.laufen(SKRIPT)

    def test_punkte_wie_die_alte_fassung(self):
        self.assertEqual(self.e['neuPosition'], self.e['altPosition'])

    def test_normalen_wie_die_alte_fassung(self):
        u"""Die Drehung der Normalen ist die Zeile, die man in einer Kopie
        vergisst — dann leuchtet das Kleidungsstück auf einer Seite anders."""
        self.assertEqual(self.e['neuNormal'], self.e['altNormal'])

    def test_normalen_sind_wirklich_gedreht(self):
        u"""Gegenprobe zur Gleichheit: Wären BEIDE Fassungen falsch, wäre der
        Test oben trotzdem grün. Blender (x, y, z) → Three (x, z, −y)."""
        self.assertEqual(self.e['neuNormal'][:6], [0, 1, -0,  0, 0, -1])

    def test_index_wie_die_alte_fassung(self):
        self.assertEqual(self.e['neuIndex'], self.e['altIndex'])

    def test_ohne_server_normalen_wird_gerechnet(self):
        self.assertTrue(self.e['altGerechnet'])
        self.assertTrue(self.e['neuGerechnet'])
        self.assertIsNone(self.e['neuNormal2'])
        self.assertIsNone(self.e['altNormal2'])

    def test_uvs_kommen_mit_wenn_sie_da_sind(self):
        self.assertEqual(self.e['neuUv'], [0, 0, 1, 0, 1, 1, 0, 1])

    def test_ohne_uvs_und_ohne_flaechen_passiert_nichts(self):
        u"""Ein Kleidungsstück bringt keine `uvs` mit — das darf kein leeres
        Attribut und keinen leeren Index erzeugen."""
        self.assertIsNone(self.e['ohneUv'])
        self.assertIsNone(self.e['ohneIndex'])

    def test_ohne_drehung_wie_die_alte_smpl_fassung(self):
        u"""SMPL liefert bereits Three-Achsen. Wer sie ein zweites Mal dreht,
        legt das Netz um 90 Grad gekippt daneben — deshalb waren die drei
        SMPL-Stellen bis zum 28.08.2026 handgebaut."""
        self.assertEqual(self.e['neuUngedreht'], self.e['altUngedreht'])
        self.assertEqual(self.e['neuUngedrehtN'], self.e['altUngedrehtN'])

    def test_ohne_drehung_ist_wirklich_ungedreht(self):
        u"""Gegenprobe: Der Schalter muss auch etwas BEWIRKEN — sonst wäre der
        Vergleich oben grün, weil beide Fassungen drehen."""
        self.assertNotEqual(self.e['neuUngedreht'], self.e['neuPosition'])
        self.assertEqual(self.e['neuUngedreht'][:3], [0, 1, 2])

    def test_aus_fertigen_puffern(self):
        u"""`smpl_koerper` holt Punkte und Normalen an anderer Stelle und
        frischt sie später im selben Puffer auf."""
        self.assertEqual(self.e['puffPosition'], [9, 8, 7, 6, 5, 4])
        self.assertEqual(self.e['puffNormal'], [1, 0, 0, 0, 1, 0])
        self.assertEqual(self.e['puffIndex'], self.e['altIndex'])

    def test_aus_puffern_ohne_normalen_und_ohne_flaechen(self):
        self.assertIsNone(self.e['puffOhneIndex'])
        self.assertTrue(self.e['puffGerechnet'])

    def test_haken_bekommt_den_gedrehten_puffer(self):
        u"""`mhproxynetz` merkt sich den Puffer für die Anpassung an die
        Figur. Er muss DERSELBE sein, den die Geometrie bekommt — sonst rechnet
        die Anpassung auf ungedrehten Punkten."""
        self.assertEqual(self.e['gemerkt'], self.e['neu3Position'])
