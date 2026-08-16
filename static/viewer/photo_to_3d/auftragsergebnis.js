import { enableTextureButtons } from './job_management.js';
import { fn } from '../gemeinsam/registrierung.js';
import { API } from './state.js';
import { state } from './state.js';
/**
 * Ergebnis eines Fotoauftrags laden und anzeigen.
 *
 * Aus job_management.js herausgeloest (Umbau 16.08.2026).
 */


// =========================================================================
// Show full JSON data in detection panel
// =========================================================================
export function showJobJson(data) {
    const el = document.getElementById('detection-json');
    if (!el) return;
    const display = {};
    if (data.gender) display.gender = data.gender;
    if (data.backend) display.backend = data.backend;
    if (data.body_type) display.body_type = data.body_type;
    if (data.confidence) display.confidence = data.confidence;
    if (data.duration) display.duration = data.duration + 's';
    if (data.skin_color) display.skin_color = data.skin_color;
    if (data.measurements) display.measurements = data.measurements;
    if (data.meta_sliders) display.meta_sliders = data.meta_sliders;
    if (data.betas) display.betas = data.betas.map(b => +b.toFixed(3));
    if (data.expression) display.expression = data.expression.map(e => +e.toFixed(3));
    if (data.morphs) {
        const cats = {};
        for (const [k, v] of Object.entries(data.morphs)) {
            const cat = k.split('_')[0];
            if (!cats[cat]) cats[cat] = {};
            cats[cat][k] = v;
        }
        display.morphs = cats;
    }
    el.textContent = JSON.stringify(display, null, 2);
    el.style.display = 'block';
}

// =========================================================================
// Job preload (for loading saved analysis results)
// =========================================================================
export async function loadJobResult(jobId) {
    try {
        const resp = await fetch(`${API}/photo-job/${jobId}/`);
        const data = await resp.json();
        if (!data.ok) { console.error('Job load failed:', data.error); return; }

        state.currentJobId = jobId;
        state._previewDataCache = null;
        enableTextureButtons();

        if (data.photo_url) {
            const img = document.getElementById('photo-img');
            const placeholder = document.getElementById('upload-zone');
            if (img) { img.src = data.photo_url; img.style.display = 'block'; }
            if (placeholder) placeholder.style.display = 'none';
            const preview = document.getElementById('photo-preview');
            if (preview) preview.style.display = 'block';
            const actions = document.getElementById('photo-actions');
            if (actions) actions.style.display = 'block';
        }

        // === Step 1: Set ALL state ===
        if (data.skin_color) {
            state.detectedSkinColor = data.skin_color;
            const picker = document.getElementById('skin-color-viewer');
            if (picker) picker.value = data.skin_color;
        }
        if (data.betas) {
            for (let i = 0; i < Math.min(data.betas.length, 10); i++) {
                state.smplxBetas[i] = data.betas[i];
            }
        }
        state.smplxGender = data.gender || 'female';
        if (data.expression && data.expression.length > 0) {
            for (let i = 0; i < Math.min(data.expression.length, 10); i++) {
                state.smplxExpr[i] = data.expression[i];
            }
        }
        if (data.morphs) {
            for (const [morphName, val] of Object.entries(data.morphs)) {
                state.morphValues[morphName] = val;
            }
        }
        if (data.meta_sliders) {
            const defaultRanges = {
                height: { min: 150, max: 200 }, mass: { min: 45, max: 200 },
                tone: { min: 0, max: 100 }, age: { min: 18, max: 100 },
            };
            const metaDefs = state.morphsData?.meta_sliders || {};
            for (const [name, val] of Object.entries(data.meta_sliders)) {
                const def = metaDefs[name] || defaultRanges[name];
                if (def) {
                    const min = def.min, max = def.max;
                    const neutral = (min + max) / 2, half = (max - min) / 2;
                    state.metaValues[name] = half ? (val - neutral) / half : 0;
                }
            }
        }
        if (data.body_type) state.currentBodyType = data.body_type;

        // === Step 2: Update UI sliders ===
        const btSelect = document.getElementById('body-type-select');
        if (btSelect) btSelect.value = state.currentBodyType;
        const genderSel = document.getElementById('smplx-gender');
        if (genderSel) genderSel.value = state.smplxGender;
        if (data.meta_sliders) {
            for (const [name, val] of Object.entries(data.meta_sliders)) {
                const slider = document.getElementById(`meta-${name}`);
                const valSpan = document.getElementById(`meta-${name}-val`);
                if (slider) { slider.value = val; if (valSpan) valSpan.textContent = val; }
            }
        }
        document.querySelectorAll('[data-beta-idx]').forEach(sl => {
            const i = parseInt(sl.dataset.betaIdx);
            sl.value = Math.round(state.smplxBetas[i] * 100);
            const vs = sl.parentElement?.querySelector('.slider-val');
            if (vs) vs.textContent = state.smplxBetas[i].toFixed(1);
        });
        document.querySelectorAll('[data-expr-idx]').forEach(sl => {
            const i = parseInt(sl.dataset.exprIdx);
            sl.value = Math.round(state.smplxExpr[i] * 100);
            const vs = sl.parentElement?.querySelector('.slider-val');
            if (vs) vs.textContent = state.smplxExpr[i].toFixed(1);
        });

        // === Step 3: Load models ===
        console.log('[Photo->3D] Loading job result:', {
            bodyType: state.currentBodyType, smplxGender: state.smplxGender,
            morphCount: Object.keys(state.morphValues).length,
        });
        try {
            const mResp = await fetch(`${API}/morphs/?body_type=${encodeURIComponent(state.currentBodyType)}`);
            state.morphsData = await mResp.json();
            state.skinColors = state.morphsData.skin_colors || {};
            fn.buildMorphPanel(state.morphsData);
        } catch (e) { console.warn('Failed to refresh morphs:', e); }

        try {
            const swResp = await fetch(`${API}/skin-weights/?body_type=${encodeURIComponent(state.currentBodyType)}`);
            state.skinWeightData = await swResp.json();
            const dsResp = await fetch(`${API}/rigify-skeleton/?body_type=${encodeURIComponent(state.currentBodyType)}`);
            state.rigifySkeletonData = await dsResp.json();
            state.rigifySkeleton = null;
            fn.buildRigifySkeleton();
        } catch (e) { console.warn('Failed to reload skin weights:', e); }

        await fn.loadMesh(state.currentBodyType);
        fn.applyFacialExpression(state.smplxExpr);
        await fn.loadSmplxModel();
        if (state.detectedSkinColor && state.smplxSkinnedMesh) {
            state.smplxSkinnedMesh.material.color.set(state.detectedSkinColor);
        }

        const resultsDiv = document.getElementById('detection-results');
        const paramsDiv = document.getElementById('detection-params');
        if (resultsDiv) resultsDiv.style.display = 'block';
        if (paramsDiv) {
            paramsDiv.innerHTML = `<div style="padding:4px 0;font-size:0.85rem;">
                <b>Geschlecht:</b> ${data.gender === 'male' ? 'Männlich' : 'Weiblich'} &nbsp;|&nbsp;
                <b>Body Type:</b> ${state.currentBodyType} &nbsp;|&nbsp;
                <b>Backend:</b> ${data.backend || '?'}
            </div>`;
        }
        showJobJson(data);
    } catch (e) {
        console.error('Failed to load job:', e);
    }
}
