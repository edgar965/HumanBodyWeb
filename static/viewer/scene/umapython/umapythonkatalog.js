import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { generateCharacterId } from '../utils.js';
import { markDirty } from '../undo.js';
import { UmapythonFigur } from './umapythonfigur.js';
import { Figurplatzierung } from '../figurplatzierung.js';

/**
 * Umapythonkatalog — UMAs Rassen anbieten und eine davon in die Szene bauen.
 *
 * WARUM (Edgar, 08.09.2026: „Ich möchte doch ein Male, Female, Elf usw.
 * auswählen, genau so wie UMA das macht!"): Der Reiter zeigte bis dahin
 * Testpaare des Konformers — einen GarmentCode-Körper mit drapiertem Stück.
 * Das war ein Prüfstand, keine Portierung.
 *
 * Welche Rassen es gibt, sagt UMAs eigener Assetindex (20 Stück, darunter
 * Elf, HalfOrc, Sylvan, Sprite). Hier wird nichts geraten und nichts
 * gepflegt: Die Rassen gehören dem Unity-Projekt, und das bleibt unberührt.
 */
export class Umapythonkatalog {

    static async liste() {
        return UmapythonFigur.rassen();
    }

    static async hinzufuegen(rasse, lage = null) {
        const id = generateCharacterId();
        const figur = new UmapythonFigur(id, { rasse });
        await figur.load();
        Figurplatzierung.anwenden(figur, lage);
        state.characters.set(id, figur);
        state.scene.add(figur.group);
        fn.updateCharacterListUI();
        fn.updateVertexCount();
        fn.selectCharacter(id);
        markDirty();
        return figur;
    }
}

fn.addUmapythonFigur = Umapythonkatalog.hinzufuegen;
