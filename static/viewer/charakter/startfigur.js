import { state } from './state.js';
import { Charakterdialog } from './charakterdialog.js';
import { Letztewahl } from './letztewahl.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Startfigur — die Figur, mit der die Szene-Seite aufgeht.
 *
 * SEIT DEM 30.09.2026 IST DAS DIE ZULETZT GELADENE (Edgar: „entferne das Standardmodell
 * und die Standard Animation. Auf der Seite /Charakter/ soll immer nur der letzte
 * geladene Modell und die letzte Animation geladen werden"). Vorher stand sie als
 * Einstellung in `/settings/charakter/` (`default_model_scene` samt Figurart und
 * Bereich) — eine Vorgabe von Hand, die nie beschrieb, woran gerade gearbeitet wurde.
 * Jetzt kommt sie aus `Letztewahl` (`localStorage`), gesetzt beim Laden jeder Figur.
 *
 * Geladen wird über dieselben Lader wie im Dialog „Charakter hinzufügen"
 * (`Charakterdialog.LADER`) — ein gespeichertes Genesis-9-Modell lädt anders als eines
 * aus dem Daz-Katalog. `state.defaultPresetName` bleibt gesetzt: Die Sitzungsablage
 * vergleicht damit, ob sich die Figur geändert hat (`session.js`, über `kennung()`).
 */
export class Startfigur {

    /** HumanBody, solange nie etwas geladen wurde. */
    static VORGABE = { name: 'femaleWithClothes', quelle: 'modell', bereich: 'gespeichert' };

    /**
     * Die zuletzt geladene Figur — IMMER frisch aus der Ablage, nie zwischengespeichert:
     * Die Lader melden dorthin (`Charakterdialog.LADER`), und `session.js` vergleicht
     * `kennung()` noch im selben Seitenleben. Ein Zwischenspeicher wäre nach dem ersten
     * Laden veraltet und würde die Sitzung fälschlich verwerfen.
     */
    static get wahl() {
        return Startfigur._aus(Letztewahl.figur());
    }

    /** Eine Wahl auf gültige Werte ziehen — eine unbekannte Figurart fiele sonst auf. */
    static _aus({ name, quelle, bereich }) {
        return {
            name: name || Startfigur.VORGABE.name,
            quelle: Charakterdialog.LADER[quelle] ? quelle : Startfigur.VORGABE.quelle,
            bereich: bereich === 'standard' ? 'standard' : 'gespeichert',
        };
    }

    /**
     * Eine Figur wurde geladen: Sie ist ab jetzt die Startfigur. Gerufen von jedem
     * Ladeweg (`Charakterdialog.LADER` umhüllt alle) — nicht nur beim Start, sonst
     * merkte sich die Szene genau das nicht, was der Nutzer gerade getan hat.
     */
    static setzen(name, quelle, bereich) {
        const wahl = Startfigur._aus({ name, quelle, bereich });
        state.defaultPresetName = wahl.name;
        Letztewahl.figurGemerkt(wahl.name, wahl.quelle, wahl.bereich);
        return wahl;
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
