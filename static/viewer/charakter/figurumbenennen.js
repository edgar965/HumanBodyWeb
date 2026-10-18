import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { markDirty } from './undo.js';

/**
 * Figurumbenennen — eine Figur der Szene umbenennen (Rechtsklick auf die Modellzeile, `Speichernmenue.binden`).
 *
 * Edgar, 18.10.2026: „es sollen doch ALLE Assets umbenannt und gelöscht werden können?" — „mach beide": die Modellzeilen der Szene ließen sich nur entfernen.
 *
 * Es ändert den Namen der FIGUR IN DER SZENE (`presetName`, in der Liste und im Kopf der Eigenschaften), nicht den Katalogeintrag, aus dem sie kam — der heißt weiter
 * wie vorher (umbenennen im Katalog geht im Dialog „Charakter hinzufügen"). Hängt an der Figur ein Katalogschlüssel (`presetKey`), wird er mitgeführt: Beim Laden
 * einer Szene setzt `CharacterInstance.fromJSON` den Namen aus dem Schlüssel, ein nur umbenanntes `presetName` wäre nach dem Neuladen wieder weg. Folge: „Modell speichern"
 * legt die Figur danach unter dem neuen Namen im Katalog ab.
 */
export class Figurumbenennen {

    /** Nach dem Namen fragen und ihn setzen. → `true`, wenn er sich geändert hat. */
    static umbenennen(charId) {
        const inst = state.characters.get(charId);
        if (!inst) return false;
        const alt = inst.presetName || '';
        const antwort = window.prompt(`Neuer Name für das Modell „${alt}" (in der Szene):`, alt);
        const name = antwort === null ? '' : antwort.trim();
        if (!name || name === alt) return false;
        inst.presetName = name;
        if (inst.presetKey) inst.presetKey = name;
        fn.updateCharacterListUI();
        if (state.selectedCharacterId === charId) fn.populateProperties?.(charId);      // der Kopf der Eigenschaften trägt den Namen
        markDirty();
        return true;
    }
}
