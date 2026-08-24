/**
 * Result Character — Shared mutable state object.
 * All modules import state from here.
 *
 * Note: result_character is a closure-based module (initResultCharacter function),
 * so this state is populated at init time by the index module.
 */
import * as THREE from 'three';

// Die Tabelle stand hier als eine von vier Kopien, eine davon unter
// anderem Namen — jetzt an EINER Stelle (`gemeinsam/tonwerte.js`,
// Befunde `doppelcode` und `namensvarianten`, 17.08.2026).
import { tonwerte } from '../gemeinsam/tonwerte.js';
export const TONE_MAPPINGS = tonwerte(THREE);

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
