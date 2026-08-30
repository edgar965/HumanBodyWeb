/**
 * Kategoriewahl — ein Auswahlfeld mit Kategorienamen füllen.
 *
 * WARUM (Befund `doppelcode`, 30.08.2026): Dieselbe Schleife stand in
 * `viewer/kleiderpakete.js` und `viewer/smpl_kleiderliste.js`. Sie war schon
 * auseinandergelaufen: Die eine Fassung räumt vorher auf, die andere nicht —
 * und wer bei ihr zweimal lädt, hat jede Kategorie doppelt in der Liste.
 * Deshalb ist das Aufräumen hier die Vorgabe.
 *
 * DER ERSTE EINTRAG BLEIBT STEHEN. Er ist das „alle"/„All" der Vorlage und
 * trägt den leeren Wert, an dem die Filter erkennen, dass nicht gefiltert
 * werden soll. Wer ihn mitlöscht, bekommt eine Liste, aus der man nicht mehr
 * zu „alle" zurückkommt.
 *
 * DIE GROSSSCHREIBUNG ist reine Anzeige: Der Wert bleibt der Name, wie er vom
 * Server kommt. Ein groß geschriebener Wert liefe in den Vergleichen ins
 * Leere, ohne dass etwas rot wird — die Liste wäre einfach immer leer.
 */
import { Auswahlfeld } from './auswahlfeld.js';

export class Kategoriewahl {
    /**
     * @param {string} feldKennung Kennung des `<select>`
     * @param {Array} namen Kategorienamen vom Server
     * @param {boolean} aufraeumen Vorhandene Einträge (außer dem ersten)
     *     vorher entfernen. Vorgabe: ja.
     * @returns {number} wie viele Einträge angehängt wurden
     */
    static fuellen(feldKennung, namen, { aufraeumen = true } = {}) {
        const wahl = document.getElementById(feldKennung);
        if (!wahl || !namen) return 0;
        if (aufraeumen) {
            while (wahl.options.length > 1) wahl.remove(1);
        }
        return Auswahlfeld.ausNamen(wahl, namen,
            (name) => name.charAt(0).toUpperCase() + name.slice(1));
    }
}
