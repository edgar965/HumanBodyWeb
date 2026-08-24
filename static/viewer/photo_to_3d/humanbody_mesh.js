/**
 * Photo To 3D — HumanBody mesh loading, DEF skeleton, skin color.
 */
import * as THREE from 'three';
import { state, API, MODEL_OFFSET_X } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Hautfarbe } from '../gemeinsam/hautfarbe.js';
import { Koerpernetz } from './koerpernetz.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import {
    base64ToFloat32, base64ToUint32, blenderToThreeCoords,
    alignBodyToSMPLX, BODY_MATERIALS,
} from './helpers.js';

// =========================================================================
// HumanBody skin color
// =========================================================================
function getSkinMat() {
    if (!state.bodyMesh || !state.bodyMesh.material) return null;
    return Array.isArray(state.bodyMesh.material) ? state.bodyMesh.material[0] : state.bodyMesh.material;
}

export function applySkinColor(bodyType) {
    const mat = getSkinMat();
    if (!mat) return;
    // Prefer detected skin color from photo analysis
    if (state.detectedSkinColor) {
        mat.color.set(state.detectedSkinColor);
        const picker = document.getElementById('skin-color-viewer');
        if (picker) picker.value = state.detectedSkinColor;
        return;
    }
    if (Hautfarbe.ausKoerperart(mat, bodyType, state.skinColors)) {
        const picker = document.getElementById('skin-color-viewer');
        if (picker) picker.value = '#' + mat.color.getHexString();
    }
}

// =========================================================================
// HumanBody mesh loading (shifted left)
// =========================================================================
export async function loadMesh(bodyType) {
    // Das Netz baut `Koerpernetz` (koerpernetz.js) — vorher standen hier
    // 119 Zeilen in einer Funktion.
    const netz = await new Koerpernetz(bodyType).laden();
    if (netz) applySkinColor(bodyType || state.currentBodyType);
    return netz;
}

export function requestMeshUpdate() {
    state.meshUpdatePending = true;
    if (!state.meshUpdateTimer) {
        state.meshUpdateTimer = setTimeout(async () => {
            state.meshUpdateTimer = null;
            if (state.meshUpdatePending) {
                state.meshUpdatePending = false;
                await loadMesh(state.currentBodyType);
            }
        }, 80);
    }
}

// =========================================================================
// HumanBody DEF Skeleton
// =========================================================================
export async function loadRigifySkeleton(bodyType) {
    bodyType = bodyType || state.currentBodyType;
    try {
        const resp = await fetch(`${API}/rigify-skeleton/?body_type=${encodeURIComponent(bodyType)}`);
        if (resp.ok) state.rigifySkeletonData = await resp.json();
    } catch (e) { Protokoll.warnung('humanbody_mesh', 'DEF skeleton not available:', e); }
    try {
        const resp = await fetch(`${API}/skin-weights/?body_type=${encodeURIComponent(bodyType)}`);
        if (resp.ok) state.skinWeightData = await resp.json();
    } catch (e) { Protokoll.warnung('humanbody_mesh', 'Skin weights not available:', e); }
    if (state.rigifySkeletonData && state.skinWeightData) buildRigifySkeleton();
}

export function buildRigifySkeleton() {
    const skelByName = {};
    for (const b of state.rigifySkeletonData.bones) skelByName[b.name] = b;

    const bones = [];
    const boneByName = {};
    let rootBone = null;

    for (const name of state.skinWeightData.bone_names) {
        const bone = new THREE.Bone();
        bone.name = name.replace(/\./g, '_');
        bones.push(bone);
        boneByName[name] = bone;
    }

    for (let i = 0; i < state.skinWeightData.bone_names.length; i++) {
        const name = state.skinWeightData.bone_names[i];
        const bone = bones[i];
        const data = skelByName[name];
        if (!data) continue;

        const p = data.local_position;
        bone.position.set(p[0], p[2], -p[1]);
        const q = data.local_quaternion;
        bone.quaternion.set(q[1], q[3], -q[2], q[0]);

        if (data.parent && boneByName[data.parent]) {
            boneByName[data.parent].add(bone);
        } else if (!rootBone) {
            rootBone = bone;
        }
    }

    for (let i = 0; i < bones.length; i++) {
        if (!bones[i].parent && bones[i] !== rootBone && rootBone) {
            rootBone.add(bones[i]);
        }
    }

    // Store rest quaternions for facial expression deltas
    const restQuats = {};
    for (const [name, bone] of Object.entries(boneByName)) {
        restQuats[name] = bone.quaternion.clone();
    }

    if (rootBone) {
        rootBone.updateWorldMatrix(true, true);
        state.rigifySkeleton = { rootBone, bones, boneByName, restQuats };
    }
}

fn.loadMesh = loadMesh;
fn.requestMeshUpdate = requestMeshUpdate;
fn.loadRigifySkeleton = loadRigifySkeleton;
fn.buildRigifySkeleton = buildRigifySkeleton;
fn.applySkinColor = applySkinColor;
