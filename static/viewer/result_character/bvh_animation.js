/**
 * Result Character — BVH loading, retarget, and camera positioning.
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { fetchRetargetedClipForJob, fetchMergedClipForJob } from '../retarget_hybrid.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Die gemessene Koerperhoehe der Figur — Grundlage der Umzielung.
 *
 * 1,68 m ist der Rueckfall, wenn noch kein Netz da ist oder es leer ist. Der
 * Wert geht als Massstab in `fetchRetargetedClipForJob`: Ist er falsch,
 * stimmen die Schrittlaengen nicht, und die Figur rutscht oder stakst — kein
 * Fehler, den man einer Meldung ansieht.
 */
function _koerperhoehe() {
    if (!state.bodyMesh) return 1.68;
    const kasten = new THREE.Box3().setFromObject(state.bodyMesh);
    return kasten.isEmpty() ? 1.68 : kasten.max.y - kasten.min.y;
}

/**
 * Einen umgezielten Clip abspielen.
 *
 * BEFUND `doppelcode` (30.08.2026): `applyBvhRetarget` und
 * `applyHybridRetarget` waren derselbe Ablauf mit einer anderen Abrufstelle —
 * alten Mischer stoppen, Hoehe messen, Clip holen, neuen Mischer bauen, EINMAL
 * abspielen. Die Doppelung war schon sichtbar: Die Hybrid-Fassung protokolliert
 * nichts, die andere an vier Stellen.
 *
 * `LoopOnce` mit `clampWhenFinished`: Der Clip laeuft einmal und bleibt im
 * letzten Bild stehen. Ohne `clampWhenFinished` springt die Figur am Ende in
 * die Ruhelage zurueck — das sieht aus wie ein abgebrochener Import.
 *
 * @param {Function} holen (jobId, skelett, optionen) -> Promise<AnimationClip>
 * @param {string} woher Name fuer das Protokoll
 */
async function _abspielen(holen, woher) {
    if (state.mixer) {
        state.mixer.stopAllAction();
        state.mixer = null;
        state.currentAction = null;
    }
    const hoehe = _koerperhoehe();
    Protokoll.debug('result_character', woher, 'bodyHeight=', hoehe);
    const clip = await holen(state.jobId, state.rigifySkeleton, {
        bodyHeight: hoehe,
        footCorrection: state.enableFootCorrection,
        deltaNorm: state.deltaNormMode,
    });
    Protokoll.debug('result_character', woher, 'clip:', clip.duration, 'sec,',
                    clip.tracks.length, 'tracks');

    state.mixer = new THREE.AnimationMixer(state.bodyMesh);
    state.currentAction = state.mixer.clipAction(clip);
    state.currentAction.setLoop(THREE.LoopOnce);
    state.currentAction.clampWhenFinished = true;
    state.currentAction.play();
    state.bvhClipDuration = clip.duration;
}

export async function applyBvhRetarget() {
    Protokoll.debug('result_character', 'applyBvhRetarget called, jobId=', state.jobId, 'rigifySkeleton=',
        !!state.rigifySkeleton, 'bodyMesh=', !!state.bodyMesh);
    await _abspielen(fetchRetargetedClipForJob, 'bvh');
}

/**
 * Position camera in front of the character based on actual retargeted bone positions.
 */
export function positionCameraAfterRetarget() {
    if (!state.rigifySkeleton || !state.mixer || !state.bodyMesh) return;

    state.mixer.setTime(0);
    state.bodyMesh.updateWorldMatrix(true, true);
    state.rigifySkeleton.rootBone.updateWorldMatrix(true, true);

    const thighL = state.rigifySkeleton.boneByName['DEF-thigh.L'];
    const thighR = state.rigifySkeleton.boneByName['DEF-thigh.R'];
    if (!thighL || !thighR) return;

    const posL = new THREE.Vector3();
    const posR = new THREE.Vector3();
    thighL.getWorldPosition(posL);
    thighR.getWorldPosition(posR);

    const right = new THREE.Vector3().subVectors(posR, posL);
    right.y = 0;
    if (right.lengthSq() < 0.0001) return;
    right.normalize();

    const up = new THREE.Vector3(0, 1, 0);
    const forward = new THREE.Vector3().crossVectors(up, right).normalize();

    const spine = state.rigifySkeleton.boneByName['DEF-spine.003']
               || state.rigifySkeleton.boneByName['DEF-spine.001']
               || state.rigifySkeleton.boneByName['DEF-spine'];
    const center = new THREE.Vector3();
    if (spine) {
        spine.getWorldPosition(center);
    } else {
        center.addVectors(posL, posR).multiplyScalar(0.5);
    }

    const dist = 3.5;
    state.camera.position.set(
        center.x + forward.x * dist,
        center.y + 0.1,
        center.z + forward.z * dist
    );
    state.controls.target.copy(center);
    state.controls.update();
}

export async function loadBVH() {
    try {
        if (state.bvhFaceUrl) {
            await applyHybridRetarget();
        } else {
            await applyBvhRetarget();
        }
        positionCameraAfterRetarget();
    } catch (err) {
        console.error('[result_character] BVH retarget error:', err);
        if (state.loadingEl) {
            state.loadingEl.style.display = '';
            state.loadingEl.innerHTML = '<span class="fehlertext"><i class="fas fa-exclamation-triangle"></i> Retarget: ' + (err.message || err) + '</span>';
        }
    }
}

async function applyHybridRetarget() {
    await _abspielen(fetchMergedClipForJob, 'hybrid');
}

fn.loadBVH = loadBVH;
