/**
 * Result Character — BVH loading, retarget, and camera positioning.
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';
import { fetchRetargetedClipForJob, fetchMergedClipForJob } from '../retarget_hybrid.js?v=32';

export async function applyBvhRetarget() {
    console.log('[result_character] applyBvhRetarget called, jobId=', state.jobId, 'rigifySkeleton=', !!state.rigifySkeleton, 'bodyMesh=', !!state.bodyMesh);
    if (state.mixer) { state.mixer.stopAllAction(); state.mixer = null; state.currentAction = null; }

    let bodyH = 1.68;
    if (state.bodyMesh) {
        const bb = new THREE.Box3().setFromObject(state.bodyMesh);
        if (!bb.isEmpty()) bodyH = bb.max.y - bb.min.y;
    }
    console.log('[result_character] bodyHeight=', bodyH);

    const clip = await fetchRetargetedClipForJob(state.jobId, state.rigifySkeleton, {
        bodyHeight: bodyH,
        footCorrection: state.enableFootCorrection,
        deltaNorm: state.deltaNormMode,
    });

    console.log('[result_character] clip:', clip.duration, 'sec,', clip.tracks.length, 'tracks');

    state.mixer = new THREE.AnimationMixer(state.bodyMesh);
    state.currentAction = state.mixer.clipAction(clip);
    state.currentAction.setLoop(THREE.LoopOnce);
    state.currentAction.clampWhenFinished = true;
    state.currentAction.play();
    state.bvhClipDuration = clip.duration;
    console.log('[result_character] Animation playing, bvhClipDuration=', state.bvhClipDuration);
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
            state.loadingEl.innerHTML = '<span style="color:#e74c3c"><i class="fas fa-exclamation-triangle"></i> Retarget: ' + (err.message || err) + '</span>';
        }
    }
}

async function applyHybridRetarget() {
    if (state.mixer) { state.mixer.stopAllAction(); state.mixer = null; state.currentAction = null; }

    let bodyH = 1.68;
    if (state.bodyMesh) {
        const bb = new THREE.Box3().setFromObject(state.bodyMesh);
        if (!bb.isEmpty()) bodyH = bb.max.y - bb.min.y;
    }

    const clip = await fetchMergedClipForJob(state.jobId, state.rigifySkeleton, {
        bodyHeight: bodyH,
        footCorrection: state.enableFootCorrection,
        deltaNorm: state.deltaNormMode,
    });

    state.mixer = new THREE.AnimationMixer(state.bodyMesh);
    state.currentAction = state.mixer.clipAction(clip);
    state.currentAction.setLoop(THREE.LoopOnce);
    state.currentAction.clampWhenFinished = true;
    state.currentAction.play();
    state.bvhClipDuration = clip.duration;
}

fn.loadBVH = loadBVH;
fn.positionCameraAfterRetarget = positionCameraAfterRetarget;
