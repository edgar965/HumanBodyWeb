/**
 * Photo To 3D — Job management: backend status, save, screenshot, texture, tabs, job preload.
 */
import { state, API } from './state.js';
import { fn } from './registry.js';

// =========================================================================
// Status + Save
// =========================================================================
export async function loadBackendStatus() {
    const list = document.getElementById('backend-list');
    if (!list) return;

    try {
        const resp = await fetch(`${API}/analyze-photo/status/`);
        const data = await resp.json();
        state.backendStatus = data.backends || {};
    } catch (e) {
        console.warn('Failed to load backend status:', e);
        return;
    }

    list.innerHTML = '';
    const order = ['smplest_x', 'pymafx', 'hmr2', 'mediapipe'];

    for (const key of order) {
        const info = state.backendStatus[key];
        if (!info) continue;

        const item = document.createElement('div');
        item.className = 'backend-item';
        if (key === state.selectedBackend && info.available) item.classList.add('selected');
        if (!info.available) item.classList.add('disabled');
        item.dataset.backend = key;

        const radio = document.createElement('div');
        radio.className = 'backend-radio';

        const dot = document.createElement('div');
        dot.className = 'backend-status-dot ' + (info.available ? 'ok' : 'no');

        const infoDiv = document.createElement('div');
        infoDiv.className = 'backend-info';

        const labelDiv = document.createElement('div');
        labelDiv.className = 'backend-label';
        labelDiv.textContent = info.label;

        if (info.quality === 'best') {
            const badge = document.createElement('span');
            badge.className = 'backend-badge best';
            badge.textContent = 'Best';
            labelDiv.appendChild(badge);
        }

        const hwBadge = document.createElement('span');
        hwBadge.className = 'backend-badge ' + (info.gpu ? 'gpu' : 'cpu');
        hwBadge.textContent = info.gpu ? 'GPU' : 'CPU';
        labelDiv.appendChild(hwBadge);

        const descDiv = document.createElement('div');
        descDiv.className = 'backend-desc';
        descDiv.textContent = info.available ? info.desc : info.info;

        infoDiv.appendChild(labelDiv);
        infoDiv.appendChild(descDiv);

        item.appendChild(radio);
        item.appendChild(dot);
        item.appendChild(infoDiv);

        item.addEventListener('click', () => {
            if (!info.available) return;
            state.selectedBackend = key;
            list.querySelectorAll('.backend-item').forEach(el => el.classList.remove('selected'));
            item.classList.add('selected');
        });

        list.appendChild(item);
    }

    if (!state.backendStatus[state.selectedBackend]?.available) {
        for (const key of order) {
            if (state.backendStatus[key]?.available) {
                state.selectedBackend = key;
                const el = list.querySelector(`[data-backend="${key}"]`);
                if (el) el.classList.add('selected');
                break;
            }
        }
    }
}

export function initSaveButton() {
    const btn = document.getElementById('save-model-btn');
    if (!btn) return;
    btn.addEventListener('click', async () => {
        const name = prompt('Preset-Name:', 'PhotoTo3D_' + state.currentBodyType);
        if (!name) return;
        const saveData = {
            name, data: {
                name, body_type: state.currentBodyType,
                morphs: { ...state.morphValues }, meta: { ...state.metaValues },
                skin_color: document.getElementById('skin-color-viewer')?.value || '#d4a574',
            },
        };
        try {
            const resp = await fetch(`${API}/model/save/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(saveData) });
            const result = await resp.json();
            if (result.ok) { btn.innerHTML = '<i class="fas fa-check"></i> Gespeichert'; setTimeout(() => { btn.innerHTML = '<i class="fas fa-save"></i> Speichern'; }, 2000); }
        } catch (e) { console.error('Save failed:', e); }
    });
}

// =========================================================================
// Screenshot capture
// =========================================================================
export async function captureAndSaveScreenshot(jobId) {
    if (!jobId || !state.renderer) return;
    try {
        state.renderer.render(state.scene, state.camera);
        const dataUrl = state.renderer.domElement.toDataURL('image/jpeg', 0.85);
        await fetch(`${API}/photo-job/${jobId}/screenshot/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: dataUrl }),
        });
        console.log('[Photo->3D] Screenshot saved for job', jobId);
    } catch (e) {
        console.warn('Screenshot capture failed:', e);
    }
}

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
// Texture buttons
// =========================================================================
export function initTextureButtons() {
    document.querySelectorAll('.btn-texture[data-backend]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const backend = btn.dataset.backend;
            if (!state.currentJobId) return;

            document.querySelectorAll('.btn-texture').forEach(b => { b.disabled = true; });
            btn.classList.add('loading');
            showTextureProgress(true, `${backend}: Textur wird erstellt...`, 10);
            const t0 = performance.now();
            try {
                await fn.loadSmplxTexture(state.currentJobId, backend);
                const dur = ((performance.now() - t0) / 1000).toFixed(1);
                showTextureProgress(true, `${backend}: Fertig (${dur}s)`, 100);
                const info = document.getElementById('texture-info');
                if (info) {
                    info.style.display = 'block';
                    info.textContent = `${backend} Textur auf SMPL-X Mesh angewendet`;
                }
                setTimeout(() => captureAndSaveScreenshot(state.currentJobId), 500);
            } catch (e) {
                showTextureProgress(true, `${backend}: Fehler — ${e.message}`, 0);
            } finally {
                btn.classList.remove('loading');
                enableTextureButtons();
            }
        });
    });

    const wizBtn = document.getElementById('btn-start-wizard');
    if (wizBtn) {
        wizBtn.addEventListener('click', () => fn.startWizard());
    }
}

export function enableTextureButtons() {
    document.querySelectorAll('.btn-texture').forEach(btn => {
        btn.disabled = !state.currentJobId;
    });
}

export function showTextureProgress(visible, status, percent) {
    const el = document.getElementById('texture-progress');
    const fill = document.getElementById('texture-progress-fill');
    const statusEl = document.getElementById('texture-status');
    if (!el) return;
    el.style.display = visible ? 'block' : 'none';
    if (fill) fill.style.width = (percent || 0) + '%';
    if (statusEl) statusEl.textContent = status || '';
}

// =========================================================================
// Photo Tabs
// =========================================================================
export function initPhotoTabs() {
    const tabs = document.querySelectorAll('.photo-tab');
    const contents = document.querySelectorAll('.photo-tab-content');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
            if (tab.dataset.tab === 'textur' && state.currentJobId) {
                fn.renderAlignmentPreview();
            }
        });
    });
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

fn.loadBackendStatus = loadBackendStatus;
fn.initSaveButton = initSaveButton;
fn.initTextureButtons = initTextureButtons;
fn.enableTextureButtons = enableTextureButtons;
fn.showTextureProgress = showTextureProgress;
fn.initPhotoTabs = initPhotoTabs;
fn.loadJobResult = loadJobResult;
fn.captureAndSaveScreenshot = captureAndSaveScreenshot;
