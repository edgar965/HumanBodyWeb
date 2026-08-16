import { SMPLX_BETA_LABELS, SMPLX_EXPR_LABELS } from './state.js';
import * as THREE from 'three';
import { fn } from '../gemeinsam/registrierung.js';
import { loadSmplxModel } from './smplx_model.js';
import { state } from './state.js';
import { Smplxregler } from './smplxregler.js';
/**
 * Bedienfeld der SMPL-X-Regler.
 *
 * Aus smplx_model.js herausgeloest (Umbau 16.08.2026).
 */


export function requestSmplxUpdate() {
    if (state.smplxUpdateTimer) clearTimeout(state.smplxUpdateTimer);
    state.smplxUpdateTimer = setTimeout(() => {
        state.smplxUpdateTimer = null;
        loadSmplxModel();
        fn.applyFacialExpression(state.smplxExpr);
    }, 120);
}

export function showSmplxRig() {
    if (!state.smplxSkinnedMesh) return;
    if (state.smplxSkelHelper) {
        state.smplxGroup.remove(state.smplxSkelHelper);
        state.smplxSkelHelper.dispose();
    }
    state.smplxSkelHelper = new THREE.SkeletonHelper(state.smplxSkinnedMesh);
    state.smplxSkelHelper.material.depthTest = false;
    state.smplxSkelHelper.material.depthWrite = false;
    state.smplxSkelHelper.material.color.set(0xff8844);
    state.smplxSkelHelper.renderOrder = 999;
    state.smplxGroup.add(state.smplxSkelHelper);
}

// =========================================================================
// SMPL-X slider panel
// =========================================================================
export function buildSmplxPanel() {
    // Die Regler stecken in `Smplxregler` — vorher standen hier 126 Zeilen mit
    // zwei gleichlautenden Reglergruppen.
    return new Smplxregler({ SMPLX_BETA_LABELS, SMPLX_EXPR_LABELS },
                           requestSmplxUpdate).bauen();
}
