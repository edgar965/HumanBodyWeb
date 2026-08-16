import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { getSheet, createMeshSheet } from './theatre-bridge.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords }
    from '../../static/viewer/gemeinsam/kodierung.js';
// Figur, Haare und Kleidung: laden/vorgabefigur.js und laden/kleidungsnetz.js
// (vorher 242 Zeilen hier). Kleidungsnetz wird von dort benutzt, nicht mehr
// direkt aus dieser Datei.
import { Vorgabefigur } from './laden/vorgabefigur.js';
// model_generator.js wurde am 16.08.2026 in modellbau/ zerlegt. Dieser Import
// zeigte danach ins Leere und der Vite-Build brach ab — unbemerkt, weil
// static/theatre/theatre-app.js als altes Ergebnis weiter ausgeliefert wurde.
import { generateRigBoneMesh } from '../../static/viewer/modellbau/rignetz.js';
import { generateModelMesh } from '../../static/viewer/modellbau/modellnetz.js';

const gltfLoader = new GLTFLoader();
const bvhLoader = new BVHLoader();
let _assetCounter = 0;

// Cached skeleton data for generated models (lazy-fetched)
let _cachedRigifySkeleton = null;
let _cachedSkinWeights = null;
let _cachedRigBones = null;

async function _ensureRigifySkeleton() {
    if (!_cachedRigifySkeleton) {
        const r = await fetch('/api/character/rigify-skeleton/');
        if (r.ok) _cachedRigifySkeleton = await r.json();
    }
    return _cachedRigifySkeleton;
}

async function _ensureSkinWeights() {
    if (!_cachedSkinWeights) {
        const r = await fetch('/api/character/skin-weights/');
        if (r.ok) _cachedSkinWeights = await r.json();
    }
    return _cachedSkinWeights;
}

async function _ensureRigBones() {
    if (!_cachedRigBones) {
        const r = await fetch('/api/character/rig/');
        if (r.ok) _cachedRigBones = await r.json();
    }
    return _cachedRigBones;
}

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

// Material definitions (must match result_character.js)
const BODY_MATERIALS = [
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

// Die drei Umsetzfunktionen (base64 -> Float32/Uint32, Blender-Achsen ->
// Three.js) standen hier als ACHTE Kopie im Projekt. Sie liegen seit dem
// 15.08.2026 in static/viewer/gemeinsam/kodierung.js — siehe dort, warum.

/**
 * Build a character mesh from API response data.
 * Uses multi-materials (BODY_MATERIALS) and material groups like result_character.js
 * @param {Object} data API response with vertices, faces, uvs, normals, groups
 * @returns {THREE.Group}
 */
function buildCharacterMesh(data) {
    const verts = base64ToFloat32(data.vertices);
    const faces = base64ToUint32(data.faces);

    // Convert from Blender Z-up to Three.js Y-up
    blenderToThreeCoords(verts);

    const geometry = new THREE.BufferGeometry();
    const positions = new THREE.BufferAttribute(verts, 3);
    const index = new THREE.BufferAttribute(faces, 1);

    geometry.setAttribute('position', positions);
    geometry.setIndex(index);

    if (data.uvs) {
        const uvs = base64ToFloat32(data.uvs);
        geometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
    }

    if (data.normals) {
        const normals = base64ToFloat32(data.normals);
        blenderToThreeCoords(normals);
        geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
    } else {
        geometry.computeVertexNormals();
    }

    // Create material array (11 materials for different body parts)
    const materials = BODY_MATERIALS.map(d => new THREE.MeshStandardMaterial({
        color: d.color,
        roughness: d.roughness,
        metalness: d.metalness,
        side: THREE.DoubleSide,
        transparent: d.transparent || false,
        opacity: d.opacity !== undefined ? d.opacity : 1.0,
    }));

    // Add material groups (assigns material indices to face ranges)
    const groups = data.groups || [];
    let mesh;

    if (index && groups.length > 0) {
        for (const g of groups) {
            geometry.addGroup(g.start, g.count, g.materialIndex);
        }
        mesh = new THREE.Mesh(geometry, materials); // Array of materials!
    } else {
        mesh = new THREE.Mesh(geometry, materials[0]); // Fallback to skin
    }

    mesh.castShadow = true;
    mesh.receiveShadow = true;

    // NO rotation needed - we already converted coordinates with blenderToThreeCoords()

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
 * Build a generated model mesh client-side (no server mesh API needed).
 * Uses model_generator.js functions to create geometry from bone config.
 * @param {Object} config  Generated model config (type: 'generated_model')
 * @returns {Promise<THREE.Group>}
 */
async function buildGeneratedModel(config) {
    const skelType = config.skeleton_type || 'def';
    let result;

    const rigifySkel = await _ensureRigifySkeleton();
    const swData = await _ensureSkinWeights();

    if (skelType === 'rig') {
        const rigData = await _ensureRigBones();
        if (!rigData) throw new Error('Rig bones data not loaded');
        result = generateRigBoneMesh(rigData, config, rigifySkel, swData);
    } else {
        if (!rigifySkel || !swData) throw new Error('Skeleton data not loaded');
        result = generateModelMesh(rigifySkel, swData, config);
    }

    if (!result) throw new Error('No visible bones in generated model config');

    const group = new THREE.Group();
    group.add(result.mesh);
    group.userData.isGeneratedModel = true;

    // If the mesh is a SkinnedMesh, store references for animation system
    if (result.skeleton && result.mesh.isSkinnedMesh) {
        group.userData.isSkinnedMesh = true;
        group.userData.skinnedMesh = result.mesh;
        group.userData.skeleton = result.skeleton.skeleton;
        group.userData.rootBone = result.skeleton.rootBone;
        // Store full rigifySkeleton-compatible object for retarget (boneByName, rootBone, etc.)
        group.userData.rigifySkelObj = result.skeleton;
    }

    return group;
}

/**
 * Figur samt Haaren und Kleidung aus einer Vorgabe laden.
 *
 * Der Rumpf steckt in laden/vorgabefigur.js (vorher 105 Zeilen hier, plus 40
 * fuer das Haarladen). Diese Fassade bleibt, damit die rund zwanzig
 * Aufrufstellen im Projekt unveraendert weiterlaufen.
 */
export async function loadCharacterFromPreset(scene, preset, presetName) {
    const figur = new Vorgabefigur({
        netzBauen: buildCharacterMesh,
        erzeugtesModell: buildGeneratedModel,
        inTheatre: (gruppe, name) => {
            _assetCounter++;
            const sheet = getSheet();
            if (sheet) createMeshSheet(sheet, name || `Character ${_assetCounter}`, gruppe);
        },
    });
    return figur.laden(scene, preset, presetName);
}


/**
 * Load a garment mesh from the garment fit API.
 * @param {Object} garmentData  Garment data from preset (id, offset, stiffness, color, etc.)
 * @param {string} bodyType  Current body type
 * @returns {Promise<THREE.Mesh>}
 */

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
    skeletonHelper.visible = true; // Make visible initially
    skeletonHelper.userData.isRig = true; // Mark as rig for toggle button
    skeletonHelper.renderOrder = 999; // Render AFTER character mesh (on top)

    // Make skeleton always visible (render over character mesh)
    if (skeletonHelper.material) {
        skeletonHelper.material.depthTest = false; // Ignore depth (always visible)
        skeletonHelper.material.depthWrite = false; // Don't write to depth buffer
    }

    // Position bones
    const rootBone = result.skeleton.bones[0];
    rootBone.userData.isRig = true; // Mark root bone as rig too
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
