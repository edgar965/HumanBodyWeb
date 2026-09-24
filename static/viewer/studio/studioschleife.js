import { state, HEADER_WIDTH } from './state.js';
import { Zeitleistenfolge } from './zeitleiste_folgen.js';
import { Bildtakt } from './bildtakt.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';
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
 * gleich: Beim Abspielen läuft der Abspielkopf mit der Bildrate weiter
 * (`Bildtakt` führt den Bruchteil mit — die Rundung je Schritt band das
 * Tempo an den Monitor, 13.09.2026); am
 * Ende der letzten Animation hält er an oder springt mit „Endlos" auf 0
 * (`Abspielende`, 11.09.2026 — vorher immer auf 0, und erst am Ende der
 * Projektdauer). Die Zeitleiste blättert mit, sobald der Kopf den sichtbaren
 * Bereich verlässt (`Zeitleistenfolge`, 13.09.2026). Ohne Abspielen wird
 * nur die Sichtbarkeit der Lichter nachgezogen.
 */
export class Studioschleife extends Zeichenschleife {

    /** Größter Zeitschritt — nach einem Tabwechsel sonst ein Sprung. */
    static MAX_SCHRITT_S = 0.1;

    /** Bruchteile eines Bildes zwischen zwei Schritten. */
    takt = new Bildtakt();

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
        state.playheadFrame += this.takt.bilder(dt, state.project.fps, state.playbackSpeed);
        const naechstes = Abspielende.naechstes(state.playheadFrame, abspielende(), state.endlos);
        state.playheadFrame = naechstes.bild;
        if (naechstes.anhalten) pausePlayback();
        applyPlayhead();
        Zeitleistenfolge.nachziehen(state, Zeitleistenflaeche.breite - HEADER_WIDTH);
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
