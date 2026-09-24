import { state, HEADER_WIDTH, RULER_HEIGHT } from './state.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';

/**
 * Das Lineal am oberen Rand der Zeitleiste — Grundstreifen und Sekundenmarken.
 *
 * Aus zeitleiste_zeichnen.js herausgelöst (Umbau 27.08.2026, Befund
 * `jsfunktionen`: `renderTimeline()` hatte 95 Zeilen).
 *
 * SEIT 11.09.2026 BLEIBT ES SICHTBAR, seit 13.09.2026 ohne Nachziehen: Es hat
 * eine eigene Leinwand (`Zeitleistenflaeche.lineal`, `position: sticky`),
 * die der Browser am oberen Rand des Rahmens hält — die Spurenleinwand
 * läuft darunter durch. Vorher wurde es um `scrollTop` versetzt auf die
 * Spurenleinwand gezeichnet und hing beim Blättern einen Bildaufbau nach.
 */
export class Zeitleistenlineal {
    /** Angestrebter Abstand zweier Marken in Pixeln. */
    static MARKENABSTAND = 50;
    /** So weit über das Projektende hinaus wird noch beschriftet. */
    static UEBERHANG_S = 10;

    /**
     * @param {number} breite Leinwandbreite
     * @param {number} pps Pixel je Sekunde beim aktuellen Zoom
     */
    static zeichnen(breite, pps) {
        const ctx = Zeitleistenflaeche.linealCtx;
        if (!ctx) return;
        ctx.clearRect(0, 0, breite, RULER_HEIGHT);
        Zeitleistenlineal._streifen(ctx, breite, pps);
    }

    static _streifen(ctx, breite, pps) {
        ctx.fillStyle = '#1a1a2e';
        ctx.fillRect(0, 0, breite, RULER_HEIGHT);
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, RULER_HEIGHT);
        ctx.lineTo(breite, RULER_HEIGHT);
        ctx.stroke();
        Zeitleistenlineal._marken(ctx, breite, pps);
    }

    static _marken(ctx, breite, pps) {
        ctx.fillStyle = '#64748b';
        ctx.font = '10px monospace';
        // Bei starkem Herauszoomen sonst eine Marke je Pixel.
        const schritt = Math.max(
            1, Math.floor(Zeitleistenlineal.MARKENABSTAND / pps));
        const ende = state.project.duration + Zeitleistenlineal.UEBERHANG_S;
        for (let s = 0; s < ende; s += schritt) {
            const x = HEADER_WIDTH + s * pps - state.timelineScrollX;
            if (x < HEADER_WIDTH || x > breite) continue;
            ctx.fillText(`${s}s`, x + 2, 12);
            ctx.beginPath();
            ctx.moveTo(x, 14);
            ctx.lineTo(x, RULER_HEIGHT);
            ctx.stroke();
        }
    }
}
