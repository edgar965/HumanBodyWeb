import { UmapythonModell } from '../../gemeinsam/umapythonmodell.js';
import { Figurablage } from '../figurablage.js';

/**
 * UmapythonFigur — die in Python gebaute UMA-Figur der Szene: der Bau steht in `UmapythonModell`
 * (`gemeinsam/umapythonmodell.js`, seit 13.09.2026 für alle Seiten), hier nur das
 * Speichern und Laden mit den GarmentCode-Stücken (`Figurablage`).
 *
 * OHNE `toJSON`/`fromJSON` BRICHT DIE UNDO-AUFNAHME (08.09.2026):
 * `Szenenzustand.einsammeln` ruft `figur.toJSON()` über ALLE Figuren.
 */
export class UmapythonFigur extends UmapythonModell {

    toJSON() {
        return {
            ...Figurablage.grunddaten(this),
            rasse: this.rasse,
            dna: { ...this.dna },
            kleidung: [...this.kleidung],
        };
    }

    static fromJSON(daten) {
        return Figurablage.ausJSON(UmapythonFigur, daten);
    }
}
