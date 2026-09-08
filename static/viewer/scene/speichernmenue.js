import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Kontextmenue } from '../gemeinsam/kontextmenue.js';
import { Szenenausgabe } from './szenenausgabe.js';

/**
 * Speichern — Modell oder Szene.
 *
 * Edgar, 08.09.2026: „Bei Menü Speichern soll «Modell» oder Szene kommen, und
 * das Modell soll oder Szene sollen gespeichert werden" und „Auch rechtsklick
 * auf das Modell oberhalb des Tabs, neues Kontextmenü: Speichern".
 *
 * ES SIND ZWEI VERSCHIEDENE DINGE, und das war vorher nicht zu sehen: Das
 * Menü hieß „Speichern" und meinte immer die SZENE (Lichter, Kamera, alle
 * Figuren). Ein einzelnes Modell — eine Figur mit ihren Morphs, Kleidern und
 * GarmentCode-Stücken — ließ sich nur über „Modell exportieren (JSON)" in
 * eine Datei legen, nicht in den Modellkatalog des Servers.
 *
 * DAS MODELL GEHT AN DEN SERVER (`/api/character/model/save/`), nicht in eine
 * Datei: Nur was dort liegt, erscheint in „Charakter hinzufügen" und lässt
 * sich beim nächsten Mal wieder laden.
 */
export class Speichernmenue {

    static ENDPUNKT = '/api/character/model/save/';

    /** Die gewählte Figur — oder `null` mit Hinweis. */
    static figur() {
        const inst = state.selectedCharacterId
            ? state.characters.get(state.selectedCharacterId) : null;
        if (!inst) {
            alert('Bitte zuerst einen Charakter auswählen.');
            return null;
        }
        return inst;
    }

    /**
     * Das gewählte Modell in den Katalog schreiben.
     *
     * @param fragen  `true` fragt nach dem Namen („Speichern unter"),
     *                `false` nimmt den vorhandenen und fragt nur, wenn es
     *                keinen gibt.
     */
    static async modell(fragen = false) {
        const inst = Speichernmenue.figur();
        if (!inst) return false;
        const daten = Szenenausgabe.modelldaten(inst);
        let name = inst.presetKey || inst.presetName || '';
        if (fragen || !name) {
            name = prompt('Modell speichern als:', name || 'Neues Modell');
            if (!name) return false;
        }
        try {
            await Serverabruf.senden(Speichernmenue.ENDPUNKT,
                                     { name, data: daten });
        } catch (fehler) {
            alert(`Modell nicht gespeichert: ${fehler.message || fehler}`);
            return false;
        }
        // Der Server bereinigt den Namen (nur Buchstaben, Ziffern, Binde- und
        // Unterstriche). Die Figur bekommt den bereinigten Namen, sonst
        // schreibt das nächste „Speichern" eine zweite Datei.
        inst.presetName = name;
        inst.presetKey = name;
        fn.updateCharacterListUI?.();
        // Die Liste im Dialog „Charakter hinzufügen" ist jetzt veraltet.
        fn.refreshModelList?.();
        return true;
    }

    /** Die Szene speichern — der alte Weg, unverändert. */
    static szene(fragen = false) {
        if (fragen) fn.openSaveDialog();
        else fn.quickSave();
    }

    /**
     * Das Kontextmenü an eine Zeile der Charakterliste hängen.
     *
     * Gebunden wird beim Neuaufbau der Liste (`updateCharacterListUI`), also
     * bei jeder Änderung — deshalb wird die Figur über ihre KENNUNG geholt
     * und nicht über die Instanz: Die Zeile überlebt den Neuaufbau nicht, die
     * Kennung schon.
     */
    static binden(zeile, charId) {
        Kontextmenue.binden(zeile, () => {
            // Rechtsklick wählt die Zeile mit an — sonst bezieht sich
            // „Speichern" auf eine andere Figur als die angeklickte.
            if (state.selectedCharacterId !== charId) fn.selectCharacter(charId);
            return [
                { symbol: 'fa-save', text: 'Modell speichern',
                  tun: () => Speichernmenue.modell(false) },
                { symbol: 'fa-file-export', text: 'Modell speichern unter …',
                  tun: () => Speichernmenue.modell(true) },
                null,
                { symbol: 'fa-images', text: 'Szene speichern',
                  tun: () => Speichernmenue.szene(false) },
                { symbol: 'fa-folder-open', text: 'Szene speichern unter …',
                  tun: () => Speichernmenue.szene(true) },
            ];
        });
    }
}

fn.saveModelToCatalog = () => Speichernmenue.modell(false);
fn.saveModelToCatalogAs = () => Speichernmenue.modell(true);
