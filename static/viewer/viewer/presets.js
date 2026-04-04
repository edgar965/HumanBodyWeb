/**
 * Viewer — Model Presets (load/save dialogs, apply preset, gather state).
 */
import { state, DEFAULT_BODY } from './state.js';
import { fn } from './registry.js';
import { wsSend } from './websocket.js';
import { applySceneSkinSettings } from './scene_settings.js';
import { removeAllCloth, loadCloth } from './cloth.js';
import { loadHair, removeHair, applyHairColor } from './hair.js';
import { loadGarment, removeAllGarments } from './garment.js';
import { loadBVHAnimation } from './animation.js';

export function initLoadPreset() {
    const btn = document.getElementById('load-preset-btn');
    if (!btn) return;
    btn.addEventListener('click', async () => {
        const name = await showLoadDialog();
        if (!name) return;
        try {
            const resp = await fetch(`/api/character/model/${encodeURIComponent(name)}/`);
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const preset = await resp.json();
            applyModelPreset(preset);
            state.currentPresetName = preset.name || name;
            btn.innerHTML = '<i class="fas fa-check"></i> Geladen!';
            setTimeout(() => { btn.innerHTML = '<i class="fas fa-folder-open"></i> Laden'; }, 1500);
        } catch (err) { console.error('Load preset error:', err); alert('Fehler beim Laden: ' + err.message); }
    });
    loadDefaultPreset();
}

async function loadDefaultPreset() {
    const maxWait = 15000; const start = Date.now();
    while (!state.bodyMesh && Date.now() - start < maxWait) await new Promise(r => setTimeout(r, 200));
    if (!state.bodyMesh) { console.warn('Default preset: mesh not ready, skipping'); return; }
    await new Promise(r => setTimeout(r, 500));

    if (DEFAULT_BODY) {
        try {
            const bodySelect = document.getElementById('body-type-select');
            if (bodySelect) { bodySelect.value = DEFAULT_BODY; bodySelect.dispatchEvent(new Event('change')); }
            console.log(`Default body type applied: ${DEFAULT_BODY}`);
        } catch (e) { console.warn('Failed to apply default body type:', e); }
        return;
    }

    try {
        let presetName = 'femaleWithClothes'; let showRig = false; let defaultAnim = '';
        const isSmplPage = !!document.getElementById('smpl-body-panel');
        if (isSmplPage) {
            try { const smplResp = await fetch('/api/settings/smpl/'); if (smplResp.ok) { const smplCfg = await smplResp.json(); if (smplCfg.humanbody_preset) presetName = smplCfg.humanbody_preset; } } catch (e) {}
        } else {
            try { const settingsResp = await fetch('/api/settings/humanbody/'); if (settingsResp.ok) { const s = await settingsResp.json(); if (s.config) presetName = s.config; showRig = !!s.show_rig_config; defaultAnim = s.default_anim_config || ''; } } catch (e) {}
        }
        if (showRig) { state.rigVisible = true; const rigToggle = document.getElementById('rig-toggle'); if (rigToggle) rigToggle.classList.add('active'); }
        const resp = await fetch(`/api/character/model/${encodeURIComponent(presetName)}/`);
        if (!resp.ok) return;
        const preset = await resp.json();
        applyModelPreset(preset);
        setTimeout(() => applySceneSkinSettings(), 200);
        console.log(`Default preset loaded: ${presetName}`);
        if (defaultAnim) {
            setTimeout(() => {
                loadBVHAnimation(defaultAnim, 'Default', 0);
                const demoBtn = document.getElementById('play-demo-anim');
                if (demoBtn) { demoBtn.innerHTML = '<i class="fas fa-pause"></i>'; demoBtn.classList.add('active'); }
            }, 1500);
        }
    } catch (e) { console.warn('Failed to load default preset:', e); }
}

export function applyModelPreset(preset) {
    const bodySelect = document.getElementById('body-type-select');
    if (bodySelect && preset.body_type) { bodySelect.value = preset.body_type; bodySelect.dispatchEvent(new Event('change')); }

    if (preset.meta) {
        ['age', 'mass', 'tone', 'height'].forEach(name => {
            const el = document.getElementById(`meta-${name}`); const valSpan = document.getElementById(`meta-${name}-val`);
            if (el && preset.meta[name] !== undefined) {
                const internal = preset.meta[name]; const min = parseInt(el.min), max = parseInt(el.max);
                const neutral = (min + max) / 2; const half = (max - min) / 2;
                const displayVal = Math.round(internal * half + neutral);
                el.value = displayVal; if (valSpan) valSpan.textContent = displayVal;
                wsSend({ type: 'meta', name, value: internal });
            }
        });
    }

    if (preset.morphs) {
        const morphBatch = {}; const panel = document.getElementById('morphs-panel');
        if (panel) {
            panel.querySelectorAll('input[type="range"][data-morph]').forEach(slider => {
                const morphName = slider.dataset.morph; const val = preset.morphs[morphName];
                if (val !== undefined) { const intVal = Math.round(val * 100); slider.value = intVal; slider.nextElementSibling.textContent = intVal; morphBatch[morphName] = val; }
                else { slider.value = 0; slider.nextElementSibling.textContent = '0'; }
            });
        }
        if (Object.keys(morphBatch).length > 0) wsSend({ type: 'morph_batch', morphs: morphBatch });
    }

    if (preset.wardrobe && preset.wardrobe.length > 0) {
        const wardrobePanel = document.getElementById('wardrobe-panel');
        if (wardrobePanel) {
            wardrobePanel.querySelectorAll('.asset-btn.active').forEach(btn => { if (!preset.wardrobe.includes(btn.dataset.asset)) btn.click(); });
            preset.wardrobe.forEach(assetName => { const btn = wardrobePanel.querySelector(`.asset-btn[data-asset="${assetName}"]`); if (btn && !btn.classList.contains('active') && !btn.classList.contains('disabled')) btn.click(); });
        }
    }

    const isMalePreset = preset.body_type && preset.body_type.startsWith('Male_');
    if (preset.cloth && !isMalePreset) {
        removeAllCloth();
        const clothList = (Array.isArray(preset.cloth) ? preset.cloth : [preset.cloth]).filter(Boolean);
        clothList.forEach((c, i) => {
            if (!c) return;
            setTimeout(() => {
                const tpl = c.template || (c.region ? { TOP: 'TPL_TSHIRT', PANTS: 'TPL_PANTS', SKIRT: 'TPL_SKIRT', DRESS: 'TPL_DRESS' }[c.region] : 'TPL_TSHIRT');
                const tight = c.tightness !== undefined ? c.tightness : 0.5;
                loadCloth(`tpl_${tpl}`, { method: 'template', template: tpl, tightness: tight, segments: c.segments || 32, top_extend: c.top_extend || 0, bottom_extend: c.bottom_extend || 0 }, c.color || null);
            }, 500 + i * 300);
        });
        const last = clothList[clothList.length - 1];
        const tplSelect = document.getElementById('cloth-tpl-type');
        const tpl = last ? (last.template || (last.region ? { TOP: 'TPL_TSHIRT', PANTS: 'TPL_PANTS', SKIRT: 'TPL_SKIRT', DRESS: 'TPL_DRESS' }[last.region] : 'TPL_TSHIRT')) : 'TPL_TSHIRT';
        if (tplSelect) { tplSelect.value = tpl; tplSelect.dispatchEvent(new Event('change')); }
        const tight = (last && last.tightness !== undefined) ? last.tightness : 0.5;
        const tplTight = document.getElementById('cloth-tpl-tightness');
        const tplTightVal = document.getElementById('cloth-tpl-tightness-val');
        if (tplTight) tplTight.value = Math.round(tight * 100);
        if (tplTightVal) tplTightVal.textContent = tight.toFixed(2);
        const colorPicker = document.getElementById('cloth-color');
        if (colorPicker && last && last.color) colorPicker.value = last.color;
    }

    if (preset.hair_style) {
        const hairSelect = document.getElementById('hair-style-select');
        const hairColorSelect = document.getElementById('hair-color-select');
        if (hairSelect && preset.hair_style.url) { for (const opt of hairSelect.options) { if (opt.value === preset.hair_style.url) { hairSelect.value = opt.value; break; } } loadHair(preset.hair_style.url); }
        if (hairColorSelect && preset.hair_style.color) { hairColorSelect.value = preset.hair_style.color; setTimeout(() => applyHairColor(preset.hair_style.color), 1000); }
    }

    if (preset.garments && preset.garments.length > 0) {
        removeAllGarments();
        const _setEl = (id, v) => { const e = document.getElementById(id); if (e) e.value = v; };
        const loadGarments = async () => {
            for (const g of preset.garments) {
                _setEl('garment-offset', Math.round((g.offset || 0.006) * 1000)); _setEl('garment-stiffness', Math.round((g.stiffness || 0.8) * 100));
                _setEl('garment-min-dist', g.minDist !== undefined ? g.minDist : 3); _setEl('garment-crotch-floor', g.crotchFloor !== undefined ? g.crotchFloor : 0);
                _setEl('garment-lift', g.lift !== undefined ? g.lift : 0); _setEl('garment-crotch-depth', g.crotchDepth !== undefined ? g.crotchDepth : 0);
                _setEl('garment-color', g.color || '#4d5980'); _setEl('garment-roughness', Math.round((g.roughness || 0.8) * 100)); _setEl('garment-metalness', Math.round((g.metalness || 0) * 100));
                _setEl('garment-pos-x', Math.round((g.posX || 0) * 100)); _setEl('garment-pos-y', Math.round((g.posY || 0) * 100)); _setEl('garment-pos-z', Math.round((g.posZ || 0) * 100));
                _setEl('garment-scale-x', Math.round((g.scaleX || 1) * 100)); _setEl('garment-scale-y', Math.round((g.scaleY || 1) * 100)); _setEl('garment-scale-z', Math.round((g.scaleZ || 1) * 100));
                state.selectedGarmentId = g.id;
                await loadGarment(g.id);
            }
            fn.updateEquippedList();
        };
        setTimeout(() => loadGarments(), 800);
    }

    state.currentPresetName = preset.name || '';
    setTimeout(() => { try { localStorage.setItem('humanbody_current_model', JSON.stringify(gatherModelState())); } catch (e) {} }, 2000);
    console.log(`Preset "${preset.name || 'unknown'}" applied`);
}

export function gatherModelState() {
    const modelState = {};
    const bodySelect = document.getElementById('body-type-select');
    if (bodySelect) modelState.body_type = bodySelect.value;

    const meta = {};
    ['age', 'mass', 'tone', 'height'].forEach(name => {
        const el = document.getElementById(`meta-${name}`);
        if (el) { const dv = parseInt(el.value); const min = parseInt(el.min), max = parseInt(el.max); const neutral = (min + max) / 2; const half = (max - min) / 2; meta[name] = half ? (dv - neutral) / half : 0; }
    });
    modelState.meta = meta;

    const morphs = {}; const panel = document.getElementById('morphs-panel');
    if (panel) { panel.querySelectorAll('input[type="range"][data-morph]').forEach(slider => { const val = parseInt(slider.value); if (val !== 0) morphs[slider.dataset.morph] = val / 100; }); }
    modelState.morphs = morphs;

    const clothList = [];
    for (const [key, cp] of Object.entries(state.clothParams)) {
        const p = cp.params; const entry = {};
        if (p.method === 'template') { entry.template = p.template; entry.tightness = p.tightness !== undefined ? p.tightness : 0.5; entry.segments = p.segments || 32; if (p.top_extend) entry.top_extend = p.top_extend; if (p.bottom_extend) entry.bottom_extend = p.bottom_extend; }
        else if (p.method === 'builder') { entry.method = 'builder'; entry.region = p.region; entry.looseness = p.looseness; }
        else if (p.method === 'primitive') { entry.method = 'primitive'; entry.prim_type = p.prim_type; entry.segments = p.segments; entry.length = p.length; if (p.flare) entry.flare = p.flare; }
        entry.color = cp.color; clothList.push(entry);
    }
    modelState.cloth = clothList;

    const hairSelect = document.getElementById('hair-style-select'); const hairColorSelect = document.getElementById('hair-color-select');
    if (hairSelect && hairSelect.value) { modelState.hair_style = { url: hairSelect.value, name: hairSelect.options[hairSelect.selectedIndex]?.textContent || '', color: hairColorSelect ? hairColorSelect.value : '' }; }

    const wardrobePanel = document.getElementById('wardrobe-panel'); const activeAssets = [];
    if (wardrobePanel) wardrobePanel.querySelectorAll('.asset-btn.active').forEach(btn => { activeAssets.push(btn.dataset.asset); });
    modelState.wardrobe = activeAssets;

    const garments = [];
    for (const [gid, st] of Object.entries(state.garmentState)) {
        if (state.garmentMeshes[gid]) garments.push({ id: gid, offset: st.offset, stiffness: st.stiffness, color: st.color, roughness: st.roughness, metalness: st.metalness, posX: st.posX, posY: st.posY, posZ: st.posZ, scaleX: st.scaleX, scaleY: st.scaleY, scaleZ: st.scaleZ });
    }
    modelState.garments = garments;

    const sceneSaved = localStorage.getItem('humanbody_scene_settings');
    if (sceneSaved) { try { modelState.scene = JSON.parse(sceneSaved); } catch (e) {} }
    return modelState;
}

async function saveModel(name) {
    const data = gatherModelState(); data.name = name;
    try {
        const resp = await fetch('/api/character/model/save/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, data }) });
        const result = await resp.json();
        if (result.ok) { state.currentPresetName = name; console.log(`Model saved: ${result.filename}`); return true; }
        else { alert('Fehler beim Speichern: ' + (result.error || 'Unbekannt')); return false; }
    } catch (e) { alert('Fehler beim Speichern: ' + e.message); return false; }
}

function createSaveDialog() {
    if (document.getElementById('save-dialog-overlay')) return;
    const overlay = document.createElement('div'); overlay.id = 'save-dialog-overlay';
    overlay.innerHTML = `<div class="save-dialog"><div class="save-dialog-header"><h3><i class="fas fa-file-export"></i> Modell speichern unter</h3><button class="save-dialog-close" title="Schlie\u00DFen">&times;</button></div><div class="save-dialog-body"><label>Vorhandene Modelle:</label><div class="save-dialog-list" id="save-dialog-list"></div><label style="margin-top:12px;">Name:</label><input type="text" id="save-dialog-name" placeholder="Neuer Name..." autocomplete="off"></div><div class="save-dialog-footer"><button class="save-dialog-btn cancel" id="save-dialog-cancel">Abbrechen</button><button class="save-dialog-btn confirm" id="save-dialog-confirm"><i class="fas fa-save"></i> Speichern</button></div></div>`;
    document.body.appendChild(overlay);
    if (!document.getElementById('save-dialog-styles')) {
        const style = document.createElement('style'); style.id = 'save-dialog-styles';
        style.textContent = `#save-dialog-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:10000;align-items:center;justify-content:center}#save-dialog-overlay.open{display:flex}.save-dialog{background:var(--bg-secondary,#1e1e2e);border:1px solid var(--border,#333);border-radius:8px;width:420px;max-height:80vh;display:flex;flex-direction:column;box-shadow:0 8px 32px rgba(0,0,0,0.5)}.save-dialog-header{display:flex;align-items:center;justify-content:space-between;padding:14px 18px;border-bottom:1px solid var(--border,#333)}.save-dialog-header h3{margin:0;font-size:1rem;color:var(--text,#eee)}.save-dialog-close{background:none;border:none;color:var(--text-muted,#888);font-size:1.4rem;cursor:pointer;padding:0 4px;line-height:1}.save-dialog-close:hover{color:var(--text,#eee)}.save-dialog-body{padding:14px 18px;overflow-y:auto}.save-dialog-body label{display:block;font-size:0.85rem;color:var(--text-muted,#999);margin-bottom:6px}.save-dialog-list{max-height:200px;overflow-y:auto;border:1px solid var(--border,#333);border-radius:4px;background:var(--bg-primary,#12121e)}.save-dialog-item{padding:8px 12px;cursor:pointer;font-size:0.9rem;color:var(--text,#eee);border-bottom:1px solid var(--border,#222)}.save-dialog-item:last-child{border-bottom:none}.save-dialog-item:hover{background:var(--accent,#5865f2);color:#fff}.save-dialog-item.selected{background:var(--accent,#5865f2);color:#fff}#save-dialog-name{width:100%;padding:8px 10px;border:1px solid var(--border,#333);border-radius:4px;background:var(--bg-primary,#12121e);color:var(--text,#eee);font-size:0.95rem;box-sizing:border-box}#save-dialog-name:focus{outline:none;border-color:var(--accent,#5865f2)}.save-dialog-footer{display:flex;justify-content:flex-end;gap:8px;padding:12px 18px;border-top:1px solid var(--border,#333)}.save-dialog-btn{padding:8px 18px;border:1px solid var(--border,#333);border-radius:4px;cursor:pointer;font-size:0.9rem}.save-dialog-btn.cancel{background:transparent;color:var(--text-muted,#999)}.save-dialog-btn.cancel:hover{color:var(--text,#eee)}.save-dialog-btn.confirm{background:var(--accent,#5865f2);color:#fff;border-color:var(--accent,#5865f2)}.save-dialog-btn.confirm:hover{filter:brightness(1.15)}`;
        document.head.appendChild(style);
    }
}

function showLoadDialog() { return _showDialog('load'); }
function showSaveDialog() { return _showDialog('save'); }

function _showDialog(mode) {
    return new Promise((resolve) => {
        createSaveDialog();
        const overlay = document.getElementById('save-dialog-overlay');
        const list = document.getElementById('save-dialog-list');
        const nameInput = document.getElementById('save-dialog-name');
        const confirmBtn = document.getElementById('save-dialog-confirm');
        const cancelBtn = document.getElementById('save-dialog-cancel');
        const closeBtn = overlay.querySelector('.save-dialog-close');

        if (mode === 'load') {
            overlay.querySelector('.save-dialog-header h3').innerHTML = '<i class="fas fa-folder-open"></i> Modell laden';
            confirmBtn.innerHTML = '<i class="fas fa-folder-open"></i> Laden';
            nameInput.value = ''; nameInput.placeholder = 'Modellname...';
        } else {
            overlay.querySelector('.save-dialog-header h3').innerHTML = '<i class="fas fa-file-export"></i> Modell speichern unter';
            confirmBtn.innerHTML = '<i class="fas fa-save"></i> Speichern';
            nameInput.value = state.currentPresetName || ''; nameInput.placeholder = 'Neuer Name...';
        }

        list.innerHTML = '<div style="padding:8px 12px;color:var(--text-muted,#888);font-size:0.85rem;">Lade...</div>';
        overlay.classList.add('open');
        if (mode === 'save') nameInput.focus();

        fetch('/api/character/models/').then(r => r.json()).then(data => {
            list.innerHTML = '';
            (data.presets || []).forEach(p => {
                const item = document.createElement('div'); item.className = 'save-dialog-item';
                item.textContent = p.label || p.name; item.dataset.name = p.name;
                item.addEventListener('click', () => { list.querySelectorAll('.save-dialog-item').forEach(i => i.classList.remove('selected')); item.classList.add('selected'); nameInput.value = p.name; if (mode === 'save') nameInput.focus(); });
                if (mode === 'load') item.addEventListener('dblclick', () => { nameInput.value = p.name; close(p.name); });
                list.appendChild(item);
            });
            if (list.children.length === 0) list.innerHTML = '<div style="padding:8px 12px;color:var(--text-muted,#888);font-size:0.85rem;">Keine Modelle vorhanden</div>';
        }).catch(() => { list.innerHTML = '<div style="padding:8px 12px;color:#f44;font-size:0.85rem;">Fehler beim Laden</div>'; });

        function close(result) {
            overlay.classList.remove('open');
            overlay.querySelector('.save-dialog-header h3').innerHTML = '<i class="fas fa-file-export"></i> Modell speichern unter';
            confirmBtn.innerHTML = '<i class="fas fa-save"></i> Speichern'; nameInput.placeholder = 'Neuer Name...';
            confirmBtn.removeEventListener('click', onConfirm); cancelBtn.removeEventListener('click', onCancel);
            closeBtn.removeEventListener('click', onCancel); overlay.removeEventListener('click', onOverlayClick);
            nameInput.removeEventListener('keydown', onKeydown); resolve(result);
        }
        function onConfirm() { const name = nameInput.value.trim(); if (name) close(name); else nameInput.focus(); }
        function onCancel() { close(null); }
        function onOverlayClick(e) { if (e.target === overlay) close(null); }
        function onKeydown(e) { if (e.key === 'Enter') onConfirm(); if (e.key === 'Escape') onCancel(); }
        confirmBtn.addEventListener('click', onConfirm); cancelBtn.addEventListener('click', onCancel);
        closeBtn.addEventListener('click', onCancel); overlay.addEventListener('click', onOverlayClick);
        nameInput.addEventListener('keydown', onKeydown);
    });
}

export function initSaveButtons() {
    const saveBtn = document.getElementById('save-model-btn');
    const saveAsBtn = document.getElementById('save-model-as-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            if (!state.currentPresetName) { const name = await showSaveDialog(); if (!name) return; const ok = await saveModel(name); if (ok) { saveBtn.innerHTML = '<i class="fas fa-check"></i> Gespeichert!'; setTimeout(() => { saveBtn.innerHTML = '<i class="fas fa-save"></i> Speichern'; }, 1500); } return; }
            const ok = await saveModel(state.currentPresetName);
            if (ok) { saveBtn.innerHTML = '<i class="fas fa-check"></i> Gespeichert!'; setTimeout(() => { saveBtn.innerHTML = '<i class="fas fa-save"></i> Speichern'; }, 1500); }
        });
    }
    if (saveAsBtn) {
        saveAsBtn.addEventListener('click', async () => {
            const name = await showSaveDialog(); if (!name) return;
            const ok = await saveModel(name);
            if (ok) { saveAsBtn.innerHTML = '<i class="fas fa-check"></i> Gespeichert!'; setTimeout(() => { saveAsBtn.innerHTML = '<i class="fas fa-file-export"></i> Speichern unter'; }, 1500); }
        });
    }
}

fn.initLoadPreset = initLoadPreset;
fn.initSaveButtons = initSaveButtons;
fn.gatherModelState = gatherModelState;
fn.applyModelPreset = applyModelPreset;
