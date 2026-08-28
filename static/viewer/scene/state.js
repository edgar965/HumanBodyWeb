/**
 * Scene Editor -- Central shared state.
 * All other scene/ modules import from here.
 */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { detectBVHFormat, fetchRetargetedClipFromUrl, fetchRetargetedClipFromText } from '../retarget_hybrid.js';
import { buildRigifySkeleton } from '../rigify_skeleton_builder.js';
import { Knochengruppen } from '../modellbau/knochengruppen.js';
import { computeBoneWorldTransforms } from '../modellbau/knochenmatrizen.js';
import { generateModelMesh } from '../modellbau/modellnetz.js';
import { getDefaultModelConfig, getDefaultRigConfig } from '../modellbau/modellvorgaben.js';
import { generateRigBoneMesh } from '../modellbau/rignetz.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

// Re-export everything that other modules may need
export { THREE, OrbitControls, TransformControls, BVHLoader, GLTFLoader };
export { detectBVHFormat, fetchRetargetedClipFromUrl, fetchRetargetedClipFromText };
export { buildRigifySkeleton };
export {
    Knochengruppen, getDefaultModelConfig, computeBoneWorldTransforms, generateModelMesh, getDefaultRigConfig, generateRigBoneMesh,
};

export const gltfLoader = new GLTFLoader();

// =========================================================================
// Server-side logging
// =========================================================================
export function serverLog(action, detail, level) {
    const msg = detail ? `${action} — ${detail}` : action;
    Protokoll.debug('Scene', `${msg}`);
    fetch('/api/log/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ page: 'scene', action, detail: detail || '', level: level || 'info' }),
    // stumm gewollt: Diese Zeile IST der Protokollweg — ein Fehler dabei darf
    // die Aktion nicht aufhalten und sich nicht selbst melden wollen.
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

// Die Tabelle stand hier als eine von vier Kopien, eine davon unter
// anderem Namen — jetzt an EINER Stelle (`gemeinsam/tonwerte.js`,
// Befunde `doppelcode` und `namensvarianten`, 17.08.2026).
import { tonwerte } from '../gemeinsam/tonwerte.js';
export const TONE_MAPPINGS = tonwerte(THREE);

// =========================================================================
// Body materials
// =========================================================================
// Die Tabelle stand hier als sechste Kopie — jetzt an EINER Stelle
// (`gemeinsam/koerpermaterialien.js`, Befund `doppelcode` 17.08.2026).
export { BODY_MATERIALS } from '../gemeinsam/koerpermaterialien.js';

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

// Kleiderregionen: die Tabelle stand hier UND in `viewer/state.js`
// (Umbau 28.08.2026, Befund `doppelcode`). `REGION_IDS` gab es nur hier —
// die beiden waren schon dabei auseinanderzulaufen.
export { REGION_DEFS, REGION_RADIUS, REGION_IDS }
    from '../gemeinsam/kleiderregionen.js';

// Drei Stellen rufen `if (fn.serverLog) fn.serverLog(…)` — die Abfrage war
// bisher immer falsch, weil die Szenenseite ihren Logger nie angemeldet hat
// (Befund 16.08.2026). Die Aufrufe liefen also ins Leere.
fn.serverLog = serverLog;
