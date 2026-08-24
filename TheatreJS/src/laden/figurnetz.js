import * as THREE from 'three';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords }
    from '../../../static/viewer/gemeinsam/kodierung.js';
import { BODY_MATERIALS }
    from '../../../static/viewer/gemeinsam/koerpermaterialien.js';
import { generateRigBoneMesh } from '../../../static/viewer/modellbau/rignetz.js';
import { generateModelMesh } from '../../../static/viewer/modellbau/modellnetz.js';
import { Skelettdaten } from './skelettdaten.js';

/**
 * Figurnetz — aus einer Serverantwort (oder einer Bauvorschrift) ein Netz bauen.
 *
 * Herausgelöst aus `asset-loader.js` (318 Zeilen). Zwei Wege führen zur Figur:
 *
 * * **Vom Server** (`bauen`): Punkte, Flächen, UVs und Normalen kommen als
 *   base64. Achtung auf die Achsen — Blender ist Z-oben, Three.js Y-oben, und
 *   die Normalen müssen MIT gedreht werden. Danach ist KEINE Rotation der
 *   Gruppe mehr nötig; wer sie trotzdem setzt, dreht die Figur ein zweites Mal.
 * * **Erzeugt** (`erzeugtesModell`): Das Netz entsteht im Browser aus der
 *   Knochenvorschrift; dafür braucht es Skelett und Hautgewichte.
 *
 * Die elf Werkstoffe der Körperteile sind ein ARRAY am Netz — dazu müssen die
 * Flächenbereiche (`groups`) gesetzt sein. Fehlen sie, bekommt das ganze Netz
 * den ersten (Haut), sonst wäre es unsichtbar.
 */
export class Figurnetz {

    /** Aus einer Serverantwort. */
    static bauen(daten) {
        const geometrie = Figurnetz._geometrie(daten);
        const werkstoffe = Figurnetz._werkstoffe();
        const bereiche = daten.groups || [];
        for (const bereich of bereiche) {
            geometrie.addGroup(bereich.start, bereich.count, bereich.materialIndex);
        }
        const netz = new THREE.Mesh(geometrie,
                                    bereiche.length > 0 ? werkstoffe : werkstoffe[0]);
        netz.castShadow = true;
        netz.receiveShadow = true;
        const gruppe = new THREE.Group();
        gruppe.add(netz);
        return gruppe;
    }

    static _geometrie(daten) {
        const punkte = base64ToFloat32(daten.vertices);
        blenderToThreeCoords(punkte);
        const geometrie = new THREE.BufferGeometry();
        geometrie.setAttribute('position', new THREE.BufferAttribute(punkte, 3));
        geometrie.setIndex(new THREE.BufferAttribute(
            base64ToUint32(daten.faces), 1));
        if (daten.uvs) {
            geometrie.setAttribute('uv', new THREE.BufferAttribute(
                base64ToFloat32(daten.uvs), 2));
        }
        if (daten.normals) {
            const normalen = base64ToFloat32(daten.normals);
            blenderToThreeCoords(normalen);
            geometrie.setAttribute('normal',
                                   new THREE.BufferAttribute(normalen, 3));
        } else {
            geometrie.computeVertexNormals();
        }
        return geometrie;
    }

    static _werkstoffe() {
        return BODY_MATERIALS.map(angabe => new THREE.MeshStandardMaterial({
            color: angabe.color,
            roughness: angabe.roughness,
            metalness: angabe.metalness,
            side: THREE.DoubleSide,
            transparent: angabe.transparent || false,
            opacity: angabe.opacity !== undefined ? angabe.opacity : 1.0,
        }));
    }

    // ------------------------------------------------------- Erzeugtes Modell

    static async erzeugtesModell(vorschrift) {
        const skelett = await Skelettdaten.rigify();
        const gewichte = await Skelettdaten.gewichte();
        const ergebnis = await Figurnetz._erzeugen(vorschrift, skelett, gewichte);
        if (!ergebnis) {
            throw new Error('No visible bones in generated model config');
        }
        const gruppe = new THREE.Group();
        gruppe.add(ergebnis.mesh);
        gruppe.userData.isGeneratedModel = true;
        Figurnetz._skelettMerken(gruppe, ergebnis);
        return gruppe;
    }

    static async _erzeugen(vorschrift, skelett, gewichte) {
        if ((vorschrift.skeleton_type || 'def') === 'rig') {
            const knochen = await Skelettdaten.rigknochen();
            if (!knochen) throw new Error('Rig bones data not loaded');
            return generateRigBoneMesh(knochen, vorschrift, skelett, gewichte);
        }
        if (!skelett || !gewichte) throw new Error('Skeleton data not loaded');
        return generateModelMesh(skelett, gewichte, vorschrift);
    }

    /** Das Animationssystem sucht diese vier Angaben an der Gruppe. */
    static _skelettMerken(gruppe, ergebnis) {
        if (!ergebnis.skeleton || !ergebnis.mesh.isSkinnedMesh) return;
        Object.assign(gruppe.userData, {
            isSkinnedMesh: true,
            skinnedMesh: ergebnis.mesh,
            skeleton: ergebnis.skeleton.skeleton,
            rootBone: ergebnis.skeleton.rootBone,
            // Vollstaendiges Rigify-Objekt fuer das Retarget (boneByName usw.)
            rigifySkelObj: ergebnis.skeleton,
        });
    }
}
