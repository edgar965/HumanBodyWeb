/**
 * Viewer — 3D Interaction (hover highlight, click-to-select, equipped list).
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';
import { removeGarment } from './garment.js';
import { removeClothRegion } from './cloth.js';
import { removeHair } from './hair.js';
import { isVeActive, isVeBoxSelecting, getVeTargetMesh, veHandleClick, veBoxSelectStart, veBoxSelectMove, veBoxSelectEnd, veHandleKeydown } from './vertex_editor.js';

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
    const canvas = state.renderer.domElement;
    const tooltip = document.getElementById('garment-tooltip');
    const removeBtn = document.getElementById('selection-remove-btn');

    let _hoverPending = false;
    let _lastMouseEvent = null;

    canvas.addEventListener('mousemove', (e) => {
        if (isVeActive() && isVeBoxSelecting()) { veBoxSelectMove(e); return; }
        _lastMouseEvent = e;
        if (!_hoverPending) {
            _hoverPending = true;
            requestAnimationFrame(() => {
                _hoverPending = false;
                if (_lastMouseEvent) {
                    if (isVeActive()) {
                        const rect = canvas.getBoundingClientRect();
                        state._mouseNDC.x = ((_lastMouseEvent.clientX - rect.left) / rect.width) * 2 - 1;
                        state._mouseNDC.y = -((_lastMouseEvent.clientY - rect.top) / rect.height) * 2 + 1;
                        state._raycaster.setFromCamera(state._mouseNDC, state.camera);
                        const hits = state._raycaster.intersectObject(getVeTargetMesh());
                        canvas.style.cursor = hits.length > 0 ? 'pointer' : '';
                    } else {
                        _doHover(_lastMouseEvent);
                    }
                }
            });
        }
    });

    canvas.addEventListener('mouseleave', () => {
        if (state._hoveredItem && !_sameItem(state._hoveredItem, state._selectedItem)) _setEmissiveOnItem(state._hoveredItem, state._ZERO_EMISSIVE);
        state._hoveredItem = null;
        if (tooltip) tooltip.style.display = 'none';
    });

    canvas.addEventListener('mousedown', (e) => {
        if (e.button === 0) {
            state._mouseDownPos = { x: e.clientX, y: e.clientY };
            if (isVeActive() && e.altKey) veBoxSelectStart(e);
        }
    });

    canvas.addEventListener('mouseup', (e) => {
        if (isVeActive() && isVeBoxSelecting()) { veBoxSelectEnd(e); state._mouseDownPos = null; return; }
        if (e.button !== 0 || !state._mouseDownPos) return;
        const dx = e.clientX - state._mouseDownPos.x;
        const dy = e.clientY - state._mouseDownPos.y;
        state._mouseDownPos = null;
        if (Math.sqrt(dx * dx + dy * dy) > 3) return;
        if (isVeActive()) { veHandleClick(e); return; }
        _doClick();
    });

    window.addEventListener('keydown', (e) => {
        if (e.target.closest('input, select, textarea')) return;
        if (e.key === 'Delete' && state._selectedItem) { _removeSelectedItem(); return; }
        if (isVeActive()) { veHandleKeydown(e); return; }
    });

    if (removeBtn) removeBtn.addEventListener('click', () => _removeSelectedItem());

    function _doHover(e) {
        const rect = canvas.getBoundingClientRect();
        state._mouseNDC.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        state._mouseNDC.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        state._raycaster.setFromCamera(state._mouseNDC, state.camera);
        const targets = getSelectableTargets();
        const roots = targets.map(t => t.root);
        const intersects = state._raycaster.intersectObjects(roots, true);
        let newItem = null;
        if (intersects.length > 0) newItem = _findItemForObject(intersects[0].object, targets);
        if (newItem && tooltip) {
            tooltip.textContent = newItem.label;
            tooltip.style.left = (e.clientX - rect.left + 14) + 'px';
            tooltip.style.top = (e.clientY - rect.top - 10) + 'px';
            tooltip.style.display = 'block';
            canvas.style.cursor = 'pointer';
        } else { if (tooltip) tooltip.style.display = 'none'; canvas.style.cursor = ''; }
        if (!_sameItem(state._hoveredItem, newItem)) {
            if (state._hoveredItem && !_sameItem(state._hoveredItem, state._selectedItem)) _setEmissiveOnItem(state._hoveredItem, state._ZERO_EMISSIVE);
            state._hoveredItem = newItem;
            if (state._hoveredItem && !_sameItem(state._hoveredItem, state._selectedItem)) _setEmissiveOnItem(state._hoveredItem, state._HOVER_EMISSIVE);
        }
    }

    function _doClick() {
        const prev = state._selectedItem;
        if (state._hoveredItem) {
            if (_sameItem(state._selectedItem, state._hoveredItem)) {
                _setEmissiveOnItem(state._selectedItem, state._ZERO_EMISSIVE); state._selectedItem = null;
                if (removeBtn) removeBtn.style.display = 'none';
            } else {
                if (state._selectedItem) _setEmissiveOnItem(state._selectedItem, state._ZERO_EMISSIVE);
                state._selectedItem = state._hoveredItem;
                _setEmissiveOnItem(state._selectedItem, state._SELECT_EMISSIVE);
                if (removeBtn) removeBtn.style.display = '';
            }
        } else {
            if (state._selectedItem) _setEmissiveOnItem(state._selectedItem, state._ZERO_EMISSIVE);
            state._selectedItem = null;
            if (removeBtn) removeBtn.style.display = 'none';
        }
        if (!_sameItem(prev, state._selectedItem)) _onSelectionChanged(state._selectedItem);
    }
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
    _equippedListTimer = setTimeout(_buildEquippedList, 100);
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
        const nameSpan = document.createElement('span'); nameSpan.className = 'equipped-item-name'; nameSpan.textContent = t.label;
        nameSpan.addEventListener('click', () => {
            if (state._selectedItem) _setEmissiveOnItem(state._selectedItem, state._ZERO_EMISSIVE);
            const fresh = getSelectableTargets().find(x => x.type === t.type && x.id === t.id);
            if (!fresh) return;
            state._selectedItem = fresh;
            _setEmissiveOnItem(state._selectedItem, state._SELECT_EMISSIVE);
            const rb = document.getElementById('selection-remove-btn'); if (rb) rb.style.display = '';
        });
        const rmBtn = document.createElement('button'); rmBtn.className = 'equipped-item-remove'; rmBtn.innerHTML = '&#10005;'; rmBtn.title = 'Remove';
        rmBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            switch (t.type) {
                case 'garment': removeGarment(t.id); break;
                case 'cloth': removeClothRegion(t.id); break;
                case 'hair': { removeHair(); const hs2 = document.getElementById('hair-style-select'); if (hs2) hs2.value = ''; break; }
                case 'wardrobe': { const btn = document.querySelector(`.asset-btn[data-asset="${t.id}"]`); if (btn) btn.click(); break; }
                case 'smpl_garment': if (fn.removeSmplGarment) fn.removeSmplGarment(t.id); break;
            }
            if (_sameItem(state._selectedItem, t)) { state._selectedItem = null; const rb = document.getElementById('selection-remove-btn'); if (rb) rb.style.display = 'none'; }
            updateEquippedList();
        });
        li.appendChild(nameSpan); li.appendChild(rmBtn); list.appendChild(li);
    }
}

// Register
fn.getSelectableTargets = getSelectableTargets;
fn._setEmissiveOnItem = _setEmissiveOnItem;
fn.updateEquippedList = updateEquippedList;
fn.initInteraction = initInteraction;
