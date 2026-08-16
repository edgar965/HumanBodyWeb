import { SMPLX_BETA_LABELS, SMPLX_EXPR_LABELS } from './state.js';
import * as THREE from 'three';
import { fn } from '../gemeinsam/registrierung.js';
import { loadSmplxModel } from './smplx_model.js';
import { state } from './state.js';
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
    const panel = document.getElementById('smplx-panel');
    if (!panel) return;

    // Gender dropdown
    const genderRow = document.createElement('div');
    genderRow.style.cssText = 'margin-bottom:8px;';
    const genderSel = document.createElement('select');
    genderSel.className = 'viewer-select';
    genderSel.id = 'smplx-gender';
    ['female', 'male', 'neutral'].forEach(g => {
        const opt = document.createElement('option');
        opt.value = g;
        opt.textContent = g.charAt(0).toUpperCase() + g.slice(1);
        genderSel.appendChild(opt);
    });
    genderSel.value = state.smplxGender;
    genderSel.addEventListener('change', () => {
        state.smplxGender = genderSel.value;
        requestSmplxUpdate();
    });
    genderRow.appendChild(genderSel);
    panel.appendChild(genderRow);

    // Shape betas
    const shapeHeader = document.createElement('div');
    shapeHeader.className = 'morph-category-header';
    shapeHeader.textContent = 'Shape (Body)';
    shapeHeader.style.cssText = 'cursor:pointer;margin-top:4px;';
    const shapeBody = document.createElement('div');
    shapeBody.style.display = 'block';
    shapeHeader.addEventListener('click', () => {
        shapeBody.style.display = shapeBody.style.display === 'none' ? 'block' : 'none';
    });
    panel.appendChild(shapeHeader);

    for (let i = 0; i < 10; i++) {
        const row = document.createElement('div');
        row.className = 'slider-row';

        const label = document.createElement('label');
        label.textContent = SMPLX_BETA_LABELS[i];
        label.title = `Beta ${i}`;

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = -300; slider.max = 300;
        slider.value = 0; slider.step = 1;
        slider.dataset.betaIdx = i;

        const valSpan = document.createElement('span');
        valSpan.className = 'slider-val';
        valSpan.textContent = '0.0';

        slider.addEventListener('input', () => {
            const v = parseInt(slider.value) / 100.0;
            valSpan.textContent = v.toFixed(1);
            state.smplxBetas[i] = v;
            requestSmplxUpdate();
        });

        row.appendChild(label);
        row.appendChild(slider);
        row.appendChild(valSpan);
        shapeBody.appendChild(row);
    }
    panel.appendChild(shapeBody);

    // Expression params
    const exprHeader = document.createElement('div');
    exprHeader.className = 'morph-category-header';
    exprHeader.textContent = 'Expression (Face)';
    exprHeader.style.cssText = 'cursor:pointer;margin-top:8px;';
    const exprBody = document.createElement('div');
    exprBody.style.display = 'none';
    exprHeader.addEventListener('click', () => {
        exprBody.style.display = exprBody.style.display === 'none' ? 'block' : 'none';
    });
    panel.appendChild(exprHeader);

    for (let i = 0; i < 10; i++) {
        const row = document.createElement('div');
        row.className = 'slider-row';

        const label = document.createElement('label');
        label.textContent = SMPLX_EXPR_LABELS[i];

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = -300; slider.max = 300;
        slider.value = 0; slider.step = 1;
        slider.dataset.exprIdx = i;

        const valSpan = document.createElement('span');
        valSpan.className = 'slider-val';
        valSpan.textContent = '0.0';

        slider.addEventListener('input', () => {
            const v = parseInt(slider.value) / 100.0;
            valSpan.textContent = v.toFixed(1);
            state.smplxExpr[i] = v;
            requestSmplxUpdate();
        });

        row.appendChild(label);
        row.appendChild(slider);
        row.appendChild(valSpan);
        exprBody.appendChild(row);
    }
    panel.appendChild(exprBody);

    // Reset button
    const resetBtn = document.getElementById('reset-smplx');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            state.smplxBetas.fill(0);
            state.smplxExpr.fill(0);
            panel.querySelectorAll('input[type="range"]').forEach(s => {
                s.value = 0;
                const vEl = s.parentElement.querySelector('.slider-val');
                if (vEl) vEl.textContent = '0.0';
            });
            requestSmplxUpdate();
        });
    }
}
