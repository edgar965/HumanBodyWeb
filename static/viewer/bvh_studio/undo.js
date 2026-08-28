/**
 * BVH Studio — Undo/Redo system (snapshot-based, max 20 steps).
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Studiostand } from './studiostand.js';

export const undoStack = [];
export const redoStack = [];
const UNDO_MAX = 20;

export function pushUndo(label) {
    if (state._undoSuppressed) { Protokoll.debug('Undo', 'unterdrueckt:', label); return; }
    try {
        Protokoll.debug('Undo', `gemerkt: ${label} — ${state.project.tracks.length} Spuren`);
        undoStack.push(Studiostand.jetzt(label, state, fn));
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
        redoStack.push(Studiostand.jetzt('redo', state, fn));
    } catch (e) { Protokoll.warnung('Undo', 'Redo snapshot failed:', e); }
    const stand = undoStack.pop();
    await stand.herstellen(state, fn);
    fn.flashStudioInfo?.(`Undo: ${stand.label}`);
    Protokoll.info('Undo', `zurueckgenommen: ${snap.label} (${undoStack.length} verbleiben)`);
    state._undoInProgress = false;
}

export async function redo() {
    if (state._undoInProgress) return;
    if (redoStack.length === 0) { Protokoll.debug('Redo', 'nichts wiederherzustellen'); return; }
    state._undoInProgress = true;
    undoStack.push(Studiostand.jetzt('undo', state, fn));
    const stand = redoStack.pop();
    await stand.herstellen(state, fn);
    fn.flashStudioInfo?.(`Redo`);
    Protokoll.info('Redo', `wiederhergestellt (${redoStack.length} verbleiben)`);
    state._undoInProgress = false;
}
