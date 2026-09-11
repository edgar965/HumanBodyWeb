import * as THREE from 'three';
import { GarmentcodeAnziehen } from '../scene/garmentcode_anziehen.js';
import { Garmentcodestueck } from './garmentcodestueck.js';
import { Protokoll } from './protokoll.js';

/**
 * Garmentcodebindung — GarmentCode-Stücke ans Skelett der Figur binden.
 *
 * Die Stücke kommen als STARRE Netze in die Bühne (`garmentcodestueck.js`):
 * Im Theatre hat die Figur beim Laden noch kein Skelett, das baut der
 * Skinner erst beim Umwandeln; im BVH Studio steht es schon (`Spurfigur`),
 * dort bindet `Spurzubehoer` sofort nach dem Anhängen (11.09.2026). Die Rig-Datei am Netz (`userData.gcRig`) nennt je Punkt bis zu
 * vier Knochen — beim NAMEN, nicht beim Index, denn die Reihenfolge der
 * Knochen in der Datei ist nicht die des Skeletts. `GarmentcodeAnziehen`
 * kennt die Zuordnung und die Gewichtsfelder; hier kommt nur das dazu, was
 * beim Binden dazukommt: die `bindMatrix` des Körpers, so wie Skinner
 * (`_kleiderBinden`) und Spurzubehoer (`_binden`) es mit der MakeHuman-Kleidung tun.
 *
 * Die Geometrie wird geklont, aus demselben Grund wie beim Körper: Die
 * ursprüngliche hält WebGL-Zustand aus dem Rendern ohne Skinning.
 */
export class Garmentcodebindung {

    /**
     * @param {Object} skelett  { skeleton, rootBone, bones, boneByName }
     *        — aus `buildRigifySkeleton` (Skinner im Theatre, Spurfigur im Studio).
     */
    constructor(skelett) {
        this.skelett = skelett;
    }

    /**
     * Alle noch starren GarmentCode-Stücke der Figur häuten.
     * @param {THREE.Group} figur
     * @param {THREE.SkinnedMesh} koerper  das gehäutete Körpernetz
     * @returns Anzahl der gebundenen Stücke
     */
    binden(figur, koerper) {
        let gebunden = 0;
        for (const alt of [...figur.children]) {
            if (!this._offen(alt)) continue;
            const neu = this._haeuten(alt, koerper);
            if (!neu) continue;
            figur.remove(alt);
            alt.geometry.dispose();
            figur.add(neu);
            gebunden += 1;
            Protokoll.debug('garmentcodebindung', '✓ gebunden:', alt.userData.gcStueck);
        }
        return gebunden;
    }

    /** Ein starres Netz mit Rig-Daten, das noch nicht gehäutet ist. */
    _offen(netz) {
        return Boolean(netz?.isMesh && !netz.isSkinnedMesh
                       && netz.userData?.[Garmentcodestueck.KENNUNG]);
    }

    _haeuten(alt, koerper) {
        const daten = alt.userData[Garmentcodestueck.KENNUNG];
        const gewichte = daten.gewichte || [];
        const zuordnung = GarmentcodeAnziehen.zuordnung(
            daten.knochen || [], this.skelett.skeleton);
        if (!zuordnung.treffer || !gewichte.length) {
            // Ohne Gewichte in der Datei ist das der Referenzkörper-Weg
            // (kein Rig, gewollt); gewarnt wird nur, wenn Gewichte da sind
            // und kein Knochen passt — dann ging etwas verloren.
            (gewichte.length ? Protokoll.warnung : Protokoll.debug)('garmentcodebindung',
                gewichte.length
                    ? `„${alt.userData.gcStueck}": kein Knochen der Rig-Datei im Skelett`
                    : `„${alt.userData.gcStueck}": ohne Rig, bleibt starr`);
            return null;
        }
        const geo = alt.geometry.clone();
        GarmentcodeAnziehen.gewichte(geo, gewichte, zuordnung.index);
        const netz = new THREE.SkinnedMesh(geo, alt.material);
        netz.position.copy(alt.position);
        netz.rotation.copy(alt.rotation);
        netz.scale.copy(alt.scale);
        netz.name = alt.name;
        netz.userData = alt.userData;
        netz.castShadow = true;
        netz.receiveShadow = true;
        netz.frustumCulled = false;
        netz.bind(this.skelett.skeleton, koerper.bindMatrix);
        return netz;
    }
}
