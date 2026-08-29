import * as THREE from 'three';
import { buildRigifySkeleton } from '../rigify_skeleton_builder.js';

/**
 * Skinnetz — verschmolzene Geometrie an ein frisch gebautes Skelett binden.
 *
 * WARUM (Befund `doppelcode`, 29.08.2026): `modellnetz.js` und `rignetz.js`
 * bauten das Skelett je 38 Zeilen lang selbst nach — Knochen anlegen, Blender-
 * Achsen drehen, Eltern verketten, Waisen an die Wurzel hängen, Weltmatrizen
 * rechnen. Dieselben Zeilen stehen seit jeher in `rigify_skeleton_builder.js`,
 * und `modellnetz.js` sagte das sogar dazu:
 *
 *     // Build skeleton (same as buildRigifySkeleton in scene_config.js)
 *
 * Ein Kommentar, der auf die Vorlage zeigt, ist keine Wiederverwendung. Wer
 * die Achsenumrechnung dort ändert, ändert sie an einer von drei Stellen.
 *
 * WAS DABEI NICHT VERLOREN GEHEN DARF: `bind()` muss NACH dem
 * `updateWorldMatrix` der Wurzel kommen — sonst nimmt Three.js die Inversen
 * aus Einheitsmatrizen, und das Netz sitzt beim ersten Posen falsch. Die
 * Reihenfolge steckt jetzt hier, nicht mehr dreimal beim Aufrufer.
 */
export class Skinnetz {
    /**
     * @param {Object} geometrie verschmolzene BufferGeometry
     * @param {Array} materialien Materialien in Gruppenreihenfolge
     * @param {Array} knochenbereiche Vertexbereiche je Knochen (`userData`)
     * @param {Object} skelettdaten `{bones: [{name, local_position, …}]}`
     * @param {Object} gewichte `{bone_names: [...]}` — gibt die Indexordnung vor
     * @returns {{mesh: Object, skeleton: Object}}
     */
    static bauen(geometrie, materialien, knochenbereiche, skelettdaten, gewichte) {
        const skelett = buildRigifySkeleton(skelettdaten, gewichte);
        const netz = new THREE.SkinnedMesh(geometrie, materialien);
        netz.add(skelett.rootBone);
        netz.bind(skelett.skeleton);
        netz.userData.boneVertexRanges = knochenbereiche;
        netz.userData.isGeneratedModel = true;
        return { mesh: netz, skeleton: skelett };
    }
}
