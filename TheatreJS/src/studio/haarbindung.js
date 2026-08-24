import * as THREE from 'three';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Haarbindung — Haarnetze an den Kopfknochen binden.
 *
 * Herausgelöst aus `skinner.js` (303 Zeilen). Haare sind der Sonderfall unter
 * den Anbauteilen: Sie brauchen KEINE gerechneten Gewichte, sondern hängen
 * vollständig an EINEM Knochen (Gewicht 1,0). Alles andere wäre Aufwand ohne
 * Wirkung — Haare verformen sich nicht mit der Haut.
 *
 * **Die Weltmatrix muss übernommen werden** (`applyMatrix4`): Ein GLB-Haarnetz
 * bringt seine eigene Verschiebung mit; ohne sie sitzt der Haaransatz nach dem
 * Umwandeln im Bauch.
 *
 * Der Kopfknochen heißt je nach Rig anders — deshalb die Suchreihenfolge.
 */
export class Haarbindung {

    /** Kopfknochen in der Reihenfolge, in der gesucht wird. */
    static KOPFKNOCHEN = ['DEF-spine.006', 'DEF-spine.005', 'DEF-head'];
    /** Hoechstens so viele Knochen wirken auf einen Vertex (Three.js-Grenze). */
    static EINFLUESSE = 4;

    /**
     * @param {Object} skelett  { skeleton, rootBone, … }
     * @param {Object} gewichte Serverantwort mit `bone_names`
     */
    constructor(skelett, gewichte) {
        this.skelett = skelett;
        this.gewichte = gewichte;
    }

    /** Nummer des Kopfknochens in der Gewichtsliste, sonst -1. */
    kopfknochenNummer() {
        const namen = this.gewichte?.bone_names;
        if (!namen) return -1;
        for (const name of Haarbindung.KOPFKNOCHEN) {
            const nummer = namen.indexOf(name);
            if (nummer >= 0) return nummer;
        }
        return -1;
    }

    /** Alle noch ungebundenen Haarteile einer Figur umwandeln. */
    binden(figur, koerpernetz) {
        const kopf = this.kopfknochenNummer();
        if (kopf < 0) return;
        for (const haare of figur.children.filter(teil => teil.userData.isHair)) {
            if (!Haarbindung._ungebunden(haare)) continue;
            const gebunden = this.umwandeln(haare, kopf, koerpernetz);
            figur.remove(haare);
            figur.add(gebunden);
            Protokoll.debug('skinner', '✓ Haare zu SkinnedMesh umgewandelt:',
                            haare.name || 'Haare');
        }
    }

    static _ungebunden(haare) {
        let offen = false;
        haare.traverse(teil => {
            if (teil.isMesh && !teil.isSkinnedMesh) offen = true;
        });
        return offen;
    }

    /** Haarnetze vollstaendig an den Kopfknochen binden (Gewicht 1). */
    umwandeln(gltfSzene, kopfnummer, koerpernetz) {
        const gruppe = new THREE.Group();
        gruppe.userData.isHair = true;
        gltfSzene.traverse(teil => {
            if (teil.isMesh) {
                gruppe.add(this._netz(teil, kopfnummer, koerpernetz));
            }
        });
        return gruppe;
    }

    _netz(teil, kopfnummer, koerpernetz) {
        const geometrie = teil.geometry.clone();
        Haarbindung._gewichte(geometrie, kopfnummer);
        const gebunden = new THREE.SkinnedMesh(geometrie, teil.material);
        // Weltmatrix uebernehmen, sonst sitzen die Haare falsch.
        teil.updateWorldMatrix(true, false);
        gebunden.applyMatrix4(teil.matrixWorld);
        gebunden.bind(this.skelett.skeleton, koerpernetz.bindMatrix);
        gebunden.userData.isHair = true;
        return gebunden;
    }

    static _gewichte(geometrie, kopfnummer) {
        const anzahl = geometrie.attributes.position.count;
        const breite = Haarbindung.EINFLUESSE;
        const indizes = new Float32Array(anzahl * breite);
        const werte = new Float32Array(anzahl * breite);
        for (let punkt = 0; punkt < anzahl; punkt++) {
            indizes[punkt * breite] = kopfnummer;
            werte[punkt * breite] = 1.0;
        }
        geometrie.setAttribute('skinIndex',
                               new THREE.Float32BufferAttribute(indizes, breite));
        geometrie.setAttribute('skinWeight',
                               new THREE.Float32BufferAttribute(werte, breite));
    }
}
