import { fn } from '../../gemeinsam/registrierung.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { MhFigur } from './mhfigur.js';
import { Figuraufnahme } from '../figuraufnahme.js';

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
    static hinzufuegen(modell, lage = null) {
        const figur = new MhFigur(Figuraufnahme.kennung(), { modell });
        return Figuraufnahme.inDieSzene(figur, lage);
    }
}

fn.addMhFigur = Mhkatalog.hinzufuegen;
