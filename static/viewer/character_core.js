/**
 * character_core.js — Shared utilities and state for character rendering.
 * Used by both result_character.js and scene_config.js.
 *
 * Exports:
 *   Utilities:  base64ToFloat32, base64ToUint32, blenderToThreeCoords
 *   Hair:       findHeadBoneIndex, skinifyHairGroup, applyHairColor
 *   Skinning:   applySkinWeights (core vertex weight algorithm)
 *   Skin Color: applySkinColorToMaterials
 *   State:      sharedState (skinColors, hairColorData, rigifySkeletonData, skinWeightData)
 *   Loaders:    loadRigifySkeleton, loadSkinWeights, loadSkinColors, loadHairColors
 *   Scene:      createSceneSetup
 *   Constants:  BODY_MATERIALS
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

console.log('[character_core] v1.0 loaded');

// =========================================================================
// Shared state — loaded once, used by both Result and Scene
// =========================================================================
export const sharedState = {
    rigifySkeletonData: null,
    skinWeightData: null,
    skinColors: {},
    hairColorData: {},
};

// =========================================================================
// Constants
// =========================================================================
export const BODY_MATERIALS = [
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },  // 0 Skin
    { color: 0xd4a574, roughness: 0.55, metalness: 0.0 },  // 1 Censor
    { color: 0x111111, roughness: 0.8,  metalness: 0.0 },  // 2 Eyelash
    { color: 0x0a0a0a, roughness: 0.1,  metalness: 0.0 },  // 3 Pupil
    { color: 0xf4f0e8, roughness: 0.2,  metalness: 0.0 },  // 4 Sclera
    { color: 0xf4f0e8, roughness: 0.05, metalness: 0.0, opacity: 0.3, transparent: true },  // 5 Cornea
    { color: 0x4a7a9b, roughness: 0.15, metalness: 0.0 },  // 6 Iris
    { color: 0xb55a6a, roughness: 0.7,  metalness: 0.0 },  // 7 Tongue
    { color: 0xf0ece0, roughness: 0.3,  metalness: 0.0 },  // 8 Teeth
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },  // 9 Nails Hand
    { color: 0xe0a88a, roughness: 0.4,  metalness: 0.0 },  // 10 Nails Feet
];

// =========================================================================
// Base64 / Coordinate Utilities
// =========================================================================

export function base64ToFloat32(b64) {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new Float32Array(bytes.buffer);
}

export function base64ToUint32(b64) {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new Uint32Array(bytes.buffer);
}

export function blenderToThreeCoords(buf) {
    for (let i = 0; i < buf.length; i += 3) {
        const y = buf[i + 1];
        const z = buf[i + 2];
        buf[i + 1] = z;
        buf[i + 2] = -y;
    }
}

// =========================================================================
// Data Loaders (populate sharedState)
// =========================================================================

export async function loadRigifySkeleton() {
    try {
        const resp = await fetch('/api/character/rigify-skeleton/');
        if (resp.ok) {
            sharedState.rigifySkeletonData = await resp.json();
            return true;
        }
    } catch (e) {
        console.warn('[character_core] DEF skeleton not available:', e);
    }
    return false;
}

export async function loadSkinWeights(bodyType) {
    try {
        const url = bodyType
            ? '/api/character/skin-weights/?body_type=' + encodeURIComponent(bodyType)
            : '/api/character/skin-weights/';
        const resp = await fetch(url);
        if (resp.ok) {
            sharedState.skinWeightData = await resp.json();
            return true;
        }
    } catch (e) {
        console.warn('[character_core] Skin weights not available:', e);
    }
    return false;
}

export async function loadSkinColors() {
    try {
        const resp = await fetch('/api/character/morphs/');
        if (resp.ok) {
            const data = await resp.json();
            if (data.skin_colors) {
                sharedState.skinColors = data.skin_colors;
                return true;
            }
        }
    } catch (e) { /* optional */ }
    return false;
}

export async function loadHairColors() {
    try {
        const resp = await fetch('/api/character/hairstyles/');
        if (resp.ok) {
            const data = await resp.json();
            sharedState.hairColorData = data.colors || {};
            return true;
        }
    } catch (e) { /* optional */ }
    return false;
}

// =========================================================================
// Skin Weight Algorithm (shared core)
// =========================================================================

/**
 * Apply skin weights to a BufferGeometry from skinWeightData.
 * Returns {skinIndices, skinWeights} Float32Arrays (vCount * 4 each).
 */
export function computeSkinAttributes(geometry, skinWD) {
    const vCount = geometry.attributes.position.count;
    const skinIndices = new Float32Array(vCount * 4);
    const skinWeights = new Float32Array(vCount * 4);
    for (let v = 0; v < vCount; v++) {
        const infs = skinWD.weights[v] || [];
        const sorted = infs.slice().sort((a, b) => b[1] - a[1]).slice(0, 4);
        let sum = sorted.reduce((s, e) => s + e[1], 0);
        if (sum < 1e-6) sum = 1;
        for (let i = 0; i < 4; i++) {
            skinIndices[v * 4 + i] = i < sorted.length ? sorted[i][0] : 0;
            skinWeights[v * 4 + i] = i < sorted.length ? sorted[i][1] / sum : 0;
        }
    }
    return { skinIndices, skinWeights };
}

// =========================================================================
// Skin Color
// =========================================================================

/**
 * Apply skin color to materials based on body type ethnicity.
 * @param {THREE.Material[]} materials - Array of materials (at least [0] = skin)
 * @param {string} bodyType - e.g. "Female_Caucasian"
 * @param {Object} colors - skinColors map {ethnicity: [r,g,b]}
 */
export function applySkinColorToMaterials(materials, bodyType, colors) {
    if (!colors || !Object.keys(colors).length) return;
    const parts = bodyType.split('_');
    const ethnicity = parts.length > 1 ? parts.slice(1).join('_') : 'Caucasian';
    const rgb = colors[ethnicity] || colors['Caucasian'];
    if (rgb && materials[0]) {
        materials[0].color.setRGB(
            Math.pow(rgb[0], 1 / 2.2),
            Math.pow(rgb[1], 1 / 2.2),
            Math.pow(rgb[2], 1 / 2.2)
        );
        if (materials[1]) {
            materials[1].color.copy(materials[0].color);
        }
    }
}

// =========================================================================
// Hair Helpers
// =========================================================================

/** Find the head bone index in skinWeightData.bone_names. */
export function findHeadBoneIndex(skinWD) {
    if (!skinWD) return -1;
    const names = skinWD.bone_names;
    for (const tryName of ['DEF-spine.006', 'DEF-spine.005', 'DEF-head']) {
        const idx = names.indexOf(tryName);
        if (idx >= 0) return idx;
    }
    return -1;
}

/**
 * Convert a GLTF hair scene to skinned meshes bound to the head bone.
 * @param {THREE.Object3D} gltfScene - The loaded GLTF scene
 * @param {number} headBoneIdx - Index of head bone in skeleton
 * @param {Object} skeleton - {skeleton: THREE.Skeleton} from buildRigifySkeleton
 * @param {THREE.Matrix4} bindMatrix - bodyMesh.bindMatrix
 * @returns {THREE.Group} Group of SkinnedMesh children
 */
export function skinifyHairGroup(gltfScene, headBoneIdx, skeleton, bindMatrix) {
    if (headBoneIdx < 0) return gltfScene;
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
        skinnedChild.bind(skeleton, bindMatrix);
        group.add(skinnedChild);
    }
    return group;
}

/**
 * Apply hair color to all meshes in a hair object.
 * @param {THREE.Object3D} obj - Hair mesh/group
 * @param {string} colorName - Key into hairColorData
 * @param {Object} hairColors - hairColorData map {name: [r,g,b]}
 */
export function applyHairColor(obj, colorName, hairColors) {
    const rgb = hairColors[colorName];
    if (!rgb) return;
    const color = new THREE.Color(rgb[0], rgb[1], rgb[2]);
    obj.traverse(child => {
        if (child.isMesh && child.material) {
            const mats = Array.isArray(child.material) ? child.material : [child.material];
            mats.forEach(m => { m.color.copy(color); });
        }
    });
}

// =========================================================================
// Skinify Mesh (for cloth/garment with server-provided weights)
// =========================================================================

/**
 * Create SkinnedMesh (if skin data available) or plain Mesh.
 * @param {THREE.BufferGeometry} geo
 * @param {THREE.Material} mat
 * @param {Object} skeletonInfo - {skeleton: THREE.Skeleton, bodyMesh: THREE.SkinnedMesh}
 * @param {Object} data - API response with optional skin_indices/skin_weights base64
 * @returns {THREE.Mesh|THREE.SkinnedMesh}
 */
export function skinifyMesh(geo, mat, skeletonInfo, data) {
    if (skeletonInfo && skeletonInfo.skeleton && data.skin_indices && data.skin_weights) {
        const siBuf = base64ToFloat32(data.skin_indices);
        const swBuf = base64ToFloat32(data.skin_weights);
        geo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(siBuf, 4));
        geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(swBuf, 4));
        const mesh = new THREE.SkinnedMesh(geo, mat);
        mesh.bind(skeletonInfo.skeleton, skeletonInfo.bindMatrix);
        return mesh;
    }
    return new THREE.Mesh(geo, mat);
}

// =========================================================================
// Scene Setup Helper
// =========================================================================

/**
 * Create standard scene setup (renderer, scene, camera, controls, lights, grid).
 * @param {HTMLCanvasElement} canvas
 * @returns {Object} {renderer, scene, camera, controls, keyLight, fillLight, backLight, ambient, grid}
 */
export function createSceneSetup(canvas) {
    const w = canvas.clientWidth || canvas.width;
    const h = canvas.clientHeight || canvas.height;

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h, false);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.6;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);

    const camera = new THREE.PerspectiveCamera(35, w / h, 0.01, 100);
    camera.position.set(0, 1.0, 3.5);

    const controls = new OrbitControls(camera, canvas);
    controls.target.set(0, 0.9, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 0.5;
    controls.maxDistance = 15;
    controls.update();

    const keyLight = new THREE.DirectionalLight(0xffffff, 3.0);
    keyLight.position.set(2, 4, -5);
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0xeeeeff, 2.0);
    fillLight.position.set(-3, 3, -4);
    scene.add(fillLight);

    const backLight = new THREE.DirectionalLight(0xffeedd, 2.5);
    backLight.position.set(0, 4, 5);
    scene.add(backLight);

    const ambient = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambient);

    const grid = new THREE.GridHelper(4, 20, 0x333355, 0x222244);
    scene.add(grid);

    return { renderer, scene, camera, controls, keyLight, fillLight, backLight, ambient, grid };
}
