/**
 * BVH Studio — Undo/Redo system (snapshot-based, max 20 steps).
 */
import { state } from './state.js';
import { fn } from './registry.js';

export const undoStack = [];
export const redoStack = [];
const UNDO_MAX = 20;

export function pushUndo(label) {
    if (state._undoSuppressed) { console.log(`[Undo] SUPPRESSED: ${label}`); return; }
    try {
        console.log(`[Undo] pushUndo('${label}') — tracks: ${state.project.tracks.length}, clips: ${state.project.tracks.map(t=>t.clips.length)}`);
        const snapshot = {
            label,
            data: fn.buildProjectData(),
            playheadFrame: state.playheadFrame,
            selectedTrackIdx: state.selectedTrackIdx,
            selectedClipIdx: state.selectedClipIdx,
        };
        undoStack.push(snapshot);
        if (undoStack.length > UNDO_MAX) undoStack.shift();
        redoStack.length = 0;
    } catch (e) {
        console.warn('[Undo] Snapshot failed:', e);
    }
}

export async function undo() {
    if (state._undoInProgress) { console.log('[Undo] Already in progress, skip.'); return; }
    if (undoStack.length === 0) { console.log('[Undo] Nothing to undo. Stack empty.'); return; }
    state._undoInProgress = true;
    console.log(`[Undo] Starting. Stack size: ${undoStack.length}, top label: ${undoStack[undoStack.length-1].label}, tracks in snapshot: ${undoStack[undoStack.length-1].data.tracks?.length}`);
    // Save current state to redo
    try {
        redoStack.push({
            label: 'redo',
            data: fn.buildProjectData(),
            playheadFrame: state.playheadFrame,
            selectedTrackIdx: state.selectedTrackIdx,
            selectedClipIdx: state.selectedClipIdx,
        });
    } catch (e) { console.warn('[Undo] Redo snapshot failed:', e); }
    const snap = undoStack.pop();
    await fn.restoreProjectData(snap.data);
    state.playheadFrame = snap.playheadFrame || 0;
    state.selectedTrackIdx = snap.selectedTrackIdx ?? -1;
    state.selectedClipIdx = snap.selectedClipIdx ?? -1;
    fn.applyPlayhead();
    fn.renderTimeline();
    fn.updatePlaybackUI();
    fn.updateProperties();
    fn.flashStudioInfo?.(`Undo: ${snap.label}`);
    console.log(`[Undo] Restored: ${snap.label} (${undoStack.length} left)`);
    state._undoInProgress = false;
}

export async function redo() {
    if (state._undoInProgress) return;
    if (redoStack.length === 0) { console.log('[Redo] Nothing to redo'); return; }
    state._undoInProgress = true;
    undoStack.push({
        label: 'undo',
        data: fn.buildProjectData(),
        playheadFrame: state.playheadFrame,
        selectedTrackIdx: state.selectedTrackIdx,
        selectedClipIdx: state.selectedClipIdx,
    });
    const snap = redoStack.pop();
    await fn.restoreProjectData(snap.data);
    state.playheadFrame = snap.playheadFrame || 0;
    state.selectedTrackIdx = snap.selectedTrackIdx ?? -1;
    state.selectedClipIdx = snap.selectedClipIdx ?? -1;
    fn.applyPlayhead();
    fn.renderTimeline();
    fn.updatePlaybackUI();
    fn.updateProperties();
    fn.flashStudioInfo?.(`Redo`);
    console.log(`[Redo] Restored (${redoStack.length} left)`);
    state._undoInProgress = false;
}
