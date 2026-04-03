/**
 * Scene Editor -- Central shared state.
 * All other scene/ modules import from here.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { detectBVHFormat, fetchRetargetedClipFromUrl, fetchRetargetedClipFromText } from '../retarget_hybrid.js?v=32';
import { buildRigifySkeleton } from '../rigify_skeleton_builder.js?v=2';
import {
    classifyBones, getDefaultModelConfig, computeBoneWorldTransforms,
    generateModelMesh, classifyRigBones, getDefaultRigConfig,
    generateRigBoneMesh, BODY_BONES, FINGER_BONES,
} from '../model_generator.js';

// Re-export everything that other modules may need
export { THREE, OrbitControls, TransformControls, BVHLoader, GLTFLoader };
export { detectBVHFormat, fetchRetargetedClipFromUrl, fetchRetargetedClipFromText };
export { buildRigifySkeleton };
export {
    classifyBones, getDefaultModelConfig, computeBoneWorldTransforms,
    generateModelMesh, classifyRigBones, getDefaultRigConfig,
    generateRigBoneMesh, BODY_BONES, FINGER_BONES,
};

export const gltfLoader = new GLTFLoader();

// =========================================================================
// Server-side logging
// =========================================================================
export function serverLog(action, detail, level) {
    const msg = detail ? `${action} — ${detail}` : action;
    console.log(`[Scene] ${msg}`);
    fetch('/api/log/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ page: 'scene', action, detail: detail || '', level: level || 'info' }),
    }).catch(() => {});
}

// =========================================================================
// Light Presets
// =========================================================================
export const LIGHT_PRESETS = {
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

export const TONE_MAPPINGS = {
    ACESFilmic: THREE.ACESFilmicToneMapping,
    Linear:     THREE.LinearToneMapping,
    Reinhard:   THREE.ReinhardToneMapping,
    Cineon:     THREE.CineonToneMapping,
    None:       THREE.NoToneMapping
};

// =========================================================================
// Body materials
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
// Global mutable state
// =========================================================================
export const state = {
    scene: null,
    camera: null,
    renderer: null,
    controls: null,
    canvas: null,
    clock: new THREE.Clock(),
    frameCount: 0,
    fpsAccum: 0,

    // Lights
    keyLight: null,
    fillLight: null,
    backLight: null,
    ambientLight: null,

    // Legacy single mesh
    bodyMesh: null,
    bodyGeometry: null,

    // Animation
    mixer: null,
    currentAction: null,
    skeletonHelper: null,
    playing: false,
    bvhLoader: new BVHLoader(),
    rigifySkeletonData: null,
    skinWeightData: null,
    rigifySkeleton: null,
    isSkinned: false,
    skelWrapper: null,
    _animatedCharId: null,
    rigVisible: false,
    modelVisible: true,
    clothesVisible: true,

    // Skin colors + hair colors
    skinColors: {},
    hairColorData: {},

    // Auto-save debounce
    saveTimer: null,

    // Properties panel state
    morphDefs: null,
    currentPropsCharId: null,
    reloadTimer: null,

    // Asset panel cached data
    _garmentCatalog: [],
    _selectedGarmentId: null,
    _hairStylesData: [],
    _clothRegionsData: null,
    currentAnimName: '',
    currentAnimDuration: 0,
    currentAnimUrl: '',
    currentAnimBvhText: '',
    currentAnimGroundFixed: false,
    _sceneDeltaNorm: undefined,

    // Scene Editor State
    characters: new Map(),
    selectedCharacterId: null,
    transformControls: null,
    currentTransformMode: 'translate',
    transformHelper: null,
    transformDragging: false,
    currentSceneName: '',
    defaultPresetName: 'femaleWithClothes',
    _defaultAnimUrl: '',
    _sceneDirty: false,

    // Raycasting
    raycaster: new THREE.Raycaster(),
    mouse: new THREE.Vector2(),
    mouseDownPos: null,
    CLICK_THRESHOLD: 3,

    // Sub-mesh selection
    _hoveredSubMesh: null,
    _selectedSubMesh: null,
    _HOVER_EMISSIVE: new THREE.Color(0x08081a),
    _SELECT_EMISSIVE: new THREE.Color(0x12123a),
    _ZERO_EMISSIVE: new THREE.Color(0x000000),
    _hoverPending: false,
    _lastMouseEvent: null,

    // Bone selection
    _hoveredBoneName: null,
    _selectedBoneName: null,
    _boneHighlightCache: new Map(),
    _boneHoverOverlay: null,
    _boneSelectOverlay: null,
    _BONE_HOVER_MAT: new THREE.MeshBasicMaterial({
        color: 0xaaccff, transparent: true, opacity: 0.55,
        depthTest: true, depthWrite: false, side: THREE.DoubleSide,
    }),
    _BONE_SELECT_MAT: new THREE.MeshBasicMaterial({
        color: 0x4466ff, transparent: true, opacity: 0.35,
        depthTest: true, depthWrite: false, side: THREE.DoubleSide,
    }),

    // Sync flag
    _syncingSliders: false,
    _refitting: false,

    // Model generator
    _mgConfig: null,
    _mgSelectedBone: null,
    _mgInitialized: false,
    _mgSkeletonType: 'rig',
    _mgRigBonesData: null,
    _mgCharacterId: null,

    // Kleider
    _selectedKleiderId: null,
    _kleiderHullVertices: null,

    // MH
    _selectedMHId: null,

    // Pose
    _currentPose: 'a_pose',

    // Add-char dialog
    _addCharSelectedPreset: null,
    _selectedFileToLoad: null,
};

// =========================================================================
// Session key constant
// =========================================================================
export const SESSION_KEY = 'humanbody_scene_session';

// =========================================================================
// Garment region definitions (shared by garments, kleider, properties)
// =========================================================================
export const REGION_DEFS = [
    { id: 'bottom', center: 0.10 },
    { id: 'lower',  center: 0.30 },
    { id: 'mid',    center: 0.50 },
    { id: 'upper',  center: 0.70 },
    { id: 'top',    center: 0.90 },
];
export const REGION_RADIUS = 0.20;
export const REGION_IDS = ['top', 'upper', 'mid', 'lower', 'bottom'];
