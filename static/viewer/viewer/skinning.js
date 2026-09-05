/**
 * Viewer — GPU Skinning: 176-bone DEF skeleton + BVH retargeting.
 */
import * as THREE from 'three';
import { state, API } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { buildRigifySkeleton } from '../rigify_skeleton_builder.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Hautgewichte } from '../gemeinsam/hautgewichte.js';
import { Hautbindung } from '../gemeinsam/hautbindung.js';
import { Skelettnachfuehrung } from '../gemeinsam/skelettnachfuehrung.js';

export async function loadSkinWeights() {
    try {
        const resp = await fetch(`${API}/skin-weights/`);
        if (resp.ok) state.skinWeightData = await resp.json();
    } catch (e) {
        Protokoll.warnung('skinning', 'Skin weights not available:', e);
    }
}

export async function loadRigifySkeleton() {
    try {
        const resp = await fetch(`${API}/rigify-skeleton/`);
        if (resp.ok) {
            state.rigifySkeletonData = await resp.json();
            Protokoll.debug('Viewer', `DEF skeleton loaded: ${state.rigifySkeletonData.bone_count} bones`);
        }
    } catch (e) {
        Protokoll.warnung('skinning', 'DEF skeleton not available:', e);
    }
}

/**
 * Convert bodyMesh to SkinnedMesh using DEF skeleton.
 */
export function convertToRigifySkinnedMesh(rigifySkel, swData) {
    if (state.isSkinned || !state.bodyMesh || !state.bodyGeometry) return;

    state.bodyGeometry = state.bodyGeometry.clone();

    Hautgewichte.anGeometrie(state.bodyGeometry, swData, THREE.Float32BufferAttribute);

    state.rigifySkeleton = buildRigifySkeleton(state.rigifySkeletonData, swData);

    state.bodyMesh = Hautbindung.ersetzen(
        state.scene, state.bodyMesh, state.bodyGeometry,
        state.rigifySkeleton, THREE);
    state.isSkinned = true;
    // Die Knochenlagen sind meist schon da, bevor gebunden wird: Der Server
    // schickt sie zum ersten Netz, das Skinning wartet auf die Gewichte.
    if (state.skelettBewegte) skelettNachfuehren(state.skelettBewegte);
    Protokoll.debug('Viewer', 'SkinnedMesh created:', state.bodyMesh.isSkinnedMesh,
                'bones:', state.rigifySkeleton.skeleton.bones.length,
                'skinIndex:', !!state.bodyGeometry.attributes.skinIndex,
                'skinWeight:', !!state.bodyGeometry.attributes.skinWeight);
}

/**
 * Ensure body mesh is converted to SkinnedMesh (if skeleton data available).
 */
export function ensureSkinned() {
    if (state.isSkinned) return;
    if (!state.rigifySkeletonData || !state.skinWeightData || !state.bodyMesh) return;
    convertToRigifySkinnedMesh(null, state.skinWeightData);
}

/**
 * Die neuen Knochenlagen vom Server anwenden.
 *
 * Sie werden IMMER gemerkt, auch wenn noch nichts gebunden ist — sonst
 * verfaellt der Stand, den der Server zum ersten Netz mitschickt, und das
 * Skelett bliebe bis zum naechsten Reglerzug in der Ruhelage.
 *
 * @param {Object} bewegte {Knochenname: [x,y,z]} in Blender-Koordinaten
 */
export function skelettNachfuehren(bewegte) {
    state.skelettBewegte = bewegte;
    if (!state.skelettFuehrung && state.rigifySkeletonData) {
        state.skelettFuehrung = new Skelettnachfuehrung(state.rigifySkeletonData);
    }
    if (!state.skelettFuehrung || !state.isSkinned) return false;
    return state.skelettFuehrung.anwenden(
        state.bodyMesh, state.rigifySkeleton, bewegte);
}

// Register
fn.loadSkinWeights = loadSkinWeights;
fn.loadRigifySkeleton = loadRigifySkeleton;
// UEBER DIE REGISTRIERUNG UND NICHT ALS IMPORT (05.09.2026, Regression):
// Zuerst holte sich `websocket.js` diesen Namen mit `import { … } from
// './skinning.js'`. Die Viewer-Module tragen in ihren Import-Adressen KEINE
// Fassungskennung; nur die Einstiegsdatei bekommt `?t=`. Wer die Seite offen
// hatte, bekam danach eine frische Einstiegsdatei und ein Geschwistermodul
// aus dem Zwischenspeicher — und damit
//
//     SyntaxError: The requested module './skinning.js' does not provide an
//     export named 'skelettNachfuehren'
//
// Ein fehlender Export reisst den GANZEN Modulbaum ab: keine Szene, kein
// Modell, nur eine Zeile in der Konsole. Nachgestellt mit
// `ProjektTemp/altmodul.mjs` — genau ein altes Modul, und `window.__viewer`
// war weg.
//
// Ueber `fn` kann dasselbe nicht passieren: Fehlt der Name, ruft
// `fn.skelettNachfuehren?.(…)` ins Leere und die Seite laeuft weiter, das
// Skelett folgt eben bis zum naechsten Laden nicht. So macht es
// `result_character/websocket.js` mit `fn.reloadBodyMesh` schon lange.
fn.skelettNachfuehren = skelettNachfuehren;
