/**
 * Scene Editor -- Skeleton/Skinning helpers.
 * DEF Skeleton + Skin Weights + BVH skinning utilities.
 */
import { THREE, buildRigifySkeleton } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';
import { base64ToFloat32 } from './utils.js';

export async function loadRigifySkeleton() {
    try {
        const resp = await fetch('/api/character/rigify-skeleton/');
        if (resp.ok) state.rigifySkeletonData = await resp.json();
    } catch (e) { /* optional */ }
}

export async function loadSkinWeights() {
    try {
        const resp = await fetch('/api/character/skin-weights/');
        if (resp.ok) state.skinWeightData = await resp.json();
    } catch (e) { /* optional */ }
}

export function convertToRigifySkinnedMesh() {
    if (state.isSkinned || !state.bodyMesh || !state.bodyGeometry || !state.skinWeightData) return;
    state.bodyGeometry = state.bodyGeometry.clone();
    const vCount = state.bodyGeometry.attributes.position.count;
    const skinIndices = new Float32Array(vCount * 4);
    const skinWeights = new Float32Array(vCount * 4);
    for (let v = 0; v < vCount; v++) {
        const infs = state.skinWeightData.weights[v] || [];
        const sorted = infs.slice().sort((a, b) => b[1] - a[1]).slice(0, 4);
        let sum = sorted.reduce((s, e) => s + e[1], 0);
        if (sum < 1e-6) sum = 1;
        for (let i = 0; i < 4; i++) {
            skinIndices[v * 4 + i] = i < sorted.length ? sorted[i][0] : 0;
            skinWeights[v * 4 + i] = i < sorted.length ? sorted[i][1] / sum : 0;
        }
    }
    state.bodyGeometry.setAttribute('skinIndex', new THREE.Float32BufferAttribute(skinIndices, 4));
    state.bodyGeometry.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeights, 4));
    state.rigifySkeleton = buildRigifySkeleton(state.rigifySkeletonData, state.skinWeightData);
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
}

/** Convert a CharacterInstance body to SkinnedMesh for animation. */
export function convertInstToSkinned(inst) {
    if (inst.isSkinned || !inst.bodyMesh || !state.skinWeightData || !state.rigifySkeletonData) return;
    if (inst.generatedConfig) return;
    const geo = inst.bodyMesh.geometry.clone();
    const vCount = geo.attributes.position.count;
    const skinIndices = new Float32Array(vCount * 4);
    const skinWeights = new Float32Array(vCount * 4);
    for (let v = 0; v < vCount; v++) {
        const infs = state.skinWeightData.weights[v] || [];
        const sorted = infs.slice().sort((a, b) => b[1] - a[1]).slice(0, 4);
        let sum = sorted.reduce((s, e) => s + e[1], 0);
        if (sum < 1e-6) sum = 1;
        for (let i = 0; i < 4; i++) {
            skinIndices[v * 4 + i] = i < sorted.length ? sorted[i][0] : 0;
            skinWeights[v * 4 + i] = i < sorted.length ? sorted[i][1] / sum : 0;
        }
    }
    geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(skinIndices, 4));
    geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeights, 4));
    inst.rigifySkeleton = buildRigifySkeleton(state.rigifySkeletonData, state.skinWeightData);
    const mat = inst.bodyMesh.material;
    const vis = inst.bodyMesh.visible;
    inst.group.remove(inst.bodyMesh);
    inst.bodyMesh = new THREE.SkinnedMesh(geo, mat);
    inst.bodyMesh.visible = vis;
    inst.bodyMesh.add(inst.rigifySkeleton.rootBone);
    inst.bodyMesh.bind(inst.rigifySkeleton.skeleton);
    inst.group.add(inst.bodyMesh);
    inst.isSkinned = true;

    if (inst.hairMesh) {
        inst.group.remove(inst.hairMesh);
        inst._loadHair();
    }
}

/**
 * Create SkinnedMesh (if skin data available) or plain Mesh.
 */
export function _skinifyMesh(geo, mat, inst, data) {
    if (inst.isSkinned && inst.rigifySkeleton && data.skin_indices && data.skin_weights) {
        const siBuf = base64ToFloat32(data.skin_indices);
        const swBuf = base64ToFloat32(data.skin_weights);
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
        const mesh = new THREE.SkinnedMesh(geo, mat);
        mesh.bind(inst.rigifySkeleton.skeleton, inst.bodyMesh.bindMatrix);
        return mesh;
    }
    return new THREE.Mesh(geo, mat);
}

/** Find the head bone index in skinWeightData.bone_names. */
export function _findHeadBoneIndex() {
    if (!state.skinWeightData) return -1;
    const names = state.skinWeightData.bone_names;
    for (const tryName of ['DEF-spine.006', 'DEF-spine.005', 'DEF-head']) {
        const idx = names.indexOf(tryName);
        if (idx >= 0) return idx;
    }
    return -1;
}

/**
 * Convert all meshes in a GLTF scene (hair) to SkinnedMesh bound to head bone.
 */
export function _skinifyHairGroup(gltfScene, inst) {
    const headBoneIdx = _findHeadBoneIndex();
    if (headBoneIdx < 0 || !inst.isSkinned || !inst.rigifySkeleton) return gltfScene;

    const meshChildren = [];
    gltfScene.traverse(child => {
        if (child.isMesh) meshChildren.push(child);
    });

    const group = new THREE.Group();
    for (const child of meshChildren) {
        const geo = child.geometry.clone();
        const vCount = geo.attributes.position.count;
        const si = new Float32Array(vCount * 4);
        const sw = new Float32Array(vCount * 4);
        for (let v = 0; v < vCount; v++) {
            si[v * 4] = headBoneIdx;
            sw[v * 4] = 1.0;
        }
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(si, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4));

        const skinnedChild = new THREE.SkinnedMesh(geo, child.material);
        child.updateWorldMatrix(true, false);
        skinnedChild.applyMatrix4(child.matrixWorld);
        skinnedChild.bind(inst.rigifySkeleton.skeleton, inst.bodyMesh.bindMatrix);
        group.add(skinnedChild);
    }
    return group;
}

// Register
fn.loadRigifySkeleton = loadRigifySkeleton;
fn.loadSkinWeights = loadSkinWeights;
fn.convertToRigifySkinnedMesh = convertToRigifySkinnedMesh;
fn.convertInstToSkinned = convertInstToSkinned;
fn._skinifyMesh = _skinifyMesh;
fn._skinifyHairGroup = _skinifyHairGroup;
