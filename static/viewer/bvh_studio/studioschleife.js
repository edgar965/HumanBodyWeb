import { state } from './state.js';
import { renderTimeline } from './zeitleiste_zeichnen.js';
import { applyPlayhead, updatePlaybackUI,
         syncLightVisibility } from './playback.js';
import { updateDebugPanel } from './debug.js';

/**
 * Studioschleife — die Renderschleife des BVH-Studios.
 *
 * Aus `index.js animate()` herausgeloest (Umbau 16.08.2026). Der Kern bleibt
 * gleich: Beim Abspielen läuft der Abspielkopf mit der Bildrate weiter und
 * springt am Ende auf 0 zurück; ohne Abspielen wird nur die Sichtbarkeit der
 * Lichter nachgezogen.
 */
export class Studioschleife {

    /** Größter Zeitschritt — nach einem Tabwechsel sonst ein Sprung. */
    static MAX_SCHRITT_S = 0.1;

    starten() {
        const takt = () => {
            requestAnimationFrame(takt);
            this.schritt();
        };
        requestAnimationFrame(takt);
        return this;
    }

    schritt() {
        const dt = Math.min(state.clock.getDelta(), Studioschleife.MAX_SCHRITT_S);
        if (state.playing) this.abspielen(dt);
        else syncLightVisibility();
        if (!this.kameraspurAktiv()) state.controls.update();
        state.renderer.render(state.scene, state.camera);
        updateDebugPanel();
    }

    abspielen(dt) {
        const bilder = state.project.fps;
        state.playheadFrame += Math.round(dt * bilder * state.playbackSpeed);
        if (state.playheadFrame >= state.project.duration * bilder) {
            state.playheadFrame = 0;   // von vorn
        }
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
