/**
 * Clips einer Spur: anlegen, laden, teilen, kuerzen, loeschen.
 *
 * Aus tracks.js herausgeloest (Umbau 15.08.2026).
 *
 * UMBAU 17.08.2026: 298 Zeilen, drei Themen. Jetzt:
 *
 *     clipanimation.js    Bewegung holen, Punkte in Knochennamen, Glättung
 *     clipbearbeitung.js  duplizieren, löschen, kürzen, teilen
 *
 * Hier bleibt das Anlegen eines Clips auf einer Spur und der Einstieg mit den
 * bisherigen Namen (`tracks.js`, `zeitleiste_*.js`, `theatre_*.js` importieren sie).
 */

import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Clip } from './models.js';
import { pushUndo } from './undo.js';
import { addTrack } from './tracks.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Clipanimation } from './clipanimation.js';
import { Clipbearbeitung } from './clipbearbeitung.js';

/**
 * Einen Bibliotheks-Clip auf eine Spur legen — hinter den letzten.
 *
 * Ohne Spur wird eine angelegt: Ein Doppelklick in der Bibliothek soll auch im
 * leeren Projekt etwas bewirken.
 */
export async function addClipToTrack(trackIdx, category, name, frames) {
    pushUndo('Clip hinzufügen');
    Protokoll.debug('BVH Studio',
                    `addClipToTrack: trackIdx=${trackIdx}, ${category}/${name}, `
                    + `existingTracks=${state.project.tracks.length}`);
    if (trackIdx < 0 || !state.project.tracks[trackIdx]) {
        if (state.project.tracks.length === 0) addTrack();
        trackIdx = state.project.tracks.length - 1;
    }
    const spur = state.project.tracks[trackIdx];
    if (!spur) {
        Protokoll.fehler('BVH Studio', 'addClipToTrack: keine Spur');
        return;
    }
    // Mixer zurücksetzen, damit der neue Clip von vorne läuft.
    if (spur.mixer) {
        spur.mixer.stopAllAction();
        spur._activeClip = null;
        spur._activeAction = null;
    }
    const clip = new Clip(category, name, frames || 3000, state.project.fps);
    const letzter = spur.clips[spur.clips.length - 1];
    clip.startFrame = letzter ? letzter.endFrame : 0;
    spur.clips.push(clip);
    if (spur.group) spur.group.visible = true;
    fn.updateDuration();
    fn.renderTimeline();
    await Clipanimation.laden(spur, clip);
    Protokoll.debug('BVH Studio',
                    `addClipToTrack done: clips=${spur.clips.length}, `
                    + `hasMixer=${!!spur.mixer}, hasSkeleton=${!!spur.skeleton}`);
    fn.updateProperties();
}

export async function loadClipAnimation(track, clip) {
    return Clipanimation.laden(track, clip);
}
export function buildClipFromData(data, skel) {
    return Clipanimation.bauen(data, skel);
}
export function _sanitizeBoneNames(skeleton) {
    Clipanimation.namenEntschaerfen(skeleton);
}

export function duplicateSelectedClip() { Clipbearbeitung.duplizieren(); }
export function deleteSelectedClip() { Clipbearbeitung.loeschen(); }
export function trimSelectedClip(mode, frames = 10) {
    Clipbearbeitung.kuerzen(mode, frames);
}
export function splitClipAtPlayhead() { Clipbearbeitung.teilen(); }
