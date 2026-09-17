import { fetchRetargetedClipFromUrl, fetchRetargetedClipFromText } from '../state.js';
import { state } from '../state.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Eigenanimation } from '../eigenanimation.js';

/**
 * Umaanimation — eine BVH auf der UMA-Figur abspielen.
 *
 * Der Server rechnet den Clip mit `target=uma` auf das Skelett der GLB
 * (`core/dienste/retargetdaten.py`), genau wie auf der Test-Animation-Seite.
 * Die Spuren heißen nach den Knochen; der Mischer läuft auf der Figurgruppe,
 * unter der die Wurzel hängt (`UmaFigur.load`).
 *
 * KEIN `skeleton.pose()`: Das setzt auf die Bindpose der GLB zurück — eine
 * A-Pose, die entlang −Z liegt. Die Ruhelage der Figur ist die Knotenpose
 * mit den Reglern; die stellt `UmaFigur.ruhelageHerstellen` wieder her.
 *
 * Abspielen und Höhe über die Gelenke kommen aus `Eigenanimation` (erbt seit
 * 17.09.2026, Befund `doppelcode`); eigen ist nur, wie der Clip entsteht.
 */
export class Umaanimation extends Eigenanimation {

    static async starten(inst, url, rawBvhText) {
        state._animatedCharId = inst.id;
        const wahl = {
            target: 'uma',
            figur: inst.datei,            // das Skelett DIESER Datei, nicht das aus aktuell.json
            bodyHeight: Umaanimation.hoehe(inst),
            deltaNorm: state._sceneDeltaNorm,
        };
        // Fehler gehen nach oben: `loadBVHAnimation` schreibt sie in die
        // Zeile unter der Leiste (vorher stand dort nichts, der Knopf war tot).
        let clip;
        if (rawBvhText) {
            clip = await fetchRetargetedClipFromText(rawBvhText, inst.skelett, wahl);
            state.currentAnimBvhText = rawBvhText;
        } else {
            clip = await fetchRetargetedClipFromUrl(url, inst.skelett, wahl);
            state.currentAnimBvhText = await Serverabruf.text(
                url + (url.includes('?') ? '&' : '?') + '_t=' + Date.now()).catch(() => '');
        }
        return Umaanimation.abspielen(inst, clip);
    }

    /** `inst.hoehe` ist bei UMA die ROHE Höhe der GLB (2,0 m) — nicht die Figur. */
    static ersatzhoehe() {
        return 1.68;
    }

    /** Nach dem Anhalten: Ruhelage samt Reglern zurück. */
    static anhalten(inst) {
        if (inst && inst.quelle === 'uma') inst.ruhelageHerstellen();
    }
}
