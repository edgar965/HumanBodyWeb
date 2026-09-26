import { state } from './state.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Kleiderzustand — welche Kategorie offen ist und was ausgewählt war.
 *
 * Herausgelöst aus `kleider_liste.js` (267 Zeilen), wo es zwei Modulvariablen
 * und zwei Funktionen waren (`_kldOpenCat`, `_saveKldState`, `_loadKldState`) —
 * Befund `klassenplan`: geteilter Zustand gehört in eine Klasse.
 *
 * ZWEI SPEICHER, UND DAS IST ABSICHT
 * ==================================
 * * `localStorage` — sofort da, überlebt einen Reload, gilt je Browser.
 * * `/api/ui-pref/` (`last_kleider_id`) — gilt je NUTZER und überlebt einen
 *   anderen Rechner. Die Serverseite ist die langsamere; deshalb wird sie
 *   nebenläufig geschrieben und ihr Fehlschlag nur protokolliert. Die Auswahl
 *   ist eine Bequemlichkeit, kein Datum, für das eine Fehlermeldung lohnt.
 */
export class Kleiderzustand {

    static SCHLUESSEL = 'kleider_state';
    static SERVERSCHLUESSEL = 'last_kleider_id';
    static VORGABE = '/api/ui-pref/';

    constructor() {
        /** Offene Kategorie (leer = keine). */
        this.kategorie = '';
    }

    /** Aus dem localStorage lesen — auch die Auswahl in `state`. */
    laden() {
        try {
            const gemerkt = JSON.parse(
                localStorage.getItem(Kleiderzustand.SCHLUESSEL));
            if (!gemerkt) return;
            this.kategorie = gemerkt.openCat || '';
            state._selectedKleiderId = gemerkt.selectedId || '';
        } catch (fehler) {
            Protokoll.debug('kleider', 'gemerkte Auswahl nicht lesbar', fehler);
        }
    }

    merken() {
        localStorage.setItem(Kleiderzustand.SCHLUESSEL, JSON.stringify({
            openCat: this.kategorie,
            selectedId: state._selectedKleiderId,
        }));
    }

    /** Die Auswahl auch am Server vermerken (siehe Klassendoku). */
    aufDemServerMerken(id) {
        fetch(Kleiderzustand.VORGABE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key: Kleiderzustand.SERVERSCHLUESSEL,
                                   value: id }),
        }).catch(fehler => Protokoll.debug(
            'kleider', 'Auswahl nicht auf dem Server gemerkt', fehler));
    }
}
