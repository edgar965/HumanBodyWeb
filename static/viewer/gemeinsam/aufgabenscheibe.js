import { Texturweg } from './texturweg.js';

/**
 * Aufgabenscheibe — eine lange Liste in Scheiben bauen, jede in einer eigenen Aufgabe des Browsers (24.11.2026).
 *
 * Edgar, 24.11.2026: „EdgarNeu laden im Charakter dauert ewig, das muss in 2 s laden“: Die Reglerliste (2.406 Zeilen) hielt den Hauptfaden 334–610 ms an einem Stück an. In Scheiben
 * kostet sie dasselbe, aber dazwischen zeichnet die Seite und nimmt Eingaben an.
 *
 *     const scheibe = new Aufgabenscheibe();
 *     for (const x of liste) {
 *         bauen(x);
 *         if (scheibe.voll) { await scheibe.weiter(); if (veraltet()) return; }
 *     }
 */
export class Aufgabenscheibe {

    static MS = 12;

    constructor(ms = Aufgabenscheibe.MS) {
        this.ms = ms;
        this.beginn = performance.now();
    }

    /** Hat diese Aufgabe genug gearbeitet? */
    get voll() {
        return performance.now() - this.beginn > this.ms;
    }

    /** In einer neuen Aufgabe weiter. */
    async weiter() {
        await Texturweg.naechsteAufgabe();
        this.beginn = performance.now();
    }
}
