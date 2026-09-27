# -*- coding: utf-8 -*-
u"""Die ganze Haut muss in den Export — auch mit Rig (26.09.2026).

Edgar mit Nahaufnahme: „an den Wangen gibt es auch Fehler in den 3D Mesh."

Die Szene nimmt Hautdreiecke unter Kleid und Haaren aus dem Index und hebt
den vollen Index in `geometry.userData.indexVoll` auf (`figurhaut.js`). Im
Viewer sieht das niemand; in einem fremden Programm klaffen dort Löcher, und
man sieht durch sie auf Innenflächen. Bei Damira1: 12.164 von 804.992
Körperdreiecken.

`Netzpose.gebacken` setzt den vollen Index seit dem ersten Fix — der Weg mit
RIG (GLB mit Skelett) geht aber gar nicht durch `Netzpose`: dort wandern die
LEBENDEN Netze zum Exporter, mit dem gekürzten Index der Szene. Deshalb liegt
die Rechnung jetzt in `Vollindex` und wird an beiden Stellen gerufen.

Zwei Dinge sind dabei leicht zu übersehen, beide werden hier geprüft:
- die MATERIALZONEN müssen mitwandern (`groups` sind Abschnitte IM Index);
- die Szene muss hinterher wieder ihren gekürzten Index haben, sonst zeichnet
  der Browser ab dem ersten Export die verdeckte Haut mit.
"""
import json
import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from core.projekt_temp import ProjektTemp

WURZEL = Path(settings.BASE_DIR)
VIEWER = (WURZEL / 'static' / 'viewer').as_posix()

SKRIPT = """
import * as THREE from 'three';
const { Vollindex } = await import('file:///%(viewer)s/gemeinsam/vollindex.js');

/** Netz mit 4 Dreiecken in zwei Zonen; die Szene hat 2 davon entfernt. */
function netz() {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(36), 3));
    geo.userData.indexVoll = {
        index: new Uint32Array([0,1,2, 3,4,5, 6,7,8, 9,10,11]),
        gruppen: [{ start: 0, count: 6, materialIndex: 0 },
                  { start: 6, count: 6, materialIndex: 1 }],
    };
    // Was die Szene zeichnet: Dreieck 1 und 3 fehlen, Zonen entsprechend kurz.
    geo.setIndex([0,1,2, 6,7,8]);
    geo.clearGroups();
    geo.addGroup(0, 3, 0);
    geo.addGroup(3, 3, 1);
    return new THREE.Mesh(geo, [new THREE.MeshStandardMaterial(), new THREE.MeshStandardMaterial()]);
}

const ergebnis = {};

const a = netz();
ergebnis.vorher = { index: a.geometry.index.count, gruppen: a.geometry.groups.map(g => [g.start, g.count]) };
ergebnis.noetig = Vollindex.noetig(a.geometry);
Vollindex.setzen(a.geometry);
ergebnis.nachSetzen = { index: a.geometry.index.count,
                        gruppen: a.geometry.groups.map(g => [g.start, g.count, g.materialIndex]) };

// Der lebende Pfad: tauschen und zurückstellen.
const b = netz();
const alteGeometrie = b.geometry;
const zurueck = Vollindex.tauschen([b]);
ergebnis.getauscht = b.geometry.index.count;
ergebnis.szeneUnberuehrt = alteGeometrie.index.count;   // die Szene-Geometrie bleibt kurz
zurueck();
ergebnis.nachRueckgabe = b.geometry.index.count;
ergebnis.selbeGeometrie = b.geometry === alteGeometrie;

// Ohne gemerkten vollen Index passiert nichts — und `tauschen` gibt null.
const c = new THREE.Mesh(new THREE.BufferGeometry());
c.geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(9), 3));
c.geometry.setIndex([0, 1, 2]);
ergebnis.ohneVoll = Vollindex.tauschen([c]);
ergebnis.ohneVollNoetig = Vollindex.noetig(c.geometry);

console.log(JSON.stringify(ergebnis));
"""


class VollindexTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not shutil.which('node'):
            raise RuntimeError('node ist nicht im Pfad — die JS-Tests führen die Module wirklich aus.')
        ordner = Path(ProjektTemp.ordner('test_modellexport'))
        skript = ordner / 'vollindex_probe.mjs'
        skript.write_text(SKRIPT % {'viewer': VIEWER}, encoding='utf-8')
        lauf = subprocess.run(
            ['node', skript.as_posix()], cwd=WURZEL, capture_output=True, text=True, timeout=120,
        )
        if lauf.returncode != 0:
            raise RuntimeError(f'node-Lauf gescheitert:\n{lauf.stdout}\n{lauf.stderr}')
        cls.ergebnis = json.loads(lauf.stdout.strip().splitlines()[-1])

    def test_1_der_gekuerzte_index_wird_erkannt(self):
        self.assertEqual(self.ergebnis['vorher']['index'], 6, 'die Szene zeichnet nur zwei Dreiecke')
        self.assertTrue(self.ergebnis['noetig'])
        self.assertIsNone(self.ergebnis['ohneVoll'], 'ohne gemerkten Index gibt es nichts zu tauschen')
        self.assertFalse(self.ergebnis['ohneVollNoetig'])

    def test_2_voller_index_mit_seinen_materialzonen(self):
        u"""`groups` sind Abschnitte IM Index — bleiben sie stehen, schneidet
        `Gruppennetze` die Zonen danach an falschen Stellen heraus."""
        nach = self.ergebnis['nachSetzen']
        self.assertEqual(nach['index'], 12, 'alle vier Dreiecke')
        self.assertEqual(nach['gruppen'], [[0, 6, 0], [6, 6, 1]],
                         'die Zonen müssen auf den vollen Index umgerechnet sein')

    def test_3_die_szene_behaelt_ihren_kurzen_index(self):
        u"""Sonst zeichnete der Browser ab dem ersten Export die verdeckte
        Haut mit — ein Export darf die Szene nicht verändern."""
        self.assertEqual(self.ergebnis['getauscht'], 12, 'der Export bekommt den vollen Index')
        self.assertEqual(self.ergebnis['szeneUnberuehrt'], 6,
                         'die Geometrie der Szene wurde angefasst statt geklont')
        self.assertEqual(self.ergebnis['nachRueckgabe'], 6)
        self.assertTrue(self.ergebnis['selbeGeometrie'],
                        'nach der Rückgabe muss wieder DIESELBE Geometrie hängen')
