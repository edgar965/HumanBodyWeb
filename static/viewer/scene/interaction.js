/**
 * Scene Editor -- Canvas click, raycasting, sub-mesh hover/select logic.
 */
import './state.js';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import './undo.js';
import { _clearBoneHighlightCache, _clearBoneSelection, _createBoneOverlay, _getBoneFromIntersection, _removeBoneOverlay } from './knochenmarkierung.js';
import { _doSubMeshClick, _findSubMeshForObject, _removeSubMesh, _sameSubMesh, _setBodyEmissive, _setSubMeshEmissive, clearSubMeshSelection, getSelectableSubMeshes } from './teilnetz_auswahl.js';
import { Schwebeanzeige } from './schwebeanzeige.js';

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
                if (child.isMesh && !child.userData._boneOverlay) {
                    child.userData._parentCharId = id;
                    meshes.push(child);
                }
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
                        if (state.selectedCharacterId !== charId) {
                            clearSubMeshSelection();
                            fn.selectCharacter(charId);
                        }
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

/**
 * Was unter dem Zeiger liegt, zeigt `Schwebeanzeige` (Umbau 27.08.2026, Befund
 * `jsfunktionen`: `initSubMeshInteraction()` hatte 91 Zeilen).
 */
export function initSubMeshInteraction() {
    new Schwebeanzeige(state.canvas);
}

// Register
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
