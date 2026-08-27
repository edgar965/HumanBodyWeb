/**
 * Rignetz — aus den Rig-Knochen ein statisches Anzeigenetz bauen.
 *
 * Aus model_generator.js herausgeloest (Umbau 15.08.2026): 318 Zeilen, die je
 * Knochen einen Koerper erzeugen und alles zu einem Mesh verschmelzen.
 */

import * as THREE from 'three';
import { _mergeSimpleGeos, _buildPlane, _buildRhombus, _getOrLoadTexture, _makeDoubleSided } from './formenbauer.js';
import { computeRigBoneWorldTransforms } from './knochenmatrizen.js';
import { Rigformen } from './rigformen.js';
import { Netzverschmelzung } from './netzverschmelzung.js';


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

        const skelByName = {};
        for (const b of rigifySkeletonData.bones) skelByName[b.name] = b;

        const bones = [];
        const boneByName = {};
        let rootBone = null;

        for (const name of swData.bone_names) {
            const bone = new THREE.Bone();
            bone.name = name.replace(/\./g, '_');
            bones.push(bone);
            boneByName[name] = bone;
        }
        for (let i = 0; i < swData.bone_names.length; i++) {
            const name = swData.bone_names[i];
            const bone = bones[i];
            const bdata = skelByName[name];
            if (!bdata) continue;
            const p = bdata.local_position;
            bone.position.set(p[0], p[2], -p[1]);
            const q = bdata.local_quaternion;
            bone.quaternion.set(q[1], q[3], -q[2], q[0]);
            if (bdata.parent && boneByName[bdata.parent]) {
                boneByName[bdata.parent].add(bone);
            } else if (!rootBone) {
                rootBone = bone;
            }
        }
        for (let i = 0; i < bones.length; i++) {
            const name = swData.bone_names[i];
            const bdata = skelByName[name];
            if (!bdata) continue;
            if (!bdata.parent && bones[i] !== rootBone && rootBone) rootBone.add(bones[i]);
        }
        if (!rootBone && bones.length > 0) rootBone = bones[0];
        rootBone.updateWorldMatrix(true, true);

        const skeleton = new THREE.Skeleton(bones);
        const skinnedMesh = new THREE.SkinnedMesh(mergedGeo, materials);
        skinnedMesh.add(rootBone);
        skinnedMesh.bind(skeleton);

        skinnedMesh.userData.boneVertexRanges = boneVertexRanges;
        skinnedMesh.userData.isGeneratedModel = true;

        return {
            mesh: skinnedMesh,
            skeleton: { skeleton, rootBone, bones, boneByName },
        };
    }

    const plainMesh = new THREE.Mesh(mergedGeo, materials);
    plainMesh.userData.boneVertexRanges = boneVertexRanges;
    plainMesh.userData.isGeneratedModel = true;
    return { mesh: plainMesh };
}
