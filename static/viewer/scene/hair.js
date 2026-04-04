/**
 * Scene Editor -- Hair UI + loading.
 */
import { THREE, gltfLoader } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';
import { _selectedInst } from './utils.js';
import { convertInstToSkinned, _skinifyHairGroup } from './skeleton.js';

export async function loadHairUI() {
    try {
        const resp = await fetch('/api/character/hairstyles/');
        const data = await resp.json();
        state._hairStylesData = data.hairstyles || [];
        state.hairColorData = data.colors || {};
        _populatePropHairOptions();
        const select = document.getElementById('hair-style-select');
        const colorSelect = document.getElementById('hair-color-select');
        if (!select) return;
        for (const h of state._hairStylesData) { const opt = document.createElement('option'); opt.value = h.url; opt.textContent = h.label; opt.dataset.name = h.name; select.appendChild(opt); }
        if (colorSelect) { for (const name of Object.keys(state.hairColorData)) { const opt = document.createElement('option'); opt.value = name; opt.textContent = name; colorSelect.appendChild(opt); } }
        select.addEventListener('change', () => {
            const inst = _selectedInst(); if (!inst) return;
            if (!select.value) { if (inst.hairMesh) { inst.group.remove(inst.hairMesh); inst.hairMesh.traverse(c => { if (c.isMesh) { c.geometry.dispose(); (Array.isArray(c.material)?c.material:[c.material]).forEach(m=>m.dispose()); } }); inst.hairMesh = null; inst.hairStyle = null; } fn.updateEquippedList(inst); fn.updateVertexCount(); return; }
            _loadHairForCharacter(inst, select.value, colorSelect?.value || '');
        });
        if (colorSelect) { colorSelect.addEventListener('change', () => {
            const inst = _selectedInst(); if (!inst || !inst.hairMesh) return;
            const rgb = state.hairColorData[colorSelect.value]; if (!rgb) return;
            const color = new THREE.Color(rgb[0], rgb[1], rgb[2]);
            inst.hairMesh.traverse(c => { if (c.isMesh && c.material) (Array.isArray(c.material)?c.material:[c.material]).forEach(m => m.color.copy(color)); });
        }); }
    } catch (e) { console.warn('Hair UI not available:', e); }
}

export function _loadHairForCharacter(inst, url, colorName) {
    if (inst.hairMesh) { inst.group.remove(inst.hairMesh); inst.hairMesh.traverse(c => { if (c.isMesh) { c.geometry.dispose(); (Array.isArray(c.material)?c.material:[c.material]).forEach(m=>m.dispose()); } }); inst.hairMesh = null; }
    if (!inst.isSkinned && state.rigifySkeletonData && state.skinWeightData) convertInstToSkinned(inst);
    gltfLoader.load(url, (gltf) => {
        let hairGroup = gltf.scene;
        if (inst.isSkinned && inst.rigifySkeleton) hairGroup = _skinifyHairGroup(hairGroup, inst);
        inst.hairMesh = hairGroup;
        inst.hairStyle = { url, name: url.split('/').pop(), color: colorName };
        if (colorName && state.hairColorData[colorName]) {
            const rgb = state.hairColorData[colorName]; const color = new THREE.Color(rgb[0], rgb[1], rgb[2]);
            inst.hairMesh.traverse(c => { if (c.isMesh && c.material) (Array.isArray(c.material)?c.material:[c.material]).forEach(m => m.color.copy(color)); });
        }
        inst.group.add(inst.hairMesh);
        fn.updateEquippedList(inst); fn.updateVertexCount();
    }, undefined, (err) => { console.warn('Failed to load hair:', err); });
}

export function syncHairSelect(inst) {
    const select = document.getElementById('hair-style-select'); if (!select) return;
    select.value = (inst.hairStyle && inst.hairStyle.url) ? inst.hairStyle.url : '';
}

export function initPropHairControls() {
    const styleEl = document.getElementById('prop-hair-style');
    const colorEl = document.getElementById('prop-hair-color');
    if (!styleEl || !colorEl) return;
    _populatePropHairOptions();
    styleEl.addEventListener('change', () => {
        const inst = _selectedInst(); if (!inst) return;
        if (!styleEl.value) { if (inst.hairMesh) { inst.group.remove(inst.hairMesh); inst.hairMesh.traverse(c=>{if(c.isMesh){c.geometry.dispose();(Array.isArray(c.material)?c.material:[c.material]).forEach(m=>m.dispose());}}); inst.hairMesh=null; inst.hairStyle=null; } const a=document.getElementById('hair-style-select'); if(a) a.value=''; fn.updateEquippedList(inst); fn.updateVertexCount(); return; }
        _loadHairForCharacter(inst, styleEl.value, colorEl.value || '');
        const a = document.getElementById('hair-style-select'); if(a) a.value = styleEl.value;
    });
    colorEl.addEventListener('change', () => {
        const inst = _selectedInst(); if (!inst || !inst.hairMesh) return;
        const rgb = state.hairColorData[colorEl.value]; if (!rgb) return;
        const color = new THREE.Color(rgb[0], rgb[1], rgb[2]);
        inst.hairMesh.traverse(c => { if (c.isMesh && c.material) (Array.isArray(c.material)?c.material:[c.material]).forEach(m => m.color.copy(color)); });
        if (inst.hairStyle) inst.hairStyle.color = colorEl.value;
    });
}

function _populatePropHairOptions() {
    const styleEl = document.getElementById('prop-hair-style');
    const colorEl = document.getElementById('prop-hair-color');
    if (!styleEl || !colorEl || styleEl.options.length > 1) return;
    for (const h of (state._hairStylesData || [])) { const opt = document.createElement('option'); opt.value = h.url; opt.textContent = h.label; styleEl.appendChild(opt); }
    for (const name of Object.keys(state.hairColorData || {})) { const opt = document.createElement('option'); opt.value = name; opt.textContent = name; colorEl.appendChild(opt); }
}

export function _syncPropHairControls() {
    const inst = _selectedInst();
    const sec = document.getElementById('prop-hair-section');
    if (!inst || !state._selectedSubMesh || state._selectedSubMesh.type !== 'hair') { if (sec) sec.style.display = 'none'; return; }
    if (sec) sec.style.display = '';
    _populatePropHairOptions();
    const styleEl = document.getElementById('prop-hair-style');
    const colorEl = document.getElementById('prop-hair-color');
    if (styleEl) styleEl.value = (inst.hairStyle && inst.hairStyle.url) ? inst.hairStyle.url : '';
    if (colorEl) colorEl.value = (inst.hairStyle && inst.hairStyle.color) ? inst.hairStyle.color : '';
}

fn.loadHairUI = loadHairUI;
fn._loadHairForCharacter = _loadHairForCharacter;
fn.syncHairSelect = syncHairSelect;
fn.initPropHairControls = initPropHairControls;
fn._syncPropHairControls = _syncPropHairControls;
