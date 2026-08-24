import { Bedienleiste } from './bedienleiste.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Zeitleistenwerkzeuge — „Timeline neu aufbauen" und „Timeline leeren".
 *
 * Herausgelöst aus `main.js` (788 Zeilen). Beide Werkzeuge hängen am
 * Werkzeug-Menü UND an `window`, weil sie aus der Konsole gebraucht werden,
 * wenn Theatre.js einen kaputten Zustand geladen hat.
 *
 * **Neu aufbauen** schreibt den IST-Zustand aller Theatre-Objekte als
 * Schlüsselbilder bei Position 0. Verschachtelte Werte (`{x, y, z}`) müssen
 * einzeln gesetzt werden — Theatre.js nimmt kein ganzes Objekt an. Farben sind
 * die Ausnahme: Sie sind selbst ein Objekt und werden am Stück gesetzt.
 *
 * **Leeren** wirft ALLE Theatre-Schlüssel aus dem lokalen Speicher und lädt die
 * Seite neu — nur so vergisst Theatre.js seinen gespeicherten Stand wirklich.
 */
export class Zeitleistenwerkzeuge {

    static LAENGE_SEKUNDEN = 10;
    static SPEICHERMARKEN = ['theatre', 'Theatre', 'HumanBody Theatre'];

    constructor(blatt, studio, objekte) {
        this.blatt = blatt;
        this.studio = studio;
        this.objekte = objekte;
    }

    /** An Menü und `window` hängen. */
    verdrahten() {
        window.rebuildTimeline = () => this.neuAufbauen();
        window.clearTimeline = () => Zeitleistenwerkzeuge.leeren();
        for (const [kennung, tun] of [['menu-tracks-rebuild', window.rebuildTimeline],
                                      ['menu-tracks-clear', window.clearTimeline]]) {
            document.getElementById(kennung)?.addEventListener('click', ereignis => {
                ereignis.stopPropagation();
                Bedienleiste.menuesZuklappen();
                tun();
            });
        }
        return this;
    }

    neuAufbauen() {
        const folge = this.blatt.sequence;
        const objekte = window.theatreObjects || this.objekte || {};
        try {
            this.studio.transaction(({ set }) =>
                set(folge.pointer.length, Zeitleistenwerkzeuge.LAENGE_SEKUNDEN));
        } catch (fehler) {
            Protokoll.warnung('main', 'Set length failed:', fehler);
        }
        folge.position = 0;
        const eintraege = Object.entries(objekte);
        for (const [name, objekt] of eintraege) this._schreiben(name, objekt);
        this.studio.setSelection([this.blatt]);
        Protokoll.debug('main', '✓ Timeline rebuilt:', eintraege.length, 'objects');
    }

    _schreiben(name, objekt) {
        const werte = objekt.value;
        if (!werte) return;
        try {
            this.studio.transaction(({ set }) => {
                for (const [feld, wert] of Object.entries(werte)) {
                    Zeitleistenwerkzeuge._setzen(set, objekt, feld, wert);
                }
            });
            Protokoll.debug('main', '✓ Timeline:', name, 'OK');
        } catch (fehler) {
            Protokoll.fehler('main', `Timeline: ${name}`, fehler);
        }
    }

    static _setzen(set, objekt, feld, wert) {
        const verschachtelt = feld !== 'color' && typeof wert === 'object'
            && wert !== null && !Array.isArray(wert);
        if (!verschachtelt) {
            set(objekt.props[feld], wert);
            return;
        }
        for (const [unterfeld, unterwert] of Object.entries(wert)) {
            set(objekt.props[feld][unterfeld], unterwert);
        }
    }

    static leeren() {
        for (const schluessel of Object.keys(localStorage)) {
            if (Zeitleistenwerkzeuge.SPEICHERMARKEN
                    .some(marke => schluessel.includes(marke))) {
                localStorage.removeItem(schluessel);
            }
        }
        if (window.keyframeUI) window.keyframeUI.keyframes = [];
        window.location.reload();
    }
}
