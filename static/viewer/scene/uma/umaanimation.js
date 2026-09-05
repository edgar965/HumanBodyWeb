import { THREE, fetchRetargetedClipFromUrl, fetchRetargetedClipFromText } from '../state.js';
import { state } from '../state.js';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Skelettanzeige } from '../../gemeinsam/skelettanzeige.js';

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
 */
export class Umaanimation {

    static async starten(inst, url, rawBvhText) {
        state._animatedCharId = inst.id;
        const wahl = {
            target: 'uma',
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
        if (!state.skeletonHelper) {
            state.skeletonHelper = Skelettanzeige.bauen(state.scene, inst.skelett.rootBone, state.rigVisible);
        }
        state.mixer = new THREE.AnimationMixer(inst.group);
        state.currentAction = state.mixer.clipAction(clip);
        state.currentAction.play();
        state.playing = true;
        return clip;
    }

    /**
     * Höhe über die Gelenke — nicht über `Box3.setFromObject`: Das nähme die
     * Geometrie in der Bindpose der GLB (liegt entlang −Z) und meldete 2,1 m.
     */
    static hoehe(inst) {
        const punkt = new THREE.Vector3();
        let unten = Infinity, oben = -Infinity;
        for (const bone of inst.skelett.bones) {
            bone.getWorldPosition(punkt);
            unten = Math.min(unten, punkt.y);
            oben = Math.max(oben, punkt.y);
        }
        return oben > unten ? oben - unten : 1.68;
    }

    /** Nach dem Anhalten: Ruhelage samt Reglern zurück. */
    static anhalten(inst) {
        if (inst && inst.quelle === 'uma') inst.ruhelageHerstellen();
    }
}
