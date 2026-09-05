import * as THREE from 'three';
import { Testzustand } from './testzustand.js';
import { createBoneLabels, createBoneViz } from './knochenbild.js';
import { Einpassung } from './einpassung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

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
 * Die Spalte ist ein ZIEL wie DEF (Retarget vom Server, `target=uma`), kein
 * BVH-Format — sie bekommt deshalb keine `Anfangshaltung`. Die Hülle
 * (`Einpassung`) bekommt sie doch: Die UMA-Figur misst 1,89 m über die
 * Gelenke, die Seite zeigt alle Skelette mit 1,68 m.
 */
export class Umaskelett {

    static ADRESSE = '/api/character/uma-skeleton/';
    static PLATZ = 'uma';

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

    /** Vom Server holen und in die Spalte stellen; ohne GLB bleibt sie leer — mit Vermerk. */
    static async laden() {
        const platz = Testzustand.skeletons[Umaskelett.PLATZ];
        let daten;
        try {
            daten = await Serverabruf.json(Umaskelett.ADRESSE);
        } catch (fehler) {
            Protokoll.warnung('skelett_test', `UMA-Skelett nicht ladbar: ${fehler.message}`);
            Umaskelett._beschriften('UMA – keine GLB im Katalog');
            return null;
        }
        const gebaut = Umaskelett.bauen(daten);
        platz.rootBone = gebaut.rootBone;
        platz.boneByName = gebaut.boneByName;
        platz.skeleton = gebaut;
        platz.bones = gebaut.bones;
        const einpassung = new Einpassung(gebaut.rootBone, gebaut.bones);
        const massstab = einpassung.anwenden(Umaskelett.PLATZ);
        createBoneViz(gebaut.bones, Umaskelett.PLATZ, 1 / massstab);
        createBoneLabels(gebaut.bones, Umaskelett.PLATZ);
        Umaskelett._beschriften(`UMA (${daten.datei})`);
        Protokoll.debug('Viewer',
            `UMA-Skelett geladen: ${gebaut.bones.length} Knochen aus ${daten.datei}, `
            + einpassung.beschreibung());
        return gebaut;
    }

    static _beschriften(text) {
        const schild = document.querySelector('.skeleton-label.uma');
        if (schild) schild.textContent = text;
    }
}
