/**
 * Viewer — 3D Interaction (hover highlight, click-to-select, equipped list).
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { removeGarment } from './garment.js';
import { removeClothRegion } from './cloth.js';
import { removeHair } from './hair.js';
import { Zeigerinteraktion } from './zeigerinteraktion.js';
import { Zeiten } from '../gemeinsam/zeiten.js';

export function getSelectableTargets() {
    const targets = [];
    for (const [id, m] of Object.entries(state.garmentMeshes)) {
        if (m) targets.push({ root: m, type: 'garment', id, label: id.split('/').pop() });
    }
    for (const [key, m] of Object.entries(state.clothMeshes)) {
        if (m) targets.push({ root: m, type: 'cloth', id: key, label: key });
    }
    for (const [name, obj] of Object.entries(state.loadedAssets)) {
        if (obj) targets.push({ root: obj, type: 'wardrobe', id: name, label: name.replace(/_/g, ' ') });
    }
    if (state.hairMesh) {
        const hs = document.getElementById('hair-style-select');
        const label = hs ? (hs.options[hs.selectedIndex]?.textContent || 'Hair') : 'Hair';
        targets.push({ root: state.hairMesh, type: 'hair', id: 'hair', label });
    }
    for (const [id, m] of Object.entries(state.smplGarmentMeshes)) {
        if (m) targets.push({ root: m, type: 'smpl_garment', id, label: 'SMPL: ' + id });
    }
    return targets;
}

function _getMeshesOfRoot(root) {
    const meshes = [];
    if (root.isMesh) meshes.push(root);
    else root.traverse(child => { if (child.isMesh) meshes.push(child); });
    return meshes;
}

export function _setEmissiveOnItem(item, color) {
    for (const m of _getMeshesOfRoot(item.root)) {
        if (m.material && m.material.emissive) m.material.emissive.copy(color);
    }
}

function _findItemForObject(obj, targets) {
    for (const t of targets) { let cur = obj; while (cur) { if (cur === t.root) return t; cur = cur.parent; } }
    return null;
}

function _sameItem(a, b) { if (!a || !b) return false; return a.type === b.type && a.id === b.id; }

function _onSelectionChanged(item) {
    if (!item) return;
    if (item.type === 'cloth' || item.type === 'garment') {
        const mesh = state.clothMeshes[item.id] || state.garmentMeshes[item.id];
        if (!mesh || !mesh.material) return;
        const mat = mesh.material;
        const peColor = document.getElementById('pe-color');
        const peRough = document.getElementById('pe-roughness');
        const peMetal = document.getElementById('pe-metalness');
        if (peColor) peColor.value = '#' + mat.color.getHexString();
        if (peRough) { peRough.value = Math.round(mat.roughness * 100); peRough.dispatchEvent(new Event('input')); }
        if (peMetal) { peMetal.value = Math.round(mat.metalness * 100); peMetal.dispatchEvent(new Event('input')); }
    }
}

export function initInteraction() {
    // Die Ereignisse stecken in `Zeigerinteraktion` — vorher standen hier
    // 107 Zeilen mit zwei inneren Funktionen und doppelter Strahlrechnung.
    return new Zeigerinteraktion({
        ziele: getSelectableTargets,
        finden: _findItemForObject,
        gleich: _sameItem,
        leuchten: _setEmissiveOnItem,
        entfernen: _removeSelectedItem,
        gewechselt: _onSelectionChanged,
    }).verdrahten();
}

function _removeSelectedItem() {
    if (!state._selectedItem) return;
    const { type, id } = state._selectedItem;
    switch (type) {
        case 'garment': removeGarment(id); break;
        case 'cloth': removeClothRegion(id); break;
        case 'hair': { removeHair(); const hs = document.getElementById('hair-style-select'); if (hs) hs.value = ''; break; }
        case 'wardrobe': { const btn = document.querySelector(`.asset-btn[data-asset="${id}"]`); if (btn) btn.click(); break; }
        case 'smpl_garment': if (fn.removeSmplGarment) fn.removeSmplGarment(id); break;
    }
    state._selectedItem = null; state._hoveredItem = null;
    const removeBtn = document.getElementById('selection-remove-btn');
    if (removeBtn) removeBtn.style.display = 'none';
    updateEquippedList();
}

let _equippedListTimer = null;
export function updateEquippedList() {
    clearTimeout(_equippedListTimer);
    _equippedListTimer = setTimeout(_buildEquippedList, Zeiten.SAMMELN_MS);
}

function _buildEquippedList() {
    const list = document.getElementById('equipped-items-list');
    if (!list) return;
    list.innerHTML = '';
    const targets = getSelectableTargets();
    if (targets.length === 0) {
        list.innerHTML = '<li style="color:var(--text-muted);font-size:0.78rem;padding:4px 0;">No items equipped</li>';
        return;
    }
    for (const t of targets) {
        const li = document.createElement('li'); li.className = 'equipped-item';
        const nameSpan = document.createElement('span');
        nameSpan.className = 'equipped-item-name';
        nameSpan.textContent = t.label;
        nameSpan.addEventListener('click', () => {
            if (state._selectedItem) _setEmissiveOnItem(state._selectedItem, state._ZERO_EMISSIVE);
            const fresh = getSelectableTargets().find(x => x.type === t.type && x.id === t.id);
            if (!fresh) return;
            state._selectedItem = fresh;
            _setEmissiveOnItem(state._selectedItem, state._SELECT_EMISSIVE);
            const rb = document.getElementById('selection-remove-btn'); if (rb) rb.style.display = '';
        });
        const rmBtn = document.createElement('button');
        rmBtn.className = 'equipped-item-remove';
        rmBtn.innerHTML = '&#10005;';
        rmBtn.title = 'Remove';
        rmBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            switch (t.type) {
                case 'garment': removeGarment(t.id); break;
                case 'cloth': removeClothRegion(t.id); break;
                case 'hair': { removeHair(); const hs2 = document.getElementById('hair-style-select'); if (hs2) hs2.value = ''; break; }
                case 'wardrobe': { const btn = document.querySelector(`.asset-btn[data-asset="${t.id}"]`); if (btn) btn.click(); break; }
                case 'smpl_garment': if (fn.removeSmplGarment) fn.removeSmplGarment(t.id); break;
            }
            if (_sameItem(state._selectedItem, t)) {
                state._selectedItem = null;
                const rb = document.getElementById('selection-remove-btn');
                if (rb) rb.style.display = 'none';
            }
            updateEquippedList();
        });
        li.appendChild(nameSpan); li.appendChild(rmBtn); list.appendChild(li);
    }
}

// Register
fn.getSelectableTargets = getSelectableTargets;
fn._setEmissiveOnItem = _setEmissiveOnItem;
fn.updateEquippedList = updateEquippedList;
// Der Menuepunkt "Loeschen" ruft ueber die Registry — ohne diese
// Zeile tat er nichts (Befund 16.08.2026).
fn._removeSelectedItem = _removeSelectedItem;
