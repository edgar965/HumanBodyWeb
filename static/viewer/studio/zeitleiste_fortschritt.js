import { state, HEADER_WIDTH } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Abspielende } from './abspielende.js';
import { Fortschrittsmass } from './fortschrittsmass.js';
import { Zeitleistenfolge } from './zeitleiste_folgen.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';
import { formatTime } from './playback.js';

/**
 * Fortschrittsbalken — unter allen Spuren, immer sichtbar, über die ganze
 * Abspieldauer; Klick oder Ziehen setzt den Abspielkopf.
 *
 * WARUM (Edgar, 13.09.2026: „Unten, unterhalb aller Balken mach einen
 * Play-Fortschrittsbalken, auch immer sichtbar, mit Möglichkeit, die
 * Play-Position zu verschieben"): Die Zeitleiste zeigt beim Zoom 100 nur
 * wenige Sekunden, und wer senkrecht blättert, sieht den Kopf nicht. Der
 * Balken liegt AUSSERHALB des scrollenden Rahmens (eigene Leinwand
 * `#timeline-fortschritt`), sein Bezug ist das Abspielende (`Abspielende.bild`
 * — die letzte Bewegung, sonst die Projektdauer). Nach dem Setzen blättert die
 * Zeitleiste zum Kopf (`Zeitleistenfolge`).
 */
export class Fortschrittsbalken {
    /** Höhe der Leinwand in Pixeln. */
    static HOEHE = 18;
    /** Abstand des Balkens vom rechten Rand und von der Kopfspalte. */
    static RAND = 8;
    /** Dicke der Spur und Halbmesser des Griffs. */
    static DICKE = 4;
    static GRIFF = 5;

    static canvas = null;
    static ziehend = false;

    static anbinden(canvas) {
        Fortschrittsbalken.canvas = canvas;
        if (!canvas) return;
        canvas.height = Fortschrittsbalken.HOEHE;
        canvas.addEventListener('mousedown', (e) => {
            if (e.button !== 0) return;
            Fortschrittsbalken.ziehend = true;
            Fortschrittsbalken._setzen(e.clientX);
            e.preventDefault();
        });
        document.addEventListener('mousemove', (e) => {
            if (Fortschrittsbalken.ziehend) Fortschrittsbalken._setzen(e.clientX);
        });
        document.addEventListener('mouseup', () => { Fortschrittsbalken.ziehend = false; });
    }

    /** Breite an den Rahmen anpassen (bei jeder Größenänderung). */
    static breiteSetzen(breite) {
        if (Fortschrittsbalken.canvas) Fortschrittsbalken.canvas.width = breite;
    }

    static get ende() {
        return Abspielende.bild(state.project.tracks, state.project.fps, state.project.duration);
    }

    /** Linker Rand und Breite des Balkens in Leinwandpixeln. */
    static _lage() {
        const links = HEADER_WIDTH + Fortschrittsbalken.RAND;
        const breite = Fortschrittsbalken.canvas.width - links - Fortschrittsbalken.RAND;
        return { links, breite };
    }

    static zeichnen() {
        const canvas = Fortschrittsbalken.canvas;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const { links, breite } = Fortschrittsbalken._lage();
        const mitte = Fortschrittsbalken.HOEHE / 2;
        const ende = Fortschrittsbalken.ende;
        const anteil = Fortschrittsmass.anteil(state.playheadFrame, ende);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        // Zeit links, wo die Kopfspalte ist: Stand / Ende.
        ctx.fillStyle = '#94a3b8';
        ctx.font = '10px monospace';
        ctx.textBaseline = 'middle';
        ctx.fillText(`${formatTime(state.playheadFrame / state.project.fps)} / `
                     + formatTime(ende / state.project.fps), Fortschrittsbalken.RAND, mitte);
        if (breite <= 0) return;
        ctx.fillStyle = '#334155';
        ctx.fillRect(links, mitte - Fortschrittsbalken.DICKE / 2, breite, Fortschrittsbalken.DICKE);
        ctx.fillStyle = '#ef4444';
        ctx.fillRect(links, mitte - Fortschrittsbalken.DICKE / 2, breite * anteil,
                     Fortschrittsbalken.DICKE);
        ctx.beginPath();
        ctx.arc(links + breite * anteil, mitte, Fortschrittsbalken.GRIFF, 0, Math.PI * 2);
        ctx.fill();
    }

    /** Abspielkopf auf die Bildschirmstelle setzen und die Zeitleiste dorthin blättern. */
    static _setzen(clientX) {
        const { links, breite } = Fortschrittsbalken._lage();
        const x = clientX - Fortschrittsbalken.canvas.getBoundingClientRect().left - links;
        state.playheadFrame = Fortschrittsmass.bild(x, breite, Fortschrittsbalken.ende);
        Zeitleistenfolge.nachziehen(state, Zeitleistenflaeche.breite - HEADER_WIDTH);
        fn.applyPlayhead();
        fn.renderTimeline();
        fn.updatePlaybackUI();
    }
}
