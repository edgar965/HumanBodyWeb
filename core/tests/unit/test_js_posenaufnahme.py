# -*- coding: utf-8 -*-
"""`Posenaufnahme`: aus der Stellung einer Figur die Pose zurücklesen.

WARUM (Edgar, 17.10.2026, „Aktuelle Pose speichern"): Die Aufnahme ist die
Umkehrung von `Posenanwendung.anwenden` — dort liegt auf jedem Knochen
`ruhelage * delta`, und bei Oberarm und Oberschenkel wird die Drehung des
Elternknochens herausgerechnet. Stimmt die Umkehrung nicht auf den Zahn, lädt
eine gespeicherte Pose später eine andere Stellung als die, die man sah — und
das fiele erst beim Laden auf, nicht beim Speichern.

WAS HIER GEPRÜFT WIRD, mit echtem Three.js und dem ORIGINALCODE von
`Posenanwendung` (nur ihre Importe fehlen — sie hängen an `state.js` und damit
am Browser):

1. Zufällige Deltas auf alle 17 Knochen eines Rigify-artigen Skeletts mit
   schiefer Ruhelage VORWÄRTS anwenden, zurücklesen: dieselben Deltas.
2. Die zurückgelesenen Deltas auf die Ruhelage anwenden: dieselbe Endlage.
3. Die Aufnahme verändert die Knochen nicht (sie stellt kurz die Ruhelage her).
4. Mit Absatzschuh: Der Server rechnet das Fußdelta beim Laden rechts hinein,
   die Aufnahme muss es herausnehmen — sonst stünde es doppelt in der Datei.
5. GEGENPROBE: Ohne die Gliedwurzel-Korrektur weicht der Oberarm um über 90°
   ab. Der Test wird also rot, wenn jemand die Korrektur der Aufnahme streicht.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

import json

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

# Einstieg ist Three.js, nicht `posenaufnahme.js`: `Webmodul` spiegelt alles, was der
# Einstieg importiert, und über `posenanwendung.js` → `state.js` hinge daran
# `three/addons/…` — das löst der Spiegel nicht auf (lief am 17.10.2026 in der Suite
# deshalb auf WebmodulFehler). Die beiden Klassen liest das Skript von ihrem echten Ort.
MODUL = Jsmodul('..', 'vendor', 'three', 'build', 'three.module.js')
QUELLEN = {d: str(Jsmodul.VIEWER / 'charakter' / d) for d in ('posenanwendung.js', 'posenaufnahme.js')}

SKRIPT = """
const { readFileSync } = await import('node:fs');
const THREE = await import(MODUL);
const QUELLEN = __QUELLEN__;

// Die Klassen ohne ihre Importe laden (sie hängen am Browser: state.js, DOM).
const lade = (datei, klasse, stuetzen) => {
    const quelle = readFileSync(QUELLEN[datei], 'utf8')
        .replace(/^import .*$/gm, '').replace(/^export class/m, 'class');
    const rumpf = quelle + `\\nreturn ${klasse};`;
    return new Function(...Object.keys(stuetzen), rumpf)(...Object.values(stuetzen));
};
const Posenabsatz = { aktiv: (f) => !!f?.absatz && f.absatz.winkel_grad > 0 };
const Posenanwendung = lade('posenanwendung.js', 'Posenanwendung', {
    state: {}, _selectedInst: () => null, convertInstToSkinned: () => {}, Serverabruf: {},
    Protokoll: { debug() {} }, Posenabsatz, fn: {} });
const Posenaufnahme = lade('posenaufnahme.js', 'Posenaufnahme', { Posenanwendung, Posenabsatz });

// Eine feste Zahlenfolge: derselbe Lauf bei jedem Start.
const zufall = (() => {
    let s = 12345;
    return () => (s = (s * 1664525 + 1013904223) % 4294967296) / 4294967296;
})();
const drehung = (grad) => new THREE.Quaternion().setFromEuler(new THREE.Euler(
    (zufall() - 0.5) * 2 * grad * Math.PI / 180, (zufall() - 0.5) * 2 * grad * Math.PI / 180,
    (zufall() - 0.5) * 2 * grad * Math.PI / 180));

// Name (mit Punkt) -> Elternname. Oberarm und Oberschenkel sind die Gliedwurzeln.
const BAUM = {
    'DEF-spine': null, 'DEF-spine.001': 'DEF-spine', 'DEF-spine.002': 'DEF-spine.001',
    'DEF-shoulder.L': 'DEF-spine.002', 'DEF-upper_arm.L': 'DEF-shoulder.L',
    'DEF-forearm.L': 'DEF-upper_arm.L',
    'DEF-shoulder.R': 'DEF-spine.002', 'DEF-upper_arm.R': 'DEF-shoulder.R',
    'DEF-forearm.R': 'DEF-upper_arm.R',
    'DEF-thigh.L': 'DEF-spine', 'DEF-shin.L': 'DEF-thigh.L', 'DEF-foot.L': 'DEF-shin.L',
    'DEF-toe.L': 'DEF-foot.L',
    'DEF-thigh.R': 'DEF-spine', 'DEF-shin.R': 'DEF-thigh.R', 'DEF-foot.R': 'DEF-shin.R',
    'DEF-toe.R': 'DEF-foot.R',
};
const jsName = (n) => n.replace(/\\./g, '_');

function baue(mitAbsatz) {
    const knochen = {};
    for (const [name, eltern] of Object.entries(BAUM)) {
        const k = new THREE.Bone();
        k.name = jsName(name);
        k.position.set(zufall() - 0.5, zufall(), zufall() - 0.5);
        k.quaternion.copy(drehung(40));                    // eine schiefe Ruhelage
        knochen[name] = k;
        if (eltern) knochen[eltern].add(k);
    }
    const alle = Object.values(knochen);
    alle[0].updateWorldMatrix(true, true);
    const skelett = new THREE.Skeleton(alle);
    const ruhe = {};
    for (const k of skelett.bones) ruhe[k.name] = k.quaternion.clone();
    return { isSkinned: true, _aPoseBones: ruhe, skelett,
             absatz: mitAbsatz ? { winkel_grad: 30 } : null,
             group: { traverse: (cb) => cb({ isSkinnedMesh: true, skeleton: skelett }) } };
}
const winkel = (a, b) => 2 * Math.acos(Math.min(1, Math.abs(a.dot(b)))) * 180 / Math.PI;
// acos nahe 1 rauscht um ~4e-6 Grad - darunter ist "gleich".
const GLEICH = 1e-4;

const ergebnis = {};
for (const mitAbsatz of [false, true]) {
    const titel = mitAbsatz ? 'mit Absatz' : 'ohne Absatz';
    const figur = baue(mitAbsatz);
    const skelett = figur.skelett;
    const deltas = {};
    for (const name of Object.keys(BAUM)) deltas[name] = drehung(55);
    // Der Server rechnet das Fussdelta RECHTS in die Pose ein (`Absatzpose.einrechnen`).
    const absatz = mitAbsatz ? {
        'DEF-foot.L': [0.2, 0, 0, Math.sqrt(0.96)], 'DEF-foot.R': [0.2, 0, 0, Math.sqrt(0.96)],
        'DEF-toe.L': [-0.1, 0, 0, Math.sqrt(0.99)], 'DEF-toe.R': [-0.1, 0, 0, Math.sqrt(0.99)] } : null;
    figur.absatzDeltas = absatz;
    const vorwaerts = {};
    for (const [name, q] of Object.entries(deltas)) {
        const w = q.clone();
        if (absatz?.[name]) w.multiply(new THREE.Quaternion(...absatz[name]));
        vorwaerts[name] = [w.x, w.y, w.z, w.w];
    }
    new Posenanwendung(figur).anwenden(vorwaerts);
    const endlage = skelett.bones.map((k) => k.quaternion.clone());

    const zurueck = Posenaufnahme.aufnehmen(figur);
    pruefe(titel + ': Aufnahme gelungen', zurueck.ok, true);
    pruefe(titel + ': Aufnahme laesst die Knochen unveraendert',
           Math.max(...skelett.bones.map((k, i) => winkel(k.quaternion, endlage[i]))) < GLEICH, true);
    let groesste = 0;
    for (const [name, q] of Object.entries(deltas)) {
        const z = zurueck.drehungen[jsName(name)];
        if (!z) throw new Error(titel + ': Delta fehlt fuer ' + name);
        groesste = Math.max(groesste, winkel(q, new THREE.Quaternion(...z)));
    }
    pruefe(titel + ': alle 17 Deltas wie angewendet', groesste < GLEICH, true);

    // Laden der gespeicherten Pose aus der Ruhelage ergibt dieselbe Endlage.
    for (const k of skelett.bones) k.quaternion.copy(figur._aPoseBones[k.name]);
    skelett.bones[0].updateWorldMatrix(true, true);
    new Posenanwendung({ ...figur, absatzDeltas: null }).anwenden(zurueck.drehungen);
    for (const [name, w] of Object.entries(absatz || {})) {
        skelett.getBoneByName(jsName(name)).quaternion.multiply(new THREE.Quaternion(...w));
    }
    pruefe(titel + ': Laden ergibt dieselbe Endlage',
           Math.max(...skelett.bones.map((k, i) => winkel(k.quaternion, endlage[i]))) < GLEICH, true);
    ergebnis[titel] = groesste;
}

// GEGENPROBE: ohne Gliedwurzel-Korrektur muss der Oberarm danebenliegen.
{
    const figur = baue(false);
    const deltas = {};
    for (const name of Object.keys(BAUM)) { const q = drehung(55); deltas[name] = [q.x, q.y, q.z, q.w]; }
    new Posenanwendung(figur).anwenden(deltas);
    const echt = Posenanwendung.GLIEDWURZELN.slice();
    Posenanwendung.GLIEDWURZELN.length = 0;
    const falsch = Posenaufnahme.aufnehmen(figur).drehungen;
    echt.forEach((n) => Posenanwendung.GLIEDWURZELN.push(n));
    const w = winkel(new THREE.Quaternion(...deltas['DEF-upper_arm.L']),
                     new THREE.Quaternion(...falsch['DEF-upper_arm_L']));
    pruefe('Gegenprobe: ohne Korrektur weicht der Oberarm ab', w > 10, true);
}

// Ruhelage ohne Bewegung: nichts zu speichern, mit Grund.
{
    const figur = baue(false);
    const r = Posenaufnahme.aufnehmen(figur);
    pruefe('Ruhelage: nichts zu speichern', [r.ok, typeof r.grund], [false, 'string']);
    delete figur._aPoseBones;
    const o = Posenaufnahme.aufnehmen(figur);
    pruefe('ohne gesicherte Ruhelage: Grund', [o.ok, /Ruhelage/.test(o.grund)], [false, true]);
    pruefe('ohne Figur: Grund', Posenaufnahme.aufnehmen(null).ok, false);
    pruefe('fremde Figurart: Grund', Posenaufnahme.aufnehmen({ quelle: 'smpl' }).ok, false);
}

console.log(JSON.stringify({ ok: true, ...ergebnis }));
"""


class PosenaufnahmeTest(SimpleTestCase):
    """Zurücklesen ist die Umkehrung des Anwendens — auf allen Knochen."""

    def test_aufnahme_kehrt_das_anwenden_um(self):
        ausgabe = MODUL.laufen(SKRIPT.replace('__QUELLEN__', json.dumps(QUELLEN)))
        self.assertTrue(ausgabe.get('ok'), ausgabe)
