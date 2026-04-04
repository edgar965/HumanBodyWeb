/**
 * Photo To 3D — Toggle buttons: model, rig, SMPL-X, SMPL-X rig.
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';

export function initModelToggle() {
    const btn = document.getElementById('model-toggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
        if (state.bodyMesh) state.bodyMesh.visible = !state.bodyMesh.visible;
        btn.classList.toggle('active', state.bodyMesh && state.bodyMesh.visible);
    });
}

export function initRigToggle() {
    const btn = document.getElementById('rig-toggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
        state.rigVisible = !state.rigVisible;
        if (state.rigVisible && !state.skeletonHelper && state.rigifySkeleton) {
            state.skeletonHelper = new THREE.SkeletonHelper(state.rigifySkeleton.rootBone);
            state.skeletonHelper.material.depthTest = false;
            state.skeletonHelper.material.depthWrite = false;
            state.skeletonHelper.material.color.set(0x00ffaa);
            state.skeletonHelper.renderOrder = 999;
            state.scene.add(state.skeletonHelper);
        }
        if (state.skeletonHelper) state.skeletonHelper.visible = state.rigVisible;
        btn.classList.toggle('active', state.rigVisible);
    });
}

export function initSmplxToggle() {
    const btn = document.getElementById('smplx-toggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
        if (state.smplxGroup) state.smplxGroup.visible = !state.smplxGroup.visible;
        btn.classList.toggle('active', state.smplxGroup && state.smplxGroup.visible);
    });
}

export function initSmplxRigToggle() {
    const btn = document.getElementById('smplx-rig-toggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
        state.smplxRigVisible = !state.smplxRigVisible;
        if (state.smplxRigVisible) {
            fn.showSmplxRig();
        } else if (state.smplxSkelHelper) {
            state.smplxGroup?.remove(state.smplxSkelHelper);
            state.smplxSkelHelper.dispose();
            state.smplxSkelHelper = null;
        }
        btn.classList.toggle('active', state.smplxRigVisible);
    });
}

fn.initModelToggle = initModelToggle;
fn.initRigToggle = initRigToggle;
fn.initSmplxToggle = initSmplxToggle;
fn.initSmplxRigToggle = initSmplxRigToggle;
