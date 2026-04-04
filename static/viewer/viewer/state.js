/**
 * Viewer — Shared mutable state object + constants.
 * All modules import state from here.
 */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { acceleratedRaycast, computeBoundsTree, disposeBoundsTree } from 'three-mesh-bvh';

// Register BVH helpers on BufferGeometry (but NOT global raycast override)
THREE.BufferGeometry.prototype.computeBoundsTree = computeBoundsTree;
THREE.BufferGeometry.prototype.disposeBoundsTree = disposeBoundsTree;

// =========================================================================
// Viewer config — overridable via window.VIEWER_CONFIG (set in template)
// =========================================================================
const CFG = window.VIEWER_CONFIG || {};
export const API = CFG.apiPrefix || '/api/character';
export const WS_PATH = CFG.wsPath || '/ws/character/';
export const DEFAULT_BODY = CFG.defaultBodyType || null;

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

// Region definitions: each region is a band of the garment's Y extent
export const REGION_DEFS = [
    { id: 'bottom', center: 0.10 },
    { id: 'lower',  center: 0.30 },
    { id: 'mid',    center: 0.50 },
    { id: 'upper',  center: 0.70 },
    { id: 'top',    center: 0.90 },
];
export const REGION_RADIUS = 0.20;

// =========================================================================
// Shared mutable state
// =========================================================================
export const state = {
    scene: null,
    camera: null,
    renderer: null,
    controls: null,
    keyLight: null,
    fillLight: null,
    backLight: null,
    ambient: null,

    bodyMesh: null,
    bodyGeometry: null,
    vertexCount: 0,
    ws: null,
    wsReady: false,
    clock: new THREE.Clock(),
    frameCount: 0,
    fpsAccum: 0,

    // Animation
    mixer: null,
    currentAction: null,
    skeletonHelper: null,
    currentAnimName: '',
    currentAnimFrames: 0,
    currentAnimDuration: 0,
    playing: false,
    skelWrapper: null,

    // Wardrobe
    loadedAssets: {},
    gltfLoader: new GLTFLoader(),
    bvhLoader: new BVHLoader(),

    // GPU Skinning — Rigify skeleton
    skinWeightData: null,
    rigifySkeletonData: null,
    rigifySkeleton: null,
    isSkinned: false,

    // Rig skeleton visualization
    rigVisible: false,

    // Cloth
    clothMeshes: {},
    clothParams: {},

    // Garments
    garmentMeshes: {},
    garmentState: {},
    garmentOrigPositions: {},
    garmentRegionWeights: {},
    selectedGarmentId: '',

    // Hair
    hairMesh: null,
    initialBodyTop: null,
    hairColorData: {},

    // Preset
    currentPresetName: '',

    // Skin colors
    skinColors: {},

    // 3D Interaction
    _raycaster: new THREE.Raycaster(),
    _mouseNDC: new THREE.Vector2(),
    _hoveredItem: null,
    _selectedItem: null,
    _mouseDownPos: null,
    _HOVER_EMISSIVE: new THREE.Color(0x222244),
    _SELECT_EMISSIVE: new THREE.Color(0x4444aa),
    _ZERO_EMISSIVE: new THREE.Color(0x000000),

    // Morph throttle
    morphTimer: null,
    pendingMorphs: {},
    morphCategories: {},

    // SMPL
    smplGarmentMeshes: {},
    smplBodyMesh: null,
    smplBodyVisible: false,
    _smplCatalog: [],
    _smplSelectedId: '',
    _garmentCatalog: [],
};

export { acceleratedRaycast };
