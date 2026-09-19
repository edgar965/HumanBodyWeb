import { state } from './state.js';
import { Charakterdialog } from './charakterdialog.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Startfigur — das Standard-Modell der Szene-Seite, in jeder Figurart.
 *
 * WARUM (Edgar, 19.09.2026, Einstellungen → Szene): „fehlt die Möglichkeit,
 * auch ein Genesis, UMA usw. als Standard-Modell auszuwählen." Bis dahin
 * kannte der Start nur einen Namen (`state.defaultPresetName`) und lud ihn
 * als HumanBody-Vorgabe (`addCharacterFromPreset`). Jetzt kommen Figurart
 * (`default_model_scene_quelle`) und Bereich (`…_bereich`, standard oder
 * gespeichert) aus den Einstellungen mit, und geladen wird über dieselben
 * Lader wie im Dialog „Charakter hinzufügen" (`Charakterdialog.LADER`) —
 * ein gespeichertes Genesis-9-Modell lädt anders als eines aus dem Daz-Katalog.
 *
 * `state.defaultPresetName` bleibt gesetzt: Die Sitzungsablage vergleicht
 * damit, ob sich die Vorgabe geändert hat (`session.js`, über `kennung()`).
 */
export class Startfigur {

    /** HumanBody, wie es immer war. */
    static VORGABE = { name: 'femaleWithClothes', quelle: 'modell', bereich: 'gespeichert' };

    static wahl = { ...Startfigur.VORGABE };

    /** Aus den Servereinstellungen (`Starteinstellungen.anwenden`). */
    static setzen(name, quelle, bereich) {
        Startfigur.wahl = {
            name: name || Startfigur.VORGABE.name,
            quelle: Charakterdialog.LADER[quelle] ? quelle : Startfigur.VORGABE.quelle,
            bereich: bereich === 'standard' ? 'standard' : 'gespeichert',
        };
        state.defaultPresetName = Startfigur.wahl.name;
        return Startfigur.wahl;
    }

    /** „genesis9:Victoria 9" — was die Sitzungsablage vergleicht. */
    static kennung() {
        return `${Startfigur.wahl.quelle}:${Startfigur.wahl.name}`;
    }

    /** Die Startfigur in die Bühne stellen; Fehler bleiben ohne Folgen. */
    static async laden() {
        const { name, quelle, bereich } = Startfigur.wahl;
        try {
            const eintrag = { name, bereich, gespeichert: bereich === 'gespeichert' };
            return await Charakterdialog.LADER[quelle](name, null, eintrag);
        } catch (fehler) {
            Protokoll.warnung('startfigur',
                              `Standard-Modell ${quelle}/${name} nicht ladbar:`, fehler);
            return null;
        }
    }
}
