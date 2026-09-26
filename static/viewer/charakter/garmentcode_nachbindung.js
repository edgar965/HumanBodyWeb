import { Skelettereignis } from '../gemeinsam/skelettereignis.js';
import { GarmentcodeAnziehen } from './garmentcode_anziehen.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Gcreglerfolge } from '../gemeinsam/gcreglerfolge.js';

/**
 * GarmentcodeNachbindung — GarmentCode-Stücke folgen einem neuen Skelett.
 *
 * WARUM (Edgar, 19.09.2026, mit Bild: „Garment Code [animiert] auch nicht"):
 * Genesis 9 baut sein Skelett bei jedem Umbau neu (Reglerzug, Strg+Alt+H,
 * die feine Stufe nach dem Käfig). Das Modell bindet seine Daz-Stücke um
 * (`_kleiderBinden`) und meldet `Skelettereignis`; ein GarmentCode-Stück
 * hing an den alten Knochen und stand still. Hier hört die Szene zu und ruft
 * `GarmentcodeAnziehen.nachbinden`, das seit heute auch ein GEHÄUTETES Stück
 * neu bindet, wenn sein Skelett nicht mehr das der Figur ist.
 *
 * Eigenes Modul, weil `garmentcode_anziehen.js` (259 Zeilen) und
 * `garmentcode.js` (254) über der Grenze liegen und nicht wachsen dürfen.
 * Eingehängt aus `skeleton.js` — dort steht auch der HumanBody-Weg
 * (`convertInstToSkinned` → `nachbinden`).
 */
export class GarmentcodeNachbindung {

    static einhaengen() {
        Skelettereignis.hoeren(({ inst }) => {
            if (!inst) return;
            try {
                // Erst die Form (Genesis 9 nach einem Reglerzug, 24.09.2026), dann binden.
                const geformt = Gcreglerfolge.anwenden(inst);
                if (geformt) Protokoll.debug('GarmentCode', `${geformt} Stück(e) dem neuen Körper nachgeformt`);
                const anzahl = GarmentcodeAnziehen.nachbinden(inst);
                if (anzahl) Protokoll.debug('GarmentCode', `${anzahl} Stück(e) an das neue Skelett gebunden`);
            } catch (fehler) {
                Protokoll.warnung('GarmentCode', `Nachbinden gescheitert: ${fehler.message}`);
            }
        });
    }
}

GarmentcodeNachbindung.einhaengen();
