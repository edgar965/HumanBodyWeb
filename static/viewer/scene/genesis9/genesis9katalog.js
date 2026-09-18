import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Genesis9Figur } from './genesis9figur.js';
import { Figuraufnahme } from '../figuraufnahme.js';

/**
 * Genesis9katalog — die Daz-Figuren anbieten und eine in die Szene stellen.
 *
 * Gegenstück zu `Mhkatalog`, `Smplkatalog`, `Umakatalog`, `Umapythonkatalog`;
 * der Dialog „Charakter hinzufügen" hat dafür seinen sechsten Reiter.
 *
 * Die Liste sind keine Netze, sondern Reglerstellungen mit Haut: die
 * neutrale Grundfigur, Base Feminine, Base Masculine und die sechs
 * Charaktere der Starter Essentials (Amala, Fabrice, Kat, Laura, Matt, Ty)
 * — so, wie Daz Studio sie unter „Characters" führt
 * (`Genesis9/charaktere.py`).
 */
export class Genesis9katalog {

    static ADRESSE = '/api/character/genesis9-figur/';

    static async liste() {
        const daten = await Serverabruf.json(Genesis9katalog.ADRESSE);
        return daten.figuren || [];
    }

    /**
     * Die Figur bauen, in die Szene stellen und auswählen — Lage erst nach
     * `bauen()`, vorher gibt es keine Größe (`Figuraufnahme`).
     *
     * Ein GESPEICHERTES Modell (`eintrag.gespeichert`, Datei unter
     * `data/models/` mit `quelle: genesis9`) geht den Modelldaten-Weg
     * (`charakterAusModelldaten`) — mit Reglern, Haut, Augen, Brauen und
     * Kleidung aus der Datei (17.09.2026).
     */
    static hinzufuegen(figur, lage = null, eintrag = null) {
        if (eintrag?.gespeichert) return fn.addCharacterFromPreset(figur, lage);
        const neu = new Genesis9Figur(Figuraufnahme.kennung(), { figur });
        return Figuraufnahme.inDieSzene(neu, lage);
    }
}
