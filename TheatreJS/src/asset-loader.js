import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { getSheet, createMeshSheet } from './theatre-bridge.js';

const gltfLoader = new GLTFLoader();
const bvhLoader = new BVHLoader();
let _assetCounter = 0;

/**
 * Load a GLB file from a URL and add it to the scene.
 * Registers the loaded group as a Theatre object for animation.
 * @param {string} url
 * @param {THREE.Scene} scene
 * @returns {Promise<THREE.Group>}
 */
export async function loadGLBAsset(url, scene) {
    return new Promise((resolve, reject) => {
        gltfLoader.load(
            url,
            (gltf) => {
                const group = gltf.scene;
                scene.add(group);

                // Enable shadows on all meshes
                group.traverse((child) => {
                    if (child.isMesh) {
                        child.castShadow = true;
                        child.receiveShadow = true;
                    }
                });

                // Register in Theatre
                _assetCounter++;
                const name = `Asset ${_assetCounter}`;
                const sheet = getSheet();
                if (sheet) {
                    createMeshSheet(sheet, name, group);
                }

                resolve(group);
            },
            undefined,
            (err) => reject(err)
        );
    });
}

/**
 * Load a GLB from a local file (File object from input element).
 * @param {File} file
 * @param {THREE.Scene} scene
 * @returns {Promise<THREE.Group>}
 */
export async function loadGLBFromFile(file, scene) {
    const url = URL.createObjectURL(file);
    try {
        const group = await loadGLBAsset(url, scene);
        return group;
    } finally {
        URL.revokeObjectURL(url);
    }
}

// Decode base64 to Float32Array
function base64ToFloat32(b64) {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new Float32Array(bytes.buffer);
}

// Decode base64 to Uint32Array
function base64ToUint32(b64) {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new Uint32Array(bytes.buffer);
}

/**
 * Build a character mesh from API response data.
 * @param {Object} data API response with vertices, faces, uvs, normals
 * @returns {THREE.Group}
 */
function buildCharacterMesh(data) {
    const verts = base64ToFloat32(data.vertices);
    const faces = base64ToUint32(data.faces);

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(verts, 3));
    geometry.setIndex(new THREE.BufferAttribute(faces, 1));

    if (data.uvs) {
        const uvs = base64ToFloat32(data.uvs);
        geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
    }

    if (data.normals) {
        const normals = base64ToFloat32(data.normals);
        geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
    } else {
        geometry.computeVertexNormals();
    }

    const material = new THREE.MeshStandardMaterial({
        color: 0xd4a574,
        roughness: 0.7,
        metalness: 0.0,
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;

    // Blender uses Z-up, Three.js uses Y-up
    // Rotate -90° around X to convert Z-up to Y-up
    mesh.rotation.x = -Math.PI / 2;

    const group = new THREE.Group();
    group.add(mesh);
    return group;
}

/**
 * Load the HumanBody character via the Django API (default params).
 * @param {THREE.Scene} scene
 * @returns {Promise<THREE.Group>}
 */
export async function loadCharacterModel(scene) {
    const resp = await fetch('/api/character/mesh/');
    if (!resp.ok) throw new Error(`Character mesh API error: ${resp.status}`);
    const data = await resp.json();

    const group = buildCharacterMesh(data);
    scene.add(group);

    // Register in Theatre
    _assetCounter++;
    const sheet = getSheet();
    if (sheet) {
        createMeshSheet(sheet, 'Character', group);
    }

    return group;
}

/**
 * Load a character from a model preset (body_type + morphs + meta sliders).
 * @param {THREE.Scene} scene
 * @param {Object} preset  Preset JSON from /api/character/model/<name>/
 * @param {string} presetName  Display name for the Theatre object
 * @returns {Promise<THREE.Group>}
 */
export async function loadCharacterFromPreset(scene, preset, presetName) {
    // Build query string from preset data
    const params = new URLSearchParams();

    if (preset.body_type) {
        params.set('body_type', preset.body_type);
    }

    // Morph values: morph_<name>=<value>
    if (preset.morphs && typeof preset.morphs === 'object') {
        for (const [key, val] of Object.entries(preset.morphs)) {
            if (val !== undefined && val !== null) {
                params.set(`morph_${key}`, String(val));
            }
        }
    }

    // User morphs override
    if (preset.user_morphs && typeof preset.user_morphs === 'object') {
        for (const [key, val] of Object.entries(preset.user_morphs)) {
            if (val !== undefined && val !== null) {
                params.set(`morph_${key}`, String(val));
            }
        }
    }

    // Meta sliders: meta_<name>=<value>
    // Presets store meta as nested object: { meta: { age: 0, mass: 0, ... } }
    const metaKeys = ['age', 'mass', 'tone', 'height'];
    const metaObj = preset.meta || {};
    for (const mk of metaKeys) {
        const val = metaObj[mk] ?? preset[`meta_${mk}`];
        if (val !== undefined && val !== null) {
            params.set(`meta_${mk}`, String(val));
        }
    }

    const url = `/api/character/mesh/?${params.toString()}`;
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`Character mesh API error: ${resp.status}`);
    const data = await resp.json();

    const group = buildCharacterMesh(data);
    scene.add(group);

    // Register in Theatre
    _assetCounter++;
    const name = presetName || `Character ${_assetCounter}`;
    const sheet = getSheet();
    if (sheet) {
        createMeshSheet(sheet, name, group);
    }

    return group;
}

/**
 * Parse BVH text and create a SkeletonHelper + AnimationMixer.
 * @param {string} bvhText  Raw BVH file content
 * @param {THREE.Scene} scene
 * @param {string} animName  Display name
 * @returns {{ mixer: THREE.AnimationMixer, skeleton: THREE.SkeletonHelper, clip: THREE.AnimationClip }}
 */
export function loadBVHFromText(bvhText, scene, animName) {
    const result = bvhLoader.parse(bvhText);

    // Create skeleton helper
    const skeletonHelper = new THREE.SkeletonHelper(result.skeleton.bones[0]);
    skeletonHelper.skeleton = result.skeleton;

    // Position bones
    const rootBone = result.skeleton.bones[0];
    scene.add(rootBone);
    scene.add(skeletonHelper);

    // AnimationMixer on the root bone
    const mixer = new THREE.AnimationMixer(rootBone);
    const action = mixer.clipAction(result.clip);
    action.setLoop(THREE.LoopRepeat);
    action.play();
    action.paused = true; // Start paused for player control

    // Register root bone in Theatre
    _assetCounter++;
    const sheet = getSheet();
    if (sheet) {
        createMeshSheet(sheet, animName || `BVH ${_assetCounter}`, rootBone);
    }

    const duration = result.clip.duration || 1;
    return { mixer, action, skeleton: skeletonHelper, clip: result.clip, rootBone, duration };
}
