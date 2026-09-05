import * as THREE from 'three';
import { Testzustand } from './testzustand.js';

/**
 * Einpassung — ein Skelett auf die Vergleichsgröße der Seite bringen.
 *
 * WARUM (05.09.2026): Jede Spalte zeigt eine andere Quelle in ihren eigenen
 * Maßen — BVH in Zentimetern oder Zoll, UMA 1,89 m, DEF 1,60 m über die
 * Gelenke. Haltungen vergleichen kann man nur, wenn alle gleich groß
 * dastehen: über die Gelenke gemessen, auf ZIELHOEHE gebracht, mittig und mit
 * den Füßen auf dem Boden. Das trägt eine Hülle (`wrapper`) mit Maßstab und
 * Versatz; die Knochen selbst bleiben unangetastet, damit ein Retarget-Clip
 * weiter auf sie passt. Bis dahin stand dieser Schritt nur in
 * `placeBvhSkeleton` — das UMA-Skelett kam ohne ihn in die Szene und war
 * sichtbar größer als der Rest.
 */
export class Einpassung {

    static ZIELHOEHE = 1.68;

    constructor(rootBone, bones) {
        this.rootBone = rootBone;
        this.bones = bones;
        this.kasten = Einpassung._kasten(rootBone, bones);
        const hoehe = Math.max(this.kasten.max.y - this.kasten.min.y, 0.01);
        this.massstab = Einpassung.ZIELHOEHE / hoehe;
        this.mitte = new THREE.Vector3();
        this.kasten.getCenter(this.mitte);
        this.huelle = null;
    }

    /** Hülle bauen und in die Spalte hängen; gibt den Maßstab zurück. */
    anwenden(skelKey) {
        const skel = Testzustand.skeletons[skelKey];
        const s = this.massstab;
        const huelle = new THREE.Group();
        huelle.scale.set(s, s, s);
        huelle.position.set(-this.mitte.x * s, -this.kasten.min.y * s, -this.mitte.z * s);
        huelle.add(this.rootBone);
        skel.group.add(huelle);
        skel.wrapper = huelle;
        this.huelle = huelle;
        return s;
    }

    /** Kurzform fürs Protokoll: Maßstab, Höhe, Lage. */
    beschreibung() {
        const k = this.kasten;
        return `scale=${this.massstab.toFixed(4)}, `
            + `hoehe=${(k.max.y - k.min.y).toFixed(2)}, `
            + `box.y=[${k.min.y.toFixed(2)},${k.max.y.toFixed(2)}], `
            + `center.z=${this.mitte.z.toFixed(2)}`;
    }

    static _kasten(rootBone, bones) {
        rootBone.updateWorldMatrix(true, true);
        const kasten = new THREE.Box3();
        const punkt = new THREE.Vector3();
        bones.forEach(b => { b.getWorldPosition(punkt); kasten.expandByPoint(punkt); });
        return kasten;
    }
}
