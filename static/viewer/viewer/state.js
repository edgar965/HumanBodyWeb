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
// Die Tabelle stand hier als sechste Kopie — jetzt an EINER Stelle
// (`gemeinsam/koerpermaterialien.js`, Befund `doppelcode` 17.08.2026).
export { BODY_MATERIALS } from '../gemeinsam/koerpermaterialien.js';

// Kleiderregionen: siehe `gemeinsam/kleiderregionen.js` (Umbau 28.08.2026,
// Befund `doppelcode`). `REGION_IDS` kommt jetzt mit — hier fehlte es.
export { REGION_DEFS, REGION_RADIUS, REGION_IDS }
    from '../gemeinsam/kleiderregionen.js';

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

    // SMPL
    smplGarmentMeshes: {},
    smplBodyMesh: null,
    smplBodyVisible: false,
    _smplCatalog: [],
    _smplSelectedId: '',
    _garmentCatalog: [],
};

export { acceleratedRaycast };
