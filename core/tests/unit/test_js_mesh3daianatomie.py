# -*- coding: utf-8 -*-
"""`Mesh3daianatomie` (`static/viewer/mesh3dai/mesh3daianatomie.js`, 18.10.2026): das Anatomie-Stück eines Anzeigenetzes von Mesh3D-AI bekommt die Haut des Körpers — geprüft in Node.

Das Modul übergibt `Anatomiebacken.backen` nur, was es liest; das Backen selbst (Worker, Canvas) ist hier eine Attrappe am Modul (dieselbe Instanz, die `Mesh3daianatomie` importiert).
1. `_stueck`: nur die Punkte des Stücks, Index neu nummeriert, Lage aus der RUHE, UV mit.
2. `_koerper`: Index je Hautkachel als Gruppe, Materialien mit Gruppe „Body“ und der Karte der Kachel.
3. `_backen` ohne Anatomie-Teil, ohne Ruhelage oder ohne Hautkarte: `false`, nichts gebacken.
4. `_backen` mit Stück: `backen` bekommt Körper, Stück und die Gruppe „Body“; die Karte ersetzt Bild und Farbe des Stückmaterials.
5. `anwenden` rechnet einmal je Netz (zweiter Aufruf = dieselbe Zusage), ruft `fertig` nur nach Erfolg; ein Fehler im Backen wird zu `false`.

Sabotage-Gegenprobe (von Hand): in `_stueck` `pos.set(netz.ruhe…)` durch `netz.uv` ersetzen → Fall 1 rot; in `_koerper` `geo.addGroup` streichen → Fall 2 rot; in `_backen` die Bedingung `!netz.ruhe`
streichen → Fall 3 rot (wirft); `material.color.set(0xffffff)` streichen → Fall 4 rot; in `anwenden` die Prüfung `!netz._anatomie` streichen → Fall 5 rot.

Der Spiegel der Module liegt unter `HumanBodyWeb/node_modules/.pruef_webmodul/` statt im System-Temp: das Modul importiert `three` als nackten Namen, Node findet ihn nur über `node_modules` eines Vorfahren.
"""

import tempfile
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('mesh3dai', 'mesh3daianatomie.js')

SKRIPT = """
import * as THREE from 'three';
const { Mesh3daianatomie: M } = await import(MODUL);
const { Anatomiebacken } = await import(new URL('../gemeinsam/anatomiebacken.js', MODUL).href);

// Netz: Punkte 0–9; Dreiecke 0–1 Körper (Material 0 mit Karte, Material 1 ohne), 2 Körper (Material 2 mit Karte), 3–4 Anatomie (Material 3).
const netz = () => ({
    kopf: { teile: ['koerper', 'anatomie'] },
    dreiecke: new Uint32Array([0, 1, 2, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 8, 6]),
    etikett: new Int8Array([0, 0, 0, 1, 1]),
    material: new Int16Array([0, 1, 2, 3, 3]),
    ruhe: Float32Array.from({ length: 30 }, (_, i) => i / 10),
    uv: Float32Array.from({ length: 20 }, (_, i) => i / 100),
    get uvAttribut() { return new THREE.BufferAttribute(this.uv, 2); },
});
const karte = (name) => ({ name, image: { width: 4 } });
const materialien = () => [
    { map: karte('haut0'), color: new THREE.Color(0.5, 0.5, 0.5) },
    { map: null, color: new THREE.Color(1, 1, 1) },
    { map: karte('haut2'), color: new THREE.Color(1, 1, 1) },
    { map: karte('stueck'), color: new THREE.Color(0.2, 0.1, 0.1), needsUpdate: false },
];
const rund = (a) => Array.from(a, (w) => Math.round(w * 1000) / 1000);

// 1. Stück
const geo = M._stueck(netz(), [7, 8, 9, 9, 8, 6]);
pruefe('Index neu', Array.from(geo.index.array), [0, 1, 2, 2, 1, 3]);
pruefe('Lage aus der Ruhe', rund(geo.attributes.position.array), [2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 1.8, 1.9, 2.0]);
pruefe('UV', rund(geo.attributes.uv.array), [0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.12, 0.13]);

// 2. Körper
const m = materialien();
const koerper = M._koerper(netz(), new Map([[0, [0, 1, 2]], [2, [4, 5, 6]]]), m);
pruefe('Gruppen', koerper.geometry.groups.map((g) => [g.start, g.count, g.materialIndex]), [[0, 3, 0], [3, 3, 1]]);
pruefe('Index', Array.from(koerper.geometry.index.array), [0, 1, 2, 4, 5, 6]);
pruefe('Materialien', koerper.material.map((x) => [x.userData.gruppe, x.map.name]), [['Body', 'haut0'], ['Body', 'haut2']]);

// Attrappe des Backens
const aufrufe = [];
let antwort = async () => ({ map: { name: 'gebacken' } });
Anatomiebacken.backen = async (inst, stueck, quelle, gruppen) => { aufrufe.push({ inst, stueck, gruppen }); return antwort(); };

// 3. Ohne Anatomie, ohne Ruhe, ohne Hautkarte
const ohneTeil = netz(); ohneTeil.kopf.teile = ['koerper'];
const ohneRuhe = netz(); ohneRuhe.ruhe = null;
const ohneHaut = materialien(); ohneHaut[0].map = null; ohneHaut[2].map = null;
pruefe('ohne Anatomie', await M._backen(ohneTeil, materialien()), false);
pruefe('ohne Ruhe', await M._backen(ohneRuhe, materialien()), false);
pruefe('ohne Hautkarte', await M._backen(netz(), ohneHaut), false);
pruefe('nichts gebacken', aufrufe.length, 0);

// 4. Mit Stück
const m4 = materialien();
pruefe('gebacken', await M._backen(netz(), m4), true);
const a = aufrufe[0];
pruefe('Gruppe der Haut', a.gruppen, ['Body']);
pruefe('Hautkacheln (Material 1 ohne Karte fehlt)', a.inst.bodyMesh.material.map((x) => x.map.name), ['haut0', 'haut2']);
pruefe('Punkte des Stücks', a.stueck.geometry.attributes.position.count, 4);
pruefe('Karte am Stück', [m4[3].map.name, m4[3].color.getHex(), m4[3].needsUpdate], ['gebacken', 0xffffff, true]);
pruefe('Haut unverändert', [m4[0].map.name, m4[2].map.name], ['haut0', 'haut2']);

// 5. anwenden: einmal je Netz, fertig nur nach Erfolg, Fehler → false
const n5 = netz();
let fertig = 0;
const z1 = M.anwenden(n5, materialien(), () => { fertig += 1; });
const z2 = M.anwenden(n5, materialien(), () => { fertig += 1; });
pruefe('dieselbe Zusage', z1 === z2, true);
pruefe('Erfolg', await z1, true);
pruefe('fertig einmal', fertig, 1);
pruefe('einmal gebacken', aufrufe.length, 2);
const warn = console.warn; const warnungen = []; console.warn = (t) => warnungen.push(t);
antwort = async () => { throw new Error('Worker weg'); };
let fertig2 = 0;
pruefe('Fehler → false', await M.anwenden(netz(), materialien(), () => { fertig2 += 1; }), false);
console.warn = warn;
pruefe('fertig nicht gerufen', fertig2, 0);
pruefe('Warnung', warnungen.length === 1 && warnungen[0].includes('Worker weg'), true);
antwort = async () => null;
pruefe('ohne Karte → false', await M._backen(netz(), materialien()), false);
console.log(JSON.stringify({ ok: true }));
"""


class Mesh3daianatomieTest(SimpleTestCase):
    databases = set()

    def test_das_stueck_bekommt_die_haut_des_koerpers(self):
        spiegel = Path(settings.BASE_DIR) / 'node_modules' / '.pruef_webmodul'
        spiegel.mkdir(parents=True, exist_ok=True)
        original = tempfile.mkdtemp
        with mock.patch('djangobase.testhelfer.tempfile.mkdtemp', side_effect=lambda prefix='': original(prefix=prefix, dir=str(spiegel))):
            ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
