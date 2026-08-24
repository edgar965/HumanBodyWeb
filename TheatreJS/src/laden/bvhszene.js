import * as THREE from 'three';
import { BVHLoader } from 'three/addons/loaders/BVHLoader.js';
import { Theatreanmeldung } from './theatreanmeldung.js';

/**
 * Bvhszene — BVH-Text lesen und als sichtbares Skelett in die Bühne hängen.
 *
 * Herausgelöst aus `asset-loader.js` (318 Zeilen). Drei Einstellungen, die
 * nicht nach Geschmack aussehen sollten:
 *
 * * **`depthTest = false` am Skeletthelfer.** Ohne das verschwinden die Knochen
 *   im Körpernetz — man sieht das Rig nur dort, wo die Figur dünn ist.
 * * **`renderOrder = 999`**: Der Helfer wird NACH der Figur gezeichnet, sonst
 *   überdeckt sie ihn trotz `depthTest`.
 * * **`action.paused = true`**: Die Animation wird geladen, aber nicht
 *   gestartet — das Abspielen steuert der Abspieler.
 *
 * `isRig` markiert Wurzelknochen und Helfer; daran erkennt der Umschalter
 * „Rig anzeigen" sie wieder.
 */
export class Bvhszene {

    static ZEICHENREIHENFOLGE = 999;
    static _leser = new BVHLoader();

    /**
     * @returns {{mixer, action, skeleton, clip, rootBone, duration}}
     */
    static ausText(text, szene, name) {
        const ergebnis = Bvhszene._leser.parse(text);
        const wurzel = ergebnis.skeleton.bones[0];
        wurzel.userData.isRig = true;
        const helfer = Bvhszene._helfer(ergebnis, wurzel);
        szene.add(wurzel);
        szene.add(helfer);
        const mixer = new THREE.AnimationMixer(wurzel);
        const aktion = mixer.clipAction(ergebnis.clip);
        aktion.setLoop(THREE.LoopRepeat);
        aktion.play();
        aktion.paused = true;      // der Abspieler startet sie
        Theatreanmeldung.anmelden(wurzel, name, 'BVH');
        return { mixer, action: aktion, skeleton: helfer, clip: ergebnis.clip,
                 rootBone: wurzel, duration: ergebnis.clip.duration || 1 };
    }

    static _helfer(ergebnis, wurzel) {
        const helfer = new THREE.SkeletonHelper(wurzel);
        helfer.skeleton = ergebnis.skeleton;
        helfer.visible = true;
        helfer.userData.isRig = true;
        helfer.renderOrder = Bvhszene.ZEICHENREIHENFOLGE;
        if (helfer.material) {
            helfer.material.depthTest = false;
            helfer.material.depthWrite = false;
        }
        return helfer;
    }
}
