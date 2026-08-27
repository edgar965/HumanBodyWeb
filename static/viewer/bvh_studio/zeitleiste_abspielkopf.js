import { state, HEADER_WIDTH } from './state.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';

/**
 * Der Abspielkopf der Zeitleiste — rote Linie mit Griff, dazu die Bildanzeige
 * unter der Leiste.
 *
 * Aus zeitleiste_zeichnen.js herausgelöst (Umbau 27.08.2026, Befund
 * `jsfunktionen`).
 */
export class Abspielkopf {
    /** Halbe Breite des Griffs in Pixeln. */
    static GRIFF_BREITE = 6;
    /** Höhe des Griffs in Pixeln. */
    static GRIFF_HOEHE = 10;

    /**
     * @param {number} hoehe Leinwandhöhe
     * @param {number} pps Pixel je Sekunde
     */
    static zeichnen(hoehe, pps) {
        const x = HEADER_WIDTH
            + (state.playheadFrame / state.project.fps) * pps
            - state.timelineScrollX;
        // Links von der Kopfspalte ist der Kopf herausgescrollt.
        if (x < HEADER_WIDTH) return;
        const ctx = Zeitleistenflaeche.ctx;
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, hoehe);
        ctx.stroke();
        ctx.fillStyle = '#ef4444';
        ctx.beginPath();
        ctx.moveTo(x - Abspielkopf.GRIFF_BREITE, 0);
        ctx.lineTo(x + Abspielkopf.GRIFF_BREITE, 0);
        ctx.lineTo(x, Abspielkopf.GRIFF_HOEHE);
        ctx.fill();
    }

    /** „Bild 42 / 300" unter der Leiste. */
    static bildanzeige() {
        const anzeige = document.getElementById('tl-frame-info');
        if (!anzeige) return;
        const gesamt = Math.round(state.project.duration * state.project.fps);
        anzeige.textContent = `Frame ${state.playheadFrame} / ${gesamt}`;
    }
}
