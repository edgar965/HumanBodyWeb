/**
 * scene_undo.js — Snapshot-based Undo/Redo system for the Scene Editor.
 */
import { state } from './scene_state.js?v=1';

// =========================================================================
// Undo/Redo stacks
// =========================================================================
export const _undoStack = [];
export const _redoStack = [];
export const _UNDO_MAX = 20;
export let _undoSuppressed = false;
export let _undoInProgress = false;

// Lazy references to avoid circular deps — set by scene_config.js at boot
let _gatherSceneState = null;
let _loadSceneFromData = null;
let _selectCharacter = null;

export function setUndoCallbacks({ gatherSceneState, loadSceneFromData, selectCharacter }) {
    _gatherSceneState = gatherSceneState;
    _loadSceneFromData = loadSceneFromData;
    _selectCharacter = selectCharacter;
}

// =========================================================================
// Dirty tracking
// =========================================================================
export function markDirty(label) {
    pushSceneUndo(label || 'Aenderung');
    state._sceneDirty = true;
}

export function markClean() {
    state._sceneDirty = false;
}

// =========================================================================
// Push / Undo / Redo
// =========================================================================
export function pushSceneUndo(label) {
    if (_undoSuppressed || _undoInProgress) return;
    try {
        const data = _gatherSceneState();
        _undoStack.push({ label, data, selectedCharacterId: state.selectedCharacterId });
        if (_undoStack.length > _UNDO_MAX) _undoStack.shift();
        _redoStack.length = 0;
        console.log(`[Scene Undo] push '${label}' (stack: ${_undoStack.length}, chars: ${data.characters?.length || 0})`);
    } catch (e) { console.error('[Scene Undo] Snapshot failed:', e); }
}

export async function sceneUndo() {
    console.log(`[Scene Undo] called. stack: ${_undoStack.length}, inProgress: ${_undoInProgress}`);
    if (_undoInProgress || _undoStack.length === 0) { console.log('[Scene Undo] nothing to undo'); return; }
    _undoInProgress = true;
    try {
        _redoStack.push({ label: 'redo', data: _gatherSceneState(), selectedCharacterId: state.selectedCharacterId });
    } catch (e) {}
    const snap = _undoStack.pop();
    _undoSuppressed = true;
    await _loadSceneFromData(snap.data, state.currentSceneName);
    _undoSuppressed = false;
    if (snap.selectedCharacterId && state.characters.has(snap.selectedCharacterId)) {
        _selectCharacter(snap.selectedCharacterId);
    }
    console.log(`[Scene Undo] Restored: ${snap.label} (${_undoStack.length} left)`);
    _undoInProgress = false;
}

export async function sceneRedo() {
    if (_undoInProgress || _redoStack.length === 0) return;
    _undoInProgress = true;
    _undoStack.push({ label: 'undo', data: _gatherSceneState(), selectedCharacterId: state.selectedCharacterId });
    const snap = _redoStack.pop();
    _undoSuppressed = true;
    await _loadSceneFromData(snap.data, state.currentSceneName);
    _undoSuppressed = false;
    if (snap.selectedCharacterId && state.characters.has(snap.selectedCharacterId)) {
        _selectCharacter(snap.selectedCharacterId);
    }
    console.log(`[Scene Redo] Restored (${_redoStack.length} left)`);
    _undoInProgress = false;
}

// Expose for onclick buttons
window.__sceneUndo = sceneUndo;
window.__sceneRedo = sceneRedo;
