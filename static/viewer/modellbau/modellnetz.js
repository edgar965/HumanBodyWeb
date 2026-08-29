/**
 * Modellnetz — aus Skelett und Konfiguration ein SkinnedMesh bauen.
 *
 * Aus model_generator.js herausgeloest (Umbau 15.08.2026): eine Funktion von
 * 375 Zeilen, die je Knochen eine Form erzeugt, alle Formen verschmilzt,
 * Gewichte setzt und das Ergebnis an das Skelett bindet.
 *
 * Der Skelettaufbau steht seit dem 29.08.2026 in `skinnetz.js` und geht
 * damit durch `buildRigifySkeleton` — dieselben 38 Zeilen standen hier,
 * in `rignetz.js` und in `rigify_skeleton_builder.js` (Befund
 * `doppelcode`). Der Kommentar an der Stelle nannte die Vorlage sogar.
 */

import { computeBoneWorldTransforms } from './knochenmatrizen.js';
import { Knochenformen } from './knochenformen.js';
import { Netzverschmelzung } from './netzverschmelzung.js';
import { Skinnetz } from './skinnetz.js';


/**
 * Generate a merged SkinnedMesh from the model config.
 * Each visible bone gets a geometric shape (cylinder/box/sphere) positioned
 * between parent and bone world positions. All merged into one BufferGeometry.
 *
 * @param {Object} skelData - Raw skeleton data {bones: [{name, local_position, local_quaternion, parent}]}
 * @param {Object} swData   - Skin weight data {bone_names: [...], weights: [...]}
 * @param {Object} config   - Model config {bone_parts, segments, default_color, default_radius}
 * @returns {{ mesh: THREE.SkinnedMesh, skeleton: {skeleton, rootBone, bones, boneByName} }}
 */
export function generateModelMesh(skelData, swData, config) {
    const segments = config.segments || 8;
    const worldTransforms = computeBoneWorldTransforms(skelData, swData);

    // Build bone index map from swData (same order as animation skeleton)
    const boneIndexMap = {};
    for (let i = 0; i < swData.bone_names.length; i++) {
        boneIndexMap[swData.bone_names[i]] = i;
    }

    // Build children map to find each bone's TAIL position
    const childrenMap = {};  // boneName -> [childNames]
    for (const b of skelData.bones) {
        if (b.parent) {
            if (!childrenMap[b.parent]) childrenMap[b.parent] = [];
            childrenMap[b.parent].push(b.name);
        }
    }

    const skelByName = {};
    for (const b of skelData.bones) skelByName[b.name] = b;
    const geoChunks = Knochenformen.sammeln(
        skelData, swData, config, boneIndexMap, childrenMap, skelByName,
        worldTransforms);
    if (geoChunks.length === 0) return null;

    const { geometry: mergedGeo, materials, boneVertexRanges } =
        Netzverschmelzung.zusammenfuegen(geoChunks);

    return Skinnetz.bauen(mergedGeo, materials, boneVertexRanges,
                          skelData, swData);
}
