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
            // Alle zehn Formregler (Größe, Fülle, form3..form10) — nicht nur
            // die zwei benannten (25.09.2026, „SMPL-X für Vollausstattung").
            form: { ...this.form },
            haut: this.haut ? { ...this.haut } : undefined,
            // Augen, Brauen, Mund, Nägel — dieselben Felder wie HumanBody (25.09.2026).
            details: this.details ? { ...this.details } : undefined,
        };
    }

    static fromJSON(daten) {
        return Figurablage.ausJSON(SmplFigur, daten);
    }
}
