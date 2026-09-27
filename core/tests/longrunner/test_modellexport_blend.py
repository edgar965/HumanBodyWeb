# -*- coding: utf-8 -*-
u"""`.blend`-Export: was aus Blender herauskommt, muss die Figur sein (26.09.2026).

Edgar: „und einen für blender? Das Ergebnis soll so ausschauen wie das
Originalmodell."

Der Weg ist: Browser baut eine GLB -> `Modellexportlauf` ruft Blender
(`effekte/blender/modellexportblend.py`) -> `.blend`. Geprüft wird beides,
was dabei still schiefgehen kann:

1. Kommt überhaupt die Figur an? Blender öffnet die geschriebene Datei ein
   zweites Mal und zählt nach: Netz, Punkte, BEIDE Materialzonen, die
   Bildtextur. Ein Import, der die Materialien verliert, fiele sonst erst
   Edgar beim Öffnen auf.
2. Liegt sie am richtigen Platz? Seit 26.09.2026 bekommt jeder Export einen
   eigenen Unterordner (`<Ziel>/<Name>/`), weil eine `.obj` siebzehn PNGs
   mitbringt und die sonst mit denen jedes anderen Exports durcheinander
   liegen.

LANGSAM MIT ANSAGE: zwei Blender-Starts, rund eine halbe Minute. Darum
`longrunner` und nicht `unit`.

Sabotage: in `modellexportblend.py` den Import-Aufruf gegen eine leere Szene
tauschen -> Fall 1 rot; in `modellexportlauf.py` `_freie_ablage` durch
`ordner` ersetzen -> Fall 2 rot.
"""
import json
import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from core.dienste.modellexportlauf import Modellexportlauf
from core.projekt_temp import ProjektTemp

WURZEL = Path(settings.BASE_DIR)
VIEWER = (WURZEL / 'static' / 'viewer').as_posix()

#: Eine GLB mit zwei Materialzonen auf einem Netz und einer echten Bildkarte —
#: dasselbe Muster wie der Genesis-9-Körper, nur mit vier Dreiecken.
GLB_SKRIPT = """
import fs from 'node:fs';
const PNG = fs.readFileSync('%(png)s');
// Der Exporter dreht Texturen über den Kontext (`translate`/`scale`, s.
// GLTFExporter.js:1314) — jede Zeichenanweisung darf hier folgenlos bleiben,
// das Bild liefert `toBlob`.
globalThis.document = {
    createElement: () => ({
        width: 0, height: 0,
        getContext: () => new Proxy({}, { get: () => () => {} }),
        toBlob: (rueck) => rueck(new Blob([PNG], { type: 'image/png' })),
    }),
};
globalThis.FileReader = class {
    readAsArrayBuffer(blob) {
        blob.arrayBuffer().then((puffer) => { this.result = puffer; this.onloadend(); });
    }
};
// `processImage` lässt nur HTMLImageElement/HTMLCanvasElement/ImageBitmap/
// OffscreenCanvas durch (GLTFExporter.js:1357). Im Browser ist es ein
// ImageBitmap (`genesis9texturen.js` lädt alles über `createImageBitmap`) —
// in Node muss es diese Klasse erst geben.
globalThis.ImageBitmap = class ImageBitmap {
    constructor(breite, hoehe) { this.width = breite; this.height = hoehe; }
};

import * as THREE from 'three';
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js';

const geo = new THREE.BufferGeometry();
const lage = new Float32Array(36);
for (let i = 0; i < 36; i++) lage[i] = (i %% 5) * 0.2;
geo.setAttribute('position', new THREE.BufferAttribute(lage, 3));
geo.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(24), 2));
// Skin-Gewichte: alles am ersten Knochen — es geht um die Spur, nicht um Verformung.
geo.setAttribute('skinIndex', new THREE.BufferAttribute(new Uint16Array(48), 4));
geo.setAttribute('skinWeight', new THREE.BufferAttribute(
    new Float32Array(Array.from({ length: 48 }, (_, i) => (i %% 4 === 0 ? 1 : 0))), 4));
geo.setIndex([...Array(12).keys()]);
geo.addGroup(0, 6, 0);
geo.addGroup(6, 6, 1);
const karte = new THREE.Texture();
// WIRKLICH ein `ImageBitmap`: `processImage` prüft mit `instanceof`
// (GLTFExporter.js:1357), ein Objektliteral mit Breite und Höhe reicht nicht.
karte.image = new ImageBitmap(2, 2);

// Skelett und Bewegung — sonst prüft der Fall die Animation gar nicht.
const wurzel = new THREE.Bone();
wurzel.name = 'wurzel';
const kind = new THREE.Bone();
kind.name = 'glied';
kind.position.set(0, 1, 0);
wurzel.add(kind);
const skelett = new THREE.Skeleton([wurzel, kind]);

const netz = new THREE.SkinnedMesh(geo, [
    new THREE.MeshStandardMaterial({ name: 'haut', map: karte }),
    new THREE.MeshStandardMaterial({ name: 'nagel' }),
]);
netz.name = 'Probefigur';
netz.add(wurzel);
netz.bind(skelett);

const spur = new THREE.VectorKeyframeTrack(
    'glied.position', [0, 0.5, 1], [0, 1, 0,  0, 1.5, 0,  0, 1, 0]);
const clip = new THREE.AnimationClip('Probebewegung', 1, [spur]);

const glb = await new GLTFExporter().parseAsync([netz], { binary: true, animations: [clip] });
fs.writeFileSync('%(glb)s', Buffer.from(glb.buffer || glb));
console.log(JSON.stringify({ bytes: (glb.buffer || glb).byteLength }));
"""

#: Läuft IN Blender: die geschriebene `.blend` aufmachen und nachzählen.
ZAEHL_SKRIPT = """
import json
import sys

import bpy

ziel = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.open_mainfile(filepath=ziel[0])
netze = [o for o in bpy.data.objects if o.type == 'MESH']
bilder = [i for i in bpy.data.images if i.name != 'Render Result']
mit_texturknoten = [
    m.name for m in bpy.data.materials
    if m.use_nodes and any(k.type == 'TEX_IMAGE' and k.image for k in m.node_tree.nodes)
]
shading = []
for bildschirm in bpy.data.screens:
    for bereich in bildschirm.areas:
        if bereich.type == 'VIEW_3D':
            shading += [r.shading.type for r in bereich.spaces if r.type == 'VIEW_3D']
befund = {
    'objekte': [o.name for o in bpy.data.objects],
    'netze': len(netze),
    'punkte': sum(len(o.data.vertices) for o in netze),
    'werkstoffe': sorted(m.name for m in bpy.data.materials),
    'bilder': [i.name for i in bilder if i.size[0] > 0],
    # Sieht man die Textur beim Öffnen? (Edgar: „in blender fehlt die Textur")
    'mit_texturknoten': sorted(mit_texturknoten),
    'shading': sorted(set(shading)),
    # Ist die Bewegung da? (Edgar: „in blender funktioniert die animation nicht")
    'aktionen': sorted(a.name for a in bpy.data.actions),
    'skelette': [o.name for o in bpy.data.objects if o.type == 'ARMATURE'],
    'bereich': [bpy.context.scene.frame_start, bpy.context.scene.frame_end],
}
with open(ziel[1], 'w', encoding='utf-8') as datei:
    json.dump(befund, datei)
"""


class ModellexportBlendTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not shutil.which('node'):
            raise RuntimeError('node ist nicht im Pfad — der Fall baut die GLB wirklich.')
        blender = Path(settings.BLENDER_EXE)
        if not blender.exists():
            raise RuntimeError(f'Blender fehlt: {blender}')
        cls.ordner = ProjektTemp.ordner('test_blendexport')

        # 1. Ein echtes (winziges) PNG, damit Blender die Bildkarte auch lädt.
        from PIL import Image
        png = cls.ordner / 'karte.png'
        Image.new('RGB', (2, 2), (200, 120, 90)).save(png)

        # 2. Die GLB im Browser-Weg bauen.
        glb = cls.ordner / 'probe.glb'
        skript = cls.ordner / 'glb_bauen.mjs'
        skript.write_text(
            GLB_SKRIPT % {'png': png.as_posix(), 'glb': glb.as_posix()}, encoding='utf-8',
        )
        lauf = subprocess.run(['node', skript.as_posix()], cwd=WURZEL,
                              capture_output=True, text=True, timeout=120)
        if lauf.returncode != 0:
            raise RuntimeError(f'GLB-Bau gescheitert:\n{lauf.stdout}\n{lauf.stderr}')

        # 3. Derselbe Weg wie der Endpunkt: Lauf mit `blend_quelle`.
        cls.ziel = cls.ordner / 'Ablage'
        cls.ziel.mkdir()
        cls.ergebnis = Modellexportlauf(
            str(cls.ziel), 'Probefigur', [],
            SimpleUploadedFile('MODELL.glb', glb.read_bytes()),
        ).ausfuehren()

        # 4. Nachzählen — in Blender, an der geschriebenen Datei.
        blend = Path(cls.ergebnis['ordner']) / cls.ergebnis['dateien'][0]['name']
        cls.blend = blend
        befund = cls.ordner / 'befund.json'
        zaehler = cls.ordner / 'zaehlen.py'
        zaehler.write_text(ZAEHL_SKRIPT, encoding='utf-8')
        pruefung = subprocess.run(
            [str(blender), '-b', '--factory-startup', '--python', str(zaehler),
             '--', str(blend), str(befund)],
            capture_output=True, text=True, timeout=300,
        )
        if not befund.exists():
            raise RuntimeError(f'Blender-Zählung ohne Ergebnis:\n{pruefung.stdout[-2000:]}')
        cls.befund = json.loads(befund.read_text(encoding='utf-8'))

    def test_1_die_figur_steht_mit_beiden_zonen_in_der_blend(self):
        u"""Auf die ANZAHL der Objekte kommt es nicht an: bei einem Netz mit
        Skin legt Blenders glTF-Importer je Materialzone ein eigenes Objekt
        an, ohne Skin eines mit zwei Werkstoffplätzen. Beides ist richtig.
        Zählen muss man die Punkte und die Werkstoffe."""
        self.assertIn(self.befund['netze'], (1, 2), self.befund['objekte'])
        self.assertEqual(self.befund['punkte'], 12,
                         'vier Dreiecke ohne geteilte Punkte — drin ist: %s' % self.befund)
        self.assertNotIn('Icosphere', self.befund['objekte'],
                         'Blenders glTF-Import legt ein Fremdobjekt an, das nicht in der '
                         'GLB steht — es muss raus (`fremdkoerper_entfernen`)')
        self.assertIn('haut', self.befund['werkstoffe'])
        self.assertIn('nagel', self.befund['werkstoffe'],
                      'die zweite Materialzone fehlt — glTF-Primitive verloren?')
        self.assertTrue(self.befund['bilder'], 'die Bildkarte ist nicht mitgekommen')

    def test_2_jeder_export_bekommt_seinen_unterordner(self):
        ablage = Path(self.ergebnis['ordner'])
        self.assertEqual(ablage.parent, self.ziel, 'Unterordner fehlt')
        self.assertEqual(ablage.name, 'Probefigur')
        self.assertTrue(self.blend.exists())
        self.assertGreater(self.blend.stat().st_size, 1000)

    def test_3_ein_zweiter_export_ueberschreibt_nichts(self):
        zweiter = Modellexportlauf._freie_ablage(self.ziel, 'Probefigur')
        self.assertEqual(zweiter.name, 'Probefigur_2')

    def test_4_die_textur_ist_beim_oeffnen_zu_sehen(self):
        u"""Edgar: „in blender fehlt die Textur". Sie WAR da — gemessen 23
        Bilder, alle eingepackt, 18 von 20 Werkstoffen mit Texturknoten. Nur
        stand Blenders Arbeitsbereich „Layout" auf SOLID, einer einfarbig
        grauen Darstellung. Wer die Datei bekommt, soll die Figur sehen und
        nicht erst eine Ansichtseinstellung suchen."""
        self.assertIn('haut', self.befund['mit_texturknoten'],
                      'der Werkstoff hat keinen Texturknoten — die Karte ist nicht verdrahtet')
        self.assertEqual(self.befund['shading'], ['MATERIAL'],
                         'mindestens eine 3D-Ansicht steht noch auf SOLID: %s'
                         % self.befund['shading'])

    def test_5_die_animation_ist_da_und_abspielbar(self):
        u"""Edgar: „in blender funktioniert die animation nicht". Zwei Dinge
        gehören dazu: die Aktion muss im Import ankommen UND der Abspielbereich
        muss auf ihre Bilder stehen — sonst drückt man Leertaste und nichts
        regt sich, weil die Szene bei Blenders Werksbereich 1–250 steht."""
        self.assertTrue(self.befund['skelette'], 'kein Skelett in der .blend')
        self.assertTrue(self.befund['aktionen'], 'keine Aktion — die Animation ist verloren')
        von, bis = self.befund['bereich']
        self.assertLess(bis - von, 100,
                        'der Abspielbereich steht noch auf Blenders Werksvorgabe 1–250')
        self.assertGreater(bis, von, 'der Abspielbereich ist leer')
