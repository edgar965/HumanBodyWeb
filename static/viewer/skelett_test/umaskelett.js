import * as THREE from 'three';
import { Zielskelett } from './zielskelett.js';

/**
 * Umaskelett — die UMA-Figur aus dem Figurkatalog als Skelettspalte.
 *
 * WARUM (05.09.2026): UMA (Unity Multipurpose Avatar) ist die zweite Figur,
 * die Roomguest spielen kann. Ob unsere Bewegungsbibliothek darauf läuft,
 * sieht man nur im Vergleich: dieselbe BVH auf DEF und auf UMA, nebeneinander.
 * Der Server liest das Skelett aus der GLB (`core/dienste/umaskelett.py`)
 * und liefert es fertig in Three.js-Form — Y oben, Quaternion [x, y, z, w],
 * nach +Z ausgerichtet wie DEF. Anders als `rigify_skeleton_builder.js`
 * gibt es hier keine Blender-Umrechnung und keine Punkte in den Namen.
 *
 * Der Ablauf (holen, einpassen, Knochenbild, Schild) liegt seit dem
 * 19.09.2026 in `Zielskelett` — Genesis 9 geht denselben Weg. Hier bleibt,
 * was UMA eigen ist: Adresse, Platz und der Bau aus glTF-Knochen.
 */
export class Umaskelett extends Zielskelett {

    static ADRESSE = '/api/character/uma-skeleton/';
    static PLATZ = 'uma';
    static NAME = 'UMA';
    static FEHLT = 'keine GLB im Katalog';

    /** Three.js-Knochen aus der Serverantwort — die Werte werden direkt übernommen. */
    static bauen(daten) {
        const bones = [];
        const boneByName = {};
        for (const eintrag of daten.bones) {
            const bone = new THREE.Bone();
            bone.name = eintrag.name;
            bone.position.fromArray(eintrag.local_position);
            bone.quaternion.fromArray(eintrag.local_quaternion);
            bones.push(bone);
            boneByName[eintrag.name] = bone;
        }
        let rootBone = null;
        for (const eintrag of daten.bones) {
            const eltern = eintrag.parent ? boneByName[eintrag.parent] : null;
            if (eltern) eltern.add(boneByName[eintrag.name]);
            else if (!rootBone) rootBone = boneByName[eintrag.name];
            else rootBone.add(boneByName[eintrag.name]);   // zweite Wurzel unter die erste
        }
        if (!rootBone) throw new Error('UMA-Skelett ohne Knochen');
        rootBone.updateWorldMatrix(true, true);
        return { skeleton: new THREE.Skeleton(bones), rootBone, bones, boneByName };
    }

    static herkunft(daten) {
        return daten.datei || '';
    }
}
