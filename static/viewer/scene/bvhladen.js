import { THREE, fetchRetargetedClipFromUrl, fetchRetargetedClipFromText } from './state.js';
import { state } from './state.js';
import { Skelettanzeige } from '../gemeinsam/skelettanzeige.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Bvhladen — eine BVH auf die HumanBody-Figur bringen: über den Retarget
 * auf das Rigify-Skelett, oder als nackte Skelettvorschau, wenn die Figur
 * (noch) keine Hautgewichte hat.
 *
 * Herausgelöst aus `animation.js` (12.09.2026, Befund `jsfunktionen`:
 * `loadBVHAnimation` mit 121 Zeilen). Dort bleibt die Weiche nach Figurart —
 * UMA, SMPL/MakeHuman, HumanBody — und hier stehen die beiden HumanBody-Wege.
 * `meldung(text)` ist die Zeile im Animations-Reiter.
 */
export class Bvhladen {

    /** Höhe eines Netzes in Metern; `vorgabe`, wenn es keine Ausdehnung hat. */
    static hoehe(netz, vorgabe) {
        if (!netz) return vorgabe;
        const bb = new THREE.Box3().setFromObject(netz);
        return bb.isEmpty() ? vorgabe : bb.max.y - bb.min.y;
    }

    /**
     * Der Retarget: BVH → Clip auf `skel`, Mixer am Körpernetz.
     *
     * @param {object|null} inst   die Figur der Szene, oder null (Einzelkörper)
     * @param {object} skel        Rigify-Skelett mit `rootBone`
     * @param {{url: string, name: string, rawBvhText: string|null}} quelle
     * @param {(text: string) => void} meldung
     */
    static async retarget(inst, skel, quelle, meldung) {
        const { url, name, rawBvhText } = quelle;
        const bMesh = inst ? inst.bodyMesh : state.bodyMesh;
        state._animatedCharId = inst ? inst.id : null;
        try {
            const wahl = { bodyHeight: Bvhladen.hoehe(bMesh, 1.68),
                           deltaNorm: state._sceneDeltaNorm };
            let clip;
            if (rawBvhText) {
                clip = await fetchRetargetedClipFromText(rawBvhText, skel, wahl);
                state.currentAnimBvhText = rawBvhText;
            } else {
                clip = await fetchRetargetedClipFromUrl(url, skel, wahl);
                // Der Rohtext wird fuer "Boden richten" und den Export
                // gebraucht; ohne ihn bleiben beide Knoepfe wirkungslos.
                state.currentAnimBvhText = await Serverabruf.text(Bvhladen.frisch(url))
                    .catch(() => '');
            }
            if (!state.skeletonHelper) {
                state.skeletonHelper = Skelettanzeige.bauen(state.scene, skel.rootBone, state.rigVisible);
            }
            state.mixer = new THREE.AnimationMixer(bMesh);
            state.currentAction = state.mixer.clipAction(clip);
            state.currentAction.play();
            state.playing = true;
            meldung(`${name || url} · ${clip.tracks.length} Spuren · ${clip.duration.toFixed(1)} s`);
        } catch (e) {
            meldung(`Fehler: ${e.message || e}`);
            Protokoll.fehler('Bvhladen', 'Retarget fehlgeschlagen', e);
        }
    }

    /** Die Adresse mit Zeitstempel — eine BVH ist eine DATEN-Adresse, nie Statik. */
    static frisch(url) {
        return url + (url.includes('?') ? '&' : '?') + '_t=' + Date.now();
    }

    /**
     * Ohne Hautgewichte: das BVH-Skelett selbst zeigen, auf Körperhöhe
     * skaliert und an den Ort der Figur gestellt.
     */
    static vorschau(inst, targetMesh, quelle) {
        const { url, rawBvhText } = quelle;
        if (rawBvhText) {
            Bvhladen.skelettZeigen(inst, targetMesh, state.bvhLoader.parse(rawBvhText), rawBvhText);
            return;
        }
        const fileLoader = new THREE.FileLoader(state.bvhLoader.manager);
        fileLoader.load(
            Bvhladen.frisch(url),
            (text) => Bvhladen.skelettZeigen(inst, targetMesh,
                                             state.bvhLoader.parse(String(text)), String(text)),
            undefined,
            (err) => Protokoll.fehler('Bvhladen', 'BVH nicht geladen', err));
    }

    static skelettZeigen(inst, targetMesh, result, text) {
        state.currentAnimBvhText = text;
        const bvhBones = result.skeleton.bones;
        if (bvhBones.length === 0) return;
        const rootBone = bvhBones[0];
        rootBone.updateWorldMatrix(true, true);
        const skelBox = new THREE.Box3();
        const tmpVec = new THREE.Vector3();
        bvhBones.forEach(b => {
            b.updateWorldMatrix(true, false);
            b.getWorldPosition(tmpVec);
            skelBox.expandByPoint(tmpVec);
        });
        const bodyHeight = Bvhladen.hoehe(targetMesh, 1.75);
        const scale = bodyHeight / Math.max(skelBox.max.y - skelBox.min.y, 0.01);
        state.skelWrapper = new THREE.Group();
        state.skelWrapper.scale.set(scale, scale, scale);
        state.skelWrapper.add(rootBone);
        if (inst) state.skelWrapper.position.copy(inst.group.position);
        state.scene.add(state.skelWrapper);
        if (state.skeletonHelper) state.scene.remove(state.skeletonHelper);
        state.skeletonHelper = Skelettanzeige.bauen(state.scene, rootBone, state.rigVisible);
        state.mixer = new THREE.AnimationMixer(rootBone);
        state.currentAction = state.mixer.clipAction(result.clip);
        state.currentAction.play();
        state.playing = true;
        state._animatedCharId = inst ? inst.id : null;
    }
}
