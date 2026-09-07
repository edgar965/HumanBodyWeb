import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { generateCharacterId } from '../utils.js';
import { markDirty } from '../undo.js';
import { MhFigur } from './mhfigur.js';
import { Figurplatzierung } from '../figurplatzierung.js';

/**
 * Mhkatalog — den MakeHuman-Basiskörper anbieten und in die Szene stellen.
 *
 * Gegenstück zu `Umakatalog`, `Smplkatalog` und `addCharacterFromPreset`; der
 * Dialog „Charakter hinzufügen" hat dafür seinen vierten Reiter.
 *
 * Die Liste hat heute EINEN Eintrag, und das ist kein Platzhalter: MakeHuman
 * hat genau ein Basisnetz. Alles, was dort daraus wird — Geschlecht, Alter,
 * Muskeln, Gewicht, Proportionen —, sind Modellierregler aus
 * `.target`-Dateien, die dieses Projekt nicht mitbringt. Eine Liste bleibt es,
 * weil eine zweite Topologie (MakeHumans „Proxy"-Netze) genau hier stünde.
 */
export class Mhkatalog {

    static ADRESSE = '/api/character/mh-figur/';

    static async liste() {
        const daten = await Serverabruf.json(Mhkatalog.ADRESSE);
        return daten.figuren || [];
    }

    /**
     * Den Körper laden, in die Szene stellen und auswählen — derselbe Ablauf
     * wie bei UMA und SMPL: Lage erst nach `load()`, vorher gibt es keine Größe.
     */
    static async hinzufuegen(modell, lage = null) {
        const id = generateCharacterId();
        const figur = new MhFigur(id, { modell });
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

fn.addMhFigur = Mhkatalog.hinzufuegen;
