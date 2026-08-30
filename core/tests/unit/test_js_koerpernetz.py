# -*- coding: utf-8 -*-
u"""`Koerpernetz.materialsatz`: Materialliste oder Hautmaterial allein.

WARUM (28.08.2026, Befund `doppelcode`)
=======================================
Materialliste bauen und Materialgruppen setzen gehören zusammen und standen
trotzdem dreimal getrennt da — in `Koerpernetz.bauen`, in
`bvh_studio/spurfigur.js` und in `photo_to_3d/fotokoerpernetz.js`.

DIE STELLE, DIE WEHTUT
======================
Der Rückgabewert. Three.js kann mit einem Material-ARRAY nur etwas anfangen,
wenn die Geometrie Gruppen hat; ohne sie rendert es das Netz SCHWARZ. Deshalb
muss ohne Gruppen das Hautmaterial ALLEIN zurückgehen.

`spurfigur.js` hat diese Verzweigung nur an der Gruppenzahl festgemacht, nicht
am Index — ein Netz ohne Index bekam dort eine Materialliste, die keine Gruppe
adressiert. Das ist genau der schwarze Fall.

FEHLT `node`, ist das ein FEHLER — node ist Werkzeug dieses Projekts,
kein Zufall der Umgebung (siehe `Jsmodul.laufen`).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'koerpernetz.js')

SKRIPT = """
const { Koerpernetz } = await import(MODUL);

class BufferAttribute {
    constructor(array, itemSize) { this.array = array; this.itemSize = itemSize; }
}
class MeshStandardMaterial {
    constructor(angaben) { Object.assign(this, angaben); }
}
class BufferGeometry {
    constructor(mitIndex) {
        this.attribute = {}; this.index = mitIndex ? {} : null; this.groups = [];
    }
    setAttribute(name, wert) { this.attribute[name] = wert; }
    setIndex(wert) { this.index = wert; }
    getIndex() { return this.index; }
    addGroup(start, count, materialIndex) {
        this.groups.push({start, count, materialIndex});
    }
    computeVertexNormals() {}
}
const THREE = {BufferGeometry, BufferAttribute, MeshStandardMaterial,
               DoubleSide: 'doppelseitig'};

const daten = {groups: [{start: 0, count: 9, materialIndex: 0},
                        {start: 9, count: 3, materialIndex: 4}]};

// 1. MIT Index und MIT Gruppen -> die ganze Liste
const mit = new BufferGeometry(true);
const satzMit = Koerpernetz.materialsatz(mit, daten, THREE);

// 2. OHNE Index -> Hautmaterial allein, und KEINE Gruppen gesetzt
const ohneIndex = new BufferGeometry(false);
const satzOhneIndex = Koerpernetz.materialsatz(ohneIndex, daten, THREE);

// 3. MIT Index, aber ohne Gruppen in den Daten -> ebenfalls allein
const ohneGruppen = new BufferGeometry(true);
const satzOhneGruppen = Koerpernetz.materialsatz(ohneGruppen, {}, THREE);

// 4. Der Nachbereiten-Haken (die Spuren faerben dort ihre Hautfarbe ein)
const gefaerbt = new BufferGeometry(true);
Koerpernetz.materialsatz(gefaerbt, daten, THREE,
                         (liste) => { liste[0].color = 0x123456; });
const satzGefaerbt = Koerpernetz.materialsatz(
    new BufferGeometry(true), daten, THREE,
    (liste) => { liste[0].color = 0x123456; });

console.log(JSON.stringify({
    mitIstListe: Array.isArray(satzMit),
    mitAnzahl: Array.isArray(satzMit) ? satzMit.length : null,
    mitGruppen: mit.groups,
    hautfarbe: Array.isArray(satzMit) ? satzMit[0].color : null,
    seite: Array.isArray(satzMit) ? satzMit[0].side : null,
    hornhaut: Array.isArray(satzMit)
        ? {transparent: satzMit[5].transparent, opacity: satzMit[5].opacity}
        : null,
    ersteUndurchsichtig: Array.isArray(satzMit)
        ? {transparent: satzMit[0].transparent, opacity: satzMit[0].opacity}
        : null,
    ohneIndexIstListe: Array.isArray(satzOhneIndex),
    ohneIndexGruppen: ohneIndex.groups.length,
    ohneGruppenIstListe: Array.isArray(satzOhneGruppen),
    gefaerbt: Array.isArray(satzGefaerbt) ? satzGefaerbt[0].color : null,
}));
"""


class MaterialsatzTest(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.e = MODUL.laufen(SKRIPT)

    def test_mit_index_und_gruppen_kommt_die_liste(self):
        self.assertTrue(self.e['mitIstListe'])
        self.assertEqual(self.e['mitAnzahl'], 11)

    def test_die_gruppen_landen_an_der_geometrie(self):
        self.assertEqual(self.e['mitGruppen'],
                         [{'start': 0, 'count': 9, 'materialIndex': 0},
                          {'start': 9, 'count': 3, 'materialIndex': 4}])

    def test_ohne_index_kommt_das_hautmaterial_allein(self):
        u"""Der schwarze Fall: Three.js kann mit einem Array nichts anfangen,
        wenn die Geometrie keine Gruppen hat."""
        self.assertFalse(self.e['ohneIndexIstListe'])
        self.assertEqual(self.e['ohneIndexGruppen'], 0)

    def test_ohne_gruppen_in_den_daten_ebenso(self):
        self.assertFalse(self.e['ohneGruppenIstListe'])

    def test_die_werte_kommen_aus_der_materialtabelle(self):
        u"""Index 0 ist Haut, Index 5 die Hornhaut — die einzige durchsichtige.
        Wer die Tabelle umsortiert, trägt das Auge im Nagel-Material."""
        self.assertEqual(self.e['hautfarbe'], 0xd4a574)
        self.assertEqual(self.e['seite'], 'doppelseitig')
        self.assertEqual(self.e['hornhaut'],
                         {'transparent': True, 'opacity': 0.3})
        self.assertEqual(self.e['ersteUndurchsichtig'],
                         {'transparent': False, 'opacity': 1.0})

    def test_der_haken_greift_vor_der_rueckgabe(self):
        u"""Die Spuren im BVH-Studio färben dort ihre Hautfarbe ein."""
        self.assertEqual(self.e['gefaerbt'], 0x123456)
