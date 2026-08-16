/**
 * Photo To 3D — Job management: backend status, save, screenshot, texture, tabs, job preload.
 */
import { state, API } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { loadJobResult } from './auftragsergebnis.js';

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


fn.loadBackendStatus = loadBackendStatus;
fn.initSaveButton = initSaveButton;
fn.initTextureButtons = initTextureButtons;
fn.enableTextureButtons = enableTextureButtons;
fn.showTextureProgress = showTextureProgress;
fn.initPhotoTabs = initPhotoTabs;
fn.loadJobResult = loadJobResult;
fn.captureAndSaveScreenshot = captureAndSaveScreenshot;
