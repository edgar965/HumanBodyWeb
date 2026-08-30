# -*- coding: utf-8 -*-
u"""`Hautbindung` gegen die drei alten Fassungen — Schritt für Schritt.

WARUM (28.08.2026, Befund `doppelcode`)
=======================================
Neun Zeilen standen dreimal: `scene/skeleton.js`, `viewer/skinning.js` und
`result_character/mesh_loading.js`. Sie ersetzen das Körpernetz durch ein
`SkinnedMesh` und müssen dabei alles mitnehmen, was am alten Netz hing.

WAS DABEI SCHIEFGEHT, OHNE ETWAS ZU WERFEN
==========================================
* Ohne `bind()` rendert das SkinnedMesh in der Ruhelage und bewegt sich nie —
  es sieht aus wie ein Modell, das die Animation nicht kennt.
* Ohne `rootBone` als Kind bleiben die Knochenmatrizen auf Identität. Dasselbe
  Bild, anderer Grund.
* Ohne `position` steht die Figur im Ursprung statt an ihrem Platz.

DIE STELLE, DIE SCHON AUSEINANDERGELAUFEN WAR: `mesh_loading.js` hat
`visible` als einzige NICHT mitgenommen. Wer den Körper ausgeblendet hatte und
dann das Skelett zuschaltete, bekam ihn zurück — ohne dass der Schalter
umsprang. Der Test nagelt das neue, vollständige Verhalten fest.

FEHLT `node`, ist das ein FEHLER — node ist Werkzeug dieses Projekts,
kein Zufall der Umgebung (siehe `Jsmodul.laufen`).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'hautbindung.js')

SKRIPT = """
const { Hautbindung } = await import(MODUL);

class Objekt {
    constructor(name) {
        this.name = name; this.kinder = []; this.visible = true;
        this.position = {x: 0, y: 0, z: 0,
                         clone: () => ({...this.position, kopie: true}),
                         copy: (o) => { this.position.x = o.x;
                                        this.position.y = o.y;
                                        this.position.z = o.z; }};
    }
    add(kind) { this.kinder.push(kind); }
}
class SkinnedMesh extends Objekt {
    constructor(geometrie, material) {
        super('skinned');
        this.geometry = geometrie; this.material = material;
        this.gebundenAn = null;
    }
    bind(skelett) { this.gebundenAn = skelett; }
}
const THREE = { SkinnedMesh };

const szene = { drin: [], add(o) { this.drin.push(o); },
                remove(o) { this.drin = this.drin.filter(x => x !== o); } };

const alt = new Objekt('koerper');
alt.material = {name: 'haut'};
alt.position.x = 1.5; alt.position.y = -2; alt.position.z = 0.25;
alt.visible = false;                       // AUSGEBLENDET
szene.add(alt);

const geometrie = {name: 'mit skinIndex'};
const skelett = {rootBone: {name: 'wurzelknochen'}, skeleton: {name: 'skelett'}};

const neu = Hautbindung.ersetzen(szene, alt, geometrie, skelett, THREE);

console.log(JSON.stringify({
    istSkinned: neu instanceof SkinnedMesh,
    material: neu.material.name,
    geometrie: neu.geometry.name,
    ort: [neu.position.x, neu.position.y, neu.position.z],
    sichtbar: neu.visible,
    kinder: neu.kinder.map(k => k.name),
    gebundenAn: neu.gebundenAn?.name ?? null,
    inSzene: szene.drin.map(o => o.name),
}));
"""


class HautbindungTest(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.e = MODUL.laufen(SKRIPT)

    def test_es_entsteht_ein_skinnedmesh(self):
        self.assertTrue(self.e['istSkinned'])
        self.assertEqual(self.e['geometrie'], 'mit skinIndex')

    def test_material_wird_uebernommen(self):
        u"""Sonst steht die Figur in Three.js-Grau da."""
        self.assertEqual(self.e['material'], 'haut')

    def test_ort_wird_uebernommen(self):
        u"""Ohne das steht die Figur im Ursprung statt an ihrem Platz."""
        self.assertEqual(self.e['ort'], [1.5, -2, 0.25])

    def test_sichtbarkeit_wird_uebernommen(self):
        u"""DIE Stelle, die vorher auseinanderlief: `mesh_loading.js` hat sie
        als einzige nicht mitgenommen — ein ausgeblendeter Körper kam beim
        Zuschalten des Skeletts zurück, ohne dass der Schalter umsprang."""
        self.assertIs(self.e['sichtbar'], False)

    def test_wurzelknochen_haengt_am_netz(self):
        u"""Ohne ihn bleiben die Knochenmatrizen auf Identität — die Figur
        steht still, und nichts wirft."""
        self.assertEqual(self.e['kinder'], ['wurzelknochen'])

    def test_es_wird_gebunden(self):
        u"""Ohne `bind()` rendert das Netz ewig in der Ruhelage."""
        self.assertEqual(self.e['gebundenAn'], 'skelett')

    def test_das_alte_netz_ist_aus_der_szene_raus(self):
        u"""Sonst stehen zwei Körper übereinander — einer davon unbewegt."""
        self.assertEqual(self.e['inSzene'], ['skinned'])
