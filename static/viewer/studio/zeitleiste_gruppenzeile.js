import { TRACK_HEIGHT } from './state.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';
import { Gruppenkopf } from './zeitleiste_gruppenkopf.js';

/**
 * Die Gruppenzeile auf der Zeitleisten-Leinwand — das Gegenstück zu
 * `Gruppenkopf` in der Kopfspalte.
 *
 * Die Farben kommen aus `Gruppenkopf.farben()`: Bis zum 27.08.2026 standen
 * dieselben vier RGBA-Werte in beiden Dateien, und ein Farbwechsel hätte die
 * Leinwand gegen die Kopfspalte verschoben.
 *
 * Aus zeitleiste_zeichnen.js herausgelöst (Umbau 27.08.2026, Befund
 * `jsfunktionen`).
 */
export class Gruppenzeile {
    /**
     * @param {{header: string, label: string, collapsed: boolean}} reihe
     * @param {number} y obere Kante der Zeile
     * @param {number} breite Leinwandbreite
     */
    static zeichnen(reihe, y, breite) {
        const farben = Gruppenkopf.farben(reihe.header);
        const ctx = Zeitleistenflaeche.ctx;
        ctx.fillStyle = farben.grund;
        ctx.fillRect(0, y, breite, TRACK_HEIGHT);
        ctx.strokeStyle = farben.rand;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(breite, y);
        ctx.moveTo(0, y + TRACK_HEIGHT);
        ctx.lineTo(breite, y + TRACK_HEIGHT);
        ctx.stroke();
        ctx.fillStyle = farben.schrift;
        ctx.font = 'bold 11px sans-serif';
        ctx.textBaseline = 'middle';
        const pfeil = reihe.collapsed ? '▶' : '▼';
        ctx.fillText(`${pfeil} ${reihe.label}`, 8, y + TRACK_HEIGHT / 2 + 1);
        // Zurücksetzen — die Klipbeschriftungen darunter rechnen mit der
        // Grundlinie.
        ctx.textBaseline = 'alphabetic';
    }
}
