/**
 * BVH Studio — Undo/Redo system (snapshot-based, max 20 steps).
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

export const undoStack = [];
export const redoStack = [];
const UNDO_MAX = 20;

export function pushUndo(label) {
    if (state._undoSuppressed) { Protokoll.debug('Undo', 'unterdrueckt:', label); return; }
    try {
        Protokoll.debug('Undo', `gemerkt: ${label} — ${state.project.tracks.length} Spuren`);
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
        Protokoll.warnung('Undo', 'Snapshot failed:', e);
    }
}

export async function undo() {
    if (state._undoInProgress) { Protokoll.debug('Undo', 'laeuft schon'); return; }
    if (undoStack.length === 0) { Protokoll.debug('Undo', 'nichts zurueckzunehmen'); return; }
    state._undoInProgress = true;
    Protokoll.debug('Undo', `beginnt — ${undoStack.length} Schritte, oben: ${undoStack[undoStack.length - 1].label}`);
    // Save current state to redo
    try {
        redoStack.push({
            label: 'redo',
            data: fn.buildProjectData(),
            playheadFrame: state.playheadFrame,
            selectedTrackIdx: state.selectedTrackIdx,
            selectedClipIdx: state.selectedClipIdx,
        });
    } catch (e) { Protokoll.warnung('Undo', 'Redo snapshot failed:', e); }
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
    Protokoll.info('Undo', `zurueckgenommen: ${snap.label} (${undoStack.length} verbleiben)`);
    state._undoInProgress = false;
}

export async function redo() {
    if (state._undoInProgress) return;
    if (redoStack.length === 0) { Protokoll.debug('Redo', 'nichts wiederherzustellen'); return; }
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
    Protokoll.info('Redo', `wiederhergestellt (${redoStack.length} verbleiben)`);
    state._undoInProgress = false;
}
