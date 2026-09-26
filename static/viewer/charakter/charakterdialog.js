import { fn } from '../gemeinsam/registrierung.js';
import { Figurwahldialog } from '../gemeinsam/figurwahldialog.js';
import { Katalogpflege } from './katalogpflege.js';
import { Figurplatzierung } from './figurplatzierung.js';
import { Umakatalog } from './uma/umakatalog.js';
import { Smplkatalog } from './smpl/smplkatalog.js';
import { Mhkatalog } from './makehuman/mhkatalog.js';
import { Umapythonkatalog } from './umapython/umapythonkatalog.js';
import { Genesis9katalog } from './genesis9/genesis9katalog.js';

/**
 * Charakterdialog — „Charakter hinzufügen" der Szene-Seite.
 *
 * WARUM (Edgar, 06.09.2026): „mach zwei Tabs, einmal UMA, einmal HumanBody.
 * Mach auch Möglichkeiten zum Umbenennen und Löschen der Modelle aus dem
 * Dialog." Aus zwei Reitern sind am selben Tag vier geworden, am 15.09.
 * fünf, am 17.09. sechs (Genesis 9); Position und Größe der neuen Figur
 * stehen darunter.
 *
 * Der Dialog selbst ist seit dem 11.09.2026 `gemeinsam/figurwahldialog.js`
 * (Theatre, Studio, Effekte). Die Szene hielt bis zum 17.09.2026 ihre eigene
 * Fassung mit Vorlage `_charakter_dialog.html` — 225 Zeilen, die dasselbe
 * taten (Befund `doppelcode`). Was von ihr bleibt, ist das, was nur die
 * Szene weiß: wer eine gewählte Zeile in die Bühne stellt (`LADER`), die
 * Vorgabe der Lage (`Figurplatzierung`: 1,5 m rechts neben der vorhandenen
 * Figur, auf deren Höhe) und die Pflege (`Katalogpflege`).
 */
export class Charakterdialog {

    /** Die Kennung des Dialogs — Präfix aller seiner IDs. */
    static KENNUNG = 'add-char-dialog';

    /**
     * Wer eine gewählte Zeile in die Szene stellt.
     *
     * Eine Tabelle statt eines verschachtelten Bedingungsausdrucks: Bei der
     * vierten Quelle war der drei Ebenen tief. `addCharacterFromPreset` kommt
     * aus der Registrierung und wird deshalb erst beim Aufruf geholt.
     */
    static LADER = {
        uma: (name, lage) => Umakatalog.hinzufuegen(name, lage),
        // Der Eintrag geht mit: ein gespeichertes Modell laedt anders als der Katalog.
        smpl: (name, lage, eintrag) => Smplkatalog.hinzufuegen(name, lage, eintrag),
        makehuman: (name, lage) => Mhkatalog.hinzufuegen(name, lage),
        modell: (name, lage) => fn.addCharacterFromPreset(name, lage),
        umapython: (name, lage) => Umapythonkatalog.hinzufuegen(name, lage),
        // Der Eintrag geht mit: ein gespeichertes Modell laedt anders als der Katalog.
        genesis9: (name, lage, eintrag) => Genesis9katalog.hinzufuegen(name, lage, eintrag),
    };

    static _dialog = null;

    static dialog() {
        if (!Charakterdialog._dialog) {
            Charakterdialog._dialog = new Figurwahldialog({
                lader: Charakterdialog.LADER,
                vorgaben: () => Figurplatzierung.vorgaben(),
                pflege: Katalogpflege,
                kennung: Charakterdialog.KENNUNG,
            });
        }
        return Charakterdialog._dialog;
    }

    static verdrahten() {
        document.getElementById('add-character-btn')
            ?.addEventListener('click', () => Charakterdialog.oeffnen());
    }

    static oeffnen() {
        return Charakterdialog.dialog().oeffnen();
    }
}
