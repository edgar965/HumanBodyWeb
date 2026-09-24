import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';

/**
 * Schluesseltasten — K (Kameraposition setzen) und L (Licht setzen) global.
 *
 * Bis 24.09.2026 wirkten beide Tasten nur, wenn die Kamera- bzw. Lichtspur
 * gerade ausgewählt war (Edgar: „ich möchte die globalen Tasten haben für K …
 * sowie L"). Jetzt:
 *
 * * K: die gewählte Kameraspur; sonst die, die beim Abspielen die Kamera führt
 *   (`cameraActive`, erste gewinnt — wie in `applyPlayhead`); sonst die erste.
 * * L: `Lichtschluessel.einzeln` setzt ohnehin für ALLE Lichtspuren einen
 *   Keyframe (23.09.2026) — die Spurnummer muss nur irgendeine Lichtspur sein.
 */
export class Schluesseltasten {

    static kamera() {
        const spuren = state.project.tracks;
        let index = Schluesseltasten._gewaehlt('camera');
        if (index < 0) index = spuren.findIndex(s => s.type === 'camera' && s.cameraActive);
        if (index < 0) index = spuren.findIndex(s => s.type === 'camera');
        if (index >= 0) fn.addCameraKeyframe(index);
    }

    static licht() {
        let index = Schluesseltasten._gewaehlt('light');
        if (index < 0) index = state.project.tracks.findIndex(s => s.type === 'light' && s.light);
        if (index >= 0) fn.addLightKeyframe(index);
    }

    static _gewaehlt(art) {
        const index = state.selectedTrackIdx;
        return state.project.tracks[index]?.type === art ? index : -1;
    }
}
