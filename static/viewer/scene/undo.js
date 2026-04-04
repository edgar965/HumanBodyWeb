/**
 * Scene Editor -- Snapshot-based Undo/Redo system.
 */
import { state } from './state.js';
import { fn } from './registry.js';

// =========================================================================
// Undo/Redo stacks
// =========================================================================
export const _undoStack = [];
export const _redoStack = [];
export const _UNDO_MAX = 20;
export let _undoSuppressed = false;
export let _undoInProgress = false;

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
    if (!fn.gatherSceneState) return;
    try {
        const data = fn.gatherSceneState();
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
        _redoStack.push({ label: 'redo', data: fn.gatherSceneState(), selectedCharacterId: state.selectedCharacterId });
    } catch (e) {}
    const snap = _undoStack.pop();
    _undoSuppressed = true;
    try {
        await fn.loadSceneFromData(snap.data, snap.data.name || '');
        if (snap.selectedCharacterId && state.characters.has(snap.selectedCharacterId)) {
            fn.selectCharacter(snap.selectedCharacterId);
        }
    } catch (e) { console.error('[Scene Undo] Restore failed:', e); }
    _undoSuppressed = false;
    _undoInProgress = false;
}

export async function sceneRedo() {
    if (_undoInProgress || _redoStack.length === 0) return;
    _undoInProgress = true;
    try {
        _undoStack.push({ label: 'redo-back', data: fn.gatherSceneState(), selectedCharacterId: state.selectedCharacterId });
    } catch (e) {}
    const snap = _redoStack.pop();
    _undoSuppressed = true;
    try {
        await fn.loadSceneFromData(snap.data, snap.data.name || '');
        if (snap.selectedCharacterId && state.characters.has(snap.selectedCharacterId)) {
            fn.selectCharacter(snap.selectedCharacterId);
        }
    } catch (e) { console.error('[Scene Redo] Restore failed:', e); }
    _undoSuppressed = false;
    _undoInProgress = false;
}

// Expose on window for global keyboard shortcut
window.__sceneUndo = sceneUndo;
window.__sceneRedo = sceneRedo;

// Register in fn
fn.markDirty = markDirty;
fn.markClean = markClean;
fn.pushSceneUndo = pushSceneUndo;
fn.sceneUndo = sceneUndo;
fn.sceneRedo = sceneRedo;
