import { state } from './state.js';
import { renderTimeline } from './zeitleiste_zeichnen.js';
import { applyPlayhead, updatePlaybackUI, syncLightVisibility,
         abspielende, pausePlayback } from './playback.js';
import { Abspielende } from './abspielende.js';
import { updateDebugPanel } from './debug.js';
import { Zeichenschleife } from '../gemeinsam/zeichenschleife.js';
import { Figurmarkierung } from './figurmarkierung.js';

/**
 * Studioschleife — die Renderschleife des BVH-Studios.
 *
 * Aus `index.js animate()` herausgeloest (Umbau 16.08.2026). Der Kern bleibt
 * gleich: Beim Abspielen läuft der Abspielkopf mit der Bildrate weiter; am
 * Ende der letzten Animation hält er an oder springt mit „Endlos" auf 0
 * (`Abspielende`, 11.09.2026 — vorher immer auf 0, und erst am Ende der
 * Projektdauer). Ohne Abspielen wird nur die Sichtbarkeit der Lichter
 * nachgezogen.
 */
export class Studioschleife extends Zeichenschleife {

    /** Größter Zeitschritt — nach einem Tabwechsel sonst ein Sprung. */
    static MAX_SCHRITT_S = 0.1;

    schritt() {
        const dt = Math.min(state.clock.getDelta(), Studioschleife.MAX_SCHRITT_S);
        if (state.playing) this.abspielen(dt);
        else syncLightVisibility();
        if (!this.kameraspurAktiv()) state.controls.update();
        Figurmarkierung.nachziehen();   // Rahmen um die gewählte Figur
        state.renderer.render(state.scene, state.camera);
        updateDebugPanel();
    }

    abspielen(dt) {
        const bilder = state.project.fps;
        state.playheadFrame += Math.round(dt * bilder * state.playbackSpeed);
        const naechstes = Abspielende.naechstes(state.playheadFrame, abspielende(), state.endlos);
        state.playheadFrame = naechstes.bild;
        if (naechstes.anhalten) pausePlayback();
        applyPlayhead();
        renderTimeline();
        updatePlaybackUI();
    }

    /**
     * Treibt eine Kameraspur die Kamera, würde `controls.update()` die
     * berechnete Lage überschreiben — dann bleibt die Steuerung stehen.
     */
    kameraspurAktiv() {
        return state.playing && state.project.tracks.some(
            spur => spur.type === 'camera' && spur.cameraActive
                    && (spur.clips?.length || 0) > 0);
    }
}
