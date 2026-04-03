/**
 * Scene Editor -- Properties panel: transform, body type, presets, morphs, equipped list.
 */
import { THREE, serverLog } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';
import { escapeHtml, _selectedInst } from './utils.js';
import { markDirty } from './undo.js';
import { _sameSubMesh, getSelectableSubMeshes } from './interaction.js';

export function initTabs() {
    document.querySelectorAll('.panel-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            switchTab(tab.dataset.tab);
            if (tab.dataset.tab === 'modell') fn.initModelGenerator();
        });
    });
    const resetBtn = document.getElementById('prop-reset-morphs');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (!state.currentPropsCharId) return;
            const inst = state.characters.get(state.currentPropsCharId);
            if (!inst) return;
            inst.morphs = {};
            populateMorphSliders(inst);
            reloadCharacterMesh(inst);
        });
    }
    const refitBtn = document.getElementById('prop-refit-btn');
    if (refitBtn) refitBtn.addEventListener('click', () => fn._refitAllForCurrentChar());
}

export function switchTab(tabName) {
    document.querySelectorAll('.panel-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tabName));
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.toggle('active', p.id === `tab-${tabName}`));
}

export async function fetchMorphDefs() {
    if (state.morphDefs && state.morphDefs.morphs && state.morphDefs.morphs.length > 0) return state.morphDefs;
    const resp = await fetch('/api/character/morphs/');
    state.morphDefs = await resp.json();
    return state.morphDefs;
}

export async function populateProperties(charId) {
    const inst = state.characters.get(charId);
    if (!inst) return;
    state.currentPropsCharId = charId;
    document.getElementById('prop-empty').style.display = 'none';
    document.getElementById('prop-content').style.display = '';
    document.getElementById('assets-empty').style.display = 'none';
    document.getElementById('assets-content').style.display = '';
    try { await fetchMorphDefs(); } catch (e) { console.error('Failed to fetch morph defs:', e); return; }
    populateTransform(inst);
    updateEquippedList(inst);
    populateBodyType(inst);
    populatePresets(inst);
    populateMetaSliders(inst);
    populateMorphSliders(inst);
    fn.syncHairSelect(inst);
    _updatePropContext();
    const activeTab = document.querySelector('.panel-tab.active');
    if (!activeTab || activeTab.dataset.tab !== 'modell') switchTab('eigenschaften');
}

export function clearProperties() {
    fn.clearSubMeshSelection();
    state.currentPropsCharId = null;
    document.getElementById('prop-empty').style.display = '';
    document.getElementById('prop-content').style.display = 'none';
    document.getElementById('assets-empty').style.display = '';
    document.getElementById('assets-content').style.display = 'none';
}

function populateTransform(inst) {
    const grid = document.getElementById('prop-transform');
    grid.innerHTML = '';
    const rows = [
        { label: 'Pos', prop: 'position', step: 0.01 },
        { label: 'Rot', prop: 'rotation', step: 1, isDeg: true },
        { label: 'Scale', prop: 'scale', step: 0.01 },
    ];
    const axes = ['x', 'y', 'z'];
    for (const row of rows) {
        const lbl = document.createElement('label'); lbl.textContent = row.label; grid.appendChild(lbl);
        for (const axis of axes) {
            const input = document.createElement('input');
            input.type = 'number'; input.step = row.step; input.dataset.prop = row.prop; input.dataset.axis = axis; input.className = 'prop-transform-input';
            let val = row.isDeg ? THREE.MathUtils.radToDeg(inst.group.rotation[axis]) : inst.group[row.prop][axis];
            input.value = parseFloat(val.toFixed(3));
            input.addEventListener('input', () => {
                const num = parseFloat(input.value); if (isNaN(num)) return;
                if (row.isDeg) inst.group.rotation[axis] = THREE.MathUtils.degToRad(num);
                else inst.group[row.prop][axis] = num;
                fn.updateCharacterListUI();
            });
            grid.appendChild(input);
        }
    }
}

export function syncTransformInputs() {
    const inst = state.characters.get(state.currentPropsCharId);
    if (!inst) return;
    document.querySelectorAll('.prop-transform-input').forEach(input => {
        const prop = input.dataset.prop, axis = input.dataset.axis;
        if (!prop || !axis || document.activeElement === input) return;
        let val = prop === 'rotation' ? THREE.MathUtils.radToDeg(inst.group.rotation[axis]) : inst.group[prop][axis];
        input.value = parseFloat(val.toFixed(3));
    });
}

function populateBodyType(inst) {
    const select = document.getElementById('prop-body-type');
    select.innerHTML = '';
    if (state.morphDefs && state.morphDefs.body_types) {
        for (const bt of state.morphDefs.body_types) {
            const opt = document.createElement('option'); opt.value = bt; opt.textContent = bt.replace(/_/g, ' '); select.appendChild(opt);
        }
    }
    select.value = inst.bodyType;
    const newSelect = select.cloneNode(true);
    select.parentNode.replaceChild(newSelect, select);
    newSelect.addEventListener('change', () => { inst.bodyType = newSelect.value; reloadCharacterMesh(inst); });
}

async function populatePresets(inst) {
    const sel = document.getElementById('prop-preset');
    if (!sel || sel._loaded) return;
    try {
        const resp = await fetch('/api/character/charmorph-presets/');
        const data = await resp.json();
        sel.innerHTML = '<option value="">-- Kein Preset --</option>';
        for (const p of (data.presets || [])) { const opt = document.createElement('option'); opt.value = JSON.stringify(p); opt.textContent = p.label; sel.appendChild(opt); }
        sel._loaded = true;
        sel.addEventListener('change', () => {
            if (!sel.value || !inst) return;
            const p = JSON.parse(sel.value);
            if (p.meta) { for (const [key, val] of Object.entries(p.meta)) { const slider = document.querySelector(`[data-meta="${key}"]`); if (slider) { slider.value = val; slider.dispatchEvent(new Event('input')); } } }
            if (p.structural) { for (const [name, val] of Object.entries(p.structural)) { const slider = document.querySelector(`[data-morph="${name}"]`); if (slider) { slider.value = val; slider.dispatchEvent(new Event('input')); } } }
            serverLog('preset_applied', p.label);
        });
    } catch(e) { console.error('Failed to load presets:', e); }
}

function populateMetaSliders(inst) {
    const container = document.getElementById('prop-meta-sliders');
    container.innerHTML = '';
    if (!state.morphDefs || !state.morphDefs.meta_sliders) return;
    for (const [name, meta] of Object.entries(state.morphDefs.meta_sliders)) {
        const neutral = (meta.min + meta.max) / 2;
        const half = (meta.max - meta.min) / 2;
        const internal = inst.meta[name] || 0;
        const displayVal = neutral + internal * half;
        const row = document.createElement('div'); row.className = 'slider-row';
        const label = document.createElement('label'); label.textContent = meta.label || name; label.style.minWidth = '80px';
        const slider = document.createElement('input'); slider.type = 'range'; slider.min = meta.min; slider.max = meta.max; slider.step = 1; slider.value = Math.round(displayVal); slider.dataset.meta = name;
        const valSpan = document.createElement('span'); valSpan.className = 'slider-val'; valSpan.textContent = Math.round(displayVal);
        slider.addEventListener('input', () => { valSpan.textContent = slider.value; });
        slider.addEventListener('change', () => { const dv = parseFloat(slider.value); inst.meta[name] = (dv - neutral) / half; reloadCharacterMesh(inst); });
        row.appendChild(label); row.appendChild(slider); row.appendChild(valSpan); container.appendChild(row);
    }
}

function populateMorphSliders(inst) {
    const container = document.getElementById('prop-morphs-panel');
    container.innerHTML = '';
    if (!state.morphDefs || !state.morphDefs.morphs || !state.morphDefs.categories) return;
    const byCategory = {};
    for (const m of state.morphDefs.morphs) { const cat = m.category || 'Other'; if (!byCategory[cat]) byCategory[cat] = []; byCategory[cat].push(m); }
    for (const cat of state.morphDefs.categories) {
        const morphs = byCategory[cat];
        if (!morphs || morphs.length === 0) continue;
        const div = document.createElement('div'); div.className = 'morph-category';
        const header = document.createElement('div'); header.className = 'morph-category-header';
        header.innerHTML = `<span class="cat-chevron">&#9654;</span> ${escapeHtml(cat)} (${morphs.length})`;
        header.addEventListener('click', () => div.classList.toggle('open'));
        const body = document.createElement('div'); body.className = 'morph-category-body';
        for (const m of morphs) {
            const currentVal = (inst.morphs[m.name] || 0) * 100;
            const row = document.createElement('div'); row.className = 'slider-row';
            const label = document.createElement('label');
            let displayName = m.name;
            if (displayName.startsWith(cat + '_')) displayName = displayName.substring(cat.length + 1);
            label.textContent = displayName.replace(/_/g, ' '); label.title = m.name; label.style.minWidth = '80px'; label.style.fontSize = '0.72rem';
            const slider = document.createElement('input'); slider.type = 'range'; slider.min = -100; slider.max = 100; slider.step = 1; slider.value = Math.round(currentVal);
            const valSpan = document.createElement('span'); valSpan.className = 'slider-val'; valSpan.textContent = Math.round(currentVal);
            slider.addEventListener('input', () => { valSpan.textContent = slider.value; });
            slider.addEventListener('change', () => { const v = parseFloat(slider.value) / 100; if (Math.abs(v) < 0.005) delete inst.morphs[m.name]; else inst.morphs[m.name] = v; reloadCharacterMesh(inst); });
            row.appendChild(label); row.appendChild(slider); row.appendChild(valSpan); body.appendChild(row);
        }
        div.appendChild(header); div.appendChild(body); container.appendChild(div);
    }
}

export async function reloadCharacterMesh(inst) {
    clearTimeout(state.reloadTimer);
    state.reloadTimer = setTimeout(async () => {
        try { await inst.reloadBody(); fn.updateVertexCount(); fn.updateCharacterListUI(); if (state.currentPropsCharId === inst.id) updateEquippedList(inst); markDirty(); }
        catch (e) { console.error('Failed to reload:', e); }
    }, 300);
}

export function updateEquippedList(inst) {
    const list = document.getElementById('prop-equipped-list');
    if (!list) return;
    list.innerHTML = '';
    if (!inst) { list.innerHTML = '<li class="equipped-empty">Keine Objekte</li>'; return; }
    const targets = getSelectableSubMeshes(inst.id);
    if (targets.length === 0) { list.innerHTML = '<li class="equipped-empty">Keine Objekte</li>'; return; }
    for (const t of targets) {
        const li = document.createElement('li'); li.className = 'equipped-item';
        const nameSpan = document.createElement('span'); nameSpan.className = 'equipped-item-name';
        if (_sameSubMesh(state._selectedSubMesh, t)) nameSpan.classList.add('selected');
        nameSpan.textContent = t.label;
        nameSpan.addEventListener('click', () => {
            if (state._selectedSubMesh) fn._setSubMeshEmissive(state._selectedSubMesh, state._ZERO_EMISSIVE);
            const fresh = getSelectableSubMeshes(inst.id).find(x => x.type === t.type && x.key === t.key);
            if (!fresh) return;
            state._selectedSubMesh = fresh;
            fn._setSubMeshEmissive(state._selectedSubMesh, state._SELECT_EMISSIVE);
            fn._setBodyEmissive(inst, state._ZERO_EMISSIVE);
            fn._syncGarmentSliders();
            _updatePropContext();
            if (fresh.type === 'cloth') fn._syncPropGarmentControls();
            else if (fresh.type === 'hair') fn._syncPropHairControls();
            updateEquippedList(inst);
        });
        const rmBtn = document.createElement('button'); rmBtn.className = 'equipped-item-remove'; rmBtn.innerHTML = '&#10005;'; rmBtn.title = 'Entfernen';
        rmBtn.addEventListener('click', (e) => { e.stopPropagation(); fn._removeSubMesh(t); });
        li.appendChild(nameSpan); li.appendChild(rmBtn); list.appendChild(li);
    }
}

export function _updatePropContext() {
    const bodySections = ['prop-transform-section', 'prop-equipped-section', 'prop-bodytype-section', 'prop-morphs-section'];
    const isGarment = state._selectedSubMesh && state._selectedSubMesh.type === 'cloth' && state._selectedSubMesh.key.startsWith('gar_');
    const isMH = state._selectedSubMesh && state._selectedSubMesh.type === 'cloth' && state._selectedSubMesh.key.startsWith('mh_');
    const isHair = state._selectedSubMesh && state._selectedSubMesh.type === 'hair';
    const isAsset = isGarment || isMH || isHair;
    for (const id of bodySections) { const el = document.getElementById(id); if (el) el.style.display = isAsset ? 'none' : ''; }
    const gEl = document.getElementById('prop-garment-section'); if (gEl) gEl.style.display = isGarment ? '' : 'none';
    const mhEl = document.getElementById('prop-mh-section'); if (mhEl) mhEl.style.display = isMH ? '' : 'none';
    const hEl = document.getElementById('prop-hair-section'); if (hEl) hEl.style.display = isHair ? '' : 'none';
    if (isMH) fn._syncPropMHControls();
}

// Register
fn.initTabs = initTabs;
fn.switchTab = switchTab;
fn.fetchMorphDefs = fetchMorphDefs;
fn.populateProperties = populateProperties;
fn.clearProperties = clearProperties;
fn.syncTransformInputs = syncTransformInputs;
fn.reloadCharacterMesh = reloadCharacterMesh;
fn.updateEquippedList = updateEquippedList;
fn._updatePropContext = _updatePropContext;
