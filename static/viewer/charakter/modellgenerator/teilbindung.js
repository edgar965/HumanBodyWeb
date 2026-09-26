import { Modellbauzustand } from './zustand.js';

/**
 * Teilbindung — ein Bedienelement an das GEWÄHLTE Modellteil hängen.
 *
 * WARUM DIESES MODUL (28.08.2026, Befund `doppelcode`): Diese vier Zeilen
 *
 *     const feld = document.getElementById(id);
 *     if (!feld) return;
 *     feld.addEventListener(…, () => {
 *         const teil = Modellbauzustand.teil();
 *         if (!teil) return;
 *
 * standen im Modellgenerator NEUNMAL — in `formregler.js` einmal, in
 * `knochenregler.js` achtmal (Schieber, Schalter, Vektoren, Farbe, Form,
 * Kleidung, Textur setzen, Textur löschen).
 *
 * BEIDE PRÜFUNGEN SIND NÖTIG, und beide sind leicht zu vergessen:
 *
 * * **Das Element** gibt es nicht auf jeder Seite — der Modellgenerator ist
 *   ein Bereich der Szenenseite, und nicht jede Vorlage bringt jedes Feld mit.
 *   Ohne die Prüfung wirft `addEventListener` auf `null`, und das Modul bricht
 *   beim Laden ab: ALLE Regler dahinter sind dann tot, nicht nur der eine.
 * * **Das Teil** ist null, solange nichts gewählt ist. Ohne die Prüfung
 *   schreibt der erste Reglerzug in ein `undefined` — eine Ausnahme mitten im
 *   Ereignis, die niemand sieht.
 *
 * Die ANZEIGE bleibt Sache des Aufrufers: Die Tabellen im Modellgenerator
 * formatieren unterschiedlich (`toFixed(stellen)` gegen `String(v)` bei null
 * Nachkommastellen), und das hier zu vereinheitlichen wäre eine stille
 * Änderung an dem, was auf dem Bildschirm steht.
 */
export class Teilbindung {

    /**
     * Ein Ereignis binden, das nur mit gewähltem Teil etwas tut.
     *
     * @param id Kennung des Elements
     * @param ereignis 'input', 'change', 'click', …
     * @param tun (teil, element) => void
     * @returns das Element — oder null, wenn es die Seite nicht hat
     */
    static an(id, ereignis, tun) {
        const feld = document.getElementById(id);
        if (!feld) return null;
        feld.addEventListener(ereignis, () => {
            const teil = Modellbauzustand.teil();
            if (!teil) return;
            tun(teil, feld);
        });
        return feld;
    }

    /**
     * Ein Schieberegler mit Anzeigefeld (`<id>-val`).
     *
     * Die Anzeige wird IMMER aufgefrischt, auch ohne gewähltes Teil: Der
     * Regler hat sich ja bewegt, und eine Zahl, die dann stehenbleibt, sieht
     * aus wie ein hängender Regler.
     *
     * @param id Kennung des Reglers
     * @param anzeigen (wert) => string — wie die Zahl darzustellen ist
     * @param tun (teil, wert) => void
     */
    static regler(id, anzeigen, tun) {
        const regler = document.getElementById(id);
        if (!regler) return null;
        const anzeige = document.getElementById(id + '-val');
        regler.addEventListener('input', () => {
            const wert = parseFloat(regler.value);
            if (anzeige) anzeige.textContent = anzeigen(wert);
            const teil = Modellbauzustand.teil();
            if (!teil) return;
            tun(teil, wert);
        });
        return regler;
    }
}
