import { MakehumanModell } from '../../gemeinsam/makehumanmodell.js';
import { Figurablage } from '../figurablage.js';

/**
 * MhFigur — der MakeHuman-Körper der Szene: der Bau steht in `MakehumanModell`
 * (`gemeinsam/makehumanmodell.js`, seit 13.09.2026 für alle Seiten), hier nur das
 * Speichern und Laden mit den GarmentCode-Stücken (`Figurablage`).
 *
 * OHNE `toJSON`/`fromJSON` BRICHT DIE UNDO-AUFNAHME (08.09.2026):
 * `Szenenzustand.einsammeln` ruft `figur.toJSON()` über ALLE Figuren.
 */
export class MhFigur extends MakehumanModell {

    toJSON() {
        return {
            ...Figurablage.grunddaten(this),
            modell: this.modell,
            teile: [...this.teile],
            glatt: this.glatt,
            haut: { ...this.haut },
            makro: { ...this.makro },
            regler: { ...this.regler },
            kleidung: { ...this.kleidung },
        };
    }

    static fromJSON(daten) {
        return Figurablage.ausJSON(MhFigur, daten);
    }
}
