import * as THREE from 'three';
import { Knochenkette } from './knochenkette.js';

/**
 * Knochenbau — aus der Knochenliste des Servers ein echtes Three.js-Skelett.
 *
 * Der Three.js-Teil zu `knochenkette.js`; die Rechnung steht dort und ist
 * ohne Browser prüfbar. Ergebnis ist genau die Form, die `Rigauswahl` von
 * einer UMA-Figur kennt — `{skeleton, rootBone, bones, boneByName}` —, damit
 * der Rig-Schalter für SMPL und MakeHuman ohne eine Zeile Sonderfall greift.
 *
 * DIE KNOCHEN HÄNGEN AN DER FIGURGRUPPE, NICHT AN DER SZENE
 * =========================================================
 * Sonst bleiben sie stehen, wo die Figur beim Laden stand: Der Dialog setzt
 * neue Figuren 1,5 m neben die vorhandene (`figurplatzierung.js`), G/R/S
 * verschieben und drehen sie. Ein Skelett in der Szene würde all das nicht
 * mitmachen und neben seinem Körper schweben.
 */
export class Knochenbau {

    /**
     * @param angaben  `{name, knochen:[{name, eltern, kopf, schwanz, pos, quat}]}`
     * @param gruppe   die Gruppe der Figur (THREE.Object3D)
     * @returns {skeleton, rootBone, bones, boneByName} oder null
     *
     * DIE RUHEDREHUNG WIRD MITGESETZT (07.09.2026). Ohne sie stünde das
     * Skelett zwar richtig da — der Helper braucht nur Punkte —, aber jede
     * abgespielte Bewegung käme verdreht an: Der Retarget-Motor rechnet
     * gegen genau diese Ruhelage (`gelenkskelett.py`).
     */
    static bauen(angaben, gruppe) {
        const plan = Knochenkette.bauplan(angaben?.knochen);
        if (!plan.length) return null;

        const nach = new Map();
        const bones = [];
        for (const eintrag of plan) {
            const knochen = new THREE.Bone();
            knochen.name = eintrag.name;
            knochen.position.set(...eintrag.pos);
            if (eintrag.quat) knochen.quaternion.set(...eintrag.quat);
            nach.set(eintrag.name, knochen);
            bones.push(knochen);
            const eltern = eintrag.eltern ? nach.get(eintrag.eltern) : null;
            (eltern || gruppe).add(knochen);
        }

        const wurzelname = Knochenkette.wurzelname(plan);
        const rootBone = nach.get(wurzelname) || bones[0];
        // Ohne das steht der Helper beim ersten Bild noch am Ursprung: Er
        // liest die Weltmatrizen, und die entstehen sonst erst im nächsten
        // Durchlauf der Renderschleife.
        rootBone.updateMatrixWorld(true);

        return {
            skeleton: new THREE.Skeleton(bones),
            rootBone,
            bones,
            boneByName: Object.fromEntries(bones.map(k => [k.name, k])),
            quelle: angaben?.name || null,
        };
    }

    /**
     * Ein gebautes Skelett wieder abräumen.
     *
     * Nötig beim Neuaufbau: Die MakeHuman-Regler und die SMPL-Formregler
     * holen das Netz neu, und mit ihm die Knochen. Bliebe das alte hängen,
     * stünden zwei Skelette ineinander — beim zehnten Reglerzug zehn.
     */
    static abraeumen(skelett) {
        if (!skelett) return null;
        skelett.rootBone?.parent?.remove(skelett.rootBone);
        skelett.skeleton?.dispose?.();
        return null;
    }
}
