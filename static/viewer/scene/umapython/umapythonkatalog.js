import { fn } from '../../gemeinsam/registrierung.js';
import { UmapythonFigur } from './umapythonfigur.js';
import { Figuraufnahme } from '../figuraufnahme.js';

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

    static hinzufuegen(rasse, lage = null) {
        const figur = new UmapythonFigur(Figuraufnahme.kennung(), { rasse });
        return Figuraufnahme.inDieSzene(figur, lage);
    }
}

fn.addUmapythonFigur = Umapythonkatalog.hinzufuegen;
