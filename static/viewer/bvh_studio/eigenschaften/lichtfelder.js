import { Maskenbausteine as M } from './bausteine.js';

/**
 * Lichtfelder — Winkel, Penumbra und Reichweite eines Spotlichts.
 *
 * BEFUND `doppelcode` (31.08.2026): Diese drei Felder standen ZWEIMAL, in
 * zwei Dateien und in zwei Schreibweisen:
 *
 *   `eigenschaften/licht.js`                als HTML von Hand,
 *                                           `<div class="prop-row">…`
 *   `eigenschaften/klip_schluesselbilder.js` über `M.zeile` / `M.zahl`
 *
 * Gleich waren beide Male die Grenzen — `min="1" max="170" step="1"` für
 * den Winkel, `0…1` in Schritten von 0.05 für die Penumbra, `0…200` für
 * die Reichweite. Sie standen damit an vier Stellen (zweimal je Datei,
 * einmal im Markup und einmal in der Prüfung beim Übernehmen).
 *
 * WARUM DAS WEHTUT: Ein Spotlicht mit Winkel über 170° ist in Three.js
 * ungültig (`THREE.SpotLight.angle` erwartet Radiant bis PI/2); wer die
 * Grenze an EINER der beiden Stellen anhebt, bekommt ein Licht, das in
 * der Spur anders aussieht als am Schlüsselbild — und die Maske sieht
 * dabei völlig normal aus.
 *
 * DIE KENNUNGEN unterscheiden sich (`prop-light-angle` gegen
 * `prop-lkf-angle`), weil beide Masken gleichzeitig im DOM stehen können.
 * Deshalb nimmt jede Methode die Vorsilbe.
 */
export class Lichtfelder {

    /** Grenzen und Schrittweite je Feld — die eine Stelle. */
    static GRENZEN = {
        winkel: 'min="1" max="170" step="1"',
        penumbra: 'min="0" max="1" step="0.05"',
        reichweite: 'min="0" max="200" step="1"',
    };

    /**
     * Der Öffnungswinkel in Grad.
     *
     * @param vorsilbe `prop-light` oder `prop-lkf`
     * @param radiant  Winkel im Bogenmass, oder null/undefined
     * @param vorgabe  was gilt, wenn kein Winkel gesetzt ist (Bogenmass)
     * @returns {string} HTML einer Maskenzeile
     */
    static winkel(vorsilbe, radiant, vorgabe = Math.PI / 6) {
        const grad = ((radiant ?? vorgabe) * 180 / Math.PI).toFixed(1);
        return M.zeile('Winkel',
            M.zahl(`${vorsilbe}-angle`, grad, Lichtfelder.GRENZEN.winkel)
            + ' °');
    }

    /**
     * Die Weichheit des Randes, 0 bis 1.
     *
     * @param vorsilbe `prop-light` oder `prop-lkf`
     * @param wert     aktueller Wert, oder null/undefined
     * @param vorgabe  was gilt, wenn nichts gesetzt ist
     * @returns {string} HTML einer Maskenzeile
     */
    static penumbra(vorsilbe, wert, vorgabe = 0.3) {
        return M.zeile('Penumbra',
            M.zahl(`${vorsilbe}-penumbra`, (wert ?? vorgabe).toFixed(2),
                   Lichtfelder.GRENZEN.penumbra));
    }

    /**
     * Die Reichweite in Metern.
     *
     * @param vorsilbe `prop-light` oder `prop-lkf`
     * @param wert     aktueller Wert, oder null/undefined
     * @param vorgabe  was gilt, wenn nichts gesetzt ist
     * @returns {string} HTML einer Maskenzeile
     */
    static reichweite(vorsilbe, wert, vorgabe = 50) {
        return M.zeile('Reichweite',
            M.zahl(`${vorsilbe}-distance`, (wert ?? vorgabe).toFixed(1),
                   Lichtfelder.GRENZEN.reichweite));
    }

    /**
     * Alle drei hintereinander — für die Lichtspur, wo sie immer zusammen
     * erscheinen.
     *
     * @param vorsilbe `prop-light`
     * @param licht    das Three.js-Licht, oder null
     * @returns {string} HTML dreier Maskenzeilen
     */
    static alle(vorsilbe, licht) {
        return Lichtfelder.winkel(vorsilbe, licht?.angle)
            + Lichtfelder.penumbra(vorsilbe, licht?.penumbra)
            + Lichtfelder.reichweite(vorsilbe, licht?.distance);
    }
}
