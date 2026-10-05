import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Engine2d3dKleiderlaeufelayout — Größe und Spaltenbreiten der Render-Läufe-Tabelle merken, auf dem SERVER und im Browser (04.10.2026).
 *
 * Edgar: „du merkst dir immer noch nicht die Größe dieser Tabelle und die Spaltenbreite … beim nächsten Start". Bis dahin lagen beide nur im `localStorage`
 * des Browsers (Größe: `engine2d3dkleider-render-laeufe-groesse`, Breiten: `tblBreiten:engine2d3dkleider-render-laeufe`, geschrieben von djangoBase
 * `TabellenBreiten`). Löscht der Browser beim Beenden die Websitedaten, oder öffnet man die Seite unter einer anderen Adresse, sind sie weg. Jetzt hält
 * der Server eine Kopie (`/api/ui-prefs/`, Schlüssel `engine2d3dkleider.render_laeufe`): Beim Start schreibt diese Klasse sie in den `localStorage`,
 * BEVOR die Tabelle gebaut und von djangoBase gebunden wird (`bereit`); jede Änderung geht nach kurzer Pause zurück an den Server (`sichern`).
 */
export class Engine2d3dKleiderlaeufelayout {

    static ADRESSE = '/api/ui-prefs/';
    static SCHLUESSEL = 'engine2d3dkleider.render_laeufe';
    static GROESSE = 'engine2d3dkleider-render-laeufe-groesse';
    static BREITEN = 'tblBreiten:engine2d3dkleider-render-laeufe';
    static PAUSE_MS = 400;

    constructor() {
        this.rahmen = null;
        this._zuletzt = '';
        this._timer = null;
        // Das Ziehen einer Spaltenbreite endet mit `mouseup` auf dem Dokument (djangoBase schreibt die Breiten dort); die Pause lässt es zuerst fertig werden.
        document.addEventListener('mouseup', () => this._spaeter());
        /** Erfüllt, sobald die Werte des Servers im Browser stehen — erst danach die Tabelle bauen. Scheitert der Abruf, gilt der Browser allein. */
        this.bereit = this._holen();
    }

    // ------------------------------------------------------------------ Server

    async _holen() {
        try {
            const alle = await Serverabruf.json(Engine2d3dKleiderlaeufelayout.ADRESSE);
            const wert = alle[Engine2d3dKleiderlaeufelayout.SCHLUESSEL];
            if (wert && wert.groesse) this._schreiben(Engine2d3dKleiderlaeufelayout.GROESSE, wert.groesse);
            if (wert && wert.breiten) this._schreiben(Engine2d3dKleiderlaeufelayout.BREITEN, wert.breiten);
        } catch (fehler) {
            console.info('Render-Läufe: Layout vom Server nicht lesbar, es gilt der Browser', fehler);
        }
        this._zuletzt = JSON.stringify(this._lesen());
    }

    async _speichern(wert) {
        try {
            await Serverabruf.senden(Engine2d3dKleiderlaeufelayout.ADRESSE, { [Engine2d3dKleiderlaeufelayout.SCHLUESSEL]: wert });
        } catch (fehler) {
            console.info('Render-Läufe: Layout nicht auf dem Server gespeichert', fehler);
            this._zuletzt = '';          // beim nächsten Anlass noch einmal versuchen
        }
    }

    // ------------------------------------------------------------------ Browser

    _lesen() {
        const lesen = schluessel => {
            try { return JSON.parse(localStorage.getItem(schluessel) || 'null'); } catch { return null; }
        };
        const groesse = this.rahmen && (this.rahmen.style.width || this.rahmen.style.height)
            ? { breite: Math.round(this.rahmen.offsetWidth), hoehe: Math.round(this.rahmen.offsetHeight) }
            : lesen(Engine2d3dKleiderlaeufelayout.GROESSE);
        return { groesse: groesse && groesse.breite > 0 && groesse.hoehe > 0 ? groesse : null, breiten: lesen(Engine2d3dKleiderlaeufelayout.BREITEN) };
    }

    _schreiben(schluessel, wert) {
        try { localStorage.setItem(schluessel, JSON.stringify(wert)); } catch (fehler) { console.info('Render-Läufe: Layout nicht im Browser gemerkt', fehler); }
    }

    // --------------------------------------------------------------- Der Rahmen

    /**
     * Den gemerkten Stand auf den (neuen) Rahmen der Tabelle legen und seine Größe beobachten. Gemerkt wird nur, was der Nutzer gezogen hat: Dann schreibt
     * der Browser Breite und Höhe in `style` (`resize: both`); die Größe beim Anlegen ist die des Inhalts.
     */
    anwenden(rahmen) {
        this.rahmen = rahmen;
        const alt = this._lesen().groesse;
        if (alt) {
            rahmen.style.width = `${alt.breite}px`;
            rahmen.style.height = `${alt.hoehe}px`;
        }
        if (typeof ResizeObserver === 'undefined') return;
        new ResizeObserver(() => { if (rahmen.style.width || rahmen.style.height) this._spaeter(); }).observe(rahmen);
    }

    _spaeter() {
        clearTimeout(this._timer);
        this._timer = setTimeout(() => this.sichern(), Engine2d3dKleiderlaeufelayout.PAUSE_MS);
    }

    /** Größe und Breiten in den Browser UND zum Server — nur, wenn sich seit dem letzten Mal etwas geändert hat. */
    sichern() {
        const wert = this._lesen();
        const text = JSON.stringify(wert);
        if (text === this._zuletzt) return;
        this._zuletzt = text;
        if (wert.groesse) this._schreiben(Engine2d3dKleiderlaeufelayout.GROESSE, wert.groesse);
        this._speichern(wert);
    }
}
