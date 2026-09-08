import { THREE } from './state.js';
import { state } from './state.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Skelettanzeige } from '../gemeinsam/skelettanzeige.js';
import { fetchRetarget } from '../retarget_hybrid.js';

/**
 * Eigenanimation — eine BVH auf dem EIGENEN Skelett der Figur abspielen.
 *
 * WARUM (Edgar, 07.09.2026: „Das Rigging funktioniert wohl nicht für die
 * neuen Modelle SMPL, MakeHuman", und dann: „du hast doch retarget für das
 * SMPL skeleton, konfiguriere das"): Für SMPL und MakeHuman lief Play in den
 * DEF-Zweig — die Szene hängte jeder Figur das Rigify-Skelett an, samt
 * HumanBody-Hautgewichten. Gemessen: 176 Knochen und Spuren namens
 * `DEF-spine.quaternion` auf einem Netz mit 6.890 Punkten, dessen eigene
 * Knochen `Pelvis` und `Spine1` heißen. Es bewegte sich nichts.
 *
 * Der Retarget kann beide Ziele längst — er braucht nur die Namen. SMPLs 24
 * Gelenke heißen genau wie die BVH-Seite von `SkeletonAIST_SMPL`; für
 * MakeHuman gibt es `mh_zuordnung.py`. Beide Tabellen sind Umkehrungen der
 * vorhandenen DEF-Zuordnungen, keine zweite Quelle.
 *
 * MAKEHUMAN GEHT ÜBER POST, SMPL ÜBER GET: Das MakeHuman-Rig hängt an 269
 * Reglern — seine Gelenke sind Mittelwerte von Punkten DIESER Stellung.
 * Als Abfrageteil wären das mehrere Kilobyte, und die werden irgendwo
 * stillschweigend gekürzt (dieselbe Entscheidung wie bei `Mhfigur.netz`).
 *
 * Der Mischer läuft auf der FIGURGRUPPE, nicht auf dem Netz: Die Knochen
 * hängen dort (`Knochenbau`), und die Spuren nennen sie beim Namen.
 */
export class Eigenanimation {

    /**
     * Welche Figurart auf welches Zielskelett des Servers zeigt.
     *
     * `umapython` (08.09.2026) ist die in Python gebaute UMA-Figur. Sie
     * bekommt ein EIGENES Ziel, obwohl ihre Knochen genauso heißen wie die
     * der GLB-Figur: Die Zuordnungstabelle ist dieselbe
     * (`formats/uma_knochen.py`), das Skelett aber kommt aus dem Bau und
     * nicht aus einer Datei — und es hängt an den DNA-Reglern.
     */
    static ZIELE = { smpl: 'smpl', makehuman: 'makehuman',
                     umapython: 'umapython' };

    /** Trifft diese Figur zu — hat sie ein eigenes Skelett zum Bespielen? */
    static passt(inst) {
        return !!(inst && Eigenanimation.ZIELE[inst.quelle] && inst.skelett);
    }

    static async starten(inst, url, rawBvhText) {
        state._animatedCharId = inst.id;
        const clip = await Eigenanimation._clip(inst, url, rawBvhText);
        state.currentAnimBvhText = rawBvhText || await Serverabruf.text(
            url + (url.includes('?') ? '&' : '?') + '_t=' + Date.now()).catch(() => '');
        if (!state.skeletonHelper) {
            state.skeletonHelper = Skelettanzeige.bauen(
                state.scene, inst.skelett.rootBone, state.rigVisible);
        }
        state.mixer = new THREE.AnimationMixer(inst.group);
        state.currentAction = state.mixer.clipAction(clip);
        state.currentAction.play();
        state.playing = true;
        return clip;
    }

    static _clip(inst, url, rawBvhText) {
        const wahl = {
            target: Eigenanimation.ZIELE[inst.quelle],
            figur: Eigenanimation.figurname(inst),
            bodyHeight: Eigenanimation.hoehe(inst),
            deltaNorm: state._sceneDeltaNorm,
        };
        if (inst.quelle === 'makehuman') {
            wahl.makro = inst.makro || null;
            wahl.regler = inst.regler || null;
        }
        // UMA Python: Der Regler stellt einen KNOCHEN — das Skelett dieser
        // Stellung ist das Ziel, nicht das der Vorgabefigur. Dieselbe
        // Überlegung wie bei MakeHuman.
        if (inst.quelle === 'umapython') wahl.regler = inst.dna || {};
        // Bearbeiteter BVH-Text (Boden richten, Effekte) geht denselben Weg
        // wie beim DEF-Ziel: über den Text-Endpunkt. Der kennt nur DEF —
        // deshalb bleibt es hier bei der Datei, und der Rohtext dient nur
        // dem Export.
        return fetchRetarget({ bvhUrl: url }, inst.skelett, wahl);
    }

    /** Der Name, unter dem der Server das Skelett dieser Figur nachbaut. */
    static figurname(inst) {
        if (inst.quelle === 'smpl') return inst.koerper;
        if (inst.quelle === 'umapython') return inst.rasse;
        return inst.modell || 'basis';
    }

    /**
     * Höhe über die KNOCHEN, nicht über `Box3.setFromObject`.
     *
     * Sobald das Netz ein `SkinnedMesh` ist, meldet die Box die Ruhe-Box der
     * Geometrie — bei einer laufenden Bewegung ist das nicht die Figur. Die
     * Knochen stehen immer da, wo die Figur gerade steht.
     */
    static hoehe(inst) {
        const punkt = new THREE.Vector3();
        let unten = Infinity, oben = -Infinity;
        for (const bone of inst.skelett.bones) {
            bone.getWorldPosition(punkt);
            unten = Math.min(unten, punkt.y);
            oben = Math.max(oben, punkt.y);
        }
        return oben > unten ? oben - unten : (inst.hoehe || 1.68);
    }

    /** Nach dem Anhalten: zurück in die Ruhelage des eigenen Skeletts. */
    static anhalten(inst) {
        if (Eigenanimation.passt(inst)) inst.skelett.skeleton.pose();
    }
}
