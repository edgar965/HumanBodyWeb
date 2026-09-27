# -*- coding: utf-8 -*-
u"""OBJ-Export: die Exportdatei muss die Szene wiedergeben (26.09.2026).

Edgar: „kannst du dir nicht einen Testcase schreiben für obj export […]? Das
Ergebnis soll so ausschauen wie das Originalmodell."

Geprüft wird an einer Kunstfigur (neun Dreiecke, kein Genesis 9) genau das,
was an einem Tag VIER MAL still danebenging — jeder Fall hat einen echten
Vorfall hinter sich:

1. `OBJExporter` liest `mesh.material.name` OHNE Index (`OBJExporter.js:46-49`).
   Ein Material-ARRAY hat kein `.name`, also schrieb er für solche Netze GAR
   KEIN `usemtl`, und die Flächen liefen unter dem Material des vorigen Netzes
   weiter: Damiras Haar erbte das Schuhmaterial, die sieben Hautzonen verloren
   ihre Zuordnung (weiße Arme und Wangen). Gegenmittel: `Gruppennetze`.
2. Haarkarten, Wimpern und Brauen tragen ihre Form in einer `alphaMap`, nicht
   in der Geometrie. Ohne `map_d` wird aus jeder Strähnenkarte ein volles,
   undurchsichtiges Rechteck. Wimpern haben ÜBERHAUPT nur diese Maske.
3. Stranghaar besteht aus lauter entarteten Dreiecken `[a, b, b]`, die im
   Wireframe die Strähne zeichnen. Sie wegzufiltern löscht das Haar; sie roh
   zu exportieren lässt MeshLab „Identical vertex indices" melden. Richtig:
   Bänder mit Breite (`Strangbaender`).
4. Beim Zerlegen dürfen nur die BENUTZTEN Punkte je Zone mitkommen — sonst
   schreibt `OBJExporter` alle Punkte je Zone erneut und der Text sprengt
   V8s String-Grenze.
5. Vor jeder Iris sitzt eine kartenlose, fast durchsichtige Hornhaut. OBJ
   kennt keine Durchsichtigkeit; MeshLab macht daraus eine weiße Kugel über
   dem Auge. Sie gehört nicht in die Datei (`Klarflaechen`).

Sabotage (so wird der Fall rot): in `modellexport.js` den Aufruf
`Gruppennetze.zerlegen(rohe)` durch `rohe` ersetzen -> Fall 1; in `objmtl.js`
den `map_d`-Block streichen -> Fall 2; in `netzpose.js` `Strangbaender.bauen`
weglassen -> Fall 3.
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

#: Ohne Browser gibt es kein Canvas — `Werkstoffbild.png` braucht nur
#: `drawImage` und `toBlob`, der Inhalt des PNG ist hier nicht die Frage.
SKRIPT = """
globalThis.document = {
    createElement: () => ({
        width: 0, height: 0,
        getContext: () => ({ drawImage: () => {} }),
        toBlob: (rueck) => rueck(new Blob([new Uint8Array([137, 80, 78, 71])], { type: 'image/png' })),
    }),
};

import * as THREE from 'three';
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter.js';
const { Netzpose } = await import('file:///%(viewer)s/gemeinsam/netzpose.js');
const { Gruppennetze } = await import('file:///%(viewer)s/gemeinsam/gruppennetze.js');
const { Klarflaechen } = await import('file:///%(viewer)s/gemeinsam/klarflaechen.js');
const { ObjMtl } = await import('file:///%(viewer)s/gemeinsam/objmtl.js');

const bild = { width: 4, height: 4 };
const karte = (name) => { const t = new THREE.Texture(); t.image = bild; t.name = name; return t; };

/** `anzahl` Dreiecke, jedes für sich (kein geteilter Punkt). */
function flaechen(anzahl) {
    const geo = new THREE.BufferGeometry();
    const lage = new Float32Array(anzahl * 9);
    for (let i = 0; i < anzahl * 9; i++) lage[i] = (i %% 7) * 0.1;
    geo.setAttribute('position', new THREE.BufferAttribute(lage, 3));
    geo.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(anzahl * 6), 2));
    geo.setIndex([...Array(anzahl * 3).keys()]);
    return geo;
}

// 1. Körper: EIN Netz, zwei Materialzonen (wie Genesis 9 mit sieben) — und
// in der ERSTEN Zone ein entartetes Dreieck, das der `Dreieckfilter` entfernt.
// Genau daran ging es schief: Der Filter kürzte den Index, ließ `groups` aber
// stehen, und `Gruppennetze` schnitt danach an falschen Stellen.
const koerper = flaechen(4);
const rohIndex = [...koerper.getIndex().array];
rohIndex[1] = rohIndex[0];              // Dreieck 0 -> (a, a, c), Fläche 0
koerper.setIndex(rohIndex);
koerper.addGroup(0, 6, 0);
koerper.addGroup(6, 6, 1);
const netzKoerper = new THREE.Mesh(koerper, [
    new THREE.MeshStandardMaterial({ name: 'haut', map: karte('haut.jpg') }),
    new THREE.MeshStandardMaterial({ name: 'nagel', map: karte('nagel.jpg') }),
]);
netzKoerper.name = 'koerper';

// 2. Wimpern: NUR eine Deckkraftmaske, keine Farbkarte.
const netzWimper = new THREE.Mesh(flaechen(2), new THREE.MeshStandardMaterial({
    name: 'wimper', alphaMap: karte('wimper_alpha.jpg'), transparent: true,
}));
netzWimper.name = 'wimper';

// 3. Hornhaut: fast durchsichtige Schale OHNE Farbkarte, wie sie vor jeder
// Genesis-9-Iris sitzt. OBJ kennt keine Durchsichtigkeit — MeshLab zeichnet
// sie als weiße Kugel über dem Auge. Sie darf gar nicht erst mitkommen.
const netzHornhaut = new THREE.Mesh(flaechen(2), new THREE.MeshStandardMaterial({
    name: 'hornhaut', transparent: true, opacity: 0.12,
}));
netzHornhaut.name = 'hornhaut';

// 3b. Gegenprobe: ein halbdurchsichtiger Schleier MIT Karte bleibt drin —
// sonst verschwände Kleidung, die man sehen will.
const netzSchleier = new THREE.Mesh(flaechen(2), new THREE.MeshStandardMaterial({
    name: 'schleier', transparent: true, opacity: 0.2, map: karte('schleier.jpg'),
}));
netzSchleier.name = 'schleier';

// 4. Stranghaar: drei Segmente als entartete Dreiecke, Wireframe-Werkstoff.
const strang = new THREE.BufferGeometry();
strang.setAttribute('position', new THREE.BufferAttribute(new Float32Array([
    0, 0, 0,  0, 1, 0,  0, 2, 0,  1, 0, 0,
]), 3));
strang.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(8), 2));
strang.setIndex([0, 1, 1,  1, 2, 2,  0, 3, 3]);
const netzStrang = new THREE.Mesh(strang, new THREE.MeshStandardMaterial({
    name: 'strang', wireframe: true, map: karte('haar.jpg'),
}));
netzStrang.name = 'strang';

// --- derselbe Weg wie `Modellexport._obj` ---
const gebacken = [netzKoerper, netzWimper, netzHornhaut, netzSchleier, netzStrang]
    .map((m) => Netzpose.gebacken(m, Netzpose.RUHELAGE));
const { netze: zerlegt, weggelassen } = Klarflaechen.entfernen(Gruppennetze.zerlegen(gebacken));
const { mtl, bilder, warnungen } = await ObjMtl.bauen(zerlegt, true, 'T_', 0);
const gruppe = new THREE.Group();
zerlegt.forEach((o) => gruppe.add(o));
gruppe.updateMatrixWorld(true);
const obj = new OBJExporter().parse(gruppe);

// --- auswerten: Flächen je `usemtl`, wie MeshLab die Datei liest ---
const jeMaterial = {};
let laufend = null;
let entartet = 0;
let punkte = 0;
for (const zeile of obj.split('\\n')) {
    if (zeile.startsWith('usemtl ')) laufend = zeile.slice(7).trim();
    else if (zeile.startsWith('v ')) punkte++;
    else if (zeile.startsWith('f ')) {
        jeMaterial[laufend] = (jeMaterial[laufend] || 0) + 1;
        const ecken = zeile.trim().split(/\\s+/).slice(1).map((t) => t.split('/')[0]);
        if (new Set(ecken).size < ecken.length) entartet++;
    }
}
const bloecke = {};
let name = null;
for (const zeile of mtl.split('\\n')) {
    if (zeile.startsWith('newmtl ')) { name = zeile.slice(7).trim(); bloecke[name] = []; }
    else if (name && zeile.trim()) bloecke[name].push(zeile.trim().split(' ')[0]);
}
console.log(JSON.stringify({
    jeMaterial, entartet, punkte, warnungen, weggelassen,
    bloecke, bilder: bilder.map((b) => b.dateiname), netze: zerlegt.map((o) => o.name),
}));
"""


class ModellexportObjTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not shutil.which('node'):
            raise RuntimeError('node ist nicht im Pfad — die JS-Tests führen die Module wirklich aus.')
        ordner = Path(ProjektTemp.ordner('test_modellexport'))
        skript = ordner / 'obj_probe.mjs'
        skript.write_text(SKRIPT % {'viewer': VIEWER}, encoding='utf-8')
        lauf = subprocess.run(
            ['node', skript.as_posix()], cwd=WURZEL, capture_output=True, text=True, timeout=120,
        )
        if lauf.returncode != 0:
            raise RuntimeError(f'node-Lauf gescheitert:\n{lauf.stdout}\n{lauf.stderr}')
        cls.ergebnis = json.loads(lauf.stdout.strip().splitlines()[-1])

    def test_1_jede_materialzone_bekommt_ihr_eigenes_usemtl(self):
        u"""Der Vorfall: Netze mit Material-Array bekamen GAR KEIN `usemtl`,
        ihre Flächen liefen unter dem Material des vorigen Netzes weiter."""
        je = self.ergebnis['jeMaterial']
        self.assertNotIn('null', je, 'Flächen ohne usemtl — die Zuordnung ist verloren')
        self.assertEqual(je.get('haut'), 1, 'Hautzone: zwei Dreiecke, eins davon entartet')
        self.assertEqual(je.get('nagel'), 2,
                         'Nagelzone VOLLSTÄNDIG — sie steht hinter dem gefilterten Dreieck, '
                         'ihre Grenzen müssen mitgewandert sein')
        self.assertEqual(je.get('wimper'), 2, 'Wimpern: zwei Dreiecke')
        self.assertEqual(len(je), 5, 'fünf Materialien, fünf usemtl-Blöcke')
        self.assertEqual(self.ergebnis['netze'],
                         ['koerper_0', 'koerper_1', 'wimper', 'schleier', 'strang'],
                         'das Körpernetz wird in seine zwei Zonen zerlegt, die Hornhaut fällt weg')

    def test_2_farbkarte_und_deckkraftmaske_stehen_in_der_mtl(self):
        u"""Ohne `map_d` wird aus jeder Haarkarte ein volles Rechteck; die
        Wimpern haben überhaupt nur diese Maske und keine Farbkarte."""
        bloecke = self.ergebnis['bloecke']
        self.assertIn('map_Kd', bloecke['haut'], 'Haut braucht ihre Farbkarte')
        self.assertIn('map_d', bloecke['wimper'], 'Wimpern-Deckkraftmaske fehlt')
        self.assertNotIn('map_Kd', bloecke['wimper'], 'Wimpern haben keine Farbkarte')
        self.assertIn('T_wimper_alpha.png', self.ergebnis['bilder'])

    def test_3_straehnen_werden_baender_statt_flaechenloser_dreiecke(self):
        u"""Entartete Dreiecke sind im Wireframe die Strähne selbst. Filtern
        löscht das Haar, roh exportieren lässt MeshLab meckern — also Bänder."""
        self.assertEqual(self.ergebnis['entartet'], 0, 'MeshLab meldet „Identical vertex indices"')
        self.assertEqual(self.ergebnis['jeMaterial'].get('strang'), 6,
                         'drei Segmente ergeben drei Bänder zu je zwei Dreiecken')

    def test_4_zerlegung_nimmt_nur_die_benutzten_punkte_mit(self):
        u"""Werden die Punkte zwischen den Zonen geteilt, schreibt der Exporter
        sie je Zone erneut — bei Genesis 9 sprengte das V8s String-Grenze."""
        self.assertEqual(self.ergebnis['punkte'], 3 + 6 + 6 + 6 + 12,
                         'Hautzone 3 (ein Dreieck), Nagelzone 6, Wimpern 6, Schleier 6, Strähnen 3x4')

    def test_5_kein_stiller_verlust_gemeldet(self):
        self.assertEqual(self.ergebnis['warnungen'], [])

    def test_6_durchsichtige_schale_faellt_weg_der_schleier_bleibt(self):
        u"""DER VORFALL: Vor jeder Genesis-9-Iris sitzt eine kartenlose
        Hornhaut mit `d 0.12`. Die `.mtl` schreibt das korrekt — MeshLab
        stellt Durchsichtigkeit aber gar nicht dar und zeichnet eine weiße
        Kugel über dem Auge. Gemessen an Damira1: die Hornhaut reicht bis
        Z = 0,0862, der Augapfel nur bis 0,0836.

        Die Gegenprobe gehört dazu: ein halbdurchsichtiges Stück MIT Karte
        (Schleier) muss bleiben — sonst verschwände Kleidung."""
        self.assertEqual(self.ergebnis['weggelassen'], ['hornhaut'])
        self.assertNotIn('hornhaut', self.ergebnis['jeMaterial'])
        self.assertEqual(self.ergebnis['jeMaterial'].get('schleier'), 2,
                         'ein durchsichtiges Stück MIT Farbkarte bleibt im Export')
