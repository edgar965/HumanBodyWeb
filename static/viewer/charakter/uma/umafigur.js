import { UmaModell } from '../../gemeinsam/umamodell.js';
import { Figurablage } from '../figurablage.js';

/**
 * UmaFigur — die UMA-Figur der Szene: der Bau steht in `UmaModell`
 * (`gemeinsam/umamodell.js`, seit 13.09.2026 für alle Seiten), hier nur das
 * Speichern und Laden mit den GarmentCode-Stücken (`Figurablage`).
 *
 * OHNE `toJSON`/`fromJSON` BRICHT DIE UNDO-AUFNAHME (08.09.2026):
 * `Szenenzustand.einsammeln` ruft `figur.toJSON()` über ALLE Figuren.
 */
export class UmaFigur extends UmaModell {

    toJSON() {
        return {
            ...Figurablage.grunddaten(this),
            datei: this.datei,
            dna: this.dna,
            farben: this.farben,
        };
    }

    static fromJSON(daten) {
        return Figurablage.ausJSON(UmaFigur, daten);
    }
}
