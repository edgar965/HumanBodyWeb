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

// Blender to Three.js coordinate conversion (swap Y/Z, negate new Z)
function blenderToThreeCoords(buf) {
    for (let i = 0; i < buf.length; i += 3) {
        const y = buf[i + 1];
        const z = buf[i + 2];
        buf[i + 1] = z;
        buf[i + 2] = -y;
    }
}

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
 * Load a character from a model preset (body_type + morphs + meta sliders).
 * Also loads hair and garments if present in the preset.
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

    // Load hair if present
    if (preset.hair_style && preset.hair_style.url) {
        try {
            const hairGroup = await loadHairFromURL(preset.hair_style.url);
            hairGroup.userData.isHair = true; // Mark for visibility toggle
            hairGroup.traverse((child) => {
                if (child.isMesh) child.userData.isHair = true;
            });
            group.add(hairGroup); // Add as child of character group
            console.log('✓ Hair loaded:', preset.hair_style.name);
        } catch (err) {
            console.error('Failed to load hair:', err);
        }
    }

    // Load garments if present
    if (preset.garments && Array.isArray(preset.garments)) {
        for (const garmentData of preset.garments) {
            try {
                const garmentMesh = await loadGarmentMesh(garmentData, preset.body_type);
                garmentMesh.userData.isGarment = true; // Mark for visibility toggle
                group.add(garmentMesh); // Add as child of character group
                console.log('✓ Garment loaded:', garmentData.id);
            } catch (err) {
                console.error('Failed to load garment:', garmentData.id, err);
            }
        }
    }

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
 * Load hair from a URL (GLB file).
 * @param {string} url  Hair GLB URL
 * @returns {Promise<THREE.Group>}
 */
async function loadHairFromURL(url) {
    return new Promise((resolve, reject) => {
        gltfLoader.load(
            url,
            (gltf) => {
                const hairGroup = gltf.scene;
                hairGroup.traverse((child) => {
                    if (child.isMesh) {
                        child.castShadow = true;
                        child.receiveShadow = true;

                        // Fix white hair - ensure material has proper color
                        if (child.material) {
                            // If material exists but has wrong color, fix it
                            if (child.material.color) {
                                // Check if color is too bright (white)
                                const color = child.material.color;
                                if (color.r > 0.9 && color.g > 0.9 && color.b > 0.9) {
                                    // Set to dark brown/black hair color
                                    child.material.color.setRGB(0.1, 0.08, 0.06);
                                }
                            }
                            // Ensure PBR properties are set
                            if (child.material.roughness === undefined) child.material.roughness = 0.8;
                            if (child.material.metalness === undefined) child.material.metalness = 0.0;
                        }
                    }
                });
                resolve(hairGroup);
            },
            undefined,
            (err) => reject(err)
        );
    });
}

/**
 * Load a garment mesh from the garment fit API.
 * @param {Object} garmentData  Garment data from preset (id, offset, stiffness, color, etc.)
 * @param {string} bodyType  Current body type
 * @returns {Promise<THREE.Mesh>}
 */
async function loadGarmentMesh(garmentData, bodyType) {
    const { id, offset = 0.006, stiffness = 0.8, color = [0.3, 0.35, 0.5], roughness = 0.8, metalness = 0 } = garmentData;

    const cr = color[0] ?? 0.3;
    const cg = color[1] ?? 0.35;
    const cb = color[2] ?? 0.5;

    const qs = `garment_id=${encodeURIComponent(id)}&body_type=${encodeURIComponent(bodyType)}` +
               `&offset=${offset}&stiffness=${stiffness}` +
               `&color_r=${cr.toFixed(3)}&color_g=${cg.toFixed(3)}&color_b=${cb.toFixed(3)}`;

    const resp = await fetch(`/api/character/garment/fit/?${qs}`);
    if (!resp.ok) throw new Error(`Garment fit API error: ${resp.status}`);
    const data = await resp.json();
    if (data.error) throw new Error(data.error);

    const verts = base64ToFloat32(data.vertices);
    blenderToThreeCoords(verts);
    const faces = base64ToUint32(data.faces);

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(verts, 3));
    geometry.setIndex(new THREE.BufferAttribute(faces, 1));
    geometry.computeVertexNormals();

    const matColor = new THREE.Color(data.color[0], data.color[1], data.color[2]);
    const material = new THREE.MeshStandardMaterial({
        color: matColor,
        roughness: roughness,
        metalness: metalness,
        side: THREE.DoubleSide,
        polygonOffset: true,
        polygonOffsetFactor: -1,
        polygonOffsetUnit: -1,
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;

    return mesh;
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
