/**
 * Klappbereiche — die Abschnitte einer Seitenleiste auf- und zuklappen.
 *
 * WARUM (Befund `doppelcode`, 30.08.2026): Dieselben fuenf Zeilen standen als
 * `_bereicheKlappbar` in `animation/animationsseite.js` und
 * `scene/szenenaufbau.js`.
 *
 * DAS MUSTER IST FEST VERDRAHTET: `.panel-section h3` als Griff,
 * `.collapsed` am `.panel-section` als Zustand. Beides steht so in den
 * Vorlagen (`_kleidungspanele.html`, `character_viewer.html`, …) und im CSS.
 * Wer eine der beiden Klassen umbenennt, bekommt Abschnitte, die sich nicht
 * mehr oeffnen lassen — ohne Meldung.
 *
 * EINMAL JE SEITE aufrufen, nach dem Aufbau der Leiste. Ein zweiter Aufruf
 * haengt einen zweiten Zuhoerer an jeden Kopf, und der Abschnitt klappt beim
 * Klick auf und sofort wieder zu.
 */
export class Klappbereiche {
    /** @param {string} auswahl Griff-Selektor, Vorgabe `.panel-section h3` */
    static verdrahten(auswahl = '.panel-section h3') {
        for (const kopf of document.querySelectorAll(auswahl)) {
            kopf.addEventListener('click', () => {
                kopf.closest('.panel-section').classList.toggle('collapsed');
            });
        }
    }
}
