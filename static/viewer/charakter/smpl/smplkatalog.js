import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { fn } from '../../gemeinsam/registrierung.js';
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
     *
     * Ein GESPEICHERTES Modell (`eintrag.gespeichert`, Datei unter
     * `data/models/` mit `quelle: smpl`) geht den Modelldaten-Weg
     * (`charakterAusModelldaten`) — mit Namen, Reglern und Haut aus der
     * Datei, wie bei Genesis 9 (25.09.2026): `koerper` ist hier der
     * DATEINAME („SMPLX1"), keine GarmentCode-Katalogfigur — die Netz-Adresse
     * dieser Klasse kennt ihn nicht.
     */
    static hinzufuegen(koerper, lage = null, eintrag = null) {
        if (eintrag?.gespeichert) return fn.addCharacterFromPreset(koerper, lage);
        const figur = new SmplFigur(Figuraufnahme.kennung(), { koerper });
        return Figuraufnahme.inDieSzene(figur, lage);
    }
}
