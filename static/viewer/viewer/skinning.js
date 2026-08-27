/**
 * Viewer — GPU Skinning: 176-bone DEF skeleton + BVH retargeting.
 */
import * as THREE from 'three';
import { state, API } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { buildRigifySkeleton } from '../rigify_skeleton_builder.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Hautgewichte } from '../gemeinsam/hautgewichte.js';

export async function loadSkinWeights() {
    try {
        const resp = await fetch(`${API}/skin-weights/`);
        if (resp.ok) state.skinWeightData = await resp.json();
    } catch (e) {
        Protokoll.warnung('skinning', 'Skin weights not available:', e);
    }
}

export async function loadRigifySkeleton() {
    try {
        const resp = await fetch(`${API}/rigify-skeleton/`);
        if (resp.ok) {
            state.rigifySkeletonData = await resp.json();
            Protokoll.debug('Viewer', `DEF skeleton loaded: ${state.rigifySkeletonData.bone_count} bones`);
        }
    } catch (e) {
        Protokoll.warnung('skinning', 'DEF skeleton not available:', e);
    }
}

/**
 * Convert bodyMesh to SkinnedMesh using DEF skeleton.
 */
export function convertToRigifySkinnedMesh(rigifySkel, swData) {
    if (state.isSkinned || !state.bodyMesh || !state.bodyGeometry) return;

    state.bodyGeometry = state.bodyGeometry.clone();


    Hautgewichte.anGeometrie(state.bodyGeometry, swData, THREE.Float32BufferAttribute);

    state.rigifySkeleton = buildRigifySkeleton(state.rigifySkeletonData, swData);

    const mat = state.bodyMesh.material;
    const pos = state.bodyMesh.position.clone();
    const vis = state.bodyMesh.visible;
    state.scene.remove(state.bodyMesh);

    state.bodyMesh = new THREE.SkinnedMesh(state.bodyGeometry, mat);
    state.bodyMesh.position.copy(pos);
    state.bodyMesh.visible = vis;
    state.bodyMesh.add(state.rigifySkeleton.rootBone);
    state.bodyMesh.bind(state.rigifySkeleton.skeleton);

    state.scene.add(state.bodyMesh);
    state.isSkinned = true;
    Protokoll.debug('Viewer', 'SkinnedMesh created:', state.bodyMesh.isSkinnedMesh,
                'bones:', state.rigifySkeleton.skeleton.bones.length,
                'skinIndex:', !!state.bodyGeometry.attributes.skinIndex,
                'skinWeight:', !!state.bodyGeometry.attributes.skinWeight);
}

/**
 * Ensure body mesh is converted to SkinnedMesh (if skeleton data available).
 */
export function ensureSkinned() {
    if (state.isSkinned) return;
    if (!state.rigifySkeletonData || !state.skinWeightData || !state.bodyMesh) return;
    convertToRigifySkinnedMesh(null, state.skinWeightData);
}

// Register
fn.loadSkinWeights = loadSkinWeights;
fn.loadRigifySkeleton = loadRigifySkeleton;
fn.convertToRigifySkinnedMesh = convertToRigifySkinnedMesh;
fn.ensureSkinned = ensureSkinned;
