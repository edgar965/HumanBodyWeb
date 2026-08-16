/**
 * Scene Editor -- Canvas click, raycasting, sub-mesh hover/select logic.
 */
import './state.js';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import './undo.js';
import { _clearBoneHighlightCache, _clearBoneHover, _clearBoneSelection, _createBoneOverlay, _getBoneFromIntersection, _removeBoneOverlay } from './knochenmarkierung.js';
import { _doSubMeshClick, _findSubMeshForObject, _removeSubMesh, _sameSubMesh, _setBodyEmissive, _setSubMeshEmissive, clearSubMeshSelection, getAllSubMeshTargets, getSelectableSubMeshes } from './teilnetz_auswahl.js';


















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
