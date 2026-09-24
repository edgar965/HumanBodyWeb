/**
 * Zeitleistenflaeche — die Leinwand der Zeitleiste und ihr Zeichenkontext.
 *
 * WARUM (Umbau 15.08.2026): `let tlCanvas, tlCtx;` waren Modulvariablen in
 * timeline.js. Beim Aufteilen der Datei blieben sie dort, waehrend das Zeichnen
 * und die Kopfspalte in eigene Module wanderten — `ReferenceError: tlCtx is not
 * defined` beim ersten Aufbau der Seite. Geteilter Zustand braucht einen
 * eigenen Ort, sonst entscheidet der Zufall, welches Modul ihn behaelt.
 */

export class Zeitleistenflaeche {
    static canvas = null;
    static ctx = null;
    /** Die klebende Lineal-Leinwand über den Spuren (13.09.2026). */
    static lineal = null;
    static linealCtx = null;

    /** Beim Aufbau der Zeitleiste einmal setzen. */
    static setzen(canvas, lineal = null) {
        this.canvas = canvas;
        this.ctx = canvas ? canvas.getContext('2d') : null;
        this.lineal = lineal;
        this.linealCtx = lineal ? lineal.getContext('2d') : null;
        return this.ctx;
    }

    /** Der scrollbare Rahmen um die Leinwand. */
    static get rahmen() {
        return this.canvas ? this.canvas.parentElement : null;
    }

    static get bereit() {
        return !!(this.canvas && this.ctx);
    }

    /**
     * Wie weit der Rahmen nach unten geblättert ist. Leinwand-y = sichtbares
     * y + `oben`; darunter (die ersten RULER_HEIGHT sichtbaren Pixel) liegt
     * die klebende Lineal-Leinwand, dort wird gescrubbt statt geklickt.
     */
    static get oben() {
        return this.rahmen ? this.rahmen.scrollTop : 0;
    }

    static get breite() {
        return this.canvas ? this.canvas.width : 0;
    }

    static get hoehe() {
        return this.canvas ? this.canvas.height : 0;
    }

    /** Hoehe der Leinwand anpassen — der Inhalt wird dabei geloescht. */
    static hoeheSetzen(hoehe) {
        if (this.canvas && this.canvas.height !== hoehe) this.canvas.height = hoehe;
    }
}
