/**
 * Lichtspuren: Anzeiger, Helfer, Schluesselbilder, Szenenlichter.
 *
 * Aus tracks.js herausgeloest (Umbau 15.08.2026): rund 300 der 1115 Zeilen
 * drehten sich um Licht — vom Kegelanzeiger bis zum Uebernehmen gespeicherter
 * Lichtwerte. Wer eine Clipfunktion sucht, muss das nicht durchblaettern.
 *
 * UMBAU 17.08.2026: Die Datei hatte 321 Zeilen und drei Themen, darunter DREI
 * fast gleiche Keyframe-Bauer. Jetzt ist sie der Einstieg:
 *
 *     lichtanzeiger.js    Form und Helferlinien je Lichtart (Geometrie)
 *     lichtschluessel.js  EIN Keyframe-Bauer, drei Anlegewege
 *     szenenlichter.js    die vier Lichter der Grundszene als Spuren
 *
 * Die Exportnamen bleiben: `tracks.js`, `studiostart.js`, `theatre_lichtspuren.js`
 * und `eigenschaften/licht.js` importieren sie.
 */

import { Lichtanzeiger } from './lichtanzeiger.js';
import { Lichtschluessel } from './lichtschluessel.js';
import { Szenenlichter } from './szenenlichter.js';

export const _LIGHT_SHAPE_HEIGHT = Lichtanzeiger.HOEHE;

export function _buildLightIndicator(light) { return Lichtanzeiger.form(light); }
export function createLightHelper(light) { return Lichtanzeiger.helfer(light); }
export function detectLightType(light) { return Lichtanzeiger.art(light); }

export function addStandardLightKeyframes(track) {
    Lichtschluessel.standardpaar(track);
}
export function _addStandardKeyframe(track) {
    Lichtschluessel.standardpaar(track);
}
export function addLightKeyframe(trackIdx, frame) {
    Lichtschluessel.einzeln(trackIdx, frame);
}
export function addLightKeyframePair(trackIdx, frame) {
    Lichtschluessel.paar(trackIdx, frame);
}

export function applySceneLightOverrides(overrides) {
    Szenenlichter.uebernehmen(overrides);
}
export function createSceneLightTracks() {
    Szenenlichter.spurenAnlegen();
}
