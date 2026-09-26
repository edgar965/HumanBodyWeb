import { Genesis9Modell } from '../../gemeinsam/genesis9modell.js';
import { Figurablage } from '../figurablage.js';

/**
 * Genesis9Figur — die Daz-Figur der Szene: der Bau steht in `Genesis9Modell`
 * (`gemeinsam/genesis9modell.js`, für alle Seiten), hier nur das Speichern
 * und Laden mit den GarmentCode-Stücken (`Figurablage`).
 *
 * OHNE `toJSON`/`fromJSON` BRICHT DIE UNDO-AUFNAHME (08.09.2026):
 * `Szenenzustand.einsammeln` ruft `figur.toJSON()` über ALLE Figuren.
 */
export class Genesis9Figur extends Genesis9Modell {

    toJSON() {
        return {
            ...Figurablage.grunddaten(this),
            figur: this.figur,
            regler: { ...(this.regler || {}) },
            haut: this.haut,
            augen: this.augen,
            brauen: this.brauen,
            brauenstil: this.brauenstil,
            praesets: { ...this.praesets },
            hautmischung: { ...this.hautmischung },
            pose: this.pose,
            ausdruck: this.ausdruck,
            kleidung: { ...this.kleidung },
        };
    }

    static fromJSON(daten) {
        return Figurablage.ausJSON(Genesis9Figur, daten);
    }
}
