import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Die Statuszeile der Theatre-Studio-Probeseite.
 *
 * Aus dem 140-zeiligen Inline-Modul in `theatre_studio.html` herausgelöst
 * (Umbau 27.08.2026). Dort stand der Zustand als freie Funktion neben einem
 * Dutzend `console.log`-Zeilen.
 */
export class Studiozustand {
    /** Farben der Zustände. */
    static LAEUFT = '#ff0';
    static GUT = '#0f0';
    static WARNUNG = '#f80';
    static FEHLER = '#f00';

    /**
     * @param {string} text
     * @param {string} farbe eine der Konstanten oben
     */
    static setzen(text, farbe = Studiozustand.LAEUFT) {
        const el = document.getElementById('studio-status');
        if (el) {
            el.textContent = text;
            el.style.color = farbe;
        }
        Protokoll.info('Theatre-Studio', text);
    }

    /** Beschriftet Projekt- und Blattnamen im Randbereich. */
    static benennen(projekt, blatt, objekte) {
        const setzen = (id, wert) => {
            const el = document.getElementById(id);
            if (el) el.textContent = wert;
        };
        setzen('project-name', projekt);
        setzen('sheet-name', blatt);
        setzen('object-count', String(objekte));
    }
}
