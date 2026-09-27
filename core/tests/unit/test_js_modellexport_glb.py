# -*- coding: utf-8 -*-
u"""GLB-Export: die Figur muss überhaupt durchpassen (26.09.2026).

Edgar: „einen weiteren für glb" — nachdem der GLB-Export von Damira1 zweimal
mit `RangeError: Invalid string length` abbrach und den Exportdialog dauerhaft
auf „Exportiere …" stehen ließ.

WAS HIER GEMESSEN WIRD
`GLTFExporter` schreibt jedes `userData` als glTF-`extras` ins JSON. Der
Brocken ist `geometry.userData`: `figurhaut.js` legt dort `indexVoll` ab, den
vollen Index als TypedArray. `JSON.stringify` macht daraus
{"0":123456,"1":123456,…} — gemessen rund 29 Bytes je Eintrag. Und weil
`GLTFExporter` die Geometrie-Zusatzdaten INNERHALB der Materialgruppen-Schleife
serialisiert (`GLTFExporter.js:1941`), zahlt man das je Materialzone erneut.
Bei sieben Hautzonen und 4,5 Mio Indexeinträgen sind das rund 900 MB Text —
V8 bricht bei etwa 512 MB ab.

Der Fall prüft darum nicht „läuft durch", sondern die Zahl dahinter: derselbe
Export einmal mit und einmal ohne `Zusatzdaten.leeren` — der JSON-Block muss
dadurch um Größenordnungen schrumpfen. Ein Fall, der nur „kein Fehler" prüft,
bliebe grün, bis die Figur wieder etwas größer wird.

Sabotage: in `zusatzdaten.js` die Zeile `beiseite(obj.geometry);` streichen
-> Fall 2 rot.
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
globalThis.document = {
    createElement: () => ({
        width: 0, height: 0,
        getContext: () => ({ drawImage: () => {} }),
        toBlob: (rueck) => rueck(new Blob([new Uint8Array([137, 80, 78, 71])], { type: 'image/png' })),
    }),
};
// Den Binärpuffer liest der Exporter über FileReader (GLTFExporter.js:598).
globalThis.FileReader = class {
    readAsArrayBuffer(blob) {
        blob.arrayBuffer().then((puffer) => { this.result = puffer; this.onloadend(); });
    }
};

import * as THREE from 'three';
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js';
const { Zusatzdaten } = await import('file:///%(viewer)s/gemeinsam/zusatzdaten.js');

const EINTRAEGE = 20000;

function netzBauen() {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(36), 3));
    geo.setIndex([...Array(12).keys()]);
    geo.addGroup(0, 6, 0);           // zwei Materialzonen auf EINER Geometrie —
    geo.addGroup(6, 6, 1);           // genau dann zahlt man `extras` doppelt
    geo.userData = { indexVoll: { index: new Uint32Array(EINTRAEGE).fill(123456) } };
    const netz = new THREE.Mesh(geo, [
        new THREE.MeshStandardMaterial({ name: 'a' }),
        new THREE.MeshStandardMaterial({ name: 'b' }),
    ]);
    netz.name = 'probe';
    netz.userData = { regler: 'App-intern' };
    return netz;
}

/** Länge des JSON-Blocks im GLB (Kopf: magic, version, length, chunkLength). */
const jsonLaenge = (glb) => new DataView(glb.buffer || glb).getUint32(12, true);

const roh = await new GLTFExporter().parseAsync([netzBauen()], { binary: true });

const netz = netzBauen();
const zurueck = Zusatzdaten.leeren([netz]);
const geleert = await new GLTFExporter().parseAsync([netz], { binary: true });
const leerWaehrend = Object.keys(netz.geometry.userData).length;
zurueck();

console.log(JSON.stringify({
    eintraege: EINTRAEGE,
    jsonRoh: jsonLaenge(roh),
    jsonGeleert: jsonLaenge(geleert),
    leerWaehrend,
    geoDanach: Object.keys(netz.geometry.userData),
    objektDanach: Object.keys(netz.userData),
    indexDanach: netz.geometry.userData.indexVoll.index.length,
}));
"""


class ModellexportGlbTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not shutil.which('node'):
            raise RuntimeError('node ist nicht im Pfad — die JS-Tests führen die Module wirklich aus.')
        ordner = ProjektTemp.ordner('test_modellexport')
        skript = ordner / 'glb_probe.mjs'
        skript.write_text(SKRIPT % {'viewer': VIEWER}, encoding='utf-8')
        lauf = subprocess.run(
            ['node', skript.as_posix()], cwd=WURZEL, capture_output=True, text=True, timeout=120,
        )
        if lauf.returncode != 0:
            raise RuntimeError(f'node-Lauf gescheitert:\n{lauf.stdout}\n{lauf.stderr}')
        cls.ergebnis = json.loads(lauf.stdout.strip().splitlines()[-1])

    def test_1_ohne_das_leeren_waere_es_riesig(self):
        u"""Die Gegenprobe zum Fall 2: Ohne Eingriff bläht `userData` den
        JSON-Block wirklich auf — sonst würde Fall 2 nur Selbstverständliches
        messen und bliebe auch dann grün, wenn das Leeren nichts mehr tut."""
        je_eintrag = self.ergebnis['jsonRoh'] / self.ergebnis['eintraege']
        self.assertGreater(je_eintrag, 10,
                           'userData schlägt nicht mehr durch — misst der Fall noch, was er soll?')

    def test_2_geleert_bleibt_der_json_block_klein(self):
        u"""Der eigentliche Fix: `geometry.userData` darf nicht ins JSON."""
        self.assertLess(self.ergebnis['jsonGeleert'], 10000,
                        'JSON-Block zu groß — landet `geometry.userData` wieder in den extras?')
        self.assertLess(self.ergebnis['jsonGeleert'], self.ergebnis['jsonRoh'] / 50,
                        'das Leeren muss Größenordnungen bringen, nicht ein paar Prozent')
        self.assertEqual(self.ergebnis['leerWaehrend'], 0, 'während des Exports muss es leer sein')

    def test_3_nach_dem_export_steht_wieder_alles_da(self):
        u"""Die Szene läuft weiter — `indexVoll` wird von der Hautverdeckung
        gebraucht. Ein Export darf die Figur nicht beschädigen."""
        self.assertEqual(self.ergebnis['geoDanach'], ['indexVoll'])
        self.assertEqual(self.ergebnis['objektDanach'], ['regler'])
        self.assertEqual(self.ergebnis['indexDanach'], self.ergebnis['eintraege'])
