/**
 * Result Character — Mesh loading, skeleton conversion, skin color.
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import {
    base64ToFloat32, base64ToUint32, blenderToThreeCoords,
    sharedState, BODY_MATERIALS,
    loadRigifySkeleton, loadSkinWeights,
    computeSkinAttributes, applySkinColorToMaterials,
} from '../character_core.js?v=1';
import { buildRigifySkeleton } from '../rigify_skeleton_builder.js?v=2';
import { Koerpernetz } from '../gemeinsam/koerpernetz.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

const ss = sharedState;

export async function loadMesh(bodyType) {
    try {
        const data = await Serverabruf.json('/api/character/mesh/?body_type=' + encodeURIComponent(bodyType));
        if (data.error) { console.error('[result_character] mesh error:', data.error); return false; }

        // Puffer, Normalen, Materialgruppen: siehe `Koerpernetz`. Diese dreissig
        // Zeilen standen fuenfmal im Projekt (Befund `doppelcode`, 17.08.2026).
        state.bodyMesh = Koerpernetz.netz(data, THREE);
        const geo = state.bodyMesh.geometry;

        state.bodyGeometry = geo;
        state.scene.add(state.bodyMesh);

        fn.applySceneSkinSettings(state.bodyMesh);
        return true;
    } catch (e) {
        console.error('[result_character] Failed to load mesh:', e);
        return false;
    }
}

export function convertToRigifySkinnedMesh() {
    if (state.isSkinned || !state.bodyMesh || !state.bodyGeometry) return;
    state.bodyGeometry = state.bodyGeometry.clone();
    const { skinIndices, skinWeights } = computeSkinAttributes(state.bodyGeometry, ss.skinWeightData);
    state.bodyGeometry.setAttribute('skinIndex', new THREE.Float32BufferAttribute(skinIndices, 4));
    state.bodyGeometry.setAttribute('skinWeight', new THREE.Float32BufferAttribute(skinWeights, 4));
    state.rigifySkeleton = buildRigifySkeleton(ss.rigifySkeletonData, ss.skinWeightData);
    const mat = state.bodyMesh.material;
    const pos = state.bodyMesh.position.clone();
    state.scene.remove(state.bodyMesh);
    state.bodyMesh = new THREE.SkinnedMesh(state.bodyGeometry, mat);
    state.bodyMesh.position.copy(pos);
    state.bodyMesh.add(state.rigifySkeleton.rootBone);
    state.bodyMesh.bind(state.rigifySkeleton.skeleton);
    state.scene.add(state.bodyMesh);
    state.isSkinned = true;
}

export function applySkinColor(bodyType) {
    if (!state.bodyMesh) return;
    const mats = Array.isArray(state.bodyMesh.material) ? state.bodyMesh.material : [state.bodyMesh.material];
    applySkinColorToMaterials(mats, bodyType, ss.skinColors);
}

export async function reloadBodyMesh(newType) {
    if (newType === state.currentBodyType) return;
    state.currentBodyType = newType;

    if (state.mixer) { state.mixer.stopAllAction(); state.mixer = null; state.currentAction = null; }

    if (state.bodyMesh) {
        state.scene.remove(state.bodyMesh);
        if (state.bodyMesh.geometry) state.bodyMesh.geometry.dispose();
        const mats = Array.isArray(state.bodyMesh.material) ? state.bodyMesh.material : [state.bodyMesh.material];
        mats.forEach(m => m.dispose());
        state.bodyMesh = null;
    }
    state.bodyGeometry = null;
    state.rigifySkeleton = null;
    state.isSkinned = false;
    if (state.skeletonHelper) { state.scene.remove(state.skeletonHelper); state.skeletonHelper = null; }

    fn.removeAllCloth();
    fn.removeAllGarments();
    fn.removeHair();

    try {
        await Promise.all([
            loadMesh(newType),
            loadSkinWeights(newType),
        ]);

        if (state.bodyMesh && ss.rigifySkeletonData && ss.skinWeightData) {
            convertToRigifySkinnedMesh();
        }

        applySkinColor(newType);
        fn.wsSend({ type: 'body_type', value: newType });

        if (state.isSkinned) {
            await fn.loadBVH();
        }
    } catch (e) {
        console.error('[result_character] Body type switch failed:', e);
    }
}

fn.loadMesh = loadMesh;
fn.convertToRigifySkinnedMesh = convertToRigifySkinnedMesh;
fn.applySkinColor = applySkinColor;
fn.reloadBodyMesh = reloadBodyMesh;
