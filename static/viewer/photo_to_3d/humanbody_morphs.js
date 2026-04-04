/**
 * Photo To 3D — HumanBody morph UI: body type selector, meta sliders, morph panel.
 */
import { state, API } from './state.js';
import { fn } from './registry.js';

// =========================================================================
// HumanBody Morph UI
// =========================================================================
export async function loadMorphs() {
    try {
        const resp = await fetch(`${API}/morphs/`);
        state.morphsData = await resp.json();
    } catch (e) { console.error('Failed to load morphs:', e); return; }

    const data = state.morphsData;
    state.skinColors = data.skin_colors || {};

    const select = document.getElementById('body-type-select');
    data.body_types.forEach(bt => {
        const opt = document.createElement('option');
        opt.value = bt;
        opt.textContent = bt.replace('_', ' ');
        select.appendChild(opt);
    });
    select.value = state.currentBodyType;

    select.addEventListener('change', async () => {
        const oldGender = state.currentBodyType.startsWith('Male_') ? 'male' : 'female';
        state.currentBodyType = select.value;
        const newGender = state.currentBodyType.startsWith('Male_') ? 'male' : 'female';

        if (oldGender !== newGender) {
            try {
                const swResp = await fetch(`${API}/skin-weights/?body_type=${encodeURIComponent(state.currentBodyType)}`);
                state.skinWeightData = await swResp.json();
            } catch (e) { /* ignore */ }
        }

        await fn.loadMesh(state.currentBodyType);
        const mResp = await fetch(`${API}/morphs/?body_type=${encodeURIComponent(state.currentBodyType)}`);
        state.morphsData = await mResp.json();
        state.skinColors = state.morphsData.skin_colors || {};
        buildMorphPanel(state.morphsData);
    });

    ['age', 'mass', 'tone', 'height'].forEach(name => {
        const slider = document.getElementById(`meta-${name}`);
        const valSpan = document.getElementById(`meta-${name}-val`);
        if (!slider) return;
        const meta = data.meta_sliders?.[name];
        if (meta) {
            slider.min = meta.min; slider.max = meta.max;
            slider.value = meta.default; valSpan.textContent = meta.default;
        }
        slider.addEventListener('input', () => {
            valSpan.textContent = slider.value;
            const min = parseInt(slider.min), max = parseInt(slider.max);
            const neutral = (min + max) / 2, half = (max - min) / 2;
            state.metaValues[name] = half ? (parseInt(slider.value) - neutral) / half : 0;
            fn.requestMeshUpdate();
        });
    });

    const skinColorInput = document.getElementById('skin-color-viewer');
    if (skinColorInput) {
        skinColorInput.addEventListener('input', e => {
            const mat = state.bodyMesh?.material;
            const skinMat = mat ? (Array.isArray(mat) ? mat[0] : mat) : null;
            if (skinMat) skinMat.color.set(e.target.value);
        });
    }

    buildMorphPanel(data);

    const resetBtn = document.getElementById('reset-morphs');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            state.morphValues = {};
            document.querySelectorAll('#morphs-panel input[type="range"]').forEach(s => {
                s.value = 0;
                const valEl = s.parentElement.querySelector('.slider-val');
                if (valEl) valEl.textContent = '0';
            });
            fn.requestMeshUpdate();
        });
    }
}

export function buildMorphPanel(data) {
    const categories = {};
    data.morphs.forEach(m => {
        if (!categories[m.category]) categories[m.category] = [];
        categories[m.category].push(m);
    });

    const panel = document.getElementById('morphs-panel');
    panel.innerHTML = '';

    data.categories.sort().forEach(cat => {
        const morphs = categories[cat];
        if (!morphs || morphs.length === 0) return;
        const div = document.createElement('div');
        div.className = 'morph-category';
        const header = document.createElement('div');
        header.className = 'morph-category-header';
        header.textContent = `${cat} (${morphs.length})`;
        header.addEventListener('click', () => div.classList.toggle('open'));
        div.appendChild(header);
        const body = document.createElement('div');
        body.className = 'morph-category-body';
        morphs.forEach(m => {
            const row = document.createElement('div');
            row.className = 'slider-row';
            const label = document.createElement('label');
            label.textContent = m.name.split('_').slice(1).join(' ') || m.name;
            label.title = m.name;
            const slider = document.createElement('input');
            slider.type = 'range'; slider.min = -100; slider.max = 100;
            slider.value = Math.round((state.morphValues[m.name] || 0) * 100);
            slider.step = 1; slider.dataset.morph = m.name;
            const valSpan = document.createElement('span');
            valSpan.className = 'slider-val'; valSpan.textContent = slider.value;
            slider.addEventListener('input', () => {
                const v = parseInt(slider.value) / 100.0;
                valSpan.textContent = slider.value;
                state.morphValues[m.name] = v;
                fn.requestMeshUpdate();
            });
            row.appendChild(label); row.appendChild(slider); row.appendChild(valSpan);
            body.appendChild(row);
        });
        div.appendChild(body);
        panel.appendChild(div);
    });
}

fn.loadMorphs = loadMorphs;
fn.buildMorphPanel = buildMorphPanel;
