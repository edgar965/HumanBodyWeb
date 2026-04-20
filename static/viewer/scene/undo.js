/**
 * Scene Editor -- Snapshot-based Undo/Redo system.
 *
 * Design: every mutation calls `markDirty()` AFTER it has applied.
 * We keep one rolling `_lastSnapshot` that always reflects the CURRENT state.
 * When markDirty fires, we push the previous snapshot (= state BEFORE the
 * mutation) onto the undo stack, then re-snapshot to capture the new current.
 * `captureInitial()` must be called once after scene load so the first
 * mutation has a valid pre-state to push.
 */
import { state } from './state.js';
import { fn } from './registry.js';

export const _undoStack = [];
export const _redoStack = [];
export const _UNDO_MAX = 20;
export let _undoSuppressed = false;
export let _undoInProgress = false;
let _lastSnapshot = null;

function _snapshot() {
    if (!fn.gatherSceneState) return null;
    try {
        return { data: fn.gatherSceneState(), selectedCharacterId: state.selectedCharacterId };
    } catch (e) {
        console.error('[Scene Undo] gather failed:', e);
        return null;
    }
}

export function captureInitial() {
    if (_undoSuppressed || _undoInProgress) return;
    _lastSnapshot = _snapshot();
    _undoStack.length = 0;
    _redoStack.length = 0;
}

export function markDirty(label) {
    if (_undoSuppressed || _undoInProgress) return;
    if (!fn.gatherSceneState) return;
    // Push the PRE-mutation snapshot (captured at previous markDirty / init) to undo
    if (_lastSnapshot) {
        _undoStack.push({ label: label || 'Aenderung', data: _lastSnapshot.data, selectedCharacterId: _lastSnapshot.selectedCharacterId });
        if (_undoStack.length > _UNDO_MAX) _undoStack.shift();
    }
    // Re-snapshot the now-current state for the next mutation
    _lastSnapshot = _snapshot();
    _redoStack.length = 0;
    state._sceneDirty = true;
}

export function markClean() {
    state._sceneDirty = false;
}

export function pushSceneUndo(label) { markDirty(label); }

export async function sceneUndo() {
    if (_undoInProgress || _undoStack.length === 0) return;
    _undoInProgress = true;
    if (_lastSnapshot) _redoStack.push(_lastSnapshot);
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
    _lastSnapshot = snap;
}

export async function sceneRedo() {
    if (_undoInProgress || _redoStack.length === 0) return;
    _undoInProgress = true;
    if (_lastSnapshot) _undoStack.push(_lastSnapshot);
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
    _lastSnapshot = snap;
}

window.__sceneUndo = sceneUndo;
window.__sceneRedo = sceneRedo;

fn.markDirty = markDirty;
fn.markClean = markClean;
fn.pushSceneUndo = pushSceneUndo;
fn.sceneUndo = sceneUndo;
fn.sceneRedo = sceneRedo;
fn.captureInitial = captureInitial;
