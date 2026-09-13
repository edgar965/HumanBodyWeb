import { SmplModell } from '../../gemeinsam/smplmodell.js';
import { Figurablage } from '../figurablage.js';

/**
 * SmplFigur — der GarmentCode-Referenzkörper der Szene: der Bau steht in `SmplModell`
 * (`gemeinsam/smplmodell.js`, seit 13.09.2026 für alle Seiten), hier nur das
 * Speichern und Laden mit den GarmentCode-Stücken (`Figurablage`).
 *
 * OHNE `toJSON`/`fromJSON` BRICHT DIE UNDO-AUFNAHME (08.09.2026):
 * `Szenenzustand.einsammeln` ruft `figur.toJSON()` über ALLE Figuren.
 */
export class SmplFigur extends SmplModell {

    toJSON() {
        return {
            ...Figurablage.grunddaten(this),
            koerper: this.koerper,
            geschlecht: this.geschlecht,
            form: { groesse: this.form.groesse, fuelle: this.form.fuelle },
        };
    }

    static fromJSON(daten) {
        return Figurablage.ausJSON(SmplFigur, daten);
    }
}
