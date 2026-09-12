/**
 * Result Character — Mesh loading, skeleton conversion, skin color.
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Skelettanzeige } from '../gemeinsam/skelettanzeige.js';
import {
    base64ToFloat32, base64ToUint32, blenderToThreeCoords,
    sharedState, BODY_MATERIALS,
    loadRigifySkeleton, loadSkinWeights,
    computeSkinAttributes, applySkinColorToMaterials,
} from '../character_core.js';
import { buildRigifySkeleton } from '../rigify_skeleton_builder.js';
import { Koerpernetz } from '../gemeinsam/koerpernetz.js';
import { Koerperdetails } from '../gemeinsam/koerperdetails.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Netzentsorgung } from '../gemeinsam/netzentsorgung.js';
import { Hautbindung } from '../gemeinsam/hautbindung.js';
import { Skelettnachfuehrung } from '../gemeinsam/skelettnachfuehrung.js';

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
        if (state.details) Koerperdetails.anwenden(state.bodyMesh, state.details);
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
    // Rig-Vorgabe AN (12.09.2026): Der Helfer entstand nur beim Kippen des
    // Knopfs — steht der Schalter schon auf an, gehoert er hier dazu.
    if (state.rigVisible && !state.skeletonHelper) {
        state.skeletonHelper = Skelettanzeige.bauen(state.scene, state.rigifySkeleton.rootBone);
    }
    // NEU MIT `visible` (28.08.2026): Diese Fassung hat die Sichtbarkeit
    // als einzige nicht mitgenommen — ein ausgeblendeter Koerper kam beim
    // Zuschalten des Skeletts zurueck, ohne dass der Schalter umsprang.
    state.bodyMesh = Hautbindung.ersetzen(
        state.scene, state.bodyMesh, state.bodyGeometry,
        state.rigifySkeleton, THREE);
    state.isSkinned = true;
    // Der Server schickt die Knochenlagen zum ersten Netz, gebunden wird
    // erst danach. Ohne diese Zeile bliebe der zuletzt gemeldete Stand
    // liegen, bis jemand einen Regler anfasst.
    if (state.skelettBewegte) skelettNachfuehren(state.skelettBewegte);
}

/**
 * Die neuen Knochenlagen vom Server anwenden — siehe `Skelettnachfuehrung`.
 *
 * @param {Object} bewegte {Knochenname: [x,y,z]} in Blender-Koordinaten
 */
export function skelettNachfuehren(bewegte) {
    state.skelettBewegte = bewegte;
    if (!state.skelettFuehrung && ss.rigifySkeletonData) {
        state.skelettFuehrung = new Skelettnachfuehrung(ss.rigifySkeletonData);
    }
    if (!state.skelettFuehrung || !state.isSkinned) return false;
    return state.skelettFuehrung.anwenden(
        state.bodyMesh, state.rigifySkeleton, bewegte);
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
        Netzentsorgung.entfernen(state.scene, state.bodyMesh);
        state.bodyMesh = null;
    }
    state.bodyGeometry = null;
    state.rigifySkeleton = null;
    state.isSkinned = false;
    if (state.skeletonHelper) { state.scene.remove(state.skeletonHelper); state.skeletonHelper = null; }

    fn.removeAllCloth();
    fn.removeAllGarments();
    fn.removeHair();
    // GarmentCode-Stücke hängen am alten Skelett (`GarmentcodeStuecke`).
    fn.removeAllGarmentcode?.();

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
fn.reloadBodyMesh = reloadBodyMesh;

// Ueber die Registrierung erreichbar, damit `websocket.js` ihn nicht
// importieren muss — siehe `viewer/skinning.js`, Regression vom 05.09.2026.
fn.skelettNachfuehren = skelettNachfuehren;
