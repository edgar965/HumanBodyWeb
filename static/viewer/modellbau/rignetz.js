/**
 * Rignetz — aus den Rig-Knochen ein statisches Anzeigenetz bauen.
 *
 * Aus model_generator.js herausgeloest (Umbau 15.08.2026): 318 Zeilen, die je
 * Knochen einen Koerper erzeugen und alles zu einem Mesh verschmelzen.
 *
 * Der Skelettaufbau steht seit dem 29.08.2026 in `skinnetz.js`; die 38
 * Zeilen standen hier und in `modellnetz.js` doppelt (Befund `doppelcode`).
 */

import * as THREE from 'three';
import { computeRigBoneWorldTransforms } from './knochenmatrizen.js';
import { Rigformen } from './rigformen.js';
import { Netzverschmelzung } from './netzverschmelzung.js';
import { Skinnetz } from './skinnetz.js';


/**
 * Generate a non-skinned Mesh from rig bone config.
 * Rig bones have head/tail world positions — no skeleton needed for animation.
 * @param {Object} rigData - Rig bone data {bones: [{name, head, tail, parent, ...}]}
 * @param {Object} config  - Model config {bone_parts, segments, ...}
 * @returns {{ mesh: THREE.Mesh }} | null
 */
export function generateRigBoneMesh(rigData, config, rigifySkeletonData = null, swData = null) {
    const segments = config.segments || 8;
    const worldTransforms = computeRigBoneWorldTransforms(rigData);

    // Build bone index map for skinning (Rigify bones only)
    const canSkin = !!(rigifySkeletonData && swData);
    const boneIndexMap = {};
    if (canSkin) {
        for (let i = 0; i < swData.bone_names.length; i++) {
            boneIndexMap[swData.bone_names[i]] = i;
        }
    }

    const geoChunks = Rigformen.sammeln(
        rigData, config, boneIndexMap, worldTransforms, swData, canSkin);
    if (geoChunks.length === 0) return null;

    const { geometry: mergedGeo, materials, boneVertexRanges,
            mergedSkinIndices, mergedSkinWeights } =
        Netzverschmelzung.zusammenfuegen(geoChunks);

    // Build SkinnedMesh with Rigify skeleton if skin data is available
    if (canSkin) {
        mergedGeo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(mergedSkinIndices, 4));
        mergedGeo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(mergedSkinWeights, 4));

        return Skinnetz.bauen(mergedGeo, materials, boneVertexRanges,
                              rigifySkeletonData, swData);
    }

    const plainMesh = new THREE.Mesh(mergedGeo, materials);
    plainMesh.userData.boneVertexRanges = boneVertexRanges;
    plainMesh.userData.isGeneratedModel = true;
    return { mesh: plainMesh };
}
