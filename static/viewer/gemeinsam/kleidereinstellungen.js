import { Serverabruf } from './serverabruf.js';
import { Protokoll } from './protokoll.js';

/**
 * Kleidereinstellungen — die Schalter von Einstellungen → Kleider im Browser.
 *
 * Edgar (24.09.2026): „mach das einstellbar in einer neuen Seite Einstellungen
 * - Kleider, Default: An". Die Werte liegen in `AppSettings.ui_prefs` (Seite
 * `core/api/seite_kleider_einstellungen.py`), gelesen einmal je Seite über
 * `/api/ui-prefs/`. Bis die Antwort da ist, gelten die Vorgaben — eine Figur,
 * die vor der Antwort gezeichnet wird, sieht also schon die Vorgabe (An),
 * nicht einen Zwischenstand „aus".
 *
 * Gelesen wird je Bild (`an(name)`), nicht beim Verdrahten: Die Antwort kommt
 * oft nach dem ersten Stück, und ein Stück, das seinen Schalter beim Anziehen
 * festhielte, bliebe bis zum Neuladen falsch.
 */
export class Kleidereinstellungen {

    static ENDPUNKT = '/api/ui-prefs/';

    /** Schlüssel in `ui_prefs` → Vorgabe. Muss zu `KleiderEinstellungenSeite.VORGABEN` passen. */
    static VORGABEN = {
        kleider_oberflaechenbindung: true,
        kleider_normalen_aus_flaeche: true,
    };

    static _werte = { ...Kleidereinstellungen.VORGABEN };
    static _laden = null;

    /** Ist der Schalter an? Startet beim ersten Aufruf das Laden. */
    static an(name) {
        Kleidereinstellungen.laden();
        return Boolean(Kleidereinstellungen._werte[name]);
    }

    static laden() {
        if (!Kleidereinstellungen._laden) Kleidereinstellungen._laden = Kleidereinstellungen._holen();
        return Kleidereinstellungen._laden;
    }

    static async _holen() {
        try {
            const prefs = await Serverabruf.json(Kleidereinstellungen.ENDPUNKT);
            for (const name of Object.keys(Kleidereinstellungen.VORGABEN)) {
                if (prefs?.[name] !== undefined) Kleidereinstellungen._werte[name] = Kleidereinstellungen.wahr(prefs[name]);
            }
        } catch (fehler) {
            Protokoll.warnung('Kleidereinstellungen', 'Vorlieben nicht lesbar — es gelten die Vorgaben', fehler);
        }
        return Kleidereinstellungen._werte;
    }

    /** Das Formular schickt '1'/'0' (verstecktes Feld + Kästchen), ältere Stände echte Wahrheitswerte. */
    static wahr(wert) {
        return wert === true || wert === 1 || wert === '1' || wert === 'true';
    }
}
