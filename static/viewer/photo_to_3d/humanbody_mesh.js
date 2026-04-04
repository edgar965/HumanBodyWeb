/**
 * Photo To 3D — HumanBody mesh loading, DEF skeleton, skin color.
 */
import * as THREE from 'three';
import { state, API, MODEL_OFFSET_X } from './state.js';
import { fn } from './registry.js';
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
    const parts = bodyType.split('_');
    const ethnicity = parts[1] || parts[0];
    const colors = state.skinColors[ethnicity];
    if (colors) {
        mat.color.setRGB(
            Math.pow(colors[0], 1 / 2.2),
            Math.pow(colors[1], 1 / 2.2),
            Math.pow(colors[2], 1 / 2.2)
        );
        const picker = document.getElementById('skin-color-viewer');
        if (picker) picker.value = '#' + mat.color.getHexString();
    }
}

// =========================================================================
// HumanBody mesh loading (shifted left)
// =========================================================================
export async function loadMesh(bodyType) {
    bodyType = bodyType || state.currentBodyType;
    let url = `${API}/mesh/?body_type=${encodeURIComponent(bodyType)}`;
    for (const [k, v] of Object.entries(state.morphValues)) {
        if (Math.abs(v) > 0.001) url += `&morph_${k}=${v}`;
    }
    for (const [k, v] of Object.entries(state.metaValues)) {
        if (Math.abs(v) > 0.001) url += `&meta_${k}=${v}`;
    }

    try {
        const resp = await fetch(url);
        const data = await resp.json();
        if (data.error) { console.error(data.error); return; }

        if (state.bodyMesh) {
            if (state.bodyMesh.isSkinnedMesh && state.rigifySkeleton && state.rigifySkeleton.rootBone) {
                state.bodyMesh.remove(state.rigifySkeleton.rootBone);
            }
            state.scene.remove(state.bodyMesh);
            state.bodyMesh.geometry?.dispose();
            state.bodyMesh = null;
            state.bodyGeometry = null;
        }

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);

        let normalBuf = null;
        if (data.normals) {
            normalBuf = base64ToFloat32(data.normals);
            blenderToThreeCoords(normalBuf);
        }

        alignBodyToSMPLX(vertBuf);

        let index = null;
        if (data.faces) index = new THREE.BufferAttribute(base64ToUint32(data.faces), 1);
        let uvAttr = null;
        if (data.uvs) uvAttr = new THREE.BufferAttribute(base64ToFloat32(data.uvs), 2);

        const materials = BODY_MATERIALS.map(d => new THREE.MeshStandardMaterial({
            color: d.color, roughness: d.roughness, metalness: d.metalness,
            side: THREE.DoubleSide,
            transparent: d.transparent || false,
            opacity: d.opacity !== undefined ? d.opacity : 1.0,
        }));

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        if (index) geo.setIndex(index);
        if (uvAttr) geo.setAttribute('uv', uvAttr);

        if (normalBuf) {
            geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        } else {
            geo.computeVertexNormals();
        }

        const groups = data.groups || [];
        if (index && groups.length > 0) {
            for (const g of groups) geo.addGroup(g.start, g.count, g.materialIndex);
        }
        const mat = (index && groups.length > 0) ? materials : materials[0];

        // Create SkinnedMesh if skeleton + weights available, else regular Mesh
        if (state.rigifySkeleton && state.skinWeightData && state.skinWeightData.weights) {
            const vertCount = geo.attributes.position.count;
            const skinIndices = new Uint16Array(vertCount * 4);
            const skinWeights = new Float32Array(vertCount * 4);

            const skelBoneNames = state.skinWeightData.bone_names;
            const swToBoneIdx = {};
            for (let si = 0; si < skelBoneNames.length; si++) {
                const idx = state.rigifySkeleton.bones.indexOf(state.rigifySkeleton.boneByName[skelBoneNames[si]]);
                if (idx >= 0) swToBoneIdx[si] = idx;
            }

            for (let vi = 0; vi < Math.min(vertCount, state.skinWeightData.weights.length); vi++) {
                const pairs = state.skinWeightData.weights[vi];
                for (let j = 0; j < Math.min(pairs.length, 4); j++) {
                    const boneIdx = swToBoneIdx[pairs[j][0]];
                    skinIndices[vi * 4 + j] = boneIdx !== undefined ? boneIdx : 0;
                    skinWeights[vi * 4 + j] = boneIdx !== undefined ? pairs[j][1] : 0;
                }
            }
            geo.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(skinIndices, 4));
            geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeights, 4));

            state.bodyMesh = new THREE.SkinnedMesh(geo, mat);
            const skeleton = new THREE.Skeleton(state.rigifySkeleton.bones);
            state.bodyMesh.add(state.rigifySkeleton.rootBone);

            const headBone = state.rigifySkeleton.boneByName['DEF-spine.006'];
            if (headBone) {
                if (headBone._origY === undefined) headBone._origY = headBone.position.y;
                if (headBone._origZ === undefined) headBone._origZ = headBone.position.z;
                headBone.position.y = headBone._origY;
                headBone.position.z = headBone._origZ;
                state.rigifySkeleton.rootBone.updateWorldMatrix(true, true);
            }

            state.bodyMesh.bind(skeleton);
        } else {
            state.bodyMesh = new THREE.Mesh(geo, mat);
        }

        state.bodyMesh.position.x = MODEL_OFFSET_X;
        state.bodyGeometry = geo;
        state.scene.add(state.bodyMesh);

        const vcEl = document.getElementById('vertex-count');
        if (vcEl) vcEl.textContent = geo.attributes.position.count.toLocaleString();

        applySkinColor(bodyType);
    } catch (e) {
        console.error('Failed to load mesh:', e);
    }
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
    } catch (e) { console.warn('DEF skeleton not available:', e); }
    try {
        const resp = await fetch(`${API}/skin-weights/?body_type=${encodeURIComponent(bodyType)}`);
        if (resp.ok) state.skinWeightData = await resp.json();
    } catch (e) { console.warn('Skin weights not available:', e); }
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
