/**
 * Modellnetz — aus Skelett und Konfiguration ein SkinnedMesh bauen.
 *
 * Aus model_generator.js herausgeloest (Umbau 15.08.2026): eine Funktion von
 * 375 Zeilen, die je Knochen eine Form erzeugt, alle Formen verschmilzt,
 * Gewichte setzt und das Ergebnis an das Skelett bindet.
 */

import * as THREE from 'three';
import './formenbauer.js';
import { computeBoneWorldTransforms } from './knochenmatrizen.js';
import './knochengruppen.js';
import { Knochenformen } from './knochenformen.js';
import { Netzverschmelzung } from './netzverschmelzung.js';


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

    // Build skeleton (same as buildRigifySkeleton in scene_config.js)
    const skelByNameMap = {};
    for (const b of skelData.bones) skelByNameMap[b.name] = b;

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
        const bdata = skelByNameMap[name];
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
        const bdata = skelByNameMap[name];
        if (!bdata) continue;
        if (!bdata.parent && bones[i] !== rootBone && rootBone) rootBone.add(bones[i]);
    }
    if (!rootBone && bones.length > 0) rootBone = bones[0];
    rootBone.updateWorldMatrix(true, true);

    const skeleton = new THREE.Skeleton(bones);

    // Create SkinnedMesh
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
