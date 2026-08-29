/**
 * Photo To 3D — HumanBody mesh loading, DEF skeleton, skin color.
 */
import { state, API, MODEL_OFFSET_X } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Hautfarbe } from '../gemeinsam/hautfarbe.js';
import { Fotokoerpernetz } from './fotokoerpernetz.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import {
    base64ToFloat32, base64ToUint32, blenderToThreeCoords,
    alignBodyToSMPLX, BODY_MATERIALS,
} from './helpers.js';
import { buildRigifySkeleton as Rigifyskelett }
    from '../rigify_skeleton_builder.js';

// =========================================================================
// HumanBody skin color
// =========================================================================
function getSkinMat() {
    if (!state.bodyMesh || !state.bodyMesh.material) return null;
    return Array.isArray(state.bodyMesh.material) ? state.bodyMesh.material[0] : state.bodyMesh.material;
}

export function applySkinColor(bodyType) {
    const mat = getSkinMat();
    if (!mat) return;
    // Prefer detected skin color from photo analysis
    if (state.detectedSkinColor) {
        mat.color.set(state.detectedSkinColor);
        const picker = document.getElementById('skin-color-viewer');
        if (picker) picker.value = state.detectedSkinColor;
        return;
    }
    if (Hautfarbe.ausKoerperart(mat, bodyType, state.skinColors)) {
        const picker = document.getElementById('skin-color-viewer');
        if (picker) picker.value = '#' + mat.color.getHexString();
    }
}

// =========================================================================
// HumanBody mesh loading (shifted left)
// =========================================================================
export async function loadMesh(bodyType) {
    // Das Netz baut `Fotokoerpernetz` (fotokoerpernetz.js) — vorher standen hier
    // 119 Zeilen in einer Funktion.
    const netz = await new Fotokoerpernetz(bodyType).laden();
    if (netz) applySkinColor(bodyType || state.currentBodyType);
    return netz;
}

export function requestMeshUpdate() {
    state.meshUpdatePending = true;
    if (!state.meshUpdateTimer) {
        state.meshUpdateTimer = setTimeout(async () => {
            state.meshUpdateTimer = null;
            if (state.meshUpdatePending) {
                state.meshUpdatePending = false;
                await loadMesh(state.currentBodyType);
            }
        }, 80);
    }
}

// =========================================================================
// HumanBody DEF Skeleton
// =========================================================================
export async function loadRigifySkeleton(bodyType) {
    bodyType = bodyType || state.currentBodyType;
    try {
        const resp = await fetch(`${API}/rigify-skeleton/?body_type=${encodeURIComponent(bodyType)}`);
        if (resp.ok) state.rigifySkeletonData = await resp.json();
    } catch (e) { Protokoll.warnung('humanbody_mesh', 'DEF skeleton not available:', e); }
    try {
        const resp = await fetch(`${API}/skin-weights/?body_type=${encodeURIComponent(bodyType)}`);
        if (resp.ok) state.skinWeightData = await resp.json();
    } catch (e) { Protokoll.warnung('humanbody_mesh', 'Skin weights not available:', e); }
    if (state.rigifySkeletonData && state.skinWeightData) buildRigifySkeleton();
}

/**
 * Das DEF-Skelett aufbauen und die Ruhedrehungen dazu merken.
 *
 * BEFUND `doppelcode` (29.08.2026): Diese Funktion trug denselben Namen wie
 * `buildRigifySkeleton` in `rigify_skeleton_builder.js` und baute dieselben
 * 38 Zeilen noch einmal nach — nur ohne Argumente und mit `state` fest
 * verdrahtet. Zwei gleichnamige Funktionen mit verschiedener Signatur sind
 * die unangenehmste Sorte Doppelung: Wer `fn.buildRigifySkeleton` liest,
 * greift beim Suchen die falsche.
 *
 * EIN UNTERSCHIED WAR ECHT und ist geprueft, nicht weggewischt: Die alte
 * Fassung hing JEDEN elternlosen Knochen an die Wurzel, die gemeinsame nur
 * die mit Skelettdaten. Beides faellt zusammen, solange kein Gewichtsname
 * ohne Knochen ankommt — und das kann er nicht: `Skingewichte
 * ._nicht_def_entfernen` wirft solche Namen serverseitig weg. Gemessen am
 * 29.08.2026: In `humanBody_male/skin_weights_base.json` steht genau ein
 * solcher Name (`corrective_smooth_inv`, 3.192 Punkte, Gewichtssumme 2886) —
 * er verlaesst den Server nicht.
 */
export function buildRigifySkeleton() {
    const skelett = Rigifyskelett(state.rigifySkeletonData, state.skinWeightData);
    if (!skelett.rootBone) return;

    // Ruhedrehungen fuer die Mimik: die Ausdruecke kommen als Differenz dazu.
    const restQuats = {};
    for (const [name, bone] of Object.entries(skelett.boneByName)) {
        restQuats[name] = bone.quaternion.clone();
    }
    state.rigifySkeleton = { ...skelett, restQuats };
}

fn.loadMesh = loadMesh;
fn.requestMeshUpdate = requestMeshUpdate;
fn.loadRigifySkeleton = loadRigifySkeleton;
fn.buildRigifySkeleton = buildRigifySkeleton;
