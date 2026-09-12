import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { generateCharacterId } from './utils.js';
import { markDirty } from './undo.js';
import { Figurplatzierung } from './figurplatzierung.js';

/**
 * Figuraufnahme — eine frisch gebaute Figur laden, stellen, in die Szene
 * nehmen und auswählen.
 *
 * WARUM (12.09.2026, Befund `doppelcode`): Dieselben neun Zeilen standen in
 * `Mhkatalog`, `Smplkatalog`, `Umakatalog` und `Umapythonkatalog`. Die
 * Reihenfolge ist der Grund, warum sie an EINER Stelle stehen sollen: Die
 * Lage kommt erst NACH `load()` — vorher hat die Figur keine Größe, die
 * `Figurplatzierung` angleichen könnte (06.09.2026).
 */
export class Figuraufnahme {

    /** Eine neue Kennung — die Kataloge bauen ihre Figur damit. */
    static kennung() {
        return generateCharacterId();
    }

    static async inDieSzene(figur, lage = null) {
        await figur.load();
        Figurplatzierung.anwenden(figur, lage);
        state.characters.set(figur.id, figur);
        state.scene.add(figur.group);
        fn.updateCharacterListUI();
        fn.updateVertexCount();
        fn.selectCharacter(figur.id);
        markDirty();
        return figur;
    }
}
