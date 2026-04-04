/**
 * Photo To 3D — Photo upload and analyze functionality.
 */
import { state, API } from './state.js';
import { fn } from './registry.js';
import { enableTextureButtons, captureAndSaveScreenshot, showJobJson } from './job_management.js';

// =========================================================================
// Photo Upload
// =========================================================================
export function initPhotoUpload() {
    const zone = document.getElementById('upload-zone');
    const input = document.getElementById('photo-input');
    const preview = document.getElementById('photo-preview');
    const img = document.getElementById('photo-img');
    const removeBtn = document.getElementById('photo-remove');
    const actions = document.getElementById('photo-actions');
    const analyzeBtn = document.getElementById('btn-analyze');

    zone.addEventListener('click', () => input.click());
    input.addEventListener('change', () => {
        if (input.files.length > 0) showPhoto(input.files[0]);
    });
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
    zone.addEventListener('drop', e => {
        e.preventDefault(); zone.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) showPhoto(file);
    });
    removeBtn.addEventListener('click', () => {
        preview.style.display = 'none'; actions.style.display = 'none';
        zone.style.display = ''; input.value = '';
        document.getElementById('detection-results').style.display = 'none';
        state.detectedSkinColor = null;
    });
    analyzeBtn.addEventListener('click', () => analyzePhoto());

    function showPhoto(file) {
        const reader = new FileReader();
        reader.onload = e => {
            img.src = e.target.result;
            preview.style.display = 'block'; actions.style.display = 'block';
            zone.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
}

export async function analyzePhoto() {
    const input = document.getElementById('photo-input');
    const btn = document.getElementById('btn-analyze');
    const resultsDiv = document.getElementById('detection-results');
    const paramsDiv = document.getElementById('detection-params');

    let file = input.files[0];
    if (!file) {
        const imgSrc = document.getElementById('photo-img')?.src;
        if (imgSrc && (imgSrc.startsWith('data:') || imgSrc.includes('/media/'))) {
            const resp = await fetch(imgSrc);
            const blob = await resp.blob();
            file = new File([blob], 'photo.jpg', { type: blob.type });
        }
    }
    if (!file) return;

    btn.classList.add('loading');
    btn.disabled = true;

    try {
        const form = new FormData();
        form.append('photo', file);
        form.append('backend', state.selectedBackend);
        const resp = await fetch(`${API}/analyze-photo/`, { method: 'POST', body: form });
        const data = await resp.json();

        if (data.ok) {
            paramsDiv.innerHTML = '';
            const isMock = data.mock === true;
            const usedBackend = data.backend || state.selectedBackend;
            const backendLabel = state.backendStatus[usedBackend]?.label || usedBackend;
            const modelLabel = isMock ? 'Mock-Daten' : backendLabel;
            const badgeClass = isMock ? 'mock' : 'real';
            const headerEl = resultsDiv.querySelector('h4');
            if (headerEl) headerEl.innerHTML = `Erkannte Parameter <span class="detection-model-badge ${badgeClass}">${modelLabel}</span>`;

            const EXPR_DE = ['Kiefer offen', 'Lächeln', 'Brauen hoch', 'Brauen runter', 'Lippe hoch', 'Mundwinkel', 'Wangen', 'Zusammenkneifen', 'Nase', 'Augen weit'];

            const genderLabel = data.gender === 'male' ? 'Männlich' : 'Weiblich';
            const genderNote = data.estimated_gender ? ' (auto)' : '';
            const params = [
                ['Geschlecht', genderLabel + genderNote],
                ['Body Type', data.body_type.replace('_', ' ')],
            ];
            if (!isMock) params.push(['Confidence', (data.confidence * 100).toFixed(0) + '%']);
            if (data.skin_color) {
                params.push(['Hautfarbe', `<span style="display:inline-block;width:16px;height:16px;border-radius:3px;background:${data.skin_color};vertical-align:middle;border:1px solid rgba(255,255,255,0.2);margin-right:4px;"></span>${data.skin_color}`]);
            }
            if (data.measurements) {
                const mLabels = { height_cm: 'Körpergröße', shoulder_cm: 'Schulterbreite', hip_cm: 'Hüftbreite', torso_cm: 'Torsolänge', leg_cm: 'Beinlänge', arm_cm: 'Armlänge' };
                for (const [k, v] of Object.entries(data.measurements)) params.push([mLabels[k] || k, v + ' cm']);
            }
            if (data.meta_sliders) {
                const labels = { height: 'Größe (cm)', mass: 'Gewicht (kg)', tone: 'Muskeltonus', age: 'Alter' };
                for (const [k, v] of Object.entries(data.meta_sliders)) params.push([labels[k] || k, v]);
            }
            if (data.betas) {
                params.push(['Shape-Parameter', `${Math.min(data.betas.length, 10)} erkannt`]);
            }
            if (data.expression && data.expression.length > 0) {
                params.push(['Expression-Parameter', `${Math.min(data.expression.length, 10)} erkannt`]);
                const topExpr = data.expression
                    .map((v, i) => ({ label: EXPR_DE[i] || `Expr ${i}`, val: v, i }))
                    .filter(e => Math.abs(e.val) > 0.3)
                    .sort((a, b) => Math.abs(b.val) - Math.abs(a.val))
                    .slice(0, 3);
                if (topExpr.length > 0) {
                    const exprStr = topExpr.map(e => `${e.label} ${e.val >= 0 ? '+' : ''}${e.val.toFixed(1)}`).join(', ');
                    params.push(['Ausdruck', exprStr]);
                }
            }
            if (data.morphs && Object.keys(data.morphs).length > 0) {
                for (const [k, v] of Object.entries(data.morphs)) {
                    params.push([k.split('_').slice(1).join(' ') || k, (v >= 0 ? '+' : '') + (v * 100).toFixed(0) + '%']);
                }
            }
            params.forEach(([name, val]) => {
                const row = document.createElement('div');
                row.className = 'detection-param';
                row.innerHTML = `<span class="param-name">${name}</span><span class="param-val">${val}</span>`;
                paramsDiv.appendChild(row);
            });

            // --- Gender Override Dropdown ---
            const genderOverrideRow = document.createElement('div');
            genderOverrideRow.style.cssText = 'margin-top:8px;display:flex;align-items:center;gap:8px;';
            const genderOverrideLabel = document.createElement('span');
            genderOverrideLabel.style.cssText = 'font-size:0.82rem;color:var(--text);';
            genderOverrideLabel.textContent = 'Geschlecht:';
            const genderOverrideSel = document.createElement('select');
            genderOverrideSel.className = 'viewer-select';
            genderOverrideSel.style.cssText = 'margin-bottom:0;flex:1;';
            const autoLabel = `Automatisch (${genderLabel})`;
            [{ val: 'auto', label: autoLabel }, { val: 'male', label: 'Männlich' }, { val: 'female', label: 'Weiblich' }].forEach(opt => {
                const o = document.createElement('option');
                o.value = opt.val; o.textContent = opt.label;
                genderOverrideSel.appendChild(o);
            });
            genderOverrideSel.value = 'auto';
            genderOverrideSel.addEventListener('change', () => {
                const chosen = genderOverrideSel.value === 'auto' ? data.gender : genderOverrideSel.value;
                const prefix = chosen === 'male' ? 'Male' : 'Female';
                const ethnicity = state.currentBodyType.split('_')[1] || 'Caucasian';
                state.currentBodyType = `${prefix}_${ethnicity}`;
                state.smplxGender = chosen;
                const btSelect = document.getElementById('body-type-select');
                if (btSelect) { btSelect.value = state.currentBodyType; btSelect.dispatchEvent(new Event('change')); }
                const gSel = document.getElementById('smplx-gender');
                if (gSel) gSel.value = state.smplxGender;
                fn.loadSmplxModel();
            });
            genderOverrideRow.appendChild(genderOverrideLabel);
            genderOverrideRow.appendChild(genderOverrideSel);
            paramsDiv.appendChild(genderOverrideRow);

            if (isMock) {
                const info = document.createElement('div');
                info.style.cssText = 'margin-top:8px;padding:8px;background:rgba(243,156,18,0.1);border:1px solid var(--warning);border-radius:6px;font-size:0.78rem;color:var(--text-muted);';
                info.innerHTML = '<i class="fas fa-info-circle" style="color:var(--warning);margin-right:4px;"></i> SMPL-X Modell oder MediaPipe Pose nicht verfügbar. Werte sind zufällige Testdaten.';
                paramsDiv.appendChild(info);
            }
            resultsDiv.style.display = 'block';

            // === Step 1: Set ALL state values ===
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
            if (data.body_type) {
                state.currentBodyType = data.body_type;
            }

            // === Step 2: Update ALL slider UIs ===
            const btSelect = document.getElementById('body-type-select');
            if (btSelect) btSelect.value = state.currentBodyType;

            const genderSel = document.getElementById('smplx-gender');
            if (genderSel) genderSel.value = state.smplxGender;

            const smplxPanel = document.getElementById('smplx-panel');
            if (smplxPanel) {
                smplxPanel.querySelectorAll('input[data-beta-idx]').forEach(s => {
                    const idx = parseInt(s.dataset.betaIdx);
                    if (idx < state.smplxBetas.length) {
                        s.value = Math.round(state.smplxBetas[idx] * 100);
                        const vEl = s.parentElement.querySelector('.slider-val');
                        if (vEl) vEl.textContent = state.smplxBetas[idx].toFixed(1);
                    }
                });
                smplxPanel.querySelectorAll('input[data-expr-idx]').forEach(s => {
                    const idx = parseInt(s.dataset.exprIdx);
                    if (idx < state.smplxExpr.length) {
                        s.value = Math.round(state.smplxExpr[idx] * 100);
                        const vEl = s.parentElement.querySelector('.slider-val');
                        if (vEl) vEl.textContent = state.smplxExpr[idx].toFixed(1);
                    }
                });
            }

            if (data.meta_sliders) {
                for (const [name, val] of Object.entries(data.meta_sliders)) {
                    const slider = document.getElementById(`meta-${name}`);
                    const valSpan = document.getElementById(`meta-${name}-val`);
                    if (slider) { slider.value = val; if (valSpan) valSpan.textContent = val; }
                }
            }

            if (data.morphs) {
                for (const [morphName, val] of Object.entries(data.morphs)) {
                    const slider = document.querySelector(`input[data-morph="${morphName}"]`);
                    if (slider) {
                        slider.value = Math.round(val * 100);
                        const vEl = slider.parentElement.querySelector('.slider-val');
                        if (vEl) vEl.textContent = Math.round(val * 100);
                    }
                }
            }

            // === Step 3: Trigger model loads ===
            console.log('[Photo->3D] Loading models:', {
                bodyType: state.currentBodyType, smplxGender: state.smplxGender,
                betas: state.smplxBetas.slice(0, 5), meta: {...state.metaValues},
                skinColor: state.detectedSkinColor,
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
                console.log('[Photo->3D] Reloaded skin weights + skeleton for', state.currentBodyType);
            } catch (e) { console.warn('Failed to reload skin weights:', e); }

            console.log('[Photo->3D] loadMesh meta:', {...state.metaValues}, 'morphs:', {...state.morphValues});
            await fn.loadMesh(state.currentBodyType);

            fn.applyFacialExpression(state.smplxExpr);

            await fn.loadSmplxModel();

            if (state.detectedSkinColor && state.smplxSkinnedMesh) {
                state.smplxSkinnedMesh.material.color.set(state.detectedSkinColor);
            }

            if (data.job_id) {
                state.currentJobId = data.job_id;
                state._previewDataCache = null;
                enableTextureButtons();
            }

            if (data.job_id) {
                setTimeout(() => captureAndSaveScreenshot(data.job_id), 800);
            }
            showJobJson(data);
        } else {
            paramsDiv.innerHTML = `<div style="color:var(--warning);padding:8px 0;">${data.error || 'Analyse fehlgeschlagen'}</div>`;
            resultsDiv.style.display = 'block';
        }
    } catch (e) {
        console.error('Analyze failed:', e);
        paramsDiv.innerHTML = `<div style="color:var(--danger);padding:8px 0;">Fehler: ${e.message}</div>`;
        resultsDiv.style.display = 'block';
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
}

fn.initPhotoUpload = initPhotoUpload;
fn.analyzePhoto = analyzePhoto;
