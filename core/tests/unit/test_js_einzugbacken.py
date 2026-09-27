# -*- coding: utf-8 -*-
u"""Die verdeckte Haut darf nicht durch Schuh und Kleid stechen (26.09.2026).

Edgar mit Nahaufnahme der Füße: „viel besser im Meshlab, aber Schuhe noch
Fehler" — hautfarbene Flecken mitten auf den schwarzen Schuhen.

Die Szene zieht verdeckte Hautpunkte nach innen, damit kein Zipfel durch den
Stoff sticht. Das passiert im Vertex-Shader (`transformed += einzug`), nicht
in der Geometrie. Der Export wirft eigene Attribute hinaus — ohne Shader
standen die Punkte damit wieder auf der Oberfläche, und weil seit dem
Vollindex-Fix die GANZE verdeckte Haut mitkommt, lag sie vor dem Schuh.

Zwei Fallen, beide hier geprüft:
1. Der Einzug muss eingerechnet werden, BEVOR das Attribut gelöscht wird —
   und zwar in `Netzattribute.eigeneEntfernen`, weil beide Exportwege da
   vorbeikommen (beim vollen Index war genau das vergessen worden).
2. `Netzpose._skinnen` darf die Ausgangspunkte nicht wieder aus dem ORIGINAL
   holen, sonst ist der Einzug in jeder Pose außer der Ruhelage weg.
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
const { Einzugbacken } = await import('file:///%(viewer)s/gemeinsam/einzugbacken.js');
const { Netzattribute } = await import('file:///%(viewer)s/gemeinsam/netzattribute.js');
const { Netzpose } = await import('file:///%(viewer)s/gemeinsam/netzpose.js');

/** Drei Punkte; der mittlere ist „verdeckt" und wird 1 cm nach innen gezogen. */
function geometrie() {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array([
        0,0,0,  1,0,0,  2,0,0,
    ]), 3));
    geo.setAttribute('einzug', new THREE.BufferAttribute(new Float32Array([
        0,0,0,  0,-0.01,0,  0,0,0,
    ]), 3));
    geo.setAttribute('dicke', new THREE.BufferAttribute(new Float32Array([1, 1, 1]), 1));
    geo.setIndex([0, 1, 2]);
    return geo;
}

const ergebnis = {};

const a = geometrie();
ergebnis.bewegt = Einzugbacken.anwenden(a);
ergebnis.nachBacken = Array.from(a.getAttribute('position').array);

// Der Weg, den der Export wirklich nimmt.
const b = geometrie();
Netzattribute.eigeneEntfernen(b);
ergebnis.ueberNetzattribute = Array.from(b.getAttribute('position').array);
ergebnis.attributeDanach = Object.keys(b.attributes);

// Ohne Einzug passiert nichts.
const c = new THREE.BufferGeometry();
c.setAttribute('position', new THREE.BufferAttribute(new Float32Array([0,0,0, 1,0,0, 2,0,0]), 3));
ergebnis.ohneEinzug = Einzugbacken.anwenden(c);

// Und in der GEBACKENEN Kopie, wie der Export sie baut (Ruhelage).
const netz = new THREE.Mesh(geometrie(), new THREE.MeshStandardMaterial());
netz.name = 'fuss';
const kopie = Netzpose.gebacken(netz, Netzpose.RUHELAGE);
ergebnis.ueberNetzpose = Array.from(kopie.geometry.getAttribute('position').array);
ergebnis.originalUnberuehrt = Array.from(netz.geometry.getAttribute('position').array);

console.log(JSON.stringify(ergebnis));
"""


class EinzugbackenTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not shutil.which('node'):
            raise RuntimeError('node ist nicht im Pfad — die JS-Tests führen die Module wirklich aus.')
        ordner = Path(ProjektTemp.ordner('test_modellexport'))
        skript = ordner / 'einzug_probe.mjs'
        skript.write_text(SKRIPT % {'viewer': VIEWER}, encoding='utf-8')
        lauf = subprocess.run(
            ['node', skript.as_posix()], cwd=WURZEL, capture_output=True, text=True, timeout=120,
        )
        if lauf.returncode != 0:
            raise RuntimeError(f'node-Lauf gescheitert:\n{lauf.stdout}\n{lauf.stderr}')
        cls.ergebnis = json.loads(lauf.stdout.strip().splitlines()[-1])

    #: `Float32Array` speichert 0,01 als 0,009999999776… — die Punkte werden
    #: deshalb gerundet verglichen, nicht auf das letzte Bit.
    def gerundet(self, schluessel):
        return [round(w, 5) for w in self.ergebnis[schluessel]]

    def test_1_der_einzug_landet_in_den_punkten(self):
        self.assertEqual(self.ergebnis['bewegt'], 1, 'nur der verdeckte Punkt wandert')
        self.assertEqual(self.gerundet('nachBacken'), [0, 0, 0, 1, -0.01, 0, 2, 0, 0])

    def test_2_der_exportweg_rechnet_ihn_ein_bevor_er_loescht(self):
        u"""DER VORFALL: `Netzattribute.eigeneEntfernen` hat den Einzug
        einfach gelöscht — im fremden Programm stand die verdeckte Haut
        danach wieder auf der Oberfläche und stach durch den Schuh."""
        self.assertEqual(self.gerundet('ueberNetzattribute'), [0, 0, 0, 1, -0.01, 0, 2, 0, 0],
                         'der Einzug wurde gelöscht statt eingerechnet')
        self.assertEqual(self.ergebnis['attributeDanach'], ['position'],
                         'die eigenen Attribute müssen trotzdem verschwinden')

    def test_3_ohne_einzug_passiert_nichts(self):
        self.assertEqual(self.ergebnis['ohneEinzug'], 0)

    def test_4_die_gebackene_kopie_traegt_ihn_und_das_original_nicht(self):
        u"""Ein Export darf die Szene nicht verändern."""
        self.assertEqual(self.gerundet('ueberNetzpose'), [0, 0, 0, 1, -0.01, 0, 2, 0, 0])
        self.assertEqual(self.gerundet('originalUnberuehrt'), [0, 0, 0, 1, 0, 0, 2, 0, 0])
