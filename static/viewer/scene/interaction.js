/**
 * Scene Editor -- Canvas click, raycasting, sub-mesh hover/select logic.
 */
import { THREE } from './state.js';
import { state } from './state.js';
import { fn } from './registry.js';
import { markDirty } from './undo.js';

// =========================================================================
// Sub-mesh target helpers
// =========================================================================
export function getSelectableSubMeshes(charId) {
    const inst = state.characters.get(charId);
    if (!inst) return [];
    const targets = [];
    for (const [key, mesh] of Object.entries(inst.clothMeshes)) {
        if (mesh) {
            targets.push({ type: 'cloth', key, label: key, meshObj: mesh, charId });
        }
    }
    if (inst.hairMesh) {
        const hName = inst.hairStyle?.name || inst.hairStyle?.url?.split('/').pop() || 'Hair';
        targets.push({ type: 'hair', key: 'hair', label: `Hair (${hName})`, meshObj: inst.hairMesh, charId });
    }
    return targets;
}

function getAllSubMeshTargets() {
    const targets = [];
    state.characters.forEach((inst, id) => { targets.push(...getSelectableSubMeshes(id)); });
    return targets;
}

function _findSubMeshForObject(obj, targets) {
    for (const t of targets) {
        let cur = obj;
        while (cur) {
            if (cur === t.meshObj) return t;
            cur = cur.parent;
        }
    }
    return null;
}

export function _sameSubMesh(a, b) {
    if (!a || !b) return false;
    return a.type === b.type && a.key === b.key && a.charId === b.charId;
}

function _getMeshesOf(root) {
    const meshes = [];
    if (root.isMesh) { meshes.push(root); } else { root.traverse(child => { if (child.isMesh) meshes.push(child); }); }
    return meshes;
}

export function _setSubMeshEmissive(target, color) {
    if (!target || !target.meshObj) return;
    for (const m of _getMeshesOf(target.meshObj)) {
        if (m.material) {
            const mats = Array.isArray(m.material) ? m.material : [m.material];
            for (const mat of mats) { if (mat.emissive) mat.emissive.copy(color); }
        }
    }
}

export function _setBodyEmissive(inst, color) {
    if (!inst || !inst.bodyMesh) return;
    const mats = Array.isArray(inst.bodyMesh.material) ? inst.bodyMesh.material : [inst.bodyMesh.material];
    for (const mat of mats) { if (mat.emissive) mat.emissive.copy(color); }
}

export function clearSubMeshSelection() {
    if (state._selectedSubMesh) { _setSubMeshEmissive(state._selectedSubMesh, state._ZERO_EMISSIVE); state._selectedSubMesh = null; }
    if (state._hoveredSubMesh) { _setSubMeshEmissive(state._hoveredSubMesh, state._ZERO_EMISSIVE); state._hoveredSubMesh = null; }
    fn._updatePropContext();
    const tooltip = document.getElementById('mesh-tooltip');
    if (tooltip) tooltip.style.display = 'none';
}

function _doSubMeshClick(hitTarget) {
    const inst = state.characters.get(hitTarget.charId);
    if (_sameSubMesh(state._selectedSubMesh, hitTarget)) {
        _setSubMeshEmissive(state._selectedSubMesh, state._ZERO_EMISSIVE);
        state._selectedSubMesh = null;
        if (inst) _setBodyEmissive(inst, state._SELECT_EMISSIVE);
    } else {
        if (state._selectedSubMesh) _setSubMeshEmissive(state._selectedSubMesh, state._ZERO_EMISSIVE);
        state._selectedSubMesh = hitTarget;
        _setSubMeshEmissive(state._selectedSubMesh, state._SELECT_EMISSIVE);
        if (inst) _setBodyEmissive(inst, state._ZERO_EMISSIVE);
    }
    fn._syncGarmentSliders();
    fn.switchTab('eigenschaften');
    fn._updatePropContext();
    if (state._selectedSubMesh && state._selectedSubMesh.type === 'cloth') {
        fn._syncPropGarmentControls();
    } else if (state._selectedSubMesh && state._selectedSubMesh.type === 'hair') {
        fn._syncPropHairControls();
    }
    if (inst) fn.updateEquippedList(inst);
}

export function _removeSubMesh(target) {
    if (!target) return;
    const inst = state.characters.get(target.charId);
    if (!inst) return;

    switch (target.type) {
        case 'cloth': {
            const mesh = inst.clothMeshes[target.key];
            if (mesh) {
                inst.group.remove(mesh);
                mesh.geometry.dispose();
                if (Array.isArray(mesh.material)) { mesh.material.forEach(m => m.dispose()); } else { mesh.material.dispose(); }
                delete inst.clothMeshes[target.key];
                if (target.key.startsWith('gar_')) {
                    const garId = target.key.slice(4);
                    inst.garments = (inst.garments || []).filter(g => g.id !== garId);
                    delete inst.garmentState[target.key];
                    delete inst.garmentOrigPositions[target.key];
                    delete inst.garmentRegionWeights[target.key];
                } else {
                    inst.cloth = (inst.cloth || []).filter(c => {
                        const m = c.method || 'template';
                        let ck;
                        if (m === 'builder') ck = `bld_${c.region || 'TOP'}`;
                        else if (m === 'primitive') ck = `prim_${c.prim_type || 'PRIM_SKIRT'}`;
                        else ck = `tpl_${c.template || 'TPL_TSHIRT'}`;
                        return ck !== target.key;
                    });
                }
            }
            break;
        }
        case 'hair': {
            if (inst.hairMesh) {
                inst.group.remove(inst.hairMesh);
                inst.hairMesh.traverse(child => {
                    if (child.isMesh) { child.geometry.dispose(); const mats = Array.isArray(child.material) ? child.material : [child.material]; mats.forEach(m => m.dispose()); }
                });
                inst.hairMesh = null;
                inst.hairStyle = null;
            }
            break;
        }
    }

    if (_sameSubMesh(state._selectedSubMesh, target)) state._selectedSubMesh = null;
    if (_sameSubMesh(state._hoveredSubMesh, target)) state._hoveredSubMesh = null;
    fn.updateEquippedList(inst);
    fn.updateVertexCount();
    markDirty();
}

// =========================================================================
// Bone selection helpers
// =========================================================================
export function _getBoneFromIntersection(intersection, bodyMesh) {
    if (!bodyMesh || !bodyMesh.userData.boneVertexRanges) return null;
    const vertIdx = intersection.face.a;
    const ranges = bodyMesh.userData.boneVertexRanges;
    for (const [boneName, range] of Object.entries(ranges)) {
        if (vertIdx >= range.start && vertIdx < range.start + range.count) return boneName;
    }
    return null;
}

export function _getOrCreateBoneHighlightGeo(bodyMesh, boneName) {
    if (state._boneHighlightCache.has(boneName)) return state._boneHighlightCache.get(boneName);
    const geo = bodyMesh.geometry;
    const ranges = bodyMesh.userData.boneVertexRanges;
    if (!ranges || !ranges[boneName]) return null;
    const { start, count } = ranges[boneName];
    const end = start + count;
    const indexArr = geo.index.array;
    const newIndices = [];
    for (let i = 0; i < indexArr.length; i += 3) {
        const a = indexArr[i], b = indexArr[i + 1], c = indexArr[i + 2];
        if (a >= start && a < end && b >= start && b < end && c >= start && c < end) {
            newIndices.push(a - start, b - start, c - start);
        }
    }
    if (newIndices.length === 0) return null;
    const posArr = geo.attributes.position.array;
    const subGeo = new THREE.BufferGeometry();
    subGeo.setAttribute('position', new THREE.Float32BufferAttribute(posArr.slice(start * 3, end * 3), 3));
    subGeo.setIndex(newIndices);
    subGeo.computeVertexNormals();
    if (geo.attributes.skinIndex && geo.attributes.skinWeight) {
        subGeo.setAttribute('skinIndex', new THREE.Float32BufferAttribute(geo.attributes.skinIndex.array.slice(start * 4, end * 4), 4));
        subGeo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(geo.attributes.skinWeight.array.slice(start * 4, end * 4), 4));
    }
    state._boneHighlightCache.set(boneName, subGeo);
    return subGeo;
}

export function _createBoneOverlay(bodyMesh, boneName, material) {
    const subGeo = _getOrCreateBoneHighlightGeo(bodyMesh, boneName);
    if (!subGeo) return null;
    let overlay;
    if (bodyMesh.isSkinnedMesh && subGeo.attributes.skinIndex) {
        overlay = new THREE.SkinnedMesh(subGeo, material);
        overlay.bind(bodyMesh.skeleton, bodyMesh.bindMatrix);
    } else {
        overlay = new THREE.Mesh(subGeo, material);
    }
    overlay.renderOrder = 1;
    overlay.raycast = function() {};
    overlay.userData._boneOverlay = true;
    if (bodyMesh.parent) bodyMesh.parent.add(overlay);
    return overlay;
}

export function _removeBoneOverlay(overlay) {
    if (overlay && overlay.parent) overlay.parent.remove(overlay);
}

export function _clearBoneHover() {
    if (state._boneHoverOverlay) { _removeBoneOverlay(state._boneHoverOverlay); state._boneHoverOverlay = null; }
    state._hoveredBoneName = null;
}

export function _clearBoneSelection() {
    if (state._boneSelectOverlay) { _removeBoneOverlay(state._boneSelectOverlay); state._boneSelectOverlay = null; }
    state._selectedBoneName = null;
}

export function _clearBoneHighlightCache() {
    for (const geo of state._boneHighlightCache.values()) geo.dispose();
    state._boneHighlightCache.clear();
    _clearBoneHover();
    _clearBoneSelection();
}

// =========================================================================
// Canvas click binding
// =========================================================================
export function bindCanvasClick() {
    const canvas = state.canvas;
    canvas.addEventListener('pointerdown', (e) => { state.mouseDownPos = { x: e.clientX, y: e.clientY }; });
    canvas.addEventListener('pointerup', (e) => {
        if (!state.mouseDownPos) return;
        const dx = e.clientX - state.mouseDownPos.x;
        const dy = e.clientY - state.mouseDownPos.y;
        state.mouseDownPos = null;
        if (Math.sqrt(dx * dx + dy * dy) > state.CLICK_THRESHOLD) return;
        if (state.transformDragging) return;

        const rect = canvas.getBoundingClientRect();
        state.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        state.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        state.raycaster.setFromCamera(state.mouse, state.camera);

        const meshes = [];
        state.characters.forEach((inst, id) => {
            inst.group.traverse(child => {
                if (child.isMesh && !child.userData._boneOverlay) { child.userData._parentCharId = id; meshes.push(child); }
            });
        });

        const hits = state.raycaster.intersectObjects(meshes, false);
        if (hits.length > 0) {
            const hitObj = hits[0].object;
            const charId = hitObj.userData._parentCharId;
            if (charId) {
                const subTargets = getSelectableSubMeshes(charId);
                const hitTarget = _findSubMeshForObject(hitObj, subTargets);
                if (hitTarget) {
                    if (state.selectedCharacterId !== charId) { clearSubMeshSelection(); fn.selectCharacter(charId); }
                    _clearBoneSelection();
                    _doSubMeshClick(hitTarget);
                    return;
                }
                const inst = state.characters.get(charId);
                if (e.ctrlKey && inst && inst.generatedConfig && hitObj === inst.bodyMesh && inst.bodyMesh.userData.boneVertexRanges) {
                    const boneName = _getBoneFromIntersection(hits[0], inst.bodyMesh);
                    if (boneName) {
                        if (state.selectedCharacterId !== charId) { clearSubMeshSelection(); fn.selectCharacter(charId); }
                        fn._doBoneClick(boneName, inst);
                        return;
                    }
                }
                clearSubMeshSelection();
                _clearBoneSelection();
                fn.selectCharacter(charId);
                fn.switchTab('eigenschaften');
                fn._updatePropContext();
                return;
            }
        }
        _clearBoneSelection();
        fn.deselectCharacter();
    });
}

// =========================================================================
// Sub-mesh hover interaction
// =========================================================================
export function initSubMeshInteraction() {
    const canvas = state.canvas;
    const tooltip = document.getElementById('mesh-tooltip');

    canvas.addEventListener('mousemove', (e) => {
        state._lastMouseEvent = e;
        if (!state._hoverPending) {
            state._hoverPending = true;
            requestAnimationFrame(() => {
                state._hoverPending = false;
                if (state._lastMouseEvent) _doSubMeshHover(state._lastMouseEvent);
            });
        }
    });

    canvas.addEventListener('mouseleave', () => {
        if (state._hoveredSubMesh && !_sameSubMesh(state._hoveredSubMesh, state._selectedSubMesh)) {
            _setSubMeshEmissive(state._hoveredSubMesh, state._ZERO_EMISSIVE);
        }
        state._hoveredSubMesh = null;
        _clearBoneHover();
        if (tooltip) tooltip.style.display = 'none';
        canvas.style.cursor = '';
    });

    function _doSubMeshHover(e) {
        if (state._refitting) return;
        const rect = canvas.getBoundingClientRect();
        state.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        state.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        state.raycaster.setFromCamera(state.mouse, state.camera);

        const targets = getAllSubMeshTargets();
        const roots = targets.map(t => t.meshObj);
        const boneTargets = [];
        state.characters.forEach((inst, id) => {
            if (inst.generatedConfig && inst.bodyMesh && inst.bodyMesh.userData.boneVertexRanges) {
                boneTargets.push({ bodyMesh: inst.bodyMesh, charId: id });
                roots.push(inst.bodyMesh);
            }
        });

        const intersects = state.raycaster.intersectObjects(roots, true);
        let newItem = null, newBoneName = null, hitBodyMesh = null;
        if (intersects.length > 0) {
            newItem = _findSubMeshForObject(intersects[0].object, targets);
            if (!newItem) {
                for (const bt of boneTargets) {
                    if (intersects[0].object === bt.bodyMesh) {
                        newBoneName = _getBoneFromIntersection(intersects[0], bt.bodyMesh);
                        hitBodyMesh = bt.bodyMesh;
                        break;
                    }
                }
            }
        }

        const label = newItem ? newItem.label : newBoneName;
        if (label && tooltip) {
            tooltip.textContent = label;
            tooltip.style.left = (e.clientX - rect.left + 14) + 'px';
            tooltip.style.top = (e.clientY - rect.top - 10) + 'px';
            tooltip.style.display = 'block';
            canvas.style.cursor = 'pointer';
        } else {
            if (tooltip) tooltip.style.display = 'none';
            canvas.style.cursor = '';
        }

        if (!_sameSubMesh(state._hoveredSubMesh, newItem)) {
            if (state._hoveredSubMesh && !_sameSubMesh(state._hoveredSubMesh, state._selectedSubMesh)) {
                _setSubMeshEmissive(state._hoveredSubMesh, state._ZERO_EMISSIVE);
            }
            state._hoveredSubMesh = newItem;
            if (state._hoveredSubMesh && !_sameSubMesh(state._hoveredSubMesh, state._selectedSubMesh)) {
                _setSubMeshEmissive(state._hoveredSubMesh, state._HOVER_EMISSIVE);
            }
        }

        if (state._hoveredBoneName !== newBoneName) {
            if (state._boneHoverOverlay) { _removeBoneOverlay(state._boneHoverOverlay); state._boneHoverOverlay = null; }
            state._hoveredBoneName = newBoneName;
            if (newBoneName && hitBodyMesh && newBoneName !== state._selectedBoneName) {
                state._boneHoverOverlay = _createBoneOverlay(hitBodyMesh, newBoneName, state._BONE_HOVER_MAT);
            }
        }
    }
}

// Register
fn.getSelectableSubMeshes = getSelectableSubMeshes;
fn._sameSubMesh = _sameSubMesh;
fn._setSubMeshEmissive = _setSubMeshEmissive;
fn._setBodyEmissive = _setBodyEmissive;
fn.clearSubMeshSelection = clearSubMeshSelection;
fn._removeSubMesh = _removeSubMesh;
fn._clearBoneHighlightCache = _clearBoneHighlightCache;
fn._clearBoneSelection = _clearBoneSelection;
fn._createBoneOverlay = _createBoneOverlay;
fn._removeBoneOverlay = _removeBoneOverlay;
fn.bindCanvasClick = bindCanvasClick;
fn.initSubMeshInteraction = initSubMeshInteraction;
