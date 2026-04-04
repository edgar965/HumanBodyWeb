/**
 * Viewer — GPU Skinning: 176-bone DEF skeleton + BVH retargeting.
 */
import * as THREE from 'three';
import { state, API } from './state.js';
import { fn } from './registry.js';
import { buildRigifySkeleton } from '../rigify_skeleton_builder.js?v=2';

export async function loadSkinWeights() {
    try {
        const resp = await fetch(`${API}/skin-weights/`);
        if (resp.ok) state.skinWeightData = await resp.json();
    } catch (e) {
        console.warn('Skin weights not available:', e);
    }
}

export async function loadRigifySkeleton() {
    try {
        const resp = await fetch(`${API}/rigify-skeleton/`);
        if (resp.ok) {
            state.rigifySkeletonData = await resp.json();
            console.log(`DEF skeleton loaded: ${state.rigifySkeletonData.bone_count} bones`);
        }
    } catch (e) {
        console.warn('DEF skeleton not available:', e);
    }
}

/**
 * Convert bodyMesh to SkinnedMesh using DEF skeleton.
 */
export function convertToRigifySkinnedMesh(rigifySkel, swData) {
    if (state.isSkinned || !state.bodyMesh || !state.bodyGeometry) return;

    state.bodyGeometry = state.bodyGeometry.clone();

    const vCount = state.bodyGeometry.attributes.position.count;
    const skinIndices = new Float32Array(vCount * 4);
    const skinWeights = new Float32Array(vCount * 4);

    for (let v = 0; v < vCount; v++) {
        const infs = swData.weights[v] || [];
        const sorted = infs.slice().sort((a, b) => b[1] - a[1]).slice(0, 4);
        let sum = sorted.reduce((s, e) => s + e[1], 0);
        if (sum < 1e-6) sum = 1;
        for (let i = 0; i < 4; i++) {
            skinIndices[v * 4 + i] = i < sorted.length ? sorted[i][0] : 0;
            skinWeights[v * 4 + i] = i < sorted.length ? sorted[i][1] / sum : 0;
        }
    }

    state.bodyGeometry.setAttribute('skinIndex',
        new THREE.Float32BufferAttribute(skinIndices, 4));
    state.bodyGeometry.setAttribute('skinWeight',
        new THREE.Float32BufferAttribute(skinWeights, 4));

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
    console.log('SkinnedMesh created:', state.bodyMesh.isSkinnedMesh,
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
