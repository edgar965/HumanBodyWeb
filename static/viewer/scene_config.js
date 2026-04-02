/**
 * HumanBody Scene Editor — Multi-character composition with TransformControls.
 * Phase 1: Load characters from presets, position/rotate/scale with gizmos,
 * save/load scene files. Lighting/Renderer/Camera controls remain.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { detectBVHFormat, fetchRetargetedClipFromUrl, fetchRetargetedClipFromText } from './retarget_hybrid.js?v=32';
import { buildRigifySkeleton } from './rigify_skeleton_builder.js?v=2';
import { classifyBones, getDefaultModelConfig, computeBoneWorldTransforms, generateModelMesh, classifyRigBones, getDefaultRigConfig, generateRigBoneMesh, BODY_BONES, FINGER_BONES } from './model_generator.js';

const gltfLoader = new GLTFLoader();

// GLOBAL Ctrl+M Undo handler — registered at module load, capture phase
// Uses late-binding via window.__ because sceneUndo/Redo are defined later in the file
window.addEventListener('keydown', (e) => {
    if (!e.ctrlKey) return;
    if (e.code === 'KeyM' && !e.shiftKey) {
        e.preventDefault();
        e.stopImmediatePropagation();
        if (typeof sceneUndo === 'function') sceneUndo();
    } else if (e.code === 'KeyM' && e.shiftKey) {
        e.preventDefault();
        e.stopImmediatePropagation();
        if (typeof sceneRedo === 'function') sceneRedo();
    }
}, true);

// =========================================================================
// Light Presets
// =========================================================================
const LIGHT_PRESETS = {
    studio: {
        key:     { intensity: 3.0, color: 0xffffff, pos: [2, 4, -5] },
        fill:    { intensity: 2.0, color: 0xeeeeff, pos: [-3, 3, -4] },
        back:    { intensity: 2.5, color: 0xffeedd, pos: [0, 4, 5] },
        ambient: { intensity: 0.8, color: 0xffffff },
        exposure: 1.6
    },
    outdoor: {
        key:     { intensity: 4.0, color: 0xfff5e0, pos: [5, 8, -2] },
        fill:    { intensity: 1.5, color: 0x8899cc, pos: [-4, 2, -3] },
        back:    { intensity: 1.0, color: 0xffeedd, pos: [-2, 3, 4] },
        ambient: { intensity: 1.2, color: 0xddeeff },
        exposure: 1.8
    },
    dramatic: {
        key:     { intensity: 4.5, color: 0xffddaa, pos: [4, 3, -3] },
        fill:    { intensity: 0.5, color: 0x4444aa, pos: [-3, 1, -2] },
        back:    { intensity: 3.0, color: 0xff8844, pos: [0, 3, 5] },
        ambient: { intensity: 0.3, color: 0x222244 },
        exposure: 1.4
    },
    neutral: {
        key:     { intensity: 2.5, color: 0xffffff, pos: [3, 5, -4] },
        fill:    { intensity: 2.5, color: 0xffffff, pos: [-3, 5, -4] },
        back:    { intensity: 2.0, color: 0xffffff, pos: [0, 4, 5] },
        ambient: { intensity: 1.0, color: 0xffffff },
        exposure: 1.6
    }
};

const TONE_MAPPINGS = {
    ACESFilmic: THREE.ACESFilmicToneMapping,
    Linear:     THREE.LinearToneMapping,
    Reinhard:   THREE.ReinhardToneMapping,
    Cineon:     THREE.CineonToneMapping,
    None:       THREE.NoToneMapping
};

// =========================================================================
// Body materials (same as before)
// =========================================================================
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

// =========================================================================
// Global state
// =========================================================================
let scene, camera, renderer, controls, canvas;
let clock = new THREE.Clock();
let frameCount = 0;
let fpsAccum = 0;

// Lights
let keyLight, fillLight, backLight, ambientLight;

// Legacy single mesh (kept for default preview, removed when using characters)
let bodyMesh = null;
let bodyGeometry = null;

// Animation
let mixer = null;
let currentAction = null;
let skeletonHelper = null;
let playing = false;
const bvhLoader = new BVHLoader();
let rigifySkeletonData = null;
let skinWeightData = null;
let rigifySkeleton = null;
let isSkinned = false;
let skelWrapper = null;
let _animatedCharId = null;  // which character is currently animated
let rigVisible = false;
let modelVisible = true;
let clothesVisible = true;

// Skin colors + hair colors
let skinColors = {};
let hairColorData = {};  // name -> [r, g, b] (linear sRGB)

// Auto-save debounce
let saveTimer = null;

// Properties panel state
let morphDefs = null;           // Cached response from /api/character/morphs/
let currentPropsCharId = null;  // Which character's properties are displayed
let reloadTimer = null;         // Debounce for reloadCharacterMesh

// Asset panel cached data
let _garmentCatalog = [];       // Array of garment entries from library API
let _selectedGarmentId = null;  // Currently selected garment in list
let _hairStylesData = [];       // Array of { url, label, name }
let _clothRegionsData = null;   // { templates, builder_regions, primitives }
let currentAnimName = '';
let currentAnimDuration = 0;
let currentAnimUrl = '';              // URL der geladenen BVH
let currentAnimBvhText = '';          // Roher BVH-Text (original oder modifiziert)
let currentAnimGroundFixed = false;   // Ob Bodenniveau-Fix angewendet
let _sceneDeltaNorm = undefined;       // undefined=auto

// =========================================================================
// Scene Editor State
// =========================================================================
const characters = new Map();       // id -> CharacterInstance
let selectedCharacterId = null;
let transformControls = null;
let currentTransformMode = 'translate';
let transformHelper = null;       // TransformControls visual helper (Object3D)
let transformDragging = false;    // Track whether gizmo is being dragged
let currentSceneName = '';
let defaultPresetName = 'femaleWithClothes';
let _defaultAnimUrl = '';            // From settings: auto-load animation
let _sceneDirty = false;  // Track unsaved changes
const SESSION_KEY = 'humanbody_scene_session';

// Raycasting
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let mouseDownPos = null;
const CLICK_THRESHOLD = 3; // px

// Sub-mesh selection (cloth/hair hover + select)
let _hoveredSubMesh = null;   // { type, key, label, meshObj, charId }
let _selectedSubMesh = null;  // same shape
let _HOVER_EMISSIVE = new THREE.Color(0x08081a);
let _SELECT_EMISSIVE = new THREE.Color(0x12123a);
const _ZERO_EMISSIVE = new THREE.Color(0x000000);
let _hoverPending = false;
let _lastMouseEvent = null;

// Bone selection (3D overlay) for generated models
let _hoveredBoneName = null;
let _selectedBoneName = null;
let _boneHighlightCache = new Map();  // boneName -> BufferGeometry
let _boneHoverOverlay = null;         // current hover overlay mesh
let _boneSelectOverlay = null;        // current selection overlay mesh
const _BONE_HOVER_MAT = new THREE.MeshBasicMaterial({
    color: 0xaaccff, transparent: true, opacity: 0.55,
    depthTest: true, depthWrite: false, side: THREE.DoubleSide,
});
const _BONE_SELECT_MAT = new THREE.MeshBasicMaterial({
    color: 0x4466ff, transparent: true, opacity: 0.35,
    depthTest: true, depthWrite: false, side: THREE.DoubleSide,
});

// =========================================================================
// CharacterInstance
// =========================================================================
class CharacterInstance {
    constructor(id, presetData) {
        this.id = id;
        this.presetName = presetData.name || presetData.label || 'Unnamed';
        this.bodyType = presetData.body_type || 'Female_Caucasian';
        this.morphs = presetData.morphs || {};
        this.meta = presetData.meta || {};
        this.cloth = presetData.cloth || [];
        this.hairStyle = presetData.hair_style || null;
        this.garments = presetData.garments || [];
        this.group = new THREE.Group();
        this.group.userData.characterId = id;
        this.bodyMesh = null;
        this.clothMeshes = {};  // key -> THREE.Mesh
        this.garmentState = {}; // key -> {offset, stiffness, color, roughness, metalness, regionTop, ...}
        this.garmentOrigPositions = {};  // key -> Float32Array
        this.garmentRegionWeights = {};  // key -> { top: Float32Array, ... }
        this.hairMesh = null;   // THREE.Group from GLB
        this.initialBodyTop = 0; // max Y at first load, for hair scaling
        this.selected = false;
        this.isSkinned = false;
        this.rigifySkeleton = null;
        this.generatedConfig = presetData.type === 'generated_model' ? presetData : null;
    }

    async load() {
        // Generated model: build mesh client-side from config
        if (this.generatedConfig) {
            return this._loadGeneratedModel();
        }

        // Build query string
        const params = new URLSearchParams();
        params.set('body_type', this.bodyType);
        for (const [k, v] of Object.entries(this.morphs)) {
            if (v !== 0) params.set(`morph_${k}`, v);
        }
        for (const [k, v] of Object.entries(this.meta)) {
            if (v !== 0) params.set(`meta_${k}`, v);
        }

        const resp = await fetch(`/api/character/mesh/?${params}`);
        const data = await resp.json();
        if (data.error) throw new Error(data.error);

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const positions = new THREE.BufferAttribute(vertBuf, 3);

        let index = null;
        if (data.faces) {
            index = new THREE.BufferAttribute(base64ToUint32(data.faces), 1);
        }

        let uvAttr = null;
        if (data.uvs) {
            uvAttr = new THREE.BufferAttribute(base64ToFloat32(data.uvs), 2);
        }

        const materials = BODY_MATERIALS.map(d => new THREE.MeshStandardMaterial({
            color: d.color, roughness: d.roughness, metalness: d.metalness,
            side: THREE.DoubleSide,
            transparent: d.transparent || false,
            opacity: d.opacity !== undefined ? d.opacity : 1.0,
        }));

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', positions);
        if (index) geo.setIndex(index);
        if (uvAttr) geo.setAttribute('uv', uvAttr);

        if (data.normals) {
            const normalBuf = base64ToFloat32(data.normals);
            blenderToThreeCoords(normalBuf);
            geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        } else {
            geo.computeVertexNormals();
        }

        const groups = data.groups || [];
        if (index && groups.length > 0) {
            for (const g of groups) {
                geo.addGroup(g.start, g.count, g.materialIndex);
            }
            this.bodyMesh = new THREE.Mesh(geo, materials);
        } else {
            this.bodyMesh = new THREE.Mesh(geo, materials[0]);
        }

        // Apply skin color
        this._applySkinColor(materials);

        this.group.add(this.bodyMesh);

        // Record initial body top for hair scaling
        this.initialBodyTop = _getBodyTop(this);

        // Load cloth pieces
        await this._loadCloth();

        // Load hair
        await this._loadHair();

        // Load fitted garments (MH garments from the garment library)
        await this._loadGarments();

        return this;
    }

    async reloadBody() {
        // Fast path: update body mesh geometry in-place (positions + normals)
        // without replacing the mesh or reloading cloth/hair/garments.
        const params = new URLSearchParams();
        params.set('body_type', this.bodyType);
        for (const [k, v] of Object.entries(this.morphs)) {
            if (v !== 0) params.set(`morph_${k}`, v);
        }
        for (const [k, v] of Object.entries(this.meta)) {
            if (v !== 0) params.set(`meta_${k}`, v);
        }

        const resp = await fetch(`/api/character/mesh/?${params}`);
        const data = await resp.json();
        if (data.error) throw new Error(data.error);

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);

        if (this.bodyMesh && this.bodyMesh.geometry.attributes.position.count === vertBuf.length / 3) {
            // Same vertex count — update geometry in place
            this.bodyMesh.geometry.attributes.position.array.set(vertBuf);
            this.bodyMesh.geometry.attributes.position.needsUpdate = true;

            if (data.normals) {
                const normalBuf = base64ToFloat32(data.normals);
                blenderToThreeCoords(normalBuf);
                if (this.bodyMesh.geometry.attributes.normal) {
                    this.bodyMesh.geometry.attributes.normal.array.set(normalBuf);
                    this.bodyMesh.geometry.attributes.normal.needsUpdate = true;
                }
            } else {
                this.bodyMesh.geometry.computeVertexNormals();
            }

            this.bodyMesh.geometry.computeBoundingSphere();
            this.bodyMesh.geometry.computeBoundingBox();
        } else {
            // Vertex count changed (body type switch) — full mesh replacement
            if (this.bodyMesh) {
                this.group.remove(this.bodyMesh);
                this.bodyMesh.geometry.dispose();
                const mats = Array.isArray(this.bodyMesh.material)
                    ? this.bodyMesh.material : [this.bodyMesh.material];
                mats.forEach(m => m.dispose());
                this.bodyMesh = null;
            }
            await this.load();
        }
    }

    async _loadGeneratedModel() {
        const skelType = this.generatedConfig.skeleton_type || 'def';
        let result;

        if (skelType === 'rig') {
            if (!_mgRigBonesData) {
                const r = await fetch('/api/character/rig/');
                if (r.ok) _mgRigBonesData = await r.json();
            }
            if (!_mgRigBonesData) {
                throw new Error('Rig bones data not loaded — cannot build generated model');
            }
            result = generateRigBoneMesh(_mgRigBonesData, this.generatedConfig, rigifySkeletonData, skinWeightData);

            // Use the mesh's own skeleton (same as 'def' path and _mgUpdateModelDisplay)
            // so SkeletonHelper and retarget operate on the SAME bones the mixer animates
            if (result.skeleton) {
                this.rigifySkeleton = result.skeleton;
                this.isSkinned = true;
            }
        } else {
            if (!rigifySkeletonData || !skinWeightData) {
                throw new Error('Skeleton data not loaded — cannot build generated model');
            }
            result = generateModelMesh(rigifySkeletonData, skinWeightData, this.generatedConfig);

            if (result.skeleton) {
                this.rigifySkeleton = result.skeleton;
                this.isSkinned = true;
            }
        }

        if (!result) throw new Error('No visible bones in generated model config');

        this.bodyMesh = result.mesh;
        this.group.add(this.bodyMesh);

        return this;
    }

    _applySkinColor(materials) {
        if (!Object.keys(skinColors).length) return;
        // Extract ethnicity from body_type (e.g. "Female_Caucasian" -> "Caucasian")
        const parts = this.bodyType.split('_');
        const ethnicity = parts.length > 1 ? parts.slice(1).join('_') : 'Caucasian';
        const colors = skinColors[ethnicity] || skinColors['Caucasian'];
        if (colors && materials[0]) {
            materials[0].color.setRGB(
                Math.pow(colors[0], 1/2.2),
                Math.pow(colors[1], 1/2.2),
                Math.pow(colors[2], 1/2.2)
            );
            // Also set Censor material (index 1) to same skin color
            if (materials[1]) {
                materials[1].color.copy(materials[0].color);
            }
        }
    }

    async _loadCloth() {
        // Remove old cloth meshes
        for (const [key, mesh] of Object.entries(this.clothMeshes)) {
            this.group.remove(mesh);
            mesh.geometry.dispose();
            mesh.material.dispose();
        }
        this.clothMeshes = {};

        if (!this.cloth || this.cloth.length === 0) return;

        const isMale = this.bodyType.startsWith('Male_');
        if (isMale) return; // Cloth templates designed for female bodies

        // Auto-skin character if skeleton data is available
        if (!this.isSkinned && rigifySkeletonData && skinWeightData) {
            convertInstToSkinned(this);
        }

        for (const c of this.cloth) {
            try {
                const method = c.method || 'template';
                const params = new URLSearchParams();
                params.set('method', method);
                params.set('body_type', this.bodyType);

                let key;
                if (method === 'builder') {
                    params.set('region', c.region || 'TOP');
                    params.set('looseness', c.looseness !== undefined ? c.looseness : 0.5);
                    key = `bld_${c.region || 'TOP'}`;
                } else if (method === 'primitive') {
                    params.set('prim_type', c.prim_type || 'PRIM_SKIRT');
                    params.set('segments', c.segments || 32);
                    params.set('length', c.length !== undefined ? c.length : 0.5);
                    params.set('flare', c.flare !== undefined ? c.flare : 0.5);
                    key = `prim_${c.prim_type || 'PRIM_SKIRT'}`;
                } else {
                    const tpl = c.template || 'TPL_TSHIRT';
                    params.set('template', tpl);
                    params.set('tightness', c.tightness !== undefined ? c.tightness : 0.5);
                    params.set('segments', c.segments || 32);
                    if (c.top_extend) params.set('top_extend', c.top_extend);
                    if (c.bottom_extend) params.set('bottom_extend', c.bottom_extend);
                    key = `tpl_${tpl}`;
                }

                // Include morphs
                for (const [k, v] of Object.entries(this.morphs)) {
                    if (v !== 0) params.set(`morph_${k}`, v);
                }
                // Include meta (internal -1..1 values)
                for (const [k, v] of Object.entries(this.meta)) {
                    if (v !== 0) params.set(`meta_${k}`, v);
                }

                const resp = await fetch(`/api/character/cloth/?${params}`);
                const data = await resp.json();
                if (data.error) { console.warn('Cloth error:', data.error); continue; }

                const vertBuf = base64ToFloat32(data.vertices);
                blenderToThreeCoords(vertBuf);
                const faceBuf = base64ToUint32(data.faces);
                const normalBuf = base64ToFloat32(data.normals);
                blenderToThreeCoords(normalBuf);

                const geo = new THREE.BufferGeometry();
                geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
                geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
                geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));

                const matColor = c.color ? new THREE.Color(c.color) : new THREE.Color(0.5, 0.5, 0.6);
                const mat = new THREE.MeshStandardMaterial({
                    color: matColor, roughness: 0.8, metalness: 0.0,
                    side: THREE.DoubleSide,
                });

                const mesh = _skinifyMesh(geo, mat, this, data);
                this.clothMeshes[key] = mesh;
                this.group.add(mesh);
            } catch (e) {
                console.error('Failed to load cloth piece:', e);
            }
        }
    }

    async _loadGarments() {
        if (!this.garments || this.garments.length === 0) return;

        // Auto-skin character if skeleton data is available
        if (!this.isSkinned && rigifySkeletonData && skinWeightData) {
            convertInstToSkinned(this);
        }

        const params = new URLSearchParams();
        params.set('body_type', this.bodyType);
        for (const [k, v] of Object.entries(this.morphs)) {
            if (v !== 0) params.set(`morph_${k}`, v);
        }
        for (const [k, v] of Object.entries(this.meta)) {
            if (v !== 0) params.set(`meta_${k}`, v);
        }

        for (const g of this.garments) {
            try {
                const p = new URLSearchParams(params);
                p.set('garment_id', g.id);
                p.set('offset', (g.offset || 0).toFixed(4));
                p.set('stiffness', (g.stiffness || 0.5).toFixed(2));
                p.set('min_dist', g.minDist !== undefined ? g.minDist : 3);
                p.set('crotch_floor', g.crotchFloor !== undefined ? g.crotchFloor : 0);
                p.set('lift', g.lift !== undefined ? g.lift : 0);
                p.set('crotch_depth', g.crotchDepth !== undefined ? g.crotchDepth : 0);
                if (g.color) {
                    let cr, cg, cb;
                    if (Array.isArray(g.color)) {
                        [cr, cg, cb] = g.color;
                    } else {
                        const tc = new THREE.Color(g.color);
                        cr = tc.r; cg = tc.g; cb = tc.b;
                    }
                    p.set('color_r', cr.toFixed(3));
                    p.set('color_g', cg.toFixed(3));
                    p.set('color_b', cb.toFixed(3));
                }

                const resp = await fetch(`/api/character/garment/fit/?${p}`);
                const data = await resp.json();
                if (data.error) { console.warn('Garment load error:', data.error); continue; }

                const vertBuf = base64ToFloat32(data.vertices);
                blenderToThreeCoords(vertBuf);
                const faceBuf = base64ToUint32(data.faces);

                const geo = new THREE.BufferGeometry();
                geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
                geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
                geo.computeVertexNormals();

                const color = g.color ? new THREE.Color(g.color[0], g.color[1], g.color[2])
                                      : new THREE.Color(0.3, 0.35, 0.5);
                const mat = new THREE.MeshStandardMaterial({
                    color, roughness: g.roughness ?? 0.8, metalness: g.metalness ?? 0.0,
                    side: THREE.DoubleSide,
                    polygonOffset: true,
                    polygonOffsetFactor: -1,
                    polygonOffsetUnit: -1,
                });

                const mesh = _skinifyMesh(geo, mat, this, data);
                const key = `gar_${g.id}`;
                this.clothMeshes[key] = mesh;
                this.group.add(mesh);

                this.garmentOrigPositions[key] = new Float32Array(vertBuf);
                _computeGarmentRegionWeights(this, key);

                this.garmentState[key] = {
                    offset: g.offset || 0,
                    stiffness: g.stiffness || 0.5,
                    minDist: g.minDist !== undefined ? g.minDist : 3,
                    crotchFloor: g.crotchFloor !== undefined ? g.crotchFloor : 0,
                    lift: g.lift !== undefined ? g.lift : 0,
                    crotchDepth: g.crotchDepth !== undefined ? g.crotchDepth : 0,
                    color: g.color || [color.r, color.g, color.b],
                    roughness: g.roughness ?? 0.8,
                    metalness: g.metalness ?? 0.0,
                    regionTop: 0, regionUpper: 0, regionMid: 0, regionLower: 0, regionBottom: 0,
                };
            } catch (e) {
                console.error('Failed to load garment:', g.id, e);
            }
        }
    }

    async _loadHair() {
        // Remove old hair
        if (this.hairMesh) {
            this.group.remove(this.hairMesh);
            this.hairMesh.traverse(child => {
                if (child.isMesh) {
                    child.geometry.dispose();
                    const mats = Array.isArray(child.material) ? child.material : [child.material];
                    mats.forEach(m => m.dispose());
                }
            });
            this.hairMesh = null;
        }

        if (!this.hairStyle || !this.hairStyle.url) return;

        return new Promise((resolve) => {
            gltfLoader.load(this.hairStyle.url, (gltf) => {
                let hairGroup = gltf.scene;

                // Convert to skinned meshes bound to head bone
                if (this.isSkinned && this.rigifySkeleton) {
                    hairGroup = _skinifyHairGroup(hairGroup, this);
                }

                this.hairMesh = hairGroup;

                // Apply hair color if specified
                if (this.hairStyle.color && hairColorData[this.hairStyle.color]) {
                    const rgb = hairColorData[this.hairStyle.color];
                    const color = new THREE.Color(rgb[0], rgb[1], rgb[2]);
                    this.hairMesh.traverse(child => {
                        if (child.isMesh && child.material) {
                            const mats = Array.isArray(child.material) ? child.material : [child.material];
                            mats.forEach(m => { m.color.copy(color); });
                        }
                    });
                }

                this.group.add(this.hairMesh);
                resolve();
            }, undefined, (err) => {
                console.warn('Failed to load hair:', err);
                resolve();
            });
        });
    }

    dispose() {
        if (this.bodyMesh) {
            this.bodyMesh.geometry.dispose();
            const mats = Array.isArray(this.bodyMesh.material) ? this.bodyMesh.material : [this.bodyMesh.material];
            mats.forEach(m => m.dispose());
        }
        // Dispose cloth meshes
        for (const mesh of Object.values(this.clothMeshes)) {
            mesh.geometry.dispose();
            mesh.material.dispose();
        }
        // Dispose hair
        if (this.hairMesh) {
            this.hairMesh.traverse(child => {
                if (child.isMesh) {
                    child.geometry.dispose();
                    const mats = Array.isArray(child.material) ? child.material : [child.material];
                    mats.forEach(m => m.dispose());
                }
            });
        }
        if (this.group.parent) this.group.parent.remove(this.group);
    }

    toJSON() {
        // Generated model: save config directly
        if (this.generatedConfig) {
            return {
                id: this.id,
                presetName: this.presetName,
                presetKey: this.presetKey || null,
                bodyType: 'generated',
                generatedConfig: this.generatedConfig,
                transform: {
                    position: this.group.position.toArray(),
                    rotation: [this.group.rotation.x, this.group.rotation.y, this.group.rotation.z],
                    scale: this.group.scale.toArray()
                }
            };
        }

        // Sync garmentState back into garments array so UI changes are saved
        const garments = (this.garments || []).map(g => {
            const key = `gar_${g.id}`;
            const st = this.garmentState[key];
            if (!st) return g;
            return {
                id: g.id,
                offset: st.offset,
                stiffness: st.stiffness,
                minDist: st.minDist,
                crotchFloor: st.crotchFloor,
                lift: st.lift,
                crotchDepth: st.crotchDepth,
                color: st.color,
                roughness: st.roughness,
                metalness: st.metalness,
            };
        });
        return {
            id: this.id,
            presetName: this.presetName,
            bodyType: this.bodyType,
            morphs: this.morphs,
            meta: this.meta,
            cloth: this.cloth,
            hair_style: this.hairStyle,
            garments,
            transform: {
                position: this.group.position.toArray(),
                rotation: [this.group.rotation.x, this.group.rotation.y, this.group.rotation.z],
                scale: this.group.scale.toArray()
            }
        };
    }

    static async fromJSON(data) {
        let presetPayload;
        if (data.bodyType === 'generated' && data.generatedConfig) {
            // Rebuild from generated model config
            presetPayload = {
                ...data.generatedConfig,
                name: data.presetName,
                type: 'generated_model',
            };
        } else {
            presetPayload = {
                name: data.presetName,
                body_type: data.bodyType,
                morphs: data.morphs || {},
                meta: data.meta || {},
                cloth: data.cloth || [],
                hair_style: data.hair_style || null,
                garments: data.garments || [],
            };
        }

        const inst = new CharacterInstance(data.id, presetPayload);
        if (data.presetKey) inst.presetKey = data.presetKey;
        await inst.load();
        if (data.transform) {
            if (data.transform.position) inst.group.position.fromArray(data.transform.position);
            if (data.transform.rotation) {
                inst.group.rotation.set(data.transform.rotation[0], data.transform.rotation[1], data.transform.rotation[2]);
            }
            if (data.transform.scale) inst.group.scale.fromArray(data.transform.scale);
        }
        return inst;
    }
}

// =========================================================================
// Initialization
// =========================================================================
async function init() {
    canvas = document.getElementById('viewer-canvas');
    const container = canvas.parentElement;
    const w = container.clientWidth;
    const h = container.clientHeight || window.innerHeight;

    // Renderer
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.6;

    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);

    // Camera
    camera = new THREE.PerspectiveCamera(35, w / h, 0.01, 100);
    camera.position.set(0, 1.0, 3.5);

    // Controls
    controls = new OrbitControls(camera, canvas);
    controls.target.set(0, 0.9, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 0.5;
    controls.maxDistance = 15;
    controls.update();

    // Lighting
    keyLight = new THREE.DirectionalLight(0xffffff, 3.0);
    keyLight.position.set(2, 4, -5);
    scene.add(keyLight);

    fillLight = new THREE.DirectionalLight(0xeeeeff, 2.0);
    fillLight.position.set(-3, 3, -4);
    scene.add(fillLight);

    backLight = new THREE.DirectionalLight(0xffeedd, 2.5);
    backLight.position.set(0, 4, 5);
    scene.add(backLight);

    ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    // Ground grid
    const grid = new THREE.GridHelper(4, 20, 0x333355, 0x222244);
    scene.add(grid);

    // TransformControls
    transformControls = new TransformControls(camera, canvas);
    transformControls.setMode('translate');
    transformControls.setSpace('world');
    transformControls.enabled = false;
    transformHelper = transformControls.getHelper();
    transformHelper.visible = false;
    scene.add(transformHelper);

    transformControls.addEventListener('dragging-changed', (e) => {
        controls.enabled = !e.value;
        transformDragging = e.value;
    });
    transformControls.addEventListener('objectChange', () => {
        updateCharacterListUI();
        markDirty();
    });

    // Resize
    window.addEventListener('resize', onResize);

    // Panel toggle
    document.querySelectorAll('.panel-section h3').forEach(h3 => {
        h3.addEventListener('click', () => {
            h3.closest('.panel-section').classList.toggle('collapsed');
        });
    });

    // Apply expanded panels + default preset from settings
    const _settingsReady = fetch('/api/settings/humanbody/')
        .then(r => r.json())
        .then(s => {
            if (s.scene) defaultPresetName = s.scene;
            if (s.default_anim_scene) _defaultAnimUrl = s.default_anim_scene;
            const expanded = s.expanded_panels_scene;
            if (Array.isArray(expanded)) {
                document.querySelectorAll('.panel-section[data-panel-key]').forEach(panel => {
                    // Skip Modell tab panels — they manage their own state
                    if (panel.closest('#tab-modell')) return;
                    if (expanded.includes(panel.dataset.panelKey)) {
                        panel.classList.remove('collapsed');
                    } else {
                        panel.classList.add('collapsed');
                    }
                });
            }
            // Dynamic selection opacity
            if (typeof s.selection_opacity === 'number') {
                const o = s.selection_opacity;
                _SELECT_EMISSIVE = new THREE.Color(o * 0.071, o * 0.071, o * 0.227);
                _HOVER_EMISSIVE = new THREE.Color(o * 0.031, o * 0.031, o * 0.102);
            }
        })
        .catch(() => {});

    // Bind all UI controls
    bindLightingUI();
    bindRendererUI();
    bindCameraUI();
    bindActions();
    bindMenubar();
    initCharacterDialog();
    initSceneDialogs();
    _initSaveAnimDialog();
    bindKeyboardShortcuts();
    bindCanvasClick();
    initSubMeshInteraction();
    initTabs();
    bindVisibilityToggles();

    // Garment + Hair props in Eigenschaften tab
    initPropGarmentControls();
    initPropHairControls();

    // Asset + Animation panels
    loadGarmentUI();
    loadHairUI();
    loadClothUI();
    loadAnimationUI();

    // Demo animation button
    const demoBtn = document.getElementById('play-demo-anim');
    if (demoBtn) {
        demoBtn.addEventListener('click', () => {
            if (!currentAction) {
                // Need a character selected (or at least a body mesh)
                const inst = _selectedInst();
                if (!inst && !bodyMesh) return;
                loadBVHAnimation('/api/character/bvh/Mixamo/Catwalk_Idle_02/', 'Catwalk Idle 02', 0);
                demoBtn.innerHTML = '<i class="fas fa-pause"></i>';
                demoBtn.classList.add('active');
            } else if (playing) {
                currentAction.paused = true;
                playing = false;
                demoBtn.innerHTML = '<i class="fas fa-play"></i>';
                demoBtn.classList.remove('active');
            } else {
                if (!currentAction.isRunning()) currentAction.play();
                currentAction.paused = false;
                playing = true;
                demoBtn.innerHTML = '<i class="fas fa-pause"></i>';
                demoBtn.classList.add('active');
            }
        });
    }

    // Load saved settings from localStorage
    loadSettings();

    // beforeunload — save session state
    window.addEventListener('beforeunload', (e) => {
        saveSessionState();
    });

    // Start render loop
    animate();

    // Load skin colors + hair colors + skeleton/weights + settings, then restore or load default
    Promise.all([loadSkinColors(), loadHairColors(), loadRigifySkeleton(), loadSkinWeights(), _settingsReady]).then(async () => {
        if (sessionStorage.getItem(SESSION_KEY)) {
            await restoreSessionState();
        }
        if (characters.size === 0) {
            await loadDefaultCharacter();
        }
        // Auto-load default animation from settings (if set and no session restore)
        if (_defaultAnimUrl && !sessionStorage.getItem(SESSION_KEY)) {
            try {
                loadBVHAnimation(_defaultAnimUrl, _defaultAnimUrl.split('/').filter(Boolean).pop() || 'default', 0);
            } catch (e) { console.warn('[SCENE] Default animation load failed:', e); }
        }
    });
}

function onResize() {
    const container = renderer.domElement.parentElement;
    const w = Math.max(container.clientWidth, 100);
    const h = container.clientHeight || window.innerHeight;
    renderer.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
}

function animate() {
    requestAnimationFrame(animate);
    const dt = Math.min(clock.getDelta(), 0.1);
    controls.update();
    if (mixer && playing) {
        mixer.update(dt);
        // Update frame/time display
        if (currentAction) {
            const clip = currentAction.getClip();
            if (clip) {
                const t = currentAction.time;
                const dur = clip.duration;
                const ft = clip.tracks[0]?.times?.[1] || (1/30);
                const frame = Math.floor(t / ft);
                const totalFrames = Math.round(dur / ft);
                const el = document.getElementById('anim-time');
                if (el) el.textContent = `Frame ${frame} / ${totalFrames} \u2022 ${t.toFixed(2)}s / ${dur.toFixed(2)}s`;
                const tl = document.getElementById('anim-timeline');
                if (tl) tl.value = Math.round((t / dur) * 100);
            }
        }
        // Ground fix: after animation, ensure feet touch ground (Y=0)
        if (currentAnimGroundFixed && frameCount % 300 === 0) {
            console.log('[GROUND] active, checking bones...');
        }
        if (currentAnimGroundFixed) {
            const inst = _selectedInst ? _selectedInst() : null;
            const skel = inst ? inst.rigifySkeleton : rigifySkeleton;
            if (skel && skel.rootBone) {
                // Find lowest bone Y position
                const tmpV = new THREE.Vector3();
                let minY = Infinity;
                skel.rootBone.traverse(b => {
                    if (b.isBone) {
                        b.getWorldPosition(tmpV);
                        if (tmpV.y < minY) minY = tmpV.y;
                    }
                });
                if (isFinite(minY)) {
                    skel.rootBone.position.y -= minY;
                }
            }
        }
    }
    renderer.render(scene, camera);

    updateCameraInfo();

    frameCount++;
    fpsAccum += dt;
    if (fpsAccum >= 1.0) {
        document.getElementById('fps-display').textContent = frameCount;
        frameCount = 0;
        fpsAccum = 0;
    }
}

function updateCameraInfo() {
    const p = camera.position;
    const t = controls.target;
    document.getElementById('cam-pos').textContent =
        `${p.x.toFixed(2)}, ${p.y.toFixed(2)}, ${p.z.toFixed(2)}`;
    document.getElementById('cam-target').textContent =
        `${t.x.toFixed(2)}, ${t.y.toFixed(2)}, ${t.z.toFixed(2)}`;
}

// =========================================================================
// Auto-save
// =========================================================================
function autoSave() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
        const settings = gatherSettings();
        localStorage.setItem('humanbody_scene_settings', JSON.stringify(settings));
    }, 300);
    markDirty();
}

// =========================================================================
// Character Management
// =========================================================================
function generateCharacterId() {
    return `char_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

async function addCharacterFromPreset(presetName) {
    // Fetch preset data
    const resp = await fetch(`/api/character/model/${encodeURIComponent(presetName)}/`);
    if (!resp.ok) throw new Error(`Preset not found: ${presetName}`);
    const presetData = await resp.json();

    const id = generateCharacterId();
    const inst = new CharacterInstance(id, presetData);

    // Offset each new character by 0.8m on X
    const xOffset = characters.size * 0.8;
    inst.group.position.set(xOffset, 0, 0);

    inst.presetKey = presetName;  // Store original filename for server save
    await inst.load();
    characters.set(id, inst);
    scene.add(inst.group);

    updateCharacterListUI();
    updateVertexCount();
    selectCharacter(id);
    markDirty();

    return inst;
}

async function loadDefaultCharacter() {
    try {
        await addCharacterFromPreset(defaultPresetName);
        // Keep the first character selected so Assets tab is immediately usable
    } catch (e) {
        console.warn('Failed to load default character:', e);
    }
}

function selectCharacter(id) {
    // Deselect previous
    if (selectedCharacterId && characters.has(selectedCharacterId)) {
        const prev = characters.get(selectedCharacterId);
        prev.selected = false;
        _setBodyEmissive(prev, _ZERO_EMISSIVE);
    }

    selectedCharacterId = id;
    const inst = characters.get(id);
    if (!inst) {
        deselectCharacter();
        return;
    }

    inst.selected = true;
    // Highlight body if no sub-mesh is selected
    if (!_selectedSubMesh) {
        _setBodyEmissive(inst, _SELECT_EMISSIVE);
    }
    transformControls.attach(inst.group);
    transformHelper.visible = true;
    transformControls.enabled = true;

    updateCharacterListUI();
    populateProperties(id);
}

function deselectCharacter() {
    if (selectedCharacterId && characters.has(selectedCharacterId)) {
        const prev = characters.get(selectedCharacterId);
        prev.selected = false;
        _setBodyEmissive(prev, _ZERO_EMISSIVE);
    }
    clearSubMeshSelection();
    selectedCharacterId = null;
    transformControls.detach();
    transformHelper.visible = false;
    transformControls.enabled = false;
    updateCharacterListUI();
    clearProperties();
}

function deleteCharacter(id) {
    const inst = characters.get(id);
    if (!inst) return;

    if (selectedCharacterId === id) {
        deselectCharacter();
    }

    // Clear model generator reference if this was the generated character
    if (_mgCharacterId === id) {
        _clearBoneHighlightCache();
        _mgCharacterId = null;
    }

    inst.dispose();
    characters.delete(id);
    updateCharacterListUI();
    updateVertexCount();
    markDirty();
}

function setTransformMode(mode) {
    currentTransformMode = mode;
    transformControls.setMode(mode);

    // Update button states
    document.querySelectorAll('.transform-btn[data-mode]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });
}

function focusCharacter(id) {
    const inst = characters.get(id);
    if (!inst) return;
    // Compute bounding box of the character group
    const box = new THREE.Box3().setFromObject(inst.group);
    const center = box.getCenter(new THREE.Vector3());
    controls.target.copy(center);
    controls.update();
}

function updateCharacterListUI() {
    const list = document.getElementById('character-list');
    const countEl = document.getElementById('char-count');
    if (countEl) countEl.textContent = characters.size;

    list.innerHTML = '';
    characters.forEach((inst, id) => {
        const li = document.createElement('li');
        li.className = 'character-item' + (id === selectedCharacterId ? ' selected' : '');
        li.dataset.charId = id;

        const pos = inst.group.position;
        const posStr = `${pos.x.toFixed(1)}, ${pos.y.toFixed(1)}, ${pos.z.toFixed(1)}`;

        const icon = inst.generatedConfig ? 'fa-robot' : 'fa-user';
        li.innerHTML = `
            <span class="character-item-icon"><i class="fas ${icon}"></i></span>
            <div class="character-item-info">
                <div class="character-item-name">${escapeHtml(inst.presetName)}</div>
                <div class="character-item-detail">${escapeHtml(inst.bodyType)} &bull; (${posStr})</div>
            </div>
            <div class="character-item-actions">
                <button class="btn-focus" title="Fokussieren"><i class="fas fa-crosshairs"></i></button>
                <button class="btn-delete" title="Löschen"><i class="fas fa-trash"></i></button>
            </div>
        `;

        // Click to select
        li.addEventListener('click', (e) => {
            if (e.target.closest('.character-item-actions')) return;
            selectCharacter(id);
        });

        // Focus button
        li.querySelector('.btn-focus').addEventListener('click', (e) => {
            e.stopPropagation();
            selectCharacter(id);
            focusCharacter(id);
        });

        // Delete button
        li.querySelector('.btn-delete').addEventListener('click', (e) => {
            e.stopPropagation();
            deleteCharacter(id);
        });

        list.appendChild(li);
    });

    // Sync transform inputs if properties panel shows the selected character
    if (currentPropsCharId && currentPropsCharId === selectedCharacterId) {
        syncTransformInputs();
    }
}

function updateVertexCount() {
    let total = 0;
    characters.forEach(inst => {
        if (inst.bodyMesh) total += inst.bodyMesh.geometry.attributes.position.count;
        for (const m of Object.values(inst.clothMeshes)) {
            if (m && m.geometry) total += m.geometry.attributes.position.count;
        }
        if (inst.hairMesh) {
            inst.hairMesh.traverse(child => {
                if (child.isMesh && child.geometry) total += child.geometry.attributes.position.count;
            });
        }
    });
    document.getElementById('vertex-count').textContent = total.toLocaleString();
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// =========================================================================
// Canvas click — Raycast to select characters
// =========================================================================
function bindCanvasClick() {
    canvas.addEventListener('pointerdown', (e) => {
        mouseDownPos = { x: e.clientX, y: e.clientY };
    });

    canvas.addEventListener('pointerup', (e) => {
        if (!mouseDownPos) return;
        const dx = e.clientX - mouseDownPos.x;
        const dy = e.clientY - mouseDownPos.y;
        mouseDownPos = null;

        // Only count as click if mouse barely moved (not an orbit drag)
        if (Math.sqrt(dx * dx + dy * dy) > CLICK_THRESHOLD) return;

        // Don't raycast if TransformControls is being dragged
        if (transformDragging) return;

        const rect = canvas.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);

        // Collect ALL meshes from all characters, tag each with char id
        const meshes = [];
        characters.forEach((inst, id) => {
            inst.group.traverse(child => {
                if (child.isMesh && !child.userData._boneOverlay) {
                    child.userData._parentCharId = id;
                    meshes.push(child);
                }
            });
        });

        const hits = raycaster.intersectObjects(meshes, false);
        if (hits.length > 0) {
            const hitObj = hits[0].object;
            const charId = hitObj.userData._parentCharId;
            if (charId) {
                // Check if the hit is a sub-mesh (cloth/hair) of this character
                const subTargets = getSelectableSubMeshes(charId);
                const hitTarget = _findSubMeshForObject(hitObj, subTargets);
                if (hitTarget) {
                    // Select character first if not already
                    if (selectedCharacterId !== charId) {
                        clearSubMeshSelection();
                        selectCharacter(charId);
                    }
                    _clearBoneSelection();
                    _doSubMeshClick(hitTarget);
                    return;
                }

                // Check Ctrl+Click on generated model body for bone selection
                const inst = characters.get(charId);
                if (e.ctrlKey && inst && inst.generatedConfig &&
                    hitObj === inst.bodyMesh && inst.bodyMesh.userData.boneVertexRanges) {
                    const boneName = _getBoneFromIntersection(hits[0], inst.bodyMesh);
                    if (boneName) {
                        if (selectedCharacterId !== charId) {
                            clearSubMeshSelection();
                            selectCharacter(charId);
                        }
                        _doBoneClick(boneName, inst);
                        return;
                    }
                }

                // Hit the body mesh — select character, clear sub-mesh and bone
                clearSubMeshSelection();
                _clearBoneSelection();
                selectCharacter(charId);
                switchTab('eigenschaften');
                _updatePropContext();
                return;
            }
        }

        // Clicked empty space — deselect
        _clearBoneSelection();
        deselectCharacter();
    });
}

// =========================================================================
// Menubar
// =========================================================================
function closeAllMenus() {
    document.querySelectorAll('.menu.open').forEach(m => m.classList.remove('open'));
}

function bindMenubar() {
    // Click to open menu
    document.querySelectorAll('.menu-title').forEach(title => {
        title.addEventListener('click', (e) => {
            const menu = title.parentElement;
            const wasOpen = menu.classList.contains('open');
            closeAllMenus();
            if (!wasOpen) {
                updateMenuChecks();
                menu.classList.add('open');
            }
            e.stopPropagation();
        });
        // Hover-switch when another menu already open
        title.addEventListener('mouseenter', () => {
            if (document.querySelector('.menu.open')) {
                closeAllMenus();
                updateMenuChecks();
                title.parentElement.classList.add('open');
            }
        });
    });

    // Close on click outside
    document.addEventListener('click', () => closeAllMenus());

    // Prevent dropdown clicks from closing (except menu-item clicks handled below)
    document.querySelectorAll('.menu-dropdown').forEach(dd => {
        dd.addEventListener('click', (e) => e.stopPropagation());
    });

    // Route actions
    document.querySelectorAll('.menu-item[data-action]').forEach(item => {
        item.addEventListener('click', () => {
            if (item.classList.contains('disabled')) return;
            closeAllMenus();
            handleMenuAction(item.dataset.action);
        });
    });

    // Transform buttons (right side of menubar)
    document.querySelectorAll('.transform-btn[data-mode]').forEach(btn => {
        btn.addEventListener('click', () => setTransformMode(btn.dataset.mode));
    });
}

function handleMenuAction(action) {
    switch (action) {
        // Datei
        case 'new':
            newScene();
            break;
        case 'load':
            loadFromFilePicker();
            break;
        case 'save':
            quickSave();
            break;
        case 'save-as':
            openSaveDialog();
            break;
        case 'import-model':
            importModelFromFilePicker();
            break;
        case 'export-scene-json':
            exportSceneJSON();
            break;
        case 'export-model-json':
            exportModelJSON();
            break;

        // Bearbeiten
        case 'deselect':
            deselectCharacter();
            break;
        case 'delete':
            if (_selectedSubMesh) {
                _removeSubMesh(_selectedSubMesh);
            } else {
                deleteSelectedCharacter();
            }
            break;
        case 'clear-all':
            if (characters.size === 0) return;
            if (confirm('Alle Charaktere löschen?')) {
                clearAllCharacters();
            }
            break;

        // Hinzufügen
        case 'add-character':
            openAddCharacterDialog();
            break;

        // Ansicht
        case 'toggle-model':
            toggleModelVisibility();
            document.getElementById('model-toggle')?.classList.toggle('active', modelVisible);
            break;
        case 'toggle-rig':
            toggleRigVisibility();
            document.getElementById('rig-toggle')?.classList.toggle('active', rigVisible);
            break;
        case 'mode-translate':
            setTransformMode('translate');
            break;
        case 'mode-rotate':
            setTransformMode('rotate');
            break;
        case 'mode-scale':
            setTransformMode('scale');
            break;
        case 'focus-char':
            if (selectedCharacterId) focusCharacter(selectedCharacterId);
            break;

        // Werkzeuge
        case 'model-generator':
            switchTab('modell');
            initModelGenerator();
            break;
        case 'reset-scene':
            resetScene();
            break;
        case 'reset-lighting':
            resetLighting();
            break;
        case 'reset-camera':
            resetCamera();
            break;

        // Animation
        case 'anim-ground-fix':
            applyGroundLevelFix();
            break;
        case 'anim-save':
            openSaveAnimDialog();
            break;
    }
}

function updateMenuChecks() {
    // Model visibility
    const modelItem = document.querySelector('[data-action="toggle-model"]');
    if (modelItem) modelItem.classList.toggle('checked', modelVisible);

    // Rig visibility
    const rigItem = document.querySelector('[data-action="toggle-rig"]');
    if (rigItem) rigItem.classList.toggle('checked', rigVisible);

    // Transform mode radio
    document.querySelectorAll('.menu-item.radio[data-action^="mode-"]').forEach(item => {
        const mode = item.dataset.action.replace('mode-', '');
        item.classList.toggle('checked', mode === currentTransformMode);
    });
}

// =========================================================================
// Dirty tracking — mark scene as having unsaved changes
// =========================================================================
function markDirty(label) { pushSceneUndo(label || 'Aenderung'); _sceneDirty = true; }
function markClean() { _sceneDirty = false; }

// =========================================================================
// Undo/Redo system (snapshot-based)
// =========================================================================
const _undoStack = [];
const _redoStack = [];
const _UNDO_MAX = 20;
let _undoSuppressed = false;
let _undoInProgress = false;

function pushSceneUndo(label) {
    if (_undoSuppressed || _undoInProgress) return;
    try {
        const data = gatherSceneState();
        _undoStack.push({ label, data, selectedCharacterId });
        if (_undoStack.length > _UNDO_MAX) _undoStack.shift();
        _redoStack.length = 0;
        console.log(`[Scene Undo] push '${label}' (stack: ${_undoStack.length}, chars: ${data.characters?.length || 0})`);
    } catch (e) { console.error('[Scene Undo] Snapshot failed:', e); }
}

async function sceneUndo() {
    console.log(`[Scene Undo] called. stack: ${_undoStack.length}, inProgress: ${_undoInProgress}`);
    if (_undoInProgress || _undoStack.length === 0) { console.log('[Scene Undo] nothing to undo'); return; }
    _undoInProgress = true;
    try {
        _redoStack.push({ label: 'redo', data: gatherSceneState(), selectedCharacterId });
    } catch (e) {}
    const snap = _undoStack.pop();
    _undoSuppressed = true;
    await loadSceneFromData(snap.data, currentSceneName);
    _undoSuppressed = false;
    if (snap.selectedCharacterId && characters.has(snap.selectedCharacterId)) {
        selectCharacter(snap.selectedCharacterId);
    }
    console.log(`[Scene Undo] Restored: ${snap.label} (${_undoStack.length} left)`);
    _undoInProgress = false;
}

async function sceneRedo() {
    if (_undoInProgress || _redoStack.length === 0) return;
    _undoInProgress = true;
    _undoStack.push({ label: 'undo', data: gatherSceneState(), selectedCharacterId });
    const snap = _redoStack.pop();
    _undoSuppressed = true;
    await loadSceneFromData(snap.data, currentSceneName);
    _undoSuppressed = false;
    if (snap.selectedCharacterId && characters.has(snap.selectedCharacterId)) {
        selectCharacter(snap.selectedCharacterId);
    }
    console.log(`[Scene Redo] Restored (${_redoStack.length} left)`);
    _undoInProgress = false;
}

// Expose for onclick buttons
window.__sceneUndo = sceneUndo;
window.__sceneRedo = sceneRedo;

// =========================================================================
// sessionStorage persistence — survive page navigation
// =========================================================================
function saveSessionState() {
    try {
        const state = gatherSceneState();
        sessionStorage.setItem(SESSION_KEY, JSON.stringify(state));
    } catch (e) {
        console.warn('Failed to save session state:', e);
    }
}

async function restoreSessionState() {
    const raw = sessionStorage.getItem(SESSION_KEY);
    if (!raw) return false;
    try {
        const data = JSON.parse(raw);
        sessionStorage.removeItem(SESSION_KEY);

        // Restore characters
        if (data.characters && data.characters.length > 0) {
            clearAllCharacters();
            for (const charData of data.characters) {
                try {
                    const inst = await CharacterInstance.fromJSON(charData);
                    characters.set(inst.id, inst);
                    scene.add(inst.group);
                } catch (e) {
                    console.error(`Failed to restore character ${charData.presetName}:`, e);
                }
            }
        }

        // Restore lighting
        if (data.lighting) {
            if (data.lighting.key) {
                keyLight.intensity = data.lighting.key.intensity;
                keyLight.color.set(data.lighting.key.color);
                keyLight.position.set(...data.lighting.key.pos);
            }
            if (data.lighting.fill) {
                fillLight.intensity = data.lighting.fill.intensity;
                fillLight.color.set(data.lighting.fill.color);
                fillLight.position.set(...data.lighting.fill.pos);
            }
            if (data.lighting.back) {
                backLight.intensity = data.lighting.back.intensity;
                backLight.color.set(data.lighting.back.color);
                backLight.position.set(...data.lighting.back.pos);
            }
            if (data.lighting.ambient) {
                ambientLight.intensity = data.lighting.ambient.intensity;
                ambientLight.color.set(data.lighting.ambient.color);
            }
        }

        // Restore renderer
        if (data.renderer) {
            if (data.renderer.toneMapping && TONE_MAPPINGS[data.renderer.toneMapping] !== undefined) {
                renderer.toneMapping = TONE_MAPPINGS[data.renderer.toneMapping];
            }
            if (data.renderer.exposure !== undefined) {
                renderer.toneMappingExposure = data.renderer.exposure;
            }
            if (data.renderer.background) {
                scene.background.set(data.renderer.background);
            }
        }

        // Restore camera
        if (data.camera) {
            if (data.camera.fov) {
                camera.fov = data.camera.fov;
                camera.updateProjectionMatrix();
            }
            if (data.camera.position) camera.position.fromArray(data.camera.position);
            if (data.camera.target) controls.target.fromArray(data.camera.target);
            controls.update();
        }

        currentSceneName = data.name || '';
        syncUIFromState();
        updateCharacterListUI();
        updateVertexCount();

        // Auto-select first character so Assets tab is immediately usable
        if (characters.size > 0 && !selectedCharacterId) {
            selectCharacter(characters.keys().next().value);
        }

        console.log('Session state restored');
        return true;
    } catch (e) {
        console.warn('Failed to restore session state:', e);
        sessionStorage.removeItem(SESSION_KEY);
        return false;
    }
}

// =========================================================================
// Werkzeuge — Reset helpers
// =========================================================================
function resetLighting() {
    const preset = LIGHT_PRESETS.studio;
    keyLight.intensity = preset.key.intensity;
    keyLight.color.set(preset.key.color);
    keyLight.position.set(...preset.key.pos);
    fillLight.intensity = preset.fill.intensity;
    fillLight.color.set(preset.fill.color);
    fillLight.position.set(...preset.fill.pos);
    backLight.intensity = preset.back.intensity;
    backLight.color.set(preset.back.color);
    backLight.position.set(...preset.back.pos);
    ambientLight.intensity = preset.ambient.intensity;
    ambientLight.color.set(preset.ambient.color);
    renderer.toneMappingExposure = preset.exposure;
    syncUIFromState();
    markDirty();
}

function resetCamera() {
    camera.fov = 35;
    camera.position.set(0, 1.0, 3.5);
    camera.updateProjectionMatrix();
    controls.target.set(0, 0.9, 0);
    controls.update();
    markDirty();
}

function resetScene() {
    if (!confirm('Szene komplett zurücksetzen? Alle Änderungen gehen verloren.')) return;
    clearAllCharacters();
    currentSceneName = '';
    resetLighting();
    resetCamera();
    scene.background.set(0x1a1a2e);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    syncUIFromState();
    loadDefaultCharacter();
    markClean();
}

// =========================================================================
// Menu helper functions
// =========================================================================
function newScene() {
    if (characters.size > 0) {
        if (!confirm('Aktuelle Szene verwerfen und neue Szene erstellen?')) return;
    }
    clearAllCharacters();
    currentSceneName = '';
    loadDefaultCharacter();
}

function quickSave() {
    if (currentSceneName) {
        doSaveScene(currentSceneName);
    } else {
        openSaveDialog();
    }
}

async function _openJsonFilePicker() {
    if (window.showOpenFilePicker) {
        try {
            const [handle] = await window.showOpenFilePicker({
                types: [{
                    description: 'JSON',
                    accept: { 'application/json': ['.json'] },
                }],
                multiple: false,
            });
            const file = await handle.getFile();
            const text = await file.text();
            return JSON.parse(text);
        } catch (e) {
            if (e.name === 'AbortError') return null; // user cancelled
            throw e;
        }
    }
    // Fallback: hidden file input
    return new Promise((resolve) => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json,application/json';
        input.style.display = 'none';
        input.addEventListener('change', async () => {
            const file = input.files[0];
            if (!file) { resolve(null); return; }
            try {
                const text = await file.text();
                resolve(JSON.parse(text));
            } catch (e) {
                alert('Fehler beim Lesen der Datei: ' + e.message);
                resolve(null);
            }
            input.remove();
        });
        input.addEventListener('cancel', () => { resolve(null); input.remove(); });
        document.body.appendChild(input);
        input.click();
    });
}

async function _saveJsonWithPicker(jsonData, defaultName) {
    const content = JSON.stringify(jsonData, null, 2);
    if (window.showSaveFilePicker) {
        try {
            const handle = await window.showSaveFilePicker({
                suggestedName: defaultName,
                types: [{
                    description: 'JSON',
                    accept: { 'application/json': ['.json'] },
                }],
            });
            const writable = await handle.createWritable();
            await writable.write(content);
            await writable.close();
            return handle.name;              // actual filename chosen
        } catch (e) {
            if (e.name === 'AbortError') return null; // user cancelled
        }
    }
    // Fallback for browsers without File System Access API
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = defaultName;
    a.click();
    URL.revokeObjectURL(url);
    return defaultName;
}

async function loadFromFilePicker() {
    try {
        const data = await _openJsonFilePicker();
        if (!data) return;
        if (data.characters || data.lighting || data.version) {
            await loadSceneFromData(data, data.name || '');
        } else if (data.body_type) {
            clearAllCharacters();
            currentSceneName = '';
            const id = generateCharacterId();
            const inst = new CharacterInstance(id, data);
            await inst.load();
            characters.set(id, inst);
            scene.add(inst.group);
            updateCharacterListUI();
            updateVertexCount();
            selectCharacter(id);
        } else {
            alert('Unbekanntes JSON-Format. Erwartet: Szene oder Modell.');
        }
    } catch (e) {
        alert(`Fehler beim Laden: ${e.message}`);
    }
}

async function importModelFromFilePicker() {
    try {
        const data = await _openJsonFilePicker();
        if (!data) return;
        if (!data.body_type) {
            alert('Ungültiges Modell-JSON. Feld "body_type" fehlt.');
            return;
        }

        const id = generateCharacterId();
        const inst = new CharacterInstance(id, data);
        const xOffset = characters.size * 0.8;
        inst.group.position.set(xOffset, 0, 0);
        await inst.load();
        characters.set(id, inst);
        scene.add(inst.group);
        updateCharacterListUI();
        updateVertexCount();
        selectCharacter(id);
        markDirty();
    } catch (e) {
        alert(`Fehler beim Importieren: ${e.message}`);
    }
}

async function exportSceneJSON() {
    const data = gatherSceneState();
    await _saveJsonWithPicker(data, (currentSceneName || 'scene') + '.json');
}

async function exportModelJSON() {
    if (!selectedCharacterId) {
        alert('Bitte zuerst einen Charakter auswählen.');
        return;
    }
    const inst = characters.get(selectedCharacterId);
    if (!inst) return;

    let data;
    if (inst.generatedConfig) {
        // Generated model: export full generator config so it can be re-imported
        data = {
            ...inst.generatedConfig,
            type: 'generated_model',
            name: inst.presetName || inst.generatedConfig.name || 'Generiertes Modell',
            body_type: inst.generatedConfig.skeleton_type === 'rig' ? 'Rig Bones' : 'DEF Skeleton',
            skeleton_type: inst.generatedConfig.skeleton_type || 'def',
        };
    } else {
        data = {
            name: inst.presetName,
            body_type: inst.bodyType,
            morphs: inst.morphs || {},
            meta: inst.meta || {},
            cloth: inst.cloth || [],
            hair_style: inst.hairStyle || null,
            garments: inst.garments || [],
        };
    }
    await _saveJsonWithPicker(data, (inst.presetName || 'model') + '.json');
}

function bindVisibilityToggles() {
    const modelToggle = document.getElementById('model-toggle');
    if (modelToggle) {
        modelToggle.addEventListener('click', () => {
            toggleModelVisibility();
            modelToggle.classList.toggle('active', modelVisible);
        });
    }

    const clothesToggle = document.getElementById('clothes-toggle');
    if (clothesToggle) {
        clothesToggle.addEventListener('click', () => {
            clothesVisible = !clothesVisible;
            characters.forEach(inst => {
                for (const m of Object.values(inst.clothMeshes)) {
                    if (m) m.visible = clothesVisible;
                }
                if (inst.hairMesh) inst.hairMesh.visible = clothesVisible;
            });
            clothesToggle.classList.toggle('active', clothesVisible);
        });
    }

    const rigToggle = document.getElementById('rig-toggle');
    if (rigToggle) {
        rigToggle.addEventListener('click', () => {
            toggleRigVisibility();
            rigToggle.classList.toggle('active', rigVisible);
        });
    }
}

function toggleModelVisibility() {
    modelVisible = !modelVisible;
    characters.forEach(c => {
        if (c.bodyMesh) c.bodyMesh.visible = modelVisible;
    });
}

function toggleRigVisibility() {
    rigVisible = !rigVisible;
    if (rigVisible) {
        // Use per-character skeleton if available, else global
        const inst = _selectedInst();
        let skel = (inst && inst.rigifySkeleton) ? inst.rigifySkeleton : rigifySkeleton;
        // Build eagerly if data loaded but not yet constructed
        if (!skel && rigifySkeletonData && skinWeightData) {
            if (inst) {
                convertInstToSkinned(inst);
                skel = inst.rigifySkeleton;
            } else {
                rigifySkeleton = buildRigifySkeleton(rigifySkeletonData, skinWeightData);
                scene.add(rigifySkeleton.rootBone);
                skel = rigifySkeleton;
            }
        }
        if (!skeletonHelper && skel) {
            skeletonHelper = new THREE.SkeletonHelper(skel.rootBone);
            skeletonHelper.material.depthTest = false;
            skeletonHelper.material.depthWrite = false;
            skeletonHelper.material.transparent = true;
            skeletonHelper.material.color.set(0x00ffaa);
            skeletonHelper.material.linewidth = 2;
            skeletonHelper.renderOrder = 999;
            scene.add(skeletonHelper);
        }
        if (skeletonHelper) skeletonHelper.visible = true;
    } else {
        if (skeletonHelper) skeletonHelper.visible = false;
    }
}

function deleteSelectedCharacter() {
    if (!selectedCharacterId) return;
    const inst = characters.get(selectedCharacterId);
    if (inst) deleteCharacter(selectedCharacterId);
}

// =========================================================================
// Keyboard shortcuts
// =========================================================================
function bindKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
        // Ctrl shortcuts (work even in inputs)
        if (e.ctrlKey || e.metaKey) {
            switch (e.key.toLowerCase()) {
                case 's':
                    e.preventDefault();
                    if (e.shiftKey) {
                        openSaveDialog();
                    } else {
                        quickSave();
                    }
                    return;
                case 'o':
                    e.preventDefault();
                    openLoadDialog();
                    return;
                case 'n':
                    e.preventDefault();
                    newScene();
                    return;
                case 'm':
                    e.preventDefault();
                    if (e.shiftKey) sceneRedo();
                    else sceneUndo();
                    return;
            }
        }

        // Don't capture when typing in inputs
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;

        switch (e.key.toLowerCase()) {
            case 'g':
                setTransformMode('translate');
                break;
            case 'r':
                setTransformMode('rotate');
                break;
            case 's':
                setTransformMode('scale');
                break;
            case 'delete':
                if (_selectedSubMesh) {
                    _removeSubMesh(_selectedSubMesh);
                } else {
                    deleteSelectedCharacter();
                }
                break;
            case 'escape':
                deselectCharacter();
                closeAllMenus();
                closeAllDialogs();
                break;
        }
    });
}

// =========================================================================
// Character Add Dialog
// =========================================================================
let _addCharSelectedPreset = null;

function initCharacterDialog() {
    const addBtn = document.getElementById('add-character-btn');
    const dialog = document.getElementById('add-char-dialog');
    const confirmBtn = document.getElementById('add-char-confirm');

    // Panel button opens dialog too
    addBtn.addEventListener('click', () => openAddCharacterDialog());
    confirmBtn.addEventListener('click', doAddCharacter);

    async function doAddCharacter() {
        if (!_addCharSelectedPreset) return;
        closeDialog(dialog);
        try {
            await addCharacterFromPreset(_addCharSelectedPreset);
        } catch (e) {
            alert(`Fehler beim Laden: ${e.message}`);
        }
    }
}

async function openAddCharacterDialog() {
    const dialog = document.getElementById('add-char-dialog');
    const confirmBtn = document.getElementById('add-char-confirm');
    const presetList = document.getElementById('preset-list');

    openDialog(dialog);
    _addCharSelectedPreset = null;
    confirmBtn.disabled = true;
    presetList.innerHTML = '<li style="color:var(--text-muted)"><i class="fas fa-spinner fa-spin"></i> Lade Presets...</li>';

    try {
        const resp = await fetch('/api/character/models/');
        const data = await resp.json();
        presetList.innerHTML = '';

        if (!data.presets || data.presets.length === 0) {
            presetList.innerHTML = '<li style="color:var(--text-muted)">Keine Presets vorhanden. Erstelle zuerst ein Modell in der Konfiguration.</li>';
            return;
        }

        for (const p of data.presets) {
            const li = document.createElement('li');
            li.textContent = p.label || p.name;
            li.dataset.presetName = p.name;

            li.addEventListener('click', () => {
                presetList.querySelectorAll('li').forEach(x => x.classList.remove('selected'));
                li.classList.add('selected');
                _addCharSelectedPreset = p.name;
                confirmBtn.disabled = false;
            });

            li.addEventListener('dblclick', async () => {
                _addCharSelectedPreset = p.name;
                closeDialog(dialog);
                try {
                    await addCharacterFromPreset(_addCharSelectedPreset);
                } catch (e) {
                    alert(`Fehler beim Laden: ${e.message}`);
                }
            });

            presetList.appendChild(li);
        }
    } catch (e) {
        presetList.innerHTML = `<li style="color:#ef4444">Fehler: ${e.message}</li>`;
    }
}

// =========================================================================
// Scene Save/Load Dialogs
// =========================================================================
let _selectedFileToLoad = null;

function initSceneDialogs() {
    const saveDialog = document.getElementById('save-scene-dialog');
    const saveNameInput = document.getElementById('save-scene-name');
    const saveConfirm = document.getElementById('save-scene-confirm');

    saveConfirm.addEventListener('click', async () => {
        const name = saveNameInput.value.trim();
        if (!name) { saveNameInput.focus(); return; }
        closeDialog(saveDialog);
        await doSaveScene(name);
    });

    saveNameInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') saveConfirm.click();
    });

    const loadDialog = document.getElementById('load-scene-dialog');
    const loadConfirm = document.getElementById('load-scene-confirm');

    loadConfirm.addEventListener('click', async () => {
        if (!_selectedFileToLoad) return;
        closeDialog(loadDialog);
        try {
            await loadModelFile(_selectedFileToLoad);
        } catch (e) {
            alert(`Fehler beim Laden: ${e.message}`);
        }
    });

}

async function openSaveDialog() {
    const saveDialog = document.getElementById('save-scene-dialog');
    const saveNameInput = document.getElementById('save-scene-name');
    const saveList = document.getElementById('save-scene-list');

    openDialog(saveDialog);
    saveNameInput.value = currentSceneName || '';
    saveNameInput.focus();
    await loadSceneListInto(saveList, (name) => {
        saveNameInput.value = name;
    });
}

async function openLoadDialog() {
    const loadDialog = document.getElementById('load-scene-dialog');
    const loadConfirm = document.getElementById('load-scene-confirm');
    const tbody = document.getElementById('load-file-tbody');

    openDialog(loadDialog);
    _selectedFileToLoad = null;
    loadConfirm.disabled = true;
    tbody.innerHTML = '<tr><td colspan="3" style="padding:12px;color:var(--text-muted);text-align:center;"><i class="fas fa-spinner fa-spin"></i> Lade...</td></tr>';

    try {
        const resp = await fetch('/api/character/model-files/');
        const data = await resp.json();
        tbody.innerHTML = '';
        const files = data.files || [];
        if (files.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="padding:12px;color:var(--text-muted);text-align:center;">Keine Dateien vorhanden.</td></tr>';
            return;
        }
        for (const f of files) {
            const tr = document.createElement('tr');
            const isScene = f.type === 'scene';
            const icon = isScene ? 'fa-film' : 'fa-user';
            const typeBadge = isScene
                ? '<span class="file-type-scene">Szene</span>'
                : '<span class="file-type-model">Modell</span>';
            const dateStr = f.modified ? new Date(f.modified * 1000).toLocaleDateString('de-DE') : '';
            tr.innerHTML = `<td style="padding:4px 12px;"><i class="fas ${icon}" style="margin-right:6px;opacity:0.5;"></i>${escapeHtml(f.label || f.name)}</td>`
                + `<td style="padding:4px 12px;text-align:center;">${typeBadge}</td>`
                + `<td style="padding:4px 12px;text-align:right;color:var(--text-muted);font-size:0.7rem;">${dateStr}</td>`;
            tr.style.cursor = 'pointer';
            tr.addEventListener('click', () => {
                tbody.querySelectorAll('tr').forEach(r => r.classList.remove('selected'));
                tr.classList.add('selected');
                _selectedFileToLoad = f;
                loadConfirm.disabled = false;
            });
            tr.addEventListener('dblclick', () => {
                _selectedFileToLoad = f;
                closeDialog(loadDialog);
                loadModelFile(f).catch(e => alert(`Fehler beim Laden: ${e.message}`));
            });
            tbody.appendChild(tr);
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="3" style="padding:12px;color:#ef4444;text-align:center;">Fehler: ${e.message}</td></tr>`;
    }
}

async function loadSceneListInto(listEl, onSelect, onDblClick) {
    listEl.innerHTML = '<li style="color:var(--text-muted)"><i class="fas fa-spinner fa-spin"></i> Lade...</li>';
    try {
        const resp = await fetch('/api/character/scenes/');
        const data = await resp.json();
        listEl.innerHTML = '';
        if (!data.scenes || data.scenes.length === 0) {
            listEl.innerHTML = '<li style="color:var(--text-muted)">Keine Szenen vorhanden.</li>';
            return;
        }
        for (const s of data.scenes) {
            const li = document.createElement('li');
            li.innerHTML = `${escapeHtml(s.label || s.name)} <span class="preset-sub">${s.character_count} Charakter(e)</span>`;
            li.addEventListener('click', () => {
                listEl.querySelectorAll('li').forEach(x => x.classList.remove('selected'));
                li.classList.add('selected');
                onSelect(s.name);
            });
            if (onDblClick) {
                li.addEventListener('dblclick', () => onDblClick(s.name));
            }
            listEl.appendChild(li);
        }
    } catch (e) {
        listEl.innerHTML = `<li style="color:#ef4444">Fehler: ${e.message}</li>`;
    }
}

// =========================================================================
// Scene Save/Load Logic
// =========================================================================
function gatherSceneState() {
    const chars = [];
    characters.forEach(inst => chars.push(inst.toJSON()));

    return {
        version: 1,
        name: currentSceneName || 'Unnamed',
        characters: chars,
        lighting: {
            key: {
                intensity: keyLight.intensity,
                color: '#' + keyLight.color.getHexString(),
                pos: [keyLight.position.x, keyLight.position.y, keyLight.position.z]
            },
            fill: {
                intensity: fillLight.intensity,
                color: '#' + fillLight.color.getHexString(),
                pos: [fillLight.position.x, fillLight.position.y, fillLight.position.z]
            },
            back: {
                intensity: backLight.intensity,
                color: '#' + backLight.color.getHexString(),
                pos: [backLight.position.x, backLight.position.y, backLight.position.z]
            },
            ambient: {
                intensity: ambientLight.intensity,
                color: '#' + ambientLight.color.getHexString()
            }
        },
        renderer: {
            toneMapping: document.getElementById('tone-mapping').value,
            exposure: renderer.toneMappingExposure,
            background: '#' + scene.background.getHexString()
        },
        camera: {
            fov: camera.fov,
            position: camera.position.toArray(),
            target: controls.target.toArray()
        }
    };
}

function getCSRFToken() {
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

async function doSaveScene(name) {
    const data = gatherSceneState();
    data.name = name;

    try {
        const resp = await fetch('/api/character/scene/save/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify({ name, data }),
        });
        const result = await resp.json();
        if (result.ok) {
            currentSceneName = name;
            markClean();
            // Brief feedback in the Datei menu title
            const dateiTitle = document.querySelector('.menu:first-child .menu-title');
            if (dateiTitle) {
                const orig = dateiTitle.textContent;
                dateiTitle.textContent = 'Gespeichert!';
                dateiTitle.style.color = 'var(--accent)';
                setTimeout(() => { dateiTitle.textContent = orig; dateiTitle.style.color = ''; }, 1500);
            }
        } else {
            alert('Fehler: ' + (result.error || 'Unbekannt'));
        }
    } catch (e) {
        alert('Fehler: ' + e.message);
    }
}

async function loadModelFile(fileEntry) {
    if (fileEntry.type === 'scene') {
        await loadSceneFromServer(fileEntry.name);
    } else {
        // Model preset — clear existing and load as single character
        clearAllCharacters();
        currentSceneName = '';
        await addCharacterFromPreset(fileEntry.name);
    }
}

async function loadSceneFromData(data, sceneName) {
    // Clear existing
    clearAllCharacters();
    currentSceneName = sceneName || data.name || '';

    // Load characters
    if (data.characters) {
        for (const charData of data.characters) {
            try {
                const inst = await CharacterInstance.fromJSON(charData);
                characters.set(inst.id, inst);
                scene.add(inst.group);
            } catch (e) {
                console.error(`Failed to load character ${charData.presetName}:`, e);
            }
        }
    }

    // Apply lighting
    if (data.lighting) {
        if (data.lighting.key) {
            keyLight.intensity = data.lighting.key.intensity;
            keyLight.color.set(data.lighting.key.color);
            keyLight.position.set(...data.lighting.key.pos);
        }
        if (data.lighting.fill) {
            fillLight.intensity = data.lighting.fill.intensity;
            fillLight.color.set(data.lighting.fill.color);
            fillLight.position.set(...data.lighting.fill.pos);
        }
        if (data.lighting.back) {
            backLight.intensity = data.lighting.back.intensity;
            backLight.color.set(data.lighting.back.color);
            backLight.position.set(...data.lighting.back.pos);
        }
        if (data.lighting.ambient) {
            ambientLight.intensity = data.lighting.ambient.intensity;
            ambientLight.color.set(data.lighting.ambient.color);
        }
    }

    // Apply renderer
    if (data.renderer) {
        if (data.renderer.toneMapping && TONE_MAPPINGS[data.renderer.toneMapping] !== undefined) {
            renderer.toneMapping = TONE_MAPPINGS[data.renderer.toneMapping];
        }
        if (data.renderer.exposure !== undefined) {
            renderer.toneMappingExposure = data.renderer.exposure;
        }
        if (data.renderer.background) {
            scene.background.set(data.renderer.background);
        }
    }

    // Apply camera
    if (data.camera) {
        if (data.camera.fov) {
            camera.fov = data.camera.fov;
            camera.updateProjectionMatrix();
        }
        if (data.camera.position) camera.position.fromArray(data.camera.position);
        if (data.camera.target) controls.target.fromArray(data.camera.target);
        controls.update();
    }

    syncUIFromState();
    updateCharacterListUI();
    updateVertexCount();

    // Auto-select first character so Assets tab is immediately usable
    if (characters.size > 0 && !selectedCharacterId) {
        selectCharacter(characters.keys().next().value);
    }
}

async function loadSceneFromServer(name) {
    const resp = await fetch(`/api/character/scene/${encodeURIComponent(name)}/`);
    if (!resp.ok) throw new Error('Scene not found');
    const data = await resp.json();
    await loadSceneFromData(data, name);
}

function clearAllCharacters() {
    deselectCharacter();
    characters.forEach(inst => inst.dispose());
    characters.clear();
    updateCharacterListUI();
    updateVertexCount();
}

// =========================================================================
// Dialog helpers
// =========================================================================
function openDialog(overlay) {
    overlay.classList.add('visible');
}

function closeDialog(overlay) {
    overlay.classList.remove('visible');
}

function closeAllDialogs() {
    document.querySelectorAll('.scene-modal-overlay.visible').forEach(d => closeDialog(d));
}

// Bind close buttons and overlay click
document.querySelectorAll('.scene-modal-overlay').forEach(overlay => {
    overlay.querySelectorAll('[data-close]').forEach(btn => {
        btn.addEventListener('click', () => closeDialog(overlay));
    });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeDialog(overlay);
    });
});

// =========================================================================
// Mesh loading (legacy single body for preview when no characters added)
// =========================================================================
async function loadMesh() {
    try {
        const resp = await fetch('/api/character/mesh/');
        const data = await resp.json();
        if (data.error) { console.error(data.error); return; }

        document.getElementById('vertex-count').textContent =
            data.vertex_count.toLocaleString();

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const positions = new THREE.BufferAttribute(vertBuf, 3);

        let index = null;
        if (data.faces) {
            index = new THREE.BufferAttribute(base64ToUint32(data.faces), 1);
        }

        let uvAttr = null;
        if (data.uvs) {
            uvAttr = new THREE.BufferAttribute(base64ToFloat32(data.uvs), 2);
        }

        const materials = BODY_MATERIALS.map(d => new THREE.MeshStandardMaterial({
            color: d.color, roughness: d.roughness, metalness: d.metalness,
            side: THREE.DoubleSide,
            transparent: d.transparent || false,
            opacity: d.opacity !== undefined ? d.opacity : 1.0,
        }));

        let geo = new THREE.BufferGeometry();
        geo.setAttribute('position', positions);
        if (index) geo.setIndex(index);
        if (uvAttr) geo.setAttribute('uv', uvAttr);

        const groups = data.groups || [];

        if (data.normals) {
            const normalBuf = base64ToFloat32(data.normals);
            blenderToThreeCoords(normalBuf);
            geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));
        } else {
            geo.computeVertexNormals();
        }

        if (index && groups.length > 0) {
            for (const g of groups) {
                geo.addGroup(g.start, g.count, g.materialIndex);
            }
            bodyMesh = new THREE.Mesh(geo, materials);
        } else {
            bodyMesh = new THREE.Mesh(geo, materials[0]);
        }

        bodyGeometry = geo;
        scene.add(bodyMesh);

        document.getElementById('vertex-count').textContent =
            geo.attributes.position.count.toLocaleString();

        applySkinColor();
        onResize();
    } catch (e) {
        console.error('Failed to load mesh:', e);
    }
}

function getSkinMat() {
    if (!bodyMesh || !bodyMesh.material) return null;
    return Array.isArray(bodyMesh.material) ? bodyMesh.material[0] : bodyMesh.material;
}

function applySkinColor() {
    if (!Object.keys(skinColors).length) return;
    const colors = skinColors['Caucasian'];
    const mat = getSkinMat();
    if (colors && mat) {
        mat.color.setRGB(
            Math.pow(colors[0], 1/2.2),
            Math.pow(colors[1], 1/2.2),
            Math.pow(colors[2], 1/2.2)
        );
    }
}

async function loadSkinColors() {
    try {
        const data = await fetchMorphDefs();
        skinColors = data.skin_colors || {};
        applySkinColor();
    } catch (e) { /* optional */ }
}

async function loadHairColors() {
    try {
        const resp = await fetch('/api/character/hairstyles/');
        const data = await resp.json();
        hairColorData = data.colors || {};
    } catch (e) { /* optional */ }
}

// =========================================================================
// UI Bindings: Lighting
// =========================================================================
function bindLightingUI() {
    function bindSlider(id, displayId, toDisplay, onChange) {
        const slider = document.getElementById(id);
        const display = document.getElementById(displayId);
        slider.addEventListener('input', () => {
            const v = parseFloat(slider.value);
            display.textContent = toDisplay(v);
            onChange(v);
            autoSave();
        });
    }

    bindSlider('key-intensity', 'key-intensity-val', v => (v / 100).toFixed(1), v => {
        keyLight.intensity = v / 100;
    });
    document.getElementById('key-color').addEventListener('input', e => {
        keyLight.color.set(e.target.value); autoSave();
    });
    bindSlider('key-pos-x', 'key-pos-x-val', v => (v / 10).toFixed(1), v => {
        keyLight.position.x = v / 10;
    });
    bindSlider('key-pos-y', 'key-pos-y-val', v => (v / 10).toFixed(1), v => {
        keyLight.position.y = v / 10;
    });
    bindSlider('key-pos-z', 'key-pos-z-val', v => (v / 10).toFixed(1), v => {
        keyLight.position.z = v / 10;
    });

    bindSlider('fill-intensity', 'fill-intensity-val', v => (v / 100).toFixed(1), v => {
        fillLight.intensity = v / 100;
    });
    document.getElementById('fill-color').addEventListener('input', e => {
        fillLight.color.set(e.target.value); autoSave();
    });
    bindSlider('fill-pos-x', 'fill-pos-x-val', v => (v / 10).toFixed(1), v => {
        fillLight.position.x = v / 10;
    });
    bindSlider('fill-pos-y', 'fill-pos-y-val', v => (v / 10).toFixed(1), v => {
        fillLight.position.y = v / 10;
    });
    bindSlider('fill-pos-z', 'fill-pos-z-val', v => (v / 10).toFixed(1), v => {
        fillLight.position.z = v / 10;
    });

    bindSlider('back-intensity', 'back-intensity-val', v => (v / 100).toFixed(1), v => {
        backLight.intensity = v / 100;
    });
    document.getElementById('back-color').addEventListener('input', e => {
        backLight.color.set(e.target.value); autoSave();
    });
    bindSlider('back-pos-x', 'back-pos-x-val', v => (v / 10).toFixed(1), v => {
        backLight.position.x = v / 10;
    });
    bindSlider('back-pos-y', 'back-pos-y-val', v => (v / 10).toFixed(1), v => {
        backLight.position.y = v / 10;
    });
    bindSlider('back-pos-z', 'back-pos-z-val', v => (v / 10).toFixed(1), v => {
        backLight.position.z = v / 10;
    });

    bindSlider('ambient-intensity', 'ambient-intensity-val', v => (v / 100).toFixed(1), v => {
        ambientLight.intensity = v / 100;
    });
    document.getElementById('ambient-color').addEventListener('input', e => {
        ambientLight.color.set(e.target.value); autoSave();
    });

    document.getElementById('light-preset').addEventListener('change', e => {
        const preset = LIGHT_PRESETS[e.target.value];
        if (!preset) return;
        applyPreset(preset);
        autoSave();
    });
}

function applyPreset(preset) {
    keyLight.intensity = preset.key.intensity;
    keyLight.color.setHex(preset.key.color);
    keyLight.position.set(...preset.key.pos);

    fillLight.intensity = preset.fill.intensity;
    fillLight.color.setHex(preset.fill.color);
    fillLight.position.set(...preset.fill.pos);

    backLight.intensity = preset.back.intensity;
    backLight.color.setHex(preset.back.color);
    backLight.position.set(...preset.back.pos);

    ambientLight.intensity = preset.ambient.intensity;
    ambientLight.color.setHex(preset.ambient.color);

    renderer.toneMappingExposure = preset.exposure;

    syncUIFromState();
}

function syncUIFromState() {
    setSlider('key-intensity', keyLight.intensity * 100, 'key-intensity-val', v => (v / 100).toFixed(1));
    setColor('key-color', keyLight.color);
    setSlider('key-pos-x', keyLight.position.x * 10, 'key-pos-x-val', v => (v / 10).toFixed(1));
    setSlider('key-pos-y', keyLight.position.y * 10, 'key-pos-y-val', v => (v / 10).toFixed(1));
    setSlider('key-pos-z', keyLight.position.z * 10, 'key-pos-z-val', v => (v / 10).toFixed(1));

    setSlider('fill-intensity', fillLight.intensity * 100, 'fill-intensity-val', v => (v / 100).toFixed(1));
    setColor('fill-color', fillLight.color);
    setSlider('fill-pos-x', fillLight.position.x * 10, 'fill-pos-x-val', v => (v / 10).toFixed(1));
    setSlider('fill-pos-y', fillLight.position.y * 10, 'fill-pos-y-val', v => (v / 10).toFixed(1));
    setSlider('fill-pos-z', fillLight.position.z * 10, 'fill-pos-z-val', v => (v / 10).toFixed(1));

    setSlider('back-intensity', backLight.intensity * 100, 'back-intensity-val', v => (v / 100).toFixed(1));
    setColor('back-color', backLight.color);
    setSlider('back-pos-x', backLight.position.x * 10, 'back-pos-x-val', v => (v / 10).toFixed(1));
    setSlider('back-pos-y', backLight.position.y * 10, 'back-pos-y-val', v => (v / 10).toFixed(1));
    setSlider('back-pos-z', backLight.position.z * 10, 'back-pos-z-val', v => (v / 10).toFixed(1));

    setSlider('ambient-intensity', ambientLight.intensity * 100, 'ambient-intensity-val', v => (v / 100).toFixed(1));
    setColor('ambient-color', ambientLight.color);

    setSlider('exposure', renderer.toneMappingExposure * 100, 'exposure-val', v => (v / 100).toFixed(1));

    const tmSelect = document.getElementById('tone-mapping');
    for (const [name, val] of Object.entries(TONE_MAPPINGS)) {
        if (val === renderer.toneMapping) { tmSelect.value = name; break; }
    }

    setColor('bg-color', scene.background);
    setSlider('camera-fov', camera.fov, 'camera-fov-val', v => Math.round(v).toString());
}

function setSlider(id, value, displayId, toDisplay) {
    const slider = document.getElementById(id);
    slider.value = Math.round(value);
    document.getElementById(displayId).textContent = toDisplay(parseFloat(slider.value));
}

function setColor(id, threeColor) {
    document.getElementById(id).value = '#' + threeColor.getHexString();
}

// =========================================================================
// UI Bindings: Renderer
// =========================================================================
function bindRendererUI() {
    document.getElementById('tone-mapping').addEventListener('change', e => {
        renderer.toneMapping = TONE_MAPPINGS[e.target.value] || THREE.ACESFilmicToneMapping;
        autoSave();
    });

    const expSlider = document.getElementById('exposure');
    const expVal = document.getElementById('exposure-val');
    expSlider.addEventListener('input', () => {
        const v = parseFloat(expSlider.value) / 100;
        expVal.textContent = v.toFixed(1);
        renderer.toneMappingExposure = v;
        autoSave();
    });

    document.getElementById('bg-color').addEventListener('input', e => {
        scene.background.set(e.target.value);
        autoSave();
    });
}

// =========================================================================
// UI Bindings: Camera
// =========================================================================
function bindCameraUI() {
    const fovSlider = document.getElementById('camera-fov');
    const fovVal = document.getElementById('camera-fov-val');
    fovSlider.addEventListener('input', () => {
        const v = parseInt(fovSlider.value);
        fovVal.textContent = v;
        camera.fov = v;
        camera.updateProjectionMatrix();
        autoSave();
    });
}

// =========================================================================
// Actions
// =========================================================================
function bindActions() {
    document.getElementById('btn-apply').addEventListener('click', () => {
        const settings = gatherSettings();
        localStorage.setItem('humanbody_scene_settings', JSON.stringify(settings));
        const btn = document.getElementById('btn-apply');
        const orig = btn.textContent;
        btn.textContent = 'Gespeichert!';
        setTimeout(() => { btn.textContent = orig; }, 1500);
    });

    document.getElementById('btn-reset').addEventListener('click', () => {
        applyPreset(LIGHT_PRESETS.studio);
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        scene.background.set(0x1a1a2e);
        camera.fov = 35;
        camera.updateProjectionMatrix();
        document.getElementById('light-preset').value = 'studio';
        syncUIFromState();
        autoSave();
    });

    document.getElementById('btn-export').addEventListener('click', () => {
        const settings = gatherSettings();
        const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'humanbody_scene_settings.json';
        a.click();
        URL.revokeObjectURL(url);
    });
}

function gatherSettings() {
    return {
        lighting: {
            key: {
                intensity: keyLight.intensity,
                color: '#' + keyLight.color.getHexString(),
                pos: [keyLight.position.x, keyLight.position.y, keyLight.position.z]
            },
            fill: {
                intensity: fillLight.intensity,
                color: '#' + fillLight.color.getHexString(),
                pos: [fillLight.position.x, fillLight.position.y, fillLight.position.z]
            },
            back: {
                intensity: backLight.intensity,
                color: '#' + backLight.color.getHexString(),
                pos: [backLight.position.x, backLight.position.y, backLight.position.z]
            },
            ambient: {
                intensity: ambientLight.intensity,
                color: '#' + ambientLight.color.getHexString()
            }
        },
        renderer: {
            toneMapping: document.getElementById('tone-mapping').value,
            exposure: renderer.toneMappingExposure,
            background: '#' + scene.background.getHexString()
        },
        camera: {
            fov: camera.fov
        },
    };
}

// =========================================================================
// Load settings from localStorage
// =========================================================================
function loadSettings() {
    const saved = localStorage.getItem('humanbody_scene_settings');
    if (!saved) return;

    try {
        const s = JSON.parse(saved);

        if (s.lighting) {
            if (s.lighting.key) {
                keyLight.intensity = s.lighting.key.intensity;
                keyLight.color.set(s.lighting.key.color);
                keyLight.position.set(...s.lighting.key.pos);
            }
            if (s.lighting.fill) {
                fillLight.intensity = s.lighting.fill.intensity;
                fillLight.color.set(s.lighting.fill.color);
                fillLight.position.set(...s.lighting.fill.pos);
            }
            if (s.lighting.back) {
                backLight.intensity = s.lighting.back.intensity;
                backLight.color.set(s.lighting.back.color);
                backLight.position.set(...s.lighting.back.pos);
            }
            if (s.lighting.ambient) {
                ambientLight.intensity = s.lighting.ambient.intensity;
                ambientLight.color.set(s.lighting.ambient.color);
            }
        }

        if (s.renderer) {
            if (s.renderer.toneMapping && TONE_MAPPINGS[s.renderer.toneMapping] !== undefined) {
                renderer.toneMapping = TONE_MAPPINGS[s.renderer.toneMapping];
            }
            if (s.renderer.exposure !== undefined) {
                renderer.toneMappingExposure = s.renderer.exposure;
            }
            if (s.renderer.background) {
                scene.background.set(s.renderer.background);
            }
        }

        if (s.camera && s.camera.fov) {
            camera.fov = s.camera.fov;
            camera.updateProjectionMatrix();
        }

        document.getElementById('light-preset').value = '';
        syncUIFromState();

    } catch (e) {
        console.warn('Failed to load scene settings:', e);
    }
}

// =========================================================================
// DEF Skeleton + Skin Weights + BVH Animation
// =========================================================================
async function loadRigifySkeleton() {
    try {
        const resp = await fetch('/api/character/rigify-skeleton/');
        if (resp.ok) rigifySkeletonData = await resp.json();
    } catch (e) { /* optional */ }
}

async function loadSkinWeights() {
    try {
        const resp = await fetch('/api/character/skin-weights/');
        if (resp.ok) skinWeightData = await resp.json();
    } catch (e) { /* optional */ }
}

// buildRigifySkeleton() imported from rigify_skeleton_builder.js

function convertToRigifySkinnedMesh() {
    if (isSkinned || !bodyMesh || !bodyGeometry || !skinWeightData) return;
    bodyGeometry = bodyGeometry.clone();
    const vCount = bodyGeometry.attributes.position.count;
    const skinIndices = new Float32Array(vCount * 4);
    const skinWeights = new Float32Array(vCount * 4);
    for (let v = 0; v < vCount; v++) {
        const infs = skinWeightData.weights[v] || [];
        const sorted = infs.slice().sort((a, b) => b[1] - a[1]).slice(0, 4);
        let sum = sorted.reduce((s, e) => s + e[1], 0);
        if (sum < 1e-6) sum = 1;
        for (let i = 0; i < 4; i++) {
            skinIndices[v * 4 + i] = i < sorted.length ? sorted[i][0] : 0;
            skinWeights[v * 4 + i] = i < sorted.length ? sorted[i][1] / sum : 0;
        }
    }
    bodyGeometry.setAttribute('skinIndex', new THREE.Float32BufferAttribute(skinIndices, 4));
    bodyGeometry.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeights, 4));
    rigifySkeleton = buildRigifySkeleton(rigifySkeletonData, skinWeightData);
    const mat = bodyMesh.material;
    const pos = bodyMesh.position.clone();
    const vis = bodyMesh.visible;
    scene.remove(bodyMesh);
    bodyMesh = new THREE.SkinnedMesh(bodyGeometry, mat);
    bodyMesh.position.copy(pos);
    bodyMesh.visible = vis;
    bodyMesh.add(rigifySkeleton.rootBone);
    bodyMesh.bind(rigifySkeleton.skeleton);
    scene.add(bodyMesh);
    isSkinned = true;
}

/** Convert a CharacterInstance body to SkinnedMesh for animation. */
function convertInstToSkinned(inst) {
    if (inst.isSkinned || !inst.bodyMesh || !skinWeightData || !rigifySkeletonData) return;
    // Generated models have their own skinning (DEF) or none (Rig) — never apply body skin weights
    if (inst.generatedConfig) return;
    const geo = inst.bodyMesh.geometry.clone();
    const vCount = geo.attributes.position.count;
    const skinIndices = new Float32Array(vCount * 4);
    const skinWeights = new Float32Array(vCount * 4);
    for (let v = 0; v < vCount; v++) {
        const infs = skinWeightData.weights[v] || [];
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
    inst.rigifySkeleton = buildRigifySkeleton(rigifySkeletonData, skinWeightData);
    const mat = inst.bodyMesh.material;
    const vis = inst.bodyMesh.visible;
    inst.group.remove(inst.bodyMesh);
    inst.bodyMesh = new THREE.SkinnedMesh(geo, mat);
    inst.bodyMesh.visible = vis;
    inst.bodyMesh.add(inst.rigifySkeleton.rootBone);
    inst.bodyMesh.bind(inst.rigifySkeleton.skeleton);
    inst.group.add(inst.bodyMesh);
    inst.isSkinned = true;

    // Re-skin hair if already loaded (hair was added as plain mesh before skinning)
    if (inst.hairMesh) {
        inst.group.remove(inst.hairMesh);
        // Re-load hair to get fresh geometry for skinning
        inst._loadHair();
    }
}

/**
 * Create SkinnedMesh (if skin data available) or plain Mesh.
 * `inst` is a CharacterInstance, `data` is the API response with optional
 * skin_indices / skin_weights base64 fields.
 */
function _skinifyMesh(geo, mat, inst, data) {
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
function _findHeadBoneIndex() {
    if (!skinWeightData) return -1;
    const names = skinWeightData.bone_names;
    for (const tryName of ['DEF-spine.006', 'DEF-spine.005', 'DEF-head']) {
        const idx = names.indexOf(tryName);
        if (idx >= 0) return idx;
    }
    return -1;
}

/**
 * Convert all meshes in a GLTF scene (hair) to SkinnedMesh bound to head bone.
 * `inst` is a CharacterInstance that must already be skinned.
 */
function _skinifyHairGroup(gltfScene, inst) {
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

// Flag to suppress hover handler during garment refit
let _refitting = false;

async function loadBVHAnimation(url, name, fc, rawBvhText = null) {
    stopAnimation(true);
    currentAnimUrl = url;
    const groundChk = document.getElementById('scene-ground-fix');
    currentAnimGroundFixed = groundChk ? groundChk.checked : false;

    // Determine target: selected character instance, or legacy bodyMesh
    const inst = _selectedInst();
    const targetMesh = inst ? inst.bodyMesh : bodyMesh;
    if (!targetMesh) return;

    // Set up skinned mesh if needed
    let skel = null;
    if (rigifySkeletonData && skinWeightData) {
        if (inst) {
            if (!inst.isSkinned) convertInstToSkinned(inst);
        } else {
            if (!isSkinned) convertToRigifySkinnedMesh();
        }
        skel = inst ? inst.rigifySkeleton : rigifySkeleton;
    }

    if (skel) {
        const bMesh = inst ? inst.bodyMesh : bodyMesh;
        _animatedCharId = inst ? inst.id : null;

        let bodyH = 1.68;
        const bb = new THREE.Box3().setFromObject(bMesh);
        if (!bb.isEmpty()) bodyH = bb.max.y - bb.min.y;

        try {
            let clip;
            if (rawBvhText) {
                clip = await fetchRetargetedClipFromText(rawBvhText, skel, { bodyHeight: bodyH, deltaNorm: _sceneDeltaNorm });
                currentAnimBvhText = rawBvhText;
            } else {
                clip = await fetchRetargetedClipFromUrl(url, skel, { bodyHeight: bodyH, deltaNorm: _sceneDeltaNorm });
                // Also fetch the raw text for BVH editing features
                try {
                    const bustUrl = url + (url.includes('?') ? '&' : '?') + '_t=' + Date.now();
                    const textResp = await fetch(bustUrl);
                    currentAnimBvhText = await textResp.text();
                } catch { currentAnimBvhText = ''; }
            }
            console.log(`[ANIM] Retargeted clip: ${clip.duration.toFixed(2)}s, ${clip.tracks.length} tracks`);
            if (!skeletonHelper) {
                skeletonHelper = new THREE.SkeletonHelper(skel.rootBone);
                skeletonHelper.material.depthTest = false;
                skeletonHelper.material.depthWrite = false;
                skeletonHelper.material.color.set(0x00ffaa);
                skeletonHelper.renderOrder = 999;
                skeletonHelper.visible = rigVisible;
                scene.add(skeletonHelper);
            }
            mixer = new THREE.AnimationMixer(bMesh);
            currentAction = mixer.clipAction(clip);
            currentAction.play();
            playing = true;
        } catch (e) {
            console.error('[ANIM] Server retarget failed:', e);
        }
    } else {
        // Fallback: skeleton-only preview (no skin weights or un-skinnable model)
        const handleBvhFallback = (result, text) => {
            currentAnimBvhText = text;
            const bvhBones = result.skeleton.bones;
            if (bvhBones.length === 0) return;

            const rootBone = bvhBones[0];
            rootBone.updateWorldMatrix(true, true);
            const skelBox = new THREE.Box3();
            const tmpVec = new THREE.Vector3();
            bvhBones.forEach(b => { b.updateWorldMatrix(true, false); b.getWorldPosition(tmpVec); skelBox.expandByPoint(tmpVec); });
            let bodyHeight = 1.75;
            if (targetMesh) { const bb = new THREE.Box3().setFromObject(targetMesh); if (!bb.isEmpty()) bodyHeight = bb.max.y - bb.min.y; }
            const scale = bodyHeight / Math.max(skelBox.max.y - skelBox.min.y, 0.01);
            skelWrapper = new THREE.Group();
            skelWrapper.scale.set(scale, scale, scale);
            skelWrapper.add(rootBone);
            // Position skeleton at the character's group position
            if (inst) skelWrapper.position.copy(inst.group.position);
            scene.add(skelWrapper);
            if (skeletonHelper) scene.remove(skeletonHelper);
            skeletonHelper = new THREE.SkeletonHelper(rootBone);
            skeletonHelper.material.depthTest = false;
            skeletonHelper.material.depthWrite = false;
            skeletonHelper.material.color.set(0x00ffaa);
            skeletonHelper.renderOrder = 999;
            skeletonHelper.visible = rigVisible;
            scene.add(skeletonHelper);
            mixer = new THREE.AnimationMixer(rootBone);
            currentAction = mixer.clipAction(result.clip);
            currentAction.play();
            playing = true;
            _animatedCharId = inst ? inst.id : null;
        };

        if (rawBvhText) {
            const result = bvhLoader.parse(rawBvhText);
            handleBvhFallback(result, rawBvhText);
        } else {
            // Use FileLoader (XHR) for reliable large-file loading
            const fileLoader = new THREE.FileLoader(bvhLoader.manager);
            fileLoader.setRequestHeader(bvhLoader.requestHeader);
            fileLoader.setWithCredentials(bvhLoader.withCredentials);
            // Cache-bust to avoid stale browser cache from previous fetch calls
            const bustUrl = url + (url.includes('?') ? '&' : '?') + '_t=' + Date.now();
            fileLoader.load(bustUrl, (text) => {
                console.log(`[ANIM] FileLoader received ${text.length} chars (${(text.length/1024/1024).toFixed(2)} MB)`);
                const result = bvhLoader.parse(text);
                handleBvhFallback(result, text);
            }, undefined, (err) => { console.error('Failed to load BVH:', err); });
        }
    }
    // Sync play button icon
    const _pb = document.getElementById('anim-play');
    if (_pb) _pb.innerHTML = playing ? '<i class="fas fa-pause"></i>' : '<i class="fas fa-play"></i>';
}

function stopAnimation(destroy = false) {
    if (currentAction) { currentAction.stop(); currentAction.reset(); if (destroy) currentAction = null; }
    if (mixer && destroy) { mixer.stopAllAction(); mixer = null; }
    // Reset skeleton pose on the correct target
    if (_animatedCharId) {
        const inst = characters.get(_animatedCharId);
        if (inst && inst.isSkinned && inst.rigifySkeleton) inst.rigifySkeleton.skeleton.pose();
    } else {
        if (isSkinned && rigifySkeleton) rigifySkeleton.skeleton.pose();
    }
    if (skelWrapper) { scene.remove(skelWrapper); skelWrapper = null; }
    if (skeletonHelper) { scene.remove(skeletonHelper); skeletonHelper = null; }
    // Rebuild rig helper if rig is visible
    const activeSkel = _animatedCharId
        ? characters.get(_animatedCharId)?.rigifySkeleton
        : rigifySkeleton;
    if (rigVisible && activeSkel) {
        skeletonHelper = new THREE.SkeletonHelper(activeSkel.rootBone);
        skeletonHelper.material.depthTest = false;
        skeletonHelper.material.depthWrite = false;
        skeletonHelper.material.color.set(0x00ffaa);
        skeletonHelper.renderOrder = 999;
        scene.add(skeletonHelper);
    }
    _animatedCharId = null;
    playing = false;
    currentAnimUrl = '';
    currentAnimBvhText = '';
    currentAnimGroundFixed = false;
}

// =========================================================================
// Animation Ground-Fix & Save
// =========================================================================

async function applyGroundLevelFix() {
    if (!currentAnimBvhText) {
        alert('Keine Animation geladen.');
        return;
    }

    // Enable runtime ground fix while we process
    const chk = document.getElementById('scene-ground-fix');
    if (chk) chk.checked = true;
    currentAnimGroundFixed = true;

    // Modify BVH text: parse, FK per frame, correct Y, save
    const lines = currentAnimBvhText.split('\n');

    // Find Yposition channel
    let yPosChannel = -1, foundRoot = false;
    for (let i = 0; i < lines.length; i++) {
        const trimmed = lines[i].trim();
        if (trimmed.startsWith('ROOT ')) { foundRoot = true; continue; }
        if (foundRoot && trimmed.startsWith('CHANNELS')) {
            const parts = trimmed.split(/\s+/);
            for (let c = 2; c < parts.length; c++) {
                if (parts[c] === 'Yposition') { yPosChannel = c - 2; break; }
            }
            break;
        }
    }
    if (yPosChannel < 0) { alert('Yposition nicht gefunden.'); return; }

    // Find frame data
    let motionIdx = lines.findIndex(l => l.trim() === 'MOTION');
    if (motionIdx < 0) return;
    let frameTime = 1/30, dataStart = motionIdx + 1;
    while (dataStart < lines.length && !lines[dataStart].trim().match(/^[\d\-\.]/)) {
        const t = lines[dataStart].trim();
        if (t.startsWith('Frame Time:')) frameTime = parseFloat(t.split(':')[1].trim());
        dataStart++;
    }
    const frameLineIdx = [];
    for (let i = dataStart; i < lines.length; i++) {
        if (lines[i].trim().match(/^[\d\-\.]/)) frameLineIdx.push(i);
    }
    const totalFrames = frameLineIdx.length;
    if (!totalFrames) return;

    // FK per frame, correct
    const parsed = bvhLoader.parse(currentAnimBvhText);
    const bones = parsed.skeleton.bones;
    const rootBone = bones[0];
    const tmpMixer = new THREE.AnimationMixer(rootBone);
    const tmpAction = tmpMixer.clipAction(parsed.clip);
    tmpAction.play();
    const tmpV = new THREE.Vector3();
    let corrected = 0;

    for (let f = 0; f < totalFrames; f++) {
        tmpMixer.setTime(f * frameTime);
        rootBone.updateWorldMatrix(true, true);
        let minY = Infinity;
        for (const b of bones) { b.getWorldPosition(tmpV); if (tmpV.y < minY) minY = tmpV.y; }
        if (Math.abs(minY) > 0.001) {
            const li = frameLineIdx[f];
            const vals = lines[li].trim().split(/\s+/);
            vals[yPosChannel] = (parseFloat(vals[yPosChannel]) - minY).toFixed(6);
            lines[li] = vals.join(' ');
            corrected++;
        }
    }
    tmpAction.stop(); tmpMixer.stopAllAction();

    if (corrected === 0) { alert('Bereits auf Bodenniveau.'); return; }

    const modifiedBvh = lines.join('\n');
    currentAnimBvhText = modifiedBvh;
    console.log(`[GROUND] ${corrected}/${totalFrames} Frames korrigiert, speichere...`);

    // Save BVH file via API
    if (currentAnimUrl) {
        // Parse category/name from URL like /api/character/bvh/Results/nussie1/
        const urlPath = currentAnimUrl.replace(/\?.*$/, '');
        const bvhMatch = urlPath.match(/\/api\/character\/bvh\/([^/]+)\/([^/]+)/);
        const saveBody = bvhMatch
            ? { category: bvhMatch[1], name: bvhMatch[2], bvh_text: modifiedBvh }
            : { path: urlPath, bvh_text: modifiedBvh };
        try {
            const resp = await fetch('/api/character/save-bvh-text/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(saveBody),
            });
            if (resp.ok) {
                console.log('[GROUND] BVH gespeichert:', urlPath);
                // Invalidate retarget cache by reloading
                loadBVHAnimation(currentAnimUrl + (currentAnimUrl.includes('?') ? '&' : '?') + '_ground=' + Date.now(), currentAnimName, 0);
            } else {
                console.warn('[GROUND] Save failed:', await resp.text());
                // Fallback: reload from modified text
                loadBVHAnimation(currentAnimUrl, currentAnimName, 0, modifiedBvh);
            }
        } catch (e) {
            console.warn('[GROUND] Save error:', e);
            loadBVHAnimation(currentAnimUrl, currentAnimName, 0, modifiedBvh);
        }
    }
    alert(`Bodenniveau-Fix: ${corrected} von ${totalFrames} Frames korrigiert und gespeichert.`);
}

async function _applyGroundLevelFix_legacy() {
    if (!currentAnimBvhText) {
        alert('Keine Animation geladen.');
        return;
    }

    const lines = currentAnimBvhText.split('\n');

    // 1. Find Yposition channel index
    let yPosChannel = -1;
    let foundRoot = false;
    for (let i = 0; i < lines.length; i++) {
        const trimmed = lines[i].trim();
        if (trimmed.startsWith('ROOT ')) { foundRoot = true; continue; }
        if (foundRoot && trimmed.startsWith('CHANNELS')) {
            const parts = trimmed.split(/\s+/);
            for (let c = 2; c < parts.length; c++) {
                if (parts[c] === 'Yposition') { yPosChannel = c - 2; break; }
            }
            break;
        }
    }
    if (yPosChannel < 0) { alert('Yposition-Kanal nicht gefunden.'); return; }

    // 2. Find frame data lines
    let motionIdx = lines.findIndex(l => l.trim() === 'MOTION');
    if (motionIdx < 0) return;

    let frameTime = 1 / 30;
    let dataStart = motionIdx + 1;
    while (dataStart < lines.length && !lines[dataStart].trim().match(/^[\d\-\.]/)) {
        const t = lines[dataStart].trim();
        if (t.startsWith('Frame Time:')) frameTime = parseFloat(t.split(':')[1].trim());
        dataStart++;
    }

    const frameLineIdx = [];
    for (let i = dataStart; i < lines.length; i++) {
        if (lines[i].trim().match(/^[\d\-\.]/)) frameLineIdx.push(i);
    }
    const totalFrames = frameLineIdx.length;
    if (totalFrames === 0) { alert('Keine Frames.'); return; }

    // 3. FK per frame — find lowest bone Y, correct if below 0
    const parsed = bvhLoader.parse(currentAnimBvhText);
    const bones = parsed.skeleton.bones;
    const rootBone = bones[0];
    const tmpMixer = new THREE.AnimationMixer(rootBone);
    const tmpAction = tmpMixer.clipAction(parsed.clip);
    tmpAction.play();
    const tmpV = new THREE.Vector3();

    let corrected = 0;
    for (let f = 0; f < totalFrames; f++) {
        tmpMixer.setTime(f * frameTime);
        rootBone.updateWorldMatrix(true, true);

        // Find lowest bone
        let minY = Infinity;
        for (const b of bones) {
            b.getWorldPosition(tmpV);
            if (tmpV.y < minY) minY = tmpV.y;
        }

        // Correct every frame: push down if floating, push up if underground
        // Target: lowest bone sits exactly at Y=0 (ground level)
        if (Math.abs(minY) > 0.001) {
            const li = frameLineIdx[f];
            const vals = lines[li].trim().split(/\s+/);
            vals[yPosChannel] = (parseFloat(vals[yPosChannel]) - minY).toFixed(6);
            lines[li] = vals.join(' ');
            corrected++;
        }
    }
    tmpAction.stop();
    tmpMixer.stopAllAction();

    if (corrected === 0) {
        alert('Animation ist bereits auf Bodenniveau.');
        return;
    }

    const modifiedBvh = lines.join('\n');
    currentAnimBvhText = modifiedBvh;
    currentAnimGroundFixed = true;
    console.log(`[GROUND] ${corrected}/${totalFrames} Frames korrigiert`);

    // Save and reload
    const savePath = currentAnimUrl.replace(/\?.*$/, '').replace(/\.bvh$/i, '_ground.bvh');
    try {
        await fetch('/api/character/save-bvh-text/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: savePath, bvh_text: modifiedBvh }),
        });
        loadBVHAnimation(savePath + '?t=' + Date.now(), currentAnimName + ' (ground)', 0);
    } catch (e) {
        console.warn('[GROUND] Save failed:', e);
        loadBVHAnimation(currentAnimUrl, currentAnimName, 0, modifiedBvh);
    }
}

function openSaveAnimDialog() {
    if (!currentAnimBvhText) {
        alert('Keine Animation geladen.');
        return;
    }

    // Parse category + name from currentAnimUrl
    // URL format: /api/character/bvh/{category}/{name}/
    let category = '', baseName = '';
    const m = currentAnimUrl.match(/\/api\/character\/bvh\/([^/]+)\/([^/]+)\/?/);
    if (m) {
        category = decodeURIComponent(m[1]);
        baseName = decodeURIComponent(m[2]);
    } else {
        category = 'Custom';
        baseName = currentAnimName || 'animation';
    }

    // Suggest name with _ground suffix if ground-fixed
    let suggestedName = baseName;
    if (currentAnimGroundFixed && !baseName.endsWith('_ground')) {
        suggestedName = baseName + '_ground';
    }

    document.getElementById('save-anim-category').value = category;
    document.getElementById('save-anim-name').value = suggestedName;

    const dlg = document.getElementById('save-anim-dialog');
    dlg.classList.add('visible');
}

function _initSaveAnimDialog() {
    const dlg = document.getElementById('save-anim-dialog');
    if (!dlg) return;

    // Close buttons
    dlg.querySelectorAll('[data-close]').forEach(btn => {
        btn.addEventListener('click', () => dlg.classList.remove('visible'));
    });
    dlg.addEventListener('click', (e) => {
        if (e.target === dlg) dlg.classList.remove('visible');
    });

    // Save confirm
    document.getElementById('save-anim-confirm')?.addEventListener('click', async () => {
        const category = document.getElementById('save-anim-category').value.trim();
        const name = document.getElementById('save-anim-name').value.trim();
        if (!name) { alert('Bitte Dateiname eingeben.'); return; }

        try {
            const resp = await fetch('/api/character/animation/save/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
                body: JSON.stringify({ category, name, bvh_content: currentAnimBvhText })
            });
            const data = await resp.json();
            if (data.ok) {
                dlg.classList.remove('visible');
                // Update currentAnimUrl to saved location
                currentAnimUrl = `/api/character/bvh/${encodeURIComponent(category)}/${encodeURIComponent(name)}/`;
                currentAnimName = name;
                // Refresh animation list
                loadAnimationUI();
            } else {
                alert('Fehler: ' + (data.error || 'Unbekannt'));
            }
        } catch (e) {
            alert('Speichern fehlgeschlagen: ' + e.message);
        }
    });
}

// =========================================================================
// Utility
// =========================================================================
function base64ToFloat32(b64) {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new Float32Array(bytes.buffer);
}

function base64ToUint32(b64) {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new Uint32Array(bytes.buffer);
}

function blenderToThreeCoords(buf) {
    for (let i = 0; i < buf.length; i += 3) {
        const y = buf[i + 1];
        const z = buf[i + 2];
        buf[i + 1] = z;
        buf[i + 2] = -y;
    }
}

// =========================================================================
// Tabs + Properties Panel
// =========================================================================
function initTabs() {
    document.querySelectorAll('.panel-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            switchTab(tab.dataset.tab);
            if (tab.dataset.tab === 'modell') initModelGenerator();
        });
    });

    // Reset morphs button
    const resetBtn = document.getElementById('prop-reset-morphs');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (!currentPropsCharId) return;
            const inst = characters.get(currentPropsCharId);
            if (!inst) return;
            inst.morphs = {};
            populateMorphSliders(inst);
            reloadCharacterMesh(inst);
        });
    }

    // Refit garments & hair button
    const refitBtn = document.getElementById('prop-refit-btn');
    if (refitBtn) {
        refitBtn.addEventListener('click', () => _refitAllForCurrentChar());
    }
}

function switchTab(tabName) {
    document.querySelectorAll('.panel-tab').forEach(t => {
        t.classList.toggle('active', t.dataset.tab === tabName);
    });
    document.querySelectorAll('.tab-pane').forEach(p => {
        p.classList.toggle('active', p.id === `tab-${tabName}`);
    });
}

async function fetchMorphDefs() {
    // Re-fetch if not yet loaded or if previous fetch returned empty morphs
    if (morphDefs && morphDefs.morphs && morphDefs.morphs.length > 0) {
        return morphDefs;
    }
    const resp = await fetch('/api/character/morphs/');
    morphDefs = await resp.json();
    return morphDefs;
}

async function populateProperties(charId) {
    const inst = characters.get(charId);
    if (!inst) return;

    currentPropsCharId = charId;

    // Immediately show property/asset panels (before async fetch)
    document.getElementById('prop-empty').style.display = 'none';
    document.getElementById('prop-content').style.display = '';
    document.getElementById('assets-empty').style.display = 'none';
    document.getElementById('assets-content').style.display = '';

    // Fetch morph definitions
    try {
        await fetchMorphDefs();
    } catch (e) {
        console.error('Failed to fetch morph defs:', e);
        return;
    }

    populateTransform(inst);
    updateEquippedList(inst);
    populateBodyType(inst);
    populateMetaSliders(inst);
    populateMorphSliders(inst);
    syncHairSelect(inst);

    _updatePropContext();
    // Don't switch away from Modell tab (model generator needs to stay visible)
    const activeTab = document.querySelector('.panel-tab.active');
    if (!activeTab || activeTab.dataset.tab !== 'modell') {
        switchTab('eigenschaften');
    }
}

function clearProperties() {
    clearSubMeshSelection();
    currentPropsCharId = null;
    document.getElementById('prop-empty').style.display = '';
    document.getElementById('prop-content').style.display = 'none';
    document.getElementById('assets-empty').style.display = '';
    document.getElementById('assets-content').style.display = 'none';
}

function populateTransform(inst) {
    const grid = document.getElementById('prop-transform');
    grid.innerHTML = '';

    const rows = [
        { label: 'Pos', prop: 'position', step: 0.01 },
        { label: 'Rot', prop: 'rotation', step: 1, isDeg: true },
        { label: 'Scale', prop: 'scale', step: 0.01 },
    ];
    const axes = ['x', 'y', 'z'];

    for (const row of rows) {
        const lbl = document.createElement('label');
        lbl.textContent = row.label;
        grid.appendChild(lbl);

        for (const axis of axes) {
            const input = document.createElement('input');
            input.type = 'number';
            input.step = row.step;
            input.dataset.prop = row.prop;
            input.dataset.axis = axis;
            input.className = 'prop-transform-input';

            let val;
            if (row.isDeg) {
                val = THREE.MathUtils.radToDeg(inst.group.rotation[axis]);
            } else {
                val = inst.group[row.prop][axis];
            }
            input.value = parseFloat(val.toFixed(3));

            input.addEventListener('input', () => {
                const num = parseFloat(input.value);
                if (isNaN(num)) return;
                if (row.isDeg) {
                    inst.group.rotation[axis] = THREE.MathUtils.degToRad(num);
                } else {
                    inst.group[row.prop][axis] = num;
                }
                updateCharacterListUI();
            });

            grid.appendChild(input);
        }
    }
}

function syncTransformInputs() {
    const inst = characters.get(currentPropsCharId);
    if (!inst) return;

    document.querySelectorAll('.prop-transform-input').forEach(input => {
        const prop = input.dataset.prop;
        const axis = input.dataset.axis;
        if (!prop || !axis) return;

        // Don't update if this input is focused (user is typing)
        if (document.activeElement === input) return;

        let val;
        if (prop === 'rotation') {
            val = THREE.MathUtils.radToDeg(inst.group.rotation[axis]);
        } else {
            val = inst.group[prop][axis];
        }
        input.value = parseFloat(val.toFixed(3));
    });
}

function populateBodyType(inst) {
    const select = document.getElementById('prop-body-type');
    select.innerHTML = '';

    if (morphDefs && morphDefs.body_types) {
        for (const bt of morphDefs.body_types) {
            const opt = document.createElement('option');
            opt.value = bt;
            opt.textContent = bt.replace(/_/g, ' ');
            select.appendChild(opt);
        }
    }
    select.value = inst.bodyType;

    // Remove old listener by cloning
    const newSelect = select.cloneNode(true);
    select.parentNode.replaceChild(newSelect, select);

    newSelect.addEventListener('change', () => {
        inst.bodyType = newSelect.value;
        reloadCharacterMesh(inst);
    });
}

function populateMetaSliders(inst) {
    const container = document.getElementById('prop-meta-sliders');
    container.innerHTML = '';

    if (!morphDefs || !morphDefs.meta_sliders) return;

    for (const [name, meta] of Object.entries(morphDefs.meta_sliders)) {
        const neutral = (meta.min + meta.max) / 2;
        const half = (meta.max - meta.min) / 2;
        const internal = inst.meta[name] || 0;
        const displayVal = neutral + internal * half;

        const row = document.createElement('div');
        row.className = 'slider-row';

        const label = document.createElement('label');
        label.textContent = meta.label || name;
        label.style.minWidth = '80px';

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = meta.min;
        slider.max = meta.max;
        slider.step = 1;
        slider.value = Math.round(displayVal);

        const valSpan = document.createElement('span');
        valSpan.className = 'slider-val';
        valSpan.textContent = Math.round(displayVal);

        slider.addEventListener('input', () => {
            valSpan.textContent = slider.value;
        });

        slider.addEventListener('change', () => {
            const dv = parseFloat(slider.value);
            const internalVal = (dv - neutral) / half;
            inst.meta[name] = internalVal;
            reloadCharacterMesh(inst);
        });

        row.appendChild(label);
        row.appendChild(slider);
        row.appendChild(valSpan);
        container.appendChild(row);
    }
}

function populateMorphSliders(inst) {
    const container = document.getElementById('prop-morphs-panel');
    container.innerHTML = '';

    if (!morphDefs || !morphDefs.morphs || !morphDefs.categories) return;

    // Group morphs by category
    const byCategory = {};
    for (const m of morphDefs.morphs) {
        const cat = m.category || 'Other';
        if (!byCategory[cat]) byCategory[cat] = [];
        byCategory[cat].push(m);
    }

    for (const cat of morphDefs.categories) {
        const morphs = byCategory[cat];
        if (!morphs || morphs.length === 0) continue;

        const div = document.createElement('div');
        div.className = 'morph-category';

        const header = document.createElement('div');
        header.className = 'morph-category-header';
        header.innerHTML = `<span class="cat-chevron">&#9654;</span> ${escapeHtml(cat)} (${morphs.length})`;
        header.addEventListener('click', () => div.classList.toggle('open'));

        const body = document.createElement('div');
        body.className = 'morph-category-body';

        for (const m of morphs) {
            const currentVal = (inst.morphs[m.name] || 0) * 100;

            const row = document.createElement('div');
            row.className = 'slider-row';

            const label = document.createElement('label');
            // Clean up morph name for display
            let displayName = m.name;
            if (displayName.startsWith(cat + '_')) {
                displayName = displayName.substring(cat.length + 1);
            }
            label.textContent = displayName.replace(/_/g, ' ');
            label.title = m.name;
            label.style.minWidth = '80px';
            label.style.fontSize = '0.72rem';

            const slider = document.createElement('input');
            slider.type = 'range';
            slider.min = -100;
            slider.max = 100;
            slider.step = 1;
            slider.value = Math.round(currentVal);

            const valSpan = document.createElement('span');
            valSpan.className = 'slider-val';
            valSpan.textContent = Math.round(currentVal);

            slider.addEventListener('input', () => {
                valSpan.textContent = slider.value;
            });

            slider.addEventListener('change', () => {
                const v = parseFloat(slider.value) / 100;
                if (Math.abs(v) < 0.005) {
                    delete inst.morphs[m.name];
                } else {
                    inst.morphs[m.name] = v;
                }
                reloadCharacterMesh(inst);
            });

            row.appendChild(label);
            row.appendChild(slider);
            row.appendChild(valSpan);
            body.appendChild(row);
        }

        div.appendChild(header);
        div.appendChild(body);
        container.appendChild(div);
    }
}

async function reloadCharacterMesh(inst) {
    clearTimeout(reloadTimer);
    reloadTimer = setTimeout(async () => {
        try {
            await inst.reloadBody();
            updateVertexCount();
            updateCharacterListUI();
            if (currentPropsCharId === inst.id) updateEquippedList(inst);
            markDirty();
        } catch (e) {
            console.error('Failed to reload character mesh:', e);
        }
    }, 300);
}

// =========================================================================
// Refit all garments & hair for current character
// =========================================================================

/** Returns the max Y coordinate from a character's body mesh positions. */
function _getBodyTop(inst) {
    if (!inst.bodyMesh || !inst.bodyMesh.geometry.attributes.position) return 1.0;
    const pos = inst.bodyMesh.geometry.attributes.position.array;
    let maxY = -Infinity;
    for (let i = 1; i < pos.length; i += 3) {
        if (pos[i] > maxY) maxY = pos[i];
    }
    return maxY > 0 ? maxY : 1.0;
}

async function _refitAllForCurrentChar() {
    const inst = characters.get(currentPropsCharId);
    if (!inst) return;

    const btn = document.getElementById('prop-refit-btn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refit...';
    }

    _refitting = true;

    try {
        // --- Refit garments (gar_*) ---
        const garKeys = Object.keys(inst.clothMeshes).filter(k => k.startsWith('gar_'));
        for (const key of garKeys) {
            const garId = key.substring(4); // strip 'gar_'
            const gState = inst.garmentState[key] || {};
            const params = _charQueryParams(inst);
            params.set('garment_id', garId);
            params.set('offset', (gState.offset || 0.006).toFixed(4));
            params.set('stiffness', (gState.stiffness || 0.5).toFixed(2));
            if (gState.minDist != null) params.set('min_dist', gState.minDist);
            if (gState.crotchFloor != null) params.set('crotch_floor', gState.crotchFloor);
            if (gState.lift != null) params.set('lift', gState.lift);
            if (gState.crotchDepth != null) params.set('crotch_depth', gState.crotchDepth);

            let color = gState.color;
            // Normalize color to [r, g, b] floats
            if (!color || !Array.isArray(color)) {
                const c = new THREE.Color(color || 0x4d5980);
                color = [c.r, c.g, c.b];
            }
            params.set('color_r', Number(color[0]).toFixed(3));
            params.set('color_g', Number(color[1]).toFixed(3));
            params.set('color_b', Number(color[2]).toFixed(3));

            try {
                const resp = await fetch(`/api/character/garment/fit/?${params}`);
                const data = await resp.json();
                if (data.error) { console.log(`[Refit] ${key}: ${data.error}`); continue; }

                // Remove old mesh — copied from viewer.js loadGarment()
                if (inst.clothMeshes[key]) {
                    inst.group.remove(inst.clothMeshes[key]);
                    inst.clothMeshes[key].geometry.dispose();
                    inst.clothMeshes[key].material.dispose();
                }

                const vertBuf = base64ToFloat32(data.vertices);
                blenderToThreeCoords(vertBuf);
                const faceBuf = base64ToUint32(data.faces);

                const geo = new THREE.BufferGeometry();
                geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
                geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
                // Let Three.js compute smooth vertex normals — same as viewer.js
                geo.computeVertexNormals();

                const matColor = new THREE.Color(color[0], color[1], color[2]);
                const mat = new THREE.MeshStandardMaterial({
                    color: matColor,
                    roughness: gState.roughness ?? 0.8,
                    metalness: gState.metalness ?? 0.0,
                    side: THREE.DoubleSide,
                    polygonOffset: true,
                    polygonOffsetFactor: -1,
                    polygonOffsetUnit: -1,
                });

                const mesh = _skinifyMesh(geo, mat, inst, data);
                inst.clothMeshes[key] = mesh;
                inst.group.add(mesh);

                // Recompute region weights + re-apply offsets
                inst.garmentOrigPositions[key] = new Float32Array(vertBuf);
                _computeGarmentRegionWeights(inst, key);
                _applyGarmentRegionOffsets(inst, key);

                console.log(`[Refit] ${key}: ${data.vertex_count} verts, skinned=${mesh.isSkinnedMesh || false}`);
            } catch (e) {
                console.log(`[Refit] ${key} failed: ${e.message}`);
            }
        }

        // --- Refit cloth pieces (tpl_*, bld_*, prim_*) ---
        const clothKeys = Object.keys(inst.clothMeshes).filter(k =>
            k.startsWith('tpl_') || k.startsWith('bld_') || k.startsWith('prim_'));
        for (const key of clothKeys) {
            try {
                const clothDef = inst.cloth.find(c => c.key === key);
                if (clothDef) {
                    await _loadClothForCharacter(inst, key, clothDef);
                }
            } catch (e) {
                console.error(`Refit cloth ${key} failed:`, e);
            }
        }

        // --- Refit hair — copied from viewer.js refitHairToBody() ---
        if (inst.bodyMesh && inst.initialBodyTop > 0 && inst.hairMesh && inst.hairStyle && inst.hairStyle.url) {
            const currentTop = _getBodyTop(inst);
            if (currentTop !== null && Math.abs(currentTop - inst.initialBodyTop) > 0.001) {
                const scale = currentTop / inst.initialBodyTop;
                const hairUrl = inst.hairStyle.url;
                const colorName = inst.hairStyle.color || '';

                // Remove old hair
                inst.group.remove(inst.hairMesh);
                inst.hairMesh.traverse(child => {
                    if (child.isMesh) {
                        child.geometry.dispose();
                        const mats = Array.isArray(child.material) ? child.material : [child.material];
                        mats.forEach(m => m.dispose());
                    }
                });
                inst.hairMesh = null;

                // Auto-skin if needed
                if (!inst.isSkinned && rigifySkeletonData && skinWeightData) {
                    convertInstToSkinned(inst);
                }

                gltfLoader.load(hairUrl, (gltf) => {
                    let hairGroup = gltf.scene;

                    // Scale geometry vertices before skinning so bone binding stays correct
                    hairGroup.traverse(child => {
                        if (child.isMesh) {
                            child.geometry.scale(scale, scale, scale);
                        }
                    });

                    // Re-bind to skeleton
                    if (inst.isSkinned && inst.rigifySkeleton) {
                        hairGroup = _skinifyHairGroup(hairGroup, inst);
                    }

                    inst.hairMesh = hairGroup;
                    inst.hairStyle = { url: hairUrl, name: hairUrl.split('/').pop(), color: colorName };

                    if (colorName && hairColorData[colorName]) {
                        const rgb = hairColorData[colorName];
                        const color = new THREE.Color(rgb[0], rgb[1], rgb[2]);
                        inst.hairMesh.traverse(child => {
                            if (child.isMesh && child.material) {
                                const mats = Array.isArray(child.material) ? child.material : [child.material];
                                mats.forEach(m => { m.color.copy(color); });
                            }
                        });
                    }

                    inst.group.add(inst.hairMesh);
                    updateEquippedList(inst);
                    updateVertexCount();
                    console.log(`[Hair refit] scale=${scale.toFixed(4)} (initial=${inst.initialBodyTop.toFixed(4)}, current=${currentTop.toFixed(4)})`);
                }, undefined, (err) => {
                    console.error('[Hair refit] failed to reload:', err);
                });
            }
        }

        updateEquippedList(inst);
        updateVertexCount();
        markDirty();
    } catch (e) {
        console.error('Refit all failed:', e);
    } finally {
        _refitting = false;
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-sync"></i> Garments &amp; Haare anpassen';
        }
    }
}

// =========================================================================
// Sub-mesh interaction (cloth/hair hover, select, remove)
// =========================================================================

/** Returns array of selectable sub-mesh targets for a character instance. */
function getSelectableSubMeshes(charId) {
    const inst = characters.get(charId);
    if (!inst) return [];
    const targets = [];
    // Cloth meshes
    for (const [key, mesh] of Object.entries(inst.clothMeshes)) {
        if (mesh) {
            targets.push({
                type: 'cloth', key, label: key,
                meshObj: mesh, charId
            });
        }
    }
    // Hair mesh
    if (inst.hairMesh) {
        const hName = inst.hairStyle?.name || inst.hairStyle?.url?.split('/').pop() || 'Hair';
        targets.push({
            type: 'hair', key: 'hair', label: `Hair (${hName})`,
            meshObj: inst.hairMesh, charId
        });
    }
    return targets;
}

/** Get all sub-mesh targets across ALL characters (for hover). */
function getAllSubMeshTargets() {
    const targets = [];
    characters.forEach((inst, id) => {
        targets.push(...getSelectableSubMeshes(id));
    });
    return targets;
}

/** Walk up the object tree to find which target item owns a hit object. */
function _findSubMeshForObject(obj, targets) {
    for (const t of targets) {
        let cur = obj;
        while (cur) {
            if (cur === t.meshObj) return t;
            cur = cur.parent;
        }
    }
    return null;
}

/** Compare two sub-mesh targets for identity. */
function _sameSubMesh(a, b) {
    if (!a || !b) return false;
    return a.type === b.type && a.key === b.key && a.charId === b.charId;
}

/** Collect all child meshes of a root object. */
function _getMeshesOf(root) {
    const meshes = [];
    if (root.isMesh) {
        meshes.push(root);
    } else {
        root.traverse(child => { if (child.isMesh) meshes.push(child); });
    }
    return meshes;
}

/** Set emissive color on all meshes within a sub-mesh target. */
function _setSubMeshEmissive(target, color) {
    if (!target || !target.meshObj) return;
    for (const m of _getMeshesOf(target.meshObj)) {
        if (m.material) {
            const mats = Array.isArray(m.material) ? m.material : [m.material];
            for (const mat of mats) {
                if (mat.emissive) mat.emissive.copy(color);
            }
        }
    }
}

/** Set emissive on the body mesh of a character instance. */
function _setBodyEmissive(inst, color) {
    if (!inst || !inst.bodyMesh) return;
    const mats = Array.isArray(inst.bodyMesh.material) ? inst.bodyMesh.material : [inst.bodyMesh.material];
    for (const mat of mats) {
        if (mat.emissive) mat.emissive.copy(color);
    }
}

/** Clear current sub-mesh selection and hover. */
function clearSubMeshSelection() {
    if (_selectedSubMesh) {
        _setSubMeshEmissive(_selectedSubMesh, _ZERO_EMISSIVE);
        _selectedSubMesh = null;
    }
    if (_hoveredSubMesh) {
        _setSubMeshEmissive(_hoveredSubMesh, _ZERO_EMISSIVE);
        _hoveredSubMesh = null;
    }
    _updatePropContext();
    const tooltip = document.getElementById('mesh-tooltip');
    if (tooltip) tooltip.style.display = 'none';
}

/** Handle click on a sub-mesh target: toggle selection. */
function _doSubMeshClick(hitTarget) {
    const inst = characters.get(hitTarget.charId);
    if (_sameSubMesh(_selectedSubMesh, hitTarget)) {
        // Deselect sub-mesh → body becomes selected
        _setSubMeshEmissive(_selectedSubMesh, _ZERO_EMISSIVE);
        _selectedSubMesh = null;
        if (inst) _setBodyEmissive(inst, _SELECT_EMISSIVE);
    } else {
        // Select new sub-mesh → clear body highlight
        if (_selectedSubMesh) _setSubMeshEmissive(_selectedSubMesh, _ZERO_EMISSIVE);
        _selectedSubMesh = hitTarget;
        _setSubMeshEmissive(_selectedSubMesh, _SELECT_EMISSIVE);
        if (inst) _setBodyEmissive(inst, _ZERO_EMISSIVE);
    }
    // Sync garment sliders if this is a garment
    _syncGarmentSliders();
    // Switch to Eigenschaften tab and update context
    switchTab('eigenschaften');
    _updatePropContext();
    if (_selectedSubMesh && _selectedSubMesh.type === 'cloth') {
        _syncPropGarmentControls();
    } else if (_selectedSubMesh && _selectedSubMesh.type === 'hair') {
        _syncPropHairControls();
    }
    // Update equipped list highlight
    if (inst) updateEquippedList(inst);
}

/** Sync garment property sliders to the currently selected garment sub-mesh. */
let _syncingSliders = false;  // Suppress refit during slider sync

function _syncGarmentSliders() {
    if (!_selectedSubMesh || _selectedSubMesh.type !== 'cloth') return;
    const inst = characters.get(_selectedSubMesh.charId);
    if (!inst) return;
    const key = _selectedSubMesh.key;
    const st = inst.garmentState[key];
    if (!st) return;

    // Update _selectedGarmentId so "Fit" re-fits this garment
    if (key.startsWith('gar_')) _selectedGarmentId = key.slice(4);

    _syncingSliders = true;
    const offEl = document.getElementById('garment-offset');
    if (offEl) { offEl.value = Math.round(st.offset * 1000); offEl.dispatchEvent(new Event('input')); }
    const stiffEl = document.getElementById('garment-stiffness');
    if (stiffEl) { stiffEl.value = Math.round(st.stiffness * 100); stiffEl.dispatchEvent(new Event('input')); }
    const minDistEl = document.getElementById('garment-min-dist');
    if (minDistEl) { minDistEl.value = st.minDist !== undefined ? st.minDist : 3; minDistEl.dispatchEvent(new Event('input')); }
    const crotchFloorEl = document.getElementById('garment-crotch-floor');
    if (crotchFloorEl) { crotchFloorEl.value = st.crotchFloor !== undefined ? st.crotchFloor : 0; crotchFloorEl.dispatchEvent(new Event('input')); }
    const liftEl = document.getElementById('garment-lift');
    if (liftEl) { liftEl.value = st.lift !== undefined ? st.lift : 0; liftEl.dispatchEvent(new Event('input')); }
    const crotchDepthSyncEl = document.getElementById('garment-crotch-depth');
    if (crotchDepthSyncEl) { crotchDepthSyncEl.value = st.crotchDepth !== undefined ? st.crotchDepth : 0; crotchDepthSyncEl.dispatchEvent(new Event('input')); }
    const roughEl = document.getElementById('garment-roughness');
    if (roughEl) { roughEl.value = Math.round(st.roughness * 100); roughEl.dispatchEvent(new Event('input')); }
    const metalEl = document.getElementById('garment-metalness');
    if (metalEl) { metalEl.value = Math.round(st.metalness * 100); metalEl.dispatchEvent(new Event('input')); }
    const colorEl = document.getElementById('garment-color');
    if (colorEl && st.color) colorEl.value = '#' + new THREE.Color(st.color[0], st.color[1], st.color[2]).getHexString();
    // Region sliders
    for (const rid of REGION_IDS) {
        const stKey = 'region' + rid[0].toUpperCase() + rid.slice(1);
        const rEl = document.getElementById(`garment-region-${rid}`);
        if (rEl) { rEl.value = Math.round((st[stKey] || 0) * 100); rEl.dispatchEvent(new Event('input')); }
    }
    _syncingSliders = false;
}

/** Remove a sub-mesh (cloth or hair) from a character. */
function _removeSubMesh(target) {
    if (!target) return;
    const inst = characters.get(target.charId);
    if (!inst) return;

    switch (target.type) {
        case 'cloth': {
            const mesh = inst.clothMeshes[target.key];
            if (mesh) {
                inst.group.remove(mesh);
                mesh.geometry.dispose();
                if (Array.isArray(mesh.material)) {
                    mesh.material.forEach(m => m.dispose());
                } else {
                    mesh.material.dispose();
                }
                delete inst.clothMeshes[target.key];
                // Also remove from inst.cloth / inst.garments arrays
                if (target.key.startsWith('gar_')) {
                    const garId = target.key.slice(4);
                    inst.garments = (inst.garments || []).filter(g => g.id !== garId);
                    delete inst.garmentState[target.key];
                    delete inst.garmentOrigPositions[target.key];
                    delete inst.garmentRegionWeights[target.key];
                } else {
                    // Remove cloth entry matching this key
                    inst.cloth = (inst.cloth || []).filter(c => {
                        const m = c.method || 'template';
                        let ck;
                        if (m === 'builder') ck = `bld_${c.region || 'TOP'}`;
                        else if (m === 'primitive') ck = `prim_${c.prim_type || 'PRIM_SKIRT'}`;
                        else ck = `tpl_${c.template || 'TPL_TSHIRT'}`;
                        return ck !== target.key;
                    });
                }
            }
            break;
        }
        case 'hair': {
            if (inst.hairMesh) {
                inst.group.remove(inst.hairMesh);
                inst.hairMesh.traverse(child => {
                    if (child.isMesh) {
                        child.geometry.dispose();
                        const mats = Array.isArray(child.material) ? child.material : [child.material];
                        mats.forEach(m => m.dispose());
                    }
                });
                inst.hairMesh = null;
                inst.hairStyle = null;
            }
            break;
        }
    }

    // Clear selection state
    if (_sameSubMesh(_selectedSubMesh, target)) _selectedSubMesh = null;
    if (_sameSubMesh(_hoveredSubMesh, target)) _hoveredSubMesh = null;

    updateEquippedList(inst);
    updateVertexCount();
    markDirty();
}

// =========================================================================
// Bone Selection — 3D overlay for generated models
// =========================================================================

/** Determine which bone was hit by a raycast intersection on a generated model. */
function _getBoneFromIntersection(intersection, bodyMesh) {
    if (!bodyMesh || !bodyMesh.userData.boneVertexRanges) return null;
    const vertIdx = intersection.face.a;
    const ranges = bodyMesh.userData.boneVertexRanges;
    for (const [boneName, range] of Object.entries(ranges)) {
        if (vertIdx >= range.start && vertIdx < range.start + range.count) {
            return boneName;
        }
    }
    return null;
}

/** Get or create a sub-geometry for a specific bone (cached). */
function _getOrCreateBoneHighlightGeo(bodyMesh, boneName) {
    if (_boneHighlightCache.has(boneName)) return _boneHighlightCache.get(boneName);

    const geo = bodyMesh.geometry;
    const ranges = bodyMesh.userData.boneVertexRanges;
    if (!ranges || !ranges[boneName]) return null;

    const { start, count } = ranges[boneName];
    const end = start + count;

    // Extract faces whose vertices all lie within this bone's vertex range
    const indexArr = geo.index.array;
    const newIndices = [];
    for (let i = 0; i < indexArr.length; i += 3) {
        const a = indexArr[i], b = indexArr[i + 1], c = indexArr[i + 2];
        if (a >= start && a < end && b >= start && b < end && c >= start && c < end) {
            newIndices.push(a - start, b - start, c - start);
        }
    }
    if (newIndices.length === 0) return null;

    // Copy vertex data for this range
    const posArr = geo.attributes.position.array;
    const subGeo = new THREE.BufferGeometry();
    subGeo.setAttribute('position', new THREE.Float32BufferAttribute(
        posArr.slice(start * 3, end * 3), 3));
    subGeo.setIndex(newIndices);
    subGeo.computeVertexNormals();

    // Copy skin data if present (needed for SkinnedMesh overlay)
    if (geo.attributes.skinIndex && geo.attributes.skinWeight) {
        subGeo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(
            geo.attributes.skinIndex.array.slice(start * 4, end * 4), 4));
        subGeo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(
            geo.attributes.skinWeight.array.slice(start * 4, end * 4), 4));
    }

    _boneHighlightCache.set(boneName, subGeo);
    return subGeo;
}

/** Create and add an overlay mesh for a bone highlight. */
function _createBoneOverlay(bodyMesh, boneName, material) {
    const subGeo = _getOrCreateBoneHighlightGeo(bodyMesh, boneName);
    if (!subGeo) return null;

    let overlay;
    if (bodyMesh.isSkinnedMesh && subGeo.attributes.skinIndex) {
        overlay = new THREE.SkinnedMesh(subGeo, material);
        overlay.bind(bodyMesh.skeleton, bodyMesh.bindMatrix);
    } else {
        overlay = new THREE.Mesh(subGeo, material);
    }
    overlay.renderOrder = 1;
    overlay.raycast = function() {};  // non-raycastable
    overlay.userData._boneOverlay = true;

    // Add to same parent as bodyMesh so transforms match
    if (bodyMesh.parent) bodyMesh.parent.add(overlay);
    return overlay;
}

/** Remove an overlay mesh from the scene. */
function _removeBoneOverlay(overlay) {
    if (overlay && overlay.parent) {
        overlay.parent.remove(overlay);
    }
}

/** Clear bone hover state. */
function _clearBoneHover() {
    if (_boneHoverOverlay) {
        _removeBoneOverlay(_boneHoverOverlay);
        _boneHoverOverlay = null;
    }
    _hoveredBoneName = null;
}

/** Clear bone selection state. */
function _clearBoneSelection() {
    if (_boneSelectOverlay) {
        _removeBoneOverlay(_boneSelectOverlay);
        _boneSelectOverlay = null;
    }
    _selectedBoneName = null;
}

/** Invalidate all bone highlight caches (call on model regeneration). */
function _clearBoneHighlightCache() {
    for (const geo of _boneHighlightCache.values()) {
        geo.dispose();
    }
    _boneHighlightCache.clear();
    _clearBoneHover();
    _clearBoneSelection();
}

/** Handle Ctrl+Click on a generated model bone. */
function _doBoneClick(boneName, inst) {
    // Ensure model generator is initialized from this instance's config
    if (!_mgConfig && inst.generatedConfig) {
        _mgConfig = JSON.parse(JSON.stringify(inst.generatedConfig));
        _mgSkeletonType = inst.generatedConfig.skeleton_type || 'rig';
        _mgCharacterId = inst.id;
        if (!_mgInitialized) {
            _bindModelGeneratorUI();
            _mgInitialized = true;
        }
        const skelSelect = document.getElementById('mg-skeleton-type');
        if (skelSelect) skelSelect.value = _mgSkeletonType;
        _populateBoneTree();
        _syncMGGlobalUI();
    }
    // Link model generator to this character if not linked
    if (!_mgCharacterId && inst.generatedConfig) {
        _mgConfig = JSON.parse(JSON.stringify(inst.generatedConfig));
        _mgCharacterId = inst.id;
        _populateBoneTree();
    }

    if (_selectedBoneName === boneName) {
        // Toggle off
        _clearBoneSelection();
        _mgSelectedBone = null;
        const propsSection = document.getElementById('mg-bone-props-section');
        if (propsSection) propsSection.style.display = 'none';
        document.querySelectorAll('.mg-bone-item.selected').forEach(el => el.classList.remove('selected'));
        return;
    }

    // Select new bone
    _clearBoneSelection();
    _selectedBoneName = boneName;
    if (inst.bodyMesh) {
        _boneSelectOverlay = _createBoneOverlay(inst.bodyMesh, boneName, _BONE_SELECT_MAT);
    }

    // Sync with Model Generator UI
    _mgSelectBone(boneName);
    switchTab('modell');

    // Ensure bone properties section is expanded
    const propsSection = document.getElementById('mg-bone-props-section');
    if (propsSection) propsSection.classList.remove('collapsed');

    // Scroll bone into view in tree
    const treeItem = document.querySelector(`.mg-bone-item[data-bone="${boneName}"]`);
    if (treeItem) {
        // Expand parent category if collapsed
        const catBody = treeItem.closest('.mg-category-body');
        if (catBody && catBody.classList.contains('hidden')) {
            catBody.classList.remove('hidden');
            const header = catBody.previousElementSibling;
            if (header) header.classList.remove('collapsed');
        }
        treeItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

/** Bind mousemove hover + tooltip for sub-meshes. Called once from init(). */
function initSubMeshInteraction() {
    const tooltip = document.getElementById('mesh-tooltip');

    canvas.addEventListener('mousemove', (e) => {
        _lastMouseEvent = e;
        if (!_hoverPending) {
            _hoverPending = true;
            requestAnimationFrame(() => {
                _hoverPending = false;
                if (_lastMouseEvent) _doSubMeshHover(_lastMouseEvent);
            });
        }
    });

    canvas.addEventListener('mouseleave', () => {
        if (_hoveredSubMesh && !_sameSubMesh(_hoveredSubMesh, _selectedSubMesh)) {
            _setSubMeshEmissive(_hoveredSubMesh, _ZERO_EMISSIVE);
        }
        _hoveredSubMesh = null;
        _clearBoneHover();
        if (tooltip) tooltip.style.display = 'none';
        canvas.style.cursor = '';
    });

    function _doSubMeshHover(e) {
        if (_refitting) return;  // Suppress hover during garment refit
        const rect = canvas.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(mouse, camera);

        // Collect sub-mesh targets (garments, hair)
        const targets = getAllSubMeshTargets();
        const roots = targets.map(t => t.meshObj);

        // Also include generated model body meshes for bone hover
        const boneTargets = [];  // { bodyMesh, charId }
        characters.forEach((inst, id) => {
            if (inst.generatedConfig && inst.bodyMesh && inst.bodyMesh.userData.boneVertexRanges) {
                boneTargets.push({ bodyMesh: inst.bodyMesh, charId: id });
                roots.push(inst.bodyMesh);
            }
        });

        const intersects = raycaster.intersectObjects(roots, true);

        let newItem = null;
        let newBoneName = null;
        let hitBodyMesh = null;

        if (intersects.length > 0) {
            // Check if closest hit is a sub-mesh (garment/hair)
            newItem = _findSubMeshForObject(intersects[0].object, targets);

            // If not a sub-mesh, check if it's a generated model body mesh
            if (!newItem) {
                for (const bt of boneTargets) {
                    if (intersects[0].object === bt.bodyMesh) {
                        newBoneName = _getBoneFromIntersection(intersects[0], bt.bodyMesh);
                        hitBodyMesh = bt.bodyMesh;
                        break;
                    }
                }
            }
        }

        // Update tooltip
        const label = newItem ? newItem.label : newBoneName;
        if (label && tooltip) {
            tooltip.textContent = label;
            tooltip.style.left = (e.clientX - rect.left + 14) + 'px';
            tooltip.style.top = (e.clientY - rect.top - 10) + 'px';
            tooltip.style.display = 'block';
            canvas.style.cursor = 'pointer';
        } else {
            if (tooltip) tooltip.style.display = 'none';
            canvas.style.cursor = '';
        }

        // Update sub-mesh emissive highlight
        if (!_sameSubMesh(_hoveredSubMesh, newItem)) {
            if (_hoveredSubMesh && !_sameSubMesh(_hoveredSubMesh, _selectedSubMesh)) {
                _setSubMeshEmissive(_hoveredSubMesh, _ZERO_EMISSIVE);
            }
            _hoveredSubMesh = newItem;
            if (_hoveredSubMesh && !_sameSubMesh(_hoveredSubMesh, _selectedSubMesh)) {
                _setSubMeshEmissive(_hoveredSubMesh, _HOVER_EMISSIVE);
            }
        }

        // Update bone hover overlay
        if (_hoveredBoneName !== newBoneName) {
            if (_boneHoverOverlay) {
                _removeBoneOverlay(_boneHoverOverlay);
                _boneHoverOverlay = null;
            }
            _hoveredBoneName = newBoneName;
            if (newBoneName && hitBodyMesh && newBoneName !== _selectedBoneName) {
                _boneHoverOverlay = _createBoneOverlay(hitBodyMesh, newBoneName, _BONE_HOVER_MAT);
            }
        }
    }
}

/** Build the equipped items list in the Eigenschaften panel. */
function updateEquippedList(inst) {
    const list = document.getElementById('prop-equipped-list');
    if (!list) return;
    list.innerHTML = '';

    if (!inst) {
        list.innerHTML = '<li class="equipped-empty">Keine Objekte</li>';
        return;
    }

    const targets = getSelectableSubMeshes(inst.id);
    if (targets.length === 0) {
        list.innerHTML = '<li class="equipped-empty">Keine Objekte</li>';
        return;
    }

    for (const t of targets) {
        const li = document.createElement('li');
        li.className = 'equipped-item';

        const nameSpan = document.createElement('span');
        nameSpan.className = 'equipped-item-name';
        if (_sameSubMesh(_selectedSubMesh, t)) {
            nameSpan.classList.add('selected');
        }
        nameSpan.textContent = t.label;
        nameSpan.addEventListener('click', () => {
            // Select in 3D
            if (_selectedSubMesh) _setSubMeshEmissive(_selectedSubMesh, _ZERO_EMISSIVE);
            // Re-fetch fresh target in case mesh was recreated
            const fresh = getSelectableSubMeshes(inst.id).find(x => x.type === t.type && x.key === t.key);
            if (!fresh) return;
            _selectedSubMesh = fresh;
            _setSubMeshEmissive(_selectedSubMesh, _SELECT_EMISSIVE);
            _setBodyEmissive(inst, _ZERO_EMISSIVE);
            _syncGarmentSliders();
            // Update context and sync controls
            _updatePropContext();
            if (fresh.type === 'cloth') {
                _syncPropGarmentControls();
            } else if (fresh.type === 'hair') {
                _syncPropHairControls();
            }
            updateEquippedList(inst);
        });

        const rmBtn = document.createElement('button');
        rmBtn.className = 'equipped-item-remove';
        rmBtn.innerHTML = '&#10005;';
        rmBtn.title = 'Entfernen';
        rmBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            _removeSubMesh(t);
        });

        li.appendChild(nameSpan);
        li.appendChild(rmBtn);
        list.appendChild(li);
    }
}

// =========================================================================
// Asset Panel: Slider helpers
// =========================================================================
function _bindSlider(id, valId, fmt) {
    const slider = document.getElementById(id);
    const val = document.getElementById(valId);
    if (slider && val) {
        slider.addEventListener('input', () => {
            val.textContent = fmt(parseInt(slider.value));
        });
    }
}

function _sliderVal(id) {
    const el = document.getElementById(id);
    return el ? parseInt(el.value) : 0;
}

/** Get the currently selected character (for asset operations). */
function _selectedInst() {
    return selectedCharacterId ? characters.get(selectedCharacterId) : null;
}

/** Build morph+meta query params for the selected character. */
function _charQueryParams(inst) {
    const params = new URLSearchParams();
    params.set('body_type', inst.bodyType);
    for (const [k, v] of Object.entries(inst.morphs || {})) {
        if (v !== 0) params.set(`morph_${k}`, v);
    }
    for (const [k, v] of Object.entries(inst.meta || {})) {
        if (v !== 0) params.set(`meta_${k}`, v);
    }
    return params;
}

// =========================================================================
// Eigenschaften Tab: Garment Properties
// =========================================================================
// --- Garment Region Definitions ---
const REGION_DEFS = [
    { id: 'bottom', center: 0.10 },  //  0-20%
    { id: 'lower',  center: 0.30 },  // 20-40%
    { id: 'mid',    center: 0.50 },  // 40-60%
    { id: 'upper',  center: 0.70 },  // 60-80%
    { id: 'top',    center: 0.90 },  // 80-100%
];
const REGION_RADIUS = 0.20;
const REGION_IDS = ['top', 'upper', 'mid', 'lower', 'bottom'];

/** Compute per-vertex cosine-blended region weights for a garment. */
function _computeGarmentRegionWeights(inst, key) {
    const orig = inst.garmentOrigPositions[key];
    if (!orig) return;
    const n = orig.length / 3;
    let yMin = Infinity, yMax = -Infinity;
    for (let i = 0; i < n; i++) {
        const y = orig[i * 3 + 1];
        if (y < yMin) yMin = y;
        if (y > yMax) yMax = y;
    }
    const yRange = yMax - yMin || 1e-6;
    const weights = {};
    for (const def of REGION_DEFS) weights[def.id] = new Float32Array(n);
    for (let i = 0; i < n; i++) {
        const t = (orig[i * 3 + 1] - yMin) / yRange;
        for (const def of REGION_DEFS) {
            const dist = Math.abs(t - def.center);
            if (dist < REGION_RADIUS) {
                weights[def.id][i] = 0.5 * (1 + Math.cos(Math.PI * dist / REGION_RADIUS));
            }
        }
    }
    inst.garmentRegionWeights[key] = weights;
}

/** Apply per-region Y-offsets to a garment mesh using cosine-blended weights. */
function _applyGarmentRegionOffsets(inst, key) {
    const mesh = inst.clothMeshes[key];
    const orig = inst.garmentOrigPositions[key];
    const rw = inst.garmentRegionWeights[key];
    const st = inst.garmentState[key];
    if (!mesh || !orig || !rw || !st) return;

    const positions = mesh.geometry.attributes.position.array;
    const n = orig.length / 3;

    // Reset positions to original first
    positions.set(orig);

    // Apply per-region Y-offsets
    for (const def of REGION_DEFS) {
        const stKey = 'region' + def.id[0].toUpperCase() + def.id.slice(1);
        const offset = st[stKey] || 0;
        if (Math.abs(offset) < 1e-6) continue;
        const w = rw[def.id];
        for (let i = 0; i < n; i++) {
            positions[i * 3 + 1] += offset * w[i];
        }
    }

    mesh.geometry.attributes.position.needsUpdate = true;
    mesh.geometry.computeBoundingSphere();
}

/**
 * Update Eigenschaften tab context: show body sections or garment section
 * based on current selection state.
 *   - No sub-mesh selected (body click): Transform, Ausstattung, Body Type, Morphs
 *   - Garment selected: Garment Eigenschaften only
 */
function _updatePropContext() {
    const bodySections = ['prop-transform-section', 'prop-equipped-section',
                          'prop-bodytype-section', 'prop-morphs-section'];
    const garmentSection = 'prop-garment-section';
    const hairSection = 'prop-hair-section';

    const isGarment = _selectedSubMesh && _selectedSubMesh.type === 'cloth'
                      && _selectedSubMesh.key.startsWith('gar_');
    const isHair = _selectedSubMesh && _selectedSubMesh.type === 'hair';
    const isAsset = isGarment || isHair;

    for (const id of bodySections) {
        const el = document.getElementById(id);
        if (el) el.style.display = isAsset ? 'none' : '';
    }
    const gEl = document.getElementById(garmentSection);
    if (gEl) gEl.style.display = isGarment ? '' : 'none';
    const hEl = document.getElementById(hairSection);
    if (hEl) hEl.style.display = isHair ? '' : 'none';
}

/** Sync the Eigenschaften-tab garment controls FROM garmentState. */
function _syncPropGarmentControls() {
    const sel = _selectedGarmentMesh();
    const sec = document.getElementById('prop-garment-section');
    if (!sel || !sel.key.startsWith('gar_')) {
        if (sec) sec.style.display = 'none';
        return;
    }
    if (sec) sec.style.display = '';

    const st = sel.inst.garmentState[sel.key];
    if (!st) return;

    const offEl = document.getElementById('prop-garment-offset');
    if (offEl) { offEl.value = Math.round(st.offset * 1000); }
    const offVal = document.getElementById('prop-garment-offset-val');
    if (offVal) offVal.textContent = st.offset.toFixed(3);

    const stiffEl = document.getElementById('prop-garment-stiffness');
    if (stiffEl) { stiffEl.value = Math.round(st.stiffness * 100); }
    const stiffVal = document.getElementById('prop-garment-stiffness-val');
    if (stiffVal) stiffVal.textContent = st.stiffness.toFixed(2);

    const minDistEl = document.getElementById('prop-garment-min-dist');
    if (minDistEl) { minDistEl.value = st.minDist !== undefined ? st.minDist : 3; }
    const minDistVal = document.getElementById('prop-garment-min-dist-val');
    if (minDistVal) minDistVal.textContent = (st.minDist !== undefined ? st.minDist : 3) + ' mm';

    const crotchFloorEl = document.getElementById('prop-garment-crotch-floor');
    if (crotchFloorEl) { crotchFloorEl.value = st.crotchFloor !== undefined ? st.crotchFloor : 0; }
    const crotchFloorVal = document.getElementById('prop-garment-crotch-floor-val');
    if (crotchFloorVal) crotchFloorVal.textContent = (st.crotchFloor !== undefined ? st.crotchFloor : 0) + ' mm';

    const propLiftEl = document.getElementById('prop-garment-lift');
    if (propLiftEl) { propLiftEl.value = st.lift !== undefined ? st.lift : 0; }
    const propLiftVal = document.getElementById('prop-garment-lift-val');
    if (propLiftVal) propLiftVal.textContent = (st.lift !== undefined ? st.lift : 0) + ' mm';

    const propCDEl = document.getElementById('prop-garment-crotch-depth');
    if (propCDEl) { propCDEl.value = st.crotchDepth !== undefined ? st.crotchDepth : 0; }
    const propCDVal = document.getElementById('prop-garment-crotch-depth-val');
    if (propCDVal) propCDVal.textContent = (st.crotchDepth !== undefined ? st.crotchDepth : 0) + ' mm';

    const roughEl = document.getElementById('prop-garment-roughness');
    if (roughEl) { roughEl.value = Math.round(st.roughness * 100); }
    const roughVal = document.getElementById('prop-garment-roughness-val');
    if (roughVal) roughVal.textContent = st.roughness.toFixed(2);

    const metalEl = document.getElementById('prop-garment-metalness');
    if (metalEl) { metalEl.value = Math.round(st.metalness * 100); }
    const metalVal = document.getElementById('prop-garment-metalness-val');
    if (metalVal) metalVal.textContent = st.metalness.toFixed(2);

    const colorEl = document.getElementById('prop-garment-color');
    if (colorEl && st.color) colorEl.value = '#' + new THREE.Color(st.color[0], st.color[1], st.color[2]).getHexString();

    // Region sliders
    for (const rid of REGION_IDS) {
        const stKey = 'region' + rid[0].toUpperCase() + rid.slice(1);
        const el = document.getElementById(`prop-garment-region-${rid}`);
        if (el) el.value = Math.round((st[stKey] || 0) * 100);
        const valEl = document.getElementById(`prop-garment-region-${rid}-val`);
        if (valEl) valEl.textContent = ((st[stKey] || 0)).toFixed(2) + ' m';
    }
}

/** Save prop-tab slider state back into garmentState + sync asset-tab sliders. */
function _savePropGarmentState() {
    const sel = _selectedGarmentMesh();
    if (!sel) return;
    const st = sel.inst.garmentState[sel.key];
    if (!st) return;
    st.offset = _sliderVal('prop-garment-offset') / 1000;
    st.stiffness = _sliderVal('prop-garment-stiffness') / 100;
    st.minDist = _sliderVal('prop-garment-min-dist');
    st.crotchFloor = _sliderVal('prop-garment-crotch-floor');
    st.lift = _sliderVal('prop-garment-lift');
    st.crotchDepth = _sliderVal('prop-garment-crotch-depth');
    st.roughness = _sliderVal('prop-garment-roughness') / 100;
    st.metalness = _sliderVal('prop-garment-metalness') / 100;
    for (const rid of REGION_IDS) {
        const stKey = 'region' + rid[0].toUpperCase() + rid.slice(1);
        st[stKey] = _sliderVal(`prop-garment-region-${rid}`) / 100;
    }
    const colorEl = document.getElementById('prop-garment-color');
    if (colorEl) {
        const c = new THREE.Color(colorEl.value);
        st.color = [c.r, c.g, c.b];
    }
    // Also sync asset-tab sliders so they stay in sync
    _syncGarmentSliders();
}

/** Do a garment refit using prop-tab slider values. */
function _doPropGarmentRefit() {
    const sel = _selectedGarmentMesh();
    if (!sel || !sel.key.startsWith('gar_')) return;
    _selectedGarmentId = sel.key.slice(4);
    // Copy prop-tab values to asset-tab sliders (refit reads from those)
    const offEl = document.getElementById('garment-offset');
    if (offEl) offEl.value = document.getElementById('prop-garment-offset')?.value || offEl.value;
    const stiffEl = document.getElementById('garment-stiffness');
    if (stiffEl) stiffEl.value = document.getElementById('prop-garment-stiffness')?.value || stiffEl.value;
    const minDistEl = document.getElementById('garment-min-dist');
    if (minDistEl) minDistEl.value = document.getElementById('prop-garment-min-dist')?.value || minDistEl.value;
    const crotchFloorEl = document.getElementById('garment-crotch-floor');
    if (crotchFloorEl) crotchFloorEl.value = document.getElementById('prop-garment-crotch-floor')?.value || crotchFloorEl.value;
    const liftElSync = document.getElementById('garment-lift');
    if (liftElSync) liftElSync.value = document.getElementById('prop-garment-lift')?.value || liftElSync.value;
    const crotchDepthElSync = document.getElementById('garment-crotch-depth');
    if (crotchDepthElSync) crotchDepthElSync.value = document.getElementById('prop-garment-crotch-depth')?.value || crotchDepthElSync.value;
    const colorEl = document.getElementById('garment-color');
    const propColorEl = document.getElementById('prop-garment-color');
    if (colorEl && propColorEl) colorEl.value = propColorEl.value;
    const roughEl = document.getElementById('garment-roughness');
    if (roughEl) roughEl.value = document.getElementById('prop-garment-roughness')?.value || roughEl.value;
    const metalEl = document.getElementById('garment-metalness');
    if (metalEl) metalEl.value = document.getElementById('prop-garment-metalness')?.value || metalEl.value;
    // Sync region sliders prop→asset before refit
    for (const rid of REGION_IDS) {
        const assetEl = document.getElementById(`garment-region-${rid}`);
        const propEl = document.getElementById(`prop-garment-region-${rid}`);
        if (assetEl && propEl) assetEl.value = propEl.value;
    }
    _doGarmentFit();
}

function initPropGarmentControls() {
    _bindSlider('prop-garment-offset', 'prop-garment-offset-val', v => (v / 1000).toFixed(3));
    _bindSlider('prop-garment-stiffness', 'prop-garment-stiffness-val', v => (v / 100).toFixed(2));
    _bindSlider('prop-garment-min-dist', 'prop-garment-min-dist-val', v => v + ' mm');
    _bindSlider('prop-garment-crotch-floor', 'prop-garment-crotch-floor-val', v => v + ' mm');
    _bindSlider('prop-garment-lift', 'prop-garment-lift-val', v => v + ' mm');
    _bindSlider('prop-garment-crotch-depth', 'prop-garment-crotch-depth-val', v => v + ' mm');
    _bindSlider('prop-garment-roughness', 'prop-garment-roughness-val', v => (v / 100).toFixed(2));
    _bindSlider('prop-garment-metalness', 'prop-garment-metalness-val', v => (v / 100).toFixed(2));

    // Roughness: real-time material update
    const roughSlider = document.getElementById('prop-garment-roughness');
    if (roughSlider) roughSlider.addEventListener('input', () => {
        const sel = _selectedGarmentMesh();
        if (sel) { sel.mesh.material.roughness = _sliderVal('prop-garment-roughness') / 100; _savePropGarmentState(); }
    });

    // Metalness: real-time material update
    const metalSlider = document.getElementById('prop-garment-metalness');
    if (metalSlider) metalSlider.addEventListener('input', () => {
        const sel = _selectedGarmentMesh();
        if (sel) { sel.mesh.material.metalness = _sliderVal('prop-garment-metalness') / 100; _savePropGarmentState(); }
    });

    // Color: real-time material update
    const colorPicker = document.getElementById('prop-garment-color');
    if (colorPicker) colorPicker.addEventListener('input', () => {
        const sel = _selectedGarmentMesh();
        if (sel) { sel.mesh.material.color.set(colorPicker.value); _savePropGarmentState(); }
    });

    // Offset & Stiffness: debounced server re-fit
    let _propRefitTimer = null;
    function _debouncedPropRefit() {
        const sel = _selectedGarmentMesh();
        if (!sel || !sel.key.startsWith('gar_')) return;
        clearTimeout(_propRefitTimer);
        _propRefitTimer = setTimeout(() => _doPropGarmentRefit(), 400);
    }
    const offSlider = document.getElementById('prop-garment-offset');
    if (offSlider) offSlider.addEventListener('input', _debouncedPropRefit);
    const stiffSlider = document.getElementById('prop-garment-stiffness');
    if (stiffSlider) stiffSlider.addEventListener('input', _debouncedPropRefit);
    const propMinDistSlider = document.getElementById('prop-garment-min-dist');
    if (propMinDistSlider) propMinDistSlider.addEventListener('input', _debouncedPropRefit);
    const propCrotchFloorSlider = document.getElementById('prop-garment-crotch-floor');
    if (propCrotchFloorSlider) propCrotchFloorSlider.addEventListener('input', _debouncedPropRefit);
    const propLiftSlider = document.getElementById('prop-garment-lift');
    if (propLiftSlider) propLiftSlider.addEventListener('input', _debouncedPropRefit);
    const propCrotchDepthSlider = document.getElementById('prop-garment-crotch-depth');
    if (propCrotchDepthSlider) propCrotchDepthSlider.addEventListener('input', _debouncedPropRefit);

    // Region sliders: live vertex buffer update
    for (const rid of REGION_IDS) {
        _bindSlider(`prop-garment-region-${rid}`, `prop-garment-region-${rid}-val`, v => (v / 100).toFixed(2) + ' m');
        const rEl = document.getElementById(`prop-garment-region-${rid}`);
        if (rEl) rEl.addEventListener('input', () => {
            const sel = _selectedGarmentMesh();
            if (!sel) return;
            _savePropGarmentState();
            _applyGarmentRegionOffsets(sel.inst, sel.key);
        });
    }
}

// =========================================================================
// Eigenschaften: Hair Controls
// =========================================================================
function initPropHairControls() {
    const styleEl = document.getElementById('prop-hair-style');
    const colorEl = document.getElementById('prop-hair-color');
    if (!styleEl || !colorEl) return;

    // Populate from cached data once available (re-called after loadHairUI)
    _populatePropHairOptions();

    styleEl.addEventListener('change', () => {
        const inst = _selectedInst();
        if (!inst) return;
        if (!styleEl.value) {
            // Remove hair
            if (inst.hairMesh) {
                inst.group.remove(inst.hairMesh);
                inst.hairMesh.traverse(child => {
                    if (child.isMesh) {
                        child.geometry.dispose();
                        const mats = Array.isArray(child.material) ? child.material : [child.material];
                        mats.forEach(m => m.dispose());
                    }
                });
                inst.hairMesh = null;
                inst.hairStyle = null;
            }
            // Sync asset-tab dropdown
            const assetSelect = document.getElementById('hair-style-select');
            if (assetSelect) assetSelect.value = '';
            updateEquippedList(inst);
            updateVertexCount();
            return;
        }
        const colorName = colorEl.value || '';
        _loadHairForCharacter(inst, styleEl.value, colorName);
        // Sync asset-tab dropdown
        const assetSelect = document.getElementById('hair-style-select');
        if (assetSelect) assetSelect.value = styleEl.value;
        const assetColor = document.getElementById('hair-color-select');
        if (assetColor) assetColor.value = colorName;
    });

    colorEl.addEventListener('change', () => {
        const inst = _selectedInst();
        if (!inst || !inst.hairMesh) return;
        const rgb = hairColorData[colorEl.value];
        if (!rgb) return;
        const color = new THREE.Color(rgb[0], rgb[1], rgb[2]);
        inst.hairMesh.traverse(child => {
            if (child.isMesh && child.material) {
                const mats = Array.isArray(child.material) ? child.material : [child.material];
                mats.forEach(m => { m.color.copy(color); });
            }
        });
        // Update hairStyle color
        if (inst.hairStyle) inst.hairStyle.color = colorEl.value;
        // Sync asset-tab color dropdown
        const assetColor = document.getElementById('hair-color-select');
        if (assetColor) assetColor.value = colorEl.value;
    });
}

function _populatePropHairOptions() {
    const styleEl = document.getElementById('prop-hair-style');
    const colorEl = document.getElementById('prop-hair-color');
    if (!styleEl || !colorEl) return;

    // Only populate once (keep the first "no hair" option)
    if (styleEl.options.length > 1) return;

    for (const h of (_hairStylesData || [])) {
        const opt = document.createElement('option');
        opt.value = h.url;
        opt.textContent = h.label;
        opt.dataset.name = h.name;
        styleEl.appendChild(opt);
    }

    for (const name of Object.keys(hairColorData || {})) {
        const opt = document.createElement('option');
        opt.value = name;
        opt.textContent = name;
        colorEl.appendChild(opt);
    }
}

function _syncPropHairControls() {
    const inst = _selectedInst();
    const sec = document.getElementById('prop-hair-section');
    if (!inst || !_selectedSubMesh || _selectedSubMesh.type !== 'hair') {
        if (sec) sec.style.display = 'none';
        return;
    }
    if (sec) sec.style.display = '';

    // Ensure options are populated
    _populatePropHairOptions();

    const styleEl = document.getElementById('prop-hair-style');
    const colorEl = document.getElementById('prop-hair-color');
    if (styleEl) {
        styleEl.value = (inst.hairStyle && inst.hairStyle.url) ? inst.hairStyle.url : '';
    }
    if (colorEl) {
        colorEl.value = (inst.hairStyle && inst.hairStyle.color) ? inst.hairStyle.color : '';
    }
}

// =========================================================================
// Asset Panel: Garment Fit
// =========================================================================
/** Get the mesh+inst for the currently selected garment sub-mesh. */
function _selectedGarmentMesh() {
    if (!_selectedSubMesh || _selectedSubMesh.type !== 'cloth') return null;
    const inst = characters.get(_selectedSubMesh.charId);
    if (!inst) return null;
    const key = _selectedSubMesh.key;
    const mesh = inst.clothMeshes[key];
    if (!mesh) return null;
    return { inst, key, mesh };
}

/** Save slider state back into garmentState for the selected garment. */
function _saveSelectedGarmentState() {
    const sel = _selectedGarmentMesh();
    if (!sel) return;
    const st = sel.inst.garmentState[sel.key];
    if (!st) return;
    st.offset = _sliderVal('garment-offset') / 1000;
    st.stiffness = _sliderVal('garment-stiffness') / 100;
    st.minDist = _sliderVal('garment-min-dist');
    st.crotchFloor = _sliderVal('garment-crotch-floor');
    st.lift = _sliderVal('garment-lift');
    st.crotchDepth = _sliderVal('garment-crotch-depth');
    st.roughness = _sliderVal('garment-roughness') / 100;
    st.metalness = _sliderVal('garment-metalness') / 100;
    for (const rid of REGION_IDS) {
        const stKey = 'region' + rid[0].toUpperCase() + rid.slice(1);
        st[stKey] = _sliderVal(`garment-region-${rid}`) / 100;
    }
    const colorEl = document.getElementById('garment-color');
    if (colorEl) {
        const c = new THREE.Color(colorEl.value);
        st.color = [c.r, c.g, c.b];
    }
}

async function loadGarmentUI() {
    _bindSlider('garment-offset', 'garment-offset-val', v => (v / 1000).toFixed(3));
    _bindSlider('garment-stiffness', 'garment-stiffness-val', v => (v / 100).toFixed(2));
    _bindSlider('garment-min-dist', 'garment-min-dist-val', v => v + ' mm');
    _bindSlider('garment-crotch-floor', 'garment-crotch-floor-val', v => v + ' mm');
    _bindSlider('garment-lift', 'garment-lift-val', v => v + ' mm');
    _bindSlider('garment-crotch-depth', 'garment-crotch-depth-val', v => v + ' mm');
    _bindSlider('garment-roughness', 'garment-roughness-val', v => (v / 100).toFixed(2));
    _bindSlider('garment-metalness', 'garment-metalness-val', v => (v / 100).toFixed(2));

    // --- Live garment property change handlers ---
    // Roughness: real-time client-side material update
    const roughSlider = document.getElementById('garment-roughness');
    if (roughSlider) roughSlider.addEventListener('input', () => {
        if (_syncingSliders) return;
        const sel = _selectedGarmentMesh();
        if (sel) { sel.mesh.material.roughness = _sliderVal('garment-roughness') / 100; _saveSelectedGarmentState(); }
    });
    // Metalness: real-time client-side material update
    const metalSlider = document.getElementById('garment-metalness');
    if (metalSlider) metalSlider.addEventListener('input', () => {
        if (_syncingSliders) return;
        const sel = _selectedGarmentMesh();
        if (sel) { sel.mesh.material.metalness = _sliderVal('garment-metalness') / 100; _saveSelectedGarmentState(); }
    });
    // Color: real-time client-side material update
    const colorPicker = document.getElementById('garment-color');
    if (colorPicker) colorPicker.addEventListener('input', () => {
        if (_syncingSliders) return;
        const sel = _selectedGarmentMesh();
        if (sel) { sel.mesh.material.color.set(colorPicker.value); _saveSelectedGarmentState(); }
    });
    // Offset & Stiffness: debounced server re-fit (fires while dragging, with 400ms debounce)
    let _garmentRefitTimer = null;
    function _debouncedGarmentRefit() {
        if (_syncingSliders) return;  // Don't refit during slider sync
        const sel = _selectedGarmentMesh();
        if (!sel || !sel.key.startsWith('gar_')) return;
        _selectedGarmentId = sel.key.slice(4);
        clearTimeout(_garmentRefitTimer);
        _garmentRefitTimer = setTimeout(() => _doGarmentFit(), 400);
    }
    const offSlider = document.getElementById('garment-offset');
    if (offSlider) offSlider.addEventListener('input', _debouncedGarmentRefit);
    const stiffSlider = document.getElementById('garment-stiffness');
    if (stiffSlider) stiffSlider.addEventListener('input', _debouncedGarmentRefit);
    const minDistSlider = document.getElementById('garment-min-dist');
    if (minDistSlider) minDistSlider.addEventListener('input', _debouncedGarmentRefit);
    const crotchFloorSlider = document.getElementById('garment-crotch-floor');
    if (crotchFloorSlider) crotchFloorSlider.addEventListener('input', _debouncedGarmentRefit);
    const liftSlider = document.getElementById('garment-lift');
    if (liftSlider) liftSlider.addEventListener('input', _debouncedGarmentRefit);
    const crotchDepthSlider = document.getElementById('garment-crotch-depth');
    if (crotchDepthSlider) crotchDepthSlider.addEventListener('input', _debouncedGarmentRefit);

    // Region sliders: live vertex buffer update (asset tab)
    for (const rid of REGION_IDS) {
        _bindSlider(`garment-region-${rid}`, `garment-region-${rid}-val`, v => (v / 100).toFixed(2) + ' m');
        const rEl = document.getElementById(`garment-region-${rid}`);
        if (rEl) rEl.addEventListener('input', () => {
            if (_syncingSliders) return;
            const sel = _selectedGarmentMesh();
            if (!sel) return;
            _saveSelectedGarmentState();
            _applyGarmentRegionOffsets(sel.inst, sel.key);
        });
    }

    const catSelect = document.getElementById('garment-category');
    if (catSelect) catSelect.addEventListener('change', () => _renderGarmentList());

    const createBtn = document.getElementById('garment-create');
    if (createBtn) createBtn.addEventListener('click', () => _doGarmentFit());

    const removeBtn = document.getElementById('garment-remove');
    if (removeBtn) removeBtn.addEventListener('click', () => {
        if (_selectedGarmentId && _selectedSubMesh) _removeSubMesh(_selectedSubMesh);
    });

    const removeAllBtn = document.getElementById('garment-remove-all');
    if (removeAllBtn) removeAllBtn.addEventListener('click', () => {
        const inst = _selectedInst();
        if (!inst) return;
        const keys = Object.keys(inst.clothMeshes).filter(k => k.startsWith('gar_'));
        for (const key of keys) {
            const t = { type: 'cloth', key, meshObj: inst.clothMeshes[key], charId: inst.id };
            _removeSubMesh(t);
        }
    });

    // Load garment library
    try {
        const resp = await fetch('/api/character/garment/library/');
        const data = await resp.json();
        _garmentCatalog = [];
        if (catSelect && data.categories) {
            data.categories.forEach(cat => {
                const opt = document.createElement('option');
                opt.value = cat;
                opt.textContent = cat.charAt(0).toUpperCase() + cat.slice(1);
                catSelect.appendChild(opt);
            });
        }
        if (data.garments) {
            for (const cat of Object.keys(data.garments)) {
                for (const g of data.garments[cat]) {
                    g._category = cat;
                    _garmentCatalog.push(g);
                }
            }
        }
        _renderGarmentList();
    } catch (e) {
        const list = document.getElementById('garment-list');
        if (list) list.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Garment-Library nicht verfügbar</div>';
    }
}

function _renderGarmentList() {
    const list = document.getElementById('garment-list');
    if (!list) return;
    list.innerHTML = '';

    const catFilter = document.getElementById('garment-category')?.value || '';
    const filtered = catFilter
        ? _garmentCatalog.filter(g => g._category === catFilter)
        : _garmentCatalog;

    if (filtered.length === 0) {
        list.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Garments gefunden</div>';
        return;
    }

    // Group by category
    const byCategory = {};
    for (const g of filtered) {
        const cat = g._category || 'Other';
        if (!byCategory[cat]) byCategory[cat] = [];
        byCategory[cat].push(g);
    }

    for (const [cat, garments] of Object.entries(byCategory)) {
        const catDiv = document.createElement('div');
        catDiv.className = 'anim-category';
        const header = document.createElement('div');
        header.className = 'anim-category-header';
        header.innerHTML = `<span class="cat-chevron"><i class="fas fa-chevron-right"></i></span>
            <span>${escapeHtml(cat)}</span>
            <span class="cat-count">${garments.length}</span>`;
        header.addEventListener('click', () => catDiv.classList.toggle('open'));
        catDiv.appendChild(header);

        const body = document.createElement('div');
        body.className = 'anim-category-body';
        for (const g of garments) {
            const item = document.createElement('div');
            item.className = 'anim-item garment-item' + (g.id === _selectedGarmentId ? ' active' : '');
            // Thumbnail + name (same layout as viewer.js)
            if (g.has_thumb) {
                const img = document.createElement('img');
                img.src = `/api/character/garment/thumb/${g.id}/`;
                img.alt = g.name;
                img.className = 'garment-thumb';
                img.style.cssText = 'width:36px;height:36px;border-radius:3px;object-fit:cover;flex-shrink:0;margin-right:6px;';
                item.appendChild(img);
            }
            const nameSpan = document.createElement('span');
            nameSpan.className = 'garment-name';
            nameSpan.textContent = g.name || g.id;
            nameSpan.style.cssText = 'flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;';
            item.appendChild(nameSpan);
            item.style.cssText += 'display:flex;align-items:center;padding:4px 12px 4px 28px;';
            item.addEventListener('click', () => {
                list.querySelectorAll('.anim-item.active').forEach(el => el.classList.remove('active'));
                item.classList.add('active');
                _selectedGarmentId = g.id;
                // Apply garment defaults to sliders
                if (g.offset !== undefined) {
                    const offEl = document.getElementById('garment-offset');
                    if (offEl) { offEl.value = Math.round(g.offset * 1000); offEl.dispatchEvent(new Event('input')); }
                }
                if (g.stiffness !== undefined) {
                    const stEl = document.getElementById('garment-stiffness');
                    if (stEl) { stEl.value = Math.round(g.stiffness * 100); stEl.dispatchEvent(new Event('input')); }
                }
                // Reset min-dist / crotch-floor to defaults for new garment
                const mdEl = document.getElementById('garment-min-dist');
                if (mdEl) { mdEl.value = 3; mdEl.dispatchEvent(new Event('input')); }
                const cfEl = document.getElementById('garment-crotch-floor');
                if (cfEl) { cfEl.value = 0; cfEl.dispatchEvent(new Event('input')); }
                const liftDefEl = document.getElementById('garment-lift');
                if (liftDefEl) { liftDefEl.value = 0; liftDefEl.dispatchEvent(new Event('input')); }
                const cdDefEl = document.getElementById('garment-crotch-depth');
                if (cdDefEl) { cdDefEl.value = 0; cdDefEl.dispatchEvent(new Event('input')); }
                if (g.color) {
                    const cEl = document.getElementById('garment-color');
                    if (cEl) {
                        const c = Array.isArray(g.color) ? g.color : [0.3, 0.35, 0.5];
                        cEl.value = '#' + new THREE.Color(c[0], c[1], c[2]).getHexString();
                    }
                }
                // Reset region sliders to 0
                for (const rid of REGION_IDS) {
                    const rEl = document.getElementById(`garment-region-${rid}`);
                    if (rEl) { rEl.value = 0; rEl.dispatchEvent(new Event('input')); }
                }
            });
            item.addEventListener('dblclick', () => _doGarmentFit());
            body.appendChild(item);
        }
        catDiv.appendChild(body);
        list.appendChild(catDiv);
    }
}

async function _doGarmentFit() {
    if (!_selectedGarmentId) return;
    const inst = _selectedInst();
    if (!inst) return;

    // Auto-skin character if skeleton data is available
    if (!inst.isSkinned && rigifySkeletonData && skinWeightData) {
        convertInstToSkinned(inst);
    }

    // Remember selection key before refit
    const selKey = (_selectedSubMesh && _selectedSubMesh.charId === inst.id)
        ? _selectedSubMesh.key : null;

    _refitting = true;

    const params = _charQueryParams(inst);
    params.set('garment_id', _selectedGarmentId);
    params.set('offset', (_sliderVal('garment-offset') / 1000).toFixed(4));
    params.set('stiffness', (_sliderVal('garment-stiffness') / 100).toFixed(2));
    params.set('min_dist', _sliderVal('garment-min-dist'));
    params.set('crotch_floor', _sliderVal('garment-crotch-floor'));
    params.set('lift', _sliderVal('garment-lift'));
    params.set('crotch_depth', _sliderVal('garment-crotch-depth'));

    // Color
    const colorHex = document.getElementById('garment-color')?.value || '#4d5980';
    const c = new THREE.Color(colorHex);
    params.set('color_r', c.r.toFixed(3));
    params.set('color_g', c.g.toFixed(3));
    params.set('color_b', c.b.toFixed(3));

    try {
        const resp = await fetch(`/api/character/garment/fit/?${params}`);
        const data = await resp.json();
        if (data.error) { console.warn('Garment fit error:', data.error); _refitting = false; return; }

        const key = `gar_${_selectedGarmentId}`;

        // Remove old if exists
        if (inst.clothMeshes[key]) {
            inst.group.remove(inst.clothMeshes[key]);
            inst.clothMeshes[key].geometry.dispose();
            inst.clothMeshes[key].material.dispose();
            delete inst.clothMeshes[key];
        }

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces);
        const normalBuf = base64ToFloat32(data.normals);
        blenderToThreeCoords(normalBuf);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));

        const roughness = _sliderVal('garment-roughness') / 100;
        const metalness = _sliderVal('garment-metalness') / 100;
        const mat = new THREE.MeshStandardMaterial({
            color: c, roughness, metalness, side: THREE.DoubleSide,
        });

        const mesh = _skinifyMesh(geo, mat, inst, data);
        inst.clothMeshes[key] = mesh;
        inst.group.add(mesh);

        // Store original positions + compute region weights
        inst.garmentOrigPositions[key] = new Float32Array(vertBuf);
        _computeGarmentRegionWeights(inst, key);

        // Preserve region state across re-fits
        const prevSt = inst.garmentState[key];

        // Save garment state
        const gState = {
            offset: _sliderVal('garment-offset') / 1000,
            stiffness: _sliderVal('garment-stiffness') / 100,
            minDist: _sliderVal('garment-min-dist'),
            crotchFloor: _sliderVal('garment-crotch-floor'),
            lift: _sliderVal('garment-lift'),
            crotchDepth: _sliderVal('garment-crotch-depth'),
            color: [c.r, c.g, c.b],
            roughness,
            metalness,
            regionTop: prevSt?.regionTop || 0,
            regionUpper: prevSt?.regionUpper || 0,
            regionMid: prevSt?.regionMid || 0,
            regionLower: prevSt?.regionLower || 0,
            regionBottom: prevSt?.regionBottom || 0,
        };
        inst.garmentState[key] = gState;

        // Apply region offsets to the new mesh
        _applyGarmentRegionOffsets(inst, key);

        // Update persistent garments array for save/load
        inst.garments = inst.garments.filter(g => g.id !== _selectedGarmentId);
        inst.garments.push({ id: _selectedGarmentId, ...gState });

        // Re-select by key (not by stale reference) to fix selection loss
        if (selKey === key) {
            _selectedSubMesh = { type: 'cloth', key, label: _selectedGarmentId, meshObj: mesh, charId: inst.id };
            _setSubMeshEmissive(_selectedSubMesh, _SELECT_EMISSIVE);
            _syncPropGarmentControls();
        }

        _refitting = false;
        updateEquippedList(inst);
        updateVertexCount();
    } catch (e) {
        _refitting = false;
        console.error('Garment fit failed:', e);
    }
}

// =========================================================================
// Asset Panel: Hair
// =========================================================================
async function loadHairUI() {
    try {
        const resp = await fetch('/api/character/hairstyles/');
        const data = await resp.json();
        _hairStylesData = data.hairstyles || [];
        hairColorData = data.colors || {};

        // Populate prop-tab hair dropdowns now that data is available
        _populatePropHairOptions();

        const select = document.getElementById('hair-style-select');
        const colorSelect = document.getElementById('hair-color-select');
        if (!select) return;

        for (const h of _hairStylesData) {
            const opt = document.createElement('option');
            opt.value = h.url;
            opt.textContent = h.label;
            opt.dataset.name = h.name;
            select.appendChild(opt);
        }

        if (colorSelect) {
            for (const name of Object.keys(hairColorData)) {
                const opt = document.createElement('option');
                opt.value = name;
                opt.textContent = name;
                colorSelect.appendChild(opt);
            }
        }

        select.addEventListener('change', () => {
            const inst = _selectedInst();
            if (!inst) return;
            if (!select.value) {
                // Remove hair
                if (inst.hairMesh) {
                    inst.group.remove(inst.hairMesh);
                    inst.hairMesh.traverse(child => {
                        if (child.isMesh) {
                            child.geometry.dispose();
                            const mats = Array.isArray(child.material) ? child.material : [child.material];
                            mats.forEach(m => m.dispose());
                        }
                    });
                    inst.hairMesh = null;
                    inst.hairStyle = null;
                }
                updateEquippedList(inst);
                updateVertexCount();
                return;
            }
            const colorName = colorSelect?.value || '';
            _loadHairForCharacter(inst, select.value, colorName);
        });

        if (colorSelect) {
            colorSelect.addEventListener('change', () => {
                const inst = _selectedInst();
                if (!inst || !inst.hairMesh) return;
                const rgb = hairColorData[colorSelect.value];
                if (!rgb) return;
                const color = new THREE.Color(rgb[0], rgb[1], rgb[2]);
                inst.hairMesh.traverse(child => {
                    if (child.isMesh && child.material) {
                        const mats = Array.isArray(child.material) ? child.material : [child.material];
                        mats.forEach(m => { m.color.copy(color); });
                    }
                });
            });
        }
    } catch (e) {
        console.warn('Hair UI not available:', e);
    }
}

function _loadHairForCharacter(inst, url, colorName) {
    // Remove old hair
    if (inst.hairMesh) {
        inst.group.remove(inst.hairMesh);
        inst.hairMesh.traverse(child => {
            if (child.isMesh) {
                child.geometry.dispose();
                const mats = Array.isArray(child.material) ? child.material : [child.material];
                mats.forEach(m => m.dispose());
            }
        });
        inst.hairMesh = null;
    }

    // Auto-skin character if skeleton data is available
    if (!inst.isSkinned && rigifySkeletonData && skinWeightData) {
        convertInstToSkinned(inst);
    }

    gltfLoader.load(url, (gltf) => {
        let hairGroup = gltf.scene;

        // Convert to skinned meshes bound to head bone
        if (inst.isSkinned && inst.rigifySkeleton) {
            hairGroup = _skinifyHairGroup(hairGroup, inst);
        }

        inst.hairMesh = hairGroup;
        inst.hairStyle = { url, name: url.split('/').pop(), color: colorName };

        if (colorName && hairColorData[colorName]) {
            const rgb = hairColorData[colorName];
            const color = new THREE.Color(rgb[0], rgb[1], rgb[2]);
            inst.hairMesh.traverse(child => {
                if (child.isMesh && child.material) {
                    const mats = Array.isArray(child.material) ? child.material : [child.material];
                    mats.forEach(m => { m.color.copy(color); });
                }
            });
        }

        inst.group.add(inst.hairMesh);
        updateEquippedList(inst);
        updateVertexCount();
    }, undefined, (err) => {
        console.warn('Failed to load hair:', err);
    });
}

/** Sync hair dropdown to current character's hair state. */
function syncHairSelect(inst) {
    const select = document.getElementById('hair-style-select');
    if (!select) return;
    if (inst.hairStyle && inst.hairStyle.url) {
        select.value = inst.hairStyle.url;
    } else {
        select.value = '';
    }
}

// =========================================================================
// Asset Panel: Cloth (Template, Builder, Primitive)
// =========================================================================
async function loadClothUI() {
    _bindSlider('cloth-tpl-segments', 'cloth-tpl-segments-val', v => v);
    _bindSlider('cloth-tpl-tightness', 'cloth-tpl-tightness-val', v => (v / 100).toFixed(2));
    _bindSlider('cloth-tpl-top-ext', 'cloth-tpl-top-ext-val', v => (v / 100).toFixed(2) + ' m');
    _bindSlider('cloth-tpl-bot-ext', 'cloth-tpl-bot-ext-val', v => (v / 100).toFixed(2) + ' m');
    _bindSlider('cloth-bld-looseness', 'cloth-bld-looseness-val', v => (v / 100).toFixed(2));
    _bindSlider('cloth-prim-segments', 'cloth-prim-segments-val', v => v);
    _bindSlider('cloth-prim-length', 'cloth-prim-length-val', v => (v / 100).toFixed(2));
    _bindSlider('cloth-prim-flare', 'cloth-prim-flare-val', v => (v / 100).toFixed(2));

    try {
        const resp = await fetch('/api/character/cloth/regions/');
        _clothRegionsData = await resp.json();

        // Populate template dropdown
        const tplSelect = document.getElementById('cloth-tpl-type');
        if (tplSelect && _clothRegionsData.templates) {
            for (const t of _clothRegionsData.templates) {
                const opt = document.createElement('option');
                opt.value = t.key;
                opt.textContent = t.label;
                tplSelect.appendChild(opt);
            }
        }

        // Populate builder region dropdown
        const bldSelect = document.getElementById('cloth-bld-region');
        if (bldSelect && _clothRegionsData.builder_regions) {
            for (const r of _clothRegionsData.builder_regions) {
                const opt = document.createElement('option');
                opt.value = r.key;
                opt.textContent = r.label;
                bldSelect.appendChild(opt);
            }
        }

        // Populate primitive dropdown
        const primSelect = document.getElementById('cloth-prim-type');
        if (primSelect && _clothRegionsData.primitives) {
            for (const p of _clothRegionsData.primitives) {
                const opt = document.createElement('option');
                opt.value = p.key;
                opt.textContent = p.label;
                primSelect.appendChild(opt);
            }
            primSelect.addEventListener('change', () => {
                const flareRow = document.getElementById('cloth-prim-flare-row');
                if (flareRow) flareRow.style.display = primSelect.value === 'PRIM_SKIRT' ? 'flex' : 'none';
            });
        }
    } catch (e) {
        console.warn('Cloth UI not available:', e);
    }

    // --- Button bindings ---

    // Template create
    const tplCreate = document.getElementById('cloth-tpl-create');
    if (tplCreate) tplCreate.addEventListener('click', () => _doClothFromTemplate(false));

    // Template update
    const tplUpdate = document.getElementById('cloth-tpl-update');
    if (tplUpdate) tplUpdate.addEventListener('click', () => _doClothFromTemplate(true));

    // Template delete
    const tplDelete = document.getElementById('cloth-tpl-delete');
    if (tplDelete) tplDelete.addEventListener('click', () => {
        const inst = _selectedInst();
        if (!inst) return;
        const tpl = document.getElementById('cloth-tpl-type')?.value;
        if (!tpl) return;
        const key = `tpl_${tpl}`;
        if (inst.clothMeshes[key]) {
            const t = { type: 'cloth', key, meshObj: inst.clothMeshes[key], charId: inst.id };
            _removeSubMesh(t);
        }
    });

    // Remove all cloth
    const removeAll = document.getElementById('cloth-remove-all');
    if (removeAll) removeAll.addEventListener('click', () => {
        const inst = _selectedInst();
        if (!inst) return;
        const keys = Object.keys(inst.clothMeshes).filter(k => k.startsWith('tpl_'));
        for (const key of keys) {
            const t = { type: 'cloth', key, meshObj: inst.clothMeshes[key], charId: inst.id };
            _removeSubMesh(t);
        }
    });

    // Builder create
    const bldCreate = document.getElementById('cloth-bld-create');
    if (bldCreate) bldCreate.addEventListener('click', () => {
        const inst = _selectedInst();
        if (!inst) return;
        const region = document.getElementById('cloth-bld-region')?.value || 'TOP';
        const loose = _sliderVal('cloth-bld-looseness') / 100;
        _loadClothForCharacter(inst, `bld_${region}`, {
            method: 'builder', region, looseness: loose,
        });
    });

    // Primitive create
    const primCreate = document.getElementById('cloth-prim-create');
    if (primCreate) primCreate.addEventListener('click', () => {
        const inst = _selectedInst();
        if (!inst) return;
        const pt = document.getElementById('cloth-prim-type')?.value || 'PRIM_SKIRT';
        _loadClothForCharacter(inst, `prim_${pt}`, {
            method: 'primitive',
            prim_type: pt,
            segments: _sliderVal('cloth-prim-segments'),
            length: _sliderVal('cloth-prim-length') / 100,
            flare: _sliderVal('cloth-prim-flare') / 100,
        });
    });
}

function _doClothFromTemplate(isUpdate) {
    const inst = _selectedInst();
    if (!inst) return;
    const tpl = document.getElementById('cloth-tpl-type')?.value;
    if (!tpl) return;
    const key = `tpl_${tpl}`;

    // If update and mesh doesn't exist, create instead
    if (isUpdate && !inst.clothMeshes[key]) return;

    _loadClothForCharacter(inst, key, {
        method: 'template',
        template: tpl,
        segments: _sliderVal('cloth-tpl-segments'),
        tightness: _sliderVal('cloth-tpl-tightness') / 100,
        top_extend: _sliderVal('cloth-tpl-top-ext') / 100,
        bottom_extend: _sliderVal('cloth-tpl-bot-ext') / 100,
    });
}

async function _loadClothForCharacter(inst, key, clothParams) {
    const params = _charQueryParams(inst);
    for (const [k, v] of Object.entries(clothParams)) {
        params.set(k, v);
    }

    // Color from color picker
    const colorHex = document.getElementById('cloth-color')?.value || '#404870';
    const matColor = new THREE.Color(colorHex);

    try {
        const resp = await fetch(`/api/character/cloth/?${params}`);
        const data = await resp.json();
        if (data.error) { console.warn('Cloth error:', data.error); return; }

        // Remove old mesh for this key
        if (inst.clothMeshes[key]) {
            inst.group.remove(inst.clothMeshes[key]);
            inst.clothMeshes[key].geometry.dispose();
            inst.clothMeshes[key].material.dispose();
            delete inst.clothMeshes[key];
        }

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces);
        const normalBuf = base64ToFloat32(data.normals);
        blenderToThreeCoords(normalBuf);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));

        const mat = new THREE.MeshStandardMaterial({
            color: matColor, roughness: 0.8, metalness: 0.0, side: THREE.DoubleSide,
        });

        const mesh = new THREE.Mesh(geo, mat);
        inst.clothMeshes[key] = mesh;
        inst.group.add(mesh);

        // Sync to inst.cloth for scene persistence
        const clothEntry = { ...clothParams, color: colorHex };
        if (!inst.cloth) inst.cloth = [];
        const idx = inst.cloth.findIndex(c => {
            const m = c.method || 'template';
            let ck;
            if (m === 'builder') ck = `bld_${c.region || 'TOP'}`;
            else if (m === 'primitive') ck = `prim_${c.prim_type || 'PRIM_SKIRT'}`;
            else ck = `tpl_${c.template || 'TPL_TSHIRT'}`;
            return ck === key;
        });
        if (idx >= 0) {
            inst.cloth[idx] = clothEntry;
        } else {
            inst.cloth.push(clothEntry);
        }

        updateEquippedList(inst);
        updateVertexCount();
        markDirty();
    } catch (e) {
        console.error('Cloth load failed:', e);
    }
}

// =========================================================================
// Animation Panel
// =========================================================================
async function loadAnimationUI() {
    // Load animation tree
    try {
        const resp = await fetch('/api/character/animations/');
        const data = await resp.json();
        const tree = document.getElementById('anim-tree');
        if (!tree) return;
        tree.innerHTML = '';

        const categories = data.categories || {};
        const catNames = Object.keys(categories).sort();

        if (catNames.length === 0) {
            tree.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Animationen gefunden</div>';
            return;
        }

        for (const cat of catNames) {
            const anims = categories[cat];
            const catDiv = document.createElement('div');
            catDiv.className = 'anim-category';

            const header = document.createElement('div');
            header.className = 'anim-category-header';
            header.innerHTML = `<span class="cat-chevron"><i class="fas fa-chevron-right"></i></span>
                <span>${escapeHtml(cat)}</span>
                <span class="cat-count">${anims.length}</span>`;
            header.addEventListener('click', () => catDiv.classList.toggle('open'));
            catDiv.appendChild(header);

            const body = document.createElement('div');
            body.className = 'anim-category-body';

            for (const anim of anims) {
                const item = document.createElement('div');
                item.className = 'anim-item';
                item.innerHTML = `<span>${escapeHtml(anim.name)}</span><span class="frames">${anim.frames || ''}f</span>`;
                item.addEventListener('click', () => {
                    tree.querySelectorAll('.anim-item.active').forEach(el => el.classList.remove('active'));
                    item.classList.add('active');
                    currentAnimName = anim.name;
                    loadBVHAnimation(anim.url, anim.name, anim.frames || 0);
                    const info = document.getElementById('anim-info');
                    if (info) info.textContent = `${anim.name} — ${anim.frames || '?'}f`;
                    const playBtn = document.getElementById('anim-play');
                    if (playBtn) playBtn.innerHTML = '<i class="fas fa-pause"></i>';
                });
                body.appendChild(item);
            }

            catDiv.appendChild(body);
            tree.appendChild(catDiv);
        }
    } catch (e) {
        const tree = document.getElementById('anim-tree');
        if (tree) tree.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Animationen nicht verfügbar</div>';
    }

    // Bind playback controls
    const playBtn = document.getElementById('anim-play');
    const stopBtn = document.getElementById('anim-stop');
    const timeline = document.getElementById('anim-timeline');
    const speedSlider = document.getElementById('anim-speed');
    const speedLabel = document.getElementById('speed-label');

    if (speedSlider && speedLabel) {
        speedSlider.addEventListener('input', () => {
            const speed = parseInt(speedSlider.value) / 100;
            speedLabel.textContent = `Speed: ${speed.toFixed(1)}x`;
            if (mixer) mixer.timeScale = speed;
        });
    }

    if (playBtn) {
        playBtn.addEventListener('click', () => {
            if (!currentAction) return;
            playing = !playing;
            if (playing) {
                if (!currentAction.isRunning()) currentAction.play();
                currentAction.paused = false;
            } else {
                currentAction.paused = true;
            }
            playBtn.innerHTML = playing ? '<i class="fas fa-pause"></i>' : '<i class="fas fa-play"></i>';
        });
    }

    if (stopBtn) {
        stopBtn.addEventListener('click', () => {
            stopAnimation(false);  // false = pause, don't destroy
            if (playBtn) playBtn.innerHTML = '<i class="fas fa-play"></i>';
            if (timeline) timeline.value = 0;
            currentAnimName = '';
            currentAnimDuration = 0;
            const info = document.getElementById('anim-info');
            if (info) info.textContent = '\u2014';
            // Update demo button too
            const demoBtn = document.getElementById('play-demo-anim');
            if (demoBtn) { demoBtn.innerHTML = '<i class="fas fa-play"></i>'; demoBtn.classList.remove('active'); }
        });
    }

    if (timeline) {
        timeline.addEventListener('input', () => {
            if (currentAction && currentAction.getClip()) {
                const dur = currentAction.getClip().duration;
                const time = (parseInt(timeline.value) / 100) * dur;
                currentAction.time = time;
                if (mixer) mixer.update(0);
            }
        });
    }

    // Delta norm toggle
    const deltaSel = document.getElementById('scene-delta-norm');
    if (deltaSel) {
        deltaSel.addEventListener('change', () => {
            const v = deltaSel.value;
            _sceneDeltaNorm = v === 'auto' ? undefined : v === '1';
            // Reload current animation with new setting
            if (currentAnimUrl) {
                loadBVHAnimation(currentAnimUrl, currentAnimName, 0, currentAnimBvhText || null);
            }
        });
    }

    // Ground fix toggle
    const groundChk = document.getElementById('scene-ground-fix');
    if (groundChk) {
        groundChk.addEventListener('change', () => {
            currentAnimGroundFixed = groundChk.checked;
        });
    }

    // Smooth sigma slider
    const smoothSlider = document.getElementById('smooth-sigma');
    const smoothVal = document.getElementById('smooth-sigma-val');
    if (smoothSlider && smoothVal) {
        smoothSlider.addEventListener('input', () => {
            smoothVal.textContent = parseFloat(smoothSlider.value).toFixed(1);
        });
    }

    // Smooth apply — Gaussian smooth on the retargeted AnimationClip tracks
    let _unsmoothClipData = null;  // backup for reset
    document.getElementById('smooth-apply')?.addEventListener('click', () => {
        if (!currentAction) { alert('Keine Animation geladen.'); return; }
        const clip = currentAction.getClip();
        if (!clip) return;
        const sigma = parseFloat(smoothSlider?.value || 2);
        if (sigma <= 0) return;

        // Backup original track values for reset
        if (!_unsmoothClipData) {
            _unsmoothClipData = clip.tracks.map(t => ({
                name: t.name,
                values: new Float32Array(t.values),
            }));
        }

        // Gaussian kernel
        const radius = Math.ceil(sigma * 3);
        const kernel = [];
        let ksum = 0;
        for (let i = -radius; i <= radius; i++) {
            const v = Math.exp(-0.5 * (i / sigma) ** 2);
            kernel.push(v);
            ksum += v;
        }
        for (let i = 0; i < kernel.length; i++) kernel[i] /= ksum;

        // Apply to each track
        for (const track of clip.tracks) {
            const stride = track.getValueSize();
            const nKeys = track.values.length / stride;
            const orig = new Float32Array(track.values);

            for (let c = 0; c < stride; c++) {
                for (let k = 0; k < nKeys; k++) {
                    let sum = 0;
                    for (let j = 0; j < kernel.length; j++) {
                        const idx = Math.max(0, Math.min(nKeys - 1, k + j - radius));
                        sum += kernel[j] * orig[idx * stride + c];
                    }
                    track.values[k * stride + c] = sum;
                }
            }

            // Re-normalize quaternion tracks
            if (stride === 4) {
                for (let k = 0; k < nKeys; k++) {
                    const i = k * 4;
                    const len = Math.sqrt(
                        track.values[i] ** 2 + track.values[i+1] ** 2 +
                        track.values[i+2] ** 2 + track.values[i+3] ** 2
                    );
                    if (len > 1e-8) {
                        track.values[i] /= len;
                        track.values[i+1] /= len;
                        track.values[i+2] /= len;
                        track.values[i+3] /= len;
                    }
                }
            }
        }

        console.log(`[SMOOTH] Applied sigma=${sigma} to ${clip.tracks.length} tracks, ${radius * 2 + 1} kernel`);
        // Reset mixer to apply changes
        if (mixer) mixer.setTime(currentAction.time);
    });

    // Smooth reset
    document.getElementById('smooth-reset')?.addEventListener('click', () => {
        if (!_unsmoothClipData || !currentAction) return;
        const clip = currentAction.getClip();
        for (let i = 0; i < clip.tracks.length; i++) {
            const backup = _unsmoothClipData.find(b => b.name === clip.tracks[i].name);
            if (backup) clip.tracks[i].values.set(backup.values);
        }
        _unsmoothClipData = null;
        if (mixer) mixer.setTime(currentAction.time);
        console.log('[SMOOTH] Reset to original');
    });

    // Save animation
    document.getElementById('anim-save-btn')?.addEventListener('click', () => {
        if (!currentAnimBvhText && !currentAnimUrl) { alert('Keine Animation geladen.'); return; }
        openSaveAnimDialog();
    });
}

// =========================================================================
// Model Generator UI
// =========================================================================
let _mgConfig = null;      // Current model config
let _mgSelectedBone = null; // Currently selected bone name
let _mgInitialized = false;
let _mgSkeletonType = 'rig';  // 'def' or 'rig'
let _mgRigBonesData = null;   // Cached rig bones data
let _mgCharacterId = null;    // ID of generated character in characters map

async function initModelGenerator() {
    if (!rigifySkeletonData || !skinWeightData) {
        console.warn('Model Generator: skeleton data not loaded yet');
        return;
    }

    if (!_mgConfig) {
        // Check if a loaded character already has a generated config (e.g. Rig3)
        const sel = _selectedInst();
        const genInst = (sel && sel.generatedConfig) ? sel
            : [...characters.values()].find(c => c.generatedConfig) || null;
        if (genInst && genInst.generatedConfig) {
            _mgConfig = JSON.parse(JSON.stringify(genInst.generatedConfig));
            _mgSkeletonType = genInst.generatedConfig.skeleton_type || 'rig';
            _mgCharacterId = genInst.id;
            // Ensure rig bones data is loaded for rig-type models
            if (_mgSkeletonType === 'rig' && !_mgRigBonesData) {
                try {
                    const resp = await fetch('/api/character/rig/');
                    if (resp.ok) _mgRigBonesData = await resp.json();
                } catch (e) { /* ignore */ }
            }
            console.log('[MG] Synced config from loaded character:', genInst.presetName);
        } else if (_mgSkeletonType === 'rig') {
            // Load rig bones data for default rig mode
            if (!_mgRigBonesData) {
                try {
                    const resp = await fetch('/api/character/rig/');
                    if (resp.ok) _mgRigBonesData = await resp.json();
                } catch (e) {
                    console.warn('Failed to load rig bones:', e);
                }
            }
            if (_mgRigBonesData && _mgRigBonesData.bones && _mgRigBonesData.bones.length > 0) {
                _mgConfig = getDefaultRigConfig(_mgRigBonesData);
            } else {
                // Fallback to DEF if rig data unavailable
                _mgSkeletonType = 'def';
                _mgConfig = getDefaultModelConfig(rigifySkeletonData, skinWeightData);
            }
        } else {
            _mgConfig = getDefaultModelConfig(rigifySkeletonData, skinWeightData);
        }
    }

    if (!_mgInitialized) {
        _bindModelGeneratorUI();
        _mgInitialized = true;
    }

    // Sync skeleton type dropdown
    const skelSelect = document.getElementById('mg-skeleton-type');
    if (skelSelect) skelSelect.value = _mgSkeletonType;

    _populateBoneTree();
    _syncMGGlobalUI();

    // Expand Modell tab panel sections
    document.querySelectorAll('#tab-modell .panel-section').forEach(p => {
        p.classList.remove('collapsed');
    });
}

function _bindModelGeneratorUI() {
    // Skeleton type selector
    const skelSelect = document.getElementById('mg-skeleton-type');
    if (skelSelect) skelSelect.addEventListener('change', async () => {
        const newType = skelSelect.value;
        if (newType === _mgSkeletonType) return;
        _mgSkeletonType = newType;

        if (newType === 'rig') {
            // Fetch rig bones data if not cached
            if (!_mgRigBonesData) {
                try {
                    const resp = await fetch('/api/character/rig/');
                    if (resp.ok) _mgRigBonesData = await resp.json();
                } catch (e) {
                    console.warn('Failed to load rig bones:', e);
                }
            }
            if (_mgRigBonesData && _mgRigBonesData.bones && _mgRigBonesData.bones.length > 0) {
                _mgConfig = getDefaultRigConfig(_mgRigBonesData);
            } else {
                console.warn('Rig bones data not available');
                _mgSkeletonType = 'def';
                skelSelect.value = 'def';
                return;
            }
        } else {
            _mgConfig = getDefaultModelConfig(rigifySkeletonData, skinWeightData);
        }

        _mgSelectedBone = null;
        _clearBoneHighlightCache();
        const propsSection = document.getElementById('mg-bone-props-section');
        if (propsSection) propsSection.style.display = 'none';

        _populateBoneTree();
        _syncMGGlobalUI();
    });

    // Global controls
    const nameInput = document.getElementById('mg-model-name');
    if (nameInput) nameInput.addEventListener('input', () => { _mgConfig.name = nameInput.value; });

    const colorInput = document.getElementById('mg-default-color');
    if (colorInput) colorInput.addEventListener('input', () => {
        _mgConfig.default_color = colorInput.value;
    });

    const radiusSlider = document.getElementById('mg-default-radius');
    const radiusVal = document.getElementById('mg-default-radius-val');
    if (radiusSlider) radiusSlider.addEventListener('input', () => {
        const v = parseFloat(radiusSlider.value);
        _mgConfig.default_radius = v;
        if (radiusVal) radiusVal.textContent = v.toFixed(3);
    });

    const segSlider = document.getElementById('mg-segments');
    const segVal = document.getElementById('mg-segments-val');
    if (segSlider) segSlider.addEventListener('input', () => {
        const v = parseInt(segSlider.value);
        _mgConfig.segments = v;
        if (segVal) segVal.textContent = v;
    });

    // Bone properties
    const boneShape = document.getElementById('mg-bone-shape');
    if (boneShape) boneShape.addEventListener('change', () => {
        if (!_mgSelectedBone || !_mgConfig.bone_parts[_mgSelectedBone]) return;
        _mgConfig.bone_parts[_mgSelectedBone].shape = boneShape.value;
        const overlapRow = document.getElementById('mg-overlap-row');
        if (overlapRow) overlapRow.style.display = boneShape.value === 'double_oval' ? '' : 'none';
        const tutuParams = document.getElementById('mg-tutu-params');
        if (tutuParams) tutuParams.style.display = boneShape.value === 'tutu' ? '' : 'none';
        const spiralParams = document.getElementById('mg-spiral-tutu-params');
        if (spiralParams) spiralParams.style.display = boneShape.value === 'spiral_tutu' ? '' : 'none';
        const helixParams = document.getElementById('mg-helix-ribbon-params');
        if (helixParams) helixParams.style.display = boneShape.value === 'helix_ribbon' ? '' : 'none';
        const skirtParams = document.getElementById('mg-skirt-params');
        if (skirtParams) skirtParams.style.display = boneShape.value === 'skirt' ? '' : 'none';
        _mgAutoRegenerate();
    });

    // Tutu parameter sliders
    function _tutuSlider(id, valId, prop, fmt) {
        const el = document.getElementById(id);
        const valEl = document.getElementById(valId);
        if (!el) return;
        el.addEventListener('input', () => {
            const v = parseFloat(el.value);
            if (valEl) valEl.textContent = v.toFixed(fmt || 3);
            if (!_mgSelectedBone || !_mgConfig.bone_parts[_mgSelectedBone]) return;
            _mgConfig.bone_parts[_mgSelectedBone][prop] = v;
            _mgAutoRegenerate();
        });
    }
    _tutuSlider('mg-tutu-thickness', 'mg-tutu-thickness-val', 'tutuThickness', 3);
    _tutuSlider('mg-tutu-droop', 'mg-tutu-droop-val', 'tutuDroop', 3);
    _tutuSlider('mg-tutu-droop-start', 'mg-tutu-droop-start-val', 'tutuDroopStart', 2);
    _tutuSlider('mg-tutu-offset', 'mg-tutu-offset-val', 'tutuOffset', 3);

    // Spiral-Tutu sliders
    _tutuSlider('mg-spiral-winds', 'mg-spiral-winds-val', 'spiralWinds', 0);
    _tutuSlider('mg-spiral-start-r', 'mg-spiral-start-r-val', 'spiralStartR', 3);
    _tutuSlider('mg-spiral-end-r', 'mg-spiral-end-r-val', 'spiralEndR', 3);
    _tutuSlider('mg-spiral-pos-top', 'mg-spiral-pos-top-val', 'spiralPosTop', 3);
    _tutuSlider('mg-spiral-pos-bottom', 'mg-spiral-pos-bottom-val', 'spiralPosBottom', 3);
    _tutuSlider('mg-spiral-thickness', 'mg-spiral-thickness-val', 'tutuThickness', 3);
    _tutuSlider('mg-spiral-droop', 'mg-spiral-droop-val', 'tutuDroop', 3);
    const spiralSkirtCb = document.getElementById('mg-spiral-skirt');
    if (spiralSkirtCb) spiralSkirtCb.addEventListener('change', () => {
        if (!_mgSelectedBone || !_mgConfig.bone_parts[_mgSelectedBone]) return;
        _mgConfig.bone_parts[_mgSelectedBone].spiralSkirt = spiralSkirtCb.checked;
        _mgAutoRegenerate();
    });

    // Helix ribbon sliders
    _tutuSlider('mg-helix-winds', 'mg-helix-winds-val', 'spiralWinds', 1);
    _tutuSlider('mg-helix-start-r', 'mg-helix-start-r-val', 'spiralStartR', 3);
    _tutuSlider('mg-helix-end-r', 'mg-helix-end-r-val', 'spiralEndR', 3);
    _tutuSlider('mg-helix-ribbon-w', 'mg-helix-ribbon-w-val', 'ribbonWidth', 3);
    _tutuSlider('mg-helix-pos-top', 'mg-helix-pos-top-val', 'spiralPosTop', 3);
    _tutuSlider('mg-helix-pos-bottom', 'mg-helix-pos-bottom-val', 'spiralPosBottom', 3);
    _tutuSlider('mg-helix-thickness', 'mg-helix-thickness-val', 'tutuThickness', 3);
    _tutuSlider('mg-helix-droop', 'mg-helix-droop-val', 'tutuDroop', 3);
    const helixSkirtCb = document.getElementById('mg-helix-skirt');
    if (helixSkirtCb) helixSkirtCb.addEventListener('change', () => {
        if (!_mgSelectedBone || !_mgConfig.bone_parts[_mgSelectedBone]) return;
        _mgConfig.bone_parts[_mgSelectedBone].spiralSkirt = helixSkirtCb.checked;
        _mgAutoRegenerate();
    });

    // Skirt sliders
    _tutuSlider('mg-skirt-radius-top', 'mg-skirt-radius-top-val', 'skirtRadiusTop', 3);
    _tutuSlider('mg-skirt-radius-bottom', 'mg-skirt-radius-bottom-val', 'skirtRadiusBottom', 3);
    _tutuSlider('mg-skirt-pos-top', 'mg-skirt-pos-top-val', 'skirtPosTop', 3);
    _tutuSlider('mg-skirt-pos-bottom', 'mg-skirt-pos-bottom-val', 'skirtPosBottom', 3);
    _tutuSlider('mg-skirt-thickness', 'mg-skirt-thickness-val', 'skirtThickness', 3);

    const boneRadius = document.getElementById('mg-bone-radius');
    const boneRadiusVal = document.getElementById('mg-bone-radius-val');
    if (boneRadius) boneRadius.addEventListener('input', () => {
        const v = parseFloat(boneRadius.value);
        if (boneRadiusVal) boneRadiusVal.textContent = v.toFixed(3);
        if (!_mgSelectedBone || !_mgConfig.bone_parts[_mgSelectedBone]) return;
        _mgConfig.bone_parts[_mgSelectedBone].radius = v;
        _updateBoneTreeItem(_mgSelectedBone);
        _mgAutoRegenerate();
    });

    const boneColor = document.getElementById('mg-bone-color');
    if (boneColor) boneColor.addEventListener('input', () => {
        if (!_mgSelectedBone || !_mgConfig.bone_parts[_mgSelectedBone]) return;
        _mgConfig.bone_parts[_mgSelectedBone].color = boneColor.value;
        _updateBoneTreeItem(_mgSelectedBone);
        _mgAutoRegenerate();
    });

    // Overlap slider (double_oval)
    const boneOverlap = document.getElementById('mg-bone-overlap');
    const boneOverlapVal = document.getElementById('mg-bone-overlap-val');
    if (boneOverlap) boneOverlap.addEventListener('input', () => {
        const v = parseFloat(boneOverlap.value);
        if (boneOverlapVal) boneOverlapVal.textContent = v.toFixed(2);
        if (!_mgSelectedBone || !_mgConfig.bone_parts[_mgSelectedBone]) return;
        _mgConfig.bone_parts[_mgSelectedBone].overlap = v;
        _mgAutoRegenerate();
    });

    // Head/Tail offset sliders
    for (const end of ['head', 'tail']) {
        for (const axis of ['x', 'y', 'z']) {
            const slider = document.getElementById(`mg-${end}-off-${axis}`);
            const valSpan = document.getElementById(`mg-${end}-off-${axis}-val`);
            if (!slider) continue;
            slider.addEventListener('input', () => {
                const v = parseFloat(slider.value);
                if (valSpan) valSpan.textContent = v.toFixed(3);
                if (!_mgSelectedBone || !_mgConfig.bone_parts[_mgSelectedBone]) return;
                const part = _mgConfig.bone_parts[_mgSelectedBone];
                const key = end + 'Offset'; // headOffset or tailOffset
                if (!part[key]) part[key] = { x: 0, y: 0, z: 0 };
                part[key][axis] = v;
                _mgAutoRegenerate();
            });
        }
    }

    // Shape rotation sliders (degrees)
    for (const axis of ['x', 'y', 'z']) {
        const slider = document.getElementById(`mg-shape-rot-${axis}`);
        const valSpan = document.getElementById(`mg-shape-rot-${axis}-val`);
        if (!slider) continue;
        slider.addEventListener('input', () => {
            const v = parseFloat(slider.value);
            if (valSpan) valSpan.textContent = v;
            if (!_mgSelectedBone || !_mgConfig.bone_parts[_mgSelectedBone]) return;
            const part = _mgConfig.bone_parts[_mgSelectedBone];
            if (!part.shapeRotation) part.shapeRotation = { x: 0, y: 0, z: 0 };
            part.shapeRotation[axis] = v;
            _mgAutoRegenerate();
        });
    }

    // Action buttons
    const genBtn = document.getElementById('mg-generate');
    if (genBtn) genBtn.addEventListener('click', () => {
        _mgGenerateCharacter();
    });

    const saveServerBtn = document.getElementById('mg-save-server');
    if (saveServerBtn) saveServerBtn.addEventListener('click', () => {
        _mgSaveModelToServer();
    });
}

function _syncMGGlobalUI() {
    if (!_mgConfig) return;
    const nameInput = document.getElementById('mg-model-name');
    if (nameInput) nameInput.value = _mgConfig.name || 'Neues Modell';
    const colorInput = document.getElementById('mg-default-color');
    if (colorInput) colorInput.value = _mgConfig.default_color || '#4488cc';
    const radiusSlider = document.getElementById('mg-default-radius');
    const radiusVal = document.getElementById('mg-default-radius-val');
    if (radiusSlider) radiusSlider.value = _mgConfig.default_radius || 0.03;
    if (radiusVal) radiusVal.textContent = (_mgConfig.default_radius || 0.03).toFixed(3);
    const segSlider = document.getElementById('mg-segments');
    const segVal = document.getElementById('mg-segments-val');
    if (segSlider) segSlider.value = _mgConfig.segments || 8;
    if (segVal) segVal.textContent = _mgConfig.segments || 8;
}

function _populateBoneTree() {
    const container = document.getElementById('mg-bone-tree');
    if (!container || !_mgConfig) return;

    let categories;
    if (_mgSkeletonType === 'rig' && _mgRigBonesData) {
        const classified = classifyRigBones(_mgRigBonesData);
        categories = [
            { label: `DEF (${classified.def.length})`, bones: classified.def, collapsed: false },
            { label: `MCH (${classified.mch.length})`, bones: classified.mch, collapsed: true },
            { label: `ORG (${classified.org.length})`, bones: classified.org, collapsed: true },
            { label: `Control (${classified.control.length})`, bones: classified.control, collapsed: true },
        ];
    } else {
        const classified = classifyBones(rigifySkeletonData);
        categories = [
            { label: 'K\u00f6rper', bones: classified.body, collapsed: false },
            { label: 'Finger', bones: classified.finger, collapsed: true },
            { label: 'Gesicht', bones: classified.face, collapsed: true },
        ];
    }

    container.innerHTML = '';

    for (const cat of categories) {
        if (cat.bones.length === 0) continue;
        const catDiv = document.createElement('div');
        catDiv.className = 'mg-category';

        const header = document.createElement('div');
        header.className = 'mg-category-header' + (cat.collapsed ? ' collapsed' : '');
        header.innerHTML = `<span class="mg-chevron">&#9660;</span> ${cat.label} (${cat.bones.length})`;
        catDiv.appendChild(header);

        const body = document.createElement('div');
        body.className = 'mg-category-body' + (cat.collapsed ? ' hidden' : '');

        for (const boneName of cat.bones) {
            const part = _mgConfig.bone_parts[boneName];
            if (!part) continue;

            const item = document.createElement('div');
            item.className = 'mg-bone-item';
            item.dataset.bone = boneName;

            const cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.checked = part.visible;
            cb.addEventListener('change', (e) => {
                e.stopPropagation();
                part.visible = cb.checked;
                _mgAutoRegenerate();
            });

            const label = document.createElement('span');
            label.className = 'mg-bone-label';
            label.textContent = boneName.replace(/^(DEF|MCH|ORG)-/, '');
            label.title = boneName;

            const swatch = document.createElement('span');
            swatch.className = 'mg-bone-swatch';
            swatch.style.backgroundColor = part.color || _mgConfig.default_color;

            item.appendChild(cb);
            item.appendChild(label);
            item.appendChild(swatch);

            item.addEventListener('click', (e) => {
                if (e.target === cb) return; // checkbox handles itself
                _mgSelectBone(boneName);
            });

            body.appendChild(item);
        }

        catDiv.appendChild(body);
        container.appendChild(catDiv);

        // Toggle collapse
        header.addEventListener('click', () => {
            header.classList.toggle('collapsed');
            body.classList.toggle('hidden');
        });
    }
}

function _mgSelectBone(boneName) {
    _mgSelectedBone = boneName;
    // Highlight in tree
    document.querySelectorAll('.mg-bone-item').forEach(el => {
        el.classList.toggle('selected', el.dataset.bone === boneName);
    });
    // Show bone properties
    const propsSection = document.getElementById('mg-bone-props-section');
    if (propsSection) propsSection.style.display = '';
    const nameEl = document.getElementById('mg-bone-name');
    if (nameEl) nameEl.textContent = boneName;

    const part = _mgConfig.bone_parts[boneName];
    if (!part) return;

    const shapeSelect = document.getElementById('mg-bone-shape');
    if (shapeSelect) shapeSelect.value = part.shape || 'cylinder';
    const radiusSlider = document.getElementById('mg-bone-radius');
    const radiusVal = document.getElementById('mg-bone-radius-val');
    if (radiusSlider) radiusSlider.value = part.radius || 0.03;
    if (radiusVal) radiusVal.textContent = (part.radius || 0.03).toFixed(3);
    const colorInput = document.getElementById('mg-bone-color');
    if (colorInput) colorInput.value = part.color || _mgConfig.default_color;

    // Overlap slider — show only for double_oval
    const overlapRow = document.getElementById('mg-overlap-row');
    if (overlapRow) overlapRow.style.display = (part.shape === 'double_oval') ? '' : 'none';
    const overlapSlider = document.getElementById('mg-bone-overlap');
    const overlapVal = document.getElementById('mg-bone-overlap-val');
    if (overlapSlider) overlapSlider.value = part.overlap ?? 0.5;
    if (overlapVal) overlapVal.textContent = (part.overlap ?? 0.5).toFixed(2);

    // Shape-specific params — show/hide based on shape
    const tutuParams = document.getElementById('mg-tutu-params');
    if (tutuParams) tutuParams.style.display = (part.shape === 'tutu') ? '' : 'none';
    const spiralParams = document.getElementById('mg-spiral-tutu-params');
    if (spiralParams) spiralParams.style.display = (part.shape === 'spiral_tutu') ? '' : 'none';
    const spiralSkirtCb = document.getElementById('mg-spiral-skirt');
    if (spiralSkirtCb) spiralSkirtCb.checked = !!part.spiralSkirt;
    const helixParams = document.getElementById('mg-helix-ribbon-params');
    if (helixParams) helixParams.style.display = (part.shape === 'helix_ribbon') ? '' : 'none';
    const helixSkirtCb = document.getElementById('mg-helix-skirt');
    if (helixSkirtCb) helixSkirtCb.checked = !!part.spiralSkirt;
    const skirtParams = document.getElementById('mg-skirt-params');
    if (skirtParams) skirtParams.style.display = (part.shape === 'skirt') ? '' : 'none';

    const shapeSliders = [
        // Tutu
        ['mg-tutu-thickness', 'mg-tutu-thickness-val', 'tutuThickness', 0.01, 3],
        ['mg-tutu-droop', 'mg-tutu-droop-val', 'tutuDroop', 0.03, 3],
        ['mg-tutu-droop-start', 'mg-tutu-droop-start-val', 'tutuDroopStart', 0.7, 2],
        ['mg-tutu-offset', 'mg-tutu-offset-val', 'tutuOffset', 0, 3],
        // Spiral-Tutu
        ['mg-spiral-winds', 'mg-spiral-winds-val', 'spiralWinds', 3, 0],
        ['mg-spiral-start-r', 'mg-spiral-start-r-val', 'spiralStartR', 0.15, 3],
        ['mg-spiral-end-r', 'mg-spiral-end-r-val', 'spiralEndR', 0.35, 3],
        ['mg-spiral-pos-top', 'mg-spiral-pos-top-val', 'spiralPosTop', 0.05, 3],
        ['mg-spiral-pos-bottom', 'mg-spiral-pos-bottom-val', 'spiralPosBottom', -0.15, 3],
        ['mg-spiral-thickness', 'mg-spiral-thickness-val', 'tutuThickness', 0.008, 3],
        ['mg-spiral-droop', 'mg-spiral-droop-val', 'tutuDroop', 0.02, 3],
        // Helix ribbon
        ['mg-helix-winds', 'mg-helix-winds-val', 'spiralWinds', 3, 1],
        ['mg-helix-start-r', 'mg-helix-start-r-val', 'spiralStartR', 0.15, 3],
        ['mg-helix-end-r', 'mg-helix-end-r-val', 'spiralEndR', 0.35, 3],
        ['mg-helix-ribbon-w', 'mg-helix-ribbon-w-val', 'ribbonWidth', 0.04, 3],
        ['mg-helix-pos-top', 'mg-helix-pos-top-val', 'spiralPosTop', 0.05, 3],
        ['mg-helix-pos-bottom', 'mg-helix-pos-bottom-val', 'spiralPosBottom', -0.15, 3],
        ['mg-helix-thickness', 'mg-helix-thickness-val', 'tutuThickness', 0.005, 3],
        ['mg-helix-droop', 'mg-helix-droop-val', 'tutuDroop', 0.015, 3],
        // Skirt
        ['mg-skirt-radius-top', 'mg-skirt-radius-top-val', 'skirtRadiusTop', 0.08, 3],
        ['mg-skirt-radius-bottom', 'mg-skirt-radius-bottom-val', 'skirtRadiusBottom', 0.25, 3],
        ['mg-skirt-pos-top', 'mg-skirt-pos-top-val', 'skirtPosTop', 0.02, 3],
        ['mg-skirt-pos-bottom', 'mg-skirt-pos-bottom-val', 'skirtPosBottom', -0.15, 3],
        ['mg-skirt-thickness', 'mg-skirt-thickness-val', 'skirtThickness', 0.005, 3],
    ];
    for (const [slId, valId, prop, def, dec] of shapeSliders) {
        const sl = document.getElementById(slId);
        const sp = document.getElementById(valId);
        const v = part[prop] ?? def;
        if (sl) sl.value = v;
        if (sp) sp.textContent = dec === 0 ? String(Math.round(v)) : v.toFixed(dec);
    }

    // Head/Tail offset sliders
    for (const end of ['head', 'tail']) {
        const off = part[end + 'Offset'] || { x: 0, y: 0, z: 0 };
        for (const axis of ['x', 'y', 'z']) {
            const sl = document.getElementById(`mg-${end}-off-${axis}`);
            const sp = document.getElementById(`mg-${end}-off-${axis}-val`);
            if (sl) sl.value = off[axis] || 0;
            if (sp) sp.textContent = (off[axis] || 0).toFixed(3);
        }
    }

    // Shape rotation sliders
    const rot = part.shapeRotation || { x: 0, y: 0, z: 0 };
    for (const axis of ['x', 'y', 'z']) {
        const sl = document.getElementById(`mg-shape-rot-${axis}`);
        const sp = document.getElementById(`mg-shape-rot-${axis}-val`);
        if (sl) sl.value = rot[axis] || 0;
        if (sp) sp.textContent = rot[axis] || 0;
    }

    // Bidirectional sync: show 3D selection overlay
    if (_boneSelectOverlay) {
        _removeBoneOverlay(_boneSelectOverlay);
        _boneSelectOverlay = null;
    }
    _selectedBoneName = boneName;
    if (_mgCharacterId) {
        const inst = characters.get(_mgCharacterId);
        if (inst && inst.bodyMesh && inst.bodyMesh.userData.boneVertexRanges) {
            _boneSelectOverlay = _createBoneOverlay(inst.bodyMesh, boneName, _BONE_SELECT_MAT);
        }
    }
}

function _updateBoneTreeItem(boneName) {
    const item = document.querySelector(`.mg-bone-item[data-bone="${boneName}"]`);
    if (!item) return;
    const part = _mgConfig.bone_parts[boneName];
    if (!part) return;
    const swatch = item.querySelector('.mg-bone-swatch');
    if (swatch) swatch.style.backgroundColor = part.color;
}

let _mgRegenTimer = null;
let _mgRegenBusy = false;
function _mgAutoRegenerate() {
    if (!_mgCharacterId) return; // Only auto-regen if character exists
    if (_mgRegenBusy) {
        // Already generating — schedule one more after current finishes
        _mgRegenTimer = true;
        return;
    }
    _mgRegenBusy = true;
    requestAnimationFrame(() => {
        _mgGenerateCharacter();
        _mgRegenBusy = false;
        if (_mgRegenTimer) {
            _mgRegenTimer = false;
            _mgAutoRegenerate();
        }
    });
}

function _mgGeneratePreview() {
    if (!_mgConfig) {
        console.warn('Model Generator: missing config');
        return;
    }

    let result;
    if (_mgSkeletonType === 'rig' && _mgRigBonesData) {
        result = generateRigBoneMesh(_mgRigBonesData, _mgConfig, rigifySkeletonData, skinWeightData);
    } else {
        if (!rigifySkeletonData || !skinWeightData) {
            console.warn('Model Generator: missing skeleton data');
            return;
        }
        result = generateModelMesh(rigifySkeletonData, skinWeightData, _mgConfig);
    }

    if (!result) {
        console.warn('Model Generator: no visible bones');
        return;
    }

    return result;
}

function _mgGenerateCharacter() {
    const result = _mgGeneratePreview();
    if (!result) return;

    // Clear bone highlight cache and overlays (references become invalid)
    _clearBoneHighlightCache();

    // Remember position + presetKey of old character before removing
    let oldPos = null;
    let oldPresetKey = null;
    if (_mgCharacterId && characters.has(_mgCharacterId)) {
        const old = characters.get(_mgCharacterId);
        oldPos = old.group.position.clone();
        oldPresetKey = old.presetKey || null;
        deleteCharacter(_mgCharacterId);
        _mgCharacterId = null;
    }

    // Create CharacterInstance
    const id = generateCharacterId();
    const configCopy = JSON.parse(JSON.stringify(_mgConfig));
    configCopy.type = 'generated_model';
    configCopy.skeleton_type = _mgSkeletonType;
    const inst = new CharacterInstance(id, configCopy);
    inst.presetName = _mgConfig.name || 'Generiertes Modell';
    inst.presetKey = oldPresetKey;
    inst.bodyType = _mgSkeletonType === 'rig' ? 'Rig Bones' : 'DEF Skeleton';

    // Set the mesh directly
    inst.bodyMesh = result.mesh;
    if (result.skeleton) {
        inst.rigifySkeleton = result.skeleton;
        inst.isSkinned = true;
    }
    inst.group.add(result.mesh);

    // Restore position or offset
    if (oldPos) {
        inst.group.position.copy(oldPos);
    }

    characters.set(id, inst);
    scene.add(inst.group);
    _mgCharacterId = id;

    updateCharacterListUI();
    updateVertexCount();
    selectCharacter(id);

    const vc = result.mesh.geometry.attributes.position.count;
    console.log(`Model Generator: created ${_mgSkeletonType === 'rig' ? 'Mesh' : 'SkinnedMesh'} with ${vc} vertices as character "${inst.presetName}"`);
}

async function _mgSaveModelToServer() {
    // Sync config if needed
    if (!_mgConfig) {
        let inst = _selectedInst();
        if (!inst || !inst.generatedConfig) {
            for (const [, c] of characters) {
                if (c.generatedConfig) { inst = c; break; }
            }
        }
        if (inst && inst.generatedConfig) {
            _mgConfig = JSON.parse(JSON.stringify(inst.generatedConfig));
            _mgSkeletonType = inst.generatedConfig.skeleton_type || 'rig';
            _mgCharacterId = inst.id;
        }
    }
    if (!_mgConfig) {
        alert('Kein Modell vorhanden.');
        return;
    }

    const data = {
        ..._mgConfig,
        type: 'generated_model',
        name: _mgConfig.name || 'Generiertes Modell',
        body_type: _mgSkeletonType === 'rig' ? 'Rig Bones' : 'DEF Skeleton',
        skeleton_type: _mgSkeletonType
    };
    const inst = _mgCharacterId ? characters.get(_mgCharacterId) : null;
    const defaultName = ((inst && inst.presetKey) ? inst.presetKey : defaultPresetName || _mgConfig.name || 'Neues Modell') + '.json';
    const chosenName = await _saveJsonWithPicker(data, defaultName);
    if (!chosenName) return;                // user cancelled file dialog

    // Also save to server models directory so Theatre and other pages see it
    const saveName = chosenName.replace(/\.json$/i, '');
    try {
        await fetch('/api/character/model/save/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify({ name: saveName, data })
        });
        if (_mgCharacterId) {
            const ci = characters.get(_mgCharacterId);
            if (ci) {
                ci.generatedConfig = JSON.parse(JSON.stringify(data));
                ci.presetKey = saveName;
            }
        }
        console.log(`[MG] Model saved as "${saveName}" (file + server)`);
    } catch (e) { console.warn('[MG] Server save failed:', e); }
}

async function _mgSaveModel() {
    // Sync config from selected character if not yet linked
    if (!_mgConfig) {
        // Try selected character first, then any character with generatedConfig
        let inst = _selectedInst();
        if (!inst || !inst.generatedConfig) {
            for (const [, c] of characters) {
                if (c.generatedConfig) { inst = c; break; }
            }
        }
        if (inst && inst.generatedConfig) {
            _mgConfig = JSON.parse(JSON.stringify(inst.generatedConfig));
            _mgSkeletonType = inst.generatedConfig.skeleton_type || 'rig';
            _mgCharacterId = inst.id;
            console.log('[MG] Synced config from character:', inst.presetName);
        }
    }
    if (!_mgConfig) {
        alert('Kein Modell vorhanden. Bitte zuerst ein Modell erzeugen.');
        return;
    }

    // Format as importable character preset
    const data = {
        ..._mgConfig,
        type: 'generated_model',
        name: _mgConfig.name || 'Generiertes Modell',
        body_type: _mgSkeletonType === 'rig' ? 'Rig Bones' : 'DEF Skeleton',
        skeleton_type: _mgSkeletonType
    };
    const defaultName = (_mgConfig.name || 'Neues Modell').trim().replace(/[^a-zA-Z0-9_\-äöüÄÖÜß ]/g, '_') + '.json';
    await _saveJsonWithPicker(data, defaultName);
}

// =========================================================================
// Boot
// =========================================================================
init();
