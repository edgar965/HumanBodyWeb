/**
 * Result Character — Shared mutable state object.
 * All modules import state from here.
 *
 * Note: result_character is a closure-based module (initResultCharacter function),
 * so this state is populated at init time by the index module.
 */
import * as THREE from 'three';

export const TONE_MAPPINGS = {
    ACESFilmic: THREE.ACESFilmicToneMapping,
    Linear:     THREE.LinearToneMapping,
    Reinhard:   THREE.ReinhardToneMapping,
    Cineon:     THREE.CineonToneMapping,
    None:       THREE.NoToneMapping,
};

/**
 * Mutable state for the result character viewer.
 * Populated by initResultCharacter() in index.js.
 */
export const state = {
    renderer: null,
    scene: null,
    camera: null,
    controls: null,

    bodyMesh: null,
    bodyGeometry: null,
    rigifySkeleton: null,
    isSkinned: false,
    mixer: null,
    currentAction: null,
    currentBodyType: 'Female_Caucasian',
    currentPresetName: '',
    bvhClipDuration: 0,
    skeletonHelper: null,
    rigVisible: false,
    clothesVisible: true,
    enableFootCorrection: false,
    deltaNormMode: undefined,

    // Cloth
    clothMeshes: {},

    // Hair
    hairMesh: null,

    // Garment meshes
    garmentMeshes: {},

    // Current morph/meta state
    currentMorphs: {},
    currentMeta: {},

    // External refs (set at init time)
    video: null,
    canvas: null,
    loadingEl: null,
    panel: null,
    modelSelectId: null,
    jobId: null,
    bvhUrl: null,
    bvhFaceUrl: null,

    // WebSocket
    ws: null,
    wsReady: false,
    morphTimer: null,
    pendingMorphs: {},

    // Data
    morphData: null,
    hairData: null,
    presetData: null,
    defaultPresetName: 'femaleWithClothes',
};
