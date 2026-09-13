import { generateRigBoneMesh } from '../modellbau/rignetz.js';
import { generateModelMesh } from '../modellbau/modellnetz.js';
import { Skelettdaten } from './skelettdaten.js';

/**
 * Erzeugtesmodell — ein Modell aus einer Knochenvorschrift (Rig1–4,
 * `type: 'generated_model'`) statt aus dem Netz des Servers.
 *
 * Stand dreimal: `scene/charakter_koerper.js` (`ausKonfiguration`),
 * `bvh_studio/spurfigur.js` (`_knochennetz`) und `TheatreJS/src/laden/
 * figurnetz.js` (`erzeugtesModell`) — dieselben zwei Wege, `rig` über die
 * Rig-Knochen des Servers, `def` über Skelett und Hautgewichte. Seit
 * 13.09.2026 EINMAL hier, gerufen aus `HumanbodyModell.bauen`.
 *
 * Skelett und Gewichte gibt die Seite mit, wenn sie sie hat; sonst holt
 * `Skelettdaten` sie (gemerkt). Die Rig-Knochen kommen immer von dort.
 */
export class Erzeugtesmodell {

    /**
     * @param vorschrift    die Modellvorgabe (`skeleton_type`, Knochen …)
     * @param skelettdaten  Rigify-Skelett, oder null
     * @param gewichte      Hautgewichte, oder null
     * @returns {Promise<{mesh: *, skeleton: *}>}
     */
    static async bauen(vorschrift, skelettdaten = null, gewichte = null) {
        const skelett = skelettdaten || await Skelettdaten.rigify();
        const haut = gewichte || await Skelettdaten.gewichte();
        if (!skelett || !haut) throw new Error('Skeleton data not loaded');
        let ergebnis;
        if ((vorschrift.skeleton_type || 'def') === 'rig') {
            const knochen = await Skelettdaten.rigknochen();
            if (!knochen) throw new Error('Rig bones data not loaded');
            ergebnis = generateRigBoneMesh(knochen, vorschrift, skelett, haut);
        } else {
            ergebnis = generateModelMesh(skelett, haut, vorschrift);
        }
        if (!ergebnis?.mesh) throw new Error('No visible bones in generated model config');
        return ergebnis;
    }
}
