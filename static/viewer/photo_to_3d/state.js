/**
 * Photo To 3D — Shared mutable state object.
 * All modules import state from here.
 */
import * as THREE from 'three';

export const API = '/api/character';

export const state = {
    scene: null,
    camera: null,
    renderer: null,
    controls: null,
    clock: new THREE.Clock(),
    frameCount: 0,
    fpsAccum: 0,

    // --- HumanBody model (left) ---
    bodyMesh: null,
    bodyGeometry: null,
    skeletonHelper: null,
    rigVisible: false,
    rigifySkeletonData: null,
    rigifySkeleton: null,
    skinWeightData: null,

    // --- SMPL-X model (right) ---
    smplxGroup: null,
    smplxSkinnedMesh: null,
    smplxSkelHelper: null,
    smplxRigVisible: false,
    smplxBetas: new Array(10).fill(0),
    smplxExpr: new Array(10).fill(0),
    smplxGender: 'female',
    smplxUpdateTimer: null,
    currentJobId: null,

    // --- Backend selection ---
    selectedBackend: 'smplest_x',
    backendStatus: {},

    // --- Morph state (HumanBody) ---
    currentBodyType: 'Female_Caucasian',
    morphValues: {},
    metaValues: {},
    skinColors: {},
    morphsData: null,
    meshUpdateTimer: null,
    meshUpdatePending: false,
    detectedSkinColor: null,

    // --- Alignment wizard ---
    _previewDataCache: null,
};

export const MODEL_OFFSET_X = -0.7;
export const SMPLX_OFFSET_X = 0.7;

export const SMPLX_BETA_LABELS = [
    'Stature', 'Weight', 'Proportions', 'Shoulders', 'Waist',
    'Hips', 'Torso', 'Chest', 'Arms', 'Legs',
];

export const SMPLX_EXPR_LABELS = [
    'Jaw Open', 'Smile', 'Brow Up', 'Brow Down', 'Lip Up',
    'Lip Corner', 'Cheek Puff', 'Squint', 'Nose Wrinkle', 'Eye Wide',
];
