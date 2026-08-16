import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';

/**
 * Vorgabenformular — ein Einstellungsformular als JSON an `/api/ui-prefs/`
 * senden, statt die Seite neu zu laden.
 *
 * Herausgeloest aus settings_bvh_studio.html (Umbau 16.08.2026). Der Block dort
 * hatte drei Schwaechen:
 *
 *  * Der CSRF-Token wurde mit einer eigenen Regex aus dem Cookie geholt —
 *    die fuenfte Fassung derselben Zeile im Projekt. Jetzt `Serverabruf`.
 *  * Bei einem Serverfehler kam nur "Fehler beim Speichern." ohne Grund.
 *  * Das Formular wurde ueber `document.getElementById` im Inline-Skript
 *    gegriffen, ohne Pruefung — fehlt die Kennung, wirft die Zeile und der
 *    Rest des Blocks (die Projektliste) laeuft nicht mehr.
 */
export class Vorgabenformular {

    static ENDPUNKT = '/api/ui-prefs/';
    /** Dieses Feld gehoert zu Django, nicht zu den Einstellungen. */
    static AUSNAHME = 'csrfmiddlewaretoken';

    /**
     * @param {string} formularId  Kennung des <form>-Elements
     * @param {string} erfolg      Meldung nach dem Speichern
     */
    static anmelden(formularId, erfolg = 'Einstellungen gespeichert.') {
        const formular = document.getElementById(formularId);
        if (!formular) return null;
        return new Vorgabenformular(formular, erfolg).anmelden();
    }

    constructor(formular, erfolg) {
        this.formular = formular;
        this.erfolg = erfolg;
    }

    anmelden() {
        this.formular.addEventListener('submit', ereignis => {
            ereignis.preventDefault();
            this.senden();
        });
        return this;
    }

    /** Alle Felder ausser dem CSRF-Feld als flaches Objekt. */
    werte() {
        const daten = {};
        for (const [schluessel, wert] of new FormData(this.formular)) {
            if (schluessel !== Vorgabenformular.AUSNAHME) daten[schluessel] = wert;
        }
        return daten;
    }

    async senden() {
        try {
            await Serverabruf.senden(Vorgabenformular.ENDPUNKT, this.werte());
            alert(this.erfolg);
        } catch (fehler) {
            alert('Fehler beim Speichern: ' + fehler.message);
        }
    }
}
