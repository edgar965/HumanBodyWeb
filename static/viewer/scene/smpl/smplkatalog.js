import { fn } from '../../gemeinsam/registrierung.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { SmplFigur } from './smplfigur.js';
import { Figuraufnahme } from '../figuraufnahme.js';

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
    static hinzufuegen(koerper, lage = null) {
        const figur = new SmplFigur(Figuraufnahme.kennung(), { koerper });
        return Figuraufnahme.inDieSzene(figur, lage);
    }
}

fn.addSmplFigur = Smplkatalog.hinzufuegen;
