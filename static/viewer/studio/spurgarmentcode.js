import { Genesis9Modell } from '../gemeinsam/genesis9modell.js';
import { GarmentcodeAblage } from '../scene/garmentcode_ablage.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
// Nebenwirkung des Imports: Genesis 9 baut sein Skelett nach dem Käfig mit der
// feinen Stufe neu (`Skelettereignis`) — ohne diesen Hörer hinge das Kleid an
// den alten Knochen und stünde in der Animation still (wie in der Szene, 19.09.2026).
import '../scene/garmentcode_nachbindung.js';

/**
 * Spurgarmentcode — die GarmentCode-Stücke eines gespeicherten Genesis-9-Modells
 * im BVH Studio anziehen.
 *
 * ANLASS (Edgar, 24.09.2026, mit Bild: „Damira1 wird ohne Kleid (Garment Code)
 * angezeigt"): Das Studio kennt vom Modell nur den Namen; `Genesis9Modell.
 * _vorgabeUebernehmen` holt Haut, Augen und Daz-Kleidung aus dem Katalogeintrag,
 * die Liste `garmentcode` (`GarmentcodeAblage`) nahm niemand. HumanBody-Figuren
 * bekommen sie über `Modellzubehoer`; Genesis 9 geht denselben Weg wie die Szene
 * (`GarmentcodeAblage.laden`: nacheinander anziehen, Material setzen, danach die
 * Daz-Stücke über `Genesis9lagen.nachGcBau` neu legen).
 */
export class Spurgarmentcode {

    /** @returns Anzahl der angezogenen Stücke */
    static async genesis9(modell) {
        try {
            const eintrag = await Genesis9Modell.eintrag(modell.figur);
            const liste = eintrag?.gespeichert ? (eintrag.garmentcode || []) : [];
            if (!liste.length) return 0;
            const anzahl = await GarmentcodeAblage.laden(modell, liste);
            Protokoll.debug('Spurgarmentcode', `${modell.figur}: ${anzahl}/${liste.length} GarmentCode-Stück(e)`);
            return anzahl;
        } catch (fehler) {
            Protokoll.warnung('Spurgarmentcode', `GarmentCode für „${modell.figur}":`, fehler.message || fehler);
            return 0;
        }
    }
}
