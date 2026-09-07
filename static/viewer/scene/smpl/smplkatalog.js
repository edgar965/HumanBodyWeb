import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { generateCharacterId } from '../utils.js';
import { markDirty } from '../undo.js';
import { SmplFigur } from './smplfigur.js';
import { Figurplatzierung } from '../figurplatzierung.js';

/**
 * Smplkatalog — die SMPL-Referenzkörper von GarmentCode anbieten und in die
 * Szene stellen. Gegenstück zu `Umakatalog` und `addCharacterFromPreset`;
 * der Dialog „Charakter hinzufügen" hat dafür seinen dritten Reiter.
 */
export class Smplkatalog {

    static ADRESSE = '/api/character/smpl-figur/';

    static async liste() {
        const daten = await Serverabruf.json(Smplkatalog.ADRESSE);
        return daten.figuren || [];
    }

    /**
     * Einen Körper laden, in die Szene stellen und auswählen — derselbe
     * Ablauf wie bei UMA: Lage erst nach `load()`, vorher gibt es keine Größe.
     */
    static async hinzufuegen(koerper, lage = null) {
        const id = generateCharacterId();
        const figur = new SmplFigur(id, { koerper });
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

fn.addSmplFigur = Smplkatalog.hinzufuegen;
